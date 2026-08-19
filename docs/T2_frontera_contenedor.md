# T2 · Frontera del Contenedor y Clon Limpio

**Sesión 2 · Reproducibilidad y Entornos Aislados**

Este documento registra los hallazgos y correcciones realizados al someter nuestro repositorio a la prueba del "clon limpio" en un equipo físico diferente (laptop) al de desarrollo original (PC de escritorio). El objetivo es documentar qué elementos no viajan en el código y cómo aseguramos que cualquier integrante del grupo pueda levantar el proyecto sin errores.

## 1. Prueba en entorno limpio: Registro de fallos

Al intentar levantar el proyecto clonado desde cero, identificamos las siguientes fricciones en la frontera del contenedor:

*   **Fallo 1: Ausencia de variables de entorno y credenciales expuestas**
    *   **El problema:** El contenedor de la base de datos no pudo levantarse porque el archivo `.env` no viajó con el código (está protegido por el `.gitignore`). Además, detectamos que el cuaderno `01_conexion_db.ipynb` tenía credenciales escritas en texto plano (como `usuario_acueducto`), vulnerando la seguridad.
    *   **La solución:** Inicialmente se transfirió el archivo `.env` de forma manual entre los equipos. Para sistematizar la solución para el resto del equipo, creamos el archivo plantilla `.env.example`. Adicionalmente, refactorizamos la conexión en el notebook para que lea las contraseñas de forma invisible desde el sistema operativo usando `os.environ`[cite: 1].

*   **Fallo 2: Ausencia de datos crudos (`FileNotFoundError`)**
    *   **El problema:** Al ejecutar el cuaderno `s01_perfilamiento.ipynb`, el código arrojó un error indicando que no encontraba la ruta del archivo `secop_sample.csv`[cite: 1]. Esto ocurrió porque Git ignoró correctamente el archivo pesado original (de más de 300 MB), dejando la carpeta `data/raw/` vacía en el nuevo clon.
    *   **La solución:** En lugar de transferir el archivo manualmente mediante memorias USB, creamos una carpeta compartida en Google Drive con los documentos masivos centralizados. Se estableció como regla para los integrantes del grupo que el primer paso tras clonar es descargar `secop_sample.csv` desde el Drive y ubicarlo manualmente en la carpeta `data/raw/`.

*   **Fallo 3: Ausencia de la muestra procesada**
    *   **El problema:** Los contenedores que dependen de los datos de la carpeta `muestra/` fallarían porque esta carpeta tampoco existe en un repositorio recién clonado desde GitHub.
    *   **La solución:** Documentamos en la guía de incorporación la necesidad de ejecutar el script `python genera_muestra.py` en la consola local antes de iniciar los contenedores, garantizando que el entorno tenga los datos sintéticos listos[cite: 1].

## 2. Verificación de dependencias

Tras aplicar las soluciones documentadas (crear el `.env`, descargar los datos del Drive y generar la muestra), ejecutamos el cuaderno `00_verificacion.ipynb`[cite: 1]. 

El entorno se ejecutó exitosamente sin arrojar discrepancias en las versiones de las librerías. Esto nos confirma que la imagen de Docker está aislando y congelando correctamente las dependencias de Python establecidas en la Sesión 2, garantizando que el código del SECOP II corra exactamente igual en cualquier máquina del equipo[cite: 1].

## 3. Errores al realizar actualizaciones en git

En una de las actualizaciones se subió por error el archivo ideam_sample.csv