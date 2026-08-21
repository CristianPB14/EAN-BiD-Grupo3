# Reto de Negocio S6: Justificación Técnica de Formatos

La decisión de transformar nuestra capa refinada a Parquet (zstd) tiene un impacto medible directo en los costos de infraestructura del acueducto:

*   **Ahorro de almacenamiento:** Logramos una reducción del espacio en disco de aproximadamente el **84%** al pasar de CSV a Parquet. Al multiplicar este ahorro por el factor de réplica proyectado a 12 meses (R=3), el impacto financiero es masivo.
*   **Velocidad de consulta:** Usando DuckDB, el análisis de agregación sobre Parquet respondió drásticamente más rápido. El CSV fue 33.6 veces más lento que el Parquet.
*   **Costo de procesamiento (CPU):** Comprimir en zstd requirió fracciones de segundo adicionales en escritura, un costo técnico marginal que se paga con creces al momento de leer.

**Recomendación gerencial:**
Estandarizar Parquet (zstd) en la capa refinada. Esta combinación reduce el volumen facturado de almacenamiento de objetos (MinIO/S3) y abarata las consultas analíticas al evitar escanear columnas innecesarias (column pruning). El CSV debe quedar estrictamente reservado como formato histórico en la capa cruda.