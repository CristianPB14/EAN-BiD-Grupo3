# S6 · Reto de negocio · Bajar el costo de almacenamiento sin frenar las consultas

**Competencia: Emprendimiento Sostenible · Dirigido a la gerencia**

**Recomendación:** estandarizar Parquet con compresión ZSTD en la capa refinada del lago. Reduce el
espacio facturado en un 83 % y hace las consultas 34 veces más rápidas, a cambio de menos de dos
segundos adicionales de procesamiento cada vez que se carga el dato.

## 1. El ahorro de espacio

Sobre la muestra real de contratación pública que maneja el equipo:

| | Tamaño | Reducción |
|---|---|---|
| CSV, formato actual | **326,9 MB** | — |
| Parquet con ZSTD | **52,9 MB** | **−83 %** |

Llevado al volumen proyectado a doce meses de la ficha técnica del proyecto, y multiplicado por el
factor de réplica 3 que ya recomendamos para proteger el dato:

| Formato | Volumen a 12 meses | Espacio facturado con 3 copias |
|---|---|---|
| CSV | 0,5468 GB | 1,6404 GB |
| Parquet ZSTD | 0,0927 GB | 0,2781 GB |
| **Ahorro** | | **1,36 GB, un 83 % menos** |

El ahorro no es un porcentaje abstracto: **se multiplica por el número de copias que guardamos**.
Cada gigabyte que dejamos de escribir es un gigabyte que dejamos de pagar tres veces.

## 2. El efecto en la velocidad

La misma consulta de auditoría —valor promedio contratado por departamento— sobre los dos formatos,
devolviendo idéntico resultado:

| Formato | Tiempo de respuesta |
|---|---|
| CSV | 0,5659 s |
| Parquet ZSTD | 0,0168 s |
| | **33,6 veces más rápido** |

La razón, en términos no técnicos: el CSV obliga a leer las 85 columnas de cada contrato para
responder una pregunta que solo necesita dos. Parquet guarda cada columna por separado, así que lee
únicamente las dos que la pregunta pide y deja las otras 83 sin tocar.

**El ahorro y la velocidad no compiten entre sí.** Es lo contrario de lo que suele temerse al
comprimir: aquí el archivo más pequeño es además el que se consulta más rápido, porque hay menos
bytes que traer del disco.

## 3. El costo técnico

Comprimir con ZSTD cuesta **1,651 segundos** de procesamiento al escribir el archivo, frente a
**1,205 segundos** del codec más liviano disponible. Son **0,45 segundos adicionales** por carga, y
se pagan una sola vez cada vez que el dato se genera.

Descartamos gzip, la alternativa que más comprime, precisamente por su costo: tarda **7,224
segundos**, es decir **4,4 veces más que ZSTD**, y a cambio solo entrega un archivo un 4,4 % más
pequeño. No compensa.

## 4. La recomendación

Adoptar Parquet con ZSTD como formato estándar de la capa refinada y de la consolidada. El CSV queda
reservado exclusivamente para la capa cruda, donde su valor no es la eficiencia sino la fidelidad:
es el dato tal como lo entregó la fuente oficial, sin transformar, y por eso debe permanecer intacto
como respaldo verificable ante cualquier auditoría.

**Cuándo revisar esta decisión.** Si el patrón de uso cambia y el dato pasa a reescribirse varias
veces al día, el equilibrio se inclinaría hacia un codec más rápido de escribir. Mientras el dato
siga siendo de escritura ocasional y consulta intensiva, esta recomendación se sostiene.

---

### Declaración de uso de asistentes de inteligencia artificial

Estructura y redacción de reto de negocio realizada con ayuda de Claude y Gemini, luego de analizadas las cifras entre el grupo de trabajo.
