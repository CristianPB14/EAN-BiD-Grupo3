# Reto de Negocio - Sesión 5: Mapa del Lago de Datos

¡Hola! Si acabas de unirte al equipo y necesitas encontrar o procesar datos en nuestro Lago de Datos local (MinIO), esta guía rápida es para ti.

## 1. El Mapa de los Cubos (Buckets)
Nuestro almacenamiento está dividido estrictamente en tres niveles:
*   **`cruda/`**: Los datos originales exactamente como se descargaron de la fuente pública. Aquí nada se filtra ni se altera.
*   **`refinada/`**: Los datos limpios, con tipos corregidos (fechas, números) y guardados en formato eficiente (Parquet).
*   **`consolidada/`**: Tablas resumen cruzadas y agrupadas, listas para responder preguntas de negocio o alimentar tableros.

## 2. La Regla de Oro
**Los errores se corrigen aguas abajo, NUNCA reescribiendo la capa cruda.**
Si encuentras un error de formato (como comas atravesadas en SECOP II que rompen las columnas), debes corregir el script que transforma los datos de cruda a refinada. El archivo en `cruda/` jamás se edita; esto garantiza que siempre podamos reprocesar la historia completa si nuestra lógica de limpieza falla.

## 3. Plantillas de Rutas por Capa
Usamos particionado estilo Hive (`clave=valor`) para optimizar el rendimiento de las consultas y descartar datos que no necesitamos leer:
*   **Cruda:** `cruda/<fuente>/anio=YYYY/mes=MM/dia=DD/<archivo>.csv`
*   **Refinada:** `refinada/<fuente>/departamento=<departamento>/anio=YYYY/<entidad>.parquet`
*   **Consolidada:** `consolidada/<dominio_negocio>/<tabla_agregada>/anio=YYYY/<archivo>.parquet`

## 4. Ejemplo Resuelto de Búsqueda
**Caso:** "Necesitas auditar los contratos originales de SECOP II del 19 de agosto de 2026".
**Ruta exacta que debes consultar sin preguntarle a nadie:**
`cruda/secop/anio=2026/mes=08/dia=19/secop_sample.csv`