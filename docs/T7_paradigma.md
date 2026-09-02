# T7 · Decisión de paradigma del proyecto

**Sesión 7 · Taller de decisión · Fuente: SECOP II · Grupo 3**

---

## 1. La restricción que impone la fuente

Antes de asignar ningún paradigma hay que establecer un límite que ninguna decisión de arquitectura
puede saltarse: **la frescura alcanzable está acotada por la frescura que la fuente ofrece.** Si el
portal publica en tandas, ningún motor de flujo aguas abajo convierte el dato en continuo.

Nuestra ficha técnica T1 ya midió esa brecha, en el elemento 4:

| Frecuencia | Lo que dice / lo que se observa |
|---|---|
| **Declarada** | El portal de datos abiertos la describe como continua o diaria |
| **Observada** | Al agrupar por `fecha_de_firma` sobre la muestra: **182.511 registros comparten el mismo día** frente a 2.932 con salto de un día |

Esa distribución no corresponde a una fuente continua. Corresponde a un **volcado en bloque
etiquetado como continuo**: el 91 % de la muestra entra en una sola fecha. Con un peso medio de
**1,60 KB por registro**, esa ráfaga equivale a unos **285 MB llegando de golpe**.

**Consecuencia para la arquitectura.** Ningún requisito de este proyecto puede exigir frescura de
segundos, porque la fuente no la ofrece. Diseñar un flujo verdadero sobre SECOP II sería pagar por
una frescura que la API no entrega: el dato seguiría llegando en tandas, solo que a través de una
tubería más cara. Esta restricción no es una limitación de nuestro diseño, es una propiedad de la
fuente, y la declaramos explícitamente porque condiciona todo lo que sigue.

> **Medición pendiente que refinaría este número.** El retraso entre `fecha_de_firma` y
> `ultima_actualizacion` daría la mediana de días que tarda un contrato en aparecer publicado. Ese
> valor es el techo exacto de frescura de la fuente. Lo dejamos señalado como refinamiento.

---

## 2. Requisitos de dato del proyecto, con sus dos cifras

El proyecto de auditoría de contratación pública tiene tres requisitos de dato. Para cada uno, la
frescura que **exige** —no la deseable— y el volumen que llega por ciclo.

### P1 · Ingesta incremental de contratos nuevos al lago

| Criterio | Valor |
|---|---|
| Quién lo usa y para qué | Es el requisito de base: alimenta a P2 y P3. Sin él, nada más existe |
| **Frescura exigida** | **Horas.** Acotada por la fuente, no por nuestra necesidad (ver sección 1) |
| **Volumen por ciclo** | **Muy irregular.** En un ciclo cualquiera, cero registros; en un ciclo de publicación, del orden de **10⁵ registros y centenares de MB** |
| Paradigma | **Micro-lotes** |

### P2 · Detección de irregularidades en contratos recién publicados

| Criterio | Valor |
|---|---|
| Quién lo usa y para qué | El equipo de auditoría, para señalar contratos que superan umbrales de cuantía sin la modalidad de contratación correspondiente, o adjudicaciones atípicas |
| **Frescura exigida** | **Horas.** Es el requisito más exigente del proyecto, pero sigue sin llegar a minutos: el hallazgo dispara una revisión humana que ocurre en horario laboral, no una acción automática |
| **Volumen por ciclo** | El mismo de P1: se evalúan solo los registros nuevos, del orden de **10⁵ en un ciclo de publicación** |
| Paradigma | **Micro-lotes**, encadenado a P1 |

> Aquí está la tentación que el taller combate. «Detección de irregularidades» *suena* a tiempo real.
> Pero la prueba de la guía lo desmonta: si un contrato irregular se detecta seis horas más tarde,
> **no pasa nada material** — el contrato ya está firmado y publicado, y la auditoría es posterior
> por naturaleza. La frescura deseable sería segundos; la exigida son horas.

### P3 · Informes periódicos de transparencia

| Criterio | Valor |
|---|---|
| Quién lo usa y para qué | Entes de control y publicación externa: totales de contratación por departamento, sector y modalidad |
| **Frescura exigida** | **Días.** El informe tiene periodicidad mensual o trimestral y una fecha de corte declarada |
| **Volumen por ciclo** | El acumulado del período. Con `S₀ = 0,3045 GB` y `g = 5 %` mensual declarado en T1, el volumen mensual pasa de 0,3045 GB hoy a **0,5468 GB a doce meses** |
| Paradigma | **Lotes** |

---

## 3. El paradigma del proyecto: híbrido, con predominio de lotes

| Requisito | Frescura exigida | Volumen por ciclo | Paradigma |
|---|---|---|---|
| P1 · Ingesta incremental | Horas | ~10⁵ registros en ráfaga | Micro-lotes |
| P2 · Detección de irregularidades | Horas | ~10⁵ registros en ráfaga | Micro-lotes |
| P3 · Informes de transparencia | Días | Acumulado mensual, 0,30 → 0,55 GB | Lotes |

**La decisión: híbrido de micro-lotes y lotes, sin flujo verdadero.**

### Por qué micro-lotes y no flujo

La consulta periódica a la API de Socrata con `$limit`, apoyada en el identificador estable
`proceso_de_compra` que documentamos en el elemento 7 de la ficha T1, permite traer únicamente los
expedientes nuevos sin duplicidad. Eso es exactamente una carga incremental, y una carga incremental
ejecutada cada N minutos **es** un micro-lote.

Es además el paradigma más honesto con la fuente. Un flujo verdadero exigiría que el portal empujara
eventos; lo que ofrece es una API de consulta. Montar un motor de flujo encima de una fuente que
publica en tandas añade costo operativo permanente sin añadir un solo segundo de frescura real.

### El intervalo del micro-lote, dimensionado por la ráfaga

Aquí aparece la consecuencia práctica de la sección 1. Si consultamos cada 15 minutos, tenemos 96
ciclos al día: **en 95 de ellos no llega nada, y en uno llegan del orden de 180.000 registros**.

| Intervalo | Ciclos por día | Comportamiento |
|---|---|---|
| 5 min | 288 | 287 ciclos vacíos, uno con la ráfaga completa |
| **15 min** | **96** | Equilibrio razonable entre frescura y ciclos desperdiciados |
| 60 min | 24 | Menos desperdicio, frescura de hasta una hora |

**El proceso debe dimensionarse para la ráfaga, no para el promedio.** Un cálculo basado en el
promedio de registros por ciclo —unos 1.900 si se reparten los 182.511 entre 96 ciclos— daría un
sistema que colapsa el día de la publicación. Es el mismo error que la sesión 1 enseñó a no cometer
con la memoria: dimensionar sobre el caso típico en vez del caso límite.

Elegimos **15 minutos** como intervalo de partida, revisable con la medición del retraso de
publicación señalada en la sección 1.

### Por qué esto no es «todo lotes por defecto»

La rúbrica distingue entre elegir lotes por defecto y elegirlo con argumento. Nuestra decisión no es
por comodidad ni por costo: es porque **medimos la fuente y encontramos que no ofrece la frescura que
un flujo requeriría para tener sentido**. Si SECOP II publicara por eventos, P2 sería un candidato
legítimo a flujo. No los publica, y esa es la razón.

---

## 4. El compromiso CAP que aceptamos

El punto concreto donde nuestra arquitectura paga el compromiso: **el tablero de auditoría consulta
la capa consolidada del lago en MinIO, y una partición de red deja el almacenamiento inalcanzable.**

Las dos opciones y lo que cada una cuesta:

| Opción | Qué hace el tablero | Qué se arriesga |
|---|---|---|
| Disponibilidad | Muestra la última consolidación en caché | Que alguien lea una cifra presupuestal desactualizada y decida sobre ella |
| **Consistencia** | **No muestra nada y avisa «datos no disponibles»** | Que el tablero quede inutilizable mientras dure la partición |

**Elegimos consistencia.** La razón es el uso del dato, no una preferencia técnica: este tablero
alimenta decisiones de auditoría sobre contratación pública, donde una cifra equivocada puede
sustentar un hallazgo infundado o, peor, ocultar uno real. **Una cifra desactualizada presentada sin
advertencia es más peligrosa que la ausencia de cifra**, porque la ausencia es evidente y el error
silencioso no.

El costo lo asumimos con los ojos abiertos: durante una partición el tablero queda inutilizable. Lo
aceptamos porque es una herramienta interna, de consulta en jornada laboral, y no un servicio de cara
al público donde la indisponibilidad tendría consecuencias inmediatas.

> **Precisión sobre el teorema.** La formulación de «elegir dos de tres» es incorrecta, y Brewer la
> corrigió en 2012: las particiones de red no son una opción que se elige, son una condición del
> entorno distribuido. La decisión real ocurre **únicamente durante la partición**. Fuera de ella,
> nuestro sistema tiene consistencia y disponibilidad a la vez.
>
> Brewer añade además que la elección no es global ni permanente, sino que puede tomarse por
> operación y por subsistema. Nuestra elección de consistencia aplica al tablero de auditoría; una
> vista exploratoria sin valor probatorio podría razonablemente elegir lo contrario.
>
> **Extensión PACELC.** El CAP no cubre el caso sin fallos, y ahí también hay un precio: *si hay
> Partición, elegir entre Availability y Consistency; en caso contrario (Else), entre Latency y
> Consistency*. En nuestro caso eso se traduce en que cada verificación adicional que hacemos para
> asegurar que la cifra es la vigente es tiempo que el tablero tarda en pintar. Aceptamos esa
> latencia por la misma razón que aceptamos la indisponibilidad.

---

## 5. Resumen de la decisión

1. La fuente publica en tandas y esa es la restricción dura: **ningún requisito puede exigir
   segundos**, y está medido, no supuesto.
2. El proyecto es **híbrido**: micro-lotes cada 15 minutos para ingesta y detección, lotes para los
   informes periódicos.
3. **No hay flujo verdadero**, y la razón está en la fuente, no en el presupuesto.
4. El micro-lote se dimensiona para la **ráfaga de ~180.000 registros**, no para el promedio.
5. Bajo partición elegimos **consistencia** en el tablero de auditoría, porque una cifra
   presupuestal desactualizada sin advertencia es peor que la ausencia de cifra.

---

*T7 alimenta el hito de la sesión 8: la elección entre arquitecturas Lambda y Kappa se hace sobre
esta decisión de paradigma. Un proyecto con predominio de lotes y un componente de micro-lotes se
acerca más a Lambda que a Kappa, porque Kappa exigiría que todo el histórico estuviera disponible
como flujo reproducible, y nuestra fuente no lo ofrece.*
