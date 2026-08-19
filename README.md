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

## 1. Estado del avance (S1 → S5)

Leyenda: ✅ completo · 🟡 plantilla lista, falta completar con cifras propias o correr en el clúster · ❌ pendiente

| Sesión | Nivel 1 | Nivel 2 | Nivel 3 | Reto de negocio | Tarea acumulativa |
|---|---|---|---|---|---|
| **S1** | ✅ `notebooks/s01_perfilamiento.ipynb` mide k y perfila SECOP II, IDEAM y GEIH | ✅ Cálculo corregido y dinámico; reflexión en `resultados/s1_nivel2_sensibilidad.md` completada | ✅ `resultados/s1_nivel3_matriz.md`, matriz completada | ✅ `resultados/s1_reto_negocio.md`, declaración de uso de IA completada | ✅ `docs/ficha_tecnica_T1.md`, fuente única elegida (IDEAM) y ficha completada |
| **S2** | ✅ `notebooks/00_verificacion.ipynb` sin discrepancias | ✅ Postgres alcanzable y credenciales corregidas | ✅ `docs/T2_frontera_contenedor.md`, completada con prueba en clon limpio | ✅ `docs/guia_incorporacion.md` completada | ✅ README actualizado y prueba de clon limpio realizada |
| **S3** | ✅ Clúster arranca en clon limpio; fsck evidenciado en `resultados/s3_evidencia_fsck.md` | ✅ `resultados/s3_comparacion_factores.md` completada con mediciones del clúster | ✅ `docs/T3_proyeccion_almacenamiento.md` completada, decisión de factor/bloque documentada | ✅ `resultados/s3_reto_negocio.md` completado | ✅ Documento de T3 completado |
| **S4** | ✅ `muestra/mapper.py`, `muestra/reducer.py`; YARN configurado y funcional | ✅ Combinador ejecutado y contadores documentados en `resultados/s4_contadores_mezcla.md` | ✅ `docs/T4_agregacion_mapreduce.md`, agregación propia sobre SECOP II documentada y ejecutada | ✅ `resultados/s4_reto_negocio.md` completado | ✅ T4 completada y documentada |
| **S5** | ✅ Contenedor MinIO levantado y cubos creados | ✅ Inmutabilidad y versionado evidenciados en `resultados/s5_versionado.md` | ✅ `docs/T5_convencion_lago.md` con mapa de capas y rutas particionadas completado | ✅ `resultados/s5_reto_negocio.md` completado | ✅ T5 completada, README actualizado |

**Lo que se ha corregido y logrado durante la ejecución del proyecto:**
Se subsanaron problemas de variables de entorno y formato de salto de línea que rompían la ejecución en entornos Linux, se configuró exitosamente la conexión segura a la base de datos, se ejecutaron MapReduce jobs sobre un clúster de Hadoop comprobando reducción masiva de tráfico de red al implementar un combinador, y finalmente se orquestó la estructura de un Lago de Datos con MinIO implementando versionado e inmutabilidad.

---

## 2. Estructura del repositorio

```
EAN-BiD-Grupo3/
├── README.md
├── docker-compose.yml               # clúster HDFS + YARN (S3 + S4)
├── docker-compose-jupyter.yml       # Jupyter + Postgres (S2)
├── docker-compose-minio.yml         # Lago de datos MinIO (S5)
├── hadoop.env                       # config del clúster, sin secretos
├── .env.example                     # plantilla de credenciales
├── requirements.txt
├── .gitignore                       # bloquea credenciales, datos pesados y temporales
├── genera_muestra.py                # Generador de datos sintéticos
├── muestra/
│   ├── mapper.py                    # S4 nivel 1
│   ├── reducer.py                   # S4 nivel 1
│   ├── combiner.py                  # S4 nivel 2
│   ├── reducer2.py                  # S4 nivel 2
│   ├── mapper_t4.py                 # S4 nivel 3 (agregación sobre SECOP II)
│   └── reducer_t4.py                # S4 nivel 3 (agregación sobre SECOP II)
├── data/
│   └── raw/                         # datos crudos (bloqueados en .gitignore)
├── notebooks/
│   ├── 00_verificacion.ipynb        # S2 nivel 1
│   ├── 01_conexion_db.ipynb         # S2 nivel 2
│   └── s01_perfilamiento.ipynb      # S1 niveles 1 y 2
├── src/
│   ├── README.md                    
│   └── lago.py                      # Script S5 (creación de cubos y versionado en MinIO)
├── docs/
│   ├── ficha_tecnica_T1.md          
│   ├── guia_incorporacion.md        
│   ├── T2_frontera_contenedor.md    
│   ├── T3_proyeccion_almacenamiento.md  
│   ├── T4_agregacion_mapreduce.md   
│   └── T5_convencion_lago.md        # Nuevo - S5
└── resultados/
    ├── s1_nivel2_sensibilidad.md    
    ├── s1_nivel3_matriz.md          
    ├── s1_reto_negocio.md           
    ├── s3_evidencia_fsck.md         
    ├── s3_comparacion_factores.md   
    ├── s3_reto_negocio.md           
    ├── s4_contadores_mezcla.md      
    ├── s4_reto_negocio.md           
    ├── s5_versionado.md             # Nuevo - S5
    ├── s5_reto_negocio.md           # Nuevo - S5
    └── mediciones.csv
```

---

## 3. Cómo levantar los entornos

### 3.1 Jupyter + Postgres (sesión 2)

```bash
git clone [https://github.com/CristianPB14/EAN-BiD-Grupo3.git](https://github.com/CristianPB14/EAN-BiD-Grupo3.git)
cd EAN-BiD-Grupo3
cp .env.example .env        # complete POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB y MINIO credenciales
docker compose -f docker-compose-jupyter.yml up --build
```

Abra `http://localhost:8888` y ejecute los notebooks en orden numérico.

### 3.2 Clúster HDFS + YARN (sesiones 3 y 4)

```bash
docker compose up -d
```

Interfaces: `localhost:9870` (NameNode), `localhost:8088` (YARN), `localhost:8188` (historial de trabajos).
Al terminar: `docker compose down`

### 3.3 Lago de Datos Local - MinIO (sesión 5)

*Asegúrese de bajar el clúster de Hadoop primero para liberar el puerto 9000.*

```bash
docker compose -f docker-compose-minio.yml up -d
```

Interfaces: `localhost:9001` (Consola Web de MinIO). Para interactuar, ejecute `python src/lago.py`.

---

## 4. Equipo y flujo de trabajo

Grupo 3 · IFPN0025.
El flujo de trabajo adoptado exige confirmar el estado de las credenciales y los datos excluidos antes de cada commit usando `git status --short`. Todas las dependencias deben fijarse estrictamente dentro del archivo `requirements.txt`.

---

## 5. Material de referencia

- Kleppmann, M. (2017). *Designing data-intensive applications*. O'Reilly Media.
- Reis, J., y Housley, M. (2022). *Fundamentals of data engineering*. O'Reilly Media.
- Shvachko, K., Kuang, H., Radia, S., y Chansler, R. (2010). The Hadoop Distributed File System.
- Dean, J., y Ghemawat, S. (2008). MapReduce: Simplified data processing on large clusters.

---

*IFPN0025 · Big Data e Ingeniería de Datos · Universidad Ean · Facultad de Ingeniería · Ingeniería en Ciencia de Datos. Repositorio de trabajo del Grupo 3.*