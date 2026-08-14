# S2 · Nivel 3 · Frontera del contenedor

Dónde vive cada elemento del proyecto, y por qué.

| Elemento | ¿Dentro de la imagen? ¿Volumen montado? ¿En el compose? ¿En `.env`? | Justificación |
|---|---|---|
| Código de los cuadernos | Volumen montado (`./notebooks:/home/jovyan/work/notebooks`) | Cambia constantemente durante el desarrollo; reconstruir la imagen por cada edición sería lento. Se versiona en Git, no en la imagen. |
| Librerías de Python | Dentro de la imagen, instaladas desde `requirements.txt` al construir/levantar el contenedor | Son iguales para todo el equipo; deben quedar fijas y no depender de qué tenga cada persona en su máquina. |
| Datos crudos | Volumen montado (`./data:/home/jovyan/work/data`), y **nunca entran a Git** (`data/raw/*` en `.gitignore`) | Son grandes, binarios, y cambian de tamaño constantemente; harían el repositorio inmanejable. Se documentan en la ficha técnica (T1), no se versionan aquí. |
| Credenciales de la base de datos | Archivo `.env`, inyectadas al compose con `${POSTGRES_USER}` etc. | Nunca deben quedar en texto plano en un archivo versionado (ver la corrección en `notebooks/01_conexion_db.ipynb`). `.env` está en `.gitignore`; `.env.example` sí se versiona, sin valores. |
| Configuración del clúster HDFS/YARN (`hadoop.env`) | Se versiona en la raíz del repositorio | No contiene secretos, solo nombres de servicio y rutas internas del clúster; todo el equipo necesita exactamente los mismos valores para que los nodos se descubran entre sí. |

## Prueba en entorno limpio

`COMPLETAR`: documenten aquí el resultado de reproducir el proyecto en una máquina distinta (otro
equipo del grupo, una máquina virtual, o GitHub Codespaces). Casi siempre algo falla la primera vez —
ese hallazgo es el que hay que registrar, no ocultar.

- **Qué probaron:** `COMPLETAR`
- **Qué falló la primera vez:** `COMPLETAR`
- **Cómo lo resolvieron:** `COMPLETAR`

---

*Sesión 2, nivel 3. Sin ruta única: lo que se evalúa es que cada decisión tenga una razón, no que
coincida con una respuesta modelo.*
