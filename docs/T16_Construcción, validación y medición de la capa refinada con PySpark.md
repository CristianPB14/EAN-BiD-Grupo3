##  1. Introducción

En la **Tarea T16** se desarrolla una nueva capa refinada utilizando **Apache Spark y PySpark**.

El objetivo no es solamente cargar los datos, sino construir un proceso que pueda ser:

- **Reejecutado** sin generar duplicados.
- **Reconciliado** contra las capas anteriores.
-  **Medido** bajo diferentes estrategias de procesamiento.
-  **Explicado** mediante decisiones técnicas.
-  **Verificado** mediante evidencias reproducibles.

La información corresponde a mediciones horarias de un acueducto. La base contiene:

- **200 medidores**
- **120 días**
- **24 mediciones por día**
- **4 sectores**
- **576.000 lecturas en total**

El volumen base se obtiene mediante:

```text
200 medidores × 120 días × 24 horas
= 576.000 lecturas
```

---

# 2. Objetivo

El objetivo de T16 es implementar una capa refinada utilizando **PySpark DataFrames**, manteniendo la trazabilidad y consistencia de los datos.

Específicamente, se busca:

1. Leer los archivos CSV de la capa `cruda/`.
2. Utilizar un esquema declarado.
3. Convertir correctamente los timestamps.
4. Crear columnas derivadas.
5. Clasificar los niveles de presión.
6. Escribir la información en formato Parquet.
7. Particionar por año, mes y día.
8. Ejecutar nuevamente el proceso sin duplicar información.
9. Reconciliar los resultados contra las capas anteriores.
10. Comparar diferentes implementaciones de la clasificación.
11. Comparar DataFrames frente a la línea base RDD.
12. Documentar las decisiones y resultados.

---

#  3. Estructura de los datos

La capa de entrada corresponde a:

```text
cruda/
```

Los archivos están organizados por día y contienen las siguientes columnas:

| Campo | Descripción |
|---|---|
| `meter_id` | Identificador del medidor |
| `timestamp` | Fecha y hora de la medición |
| `sector` | Sector del acueducto |
| `consumo_m3` | Consumo en metros cúbicos |
| `presion_bar` | Presión registrada en bar |
| `quality_flag` | Indicador de calidad |

Ejemplo de un registro:

```text
MED0001,2024-01-01 13:00:00,S-NORTE,0.214,3.223,OK
```

---

#  4. Esquema declarado

Una de las decisiones importantes de T16 es **no permitir que Spark infiera automáticamente el esquema**.

Se declara explícitamente el tipo de cada columna:

| Campo | Tipo Spark | Justificación |
|---|---|---|
| `meter_id` | `StringType` | Identificador del medidor |
| `timestamp` | `TimestampType` | Permite trabajar con fecha y hora |
| `sector` | `StringType` | Identificación del sector |
| `consumo_m3` | `DoubleType` | Variable numérica |
| `presion_bar` | `DoubleType` | Variable numérica |
| `quality_flag` | `StringType` | Estado de calidad |

Esto permite tener mayor control sobre la estructura de los datos y facilita la detección de valores que no puedan convertirse correctamente.

La lectura se realiza en modo:

```text
PERMISSIVE
```

De esta manera, los registros problemáticos pueden convertirse en valores nulos sin detener completamente el proceso.

---

#  5. Transformaciones realizadas

Después de leer los datos, se generan nuevas columnas a partir del timestamp y del indicador de calidad.

| Columna | Descripción |
|---|---|
| `fecha` | Fecha de la medición |
| `hora` | Hora de la medición |
| `es_confiable` | Indica si la medición tiene `quality_flag = OK` |
| `anio` | Año |
| `mes` | Mes en formato `MM` |
| `dia` | Día en formato `DD` |

Por ejemplo:

```text
timestamp = 2024-01-01 13:00:00
```

produce:

```text
fecha = 2024-01-01
hora  = 13
anio  = 2024
mes   = 01
dia   = 01
```

La columna:

```text
es_confiable
```

se obtiene mediante:

```text
quality_flag == "OK"
```

Se conserva toda la información original y solamente se agregan variables derivadas para facilitar el análisis.

---

# 6. Clasificación de la presión

Se crea la columna:

```text
nivel_presion
```

utilizando las siguientes reglas:

| Presión | Nivel |
|---:|---|
| `< 2.5` bar | 🔵 `baja` |
| `2.5 – 3.5` bar | 🟢 `normal` |
| `> 3.5` bar | 🔴 `alta` |
| `NULL` | `NULL` |

La clasificación se realiza mediante expresiones nativas de Spark.

Es importante conservar los valores nulos. Un valor faltante no significa que la presión sea normal.

---

#  7. Construcción de `refinada_spark`

Los datos transformados se almacenan en una nueva capa:

```text
refinada_spark/
```

El formato utilizado es:

```text
Parquet
```

y la información se particiona mediante:

```text
anio
mes
dia
```

La estructura esperada es:

```text
refinada_spark/
│
└── anio=2024/
    │
    ├── mes=01/
    │   ├── dia=01/
    │   ├── dia=02/
    │   ├── ...
    │   └── dia=31/
    │
    └── ...
```

Esta organización permite que Spark pueda aprovechar **partition pruning** cuando una consulta filtra por fecha.

---

# 8. Manejo del timestamp

La nueva capa utiliza:

```text
TimestampType
```

y se configura la sesión de Spark utilizando:

```text
UTC
```

Para la escritura en Parquet se establece:

```text
TIMESTAMP_MICROS
```

Esto significa que el timestamp se almacena con precisión de microsegundos.

Esta decisión es importante porque la capa heredada `refinada/` utiliza una representación temporal diferente.

Por lo tanto, durante la reconciliación se comparan los timestamps utilizando una representación compatible, evitando interpretar una diferencia de formato como una diferencia en los datos.

---

#  9. Reejecución del pipeline

Uno de los requisitos principales de T16 es demostrar que el proceso puede ejecutarse más de una vez sin generar duplicados.

Para cada volumen se realizan dos ejecuciones:

```text
1. Primera ejecución
2. Segunda ejecución
```

Los volúmenes evaluados son:

```text
base
ampliacion
```

Después de las dos ejecuciones se comparan:

- número de registros;
- contenido;
- hash;
- agrupaciones de control;
- existencia de duplicados.

La condición esperada es:

```text
Primera ejecución = Segunda ejecución
```

Por lo tanto:

```text
duplicados = 0
```

---

#  10. Reconciliación

La reconciliación permite comprobar que la nueva capa producida con Spark mantiene la misma información que las capas anteriores.

La comparación se realiza agrupando por:

```text
fecha
sector
quality_flag
```

Para cada grupo se verifican:

| Métrica | Validación |
|---|---|
| `rows` | Cantidad de registros |
| `sum(consumo_m3)` | Suma del consumo |
| `sum(presion_bar)` | Suma de presión |
| `min(timestamp)` | Primera medición |
| `max(timestamp)` | Última medición |

Para la **base** se compara contra:

```text
refinada/
consolidada/
```

Para la **ampliación** se compara contra:

```text
refinada/
totales_control.csv
```

El propósito es comprobar que el pipeline no:

- pierda registros;
- genere registros adicionales;
- modifique valores;
- altere las fechas;
- elimine registros por su calidad.

---

#  11. Comparación de variantes

T16 también permite estudiar tres formas diferentes de realizar la clasificación de presión.

## 11.1 Native Spark

Se utilizan expresiones propias de Spark:

```python
when()
otherwise()
```

La operación permanece dentro del motor de Spark y puede ser analizada por su optimizador.

---

## 11.2 Python UDF

Se utiliza una función Python aplicada registro por registro.

Conceptualmente:

```text
1 fila → 1 llamada a Python
```

Para la base:

```text
576.000 filas
```

la función puede ser invocada aproximadamente:

```text
576.000 veces
```

Esto genera mayor comunicación entre Spark y Python.

---

## 11.3 Pandas UDF

La tercera alternativa utiliza:

```text
Pandas + Apache Arrow
```

En lugar de procesar una fila por llamada, se procesan lotes de registros.

Conceptualmente:

```text
Spark → lote → Python/Pandas → Spark
```

Esto reduce el número de llamadas individuales y aprovecha el procesamiento vectorizado.

---

#  12. Metodología de medición

Para evitar conclusiones basadas en una sola ejecución, cada variante se mide mediante:

```text
1 calentamiento
+
3 ejecuciones medidas
```

La ejecución de calentamiento se descarta.

Para las tres ejecuciones medidas se obtiene:

```text
mínimo
máximo
mediana
```

La mediana se utiliza como indicador principal porque reduce la influencia de ejecuciones atípicas.

La operación ejecutada debe consumir realmente:

```text
nivel_presion
```

Esto es importante porque Spark utiliza **evaluación perezosa** y puede eliminar transformaciones que no sean necesarias para producir el resultado final.

---

#  13. Condiciones de medición

Se realizan las mediciones bajo dos condiciones.

### Condición A — CSV

La columna `presion_bar` se obtiene directamente desde los archivos CSV.

```text
CSV
 ↓
Spark
 ↓
clasificación
 ↓
resultado
```

Esta condición representa el flujo completo de lectura y transformación.

### Condición B — memoria

La columna de presión se mantiene en memoria mediante `cache()`.

```text
presion_bar
 ↓
cache()
 ↓
clasificación
 ↓
resultado
```

Esta condición permite observar mejor el costo específico de la transformación.

---

#  14. Reprocesamiento de seis días

También se prueba el comportamiento del pipeline cuando solamente es necesario reprocesar seis días.

La prueba se realiza sobre una **copia de la capa base**, evitando modificar la información original.

Se comparan dos estrategias:

```text
sobrescritura estática
sobrescritura dinámica
```

### Sobrescritura estática

Puede reemplazar el destino completo aunque solamente se estén procesando seis días.

Esto puede provocar pérdida de información.

### Sobrescritura dinámica

Solamente modifica las particiones correspondientes a los días procesados.

Por ejemplo:

```text
120 días originales
        ↓
reprocesamiento de 6 días
        ↓
114 particiones intactas
6 particiones actualizadas
```

Por esta razón, la estrategia dinámica es la alternativa recomendada para el reprocesamiento.

---

#  15. DataFrame frente a RDD

T16 también conecta los resultados con la línea base desarrollada anteriormente mediante RDD.

La principal diferencia es que un:

```text
RDD
```

trabaja con objetos que Spark considera menos estructurados, mientras que un:

```text
DataFrame
```

contiene información estructurada sobre columnas y tipos.

Esto permite que Spark pueda optimizar las operaciones realizadas sobre DataFrames.

Por ejemplo:

```python
df.groupBy("sector").agg(...)
```

puede ser analizado y optimizado por el motor de Spark.

Esto significa que un DataFrame no necesariamente tiene que mover menos bytes que un RDD para obtener un mejor tiempo.

También influyen:

- número de tareas;
- particiones;
- paralelismo;
- optimizaciones;
- Adaptive Query Execution;
- costo de serialización;
- distribución de los datos.

Por esta razón, la conclusión final debe basarse en las mediciones obtenidas por el equipo.

---

# 16. Resultados esperados

Al finalizar T16 se espera demostrar que:

| Validación | Resultado esperado |
|---|---|
| Esquema declarado | ✅ |
| Lectura de CSV | ✅ |
| Columnas derivadas | ✅ |
| Clasificación de presión | ✅ |
| Particionado diario | ✅ |
| Escritura Parquet | ✅ |
| Timestamp en microsegundos | ✅ |
| Reejecución | Sin duplicados |
| Reconciliación | Consistente |
| Reprocesamiento | Sin pérdida de datos |
| Comparación de UDF | Medida |
| DataFrame vs RDD | Medido |
| Evidencia técnica | Documentada |

---

#  17. Archivos generados

La implementación de T16 utiliza principalmente:

```text
pipeline/
├── refinada_spark.py
└── verificar_etapa.py

bitacora_refinada_spark.jsonl

refinada_spark/

evidencia_nivel2_<equipo>.md
```

Además, se documentan las decisiones mediante ADR, una nota para gerencia y el puente entre las tareas anteriores.

---

#  18. Verificación de la etapa

La etapa se valida mediante el script:

```bash
python pipeline/verificar_etapa.py --etapa t16
```

El resultado esperado es:

```text
T16: APROBADA
```

También se verifica la continuidad con las etapas anteriores:

```bash
python pipeline/verificar_etapa.py --etapa t12
python pipeline/verificar_etapa.py --etapa t13
python pipeline/verificar_etapa.py --etapa t14
python pipeline/verificar_etapa.py --etapa t15
python pipeline/verificar_etapa.py --etapa t16
```

Esto permite demostrar que el trabajo realizado en T16 no funciona de manera aislada, sino que mantiene continuidad con el pipeline desarrollado durante el módulo.

---

#  19. ¿Qué estamos demostrando realmente?

T16 no se trata solamente de ejecutar un código de PySpark.

La actividad busca demostrar que somos capaces de construir un proceso de datos que sea:

```text
REPRODUCIBLE
      ↓
VALIDABLE
      ↓
MEDIBLE
      ↓
TRAZABLE
      ↓
REUTILIZABLE
```

Es decir, si otra persona toma el proyecto y sigue las instrucciones documentadas, debería poder ejecutar nuevamente el pipeline y obtener resultados equivalentes.

---

#  20. Conclusión

La Tarea T16 representa una evolución del proyecto hacia un pipeline de procesamiento más estructurado y reproducible.

A partir de los datos crudos del acueducto se construye una nueva capa refinada utilizando PySpark DataFrames, incorporando un esquema declarado, columnas derivadas, clasificación de presión, particionamiento diario y almacenamiento en Parquet.

Además, se comprueba que el proceso pueda ejecutarse nuevamente sin generar duplicados y que sus resultados sean consistentes con las capas construidas anteriormente.

La comparación entre **Spark nativo, Python UDF y Pandas UDF** permite analizar diferentes formas de ejecutar una misma transformación y comprender el impacto que tiene la comunicación entre Spark y Python.

Finalmente, la comparación entre **DataFrames y RDD** conecta esta actividad con las sesiones anteriores y permite evaluar las ventajas de utilizar APIs estructuradas y optimizadas por Spark.

En conjunto, T16 permite pasar de un procesamiento que simplemente "funciona" a un proceso que puede ser:

> **ejecutado, medido, validado, explicado y reproducido.** 🚀

---

##  Resumen del flujo completo

```text
                    DATOS CRUDOS
                         │
                         ▼
                    ┌─────────┐
                    │   CSV   │
                    └────┬────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    PySpark    │
                 │   DataFrame   │
                 └───────┬───────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
           Esquema   Columnas   Clasificación
           declarado derivadas    presión
              │          │          │
              └──────────┼──────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ refinada_spark│
                 │    Parquet    │
                 └───────┬───────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
         Reconciliación Reproceso  Mediciones
              │          │          │
              └──────────┼──────────┘
                         │
                         ▼
                  VERIFICACIÓN T16
                         │
                         ▼
                      APROBADA
```

---

##  Relación con las tareas anteriores

```text
T9
│
├── Arquitectura
│
▼
T10
│
├── Modelo físico
│
▼
T11
│
├── Carga y medición
│
▼
T12–T14
│
├── Validaciones y persistencia
│
▼
T15
│
├── RDD
│
├── Particiones
│
├── Shuffle
│
└── Línea base
       │
       ▼
T16
│
├── PySpark DataFrames
├── Capa refinada
├── Reconciliación
├── Reejecución
├── UDF
├── Pandas UDF
├── Reprocesamiento
└── DataFrame vs RDD
```
Se construye una nueva capa de datos refinada utilizando PySpark, tomando como entrada las mediciones del acueducto almacenadas en archivos CSV. 
El proceso consiste en leer los datos con un esquema definido, transformar la información agregando variables como fecha, hora, confiabilidad y nivel de presión, 
y finalmente almacenar los resultados en formato Parquet, organizados por año, mes y día. Además de transformar los datos, buscamos comprobar que el proceso sea 
reejecutable sin generar duplicados, que los resultados coincidan con las capas construidas anteriormente y que el comportamiento del procesamiento pueda medirse y compararse. 
Para esto se evalúan diferentes alternativas de clasificación de presión, como las expresiones nativas de Spark, las funciones Python UDF y las Pandas UDF, y posteriormente 
se comparan los resultados con la línea base desarrollada mediante RDD. En resumen, T16 busca demostrar que el pipeline no solamente funciona, sino que también es reproducible, 
verificable, medible y justificable técnicamente.
