# T6 · Diseño de Formato y Codec

**Sesión 6 · Formatos de archivo y compresión · Fuente: SECOP II**

## 1. Patrón de acceso de la fuente

SECOP II es una fuente que se consulta masivamente pero que **rara vez se reescribe**: los contratos
firmados son inmutables en el tiempo y solo se agregan registros nuevos. Nuestras consultas de
auditoría analizan un número reducido de columnas —típicamente `departamento` y
`valor_del_contrato`— de las **85 totales**, es decir apenas un 2,4 % del ancho de la tabla.

Ese patrón, escribir una vez y leer muchas veces pidiendo pocas columnas, es exactamente el caso
donde un formato orientado a columnas rinde más, porque permite al motor descartar las 83 columnas
que la consulta no pide sin llegar a leerlas del disco (*column pruning*).

## 2. La medición

Sobre la muestra completa de 200.000 filas y 326,9 MB de CSV, medida con la mediana de cinco
repeticiones (ver `resultados/s6_tabla_codecs.md`, generado por `src/s6_formatos.py`):

| Formato | Tamaño | vs CSV | Escritura | Lectura selectiva |
|---|---|---|---|---|
| CSV | 326,9 MB | — | — | — |
| snappy | 82,5 MB | −73,5 % | 1,205 s | 0,0094 s |
| gzip | **50,5 MB** | **−83,8 %** | 7,224 s | 0,0107 s |
| zstd | 52,9 MB | −83,0 % | **1,651 s** | **0,0089 s** |

## 3. Selección de formato y codec

Elegimos **Parquet con compresión ZSTD**.

**Por qué Parquet y no CSV.** Nos otorga un esquema autodescriptivo —el archivo lleva sus propios
tipos, de modo que desaparece la ambigüedad de tipos que sufrimos en la sesión 1— y permite al motor
de consulta descartar las columnas no requeridas. La ganancia no es marginal: sobre la misma
agregación por departamento, DuckDB respondió en 0,0168 s contra 0,5659 s del CSV, **33,6 veces más
rápido entregando exactamente el mismo resultado**.

**Por qué ZSTD y no gzip, con nuestros números.** gzip produce el archivo más pequeño, pero la
diferencia es estrecha y el precio es alto:

- gzip pesa **50,5 MB** frente a los **52,9 MB** de zstd: apenas un **4,4 % menos**.
- gzip tarda **7,224 s** en escribir frente a **1,651 s** de zstd: **4,4 veces más CPU**.

Pagar 4,4 veces el costo de escritura para ganar un 4,4 % de disco no se justifica en una capa
refinada que se regenera cada vez que reprocesamos desde la cruda. Además, zstd resultó ser el más
rápido de los tres en la lectura selectiva (0,0089 s), que es la operación que nuestro patrón de
acceso ejecuta con más frecuencia.

**Por qué no snappy.** Es el más rápido de escribir, pero deja el archivo en 82,5 MB: **56 % más
grande que zstd** por ahorrar medio segundo de escritura (1,205 s contra 1,651 s). Dado que el dato
se escribe una vez y se consulta muchas, ese medio segundo se paga una sola vez y los 30 MB extra se
pagan todos los meses en la factura de almacenamiento.

## 4. El compromiso, declarado

No elegimos el codec que más comprime ni el que más rápido escribe, sino el que mejor equilibra
ambas dimensiones **para nuestro patrón de acceso concreto**. Si SECOP II fuera una fuente que
reescribimos varias veces al día, snappy sería la elección correcta; si fuera un archivo histórico
que se consulta una vez al año, gzip lo sería. Es escritura poco frecuente con lectura intensiva y
selectiva, y ahí zstd domina.

Conviene además dimensionar el aporte de cada decisión por separado: pasar de CSV a Parquet ya
entrega el grueso del ahorro (de 326,9 MB a 82,5 MB con el codec más flojo, un −73,5 %). La elección
del codec afina sobre esa base, moviendo el resultado entre −73,5 % y −83,8 %. **La orientación
columnar pesa más que el codec**, y por eso la decisión de formato es la importante y la de codec es
el ajuste fino.

## 5. Alcance de la decisión

Esta elección aplica a la **capa refinada y a la consolidada**. La capa cruda conserva el CSV
original tal como llegó del portal, sin tocar, según la regla de inmutabilidad declarada en
`docs/T5_convencion_lago.md`. El Parquet resultante se depositó en el cubo `refinada` respetando la
convención de rutas `refinada/secop/departamento=<departamento>/anio=YYYY/`, y la evidencia de la
carga está en `resultados/s6_evidencia_lago.md`.

---

*Criterio de aceptación: la elección del codec se deriva de la medición propia registrada en
`resultados/s6_tabla_codecs.md` y del patrón de acceso declarado en la sección 1, no de una
recomendación general.*
