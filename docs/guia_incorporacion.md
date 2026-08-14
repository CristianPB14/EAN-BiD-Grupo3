# Guía de incorporación · primer día en el proyecto acueducto

**Reto de negocio de la sesión 2 · competencia Power Humanise**

Dirigida a alguien que se une al equipo sin haber visto el proyecto antes. Si un paso asume algo que
esa persona no sabría, está mal escrito — reescríbanlo.

## Requisitos previos

- Git instalado y configurado con su nombre y correo.
- Docker Desktop (Windows/macOS) o Docker Engine (Linux), con al menos 8 GB de RAM asignados.
- Una cuenta de GitHub con acceso al repositorio `EAN-BiD-Grupo3`.

## Pasos, del clon al entorno corriendo

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/CristianPB14/EAN-BiD-Grupo3.git
   cd EAN-BiD-Grupo3
   ```
2. Copiar la plantilla de variables de entorno y completarla:
   ```bash
   cp .env.example .env
   # abrir .env y llenar POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
   ```
3. Levantar el stack de Jupyter + Postgres:
   ```bash
   docker compose -f docker-compose-jupyter.yml up --build
   ```
4. Abrir `http://localhost:8888` y ejecutar `notebooks/00_verificacion.ipynb`.
5. Para trabajar con el clúster HDFS + YARN (sesiones 3 y 4), en otra terminal:
   ```bash
   docker compose up -d
   ```
6. Confirmar que el nodo maestro está arriba en `http://localhost:9870` (pestaña *Datanodes*, deben
   verse tres nodos vivos) y el gestor de recursos en `http://localhost:8088`.
7. `COMPLETAR`: agregar cualquier paso específico del equipo que no esté cubierto arriba (por ejemplo,
   dónde conseguir la muestra de datos si no se genera con `genera_muestra.py`).

## Cómo saber que quedó bien

- `notebooks/00_verificacion.ipynb` imprime `"Entorno reproducible verificado."`, sin discrepancias
  de versión.
- La pestaña *Datanodes* de `localhost:9870` muestra tres nodos de datos vivos.

## Si un paso falla

- Revisen primero la tabla "Problemas frecuentes" al final de cada guía de sesión (S2, S3, S4).
- Si el problema persiste, escriban en el canal del equipo antes de perder tiempo solos: es
  exactamente lo que esta guía existe para evitar.

---

*Sesión 2 · Reproducibilidad como requisito de ingeniería. Tributa a Power Humanise: reduce la
fricción de quien llega después y protege el conocimiento del equipo de la salida de una sola
persona.*
