import os, time, statistics
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.compute as pc
import pyarrow.parquet as pq
import duckdb
from lago import cliente

ESPERADAS = 85

def leer_csv(ruta, delimiter=",", encoding=None, esperadas=None):
    read_opts  = pv.ReadOptions(encoding=encoding) if encoding else None
    
    # El parámetro newlines_in_values va aquí, dentro de ParseOptions
    parse_opts = pv.ParseOptions(delimiter=delimiter, newlines_in_values=True)
    
    tabla = pv.read_csv(ruta, read_options=read_opts, parse_options=parse_opts)
    
    if tabla.num_columns == 1:
        raise ValueError(f"{ruta} se leyó con 1 sola columna. Revisa el separador.")
    if esperadas and tabla.num_columns != esperadas:
        print(f"AVISO: esperaba {esperadas} columnas y leyó {tabla.num_columns}.")
    print(f"Leído {ruta}: {tabla.num_rows:,} filas x {tabla.num_columns} columnas")
    return tabla

def mediana_tiempo(funcion, repeticiones=5):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        funcion()
        tiempos.append(time.perf_counter() - t0)
    return statistics.median(tiempos)

def comparar_codecs(tabla, ruta_csv, columnas_consulta, prefijo="muestra"):
    tam_csv = os.path.getsize(ruta_csv)
    filas = [("CSV", tam_csv, None, None)]
    
    with open("resultados/s6_tabla_codecs.md", "w", encoding="utf-8") as f:
        f.write("# S6 · Comparación de Codecs y Tiempos de Consulta\n\n")
        f.write("| Formato | Tamaño (B) | Escr (s) | Lect sel (s) | vs CSV |\n")
        f.write("|---|---|---|---|---|\n")
        
        for codec in ["snappy", "gzip", "zstd"]:
            destino = f"{prefijo}_{codec}.parquet"
            t_escr = mediana_tiempo(lambda: pq.write_table(tabla, destino, compression=codec))
            t_lect = mediana_tiempo(lambda: pq.read_table(destino, columns=columnas_consulta))
            filas.append((codec, os.path.getsize(destino), t_escr, t_lect))

        for nombre, tam, te, tl in filas:
            if te is None:
                f.write(f"| {nombre} | {tam:,} | - | - | - |\n")
            else:
                red = -100 * (1 - tam / tam_csv)
                f.write(f"| {nombre} | {tam:,} | {te:.3f} | {tl:.4f} | {red:.0f}% |\n")
    print("Tabla comparativa generada en resultados/s6_tabla_codecs.md")

def cronometrar(sql, repeticiones=5):
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter(); duckdb.sql(sql).fetchall()
        tiempos.append(time.perf_counter() - t0)
    return statistics.median(tiempos)

if __name__ == "__main__":
    # 1. Leer CSV
    tabla = leer_csv("data/raw/secop_sample.csv", esperadas=ESPERADAS)
    
    # 2. Comparar Codecs
    COLUMNAS = ["departamento", "valor_del_contrato"]
    comparar_codecs(tabla, "data/raw/secop_sample.csv", COLUMNAS, prefijo="secop")
    
    # 3. Comparar tiempos DuckDB (CSV vs Parquet)
    q_parquet = """SELECT departamento, avg(valor_del_contrato) AS promedio, count(*) AS n
                   FROM 'secop_zstd.parquet' WHERE valor_del_contrato IS NOT NULL
                   GROUP BY departamento ORDER BY promedio DESC LIMIT 10"""
    q_csv     = """SELECT departamento, avg(valor_del_contrato) AS promedio, count(*) AS n
                   FROM read_csv_auto('data/raw/secop_sample.csv') WHERE valor_del_contrato IS NOT NULL
                   GROUP BY departamento ORDER BY promedio DESC LIMIT 10"""
    
    tp, tc = cronometrar(q_parquet), cronometrar(q_csv)
    print(f"\nTiempos DuckDB -> Parquet: {tp:.4f}s | CSV: {tc:.4f}s | CSV es {tc/tp:.1f}x más lento")
    
    with open("resultados/s6_tabla_codecs.md", "a", encoding="utf-8") as f:
        f.write(f"\n## Medición de Motor Analítico (DuckDB)\n")
        f.write(f"- **Parquet (zstd):** {tp:.4f} s\n")
        f.write(f"- **CSV:** {tc:.4f} s\n")
        f.write(f"**Conclusión:** El CSV es {tc/tp:.1f} veces más lento entregando el mismo resultado.\n")

    # 4. Generar particiones y subir a MinIO
    print("\nParticionando y subiendo a MinIO (Capa Refinada)...")
    col = tabla.column("fecha_de_firma")
    if not pa.types.is_timestamp(col.type):
        col = pc.strptime(col, format="%Y-%m-%dT%H:%M:%S", unit="s")
    
    tabla = tabla.append_column("anio", pc.year(col))
    pq.write_to_dataset(tabla, "refinada/secop", partition_cols=["departamento", "anio"], compression="zstd")
    
    s3 = cliente()
    for carpeta, _, archivos in os.walk("refinada/secop"):
        for archivo in archivos:
            if archivo.endswith(".parquet"):
                local = os.path.join(carpeta, archivo)
                clave = os.path.relpath(local, "refinada").replace(os.sep, "/")
                s3.upload_file(local, "refinada", clave)
    print("¡Archivos subidos exitosamente al cubo 'refinada'!")