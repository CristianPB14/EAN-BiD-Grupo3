from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    TimestampType
)


# ============================================================
# 1. SESIÓN SPARK
# ============================================================

def crear_spark():
    return (
        SparkSession.builder
        .appName("T16_Refinada_Spark")
        .master("local[4]")
        .config("spark.driver.memory", "1g")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
        .getOrCreate()
    )


# ============================================================
# 2. ESQUEMA DECLARADO
# ============================================================

def definir_esquema():

    return StructType([
        StructField("meter_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("sector", StringType(), True),
        StructField("consumo_m3", DoubleType(), True),
        StructField("presion_bar", DoubleType(), True),
        StructField("quality_flag", StringType(), True)
    ])


# ============================================================
# 3. COLUMNAS DERIVADAS
# ============================================================

def columnas_derivadas(df):

    return (
        df
        .withColumn("fecha", F.to_date("timestamp"))
        .withColumn("hora", F.hour("timestamp"))
        .withColumn(
            "es_confiable",
            F.when(
                F.col("quality_flag") == "OK",
                F.lit(True)
            ).otherwise(F.lit(False))
        )
        .withColumn("anio", F.year("timestamp"))
        .withColumn(
            "mes",
            F.date_format("timestamp", "MM")
        )
        .withColumn(
            "dia",
            F.date_format("timestamp", "dd")
        )
    )


# ============================================================
# 4. CLASIFICACIÓN NATIVA DE PRESIÓN
# ============================================================

def clasificar_nativa(df):

    return df.withColumn(
        "nivel_presion",
        F.when(
            F.col("presion_bar").isNull(),
            F.lit(None).cast("string")
        )
        .when(
            F.col("presion_bar") < 2.5,
            F.lit("baja")
        )
        .when(
            F.col("presion_bar") > 3.5,
            F.lit("alta")
        )
        .otherwise(
            F.lit("normal")
        )
    )


# ============================================================
# 5. ESCRITURA DE LA CAPA REFINADA
# ============================================================

def escribir_capa(df, salida, modo="overwrite"):

    (
        df.write
        .format("parquet")
        .mode(modo)
        .partitionBy("anio", "mes", "dia")
        .save(salida)
    )


# ============================================================
# 6. LECTURA DE LA CRUDA
# ============================================================

def leer_cruda(spark, ruta):

    esquema = definir_esquema()

    return (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("sep", ",")
        .option("mode", "PERMISSIVE")
        .option("enforceSchema", "false")
        .schema(esquema)
        .load(ruta)
    )


# ============================================================
# 7. PIPELINE PRINCIPAL
# ============================================================

def construir_capa(spark, ruta_entrada, ruta_salida):

    df = leer_cruda(
        spark,
        ruta_entrada
    )

    df = columnas_derivadas(df)

    df = clasificar_nativa(df)

    escribir_capa(
        df,
        ruta_salida,
        modo="overwrite"
    )

    return df


# ============================================================
# 8. EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    spark = crear_spark()

    try:

        ruta_entrada = "datalake/cruda"
        ruta_salida = "datalake/refinada_spark"

        df_final = construir_capa(
            spark,
            ruta_entrada,
            ruta_salida
        )

        # Acción para materializar la ejecución
        total = df_final.count()

        print("=" * 60)
        print("CAPA REFINADA SPARK")
        print("=" * 60)
        print(f"Filas procesadas: {total}")
        print(f"Salida: {ruta_salida}")
        print("=" * 60)

    finally:

        spark.stop()
