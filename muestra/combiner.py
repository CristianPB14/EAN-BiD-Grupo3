#!/usr/bin/env python3
# combiner.py · agrega localmente antes de la mezcla (S4, nivel 2).
#
# Hadoop no garantiza cuántas veces corre el combinador (cero, una o varias),
# así que su entrada y su salida deben ser compatibles entre sí. Este
# combinador acepta dos formatos de valor:
#   - "presion"        -> salida directa de mapper.py (primera pasada)
#   - "suma,conteo"     -> salida de una ejecución previa del propio combinador
# y siempre emite "suma,conteo", nunca un promedio: el promedio de promedios
# no es el promedio, por eso la división se deja para el reductor final.
import sys


def emitir(sector, suma, conteo):
    print(f"{sector}\t{suma},{conteo}")


sector_actual, suma, conteo = None, 0.0, 0

for linea in sys.stdin:
    sector, valor = linea.strip().split("\t")

    if "," in valor:
        parcial_suma_str, parcial_conteo_str = valor.split(",")
        parcial_suma, parcial_conteo = float(parcial_suma_str), int(parcial_conteo_str)
    else:
        parcial_suma, parcial_conteo = float(valor), 1

    if sector != sector_actual and sector_actual is not None:
        emitir(sector_actual, suma, conteo)
        suma, conteo = 0.0, 0

    sector_actual = sector
    suma += parcial_suma
    conteo += parcial_conteo

if sector_actual is not None:
    emitir(sector_actual, suma, conteo)
