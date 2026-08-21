# T6 · Diseño de Formato y Codec

## 1. Patrón de acceso de la fuente
SECOP II es una fuente de datos que se consulta masivamente pero que rara vez se reescribe (los contratos firmados son inmutables en el tiempo). Nuestras consultas de auditoría generalmente analizan un número reducido de columnas (ej. `departamento` y `valor_del_contrato`) de las 85 totales, lo que hace vital el uso de un formato orientado a columnas para aprovechar la poda de columnas (column pruning).

## 2. Selección de formato y codec
A partir de la medición generada en `resultados/s6_tabla_codecs.md`, elegimos **Parquet con compresión ZSTD**:
*   **Parquet:** Nos otorga un esquema autodescriptivo y permite a los motores de consulta descartar las columnas no requeridas, superando en velocidad al CSV crudo en tareas analíticas.
*   **ZSTD:** Fue elegido por ofrecer el mejor equilibrio. Proporciona niveles de compresión virtualmente idénticos a gzip, pero con una penalización de CPU significativamente menor al momento de escribir los datos, abaratando el costo de procesamiento.