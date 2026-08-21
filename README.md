# EAN-BiD-Grupo3 · Proyecto Big Data e Ingeniería de Datos

**IFPN0025 · Universidad Ean · Facultad de Ingeniería · Ingeniería en Ciencia de Datos**
Docente: Jaime Alberto Ochoa Durán · Módulo 1: Fundamentos de Big Data y arquitecturas de datos

Este repositorio contiene el proyecto acumulativo del curso, construido sesión a sesión sobre el
caso hipotético del **acueducto de una ciudad intermedia colombiana**: una fuente de datos que pasa
de 11 MB a varios GB al mes por telemedición, y que sirve de hilo conductor para decidir, con cifras,
cuándo un problema de datos deja de resolverse con "un computador más grande".

Cada sesión entrega una tarea (T1, T2, T3...) que **consume la anterior y habilita la siguiente**. Este
README existe para que cualquier persona con acceso pueda entender su contenido.

> **Fuente única del proyecto: SECOP II** (Contratos Electrónicos, conjunto `jbjy-vk9h` del Portal de
> Datos Abiertos). La decisión se tomó en la sesión 3 y está justificada en
> `docs/T3_proyeccion_almacenamiento.md`, sección 0. IDEAM y la GEIH se perfilaron en la sesión 1
> como fuentes de contraste, pero no son la fuente del proyecto.

Los datos crudos no se versionan. Están centralizados en la carpeta compartida del equipo:
https://drive.google.com/drive/folders/1oaHmNeKaV13TV4X8bhu0gpUeFiZC6VlI?usp=sharing

---

## 1. Estado del avance (S1 → S6)

Leyenda: ✅ completo · 🟡 en curso · ❌ pendiente

| Sesión | Nivel 1 | Nivel 2 | Nivel 3 | Reto de negocio | Tarea acumulativa |
|---|---|---|---|---|---|
| **S1** | ✅ `notebooks/s01_perfilamiento.ipynb` mide k y perfila SECOP II, IDEAM y GEIH | ✅ Cálculo corregido y dinámico; reflexión en `resultados/s1_nivel2_sensibilidad.md` | ✅ `resultados/s1_nivel3_matriz.md`, matriz completada | ✅ `resultados/s1_reto_negocio.md`, con declaración de uso de IA | ✅ `docs/ficha_tecnica_T1.md`, fuente única elegida (**SECOP II**) y ficha completada |
| **S2** | ✅ `notebooks/00_verificacion.ipynb` sin discrepancias | ✅ Postgres alcanzable por nombre de servicio y credenciales fuera del código | ✅ `docs/T2_frontera_contenedor.md`, con cuatro fallos documentados en clon limpio | ✅ `docs/guia_incorporacion.md` | ✅ Repositorio reproducible, dependencias ancladas |
| **S3** | ✅ Clúster de 4 nodos; `fsck` evidenciado en `resultados/s3_evidencia_fsck.md` | ✅ `resultados/s3_comparacion_factores.md` con mediciones reales de R=1, 2 y 3 | ✅ `docs/T3_proyeccion_almacenamiento.md`, decisión de factor y bloque justificada | ✅ `resultados/s3_reto_negocio.md` | ✅ T3 completada |
| **S4** | ✅ `muestra/mapper.py` y `reducer.py`; YARN operativo | ✅ Combinador ejecutado, contadores en `resultados/s4_contadores_mezcla.md` | ✅ `docs/T4_agregacion_mapreduce.md`, agregación propia sobre SECOP II | ✅ `resultados/s4_reto_negocio.md` | ✅ T4 completada |
| **S5** | ✅ MinIO levantado y los tres cubos creados | ✅ Versionado e inmutabilidad en `resultados/s5_versionado.md` | ✅ `docs/T5_convencion_lago.md`, convención de rutas de las tres capas | ✅ `resultados/s5_reto_negocio.md` | ✅ T5 completada |
| **S6** | ✅ Tres codecs medidos en `resultados/s6_tabla_codecs.md` | ✅ Consulta con DuckDB sobre Parquet contra CSV, y poda de particiones | ✅ `docs/T6_formato_y_codec.md`, codec elegido con la medición propia | ✅ `resultados/s6_reto_negocio.md` | ✅ T6 completada, Parquet depositado en la capa refinada |

**Cifras consolidadas del proyecto**

| Sesión | Hallazgo medido |
|---|---|
| S1 | SECOP II: `S₀ = 0,3045 GB`, `k = 3,37`, `M = 11,20 GB`, `g = 5 %` supuesto → **`t_umbral` = 49,0 meses** |
| S3 | 10 bloques de 1 MB con `Live_repl=3`. Almacenamiento físico 9,9 / 19,8 / 29,6 MB para R = 1, 2 y 3 |
| S3 | Proyección a 12 meses: **0,5468 GB lógicos**; con R=3, 1,6404 GB físicos |
| S4 | Mezcla de **3.418.645 → 13.583 bytes** con combinador (−99,6 %); 320.000 → 500 registros |
| S6 | CSV 326,9 MB → Parquet zstd **52,9 MB (−83 %)**. Consultas **33,6× más rápidas** con DuckDB |

**Lo que se corrigió y se logró durante la ejecución del proyecto**

Se subsanaron problemas de variables de entorno y de saltos de línea que rompían la ejecución en
contenedores Linux; se sacaron las credenciales del código y se anclaron todas las dependencias; se
levantó un clúster HDFS de cuatro nodos comprobando la réplica y la pérdida de dato sin ella; se
ejecutaron trabajos MapReduce demostrando con contadores la caída del tráfico de mezcla al introducir
un combinador; se orquestó un lago de datos por capas en MinIO con versionado e inmutabilidad; y se
convirtió la capa refinada a Parquet eligiendo el codec con una medición propia y no por defecto.

---

## 2. Estructura del repositorio

```
EAN-BiD-Grupo3/
├── README.md
├── docker-compose.yml               # clúster HDFS + YARN (S3 + S4)
├── docker-compose-jupyter.yml       # Jupyter + Postgres (S2)
├── docker-compose-minio.yml         # Lago de datos MinIO (S5)
├── hadoop.env                       # config del clúster, sin secretos
├── .env.example                     # plantilla de credenciales, sin valores
├── .gitattributes                   # normaliza saltos de línea entre Windows y Linux
├── .gitignore                       # bloquea credenciales, datos pesados y temporales
├── requirements.txt                 # dependencias ancladas, incluidas pyarrow y duckdb
├── genera_muestra.py                # generador de datos sintéticos
├── muestra/
│   ├── mapper.py                    # S4 nivel 1
│   ├── reducer.py                   # S4 nivel 1
│   ├── combiner.py                  # S4 nivel 2
│   ├── reducer2.py                  # S4 nivel 2
│   ├── mapper_t4.py                 # S4 nivel 3 (agregación sobre SECOP II)
│   └── reducer_t4.py                # S4 nivel 3 (agregación sobre SECOP II)
├── data/
│   └── raw/                         # datos crudos, bloqueados en .gitignore (ver Drive)
├── notebooks/
│   ├── 00_verificacion.ipynb        # S2 nivel 1
│   ├── 01_conexion_db.ipynb         # S2 nivel 2
│   └── s01_perfilamiento.ipynb      # S1 niveles 1 y 2
├── src/
│   ├── README.md
│   ├── lago.py                      # S5 · cubos, versionado y cliente de MinIO
│   └── s6_formatos.py               # S6 · comparación de codecs, DuckDB y carga a la refinada
├── docs/
│   ├── ficha_tecnica_T1.md
│   ├── guia_incorporacion.md
│   ├── T2_frontera_contenedor.md
│   ├── T3_proyeccion_almacenamiento.md
│   ├── T4_agregacion_mapreduce.md
│   ├── T5_convencion_lago.md
│   └── T6_formato_y_codec.md        # Nuevo · S6
└── resultados/
    ├── mediciones.csv
    ├── s1_nivel2_sensibilidad.md
    ├── s1_nivel3_matriz.md
    ├── s1_reto_negocio.md
    ├── s3_evidencia_fsck.md
    ├── s3_comparacion_factores.md
    ├── s3_reto_negocio.md
    ├── s4_contadores_mezcla.md
    ├── s4_evidencia_sin_combinador.md
    ├── s4_evidencia_con_combinador.md
    ├── s4_reto_negocio.md
    ├── s5_versionado.md
    ├── s5_reto_negocio.md
    ├── s6_tabla_codecs.md           # Nuevo · S6 (lo genera el script, no se edita a mano)
    ├── s6_evidencia_lago.md         # Nuevo · S6 (lo genera el script)
    ├── s6_reto_negocio.md           # Nuevo · S6
    └── evidencia/                   # salidas crudas de fsck y de los trabajos MapReduce
```

---

## 3. Cómo levantar los entornos

Primero, en cualquier caso:

```bash
git clone https://github.com/CristianPB14/EAN-BiD-Grupo3.git
cd EAN-BiD-Grupo3
cp .env.example .env
```

Complete en `.env` las cinco variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`,
`MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD`. Descargue además los datos crudos desde la carpeta de
Drive enlazada arriba y ubíquelos en `data/raw/`.

### 3.1 Jupyter + Postgres (sesión 2)

```bash
docker compose -f docker-compose-jupyter.yml up --build
```

Abra `http://localhost:8888` y ejecute los notebooks en orden numérico.

### 3.2 Clúster HDFS + YARN (sesiones 3 y 4)

```bash
python genera_muestra.py      # crea muestra/muestra.csv, necesaria para el clúster
docker compose up -d
```

Interfaces: `localhost:9870` (NameNode), `localhost:8088` (YARN), `localhost:8188` (historial de
trabajos). Al terminar: `docker compose down`.

### 3.3 Lago de datos MinIO (sesión 5)

*Baje primero el clúster de Hadoop para liberar el puerto 9000.*

```bash
docker compose -f docker-compose-minio.yml up -d
python src/lago.py
```

Interfaz: `localhost:9001` (consola web). El puerto 9000 es la API S3, a la que apunta `boto3`.

### 3.4 Conversión a Parquet y carga a la refinada (sesión 6)

No requiere contenedor de cómputo, solo MinIO arriba para el último paso.

```bash
python src/s6_formatos.py
```

Genera `resultados/s6_tabla_codecs.md` y `resultados/s6_evidencia_lago.md` con las mediciones de la
corrida, y deposita el Parquet particionado en el cubo `refinada`. **Ambos archivos se regeneran en
cada ejecución: no los edite a mano**, porque el objetivo es que las cifras no puedan
desincronizarse del código que las produce.

---

## 4. Equipo y flujo de trabajo

Grupo 3 · IFPN0025.

Antes de cada commit se verifica con `git status --short` que no aparezca ningún archivo `.env`,
ningún dato bajo `data/raw/` y ningún `.parquet`. Todas las dependencias se fijan con versión exacta
dentro de `requirements.txt`; no se instala nada con `pip install` suelto dentro de un notebook.

---

## 5. Material de referencia

- Kleppmann, M. (2017). *Designing data-intensive applications*. O'Reilly Media.
- Reis, J., y Housley, M. (2022). *Fundamentals of data engineering*. O'Reilly Media.
- Shvachko, K., Kuang, H., Radia, S., y Chansler, R. (2010). The Hadoop Distributed File System.
- Dean, J., y Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters.

---

*IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean · Facultad de Ingeniería · Ingeniería en Ciencia de Datos. Repositorio de trabajo del Grupo 3.*
