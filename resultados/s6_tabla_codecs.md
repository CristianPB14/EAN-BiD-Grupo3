# S6 · Comparación de Codecs y Tiempos de Consulta

| Formato | Tamaño (B) | Escr (s) | Lect sel (s) | vs CSV |
|---|---|---|---|---|
| CSV | 326,908,764 | - | - | - |
| snappy | 86,467,848 | 1.205 | 0.0094 | -74% |
| gzip | 52,964,557 | 7.224 | 0.0107 | -84% |
| zstd | 55,425,021 | 1.651 | 0.0089 | -83% |

## Medición de Motor Analítico (DuckDB)
- **Parquet (zstd):** 0.0168 s
- **CSV:** 0.5659 s
**Conclusión:** El CSV es 33.6 veces más lento entregando el mismo resultado.
