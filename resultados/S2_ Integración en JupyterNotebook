### Dependencias 
pandas==2.2.2
numpy==1.26.4
jupyterlab==4.2.0
psutil==5.9.8
psycopg2-binary==2.9.9  

-----------------------------------------------------------------------------------------
### Servicios:

Se crea un entorno multi-contenedor que integre Jupyter Notebook y una base de datos PostgreSQL, 
utilizando variables de entorno y red interna de Docker.

version: '3.8'

services:
  jupyter:
    image: jupyter/scipy-notebook:python-3.11
    container_name: acueducto_jupyter
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work/notebooks
      - ./data:/home/jovyan/work/data
      - ./requirements.txt:/tmp/requirements.txt
    environment:
      - DB_HOST=db
      - DB_NAME=${POSTGRES_DB}
      - DB_USER=${POSTGRES_USER}
      - DB_PASSWORD=${POSTGRES_PASSWORD}
    command: >
      bash -c "pip install -r /tmp/requirements.txt &&
      start-notebook.sh --NotebookApp.token=''"
    depends_on:
      - db
    networks:
      - red-acueducto

  db:
    image: postgres:16-alpine
    container_name: acueducto_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - red-acueducto

volumes:
  pgdata:

networks:
  red-acueducto:
    driver: bridge

--------------------------------------------------------------------------

El archivo de dependencias contiene las librerías que necesita el proyecto para funcionar correctamente. En este caso se utilizan `pandas`, `numpy`, `jupyterlab`, `psutil` y `psycopg2-binary`, cada una con una versión específica. `pandas` y `numpy` permiten realizar el procesamiento y análisis de los datos, mientras que `jupyterlab` proporciona el entorno para trabajar con los notebooks. `psutil` permite consultar información relacionada con los recursos del sistema y `psycopg2-binary` permite establecer la comunicación entre Python y la base de datos PostgreSQL. Especificar las versiones de cada librería permite que el proyecto sea reproducible y que diferentes personas puedan trabajar con un entorno de software equivalente.

Para la ejecución del proyecto se utiliza Docker Compose, que permite crear y administrar varios contenedores que trabajan de manera conjunta. En este caso se crea un entorno compuesto por dos servicios principales: un contenedor para Jupyter y otro para PostgreSQL. De esta manera, las herramientas necesarias para analizar los datos y almacenar la información se encuentran separadas, pero pueden comunicarse entre sí mediante una red interna de Docker.

El servicio de Jupyter utiliza la imagen `jupyter/scipy-notebook:python-3.11`, que proporciona un entorno preparado para trabajar con Jupyter y Python 3.11. Además, se establece el nombre del contenedor como `acueducto_jupyter` y se utiliza el puerto `8888`, permitiendo acceder a Jupyter desde el navegador. También se crean volúmenes para conectar las carpetas locales de `notebooks` y `data` con las carpetas correspondientes dentro del contenedor. Esto permite que los notebooks y los datos permanezcan disponibles aunque el contenedor sea detenido o recreado. De igual manera, el archivo `requirements.txt` se comparte con el contenedor para que pueda instalar automáticamente las dependencias necesarias.

El servicio de Jupyter también recibe variables de entorno relacionadas con la conexión a la base de datos. Entre ellas se encuentran el nombre del host, el nombre de la base de datos, el usuario y la contraseña. La variable `DB_HOST` utiliza el valor `db`, que corresponde al nombre del servicio de PostgreSQL dentro de Docker. Esto permite que Jupyter encuentre y se comunique con la base de datos utilizando la red interna, sin depender de configuraciones específicas del computador donde se ejecuta el proyecto.

Al iniciar el contenedor de Jupyter, primero se ejecuta el comando `pip install -r /tmp/requirements.txt`, que instala las librerías especificadas en el archivo de dependencias. Una vez terminada correctamente esta instalación, se ejecuta `start-notebook.sh` para iniciar Jupyter. El parámetro utilizado permite acceder al notebook sin tener que introducir un token. Además, mediante `depends_on` se establece que el servicio de Jupyter depende del servicio de PostgreSQL, por lo que Docker inicia primero el contenedor de la base de datos.

El segundo servicio corresponde a PostgreSQL y utiliza la imagen `postgres:16-alpine`, que proporciona PostgreSQL versión 16 sobre una distribución ligera. El contenedor recibe el nombre `acueducto_postgres` y utiliza las variables de entorno `POSTGRES_DB`, `POSTGRES_USER` y `POSTGRES_PASSWORD` para definir el nombre de la base de datos, el usuario y la contraseña. Estos valores pueden mantenerse fuera del archivo principal mediante un archivo de variables de entorno, evitando escribir directamente las credenciales dentro de la configuración del proyecto.

PostgreSQL utiliza el puerto `5432`, que es el puerto habitual de este sistema gestor de bases de datos. También se configura un volumen llamado `pgdata`, conectado con la ubicación donde PostgreSQL almacena sus datos dentro del contenedor. Esto permite conservar la información de la base de datos aunque el contenedor sea eliminado y posteriormente creado nuevamente. De esta manera, los datos tienen persistencia y no dependen únicamente del ciclo de vida del contenedor.

Finalmente, tanto Jupyter como PostgreSQL están conectados a una red interna llamada `red-acueducto`, utilizando el controlador `bridge`. Esta red permite que ambos contenedores se comuniquen entre sí de forma directa mediante sus nombres de servicio. Por ejemplo, desde Jupyter se puede utilizar `db` como host para conectarse a PostgreSQL. En conjunto, esta configuración crea un entorno aislado y reproducible en el que Jupyter se encarga del análisis de datos, PostgreSQL del almacenamiento y gestión de la información, y Docker Compose de coordinar los servicios, sus dependencias, sus redes y sus volúmenes.
