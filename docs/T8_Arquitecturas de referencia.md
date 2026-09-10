# T8 · Arquitectura del proyecto

> **Big Data e Ingeniería de Datos · Universidad EAN**  
> **Hito A · Módulo 1**

## 1. Contexto y fuente

El proyecto construye un flujo de datos reproducible para almacenar, transformar y analizar información, partiendo de una fuente de datos externa y pasando por diferentes etapas de procesamiento y almacenamiento.

La fuente utilizada en las tareas iniciales corresponde a datos abiertos y el proyecto trabaja con información estructurada para posteriormente organizarla en un lago de datos y prepararla para análisis.

En T1 se realizó el perfilamiento de la fuente y se identificaron las características del conjunto de datos. A partir de esta fuente se construyeron las siguientes decisiones técnicas del proyecto.

La arquitectura propuesta mantiene una separación entre los datos originales, los datos refinados y los datos preparados para consumo analítico. Esta organización permite conservar el dato original y realizar transformaciones sin perder la trazabilidad del proceso.

---

## 2. Decisión de paradigma

La decisión de paradigma se deriva de las necesidades identificadas durante las tareas anteriores.

El proyecto es **principalmente orientado a procesamiento por lotes**, debido a que las transformaciones y análisis se realizan sobre conjuntos de datos almacenados y no requieren que cada registro sea procesado inmediatamente después de llegar.

Por esta razón, no se adopta una arquitectura Kappa como arquitectura principal. Kappa exige que todo el problema pueda tratarse como flujo, que el registro de eventos pueda conservarse y que el reprocesamiento completo sea costeable.

El proyecto tampoco requiere una arquitectura de malla de datos, porque corresponde a un proyecto desarrollado por un único equipo y sobre un dominio definido. La malla está orientada a resolver problemas de escala organizativa entre múltiples dominios y equipos.

La arquitectura seleccionada es, por tanto, una **arquitectura Lambda modesta orientada principalmente a lotes**, manteniendo una vía de procesamiento por lotes y dejando preparada la posibilidad de incorporar procesamiento de flujo acotado cuando exista un requisito que lo justifique.

### Requisitos que sustentan la decisión

| Requisito | Tratamiento | Justificación |
|---|---|---|
| Procesamiento histórico | Lote | Se trabaja sobre datos almacenados |
| Transformaciones | Lote | No requieren respuesta inmediata |
| Reprocesamiento | Lote | Permite volver a procesar los datos refinados |
| Consulta analítica | Servicio | Consume datos preparados |
| Flujo inmediato | Acotado | Solo se incorporaría cuando exista una necesidad real de baja latencia |

La elección evita introducir complejidad de procesamiento en tiempo real donde no existe una necesidad clara.

---

## 3. Arquitectura elegida

Se adopta una **Lambda modesta**, con predominio de la rama batch.

La arquitectura se deriva directamente del paradigma decidido: el procesamiento histórico se realiza mediante lotes, mientras que la arquitectura conserva la posibilidad de incorporar una rama de velocidad limitada para aquellos requisitos que posteriormente necesiten menor latencia.

La decisión también considera el costo de Lambda: mantener dos implementaciones de una misma lógica puede generar duplicación, sincronización y reconciliación de resultados. Por eso, en este proyecto la rama de velocidad no se implementa de forma generalizada; se mantiene acotada al caso en que realmente aporte valor.

### ¿Por qué no Kappa?

Kappa sería apropiada si todo el problema pudiera expresarse como flujo, si el registro completo de eventos pudiera conservarse y si el reprocesamiento fuera costeable.

En este proyecto, el procesamiento principal es sobre datos históricos almacenados y las transformaciones se ejecutan como trabajos batch. Forzar todo el procesamiento a un flujo único agregaría complejidad sin resolver una necesidad principal del proyecto.

### ¿Por qué no Data Mesh?

Data Mesh no se adopta porque su objetivo principal es solucionar problemas de escala organizativa.

El proyecto no tiene múltiples dominios autónomos ni múltiples equipos propietarios de datos. Implementar gobierno federado, dominios dueños de sus datos y una plataforma de autoservicio agregaría coordinación y gobierno innecesarios para la escala actual.

El costo aceptado de la arquitectura elegida es la posible complejidad adicional de mantener una rama de velocidad cuando sea necesaria. Se acepta este costo de manera limitada porque permite conservar una arquitectura compatible con futuras necesidades de baja latencia sin convertir todo el proyecto en un sistema de streaming.

---

## 4. Diagramas C4

Los diagramas deben interpretarse utilizando la notación C4.

El nivel 1 representa el sistema como una caja y muestra sus usuarios y sistemas externos.

El nivel 2 representa los contenedores lógicos del sistema, incluyendo aplicaciones, motores de procesamiento y almacenes de datos.

> **Importante:** un contenedor C4 no equivale a un contenedor Docker. Docker representa una tecnología de ejecución; C4 representa una unidad lógica del sistema.

### C4 nivel 1 · Contexto

```mermaid
flowchart LR
    U["Usuario / Analista"]

    S["Sistema de procesamiento y análisis de datos"]

    F["Fuente externa de datos"]

    B["Herramienta de análisis"]

    F -->|"Entrega datos"| S
    U -->|"Consulta y analiza"| S
    S -->|"Entrega datos preparados"| B
    U -->|"Realiza análisis"| B
