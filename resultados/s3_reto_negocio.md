# S3 · Reto de negocio · Por qué pagamos por guardar cada dato tres veces

**La cifra:** el factor 3 cuesta el triple de almacenamiento físico que el factor 1 (3x frente a 1x),
y el doble frente al factor 2. Con la proyección a doce meses del equipo, eso significa
0.5468 GB con factor 1 frente a 1.6405 GB con factor 3 (ver `T3_proyeccion_almacenamiento.md`).

**La distinción:** los expedientes crudos de contratación estatal (SECOP II) poseen un estricto valor probatorio y de auditoría legal. Si un registro original desaparece durante un proceso de control fiscal o veeduría, se rompe la trazabilidad de los recursos del Estado. Por el contrario, un archivo derivado que se puede regenerar desde la fuente cruda en minutos (por ejemplo, un tablero agregado con los promedios de gasto mensual por departamento) no necesita la misma resiliencia.

**La recomendación:** factor de réplica 3 para la base histórica cruda del SECOP II; factor 1 o 2 para
productos derivados e informes agregados. La razón de negocio radica en el altísimo riesgo normativo y reputacional: la pérdida de contratos públicos ante una falla de servidores representaría una vulneración grave a los principios de transparencia. Dado que el volumen proyectado a un año (1.64 GB físicos) es económicamente marginal, asumir el costo de la triple copia no es un gasto en discos duros, sino la adquisición de una póliza de seguro indispensable para la integridad jurídica de los datos.

**La alternativa:** cuando el costo de almacenamiento del factor 3 empiece a pesar en el presupuesto y
el dato lo permita, valdría la pena evaluar códigos de borrado (*erasure coding*) como alternativa más
económica que la triple copia — mismo nivel de tolerancia a fallos con menos espacio físico, a costa
de mayor complejidad de cómputo al reconstruir. No se implementa en esta sesión; se deja como línea
de exploración futura.

---

