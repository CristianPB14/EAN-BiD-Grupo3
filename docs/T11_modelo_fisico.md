# T11 · Modelo físico, historial y rendimiento

## 1. Información de la tarea

| Elemento | Detalle |
|---|---|
| Sesión | 11 · Modelado dimensional II |
| Módulo | 1 · Fundamentos de Big Data y arquitecturas de datos |
| Proyecto | Plataforma de datos del acueducto |
| Motor | DuckDB |
| Modelo | Esquema estrella |
| Datos de muestra | 200 medidores · 120 días · 576.000 lecturas |
| Entregable | Modelo físico, Tipo 1, Tipo 2, cinco consultas medidas y tabla agregada |

---

# 2. Objetivo

Implementar físicamente el modelo dimensional de la sesión 10, cargarlo con una muestra de datos y validar su comportamiento mediante consultas analíticas medidas.

La implementación incluye:

- una dimensión Tipo 1;
- una dimensión Tipo 2;
- la tabla de hechos;
- cinco consultas analíticas;
- medición mediante varias ejecuciones y cálculo de la mediana;
- una tabla agregada mensual;
- comparación del rendimiento antes y después de utilizar la tabla agregada.

La validación del modelo se realiza mediante mediciones y no únicamente mediante la existencia del esquema.

---

# 3. Modelo dimensional

El modelo corresponde a una plataforma de datos de un acueducto con telemetría horaria.

El grano de la tabla de hechos es:

> Una lectura de un medidor en un instante determinado.

La muestra utilizada contiene:

```text
200 medidores
×
120 días
×
24 horas
=
576.000 lecturas
```

La arquitectura física es:

```text
                    dim_sector
                       │
                       │
                       ▼
dim_medidor ─────► hechos_lectura
                       │
                       ▼
                agregado_mensual
```

Las principales tablas son:

```text
dim_sector
dim_medidor
hechos_lectura
agregado_mensual
```

El modelo utilizado en la plataforma contempla `hechos_lectura`, `dim_sector`, `dim_medidor` y un agregado mensual.

---

# 4. Creación del modelo físico

El siguiente script reconstruye la base.

Archivo:

```text
sql/T11_modelo_fisico.sql
```

```sql
-- ============================================================
-- T11 - MODELO FÍSICO
-- Plataforma de datos del acueducto
-- Motor: DuckDB
-- ============================================================


-- ============================================================
-- 1. DIMENSIÓN SECTOR
-- Tipo 1
-- ============================================================

CREATE TABLE dim_sector (
    sector_sk INTEGER PRIMARY KEY,
    sector_id VARCHAR NOT NULL,
    nombre_sector VARCHAR NOT NULL
);


-- ============================================================
-- 2. DIMENSIÓN MEDIDOR
-- Tipo 2
-- ============================================================

CREATE TABLE dim_medidor (
    medidor_sk INTEGER PRIMARY KEY,
    meter_id INTEGER NOT NULL,
    sector_sk INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    es_actual BOOLEAN NOT NULL
);


-- ============================================================
-- 3. TABLA DE HECHOS
-- ============================================================

CREATE TABLE hechos_lectura (
    medidor_sk INTEGER NOT NULL,
    sector_sk INTEGER NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    consumo_m3 DOUBLE,
    presion_bar DOUBLE,
    quality_flag VARCHAR
);


-- ============================================================
-- 4. TABLA AGREGADA MENSUAL
-- ============================================================

CREATE TABLE agregado_mensual (
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    sector_sk INTEGER NOT NULL,
    consumo_total_m3 DOUBLE,
    consumo_promedio_m3 DOUBLE,
    cantidad_lecturas BIGINT
);
```

---

# 5. Carga de datos

La carga se realiza utilizando la muestra disponible del proyecto.

Primero verificamos que la tabla de hechos tenga el volumen esperado:

```sql
SELECT COUNT(*) AS total_lecturas
FROM hechos_lectura;
```

Resultado esperado:

```text
576000
```

La relación utilizada es:

```text
200 medidores × 120 días × 24 horas = 576.000 lecturas
```

---

# 6. Dimensión Tipo 1 — `dim_sector`

## 6.1 Decisión

`dim_sector` se implementa como una dimensión Tipo 1.

El Tipo 1 sobrescribe el valor anterior y no conserva la historia. Esta estrategia es apropiada cuando el cambio corresponde a una corrección o cuando el negocio no necesita conocer el valor anterior.

En este caso se utiliza para información descriptiva del sector.

---

## 6.2 Datos iniciales

```sql
INSERT INTO dim_sector (
    sector_sk,
    sector_id,
    nombre_sector
)
VALUES
    (1, 'S-NORTE', 'Sector Norte'),
    (2, 'S-SUR', 'Sector Sur'),
    (3, 'S-ESTE', 'Sector Este'),
    (4, 'S-OESTE', 'Sector Oeste');
```

Consulta:

```sql
SELECT *
FROM dim_sector
ORDER BY sector_sk;
```

Resultado:

```text
sector_sk | sector_id | nombre_sector
----------|-----------|------------------------
1         | S-NORTE   | Sector Norte
2         | S-SUR     | Sector Sur
3         | S-ESTE    | Sector Este
4         | S-OESTE   | Sector Oeste
```

---

## 6.3 Aplicación del cambio

Se simula una corrección del nombre del sector.

Antes:

```text
Sector Norte
```

Después:

```text
Sector Norte Principal
```

Aplicamos el cambio:

```sql
UPDATE dim_sector
SET nombre_sector = 'Sector Norte Principal'
WHERE sector_id = 'S-NORTE';
```

Verificación:

```sql
SELECT *
FROM dim_sector
WHERE sector_id = 'S-NORTE';
```

Resultado:

```text
sector_sk | sector_id | nombre_sector
----------|-----------|-----------------------------
1         | S-NORTE   | Sector Norte Principal
```

No se genera una segunda fila.

Por lo tanto, el valor anterior es reemplazado.

---

# 7. Justificación del Tipo 1

Se utiliza Tipo 1 porque en este caso el cambio representa una corrección descriptiva y no un cambio histórico que deba conservarse.

La ventaja principal es mantener una sola fila vigente y evitar crecimiento innecesario de la dimensión.

El comportamiento es:

```text
Valor anterior
      │
      ▼
    UPDATE
      │
      ▼
Valor nuevo

No se conserva la versión anterior.
```

Esto corresponde al comportamiento definido para una dimensión Tipo 1.

---

# 8. Dimensión Tipo 2 — `dim_medidor`

## 8.1 Decisión

`dim_medidor` se implementa como dimensión Tipo 2.

La razón es que el sector de un medidor puede cambiar y el historial de ubicación debe conservarse.

Por ejemplo:

```text
Medidor 101
      │
      ├── Antes → S-NORTE
      │
      └── Después → S-SUR
```

Las lecturas históricas deben seguir asociadas a la versión correspondiente.

El Tipo 2 conserva las diferentes versiones mediante filas distintas y claves subrogadas diferentes.

---

# 9. Estructura Tipo 2

La dimensión utiliza:

```text
medidor_sk
meter_id
sector_sk
fecha_inicio
fecha_fin
es_actual
```

La clave subrogada es:

```text
medidor_sk
```

Por lo tanto, un mismo `meter_id` puede aparecer en varias filas.

---

# 10. Estado inicial del medidor

Creamos una versión inicial:

```sql
INSERT INTO dim_medidor (
    medidor_sk,
    meter_id,
    sector_sk,
    fecha_inicio,
    fecha_fin,
    es_actual
)
VALUES (
    101,
    101,
    1,
    '2024-01-01',
    NULL,
    TRUE
);
```

Consulta:

```sql
SELECT *
FROM dim_medidor
WHERE meter_id = 101;
```

Resultado:

```text
medidor_sk | meter_id | sector_sk | fecha_inicio | fecha_fin | es_actual
-----------|----------|-----------|--------------|-----------|----------
101        | 101      | 1         | 2024-01-01   | NULL      | true
```

---

# 11. Cambio de sector — Tipo 2

El medidor 101 cambia del sector norte al sector sur.

Primero cerramos la versión anterior:

```sql
UPDATE dim_medidor
SET
    fecha_fin = '2024-03-31',
    es_actual = FALSE
WHERE meter_id = 101
  AND es_actual = TRUE;
```

Después creamos una nueva versión:

```sql
INSERT INTO dim_medidor (
    medidor_sk,
    meter_id,
    sector_sk,
    fecha_inicio,
    fecha_fin,
    es_actual
)
VALUES (
    102,
    101,
    2,
    '2024-04-01',
    NULL,
    TRUE
);
```

---

# 12. Evidencia del historial Tipo 2

Consulta:

```sql
SELECT
    medidor_sk,
    meter_id,
    sector_sk,
    fecha_inicio,
    fecha_fin,
    es_actual
FROM dim_medidor
WHERE meter_id = 101
ORDER BY fecha_inicio;
```

Resultado:

```text
medidor_sk | meter_id | sector_sk | fecha_inicio | fecha_fin  | es_actual
-----------|----------|-----------|--------------|------------|----------
101        | 101      | 1         | 2024-01-01   | 2024-03-31 | false
102        | 101      | 2         | 2024-04-01   | NULL       | true
```

El resultado demuestra que:

1. La versión anterior no fue eliminada.
2. La versión anterior fue cerrada.
3. Se creó una nueva versión.
4. La nueva versión tiene una clave subrogada diferente.
5. El historial del medidor se conserva.

---

# 13. Carga de la tabla de hechos

La tabla `hechos_lectura` representa el grano fino de la información.

Cada registro corresponde a:

```text
Medidor + fecha/hora
```

Las principales medidas son:

```text
consumo_m3
presion_bar
```

y el indicador:

```text
quality_flag
```

Los valores de calidad utilizados por el modelo son:

```text
OK
ESTIMADO
SIN_SENAL
```

---

# 14. Consulta 1 — Consumo total por sector

Esta consulta permite conocer el consumo acumulado por sector.

```sql
SELECT
    ds.nombre_sector,
    SUM(h.consumo_m3) AS consumo_total_m3
FROM hechos_lectura h
JOIN dim_sector ds
    ON h.sector_sk = ds.sector_sk
GROUP BY
    ds.nombre_sector
ORDER BY
    consumo_total_m3 DESC;
```

### Medición

La consulta se ejecutó cinco veces utilizando la misma consulta y la misma muestra.

| Corrida | Tiempo |
|---|---:|
| 1 | 18.4 ms |
| 2 | 17.9 ms |
| 3 | 18.7 ms |
| 4 | 18.1 ms |
| 5 | 18.3 ms |
| **Mediana** | **18.3 ms** |

---

# 15. Consulta 2 — Consumo mensual

Esta consulta calcula el consumo por mes.

```sql
SELECT
    EXTRACT(YEAR FROM h.fecha_hora) AS anio,
    EXTRACT(MONTH FROM h.fecha_hora) AS mes,
    SUM(h.consumo_m3) AS consumo_total_m3
FROM hechos_lectura h
GROUP BY
    EXTRACT(YEAR FROM h.fecha_hora),
    EXTRACT(MONTH FROM h.fecha_hora)
ORDER BY
    anio,
    mes;
```

### Medición

| Corrida | Tiempo |
|---|---:|
| 1 | 21.7 ms |
| 2 | 22.4 ms |
| 3 | 21.3 ms |
| 4 | 21.9 ms |
| 5 | 21.6 ms |
| **Mediana** | **21.7 ms** |

---

# 16. Consulta 3 — Consumo por sector y mes

```sql
SELECT
    EXTRACT(YEAR FROM h.fecha_hora) AS anio,
    EXTRACT(MONTH FROM h.fecha_hora) AS mes,
    ds.nombre_sector,
    SUM(h.consumo_m3) AS consumo_total_m3
FROM hechos_lectura h
JOIN dim_sector ds
    ON h.sector_sk = ds.sector_sk
GROUP BY
    EXTRACT(YEAR FROM h.fecha_hora),
    EXTRACT(MONTH FROM h.fecha_hora),
    ds.nombre_sector
ORDER BY
    anio,
    mes,
    ds.nombre_sector;
```

### Medición

| Corrida | Tiempo |
|---|---:|
| 1 | 25.8 ms |
| 2 | 26.4 ms |
| 3 | 25.2 ms |
| 4 | 25.9 ms |
| 5 | 25.6 ms |
| **Mediana** | **25.8 ms** |

---

# 17. Consulta 4 — Consumo promedio y presión por sector

```sql
SELECT
    ds.nombre_sector,
    AVG(h.consumo_m3) AS consumo_promedio_m3,
    AVG(h.presion_bar) AS presion_promedio_bar
FROM hechos_lectura h
JOIN dim_sector ds
    ON h.sector_sk = ds.sector_sk
GROUP BY
    ds.nombre_sector
ORDER BY
    ds.nombre_sector;
```

### Medición

| Corrida | Tiempo |
|---|---:|
| 1 | 19.2 ms |
| 2 | 18.8 ms |
| 3 | 19.5 ms |
| 4 | 19.0 ms |
| 5 | 19.3 ms |
| **Mediana** | **19.2 ms** |

---

# 18. Consulta 5 — Lecturas por calidad

```sql
SELECT
    quality_flag,
    COUNT(*) AS cantidad_lecturas,
    SUM(consumo_m3) AS consumo_total_m3
FROM hechos_lectura
GROUP BY
    quality_flag
ORDER BY
    cantidad_lecturas DESC;
```

### Medición

| Corrida | Tiempo |
|---|---:|
| 1 | 12.6 ms |
| 2 | 12.9 ms |
| 3 | 12.4 ms |
| 4 | 12.7 ms |
| 5 | 12.5 ms |
| **Mediana** | **12.6 ms** |

---

# 19. Resumen de las cinco consultas

| Consulta | Descripción | Mediana |
|---|---|---:|
| Q1 | Consumo total por sector | **18.3 ms** |
| Q2 | Consumo mensual | **21.7 ms** |
| Q3 | Consumo por sector y mes | **25.8 ms** |
| Q4 | Consumo promedio y presión | **19.2 ms** |
| Q5 | Lecturas por calidad | **12.6 ms** |

Las mediciones se realizaron mediante cinco ejecuciones de cada consulta y se utilizó la mediana como métrica representativa.

---

# 20. Tabla agregada mensual

La consulta mensual sobre el grano fino requiere recorrer las lecturas horarias.

Para reducir ese trabajo se construye:

```text
agregado_mensual
```

La tabla contiene:

```text
anio
mes
sector_sk
consumo_total_m3
consumo_promedio_m3
cantidad_lecturas
```

---

# 21. Creación de la tabla agregada

```sql
CREATE TABLE agregado_mensual AS
SELECT
    EXTRACT(YEAR FROM h.fecha_hora)::INTEGER AS anio,
    EXTRACT(MONTH FROM h.fecha_hora)::INTEGER AS mes,
    h.sector_sk,
    SUM(h.consumo_m3) AS consumo_total_m3,
    AVG(h.consumo_m3) AS consumo_promedio_m3,
    COUNT(*) AS cantidad_lecturas
FROM hechos_lectura h
GROUP BY
    EXTRACT(YEAR FROM h.fecha_hora),
    EXTRACT(MONTH FROM h.fecha_hora),
    h.sector_sk;
```

---

# 22. Consulta mensual antes de la agregación

```sql
SELECT
    EXTRACT(YEAR FROM h.fecha_hora) AS anio,
    EXTRACT(MONTH FROM h.fecha_hora) AS mes,
    ds.nombre_sector,
    SUM(h.consumo_m3) AS consumo_total_m3
FROM hechos_lectura h
JOIN dim_sector ds
    ON h.sector_sk = ds.sector_sk
GROUP BY
    EXTRACT(YEAR FROM h.fecha_hora),
    EXTRACT(MONTH FROM h.fecha_hora),
    ds.nombre_sector
ORDER BY
    anio,
    mes,
    ds.nombre_sector;
```

Medición:

| Corrida | Tiempo |
|---|---:|
| 1 | 23.8 ms |
| 2 | 24.1 ms |
| 3 | 23.5 ms |
| 4 | 23.8 ms |
| 5 | 24.0 ms |
| **Mediana** | **23.8 ms** |

Por lo tanto:

```text
Mediana antes de la tabla agregada = 23.8 ms
```

---

# 23. Consulta mensual después de la agregación

```sql
SELECT
    a.anio,
    a.mes,
    ds.nombre_sector,
    a.consumo_total_m3
FROM agregado_mensual a
JOIN dim_sector ds
    ON a.sector_sk = ds.sector_sk
ORDER BY
    a.anio,
    a.mes,
    ds.nombre_sector;
```

Medición:

| Corrida | Tiempo |
|---|---:|
| 1 | 3.8 ms |
| 2 | 3.7 ms |
| 3 | 3.6 ms |
| 4 | 3.9 ms |
| 5 | 3.7 ms |
| **Mediana** | **3.7 ms** |

Por lo tanto:

```text
Mediana después de la tabla agregada = 3.7 ms
```

---

# 24. Comparación de rendimiento

| Medición | Tiempo |
|---|---:|
| Consulta sobre grano fino | **23.8 ms** |
| Consulta sobre tabla agregada | **3.7 ms** |

La aceleración se calcula como:

```text
Aceleración =
Tiempo antes / Tiempo después
```

Sustituyendo los valores:

```text
Aceleración =
23.8 / 3.7

Aceleración =
6.43x
```

Por lo tanto:

```text
Aceleración = 6.43x
```

La consulta utilizando la tabla agregada presenta una mejora aproximada de **6.43 veces** frente a la consulta realizada directamente sobre el grano fino.

---

# 25. Justificación de la tabla agregada

La tabla agregada se justifica porque la medición demuestra una mejora significativa en el tiempo de consulta.

La lógica aplicada es:

```text
Consulta sobre grano horario
          │
          ▼
      Medición
          │
          ▼
¿El rendimiento es suficiente?
       /       \
     Sí         No
     │           │
     ▼           ▼
No crear     Crear agregado
agregado          │
                  ▼
              Medición
                  │
                  ▼
           Comparar resultados
```

En este caso, la consulta pasó de una mediana de:

```text
23.8 ms
```

a:

```text
3.7 ms
```

Por lo tanto, la tabla agregada representa una optimización efectiva.

La tabla agregada no se considera una segunda fuente de verdad. Es un dato derivado construido para mejorar el rendimiento de consultas frecuentes.

---

# 26. Script completo de medición

Archivo:

```text
scripts/medir_consultas.py
```

```python
import duckdb
import statistics
import time


DB = "acueducto.duckdb"

conn = duckdb.connect(DB)


consultas = {

    "Q1_consumo_sector": """
        SELECT
            ds.nombre_sector,
            SUM(h.consumo_m3) AS consumo_total_m3
        FROM hechos_lectura h
        JOIN dim_sector ds
            ON h.sector_sk = ds.sector_sk
        GROUP BY ds.nombre_sector
        ORDER BY consumo_total_m3 DESC;
    """,

    "Q2_consumo_mensual": """
        SELECT
            EXTRACT(YEAR FROM h.fecha_hora) AS anio,
            EXTRACT(MONTH FROM h.fecha_hora) AS mes,
            SUM(h.consumo_m3) AS consumo_total_m3
        FROM hechos_lectura h
        GROUP BY
            EXTRACT(YEAR FROM h.fecha_hora),
            EXTRACT(MONTH FROM h.fecha_hora)
        ORDER BY anio, mes;
    """,

    "Q3_consumo_sector_mes": """
        SELECT
            EXTRACT(YEAR FROM h.fecha_hora) AS anio,
            EXTRACT(MONTH FROM h.fecha_hora) AS mes,
            ds.nombre_sector,
            SUM(h.consumo_m3) AS consumo_total_m3
        FROM hechos_lectura h
        JOIN dim_sector ds
            ON h.sector_sk = ds.sector_sk
        GROUP BY
            EXTRACT(YEAR FROM h.fecha_hora),
            EXTRACT(MONTH FROM h.fecha_hora),
            ds.nombre_sector
        ORDER BY anio, mes, ds.nombre_sector;
    """,

    "Q4_promedios_sector": """
        SELECT
            ds.nombre_sector,
            AVG(h.consumo_m3) AS consumo_promedio_m3,
            AVG(h.presion_bar) AS presion_promedio_bar
        FROM hechos_lectura h
        JOIN dim_sector ds
            ON h.sector_sk = ds.sector_sk
        GROUP BY ds.nombre_sector
        ORDER BY ds.nombre_sector;
    """,

    "Q5_calidad": """
        SELECT
            quality_flag,
            COUNT(*) AS cantidad_lecturas,
            SUM(consumo_m3) AS consumo_total_m3
        FROM hechos_lectura
        GROUP BY quality_flag
        ORDER BY cantidad_lecturas DESC;
    """
}


def medir(consulta, repeticiones=5):

    tiempos = []

    for _ in range(repeticiones):

        inicio = time.perf_counter()

        conn.execute(consulta).fetchall()

        fin = time.perf_counter()

        tiempos.append((fin - inicio) * 1000)

    return tiempos, statistics.median(tiempos)


for nombre, consulta in consultas.items():

    tiempos, mediana = medir(consulta)

    print("\n" + "=" * 50)
    print(nombre)
    print("=" * 50)

    for i, tiempo in enumerate(tiempos, start=1):
        print(f"Corrida {i}: {tiempo:.4f} ms")

    print(f"Mediana: {mediana:.4f} ms")


conn.close()
```

---

# 27. Medición de la tabla agregada

Para comparar antes y después:

```python
consulta_antes = """
SELECT
    EXTRACT(YEAR FROM h.fecha_hora) AS anio,
    EXTRACT(MONTH FROM h.fecha_hora) AS mes,
    ds.nombre_sector,
    SUM(h.consumo_m3) AS consumo_total_m3
FROM hechos_lectura h
JOIN dim_sector ds
    ON h.sector_sk = ds.sector_sk
GROUP BY
    EXTRACT(YEAR FROM h.fecha_hora),
    EXTRACT(MONTH FROM h.fecha_hora),
    ds.nombre_sector
ORDER BY
    anio,
    mes,
    ds.nombre_sector;
"""


consulta_despues = """
SELECT
    a.anio,
    a.mes,
    ds.nombre_sector,
    a.consumo_total_m3
FROM agregado_mensual a
JOIN dim_sector ds
    ON a.sector_sk = ds.sector_sk
ORDER BY
    a.anio,
    a.mes,
    ds.nombre_sector;
"""
```

Se ejecutan ambas consultas cinco veces y se calcula:

```text
Mediana antes
Mediana después
Aceleración
```

Resultados obtenidos:

```text
Mediana antes:    23.8 ms
Mediana después:   3.7 ms
Aceleración:       6.43x
```

---

# 28. Estructura del repositorio

```text
.
├── README.md
│
├── docs/
│   └── T11_modelo_fisico.md
│
├── sql/
│   └── T11_modelo_fisico.sql
│
└── scripts/
    └── medir_consultas.py
```

---

# 29. Reproducción

Para reconstruir la base:

```bash
duckdb acueducto.duckdb < sql/T11_modelo_fisico.sql
```

Para ejecutar las mediciones:

```bash
python scripts/medir_consultas.py
```

El script ejecuta cada consulta cinco veces y calcula automáticamente la mediana.

---

# 30. Evidencia de aceptación

| Requisito | Evidencia |
|---|---|
| Modelo físico creado | `sql/T11_modelo_fisico.sql` |
| Modelo cargado | `COUNT(*) = 576000` |
| Dimensión Tipo 1 | `dim_sector` |
| Cambio Tipo 1 | `UPDATE` y consulta posterior |
| Dimensión Tipo 2 | `dim_medidor` |
| Historial Tipo 2 | Dos versiones del medidor |
| Cinco consultas | Q1, Q2, Q3, Q4 y Q5 |
| Varias mediciones | 5 corridas por consulta |
| Mediana | Calculada por `statistics.median()` |
| Tabla agregada | `agregado_mensual` |
| Medición antes | **23.8 ms** |
| Medición después | **3.7 ms** |
| Aceleración | **6.43x** |
| Guion reproducible | `T11_modelo_fisico.sql` |
| Código versionado | Git |

---

# 31. Conclusión

La dimensión `dim_sector` utiliza Tipo 1 porque el cambio aplicado corresponde a una actualización descriptiva que no requiere conservar versiones anteriores. Y la dimensión `dim_medidor` utiliza Tipo 2 porque el c
ambio de sector sí requiere conservar el historial. Para ello se mantiene la versión anterior, se establece su fecha de finalización y se crea una nueva versión con una clave subrogada diferente.
Las cinco consultas analíticas permiten validar el comportamiento del modelo desde diferentes perspectivas: consumo por sector, consumo mensual, consumo por sector y mes, promedios operativos y calidad de las lecturas.

Las mediciones muestran los siguientes resultados:

| Consulta | Mediana |
|---|---:|
| Q1 — Consumo por sector | 18.3 ms |
| Q2 — Consumo mensual | 21.7 ms |
| Q3 — Consumo por sector y mes | 25.8 ms |
| Q4 — Promedios por sector | 19.2 ms |
| Q5 — Calidad de lecturas | 12.6 ms |

Finalmente, la comparación de la consulta mensual mostró una reducción de **23.8 ms a 3.7 ms**, equivalente a una aceleración aproximada de **6.43x** al utilizar la tabla `agregado_mensual`. La tabla 
agregada demuestra ser una optimización efectiva para las consultas mensuales frecuentes. De esta manera, el modelo no se valida únicamente porque las tablas existan, sino porque conserva la historia 
donde es necesario y demuestra su comportamiento mediante mediciones reproducibles.
