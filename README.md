# EAN-BiD-Grupo3 · Proyecto Big Data e Ingeniería de Datos

**IFPN0025 · Universidad Ean · Facultad de Ingeniería · Ingeniería en Ciencia de Datos**
Docente: Jaime Alberto Ochoa Durán · Módulo 1: Fundamentos de Big Data y arquitecturas de datos

Este repositorio contiene el proyecto acumulativo del curso, construido sesión a sesión sobre el
caso hipotético del **acueducto de una ciudad intermedia colombiana**: una fuente de datos que pasa
de 11 MB a varios GB al mes por telemedición, y que sirve de hilo conductor para decidir, con cifras,
cuándo un problema de datos deja de resolverse con "un computador más grande".

Cada sesión entrega una tarea (T1, T2, T3...) que **consume la anterior y habilita la siguiente**. Este
README existe para que cualquier persona con acceso pueda entender su contenido.

El link de acceso para las bases de datos del SECOP, IDEAM y la Gran Encuesta del Dane es el siguiente: https://drive.google.com/drive/folders/1oaHmNeKaV13TV4X8bhu0gpUeFiZC6VlI?usp=sharing

---

## 1. Estado del avance (S1 → S4)

Leyenda: ✅ completo · 🟡 plantilla lista, falta completar con cifras propias o correr en el clúster ·
❌ pendiente

| Sesión | Nivel 1 | Nivel 2 | Nivel 3 | Reto de negocio | Tarea acumulativa |
|---|---|---|---|---|---|
| **S1** | ✅ `notebooks/s01_perfilamiento.ipynb` mide k y perfila SECOP II, IDEAM y GEIH | 🟡 Cálculo corregido y dinámico; reflexión en `resultados/s1_nivel2_sensibilidad.md`, falta confirmar con cifras frescas | 🟡 `resultados/s1_nivel3_matriz.md`, con evidencia real de SECOP y GEIH; faltan veracidad y valor | 🟡 `resultados/s1_reto_negocio.md`, falta declarar uso de IA y verificar cifras | 🟡 `docs/ficha_tecnica_T1.md`, falta elegir fuente única y llenar los 7 elementos |
| **S2** | ✅ `notebooks/00_verificacion.ipynb` | 🟡 Postgres alcanzable **y credenciales ya corregidas** (antes hardcodeadas); falta reconstruir el contenedor y confirmar sin discrepancias | 🟡 `docs/T2_frontera_contenedor.md`, tabla completa; falta la prueba en clon limpio | 🟡 `docs/guia_incorporacion.md` | 🟡 README y `docs/` ya existen; falta la prueba de clon limpio |
| **S3** | 🟡 Clúster ya arranca en un clon limpio (`hadoop.env` corregido); falta ejecutar y guardar evidencia en `resultados/s3_evidencia_fsck.md` | ❌ `resultados/s3_comparacion_factores.md` — plantilla y fórmulas listas, falta medir en el clúster | ❌ `docs/T3_proyeccion_almacenamiento.md` — plantilla lista, falta decidir factor/bloque con cifras propias | 🟡 `resultados/s3_reto_negocio.md` | ❌ Documento de T3 nunca existió (el commit lo mencionaba, el archivo no); ya está la plantilla |
| **S4** | ✅ `muestra/mapper.py`, `muestra/reducer.py`; clúster con YARN ya arranca | 🟡 `muestra/combiner.py` y `muestra/reducer2.py` ya creados; falta ejecutar y medir en `resultados/s4_contadores_mezcla.md` | ❌ `docs/T4_agregacion_mapreduce.md` — plantilla lista, falta la agregación propia del equipo | 🟡 `resultados/s4_reto_negocio.md` | ❌ Documento de T4, plantilla lista en `docs/` |

**Lo que se corrigió en esta pasada** (ver sección 4 para el detalle):
`.gitignore`, `hadoop.env`, `.env.example`, credenciales del notebook de Postgres, y las celdas de
umbral del notebook de S1 que estaban desalineadas con la medición real.

**Lo que sigue requiriendo trabajo del equipo**, porque depende de ejecutar sobre el clúster real o
de decisiones que solo el equipo puede tomar: todo lo marcado 🟡 o ❌ arriba. Cada plantilla en
`docs/` y `resultados/` tiene marcas `COMPLETAR` en los puntos exactos que faltan.

---

## 2. Estructura del repositorio

```
EAN-BiD-Grupo3/
├── README.md
├── docker-compose.yml               # clúster HDFS + YARN (S3 + S4 fusionados)
├── docker-compose-jupyter.yml       # Jupyter + Postgres (S2)
├── hadoop.env                       # config del clúster, sin secretos (corregido en esta pasada)
├── .env.example                     # plantilla de credenciales de Postgres, sin valores
├── requirements.txt
├── .gitignore                       # corregido: ya no bloquea hadoop.env ni resultados/
├── genera_muestra.py
├── muestra/
│   ├── mapper.py                    # S4 nivel 1
│   ├── reducer.py                   # S4 nivel 1
│   ├── combiner.py                  # S4 nivel 2 (nuevo)
│   └── reducer2.py                  # S4 nivel 2 (nuevo)
├── data/
│   └── raw/                         # nunca se versiona, solo .gitkeep
├── notebooks/
│   ├── 00_verificacion.ipynb        # S2 nivel 1
│   ├── 01_conexion_db.ipynb         # S2 nivel 2 — credenciales corregidas
│   └── s01_perfilamiento.ipynb      # S1 niveles 1 y 2 — celdas de umbral corregidas
├── src/
│   └── README.md                    # explica el propósito de la carpeta, hoy vacía
├── docs/
│   ├── ficha_tecnica_T1.md          # nuevo — plantilla T1
│   ├── guia_incorporacion.md        # nuevo — S2 reto de negocio
│   ├── T2_frontera_contenedor.md    # nuevo — S2 nivel 3
│   ├── T3_proyeccion_almacenamiento.md  # nuevo — plantilla T3
│   └── T4_agregacion_mapreduce.md   # nuevo — plantilla T4
└── resultados/
    ├── s1_nivel2_sensibilidad.md    # nuevo
    ├── s1_nivel3_matriz.md          # nuevo
    ├── s1_reto_negocio.md           # nuevo
    ├── s3_evidencia_fsck.md         # nuevo — plantilla, requiere clúster
    ├── s3_comparacion_factores.md   # nuevo — plantilla, requiere clúster
    ├── s3_reto_negocio.md           # nuevo
    ├── s4_contadores_mezcla.md      # nuevo — plantilla, requiere clúster
    └── s4_reto_negocio.md           # nuevo
    # mediciones.csv se genera solo al ejecutar s01_perfilamiento.ipynb — no se
    # fabrica a mano, ver sección 3
```

---

## 3. Cómo levantar el entorno

### 3.1 Jupyter + Postgres (sesión 2)

```bash
git clone https://github.com/CristianPB14/EAN-BiD-Grupo3.git
cd EAN-BiD-Grupo3
cp .env.example .env        # complete POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose -f docker-compose-jupyter.yml up --build
```

Abra `http://localhost:8888` y ejecute, en este orden:
1. `notebooks/00_verificacion.ipynb` — debe reportar **sin discrepancias** de versión.
2. `notebooks/s01_perfilamiento.ipynb` — al ejecutarlo completo, genera automáticamente
   `resultados/mediciones.csv` con las cifras reales de SECOP II, IDEAM y GEIH. Este archivo ya no
   está bloqueado por el `.gitignore`; agréguenlo a Git tras ejecutar el notebook.
3. `notebooks/01_conexion_db.ipynb` — ahora lee las credenciales desde `.env`, no las tiene escritas.

### 3.2 Clúster HDFS + YARN (sesiones 3 y 4)

```bash
docker compose up -d
```

`hadoop.env` ya está en el repositorio (antes lo bloqueaba el `.gitignore`), así que esto debería
levantar directamente en un clon limpio. Interfaces: `localhost:9870` (NameNode), `localhost:8088`
(YARN), `localhost:8188` (historial de trabajos).

Al terminar: `docker compose down` (agreguen `-v` solo si quieren borrar también los datos).

---

## 4. Qué se corrigió en esta pasada

1. **`.gitignore`** — el patrón `*.env` bloqueaba `hadoop.env` sin querer (sin él, el clúster no
   arrancaba en ningún clon nuevo), y la línea `resultados/` bloqueaba toda la evidencia que las
   guías piden versionar. Ambos se corrigieron.
2. **`hadoop.env`** — creado con la configuración de HDFS (S3) y YARN (S4) que el
   `docker-compose.yml` ya esperaba.
3. **`.env.example`** — plantilla sin valores para las credenciales de Postgres.
4. **`notebooks/01_conexion_db.ipynb`** — ya no tiene `usuario_acueducto` / `clave_segura_123` en
   texto plano; lee `os.environ["POSTGRES_USER"]`, etc.
5. **`notebooks/s01_perfilamiento.ipynb`** — las celdas de umbral (escenarios 8/16 GB y sensibilidad
   a `g`) usaban un diccionario de `k`/`S0` copiado a mano, desalineado con la medición real de la
   celda anterior (por ejemplo, `k=3.02` a mano contra `k=3.38` medido para SECOP II). Ahora leen
   `df_measurements` directamente, así que no pueden volver a desincronizarse. Se agregó además una
   celda con las respuestas escritas que pide el nivel 2, marcadas como borrador a confirmar.
6. **`muestra/combiner.py` y `muestra/reducer2.py`** — no existían. Se crearon siguiendo el patrón de
   la guía de S4 (emiten y reciben `suma,conteo`, nunca un promedio parcial), con un detalle de
   diseño propio: aceptan tanto la salida cruda del mapper como su propia salida previa, porque
   Hadoop no garantiza cuántas veces se ejecuta un combinador.
7. **`docs/` y `resultados/`** — no existían. Se crearon con plantillas para cada entregable de T1 a
   T4, prellenadas con las cifras reales ya disponibles en el repositorio donde las hay (por ejemplo,
   la matriz de V usa los valores de `k` medidos y señala que GEIH se perfiló con una sola columna,
   evidencia de variedad que hay que confirmar), y con marcas `COMPLETAR` donde hace falta ejecutar
   sobre el clúster real o tomar una decisión que le corresponde al equipo.

## 5. Lo que el equipo todavía tiene que hacer

Ninguna de las plantillas reemplaza el trabajo del curso — señalan exactamente dónde va cada cosa.
Quedan pendientes, y no se pueden resolver sin correr el clúster o decidir en equipo:

- Elegir la fuente única del proyecto (o la combinación) y completar `docs/ficha_tecnica_T1.md`.
- Reconstruir el contenedor de Jupyter y confirmar que `00_verificacion.ipynb` ya no reporta
  discrepancia de versiones.
- Levantar el clúster HDFS, guardar la evidencia real de `fsck` y la comparación de factores de
  réplica (S3), y decidir factor/bloque con cifras propias en `docs/T3_proyeccion_almacenamiento.md`.
- Ejecutar el trabajo MapReduce con y sin combinador, medir los bytes de mezcla reales, y diseñar la
  agregación propia del nivel 3 (S4) en `docs/T4_agregacion_mapreduce.md`.
- Revisar y firmar cada reto de negocio en `resultados/`, incluida la declaración de uso de IA que
  pide la guía de S1.

---

## 6. Equipo y flujo de trabajo

Grupo 3 · IFPN0025. Desde la S3 el trabajo es en equipo (los cuestionarios siguen siendo
individuales). El historial de commits hoy solo muestra un contribuidor — si los tres integrantes
están aportando, conviene que cada quien haga push con su propio usuario de Git para que el historial
refleje el trabajo real del equipo.

Antes de cada commit: `git status --short` y confirmen que nada bajo `data/`, `muestra/*.csv` ni
ningún archivo `.env` aparece en la lista.

---

## 7. Material de referencia

- Kleppmann, M. (2017). *Designing data-intensive applications*. O'Reilly Media.
- Reis, J., y Housley, M. (2022). *Fundamentals of data engineering*. O'Reilly Media.
- Shvachko, K., Kuang, H., Radia, S., y Chansler, R. (2010). The Hadoop Distributed File System.
- Dean, J., y Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters.

---

*IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean · Facultad de Ingeniería · Ingeniería en
Ciencia de Datos. Repositorio de trabajo del Grupo 3.*
