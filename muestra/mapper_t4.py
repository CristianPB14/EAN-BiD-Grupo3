#!/usr/bin/env python3
import sys

for linea in sys.stdin:
    campos = linea.strip().split(",")
    
    # Índices reales extraídos de secop_sample.csv
    idx_modalidad = 16 
    idx_valor = 34
    
    # Saltamos líneas incompletas o la fila de cabecera
    if len(campos) <= max(idx_modalidad, idx_valor) or campos[0] == "nombre_entidad":
        continue
        
    try:
        modalidad = campos[idx_modalidad]
        valor = float(campos[idx_valor])
        # Emitimos el par: Modalidad \t Valor,1
        print(f"{modalidad}\t{valor},1")
    except ValueError:
        continue