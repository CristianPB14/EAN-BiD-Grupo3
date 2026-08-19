# S5 · Evidencia de Versionado e Inmutabilidad

**Salida de la prueba de sobrescritura en MinIO:**
```text
--- INICIANDO PRUEBA DE VERSIONADO ---
Versionado activado en el cubo 'cruda'.
Sobrescribiendo el archivo para generar una nueva versión...

Historial de versiones en el sistema:
ID Versión: 95dcb1cb-48b4-4418-b80c-1d10184f3cdf | ¿Es la actual?: True | Fecha: 2026-08-19 20:52:16.903000+00:00
ID Versión: null | ¿Es la actual?: False | Fecha: 2026-08-19 20:52:13.737000+00:00
```

**Justificación de inmutabilidad:**
La política arquitectónica de la capa cruda dicta que los datos "no se tocan" para garantizar la fidelidad con la fuente original. Al habilitar el versionado a nivel del contenedor S3/MinIO, garantizamos esta inmutabilidad mediante infraestructura, no solo mediante reglas de equipo. Como demuestra la consola, si un usuario o proceso sobrescribe un archivo por error humano o fallo lógico, la versión original (en este caso la versión `null`) sigue existiendo y es 100% recuperable, protegiendo el activo más importante del lago de datos.