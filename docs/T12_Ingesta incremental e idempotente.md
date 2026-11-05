
## Objetivo

Implementar una ingesta incremental sobre la instancia del acueducto generada con el parámetro `--equipo`, 
utilizando un estado persistente mediante una marca de agua, control de duplicados mediante una clave de deduplicación y una transacción atómica.

El objetivo principal es demostrar que el proceso puede ejecutarse nuevamente sobre el mismo lote sin generar duplicados y que puede reprocesar una ventana previamente cargada sin modificar la marca de agua.
El criterio técnico central de la T12 establece que, al ejecutar dos veces consecutivas el script sobre el mismo lote de origen, `stg_lecturas` debe conservar el mismo número de filas y `estado_ingesta` debe 
mantenerse consistente.

---

## Arquitectura de la solución

El flujo implementado es:

```text
Generador de datos
       │
       │ --equipo equipo-X
       ▼
Lote de datos de la instancia
       │
       ▼
Lectura de estado_ingesta
       │
       ▼
Filtro incremental por marca de agua
       │
       ▼
INSERT INTO stg_lecturas
ON CONFLICT DO NOTHING
       │
       ▼
Actualización de estado_ingesta
       │
       ▼
COMMIT
```

Las dos tablas principales utilizadas son:

```text
stg_lecturas
estado_ingesta
```

Los nombres se mantienen exactamente como exige la tarea, debido a que los procesos posteriores del pipeline consumirán estas tablas.

---

# Configuración del entorno

## Levantar el entorno

```bash
docker compose --profile s12 up -d
```
Verificar los servicios:

```bash
docker compose --profile s12 ps
```

Verificar el modelo dimensional:

```bash
docker exec acueducto_postgres_s12 \
psql -U postgres -d acueducto \
-c "SELECT count(*) FROM hechos_lectura;"
```

La instancia base debe contener el modelo dimensional del acueducto.

---

# Generación de la instancia del equipo

Ejemplo:

```bash
python generar_datos_S12.py --equipo equipo-X
```

En nuestro caso:

```text
Identificador utilizado: equipo-X
```

### Parámetros obtenidos de nuestra instancia

| Parámetro | Valor |
|---|---:|
| Identificador | `equipo-X` |
| Número de medidores | `[VALOR]` |
| Volumen del lote | `[VALOR]` filas |
| Tasa de reentregas | `[VALOR]%` |
| Tasa de registros tardíos | `[VALOR]%` |
| Tamaño de lote | `[VALOR]` |
| Margen de traslape | `[VALOR]` |
| Frecuencia de carga | `[VALOR]` |

Estos valores deben corresponder a la instancia real utilizada por el equipo.

---

# Estructura de las tablas

## Tabla `stg_lecturas`

La tabla de staging almacena las lecturas recibidas.

```sql
CREATE TABLE IF NOT EXISTS stg_lecturas (
    meter_id      INTEGER NOT NULL,
    "timestamp"   TIMESTAMP NOT NULL,
    sector        VARCHAR(50) NOT NULL,
    consumo_m3    NUMERIC,
    presion_bar   NUMERIC,
    quality_flag  VARCHAR(20),

    PRIMARY KEY (meter_id, "timestamp")
);
```

La clave:

```text
(meter_id, timestamp)
```

permite identificar de manera única una lectura.

---

## Tabla `estado_ingesta`

Esta tabla mantiene el estado persistente de la ingesta.

```sql
CREATE TABLE IF NOT EXISTS estado_ingesta (
    sector              VARCHAR(50) PRIMARY KEY,
    ultima_marca_agua   TIMESTAMP NOT NULL,
    ultima_ejecucion    TIMESTAMP,
    filas_cargadas      INTEGER
);
```

Inicialización:

```sql
INSERT INTO estado_ingesta (
    sector,
    ultima_marca_agua,
    ultima_ejecucion,
    filas_cargadas
)
VALUES
    ('S-NORTE', '2000-01-01 00:00:00', NULL, 0),
    ('S-SUR',   '2000-01-01 00:00:00', NULL, 0),
    ('S-ESTE',  '2000-01-01 00:00:00', NULL, 0),
    ('S-OESTE', '2000-01-01 00:00:00', NULL, 0)
ON CONFLICT (sector) DO NOTHING;
```

La fecha `2000-01-01 00:00:00` funciona como valor inicial de la marca de agua.

---

# Estrategia de ingesta incremental

La estrategia implementada sigue cuatro pasos:

1. Leer la última marca de agua.
2. Seleccionar únicamente los registros posteriores a esa marca.
3. Insertar utilizando la clave de deduplicación.
4. Actualizar la marca de agua y confirmar todo en una misma transacción.

La marca de agua representa el punto hasta donde se ha procesado exitosamente la información.

---

# Script de ingesta

Archivo:

```text
src/ingesta_incremental.py
```
 Luego se coloca el codigo py
 
# `ON CONFLICT DO NOTHING` Usos

La tabla `stg_lecturas` tiene una clave primaria compuesta:

```sql
PRIMARY KEY (meter_id, "timestamp")
```

Cuando una lectura ya existe y el mismo lote vuelve a procesarse:

```sql
ON CONFLICT (meter_id, "timestamp")
DO NOTHING;
```

evita que se genere una segunda fila.

Por lo tanto:

```text
Primera ejecución → inserta las lecturas nuevas
Segunda ejecución → no genera duplicados
```

La garantía de idempotencia no depende únicamente de la marca de agua. La clave de deduplicación y el manejo del conflicto son parte fundamental del mecanismo.

---

# Transacción atómica

La inserción de datos y la actualización del estado se realizan dentro de la misma transacción:

```sql
BEGIN;

-- INSERT

-- UPDATE estado_ingesta

COMMIT;
```

En caso de error:

```sql
ROLLBACK;
```

Esto evita que la marca de agua avance si los datos no fueron cargados correctamente.

La estrategia implementada es:

```text
INICIO
   │
   ▼
Leer estado
   │
   ▼
Insertar datos
   │
   ▼
Actualizar watermark
   │
   ▼
COMMIT
   │
   ▼
Proceso exitoso
```

Si ocurre un error:

```text
INSERT
  │
  X error
  │
  ▼
ROLLBACK
  │
  ▼
Los datos y el estado vuelven al estado anterior
```

---

# Prueba de doble ejecución

La prueba consiste en ejecutar exactamente el mismo lote dos veces.

## Primera ejecución

Antes de ejecutar:

```sql
SELECT COUNT(*)
FROM stg_lecturas;
```

Resultado:

```text
Antes de la primera ejecución: [VALOR]
```

Ejecutamos:

```bash
python src/ingesta_incremental.py
```

Después:

```sql
SELECT COUNT(*)
FROM stg_lecturas;
```

Resultado:

```text
Después de la primera ejecución: [VALOR]
```

---

## Segunda ejecución

Se ejecuta nuevamente:

```bash
python src/ingesta_incremental.py
```

Luego:

```sql
SELECT COUNT(*)
FROM stg_lecturas;
```

Resultado:

```text
Después de la segunda ejecución: [VALOR]
```

### Evidencia

| Momento | Filas `stg_lecturas` |
|---|---:|
| Antes de la primera ejecución | `[VALOR]` |
| Después de la primera ejecución | `[VALOR]` |
| Después de la segunda ejecución | `[VALOR]` |

Resultado esperado:

```text
Conteo primera ejecución = Conteo segunda ejecución
```

Por ejemplo:

```text
Primera ejecución:  X filas
Segunda ejecución:  X filas
```

Esto demuestra que volver a ejecutar el mismo lote no genera duplicados.

---

# Verificación de `estado_ingesta`

Consulta utilizada:

```sql
SELECT
    sector,
    ultima_marca_agua,
    ultima_ejecucion,
    filas_cargadas
FROM estado_ingesta
ORDER BY sector;
```

Resultado de la primera ejecución:

```text
[PEGAR AQUÍ RESULTADO REAL]
```

Resultado de la segunda ejecución:

```text
[PEGAR AQUÍ RESULTADO REAL]
```

La marca de agua no debe retroceder.

La única información que puede cambiar entre ejecuciones exitosas es, principalmente, `ultima_ejecucion`.

---

# Verificación adicional del contenido

Para comprobar que no solamente coincide el número de filas, también se verifica el consumo:

```sql
SELECT
    COUNT(*) AS total_filas,
    SUM(consumo_m3) AS consumo_total
FROM stg_lecturas;
```

Primera ejecución:

```text
Filas: [VALOR]
Consumo: [VALOR]
```

Segunda ejecución:

```text
Filas: [VALOR]
Consumo: [VALOR]
```

Los valores deben mantenerse iguales.

---

# Reproceso de ventana — Nivel 2

El reproceso de ventana es obligatorio en T12.

El objetivo es demostrar que una ventana que ya fue cargada puede abrirse nuevamente sin duplicar registros y sin modificar la marca de agua.

## Estado inicial

Para el día 1:

```text
Filas cargadas inicialmente: [VALOR]
```

---

## Crear un hueco de tres horas

Se eliminan las lecturas correspondientes a tres horas de un sector.

Ejemplo:

```sql
DELETE FROM stg_lecturas
WHERE sector = 'S-NORTE'
  AND "timestamp" >= '[FECHA] 00:00:00'
  AND "timestamp" <  '[FECHA] 03:00:00';
```

Registrar:

```text
Filas eliminadas: [VALOR]
```

---

## 14.3 Ejecutar la ingesta diaria

Se vuelve a ejecutar la ingesta normal:

```bash
python src/ingesta_incremental.py
```

Resultado esperado:

```text
Filas recuperadas por la ingesta diaria: 0
```

Esto sucede porque las lecturas eliminadas pertenecen a una ventana temporal anterior a la marca de agua.

---

# Función de reproceso

El reproceso no utiliza el filtro normal de la marca de agua.

Ejemplo:

```python
def reprocesar_ventana(conn, sector, inicio, fin):

    with conn.cursor() as cur:

        cur.execute(
            """
            INSERT INTO stg_lecturas (
                meter_id,
                "timestamp",
                sector,
                consumo_m3,
                presion_bar,
                quality_flag
            )
            SELECT
                meter_id,
                "timestamp",
                sector,
                consumo_m3,
                presion_bar,
                quality_flag
            FROM lote_entrante
            WHERE sector = %s
              AND "timestamp" >= %s
              AND "timestamp" < %s

            ON CONFLICT (meter_id, "timestamp")
            DO NOTHING;
            """,
            (
                sector,
                inicio,
                fin
            )
        )

    # IMPORTANTE:
    # El reproceso NO modifica estado_ingesta.
```

---

# Resultado del reproceso

### Antes del reproceso

```text
Filas existentes: [VALOR]
Filas eliminadas: [VALOR]
```

### Primer reproceso

```text
Filas recuperadas: [VALOR]
```

El resultado debe ser:

```text
Filas recuperadas = Filas eliminadas
```

### Segundo reproceso

Se ejecuta nuevamente:

```bash
python src/reprocesar.py
```

Resultado esperado:

```text
Filas recuperadas: 0
```

### Marca de agua

Antes:

```text
[VALOR]
```

Después del primer reproceso:

```text
[VALOR]
```

Después del segundo reproceso:

```text
[VALOR]
```

La marca de agua debe permanecer igual.

---

# Evidencia del Nivel 2

Archivo:

```text
evidencia_nivel2_equipo-X.md
```

Contenido:

```markdown
# Evidencia Nivel 2 — equipo-X

## Estado inicial

Filas en stg_lecturas: [VALOR]

## Hueco generado

Sector: S-NORTE

Ventana:
- Inicio: [FECHA Y HORA]
- Fin: [FECHA Y HORA]

Filas eliminadas: [VALOR]

## Ingesta diaria

Filas recuperadas por la ingesta diaria: 0

## Primer reproceso

Filas recuperadas: [VALOR]

## Segundo reproceso

Filas recuperadas: 0

## Marca de agua

Antes del reproceso: [VALOR]

Después del primer reproceso: [VALOR]

Después del segundo reproceso: [VALOR]

## Conclusión

El reproceso recuperó exactamente las filas eliminadas.
La segunda ejecución del reproceso no generó nuevas filas.
La marca de agua no fue modificada.
```

---

# Decisión de la clave de deduplicación — Nivel 3

La estrategia seleccionada para `stg_lecturas` es:

```text
(meter_id, timestamp)
```

Se utiliza una clave compuesta porque identifica una lectura específica de un medidor en un instante determinado.

Implementación:

```sql
PRIMARY KEY (meter_id, "timestamp")
```

Y manejo del conflicto:

```sql
ON CONFLICT (meter_id, "timestamp")
DO NOTHING;
```

## Caso límite

La fuente legacy puede presentar un escenario en el que el timestamp no sea confiable.

Ejemplo:

```text
meter_id = 25
timestamp = 2024-06-01 10:00:00
consumo_m3 = 12.5
```

y posteriormente:

```text
meter_id = 25
timestamp = 2024-06-01 10:00:00
consumo_m3 = 15.2
```

En este escenario existe una misma clave pero valores diferentes.

La decisión del equipo debe indicar si:

```text
DO NOTHING
```

o:

```text
DO UPDATE
```

es apropiado para su caso.

### Decisión del equipo

```text
[ESCRIBIR AQUÍ LA DECISIÓN REAL DEL EQUIPO]
```

### Riesgo residual

```text
[DESCRIBIR AQUÍ EL RIESGO QUE EL EQUIPO ACEPTA]
```

La tarea exige probar la estrategia contra un caso límite y documentar el riesgo residual.

---

#  Decisiones sobre la instancia `--equipo`

## Identificador

```text
equipo-X
```

## Decisión tomada

```text
[DESCRIBIR LA DECISIÓN]
```

Ejemplos de decisiones posibles:

- tamaño del lote;
- margen de traslape;
- frecuencia de carga;
- momento en que se calcula la marca de agua.

### Riesgo o costo gestionado

```text
[EXPLICAR QUÉ RIESGO O COSTO SE ESTÁ CONTROLANDO]
```

---

# Full Load vs Incremental Load

Una carga completa vuelve a procesar todo el histórico.

Una carga incremental procesa únicamente los datos nuevos desde el último punto de corte.

### Comparación

| Característica | Full Load | Incremental |
|---|---|---|
| Datos procesados | Todo el histórico | Solo nuevos datos |
| Costo computacional | Mayor | Menor |
| Necesita watermark | No necesariamente | Sí |
| Necesita deduplicación | Recomendable | Sí |
| Reintentos | Pueden duplicar | Deben ser idempotentes |
| Crecimiento del costo | Crece con el histórico | Depende principalmente del nuevo lote |

Para esta tarea se selecciona:

```text
INGESTA INCREMENTAL
```

porque permite reducir el volumen de datos procesados y permite reanudar el proceso mediante una marca de agua persistente.

## Costo de cómputo evitado

### Carga completa

```text
Datos procesados por Full Load:
[VALOR]
```

### Carga incremental

```text
Datos procesados por Incremental:
[VALOR]
```

### Cálculo

```text
Costo evitado =
Costo Full Load - Costo Incremental
```

Resultado:

```text
Costo de cómputo evitado: [VALOR]
```

Los valores deben calcularse utilizando las cifras de la instancia real del equipo y no una cifra genérica del acueducto.

---

# Prueba de idempotencia

La idempotencia se verifica mediante la ejecución consecutiva del mismo lote.

```text
                    Primera ejecución
                           │
                           ▼
                    INSERT de datos
                           │
                           ▼
                    Actualización estado
                           │
                           ▼
                         COMMIT
                           │
                           ▼
                    N filas cargadas
                           │
                           │
                    Segunda ejecución
                           │
                           ▼
                 Mismo lote nuevamente
                           │
                           ▼
                  ON CONFLICT DO NOTHING
                           │
                           ▼
                       0 nuevas filas
                           │
                           ▼
                  Mismo estado de datos
```

Resultado:

```text
Primera ejecución  → [N] filas
Segunda ejecución  → [N] filas

Duplicados → 0
```

Por lo tanto, la ejecución repetida produce el mismo estado final.

---

# Consultas de validación

## Conteo total

```sql
SELECT COUNT(*)
FROM stg_lecturas;
```

## Conteo por sector

```sql
SELECT
    sector,
    COUNT(*) AS filas
FROM stg_lecturas
GROUP BY sector
ORDER BY sector;
```

## Verificar duplicados

```sql
SELECT
    meter_id,
    "timestamp",
    COUNT(*) AS cantidad
FROM stg_lecturas
GROUP BY
    meter_id,
    "timestamp"
HAVING COUNT(*) > 1;
```

Resultado esperado:

```text
0 filas
```

## Estado de la ingesta

```sql
SELECT
    sector,
    ultima_marca_agua,
    ultima_ejecucion,
    filas_cargadas
FROM estado_ingesta
ORDER BY sector;
```

## Consumo total

```sql
SELECT
    SUM(consumo_m3) AS consumo_total
FROM stg_lecturas;
```

# Conclusión

Aprendimos a implementar una ingesta incremental para la plataforma de datos del acueducto utilizando una marca de agua persistente, una clave de deduplicación y una transacción atómica.
La prueba de doble ejecución permite verificar que volver a procesar el mismo lote no genera duplicados. El reproceso de una ventana previamente cargada demuestra que las filas eliminadas 
pueden recuperarse sin mover la marca de agua.
La solución queda preparada para que los procesos posteriores del pipeline consuman `stg_lecturas` como fuente de staging confiable.
El resultado más importante de la implementación es que el proceso deja de depender de que el script nunca se ejecute dos veces. El reintento pasa a ser una operación controlada e idempotente.

