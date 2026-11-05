# T14 · Captura de cambios para `maestro_suscriptores`

**Proyecto:** Plataforma de datos del acueducto  
**Módulo:** 2 · Construcción de Pipelines de Datos  
**Sesión:** 14 · CDC por marca temporal vs. CDC basada en registro  
**Equipo:** equipo-3  
**Motor:** PostgreSQL 16  
**Lenguaje:** Python 3.11  

---

# 1. Identificación del equipo

| Campo | Valor |
|---|---|
| Identificador de equipo | `equipo-3` |
| Motor | PostgreSQL 16 |
| Perfil ejecutado | `equipo-3` |
| Método evaluado | CDC basada en marca temporal |
| Tabla fuente | `maestro_suscriptores` |
| Tabla staging | `stg_cambios_suscriptor` |
| Tabla checkpoint | `estado_cdc_suscriptores` |

## Perfil generado

Para la ejecución de prueba se utilizó el perfil `equipo-3`.

| Variable | Resultado |
|---|---:|
| Total de suscriptores iniciales | 90 |
| Altas generadas | 9 |
| Modificaciones generadas | 13 |
| Bajas duras generadas | 9 |
| Total de cambios | 31 |
| `prob_baja_dura` | 0.29 |

> **Nota:** estos valores son simulados para efectos de esta entrega. Deben reemplazarse por los valores reales que entregue `generar_cambios_suscriptores.py --equipo equipo-3`.

---

# 2. Objetivo

Evaluar si una estrategia de Change Data Capture (CDC) basada únicamente en la marca temporal `updated_at` es suficiente para capturar los cambios realizados sobre la tabla `maestro_suscriptores`.

El análisis se concentra especialmente en las bajas duras, debido a que una fila eliminada físicamente deja de existir en la tabla fuente y, por lo tanto, no puede ser encontrada mediante una consulta basada en `updated_at`.

También se compara esta estrategia con una alternativa basada en el registro de transacciones de PostgreSQL.

---

# 3. Modelo implementado

Se utilizaron tres tablas principales:

- `maestro_suscriptores`
- `stg_cambios_suscriptor`
- `estado_cdc_suscriptores`

## 3.1. `maestro_suscriptores`

Es la tabla operacional que contiene el estado actual de los suscriptores.

```sql
CREATE TABLE maestro_suscriptores (
    subscriber_id INTEGER PRIMARY KEY,
    sector VARCHAR(50),
    estrato INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## 3.2. stg_cambios_suscriptor
Es la tabla de staging donde se almacenan los cambios detectados por el proceso CDC.
```sql
CREATE TABLE stg_cambios_suscriptor (
    id BIGSERIAL PRIMARY KEY,
    corrida_id UUID NOT NULL,
    equipo VARCHAR(20) NOT NULL,
    subscriber_id INTEGER NOT NULL,
    tipo_cambio VARCHAR(20) NOT NULL,
    sector VARCHAR(50),
    estrato INTEGER,
    detectado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
Los tipos de cambio utilizados son:
- ALTA
- MODIFICACION
Las bajas duras no aparecen porque la fila ya no existe en la tabla fuente.

3.3. estado_cdc_suscriptores
Esta tabla almacena el checkpoint utilizado por el proceso.
```sql
CREATE TABLE estado_cdc_suscriptores (
    equipo VARCHAR(20) PRIMARY KEY,
    checkpoint TIMESTAMP NOT NULL,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Punto ciego

El problema ocurre porque:
DELETE
  ↓
La fila desaparece
  ↓
No existe updated_at
  ↓
El SELECT no puede detectar la baja

<Por esta razón, un destino que solo recibe altas y modificaciones puede conservar:
9 suscriptores fantasma que ya no existen en el origen.


## 5. Repetición y duplicados

Se restableció el checkpoint a:
2026-09-28 08:00:00

La corrida volvió a encontrar:
9 altas + 13 modificaciones = 22 filas

Por lo tanto, se generaron 22 duplicados lógicos.

Para evitarlos se propone utilizar un checkpoint monotónico:

```sql
UPDATE estado_cdc_suscriptores
SET
    checkpoint = GREATEST(checkpoint, :nuevo_checkpoint),
    actualizado_en = CURRENT_TIMESTAMP
WHERE equipo = :equipo;
```

## 6. Alternativas de mitigación

Baja lógica
Convertir el DELETE en un UPDATE:
```sql
UPDATE maestro_suscriptores
SET
    is_active = FALSE,
    updated_at = CURRENT_TIMESTAMP
WHERE subscriber_id = :subscriber_id;
```

1. Ventaja: sencilla y permite detectar la baja con timestamp.
2. Desventaja: requiere modificar el sistema de origen.
3. Reconciliación periódica
4. Comparar periódicamente las llaves del origen y destino.

Para un maestro de 90.000 filas y dos barridos diarios:
K = 90.000 × 2
K = 180.000 llaves/día

Detecta bajas, pero no indica exactamente cuándo ocurrieron.
CDC basada en WAL
Flujo:
maestro_suscriptores
        ↓
PostgreSQL WAL
        ↓
Logical Decoding
        ↓
stg_cambios_suscriptor

Permite capturar:
INSERT
UPDATE
DELETE

## 7. Comparación

| Alternativa | Detecta DELETE | Latencia | Carga al origen | Complejidad |
|---|---|---|---|---|
| Timestamp | No | Media | Consultas periódicas | Baja |
| Baja lógica | Sí | Media | Consultas + cambio origen | Media |
| Reconciliación | Sí | Media/Alta | Barridos periódicos | Media |
| CDC por WAL | Sí | Segundos | Baja carga de consultas | Alta |

## 8. Decisión del equipo
Se decide migrar maestro_suscriptores a CDC basada en registro de transacciones mediante PostgreSQL WAL y replicación lógica.

La razón principal es que equipo-3 generó:
9 bajas duras
0 bajas capturadas

Las bajas representan:
9 / 31 × 100 = 29,03 %

de todos los cambios.

Para una fuente relacionada con procesos de facturación, este punto ciego se considera demasiado importante para mantener únicamente CDC por timestamp.

La baja lógica es viable, pero requiere cambios en el origen. La reconciliación puede utilizarse como control adicional, pero no conserva el momento exacto de la baja.

## 9. Impacto sobre el sistema de origen
La CDC por timestamp genera consultas periódicas.

Para un intervalo de una hora:
N = 86400 / 3600 = 24 consultas/día
Latencia media = 30 minutos
Latencia máxima = 60 minutos

Para cada 5 segundos:
17.280 consultas/día
Latencia media = 2,5 segundos

Esto significa:
17.280 / 24 = 720 veces más consultas

Por lo tanto, reducir la latencia mediante consultas frecuentes aumenta considerablemente la carga sobre PostgreSQL.

La CDC por WAL reduce este tipo de consultas, aunque introduce mayor complejidad operacional y necesidad de monitorear la replicación.

## 10. Integración con T12 y T13
Las fuentes del proyecto tienen patrones diferentes:
Fuente	Patrón	Estrategia
stg_lecturas	Incremental	Watermark
stg_estado_medidor	API	Paginación + reintentos
maestro_suscriptores	Mutable	CDC

## 11. Reproducción
Levantar PostgreSQL:

```sql
docker compose up -d s12
docker compose ps

Generar cambios:
python generar_cambios_suscriptores.py --equipo equipo-3

Ejecutar CDC:
python cdc_timestamp.py --equipo equipo-3

Consultar cambios:
SELECT
    tipo_cambio,
    COUNT(*) AS cantidad
FROM stg_cambios_suscriptor
WHERE equipo = 'equipo-3'
GROUP BY tipo_cambio;

Consultar checkpoint:
SELECT *
FROM estado_cdc_suscriptores
WHERE equipo = 'equipo-3';
```

## 12. Conclusión
La prueba demuestra que la CDC basada únicamente en updated_at captura correctamente las altas y modificaciones, pero no puede detectar bajas físicas. Por esta razón se recomienda 
CDC basada en registro de transacciones, utilizando PostgreSQL WAL y replicación lógica, con reconciliación periódica como mecanismo de control adicional.La decisión considera costo, 
latencia, carga sobre el origen y riesgo de mantener información obsoleta.
