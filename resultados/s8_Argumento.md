Claro, aquí tienes la explicación del **código en sí**, en varios párrafos:

## Idea general del notebook

Este script forma parte de un ejercicio (aparentemente del tema "T8 - Arquitectura") relacionado con **Big Data y sistemas de almacenamiento distribuido tipo HDFS** (Hadoop Distributed File System). El objetivo es analizar cómo se comportaría un dataset en un entorno distribuido: cuánto espacio ocupa, cómo se dividiría en bloques, cuánto costaría replicarlo, y qué diferencia hay entre guardar los datos en formato CSV versus un formato más eficiente como Parquet.

## Sección 1 — Configuración

Se definen dos variables clave: `BLOCK_SIZE_MIB = 128`, que representa el tamaño estándar de un bloque en HDFS (128 MiB es un valor típico en configuraciones reales de Hadoop), y `REPLICATION_FACTORS = [1, 2, 3]`, una lista de factores de réplica a evaluar. En HDFS, cada bloque de datos se replica varias veces en distintos nodos del clúster para tolerancia a fallos; un factor de réplica de 3 (el más común en producción) significa que cada bloque existe en 3 copias distintas.

## Sección 2 — Carga del dataset

Se usa `pandas` para leer un archivo CSV (`data/raw/datos.csv`) y cargarlo en un DataFrame llamado `df`. Luego se imprime cuántas filas y columnas tiene, y se muestra un preview con `df.head()` (las primeras 5 filas), algo estándar para verificar que los datos se cargaron bien antes de seguir procesando.

## Sección 3 — Cálculo de almacenamiento y réplica

Aquí se calcula cuánto espacio real ocupa el DataFrame en memoria usando `df.memory_usage(deep=True).sum()`, que devuelve el tamaño en bytes (el `deep=True` es importante porque calcula el tamaño real de las columnas tipo texto/objeto, no solo un estimado superficial). Ese valor se convierte a MiB (mebibytes, dividiendo entre 1024²).

Luego, para cada factor de réplica (1, 2 y 3), se calcula:
- **Almacenamiento total**: el tamaño del dataset multiplicado por el número de réplicas (simulando cuánto espacio ocuparía en el clúster si se guarda esa cantidad de copias).
- **Bloques HDFS necesarios**: usando `math.ceil()` para redondear hacia arriba, se calcula cuántos bloques de 128 MiB se necesitan para almacenar el dataset (si el dataset no llena un bloque completo, igual se cuenta como un bloque entero, porque así funciona HDFS).

Todo esto se organiza en una tabla (`tabla_replicacion`) usando un DataFrame de pandas, para comparar visualmente el impacto de cada factor de réplica.

## Sección 4 — Comparación CSV vs Parquet

Esta sección compara dos formatos de almacenamiento de datos:
- **CSV**: formato de texto plano, fila por fila, fácil de leer pero poco eficiente en espacio y velocidad.
- **Parquet**: formato binario columnar, mucho más usado en ecosistemas Big Data (Spark, Hadoop, Hive) porque comprime mejor los datos y permite lecturas más rápidas, especialmente cuando solo necesitas ciertas columnas.

El código mide, usando `time.perf_counter()` (un cronómetro de alta precisión), cuánto tiempo tarda en **leer** el CSV y cuánto tarda en **escribir** el mismo dataset como archivo Parquet (`df.to_parquet(...)`). Después, usando `os.path.getsize()`, obtiene el tamaño en bytes de ambos archivos en disco, los convierte a megabytes, y calcula el **porcentaje de reducción de tamaño** al usar Parquet en lugar de CSV con una fórmula simple de diferencia porcentual: `((tamaño_csv - tamaño_parquet) / tamaño_csv) * 100`. Todo esto se resume en una tabla comparativa (`comparacion`).

## Sección 5 — Resumen final

Finalmente, se imprime un resumen en consola con todos los resultados clave calculados anteriormente: el tamaño base del dataset, el tamaño de bloque HDFS usado, los factores de réplica evaluados, los tamaños de CSV y Parquet, y el porcentaje de reducción logrado. Es básicamente un reporte final en texto plano, útil para incluir como conclusión en un informe o entrega académica.

**En conjunto**, el notebook simula, de forma simplificada y sin necesidad de un clúster Hadoop real, los conceptos teóricos de **almacenamiento distribuido**: tamaño de bloque, replicación, y eficiencia de formatos de archivo — temas centrales en arquitecturas de Big Data como HDFS.
