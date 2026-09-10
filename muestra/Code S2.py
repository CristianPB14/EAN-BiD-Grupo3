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
