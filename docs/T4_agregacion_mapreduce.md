# T4 · Agregación en clave map y reduce, con estimación de mezcla

**Sesión 4 · El modelo MapReduce**

## 1. La agregación de referencia (nivel 1, ya en el repositorio)

- **Mapper:** `muestra/mapper.py` — emite `sector <tab> presion` por cada lectura.
- **Reducer:** `muestra/reducer.py` — promedia la presión por sector.
- **Clave:** el sector (aproximado por `sensor_id` en la muestra sintética).

## 2. Con combinador (nivel 2, ya en el repositorio)

- **Combinador:** `muestra/combiner.py` — agrega suma y conteo localmente antes de la mezcla.
- **Reducer adaptado:** `muestra/reducer2.py` — suma las sumas, suma los conteos, divide solo al
  final.

| Ejecución | Bytes de mezcla | Cómo se midió |
|---|---|---|
| Sin combinador (nivel 1) | `COMPLETAR` | Contadores del job, `http://localhost:8188` o salida de la ejecución |
| Con combinador (nivel 2) | `COMPLETAR` | Ídem |
| Reducción porcentual | `COMPLETAR` % | `(sin − con) / sin` |

**Verificación de correctitud:** `COMPLETAR` — confirmar que el resultado por sector es idéntico
entre `reducer.py` (nivel 1) y `reducer2.py` (nivel 2).

## 3. Agregación propia del equipo (nivel 3)

- **Pregunta de negocio que responde:** `COMPLETAR`
- **Clave de agrupación elegida:** `COMPLETAR` — y por qué esta clave y no otra
- **Predicción antes de ejecutar** (orden de magnitud de pares/bytes en la mezcla, con y sin
  combinador): `COMPLETAR`
- **Medición real tras ejecutar:** `COMPLETAR`
- **Contraste predicción vs. medición:** `COMPLETAR` — no hace falta acertar el número exacto, sí
  razonar por qué la predicción se acercó o se alejó

## 4. Sesgo de clave

`COMPLETAR`: ¿alguna clave concentra una proporción alta de los registros? Si es así, ¿qué harían al
respecto? (por ejemplo, una clave compuesta que reparta mejor, a costa de un resultado más granular).

---

*Criterio de aceptación: el trabajo produce la agregación correcta, el equipo estima el volumen de
mezcla y lo contrasta con el contador real, y la elección de clave queda justificada por su efecto en
ese volumen — reproducible por otra persona.*
