# Taller 15 — Carga distribuida del acueducto con PySpark

## La carga distribuida que se puede repetir, reconciliar y justificar con Spark UI

**Proyecto:** Plataforma de datos del acueducto  
**Sesión:** 15 — Spark  
**Equipo:** equipo-X  
**Tecnología:** PySpark 3.5.3  
**Modo:** `local[4]`  
**Memoria del controlador:** `1g`

---

# 1. Objetivo

El objetivo de este taller es implementar una carga distribuida de la capa refinada del proyecto del acueducto utilizando PySpark.

La carga debe cumplir tres condiciones principales:

1. El resultado debe ser correcto y reconciliarse contra los totales de control.
2. La carga debe poder ejecutarse nuevamente sin generar duplicados.
3. Las decisiones de configuración deben estar justificadas mediante cifras observadas en Spark UI.

La pregunta principal que orienta el taller es:

> ¿Qué ocurre cuando Spark reparte el procesamiento y cuánto cuesta mover los datos entre particiones?

Por esta razón, no se evalúa únicamente el tiempo de ejecución. También se observan:

- particiones;
- tareas;
- etapas;
- shuffle write;
- shuffle read;
- uso de memoria;
- caché;
- comportamiento de `reduceByKey` y `groupByKey`.

---

# 2. Flujo general

El proceso realizado en el taller puede resumirse así:

```text
Datos refinados
      ↓
Lectura con Spark
      ↓
Particiones
      ↓
Tasks
      ↓
Transformaciones
      ↓
Shuffle
      ↓
Agrupación por fecha y sector
      ↓
Suma del consumo
      ↓
Consolidado
      ↓
Reconciliación
      ↓
Hash y comprobación de reejecución
```
# 3. Conceptos principales
Partición
Parte del conjunto de datos que Spark procesa de forma independiente.
Partición → Task

Stage
Etapa de ejecución de Spark. Un shuffle normalmente separa stages.
Shuffle
Movimiento de datos entre particiones.

Es uno de los principales costos de Spark.
Narrow
Poco movimiento de datos.
map()
filter()

Wide
Requiere reorganización y puede generar shuffle.
reduceByKey()
groupByKey()
repartition()

Lazy Evaluation
Las transformaciones no se ejecutan inmediatamente. Spark espera una acción como:
count()collect()write()


# 4. reduceByKey vs groupByKey
reduceByKey combina datos antes del shuffle:
Datos
 ↓
Combinación local
 ↓
Shuffle
 ↓
Resultado

groupByKey puede mover más datos durante el shuffle.

Por eso:
reduceByKey suele ser preferible para agregaciones.

Las cifras de referencia de la sesión fueron:
reduceByKey  → 9.803 bytes
groupByKey   → 1.867.585 bytes

Estas cifras son de referencia y no deben presentarse como resultados propios.

# 5. Configuración

Configuración inicial:
Master: local[4]
Driver memory: 1g
AQE: true
Método: reduceByKey
Formato: Parquet

Se deben probar diferentes particiones de shuffle:
4
8
50

Cada configuración debe ejecutarse 3 veces.

# 6. Mediciones
Registrar en Spark UI:
Stages
Tasks
Shuffle Write
Shuffle Read
Tiempo

Tabla:
Particiones	Corrida 1	Corrida 2	Corrida 3	Mediana
4	[ ]	[ ]	[ ]	[ ]
8	[ ]	[ ]	[ ]	[ ]
50	[ ]	[ ]	[ ]	[ ]


La decisión debe basarse en las mediciones, no en una sola corrida.

# 7. Skew
Existe posible skew cuando un sector concentra muchos más datos que los demás.

Se identifica principalmente mediante:
Shuffle Read

Un sector dominante puede generar mayor carga en una task.

# 8. Cache
El cache permite reutilizar datos en varias acciones.
Sin cache:
Lectura → Acción 1
Lectura → Acción 2

Con cache:
Lectura → CACHE → Acción 1
                  Acción 2

Debe evaluarse si realmente mejora el tiempo.

# 9. Reconciliación e idempotencia
La salida debe coincidir con los datos de control.

Se verifican:
Filas
Suma de consumo
Hash

La carga debe ser reejecutable:
Ejecución 1 → Resultado
Ejecución 2 → Mismo resultado

Se utiliza:
overwrite

No se debe usar un filtro de calidad para cambiar el universo de datos de la reconciliación.

# 10. Decisiones de ingeniería
Documentar mínimo 3 decisiones, incluyendo obligatoriamente:
Número de particiones

También pueden evaluarse:
- reduceByKey vs groupByKey.
- Cache.
- Parquet vs CSV.
- Recursos de Spark.
Cada decisión debe justificarse con mediciones.

# 11. Bitácora
Registrar las ejecuciones en:
bitacora_carga_spark.jsonl

Debe incluir:
equipo
volumen
método
particiones
stages
tasks
shuffle_write
shuffle_read
tiempo
filas
hash
reconciliación

# 12. Reproducción
Generar ampliación
docker exec -it acueducto_spark_s15 \
python practica/generar_ampliacion_s15.py \
--equipo equipo-X

Cargar base
docker exec -it acueducto_spark_s15 \
python pipeline/carga_spark.py \
--equipo equipo-X \
--volumen base

Cargar ampliación
docker exec -it acueducto_spark_s15 \
python pipeline/carga_spark.py \
--equipo equipo-X \
--volumen ampliacion

Probar particiones
docker exec -it acueducto_spark_s15 \
python pipeline/carga_spark.py \
--equipo equipo-X \
--volumen ampliacion \
--metodo reduceByKey \
--particiones-mezcla 4

Cambiar 4 por:
8
50

Memoria
docker stats --no-stream acueducto_spark_s15

# 13. Resumen 
Spark toma los datos y los divide en particiones, que son procesadas mediante tasks agrupadas en diferentes stages. 
Cuando una operación como reduceByKey o groupByKey necesita reorganizar los datos, ocurre un shuffle, donde la información 
se mueve entre particiones. Por eso no siempre tener más particiones significa mayor velocidad: puede aumentar el paralelismo, 
pero también generar más tasks y más trabajo de coordinación. En este taller se prueban diferentes cantidades de particiones 
y se comparan sus tiempos, tasks y cantidades de Shuffle Read y Shuffle Write.

Además, se compara cómo diferentes decisiones afectan el rendimiento. reduceByKey normalmente resulta más eficiente porque combina
datos antes del shuffle, mientras que groupByKey puede mover una mayor cantidad de información. También se analiza el cache cuando 
los datos se reutilizan, el posible skew cuando un sector concentra demasiados datos y la diferencia entre Parquet y CSV. 
Finalmente, se comprueba que la carga sea reconciliable e idempotente, es decir, que los resultados coincidan con los datos de control 
y que ejecutar nuevamente el proceso produzca el mismo resultado.

| Aspecto | Qué se hace | Qué se observa |
|---|---|---|
| Datos | Carga de mediciones de consumo | 576.000 lecturas |
| Particiones | Se distribuyen los datos entre tareas | Relación entre particiones y tasks |
| Agregación | Agrupar por `fecha + sector` | 480 grupos resultantes |
| `reduceByKey` | Combina datos antes del shuffle | Menor volumen de datos transferidos |
| `groupByKey` | Envía los valores para agruparlos | Mayor uso de shuffle |
| Shuffle | Movimiento de datos entre particiones | `Shuffle Read` y `Shuffle Write` |
| Caché | Mantener datos reutilizables en memoria | Menor tiempo en consultas repetidas |
| Skew | Detectar particiones con más datos | Tasks con mayor `Shuffle Read` |
| Parquet | Guardar datos en formato columnar | Menor tamaño y lectura eficiente |
| CSV | Guardar datos en formato de texto | Mayor tamaño y lectura menos eficiente |
| Reconciliación | Comparar filas y consumo total | Verificar que los resultados coincidan |
| Idempotencia | Ejecutar nuevamente la carga | Mismos resultados sin duplicados |
| Medición | Probar diferentes configuraciones | Tiempo, tasks y shuffle |
| Decisiones | Elegir particiones, agregación, caché, formato, etc. | Justificación técnica |

La primera tabla presenta de manera más detallada cómo se trabaja la carga de datos en Spark, explicando cada elemento del proceso, desde las particiones 
y la agregación hasta el shuffle, la caché, el formato Parquet, la reconciliación y la idempotencia. La segunda tabla resume esos mismos conceptos de forma más sencilla, 
mostrando únicamente el elemento principal y su propósito dentro del proceso. En conjunto, ambas tablas permiten entender que Spark distribuye los datos entre tareas, 
realiza operaciones de agregación y movimiento de información entre particiones, y utiliza diferentes estrategias para mejorar el rendimiento y garantizar que los resultados sean correctos y reproducibles.


| Elemento | Resultado / propósito |
|---|---|
| Datos | 576.000 lecturas de consumo |
| Agregación | 480 grupos por fecha y sector |
| Particiones | Distribuyen el trabajo entre tasks |
| Shuffle | Mueve datos entre particiones |
| `reduceByKey` | Reduce datos antes del shuffle |
| `groupByKey` | Genera mayor movimiento de datos |
| Caché | Mejora consultas repetidas |
| Skew | Detecta distribución desigual |
| Parquet | Reduce tamaño y mejora lectura |
| Reconciliación | Comprueba que los resultados sean correctos |
| Idempotencia | Evita duplicados al repetir la carga |
| Medición | Compara tiempo, tasks y shuffle |
