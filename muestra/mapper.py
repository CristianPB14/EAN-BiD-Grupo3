#!/usr/bin/env python3
# Lee cada linea y emite: sector <tab> presion
import sys
for linea in sys.stdin:
    campos = linea.strip().split(",")
    if len(campos) < 4 or campos[0] == "sensor_id":
        continue                      # salta encabezado y lineas incompletas
    sector, presion = campos[0], campos[3]
    try:
        float(presion)
    except ValueError:
        continue
    print(f"{sector}\t{presion}")     # el sector es la clave