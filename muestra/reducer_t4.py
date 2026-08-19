#!/usr/bin/env python3
import sys

clave_actual = None
suma_valor = 0.0
conteo_total = 0

for linea in sys.stdin:
    campos = linea.strip().split("\t")
    if len(campos) != 2:
        continue
    
    clave = campos[0]
    try:
        valores = campos[1].split(",")
        valor = float(valores[0])
        conteo = int(valores[1])
    except ValueError:
        continue

    if clave_actual == clave:
        suma_valor += valor
        conteo_total += conteo
    else:
        if clave_actual is not None:
            print(f"{clave_actual}\t{suma_valor:.2f},{conteo_total}")
        clave_actual = clave
        suma_valor = valor
        conteo_total = conteo

if clave_actual is not None:
    print(f"{clave_actual}\t{suma_valor:.2f},{conteo_total}")