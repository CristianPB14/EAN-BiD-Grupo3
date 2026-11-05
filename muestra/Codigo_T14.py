# Sesión 14 - CDC por timestamp
# Equipo 3

from datetime import datetime, timedelta
import random

# -----------------------------
# Configuración
# -----------------------------
equipo = "equipo-3"
total_inicial = 90
altas = 9
modificaciones = 13
bajas_duras = 9

# -----------------------------
# Población inicial
# -----------------------------
suscriptores = {}

fecha_inicial = datetime(2026, 11, 1, 8, 0, 0)

for i in range(1, total_inicial + 1):
    suscriptores[i] = {
        "subscriber_id": i,
        "sector": random.choice(["Norte", "Sur", "Centro", "Occidente"]),
        "estrato": random.randint(1, 6),
        "created_at": fecha_inicial,
        "updated_at": fecha_inicial
    }

# -----------------------------
# Altas
# -----------------------------
ultimo_id = total_inicial

for _ in range(altas):
    ultimo_id += 1
    fecha = fecha_inicial + timedelta(minutes=random.randint(1, 1000))

    suscriptores[ultimo_id] = {
        "subscriber_id": ultimo_id,
        "sector": random.choice(["Norte", "Sur", "Centro", "Occidente"]),
        "estrato": random.randint(1, 6),
        "created_at": fecha,
        "updated_at": fecha
    }

# -----------------------------
# Modificaciones
# -----------------------------
ids_modificados = random.sample(list(suscriptores.keys()), modificaciones)

for subscriber_id in ids_modificados:
    fecha = fecha_inicial + timedelta(minutes=random.randint(1001, 2000))
    suscriptores[subscriber_id]["estrato"] = random.randint(1, 6)
    suscriptores[subscriber_id]["updated_at"] = fecha

# -----------------------------
# Bajas físicas
# -----------------------------
ids_baja = random.sample(list(suscriptores.keys()), bajas_duras)

for subscriber_id in ids_baja:
    del suscriptores[subscriber_id]

# -----------------------------
# CDC por timestamp
# -----------------------------
checkpoint = fecha_inicial

cambios_capturados = [
    registro
    for registro in suscriptores.values()
    if registro["updated_at"] > checkpoint
]

altas_capturadas = sum(
    1 for r in cambios_capturados
    if r["created_at"] == r["updated_at"]
)

modificaciones_capturadas = sum(
    1 for r in cambios_capturados
    if r["created_at"] < r["updated_at"]
)

bajas_capturadas = 0

# -----------------------------
# Resultados
# -----------------------------
print("=" * 50)
print("CDC POR TIMESTAMP -", equipo)
print("=" * 50)

print(f"Población inicial: {total_inicial}")
print(f"Altas generadas: {altas}")
print(f"Modificaciones generadas: {modificaciones}")
print(f"Bajas físicas generadas: {bajas_duras}")

print("\n--- Cambios capturados ---")
print(f"Altas capturadas: {altas_capturadas}")
print(f"Modificaciones capturadas: {modificaciones_capturadas}")
print(f"Bajas capturadas: {bajas_capturadas}")
print(f"Total capturado: {len(cambios_capturados)}")

print("\n--- Punto ciego ---")
print(f"Bajas no capturadas: {bajas_duras}")
print("Tasa de pérdida de bajas:",
      f"{bajas_duras / bajas_duras * 100:.2f}%")

print("\n--- Estado final ---")
print(f"Registros en origen: {len(suscriptores)}")
print(f"Registros esperados sin bajas: {total_inicial + altas}")

# -----------------------------
# Repetición del proceso
# -----------------------------
checkpoint = fecha_inicial

segunda_ejecucion = [
    r for r in suscriptores.values()
    if r["updated_at"] > checkpoint
]

duplicados = len(segunda_ejecucion)

print("\n--- Repetición del CDC ---")
print(f"Registros repetidos: {duplicados}")
print(
    "Duplicados esperados (altas + modificaciones):",
    altas + modificaciones
)

# -----------------------------
# Costos de polling
# -----------------------------
print("\n--- Costos de polling ---")

intervalos = [
    ("1 hora", 3600),
    ("5 segundos", 5)
]

for nombre, segundos in intervalos:
    consultas_dia = 86400 // segundos
    latencia_media = segundos / 2
    latencia_maxima = segundos

    print(f"\nIntervalo: {nombre}")
    print(f"Consultas/día: {consultas_dia}")
    print(f"Latencia media: {latencia_media} segundos")
    print(f"Latencia máxima: {latencia_maxima} segundos")

print("\nFactor de aumento de consultas:")
print(17280 / 24, "veces")

# -----------------------------
# Reconciliación
# -----------------------------
M = 90000
B = 2

keys_dia = M * B
latencia_maxima_reconciliacion = 86400 / B

print("\n--- Reconciliación ---")
print(f"Filas: {M}")
print(f"Barridos diarios: {B}")
print(f"Claves procesadas/día: {keys_dia}")
print(
    "Latencia máxima:",
    latencia_maxima_reconciliacion / 3600,
    "horas"
)

# -----------------------------
# Decisión
# -----------------------------
print("\n--- Decisión ADR ---")
print("Migrar a CDC basado en WAL / Logical Decoding.")
print("Mantener reconciliación periódica como control adicional.")
print("El timestamp CDC no detecta hard deletes.")
