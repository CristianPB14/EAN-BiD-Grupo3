# Guía de Incorporación 

Bienvenido al repositorio central de nuestro proyecto de análisis de contratación pública (SECOP II). Esta guía contiene el paso a paso exacto para que cualquier integrante del grupo pueda configurar su equipo desde cero, replicar el entorno de análisis sin errores y comenzar a auditar los datos.

## 1. Requisitos Previos
Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu computadora local:
* **Git:** Para el control de versiones.
* **Docker Desktop:** Para ejecutar los contenedores aislados (asegúrate de que esté abierto y corriendo en segundo plano).
* **Python 3.12+:** Instalado localmente para ejecutar scripts de preparación.
* **Editor de código:** Visual Studio Code o el editor de tu preferencia.

## 2. Clonar el Repositorio
Abre tu consola (Terminal, CMD o PowerShell), ubícate en la carpeta donde deseas guardar el proyecto y ejecuta los siguientes comandos para descargar el código y entrar a la carpeta:

```bash
git clone [https://github.com/CristianPB14/EAN-BiD-Grupo3.git](https://github.com/CristianPB14/EAN-BiD-Grupo3.git)
cd EAN-BiD-Grupo3
```

## 3. Configuración de Credenciales (.env)
Por lineamientos de seguridad, las contraseñas nunca se suben a GitHub. Debes crear tu propio archivo local para conectar la base de datos:
1. Localiza el archivo `.env.example` en la raíz del proyecto.
2. Haz una copia exacta de este archivo y renómbrala como `.env` (asegúrate de incluir el punto inicial).
3. Abre el archivo `.env` y solicita las contraseñas reales al equipo para completar las variables necesarias (`POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`).

## 4. Obtención de Datos Crudos Pesados (Drive)
Dado el volumen masivo de los expedientes contractuales del SECOP II, los archivos de datos pesados están excluidos del control de versiones.
1. Ingresa a nuestra **carpeta compartida de Google Drive** (solicita el enlace en el grupo).
2. Descarga el archivo principal de la muestra: `secop_sample.csv` (aprox. 304.5 MB).
3. Ubica este archivo exactamente en la ruta: `data/raw/secop_sample.csv` dentro de tu repositorio local. *(Nota: Si las carpetas `data` y `raw` no existen al clonar, debes crearlas manualmente).*

## 5. Generación de la Muestra Sintética
Antes de encender los contenedores, necesitamos procesar los archivos que consumirá la base de datos local.
En tu consola, asegúrate de estar en la raíz del proyecto y ejecuta el siguiente comando local:

```bash
python genera_muestra.py
```
*Este paso poblará la carpeta `muestra/` con los archivos necesarios para levantar el entorno.*

## 6. Levantar el Entorno (Docker Compose)
Con los datos en su sitio y las credenciales listas, procedemos a encender nuestra infraestructura aislada. Ejecuta:

```bash
docker compose -f docker-compose-jupyter.yml up --build -d
```
Esto forzará la construcción de la imagen, descargará las dependencias y levantará tanto nuestro entorno de Jupyter como la base de datos en contenedores independientes.

## 7. Verificación de Reproducibilidad
Para confirmar que tu equipo está sincronizado y libre de errores:
1. Abre tu navegador web e ingresa a `http://localhost:8888`.
2. Navega a la carpeta `notebooks/` y abre el cuaderno `00_verificacion.ipynb`.
3. Ejecuta todas las celdas. 

Si el mensaje final indica **"Entorno reproducible verificado"** y no arroja discrepancias de librerías, tu configuración es un éxito total.

---

### Buenas Prácticas del Equipo
* **Sincronización:** Siempre ejecuta `git pull origin main` antes de iniciar tu jornada para obtener los últimos cambios.
* **Privacidad:** El archivo `.gitignore` ya está configurado para bloquear `.csv` y `.env`. Nunca fuerces la subida de estos archivos.
* **Colaboración:** Mantén la comunicación activa con los demás integrantes del grupo ante cualquier fallo de dependencias para actualizar colectivamente el archivo `requirements.txt`.