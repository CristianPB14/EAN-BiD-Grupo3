# S4 · Nota técnica · Agregación por sector rápida y barata

**La solución:** `muestra/mapper.py` emite `sector <tab> presion` por cada lectura; `muestra/combiner.py`
agrega suma y conteo localmente en cada nodo antes de la mezcla; `muestra/reducer2.py` suma las sumas
y los conteos recibidos y solo entonces divide, para obtener el promedio de presión por sector. El
promedio nunca se calcula por partes: el promedio de promedios no es el promedio, por eso el
combinador emite `suma,conteo`, nunca un promedio parcial.

**La clave:** el sector, porque es la unidad que responde la pregunta real de la gerencia (presión
promedio por sector). Agrupar por cualquier otra columna movería datos por la red sin responder la
pregunta que se hizo.

**La evidencia:** `COMPLETAR` — bytes de mezcla con y sin combinador, tomados de
`resultados/s4_contadores_mezcla.md`, no supuestos.

**El riesgo:** `COMPLETAR` — ¿algún sector concentra una proporción alta de las lecturas? Si es así,
el combinador reduce el volumen que viaja, pero no el desbalance entre reductores: el reductor de ese
sector sigue haciendo casi todo el trabajo. Una clave compuesta (sector + hora, por ejemplo) repartiría
mejor, a costa de un resultado más granular que habría que reagregar después.

---

*Sesión 4 · competencia TECH IA MAKER.*
