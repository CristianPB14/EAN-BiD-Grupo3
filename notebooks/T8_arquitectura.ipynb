# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

BLOCK_SIZE_MIB = 128
REPLICATION_FACTORS = [1, 2, 3]

print("Configuración del proyecto")
print(f"Tamaño de bloque HDFS: {BLOCK_SIZE_MIB} MiB")
print(f"Factores de réplica evaluados: {REPLICATION_FACTORS}")


# ==========================================
# 2. CARGAR EL DATASET
# ==========================================

import pandas as pd

RUTA_CSV = "data/raw/datos.csv"

df = pd.read_csv(RUTA_CSV)

print("Dataset cargado correctamente")
print(f"Filas: {df.shape[0]:,}")
print(f"Columnas: {df.shape[1]:,}")

df.head()


# ==========================================
# 3. CÁLCULO DE ALMACENAMIENTO Y RÉPLICA
# ==========================================

import math

# Tamaño original del dataset en bytes
tamano_bytes = df.memory_usage(deep=True).sum()

# Conversión a MiB
tamano_mib = tamano_bytes / (1024 ** 2)

resultados = []

for replica in REPLICATION_FACTORS:

    almacenamiento = tamano_mib * replica

    bloques = math.ceil(
        tamano_mib / BLOCK_SIZE_MIB
    )

    resultados.append({
        "Réplica": replica,
        "Tamaño base (MiB)": round(tamano_mib, 2),
        "Bloques HDFS": bloques,
        "Almacenamiento total (MiB)": round(almacenamiento, 2)
    })

tabla_replicacion = pd.DataFrame(resultados)

print(f"Tamaño calculado del dataset: {tamano_mib:.2f} MiB")

tabla_replicacion


# ==========================================
# 4. COMPARACIÓN CSV VS PARQUET
# ==========================================

import os
import time

# ------------------------------------------
# Lectura del CSV
# ------------------------------------------

inicio = time.perf_counter()

df = pd.read_csv(RUTA_CSV)

tiempo_lectura_csv = time.perf_counter() - inicio


# ------------------------------------------
# Escritura del archivo Parquet
# ------------------------------------------

RUTA_PARQUET = "data/raw/datos.parquet"

inicio = time.perf_counter()

df.to_parquet(
    RUTA_PARQUET,
    index=False
)

tiempo_escritura_parquet = time.perf_counter() - inicio


# ------------------------------------------
# Tamaños de los archivos
# ------------------------------------------

csv_size = os.path.getsize(RUTA_CSV)
parquet_size = os.path.getsize(RUTA_PARQUET)

csv_size_mb = csv_size / (1024 ** 2)
parquet_size_mb = parquet_size / (1024 ** 2)


# ------------------------------------------
# Porcentaje de reducción
# ------------------------------------------

reduccion = (
    (csv_size_mb - parquet_size_mb)
    / csv_size_mb
) * 100


# ------------------------------------------
# Tabla de comparación
# ------------------------------------------

comparacion = pd.DataFrame({
    "Formato": ["CSV", "Parquet"],
    "Tamaño_MB": [
        round(csv_size_mb, 2),
        round(parquet_size_mb, 2)
    ],
    "Tiempo_s": [
        round(tiempo_lectura_csv, 4),
        round(tiempo_escritura_parquet, 4)
    ]
})

print(f"Reducción de tamaño al usar Parquet: {reduccion:.2f}%")

comparacion


# ==========================================
# 5. RESUMEN DE RESULTADOS
# ==========================================

print("=" * 55)
print("RESUMEN PARA T8")
print("=" * 55)

print(f"Tamaño base del dataset : {tamano_mib:.2f} MiB")
print(f"Bloque HDFS             : {BLOCK_SIZE_MIB} MiB")
print(f"Factores evaluados      : {REPLICATION_FACTORS}")
print(f"Tamaño CSV              : {csv_size_mb:.2f} MB")
print(f"Tamaño Parquet          : {parquet_size_mb:.2f} MB")
print(f"Reducción con Parquet   : {reduccion:.2f}%")

print("=" * 55)
