# ADR-0001: Paradigma de almacenamiento del proyecto

- **Estado:** Aceptado
- **Fecha:** 2026-09-10
- **Decisión:** Lago de datos por capas
- **Alternativas consideradas:** Almacén de datos, Lago de datos, Lakehouse

---

## 1. Contexto

El proyecto requiere definir el paradigma de almacenamiento que servirá
como base para las siguientes etapas de ingeniería y modelado de datos.

La arquitectura desarrollada en las sesiones anteriores utiliza un lago
de datos organizado por capas, con separación entre los datos de origen,
los datos refinados y los datos preparados para consumo analítico.

En el repositorio del proyecto esta organización se complementa con
directorios como `data/`, `src/`, `notebooks/` y `resultados/`, además de
los archivos y scripts desarrollados durante las sesiones anteriores.

La sesión 6 estableció el uso de Parquet como formato de almacenamiento
para la información refinada. Esta decisión es compatible con el
almacenamiento de objetos y con procesos de transformación mediante
Python y herramientas de procesamiento de datos.

La arquitectura de T8 y las mediciones de T7 deben mantenerse como
referencia para esta decisión. En particular, las cifras exactas de
volumen, crecimiento y características de procesamiento de T7 deben
conservarse en el documento cuando estén disponibles en el repositorio.

El proyecto necesita principalmente:

- almacenar datos de diferentes etapas del procesamiento;
- conservar los datos originales y refinados;
- trabajar con archivos Parquet;
- permitir transformaciones mediante Python;
- mantener costos de almacenamiento razonables;
- soportar el posterior modelado analítico;
- conservar una organización clara mediante capas;
- evitar introducir complejidad tecnológica que el proyecto todavía no
  necesita.

En este momento no se identifica como requisito principal la ejecución
de transacciones ACID sobre las tablas, ni la necesidad de consultar
múltiples versiones históricas de una misma tabla mediante time travel.

Por esta razón se comparan tres alternativas:

1. Almacén de datos.
2. Lago de datos.
3. Lakehouse.

---

## 2. Decisión

Se decide utilizar un **Lago de datos por capas** como paradigma de
almacenamiento del proyecto.

La decisión se apoya en la matriz de criterios ponderados y en la
coherencia con la arquitectura desarrollada previamente.

### 2.1 Criterios y pesos

Los criterios se ponderaron según las necesidades actuales del proyecto:

| Criterio | Peso | Justificación |
|---|---:|---|
| Flexibilidad de formatos | 20 % | El proyecto trabaja con datos que atraviesan diferentes etapas y requiere flexibilidad durante la ingesta y transformación. |
| Costo de almacenamiento | 20 % | Se busca conservar datos de forma eficiente y evitar costos innecesarios por una plataforma más compleja. |
| Calidad y gobierno del dato | 20 % | La organización por capas y los procesos de transformación deben mantener trazabilidad y calidad. |
| Rendimiento analítico | 15 % | El almacenamiento debe permitir el procesamiento y posterior análisis de los datos refinados y consolidados. |
| Necesidad de transacciones | 10 % | Actualmente no existe un requisito fuerte de transacciones ACID sobre las tablas almacenadas. |
| Complejidad operativa | 15 % | Se prioriza una arquitectura que pueda ser mantenida por el equipo sin introducir componentes que no sean necesarios. |

**Total: 100 %**

### 2.2 Matriz ponderada

La escala de calificación es:

- **1:** muy desfavorable
- **2:** desfavorable
- **3:** aceptable
- **4:** favorable
- **5:** muy favorable

| Criterio | Peso | Almacén | Lago | Lakehouse |
|---|---:|---:|---:|---:|
| Flexibilidad de formatos | 20 % | 2 | 5 | 5 |
| Costo de almacenamiento | 20 % | 3 | 5 | 4 |
| Calidad y gobierno del dato | 20 % | 5 | 3 | 5 |
| Rendimiento analítico | 15 % | 5 | 4 | 5 |
| Necesidad de transacciones | 10 % | 3 | 2 | 2 |
| Complejidad operativa | 15 % | 3 | 4 | 2 |
| **Puntaje final** | **100 %** | **3,50** | **4,20** | **4,05** |

### 2.3 Lectura de la matriz

La matriz favorece al **Lago de datos**, con un puntaje de **4,20/5**.

El almacén obtiene 3,50/5. Su principal ventaja es la calidad y
estructura de los datos, además del rendimiento analítico. Sin embargo,
resulta menos flexible para conservar datos variados y no aprovecha
directamente el enfoque de lago por capas que ya fue desarrollado.

El lakehouse obtiene 4,05/5. Es una alternativa técnicamente sólida y
ofrece ventajas importantes relacionadas con transacciones, evolución
controlada del esquema y time travel. Sin embargo, esas capacidades
introducen complejidad que actualmente no corresponde a una necesidad
principal del proyecto.

El lago obtiene el mejor resultado porque combina flexibilidad, bajo
costo y continuidad con la arquitectura existente. La organización por
capas reduce el riesgo de convertir el lago en un data swamp.

### 2.4 Fundamento de ingeniería

La decisión no se toma únicamente porque el lago tenga el mayor
puntaje. También existe coherencia entre la decisión y la arquitectura
existente.

El proyecto ya cuenta con una organización por capas y utiliza Parquet
en la etapa refinada. Mantener el lago evita introducir una nueva
semántica transaccional antes de que exista una necesidad real.

El lakehouse queda como una evolución posible. Si posteriormente el
proyecto necesita transacciones ACID, control transaccional de tablas,
auditoría mediante versiones o time travel, se podrá revisar esta
decisión y evaluar tecnologías como Delta Lake o Apache Iceberg.

---

## 3. Consecuencias

### 3.1 Beneficios

Al adoptar el lago de datos por capas se obtienen los siguientes
beneficios:

- Se mantiene continuidad con la arquitectura desarrollada en T5, T6,
  T7 y T8.
- Se conserva la flexibilidad del almacenamiento de objetos.
- Se mantiene el uso de Parquet como formato adecuado para los datos
  refinados.
- Se pueden conservar datos originales antes de transformarlos.
- Se evita introducir una plataforma transaccional antes de necesitarla.
- La arquitectura sigue siendo apropiada para posteriores procesos de
  modelado dimensional.
- La separación por capas ayuda a controlar la calidad y organización
  del dato.

### 3.2 Costos y sacrificios aceptados

La decisión también implica costos que el equipo acepta conscientemente.

El lago no proporciona por sí mismo las mismas garantías transaccionales
que un lakehouse. Por lo tanto, una escritura defectuosa o un proceso
concurrente debe controlarse mediante los procesos de ingestión y
transformación.

También existe mayor responsabilidad sobre el gobierno del dato. Si las
capas no se documentan, los datos pueden terminar convirtiéndose en un
data swamp.

Además, algunas capacidades que proporciona un lakehouse, como el time
travel y determinadas garantías ACID, no estarán disponibles de forma
nativa mientras se mantenga el almacenamiento como archivos Parquet
organizados por capas.

El equipo acepta estos costos porque actualmente no existe un requisito
que justifique la complejidad adicional de un lakehouse.

### 3.3 Condiciones para reabrir la decisión

Este ADR deberá revisarse si aparece alguno de los siguientes requisitos:

1. Se requiere atomicidad en las operaciones de escritura.
2. Varias cargas concurrentes necesitan garantías transaccionales.
3. Se necesita consultar versiones anteriores de las tablas mediante
   time travel.
4. Se requiere una política formal de evolución de esquema a nivel de
   tablas transaccionales.
5. Los requisitos de auditoría exigen conservar y consultar versiones
   históricas de las tablas.
6. El volumen, concurrencia o complejidad de las operaciones hace que el
   lago por archivos deje de ser suficiente.

Ante cualquiera de estas condiciones se deberá realizar nuevamente la
comparación entre Lago y Lakehouse y actualizar este ADR mediante un
nuevo registro versionado.

---

## 4. Referencias

- Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). *Lakehouse:
  A new generation of open platforms that unify data warehousing and
  advanced analytics*. Proceedings of the 11th Conference on Innovative
  Data Systems Research (CIDR).

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*.
  O'Reilly Media.

- Nygard, M. (2011). *Documenting Architecture Decisions*. Cognitect.

- Reis, J., & Housley, M. (2022). *Fundamentals of Data Engineering*.
  O'Reilly Media.
