Claro. Aquí tienes el mismo contenido **sin emojis**, listo para copiar y pegar directamente en GitHub como archivo `.md`.

# T10 — Modelo Lógico Dimensional

> **Actividad:** Tarea acumulativa T10
> **Sesión:** 10 — Modelado Dimensional I
> **Módulo:** 1 — Fundamentos de Big Data y arquitecturas de datos
> **Competencia:** TECH IA MAKER



## Introducción

La sesión 10 aborda el **modelado dimensional**, una etapa fundamental dentro del desarrollo de una solución de datos orientada al análisis. El propósito principal es transformar la información consolidada del proyecto en una estructura que permita realizar consultas de manera clara, eficiente y sin ambigüedades. Para lograrlo, el elemento más importante es definir correctamente el **grano**, es decir, establecer qué representa exactamente cada fila de la tabla de hechos.

El modelado dimensional no busca simplemente normalizar los datos ni eliminar toda repetición. Su objetivo es organizar la información pensando en las preguntas que posteriormente realizará el negocio. Por esta razón, se utiliza una estructura compuesta principalmente por una **tabla de hechos**, que contiene las medidas del proceso, y varias **dimensiones**, que proporcionan el contexto necesario para analizar dichas medidas.

En el desarrollo de la T10 se plantea un **esquema estrella**, en el cual la tabla de hechos se encuentra en el centro y las dimensiones se conectan directamente con ella. Además, se utilizan **claves subrogadas** para identificar las filas de las dimensiones de forma independiente a los identificadores provenientes de los sistemas de origen.



## Objetivo

El objetivo de esta actividad es diseñar el **modelo lógico dimensional del proyecto**, tomando como insumo la información obtenida durante las etapas anteriores de la arquitectura de datos. El modelo debe establecer un grano explícito, identificar las medidas correspondientes a dicho grano, definir al menos tres dimensiones conformadas y utilizar claves subrogadas para identificar cada dimensión.

Adicionalmente, el modelo debe poder justificarse desde el punto de vista analítico. Es decir, cada elemento incluido debe tener una función clara y debe ser coherente con el nivel de detalle establecido para la tabla de hechos.



## Análisis del modelado dimensional

El modelado dimensional permite separar dos tipos principales de información. Por una parte, se encuentran los **hechos**, que representan eventos o mediciones del proceso de negocio y generalmente contienen valores numéricos que pueden analizarse. Por otra parte, están las **dimensiones**, que proporcionan el contexto mediante el cual se pueden filtrar, agrupar o interpretar los hechos.

Por ejemplo, una medida de consumo por sí sola no proporciona suficiente información para un análisis completo. Al relacionarla con una dimensión de fecha, es posible conocer el comportamiento del consumo durante diferentes días, meses o años. Si además se relaciona con una dimensión de sector, se puede comparar el consumo entre diferentes sectores.

De esta manera, las dimensiones permiten responder preguntas como:

| Pregunta | Elemento que permite responderla |
|---|---|
| ¿Cuánto ocurrió? | Medidas de la tabla de hechos |
| ¿Cuándo ocurrió? | Dimensión fecha |
| ¿Dónde ocurrió? | Dimensión sector |
| ¿Qué elemento estuvo involucrado? | Dimensión medidor |

La principal ventaja del modelo dimensional es que esta organización está orientada directamente a las consultas analíticas. En lugar de construir numerosas relaciones entre tablas altamente normalizadas, se busca proporcionar una estructura sencilla en la que la tabla de hechos pueda relacionarse directamente con las dimensiones necesarias.



## El grano como decisión principal

El aspecto más importante del modelo es el **grano**. El grano define qué representa una fila individual de la tabla de hechos y debe establecerse antes de seleccionar las medidas o diseñar las relaciones.

### Grano definido

> **Una lectura de un medidor en una hora.**

Esta definición significa que una fila de la tabla de hechos representa una única lectura correspondiente a un medidor durante una hora determinada.

La declaración del grano permite establecer límites claros para el modelo. Si el modelo trabaja con lecturas horarias, las medidas deben existir a ese mismo nivel. Por ejemplo, una medición de consumo correspondiente a una lectura individual puede pertenecer al hecho, mientras que un promedio mensual no debería incorporarse directamente como una medida del mismo registro, porque representa una granularidad diferente.

Esta característica es fundamental para evitar errores de doble conteo o resultados difíciles de interpretar. Si se mezclan datos horarios, diarios y mensuales dentro de una misma tabla de hechos, las agregaciones pueden producir resultados incorrectos.

Por este motivo, una de las primeras pruebas realizadas consiste en verificar que la combinación de variables que representa el grano sea única.



## Tabla de hechos

La tabla de hechos constituye el **centro del esquema estrella**. En el modelo propuesto se denomina `fact_lecturas`.

Su función es almacenar cada registro correspondiente al proceso de medición y mantener las claves que permiten relacionarlo con las dimensiones.

### Estructura conceptual

```text
fact_lecturas
--------------------------------
lectura_sk
fecha_sk
medidor_sk
sector_sk
consumo
presion
```

| Campo | Función |
|---|---|
| `lectura_sk` | Identificador del registro dentro de la tabla de hechos |
| `fecha_sk` | Clave foránea hacia `dim_fecha` |
| `medidor_sk` | Clave foránea hacia `dim_medidor` |
| `sector_sk` | Clave foránea hacia `dim_sector` |
| `consumo` | Medida del proceso |
| `presion` | Medida del proceso |

La columna `lectura_sk` identifica el registro dentro de la tabla de hechos. Las columnas `fecha_sk`, `medidor_sk` y `sector_sk` funcionan como claves foráneas hacia las dimensiones.

Las variables numéricas como `consumo` y `presion`, en caso de existir realmente en los datos del proyecto, representan medidas del proceso. Estas medidas deben ser evaluadas de acuerdo con el grano para determinar si pueden sumarse, promediarse o utilizarse mediante otro tipo de agregación.

Una característica importante es que la tabla de hechos no debe convertirse en una tabla descriptiva. Los nombres, categorías, características del medidor o información geográfica pertenecen a las dimensiones, mientras que los valores medidos pertenecen al hecho.


## Dimensión fecha

La dimensión `dim_fecha` permite analizar las mediciones desde una perspectiva temporal.

### Estructura conceptual

```text
dim_fecha
--------------------------------
fecha_sk
fecha
año
mes
nombre_mes
trimestre
dia
dia_semana
```

| Campo | Descripción |
|---|---|
| `fecha_sk` | Clave subrogada |
| `fecha` | Fecha correspondiente |
| `año` | Año de la fecha |
| `mes` | Número del mes |
| `nombre_mes` | Nombre del mes |
| `trimestre` | Trimestre correspondiente |
| `dia` | Día del mes |
| `dia_semana` | Día de la semana |

La clave `fecha_sk` es una clave subrogada generada por el modelo. Los demás atributos proporcionan diferentes niveles de análisis temporal.

Esta dimensión es especialmente útil porque permite realizar consultas como el comportamiento de una medida por año, mes, trimestre, día de la semana o fecha específica sin tener que calcular estos atributos directamente sobre la tabla de hechos.

La utilización de una dimensión calendario también proporciona una estructura homogénea para las consultas y facilita posteriormente la incorporación de atributos adicionales relacionados con periodos de tiempo.


## Dimensión medidor

La dimensión `dim_medidor` representa los elementos que realizan o registran las mediciones.

### Estructura conceptual

```text
dim_medidor
--------------------------------
medidor_sk
medidor_origen
tipo_medidor
estado
```

| Campo | Descripción |
|---|---|
| `medidor_sk` | Clave subrogada |
| `medidor_origen` | Identificador proveniente del sistema fuente |
| `tipo_medidor` | Tipo de medidor |
| `estado` | Estado del medidor |

La columna `medidor_sk` es la clave subrogada, mientras que `medidor_origen` conserva el identificador proveniente del sistema fuente.

La separación entre estas dos claves es importante. El identificador original pertenece al sistema que generó los datos, mientras que la clave subrogada pertenece exclusivamente al modelo dimensional.

Esto permite que el modelo sea menos dependiente de los sistemas fuente y facilita futuras modificaciones o procesos de integración.


## Dimensión sector

La dimensión `dim_sector` permite incorporar el contexto geográfico, organizacional o territorial asociado a las mediciones.

### Estructura conceptual

```text
dim_sector
--------------------------------
sector_sk
sector_origen
nombre_sector
zona
localidad
```

| Campo | Descripción |
|---|---|
| `sector_sk` | Clave subrogada |
| `sector_origen` | Identificador proveniente del sistema fuente |
| `nombre_sector` | Nombre del sector |
| `zona` | Zona asociada |
| `localidad` | Localidad asociada |

La clave `sector_sk` identifica cada registro dentro de la dimensión y se utiliza desde la tabla de hechos.

La existencia de esta dimensión permite realizar análisis como la comparación de medidas entre sectores, zonas o localidades.


## Esquema estrella

La relación entre los elementos del modelo puede representarse mediante el siguiente esquema:

```text
                         ┌───────────────────┐
                         │     dim_fecha     │
                         │    fecha_sk       │
                         │    fecha          │
                         │    año            │
                         │    mes            │
                         └─────────┬─────────┘
                                   │
                                   │
┌───────────────────┐              │              ┌───────────────────┐
│   dim_medidor     │              │              │    dim_sector     │
│   medidor_sk      │              │              │    sector_sk      │
│   medidor_origen  │              │              │    sector_origen  │
│   tipo_medidor    │              │              │    zona            │
│   estado          │              │              │    localidad       │
└─────────┬─────────┘              │              └─────────┬─────────┘
          │                        │                        │
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  fact_lecturas    │
                         │  lectura_sk       │
                         │  fecha_sk         │
                         │  medidor_sk       │
                         │  sector_sk        │
                         │  medidas          │
                         └───────────────────┘
```

La estructura recibe el nombre de **esquema estrella** debido a que la tabla de hechos ocupa la posición central y las dimensiones funcionan como los brazos que salen de ella.

Una de las principales ventajas de este diseño es la simplicidad. Las consultas analíticas pueden relacionar directamente los hechos con las dimensiones sin tener que recorrer numerosos niveles de tablas.


## Claves subrogadas

Las claves subrogadas son otro elemento importante del modelo.

Una **clave subrogada** es un identificador generado dentro del propio modelo dimensional. No tiene significado de negocio y no depende directamente del identificador utilizado por el sistema de origen.

### Claves utilizadas

| Dimensión | Clave subrogada |
|---|---|
| `dim_fecha` | `fecha_sk` |
| `dim_medidor` | `medidor_sk` |
| `dim_sector` | `sector_sk` |

Por ejemplo, un medidor puede tener un identificador original como `M001`, pero dentro de la dimensión puede recibir:

```text
medidor_sk = 1
medidor_origen = M001
```

Esto permite mantener una separación entre el sistema fuente y el modelo analítico.

Las claves subrogadas también son importantes porque permiten manejar cambios históricos en las dimensiones. En etapas posteriores del proyecto pueden utilizarse para implementar dimensiones lentamente cambiantes, donde una modificación de un atributo puede generar una nueva versión del registro.


## Validación del modelo

El código desarrollado en Python incorpora controles para verificar que el modelo sea consistente.

La primera validación corresponde al **grano**. Se comprueba que la combinación de variables definida para identificar una lectura no aparezca repetida.

### Resultado correcto

```text
Duplicados del grano: 0
Estado: OK - El grano es único.
```

Se considera que la combinación utilizada para representar el grano es única dentro de los datos analizados.

### Resultado con error

```text
Duplicados del grano: 25
Estado: ERROR - Existen registros duplicados para el grano definido.
```

Esto significa que existe una inconsistencia que debe investigarse. No necesariamente significa que el código esté incorrecto; puede indicar que el grano elegido no representa adecuadamente la información de origen.


## Validación de claves foráneas

También se validan las claves foráneas de la tabla de hechos.

Un resultado correcto puede ser:

```text
fecha_sk: OK (nulos: 0)
medidor_sk: OK (nulos: 0)
sector_sk: OK (nulos: 0)
```

Esto indica que todos los registros de hechos tienen correspondencia con las dimensiones correspondientes.

Si alguna clave presenta valores nulos, por ejemplo:

```text
sector_sk: ERROR (nulos: 15)
```

se debe investigar por qué 15 registros no pudieron relacionarse con la dimensión.


## Código Python y automatización

El código Python desarrollado permite automatizar el proceso de construcción del modelo. Primero se localizan y cargan los archivos CSV, después se inspeccionan sus columnas y finalmente se generan las estructuras dimensionales.

El uso de `pandas` facilita operaciones como eliminación de duplicados, transformación de fechas, creación de nuevas columnas y cruces entre tablas. Por otro lado, `pathlib` permite gestionar las rutas de archivos de forma organizada.

El código genera como resultado archivos correspondientes a las dimensiones, la tabla de hechos y las validaciones.

### Archivos generados

```text
resultados/
├── dim_fecha.csv
├── dim_medidor.csv
├── dim_sector.csv
├── fact_lecturas.csv
└── validacion_grano.csv
```

Esto permite que el proceso sea reproducible y que los resultados puedan ser revisados posteriormente.


## Análisis de los resultados

Desde el punto de vista del modelado, el resultado esperado es un modelo donde cada registro de la tabla de hechos tenga un significado claro y pueda relacionarse con todas las dimensiones definidas.

La existencia de una única granularidad evita combinar diferentes niveles de información dentro de la misma estructura. Las dimensiones permiten agregar contexto a las medidas, mientras que las claves subrogadas mantienen la independencia respecto de los identificadores originales.

El esquema estrella también resulta adecuado para un escenario analítico porque facilita la consulta de información. Por ejemplo, una medida puede agregarse por fecha y sector sin necesidad de recorrer una estructura excesivamente normalizada.

El modelo también queda preparado para futuras etapas del proyecto. En la sesión siguiente puede implementarse físicamente, cargarse con datos y comenzar a trabajar con dimensiones lentamente cambiantes. Posteriormente, el modelo puede materializarse desde las capas de datos mediante herramientas de procesamiento como Spark.


## Errores que deben evitarse

Uno de los principales errores sería definir un grano demasiado amplio o ambiguo. Una frase como **"lecturas y consumos por sector"** mezcla conceptos que pueden representar diferentes niveles de detalle. El grano debe expresar una sola unidad de análisis.

También se debe evitar incluir medidas que no correspondan al nivel declarado. Si la tabla contiene información horaria, no se debe incluir directamente una medida que represente un total mensual sin realizar una transformación apropiada.

Otro error consiste en colocar atributos descriptivos directamente en la tabla de hechos. Información como nombres, categorías o características de un elemento debería mantenerse en la dimensión correspondiente.

También es incorrecto utilizar directamente las claves originales del sistema fuente como claves principales de las dimensiones cuando el diseño requiere claves subrogadas. Las dimensiones deben disponer de identificadores propios del modelo.

Finalmente, no se debe convertir automáticamente el modelo en un esquema copo de nieve únicamente porque la normalización reduzca la repetición de datos. Para el contexto analítico de esta actividad, el esquema estrella es el punto de partida y el copo de nieve debe utilizarse solamente cuando exista una razón concreta que lo justifique.


## Conclusión

El modelado dimensional constituye una etapa fundamental para convertir los datos consolidados en una estructura adecuada para el análisis. La principal decisión del proceso es el **grano**, porque determina qué representa cada fila de la tabla de hechos y establece qué medidas y dimensiones pueden formar parte del modelo.

A partir del grano definido se construye una tabla de hechos que contiene las medidas del proceso y las claves necesarias para relacionarla con las dimensiones. Las dimensiones aportan el contexto necesario para analizar la información desde diferentes perspectivas, mientras que las claves subrogadas permiten independizar el modelo de los identificadores de los sistemas fuente.

El esquema estrella resulta apropiado para este escenario porque mantiene una estructura sencilla, con los hechos en el centro y las dimensiones conectadas directamente. Esta organización facilita las consultas analíticas y evita introducir niveles de normalización que no sean necesarios.

El desarrollo en Python complementa el diseño lógico mediante un proceso reproducible de carga, transformación y validación. Las pruebas de unicidad del grano y de las claves foráneas permiten detectar inconsistencias antes de avanzar hacia la implementación física.

En conclusión, la T10 establece las bases del modelo analítico del proyecto. El resultado no consiste únicamente en un diagrama, sino en una estructura justificada por un grano explícito, medidas coherentes, dimensiones conformadas y claves subrogadas. Este diseño permite continuar con las siguientes etapas del proyecto, en las cuales el modelo podrá ser implementado físicamente, cargado con datos y utilizado para realizar consultas y análisis sobre la información.

3. Material académico de la asignatura **Big Data e Ingeniería de Datos**, Universidad Ean. Sesión 10 — Modelado Dimensional I.
````
