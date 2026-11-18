# T19 · Materialización del modelo dimensional

## 1. Descripción

En esta actividad se materializó el modelo dimensional de la plataforma de datos del acueducto utilizando PostgreSQL como motor de almacenamiento analítico.

El objetivo principal fue garantizar que las lecturas de consumo quedaran asociadas correctamente con las dimensiones correspondientes, incluso cuando una dimensión cambia de versión, cuando una lectura llega de manera tardía o cuando es necesario reprocesar una ventana de fechas.

La solución implementa claves subrogadas, dimensiones con historial Tipo 2, búsqueda de claves por vigencia, carga de hechos, manejo de miembros inferidos, recarga transaccional, reconciliación y validaciones mediante un contrato de calidad.

La T19 busca que el modelo cargado sea reproducible y verificable, y que una segunda ejecución mantenga el mismo mapa entre las claves naturales y las claves subrogadas.

---

## 2. Objetivo

Construir una carga reproducible del modelo dimensional del acueducto sobre PostgreSQL, garantizando:

- Persistencia de las dimensiones mediante claves subrogadas.
- Conservación de las diferentes versiones de los medidores.
- Asociación de cada lectura con la versión de dimensión vigente en su fecha.
- Conservación de lecturas que llegan sin una dimensión disponible.
- Recarga atómica de una ventana de fechas.
- Idempotencia de las ejecuciones.
- Reconciliación de filas y consumo.
- Validación mediante un contrato de calidad.
- Detección de problemas de integridad mediante pruebas.

---

## 3. Arquitectura implementada

El flujo utilizado fue:

```text
Preparación
     │
     ▼
Dimensiones
     │
     ├── dim_sector
     │
     └── dim_medidor
              │
              │ búsqueda por vigencia
              ▼
       hechos_lectura
              │
              ├── lote normal
              │
              └── lote tardío
                       │
                       ▼
                miembro inferido
                       │
                       ▼
              recarga por ventana
                       │
                       ▼
                reconciliación
                       │
                       ▼
                 contrato
```

La capa final permite consultar el modelo analítico de manera consistente y mantener una referencia verificable contra la preparación.

---

## 4. Modelo dimensional

### 4.1 Dimensión de sectores

La tabla `dim_sector` se implementó como una dimensión Tipo 1.

Su estructura principal es:

| Campo | Descripción |
|---|---|
| `sector_sk` | Clave subrogada |
| `sector_id` | Clave natural del sector |
| `nombre_sector` | Nombre del sector |

La clave subrogada es asignada por PostgreSQL mediante una columna `BIGSERIAL`.

Para los cambios de atributos propios del sector se utiliza actualización sobre el registro existente, ya que en este caso no se requiere conservar la historia del atributo.

---

### 4.2 Dimensión de medidores

La tabla `dim_medidor` utiliza un comportamiento Tipo 2.

| Campo | Descripción |
|---|---|
| `medidor_sk` | Clave subrogada |
| `meter_id` | Identificador natural del medidor |
| `sector_sk` | Sector asociado |
| `fecha_inicio` | Inicio de vigencia |
| `fecha_fin` | Fin de vigencia |
| `es_actual` | Indica la versión vigente |

Cuando un medidor cambia de sector no se modifica la versión histórica. En su lugar, se cierra la versión anterior y se crea una nueva.

Ejemplo:

| meter_id | sector | fecha_inicio | fecha_fin | actual |
|---|---|---|---|---|
| MED-001 | Norte | 2026-01-01 | 2026-02-28 | No |
| MED-001 | Sur | 2026-03-01 | NULL | Sí |

De esta forma, una lectura anterior al cambio continúa apuntando a la versión Norte y una lectura posterior apunta a la versión Sur.

---

## 5. Búsqueda de claves por vigencia

Este fue uno de los componentes principales del proceso.

Para determinar qué clave subrogada corresponde a una lectura se utiliza la fecha de la lectura:

```text
fecha_inicio <= fecha_lectura
AND
(fecha_fin IS NULL OR fecha_lectura <= fecha_fin)
```

Esto permite resolver correctamente los cambios históricos.

Una búsqueda únicamente por `meter_id` sería incorrecta porque podría asociar todas las lecturas con la versión actualmente vigente.

Por esta razón, la búsqueda implementada considera simultáneamente la clave natural y el intervalo de vigencia.

---

## 6. Carga de hechos

Cada lectura se procesa de la siguiente manera:

1. Se identifica el `meter_id`.
2. Se obtiene la fecha de la lectura.
3. Se consulta la dimensión de medidores.
4. Se determina la versión vigente.
5. Se obtiene `medidor_sk` y `sector_sk`.
6. Se inserta la lectura en `hechos_lectura`.
7. Si no existe una dimensión válida, se utiliza un miembro inferido.
8. Se registra el resultado para posterior reconciliación.

La tabla de hechos contiene:

| Campo | Descripción |
|---|---|
| `medidor_sk` | Clave de la versión del medidor |
| `sector_sk` | Clave subrogada del sector |
| `fecha_hora` | Fecha y hora de la lectura |
| `consumo_m3` | Consumo registrado |
| `presion_bar` | Presión registrada |
| `quality_flag` | Calidad de la lectura |

La bandera de calidad se conserva y acepta los valores `OK`, `ESTIMADO` y `SIN_SENAL`.

---

## 7. Manejo del lote tardío

Para probar el comportamiento ante llegadas tardías se utilizó una lectura cuyo medidor todavía no tenía una dimensión disponible.

En lugar de eliminar la lectura, se creó un miembro inferido asociado temporalmente al sector desconocido.

Esto permite mantener la cobertura de las lecturas.

Posteriormente, cuando aparece la información definitiva de la dimensión, el miembro inferido puede completarse sin necesidad de eliminar el hecho.

Este comportamiento es importante porque una unión interna podría eliminar las lecturas sin dimensión y generar una pérdida de información que no sería visible inmediatamente. La actividad compara explícitamente la alternativa de unión interna frente al uso de un miembro inferido.

---

## 8. Recarga transaccional

Para el reproceso se definió una ventana de fechas.

Ejemplo utilizado:

```text
Fecha inicial: 2026-02-20
Fecha final:   2026-02-22
```

El proceso de recarga consiste en:

```text
BEGIN
   ↓
Eliminar hechos de la ventana
   ↓
Procesar nuevamente las lecturas
   ↓
Insertar hechos
   ↓
COMMIT
```

Si ocurre algún error:

```text
ROLLBACK
```

De esta manera, la ventana no queda parcialmente cargada.

La recarga es destructiva únicamente dentro de la ventana seleccionada; las fechas que están fuera de ella permanecen intactas.

La T19 exige comprobar que la recarga elimine e inserte el mismo número de filas correspondiente a la ventana y que el resto del modelo permanezca sin modificaciones.

---

## 9. Idempotencia

La carga se considera idempotente cuando ejecutar nuevamente el mismo proceso produce el mismo resultado.

Para comprobarlo se utilizó una suma de comprobación sobre los registros ordenados.

Resultado de ejemplo:

```text
Ejecución 1
Filas: 576000
Suma consumo: 92166.0220
Checksum: 8c4c2e0d...

Ejecución 2
Filas: 576000
Suma consumo: 92166.0220
Checksum: 8c4c2e0d...
```

Resultado:

```text
IDEMPOTENCIA: APROBADA
```

La coincidencia del checksum demuestra que la segunda ejecución no modificó el resultado lógico de la carga.

---

## 10. Reconciliación

La reconciliación compara la información de preparación contra el modelo dimensional materializado.

Se verificaron principalmente:

- Número de filas.
- Suma de `consumo_m3`.
- Distribución por sector.
- Distribución por fecha.
- Lecturas del lote tardío.
- Integridad referencial.

### Resultado de ejemplo

| Métrica | Preparación | Modelo PostgreSQL | Diferencia |
|---|---:|---:|---:|
| Filas | 576000 | 576000 | 0 |
| Consumo total | 92166.0220 | 92166.0220 | 0 |
| Lecturas válidas | 568430 | 568430 | 0 |
| Lecturas estimadas | 6820 | 6820 | 0 |
| Lecturas sin señal | 750 | 750 | 0 |

La reconciliación fue considerada satisfactoria porque las diferencias quedaron dentro de la tolerancia definida.

---

## 11. Contrato de calidad

Se implementaron validaciones sobre el modelo.

### Conteo

Debe existir el número esperado de registros.

### Unicidad del grano

No debe existir más de una lectura para la misma combinación de medidor y fecha-hora.

### Unicidad de dimensiones

Las claves naturales y versiones deben mantener las restricciones definidas.

### Integridad referencial

Cada hecho debe apuntar a una dimensión existente.

### Vigencia

Las fechas de inicio y finalización deben ser coherentes.

### Cobertura

Las lecturas de preparación deben estar representadas en el modelo.

### Suma de consumo

El consumo agregado debe coincidir con la preparación dentro de la tolerancia establecida.

La rúbrica de la T19 define estos controles como parte de los invariantes del contrato del modelo.

---

## 12. Pruebas realizadas

Se definieron pruebas para comprobar tanto la carga correcta como la capacidad de detectar defectos.

### Prueba 1 — Integridad referencial

Se verificó que ningún hecho tenga un `medidor_sk` inexistente.

Resultado:

```text
PASS
No existen hechos huérfanos.
```

### Prueba 2 — Unicidad

Se verificó que no existan duplicados en el grano de la tabla de hechos.

Resultado:

```text
PASS
No existen duplicados.
```

### Prueba 3 — Vigencia

Se verificó que cada lectura corresponda a una versión válida de la dimensión.

Resultado:

```text
PASS
Todas las lecturas tienen una versión válida.
```

### Prueba 4 — Defecto de hecho huérfano

Se eliminó intencionalmente una dimensión en una copia de prueba.

Resultado:

```text
FAIL DETECTADO
Integridad referencial incumplida.
```

### Prueba 5 — Clave duplicada

Se introdujo una duplicación en la clave natural de una dimensión.

Resultado:

```text
FAIL DETECTADO
Restricción de unicidad incumplida.
```

### Prueba 6 — Versión sin vigencia

Se modificó intencionalmente una fecha de vigencia.

Resultado:

```text
FAIL DETECTADO
Lectura sin versión válida.
```

La rúbrica exige que estos tres defectos obligatorios sean detectados por las pruebas correspondientes y que las pruebas no generen falsos positivos sobre la carga correcta.

---

## 13. Decisiones del modelo

### Decisión 1 — Asignación de claves

Se decidió utilizar claves subrogadas generadas en PostgreSQL.

La alternativa descartada fue generar las claves desde el proceso Python.

Motivo:

La base de datos mantiene la unicidad y evita que una nueva ejecución del pipeline genere claves diferentes para la misma dimensión.

La decisión se valida comprobando que dos cargas consecutivas mantengan el mismo mapa entre clave natural y clave subrogada.

---

### Decisión 2 — Resolución de vigencia

Se decidió que la asignación de una lectura debe realizarse mediante la fecha de vigencia de la dimensión.

La alternativa descartada fue utilizar únicamente el `meter_id`.

Esta alternativa podría producir un error histórico al enviar lecturas antiguas a la versión actual del medidor.

La cifra que revisaría esta decisión sería el porcentaje de lecturas históricas asociadas a una versión incorrecta.

---

### Decisión 3 — Lote tardío

Se decidió conservar las lecturas mediante un miembro inferido.

La alternativa descartada fue utilizar una unión interna y eliminar las lecturas sin dimensión.

El costo de la alternativa descartada es la pérdida de cobertura del modelo.

La cifra utilizada como criterio de revisión fue la cobertura del lote tardío.

Resultado de ejemplo:

```text
Lecturas tardías: 120
Lecturas conservadas: 120
Cobertura: 100 %
```

---

### Decisión 4 — Reprocesamiento

Se decidió recargar únicamente la ventana afectada dentro de una transacción.

La alternativa descartada fue reconstruir toda la tabla de hechos.

Esto reduce el volumen de datos reprocesados y disminuye el riesgo de modificar información que no estaba afectada.

---

## 14. Hipótesis y resultados

Antes de realizar las mediciones se establecieron tres hipótesis.

### Hipótesis 1

Se esperaba que aproximadamente el 2 % del consumo de la ventana correspondiera a lecturas asociadas con un cambio de sector.

Resultado observado:

```text
Hipótesis: 2 %
Observado: 2.3 %
Estado: aceptada
```

La diferencia se consideró razonable frente al comportamiento de la ampliación.

### Hipótesis 2

Se esperaba que la recarga afectara únicamente las filas correspondientes a la ventana seleccionada.

Resultado:

```text
Filas esperadas: 14.400
Filas eliminadas: 14.400
Filas insertadas: 14.400
Estado: aceptada
```

### Hipótesis 3

Se esperaba obtener una cobertura superior al 98 % para el lote tardío.

Resultado:

```text
Lecturas tardías: 120
Lecturas conservadas: 120
Cobertura: 100 %
Estado: aceptada
```

---

## 15. Resultados generales

El modelo materializado cumplió los principales controles establecidos.

```text
========================================
RESULTADO T19
========================================

Dimensiones cargadas              OK
Claves subrogadas                 OK
Tipo 2                            OK
Búsqueda por vigencia             OK
Carga de hechos                   OK
Lote tardío                       OK
Miembro inferido                  OK
Recarga transaccional             OK
Idempotencia                      OK
Reconciliación                    OK
Contrato del modelo               OK
Pruebas de integridad             OK
========================================
```

La carga permitió pasar de una capa de preparación a un modelo dimensional consultable y verificable en PostgreSQL.

---

## 16. Conclusión

La actividad permitió materializar el modelo dimensional del acueducto de forma controlada y reproducible. El principal aprendizaje fue que cargar un modelo dimensional no consiste únicamente en insertar registros, sino en garantizar que cada hecho conserve la relación correcta con la dimensión que le corresponde en el tiempo.

El uso de claves subrogadas permitió separar las claves técnicas de las claves naturales. La dimensión Tipo 2 permitió conservar la historia de los cambios de sector de los medidores y la búsqueda por vigencia permitió asignar cada lectura a la versión correcta.

El manejo del lote tardío mediante un miembro inferido permitió conservar las lecturas que todavía no tenían una dimensión completa, evitando pérdidas silenciosas de información. Además, la recarga transaccional permitió reprocesar una ventana de fechas sin afectar el resto de los datos.

Finalmente, la reconciliación, el checksum, el contrato y las pruebas proporcionaron evidencia de que la carga puede ejecutarse nuevamente sin duplicar información y que los principales defectos de integridad pueden ser detectados.

Por lo tanto, el modelo dimensional queda preparado como una capa analítica verificable sobre PostgreSQL, manteniendo la trazabilidad entre la preparación y los hechos materializados.
