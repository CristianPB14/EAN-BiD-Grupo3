# T5 · Convención de Arquitectura del Lago de Datos

## 1. Mapa de Capas y Fronteras de Procesamiento

Nuestro lago de datos se divide en tres niveles lógicos (buckets), cada uno con reglas estrictas de procesamiento para SECOP II:

*   **Capa Cruda (`cruda/`):** Almacena el archivo CSV tal cual es descargado del portal de Datos Abiertos. No se altera el separador, no se cambian tipos de datos y no se eliminan filas inválidas. Es un espejo exacto de la fuente pública.
*   **Capa Refinada (`refinada/`):** El dato adquiere estructura. Aquí se cambian los tipos de datos (fechas a `datetime`, cuantías a numéricos), se eliminan las comas internas que rompen el CSV, y se guarda en formato columnar `Parquet` para eficiencia de lectura.
*   **Capa Consolidada (`consolidada/`):** Agrupa y cruza los datos refinados para responder a preguntas de negocio específicas (ej. tablas resumen con totales de presupuesto público agrupados por modalidad de contratación y departamento).

**Regla de oro de inmutabilidad:** Los errores estructurales (como las comas mal puestas en las descripciones de los contratos de SECOP) se corrigen siempre aguas abajo (al pasar de Cruda a Refinada). **Nunca se reescribe el archivo de la capa Cruda.** Esto garantiza que, si descubrimos una falla en nuestra lógica de limpieza en el futuro, siempre podemos volver al dato original y reprocesar el lago entero.

## 2. Convención de Nomenclatura de Rutas

Para garantizar que cualquier analista pueda ubicar un dato sin preguntar, establecemos las siguientes convenciones de partición:

### Capa Cruda
Plantilla: `cruda/<fuente>/anio=YYYY/mes=MM/dia=DD/<archivo>.<ext>`
*   **Ejemplo:** `cruda/secop/anio=2026/mes=08/dia=19/contratos.csv`
*   **Justificación de Fecha:** Utilizamos la fecha de *publicación/firma* del contrato en el portal, no la fecha en que el script descargó el archivo. Esto mantiene la coherencia cronológica legal del proceso.

### Capa Refinada
Plantilla: `refinada/<fuente>/departamento=<departamento>/anio=YYYY/<entidad>.parquet`
*   **Ejemplo:** `refinada/secop/departamento=Cundinamarca/anio=2026/procesos_limpios.parquet`
*   **Justificación de Partición:** Particionamos primero por `departamento` porque las consultas analíticas sobre contratación pública y derecho administrativo casi siempre se filtran primero por jurisdicción territorial antes de analizar los años o entidades específicas.

### Capa Consolidada
Plantilla: `consolidada/<dominio_negocio>/<tabla_agregada>/anio=YYYY/<archivo>.parquet`
*   **Ejemplo:** `consolidada/auditoria_presupuestal/modalidad_vs_cuantia/anio=2026/totales.parquet`

## 3. Justificación del Formato `clave=valor`
En todas las capas utilizamos rutas del estilo `anio=2026` en lugar de simplemente `2026`. Esta convención (estilo Hive) permite que motores de consulta masiva (como Spark, Trino o Athena) apliquen *poda de particiones* (Partition Pruning). Al leer la ruta, el motor interpreta `anio` como una columna real y descarta carpetas enteras sin necesidad de abrir los archivos por debajo, optimizando drásticamente los costos y tiempos de consulta.