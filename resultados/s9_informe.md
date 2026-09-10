#Decisión del paradigma de almacenamiento

## Introducción

La tarea T9 tuvo como objetivo seleccionar el paradigma de almacenamiento
más apropiado para el proyecto entre tres alternativas: almacén de datos,
lago de datos y lakehouse.

La decisión se realizó mediante una matriz de criterios ponderados y
posteriormente se documentó mediante un Architecture Decision Record
(ADR). De esta manera, la decisión queda registrada junto con sus
argumentos, beneficios, costos y condiciones para una futura revisión.

El propósito no fue seleccionar la tecnología más moderna, sino determinar
qué alternativa responde mejor a las necesidades actuales del proyecto y
mantiene coherencia con la arquitectura desarrollada durante las sesiones
anteriores.

---

## Objetivo

Determinar qué paradigma de almacenamiento presenta la mejor relación
entre flexibilidad, costo, calidad, rendimiento, necesidades
transaccionales y complejidad operativa.

La selección debe ser coherente con la arquitectura desarrollada
previamente, el uso de Parquet y la organización del lago de datos por
capas.

---

## Alternativas analizadas

### Almacén de datos

El almacén de datos está orientado principalmente al almacenamiento de
información estructurada y curada para consultas analíticas.

Su principal ventaja es el control sobre el esquema, la calidad de los
datos y el rendimiento de las consultas.

Sin embargo, presenta menor flexibilidad cuando se requiere almacenar
datos variados o conservar información en diferentes etapas de
transformación.

Para este proyecto, esta alternativa no resulta la más conveniente porque
la arquitectura existente necesita conservar flexibilidad durante la
ingesta y procesamiento de los datos.

### Lago de datos

El lago de datos permite almacenar información en diferentes formatos y
mantener los datos antes de conocer necesariamente todos sus usos
posteriores.

Esta alternativa es coherente con la arquitectura desarrollada en el
proyecto, especialmente con la organización por capas y el uso de Parquet
para los datos refinados.

Su principal riesgo es el gobierno del dato. Un lago sin organización,
documentación y responsables puede convertirse en un data swamp.

Para reducir este riesgo se mantiene una estructura por capas y procesos
definidos para la transformación y organización de los datos.

### Lakehouse

El lakehouse combina características del lago y del almacén de datos.
Permite conservar la flexibilidad del almacenamiento de objetos y añadir
capacidades relacionadas con transacciones, evolución controlada del
esquema y time travel mediante formatos de tabla.

Es una alternativa técnicamente sólida, pero introduce una complejidad
operativa superior.

En el estado actual del proyecto no se identifica una necesidad
indispensable de transacciones ACID ni de consultas sobre versiones
históricas de las tablas. Por este motivo, no se considera necesario
adoptarlo en esta etapa.

---

## Matriz de decisión

Para realizar la comparación se definieron seis criterios:

| Criterio | Peso | Almacén | Lago | Lakehouse |
|---|---:|---:|---:|---:|
| Flexibilidad de formatos | 20 % | 2 | 5 | 5 |
| Costo de almacenamiento | 20 % | 3 | 5 | 4 |
| Calidad y gobierno del dato | 20 % | 5 | 3 | 5 |
| Rendimiento analítico | 15 % | 5 | 4 | 5 |
| Necesidad de transacciones | 10 % | 3 | 2 | 2 |
| Complejidad operativa | 15 % | 3 | 4 | 2 |
| **Puntaje final** | **100 %** | **3,50** | **4,20** | **4,05** |

La escala utilizada para las calificaciones es:

- 1 = muy desfavorable
- 2 = desfavorable
- 3 = aceptable
- 4 = favorable
- 5 = muy favorable

Los pesos fueron definidos de acuerdo con las necesidades actuales del
proyecto y suman exactamente 100 %.

---

## Justificación de los pesos

La flexibilidad de formatos recibe un peso del 20 % porque el proyecto
trabaja con datos que atraviesan diferentes etapas de procesamiento y
requiere flexibilidad durante la ingesta y transformación.

El costo de almacenamiento también recibe un 20 %, debido a que se busca
mantener una solución eficiente y evitar introducir costos adicionales
que no sean necesarios para el estado actual del proyecto.

La calidad y el gobierno del dato reciben otro 20 %. Aunque el lago
ofrece flexibilidad, es necesario mantener una estructura organizada,
documentada y controlada para evitar que se convierta en un data swamp.

El rendimiento analítico recibe un 15 %, debido a que los datos serán
utilizados posteriormente en procesos de análisis y modelado.

La necesidad de transacciones recibe un 10 %, ya que actualmente no
constituye un requisito principal del proyecto.

Finalmente, la complejidad operativa recibe un 15 %, buscando una
arquitectura que pueda ser mantenida y comprendida por el equipo sin
incorporar componentes que todavía no sean necesarios.



##Resultados
Después de ejecutar la matriz ponderada mediante el script
src/matriz_almacenamiento.py, se obtuvieron los siguientes resultados:

Alternativa	Puntaje	Posición
Lago de datos	4,20 / 5,00	1.º
Lakehouse	4,05 / 5,00	2.º
Almacén de datos	3,50 / 5,00	3.º

El resultado confirma que el Lago de datos es la alternativa con mayor
puntuación de acuerdo con los pesos y calificaciones establecidos.

El Lago supera al Lakehouse por 0,15 puntos y al Almacén de datos por
0,70 puntos.

El resultado también es coherente con la arquitectura actual del
proyecto, ya que esta utiliza una organización por capas y contempla el
uso de Parquet en los datos refinados.

El Lakehouse obtiene un resultado cercano al Lago, lo cual demuestra que
es una alternativa técnicamente viable. Sin embargo, sus ventajas
adicionales están relacionadas principalmente con capacidades
transaccionales y de versionamiento que actualmente no constituyen una
necesidad crítica.

## Confirmación de la decisión
La decisión se confirma tanto desde el punto de vista cuantitativo como
desde el punto de vista de ingeniería.

Desde el punto de vista cuantitativo, el Lago de datos obtiene el mayor
puntaje de la matriz con 4,20 sobre 5,00.

Desde el punto de vista de ingeniería, la alternativa mantiene
coherencia con la arquitectura existente y evita agregar complejidad
innecesaria.

## Los principales elementos que respaldan la decisión son:

1. Existe una organización del almacenamiento mediante capas.
2. Se utiliza Parquet como formato para los datos refinados.
3. El proyecto requiere flexibilidad durante las etapas de procesamiento.
4. El almacenamiento debe mantener un costo razonable.
5. Actualmente no existe un requisito fuerte de transacciones ACID.
6. No existe una necesidad indispensable de time travel.
7. La arquitectura puede evolucionar posteriormente hacia un lakehouse si aparecen nuevos requisitos.
9. Por estas razones, la decisión de utilizar un Lago de datos por capas seconsidera confirmada.


La suma de los pesos es:

```text
20 + 20 + 20 + 15 + 10 + 15 = 100 %

Puntaje = Σ (Peso × Calificación / 100)

(20 × 5 / 100)
+ (20 × 5 / 100)
+ (20 × 3 / 100)
+ (15 × 4 / 100)
+ (10 × 2 / 100)
+ (15 × 4 / 100)

= 1,00 + 1,00 + 0,60 + 0,60 + 0,20 + 0,60

= 4,20


Lago de datos = 4,20 / 5,00


Almacén de datos = 3,50 / 5,00

Lakehouse = 4,05 / 5,00
