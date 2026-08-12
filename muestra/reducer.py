#!/usr/bin/env python3
# Recibe pares ordenados por clave y promedia la presion de cada sector
import sys
sector_actual, suma, conteo = None, 0.0, 0
for linea in sys.stdin:
    sector, presion = linea.strip().split("\t")
    presion = float(presion)
    if sector != sector_actual and sector_actual is not None:
        print(f"{sector_actual}\t{suma/conteo:.3f}")
        suma, conteo = 0.0, 0
    sector_actual = sector
    suma += presion
    conteo += 1
if sector_actual is not None:
    print(f"{sector_actual}\t{suma/conteo:.3f}")