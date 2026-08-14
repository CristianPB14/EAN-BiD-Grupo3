# S3 · Reto de negocio · Por qué pagamos por guardar cada dato tres veces

**La cifra:** el factor 3 cuesta el triple de almacenamiento físico que el factor 1 (3x frente a 1x),
y el doble frente al factor 2. Con la proyección a doce meses del equipo, eso significa
`COMPLETAR` GB con factor 1 frente a `COMPLETAR` GB con factor 3 (ver `T3_proyeccion_almacenamiento.md`).

**La distinción:** la telemetría histórica de los medidores es dato crítico e irrecuperable — una vez
pasada la hora de una lectura, esa lectura no se puede volver a capturar. Un archivo derivado que se
puede regenerar desde la fuente cruda en minutos (por ejemplo, un agregado diario recalculado desde
las lecturas horarias) no necesita la misma resiliencia.

**La recomendación:** factor de réplica 3 para la telemetría cruda histórica; factor 1 o 2 para
productos derivados y regenerables. `COMPLETAR`: ajusten esta recomendación a la fuente real del
equipo y justifiquen con la razón de negocio (qué se pierde si el dato desaparece), no con la razón
técnica.

**La alternativa:** cuando el costo de almacenamiento del factor 3 empiece a pesar en el presupuesto y
el dato lo permita, valdría la pena evaluar códigos de borrado (*erasure coding*) como alternativa más
económica que la triple copia — mismo nivel de tolerancia a fallos con menos espacio físico, a costa
de mayor complejidad de cómputo al reconstruir. No se implementa en esta sesión; se deja como línea
de exploración futura.

---

*Sesión 3 · competencia Emprendimiento Sostenible.*
