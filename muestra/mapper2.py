#!/usr/bin/env python3
# mapper2.py - emite el par (suma, conteo) desde el inicio
import sys
for linea in sys.stdin:
    campos = linea.strip().split(",")
    if len(campos) < 4 or campos[0] == "sensor_id":
        continue
    sector, presion = campos[0], campos[3]
    try:
        float(presion)
    except ValueError:
        continue
    print(f"{sector}\t{presion},1")