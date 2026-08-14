# S1 · Nivel 3 · Matriz de V dominante

Evidencia numérica en la V dominante; una línea de descarte en las otras cuatro. Basado en la última
medición disponible en `notebooks/s01_perfilamiento.ipynb` — vuelvan a confirmar tras re-ejecutar el
notebook con el entorno corregido.

| Fuente | Volumen | Velocidad | Variedad | Veracidad | Valor |
|---|---|---|---|---|---|
| **SECOP II** | **Dominante.** 200.000 filas de muestra, 85 columnas, 76,5 % de tipo texto, `k = 3,38` — el mayor volumen efectivo en memoria de las tres fuentes, y crece con cada nuevo proceso de contratación publicado. | Descartada: `COMPLETAR` — comparen frecuencia declarada del portal contra la frecuencia real observada en las marcas de tiempo. | Descartada: `COMPLETAR` — ¿el esquema de columnas se mantiene igual entre descargas? | Descartada: `COMPLETAR` — midan proporción de nulos por columna y duplicados de la clave antes de descartarla. | Descartada: `COMPLETAR` — ¿qué decisión de la organización cambia si SECOP II existe? |
| **IDEAM** | Descartada: 150.000 filas pero solo 13 columnas y `k = 3,25` — menor huella en memoria que SECOP II. | **Hipótesis a confirmar.** El diseño de la fuente (estaciones que reportan en alta frecuencia) sugiere velocidad como V dominante, pero esto es la hipótesis de la guía, no un resultado medido. `COMPLETAR`: midan la frecuencia real entre registros consecutivos de una misma estación. | Descartada: `COMPLETAR` | Descartada: `COMPLETAR` | Descartada: `COMPLETAR` |
| **GEIH** | Descartada: 29.611 filas, la muestra más pequeña de las tres. | Descartada: `COMPLETAR` | **Dominante, con una advertencia.** El perfilamiento detectó **una sola columna** en el archivo cargado (`proporcion_texto = 1.0`), pese a que el diccionario de variables de la GEIH documenta decenas de campos. Eso es evidencia directa de variedad — probablemente un separador de campo distinto a la coma, o la necesidad de leer el diccionario aparte antes de poder interpretar el archivo, tal como advierte la sección 2.3 de la guía. `COMPLETAR`: confirmen la causa exacta antes de dar esto por cerrado. | Descartada, pero **no verificada**: `COMPLETAR` | Descartada: `COMPLETAR` |

## Párrafo de cierre (máximo 120 palabras)

`COMPLETAR` — respondan: ¿qué tuvieron que medir para poder descartar? El caso de GEIH ya les dio un
ejemplo de qué significa "medir y no deducir": la proporción de texto de 1.0 no se dedujo, se
encontró al perfilar, y por sí sola ya es evidencia de variedad (un archivo delimitado mal leído). Usen
ese mismo estándar para las demás celdas antes de escribir el párrafo final.
