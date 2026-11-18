
from pathlib import Path
import json

from pyspark.sql import SparkSession, functions as F

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "lecturas_acueducto.csv"
OUT = ROOT / "salidas"

OUT.mkdir(exist_ok=True)

spark = (
    SparkSession.builder
    .appName("TareaT18_Acueducto")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# ==========================================
# 2. FUNCIÓN PARA VALIDAR CONTRATOS
# ==========================================

def validar_contrato(df, ruta, nombre):

    contrato = json.loads(
        Path(ruta).read_text(encoding="utf-8")
    )

    errores = []

    for columna in contrato["columnas_obligatorias"]:
        if columna not in df.columns:
            errores.append(
                f"Falta columna: {columna}"
            )

    if "fecha" in df.columns:
        if df.filter(F.col("fecha").isNull()).limit(1).count():
            errores.append("Hay fechas nulas")

    if "sector" in df.columns:
        if df.filter(
            F.col("sector").isNull() |
            (F.trim(F.col("sector")) == "")
        ).limit(1).count():
            errores.append("Hay sectores vacíos")

    if "consumo_total_m3" in df.columns:
        if df.filter(
            F.col("consumo_total_m3") < 0
        ).limit(1).count():
            errores.append("Hay consumos negativos")

    if errores:
        raise ValueError(
            f"Contrato {nombre} NO APROBADO: {errores}"
        )

    print(f"Contrato {nombre}: APROBADO")


# ==========================================
# 3. CAPA CRUDA
# ==========================================

cruda = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(str(DATA))
)

cruda.write.mode("overwrite").parquet(
    str(OUT / "cruda")
)

print("CAPA CRUDA")
print("Total de registros:", cruda.count())


# ==========================================
# 4. CAPA DE PREPARACIÓN
# ==========================================

preparacion = (
    cruda

    .withColumn(
        "fecha",
        F.to_date("fecha")
    )

    .withColumn(
        "sector",
        F.initcap(F.trim("sector"))
    )

    .withColumn(
        "consumo_m3",
        F.col("consumo_m3").cast("double")
    )

    .withColumn(
        "presion_psi",
        F.col("presion_psi").cast("double")
    )

    .withColumn(
        "es_valida",
        (F.col("calidad_origen") == "OK") &
        F.col("sector").isNotNull() &
        (F.col("sector") != "") &
        (F.col("consumo_m3") > 0) &
        F.col("presion_psi").between(20, 60)
    )
)

preparacion.write.mode("overwrite").parquet(
    str(OUT / "preparacion")
)

preparacion.createOrReplaceTempView(
    "lecturas_preparadas"
)

print("\nCAPA DE PREPARACIÓN")
print("Total:", preparacion.count())

validas = preparacion.filter("es_valida")
excluidas = preparacion.filter("NOT es_valida")

print("Lecturas válidas:", validas.count())
print("Lecturas excluidas:", excluidas.count())


# ==========================================
# 5. PROCESO ETL
# ==========================================

etl = (
    preparacion
    .filter("es_valida")

    .groupBy("fecha", "sector")

    .agg(
        F.count("*").alias("cantidad_lecturas"),

        F.round(
            F.sum("consumo_m3"), 2
        ).alias("consumo_total_m3"),

        F.round(
            F.avg("presion_psi"), 2
        ).alias("presion_promedio_psi")
    )
)

etl.write.mode("overwrite").parquet(
    str(OUT / "etl_producto_diario")
)

print("\nPROCESO ETL")
print("Registros ETL:", etl.count())


# ==========================================
# 6. PROCESO ELT - PRODUCTO 1
# ==========================================

sql1 = (
    ROOT / "sql" / "producto_1.sql"
).read_text(encoding="utf-8")

producto1 = spark.sql(sql1)

producto1.write.mode("overwrite").parquet(
    str(OUT / "elt_producto_1")
)

validar_contrato(
    producto1,
    ROOT / "contratos" / "contrato_producto_1.json",
    "Producto 1"
)


# ==========================================
# 7. PROCESO ELT - PRODUCTO 2
# ==========================================

sql2 = (
    ROOT / "sql" / "producto_2.sql"
).read_text(encoding="utf-8")

producto2 = spark.sql(sql2)

producto2.write.mode("overwrite").parquet(
    str(OUT / "elt_producto_2")
)

validar_contrato(
    producto2,
    ROOT / "contratos" / "contrato_producto_2.json",
    "Producto 2"
)


# ==========================================
# 8. COMPARACIÓN ETL VS ELT
# ==========================================

a = etl.select(
    "fecha",
    "sector",
    "cantidad_lecturas",
    "consumo_total_m3"
)

b = producto1.select(
    "fecha",
    "sector",
    "cantidad_lecturas",
    "consumo_total_m3"
)

diferencias = (
    a.exceptAll(b).count() +
    b.exceptAll(a).count()
)

suma_etl = etl.agg(
    F.round(F.sum("consumo_total_m3"), 2)
).first()[0] or 0

suma_elt = producto1.agg(
    F.round(F.sum("consumo_total_m3"), 2)
).first()[0] or 0

print("\nCOMPARACIÓN ETL VS ELT")

print("Diferencias:", diferencias)
print("Consumo ETL:", suma_etl)
print("Consumo ELT:", suma_elt)

if diferencias == 0:
    print("RECONCILIACIÓN APROBADA")
else:
    print("RECONCILIACIÓN NO APROBADA")


# ==========================================
# 9. REPROCESO POR VENTANA DE FECHAS
# ==========================================

inicio = "2025-01-05"
fin = "2025-01-07"

ventana = producto1.filter(
    (F.col("fecha") >= F.to_date(F.lit(inicio))) &
    (F.col("fecha") <= F.to_date(F.lit(fin)))
)

ventana.write.mode("overwrite").partitionBy(
    "fecha"
).parquet(str(OUT / "reproceso_ventana"))

print("\nREPROCESO")
print("Fecha inicial:", inicio)
print("Fecha final:", fin)
print("Registros reprocesados:", ventana.count())


# ==========================================
# 10. GUARDAR MÉTRICAS
# ==========================================

metricas = {

    "filas_crudas": cruda.count(),

    "filas_validas": validas.count(),

    "filas_excluidas": excluidas.count(),

    "filas_producto_etl": etl.count(),

    "filas_producto_elt": producto1.count(),

    "diferencias_reconciliacion": diferencias,

    "consumo_total_etl_m3": float(suma_etl),

    "consumo_total_elt_m3": float(suma_elt),

    "ventana_reproceso": {
        "inicio": inicio,
        "fin": fin,
        "filas": ventana.count()
    }
}

(OUT / "metricas.json").write_text(
    json.dumps(
        metricas,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("\nPROYECTO FINALIZADO")
print("Métricas guardadas en salidas/metricas.json")

spark.stop()
