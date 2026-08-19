# S4 · Nota técnica · Agregación por sector rápida y barata

**La solución:** `muestra/mapper.py` emite `sector <tab> presion` por cada lectura; `muestra/combiner.py` agrega suma y conteo localmente en cada nodo antes de la mezcla; `muestra/reducer2.py` suma las sumas y los conteos recibidos y solo entonces divide, para obtener el promedio de presión por sector. El promedio nunca se calcula por partes: el promedio de promedios no es el promedio, por eso el combinador emite `suma,conteo`, nunca un promedio parcial[cite: 3].

**La clave:** el sector, porque es la unidad que responde la pregunta real de la gerencia (presión promedio por sector). Agrupar por cualquier otra columna movería datos por la red sin responder la pregunta que se hizo[cite: 3].

**La evidencia:** El volumen de datos transferidos por la red (`Reduce shuffle bytes`) pasó de **3,418,645 bytes** en la ejecución sin combinador a tan solo **13,583 bytes** con el combinador[cite: 3]. Esto representa una reducción del **99.60%** en el tráfico de red, validando la altísima eficiencia de pre-agregar los datos de los 320,000 registros de lectura directamente en los nodos de mapeo[cite: 3].

**El riesgo:** Al analizar datos reales (como nuestra fuente SECOP II evaluando la modalidad de contratación), evidenciamos un fuerte sesgo de clave[cite: 3]. Modalidades como "Contratación Directa" concentran una proporción altísima de los registros. En estos casos, el combinador reduce el volumen que viaja por la red, pero no soluciona el desbalance entre los reductores: el reductor asignado a la clave principal sigue haciendo casi todo el trabajo final y crea un cuello de botella[cite: 3]. Una clave compuesta (modalidad + entidad, por ejemplo) repartiría mejor la carga, a costa de un resultado más granular que habría que reagregar después[cite: 3].

---
