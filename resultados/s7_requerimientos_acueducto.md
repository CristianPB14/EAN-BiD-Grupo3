# S7 · Nivel 1 · Asignación de paradigma a los cinco requerimientos del acueducto

**Sesión 7 · Taller de decisión · Grupo 3**

El marco de decisión es el de la sección 1 de la guía: manda la **frescura exigida**, y el volumen
por ciclo y el costo tolerable afinan. La pregunta que aplicamos a los cinco casos es siempre la
misma: *si este dato llegara con una hora de retraso, ¿qué se rompe?*

---

## R1 · Informe mensual de consumo por sector, para planear la facturación

*(Resuelto en la guía, se transcribe como referencia del método)*

| Criterio | Análisis |
|---|---|
| Frescura exigida | **Días.** El informe se planea una vez al mes; un dato de ayer sirve igual |
| Volumen por ciclo | Alto, pero se acumula un mes y se procesa de una vez |
| Costo tolerable | Bajo. No se justifica pagar por frescura que nadie usa |
| **Paradigma** | **Lotes** |
| **Justificación** | Un informe mensual no gana nada con frescura de segundos; el lote es más barato y suficiente |

---

## R2 · Alerta cuando la presión de una tubería sale de rango, para evitar una rotura

| Criterio | Análisis |
|---|---|
| Frescura exigida | **Segundos.** Es el único requerimiento donde el retraso no degrada un informe: causa un daño físico. Una sobrepresión que se detecta una hora tarde ya reventó la tubería |
| Volumen por ciclo | Bajo. Una lectura por sensor por intervalo; son pocos bytes por evento, aunque lleguen sin parar |
| Costo tolerable | **Alto.** El costo de mantener el flujo encendido es una fracción del costo de una rotura, la reparación y el desabastecimiento del sector |
| **Paradigma** | **Flujo** |
| **Justificación** | El valor de esta alerta caduca en segundos: sirve para actuar *antes* de la rotura, no para registrar que ocurrió. Es el único caso donde el sobrecosto del tiempo real se paga solo |

> **Por qué el volumen bajo no lo empuja a lotes.** El criterio 2 empuja hacia lotes cuando el
> volumen por ciclo es enorme. Aquí ocurre lo contrario: el volumen es pequeño, así que el flujo es
> además barato de sostener. Los tres criterios apuntan en la misma dirección.

---

## R3 · Tablero de caudal del centro de control, que el operador mira durante su turno

| Criterio | Análisis |
|---|---|
| Frescura exigida | **Minutos.** No necesita segundos: el operador no reacciona a cada lectura individual, sino a la tendencia de su turno. Pero un caudal de hace media hora ya no le sirve para operar |
| Volumen por ciclo | Moderado. Lecturas agregadas de todos los sectores cada pocos minutos |
| Costo tolerable | Medio. Se justifica pagar por frescura de minutos, no por frescura de segundos |
| **Paradigma** | **Casi real, resuelto con micro-lotes** |
| **Justificación** | Es el caso de manual del punto medio: micro-lotes cada uno o dos minutos entregan la frescura que el operador necesita con la simplicidad operativa de un lote, sin montar un flujo verdadero |

---

## R4 · Detección de posibles fugas a partir del patrón de consumo de la noche anterior

**Este es el requerimiento que la guía deja ambiguo a propósito. Declaramos nuestro supuesto.**

| Criterio | Análisis |
|---|---|
| Frescura exigida | **Horas.** El propio enunciado la fija: el patrón se evalúa sobre *la noche anterior completa*. Antes de que la noche termine no hay patrón que evaluar |
| Volumen por ciclo | Alto y acotado: todas las lecturas nocturnas de todos los medidores, procesadas de una vez |
| Costo tolerable | Bajo. Un proceso que corre una vez al día y se apaga |
| **Paradigma** | **Lotes, en ventana nocturna** |
| **Justificación** | Un lote que corre de madrugada deja el resultado listo al abrir la operación. Adelantar la detección exigiría cambiar la definición del indicador, no el paradigma |

> **Supuesto declarado.** Asumimos que una fuga detectada al inicio de la jornada se atiende con la
> misma eficacia que una detectada de madrugada, porque la cuadrilla de reparación opera en horario
> laboral. **Si ese supuesto cambia** —por ejemplo, si existe turno de atención nocturna, o si se
> cuantifica que las horas adicionales de fuga tienen un costo material en agua no facturada—
> entonces el requerimiento sube a casi real y se resuelve con micro-lotes sobre ventanas móviles,
> igual que R3.
>
> Es el mismo tipo de decisión que la guía pide declarar: no hay respuesta única, hay supuesto
> explícito.

---

## R5 · Carga del histórico de lecturas para el análisis de tendencias del último año

| Criterio | Análisis |
|---|---|
| Frescura exigida | **Días, o ninguna.** El dato ya es histórico por definición. Analizar tendencias de doce meses con información de ayer o de la semana pasada produce el mismo resultado |
| Volumen por ciclo | **El más alto de los cinco.** Un año completo de lecturas en una sola carga |
| Costo tolerable | Bajo, y además es un proceso puntual, no recurrente |
| **Paradigma** | **Lotes** |
| **Justificación** | Aquí el criterio 2 refuerza al criterio 1 en vez de tensionarlo: el volumen es enorme y la frescura irrelevante. Es el caso más claro de lotes de los cinco |

---

## Resumen

| # | Requerimiento | Frescura exigida | Paradigma |
|---|---|---|---|
| R1 | Informe mensual de consumo | Días | Lotes |
| R2 | Alerta de presión fuera de rango | **Segundos** | **Flujo** |
| R3 | Tablero de caudal del centro de control | Minutos | Casi real (micro-lotes) |
| R4 | Detección de fugas del patrón nocturno | Horas | Lotes nocturnos *(supuesto declarado)* |
| R5 | Carga del histórico para tendencias | Días | Lotes |

## Verificación contra la salida esperada de la guía

| Comprobación | Resultado |
|---|---|
| Los cinco tienen paradigma y una frase de justificación | ✅ |
| Al menos uno asignado a flujo | ✅ R2 |
| Al menos tres asignados a lotes o casi real | ✅ R1, R3, R4 y R5 |
| No caímos en la trampa del tiempo real | ✅ Solo uno de cinco justifica el flujo |

## Lo que el ejercicio muestra

De cinco requerimientos que provienen del mismo sistema físico y de los mismos sensores, **solo uno
justifica el flujo**. Los otros cuatro se distribuyen entre lotes y casi real. Esa proporción es el
resultado esperado y no una casualidad del caso: la frescura exigida es una propiedad de la
*decisión que el dato alimenta*, no de la tecnología que lo captura ni de la velocidad a la que se
genera. Los mismos sensores de presión alimentan tanto la alerta de segundos como el informe mensual.
