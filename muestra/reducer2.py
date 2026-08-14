#!/usr/bin/env python3
# reducer2.py · reductor adaptado para trabajar con o sin combiner.py (S4, nivel 2).
#
# Recibe pares "sector <tab> valor" donde valor puede venir como "presion"
# cruda (si combiner.py no corrió) o como "suma,conteo" (si sí corrió).
# Igual que combiner.py, acepta ambos formatos. El promedio se calcula una
# sola vez, al final, dividiendo la suma total entre el conteo total.
#
# El resultado numérico de este reductor debe ser idéntico, sector por
# sector, al de reducer.py (nivel 1). Lo que cambia es cuánto viaja por la
# mezcla, no el resultado.
import sys

sector_actual, suma, conteo = None, 0.0, 0

for linea in sys.stdin:
    sector, valor = linea.strip().split("\t")

    if "," in valor:
        parcial_suma_str, parcial_conteo_str = valor.split(",")
        parcial_suma, parcial_conteo = float(parcial_suma_str), int(parcial_conteo_str)
    else:
        parcial_suma, parcial_conteo = float(valor), 1

    if sector != sector_actual and sector_actual is not None:
        print(f"{sector_actual}\t{suma/conteo:.3f}")
        suma, conteo = 0.0, 0

    sector_actual = sector
    suma += parcial_suma
    conteo += parcial_conteo

if sector_actual is not None:
    print(f"{sector_actual}\t{suma/conteo:.3f}")
