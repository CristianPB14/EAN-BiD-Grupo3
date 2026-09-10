from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

RUTA_DATOS = "data"
RUTA_RESULTADOS = "resultados"

# Estas columnas deben corresponder a las columnas reales
# de los datos del proyecto.
COLUMNA_FECHA = "fecha"
COLUMNA_MEDIDOR = "medidor"
COLUMNA_SECTOR = "sector"

COLUMNAS_GRANO = [
    COLUMNA_MEDIDOR,
    COLUMNA_FECHA
]


# ============================================================
# 1. CARGAR DATOS
# ============================================================

def buscar_archivos_csv(ruta="data"):
    """
    Busca todos los archivos CSV dentro de la carpeta data.
    """

    return list(Path(ruta).rglob("*.csv"))


def cargar_csv(ruta):
    """
    Carga un archivo CSV intentando utilizar UTF-8.
    Si falla, intenta con latin-1.
    """

    try:
        return pd.read_csv(ruta, encoding="utf-8")

    except UnicodeDecodeError:
        return pd.read_csv(ruta, encoding="latin-1")


def cargar_datos(ruta="data"):
    """
    Carga todos los archivos CSV encontrados.
    """

    archivos = buscar_archivos_csv(ruta)

    datos = {}

    if not archivos:
        print("No se encontraron archivos CSV en la carpeta data.")
        return datos

    for archivo in archivos:

        nombre = archivo.stem

        try:

            df = cargar_csv(archivo)

            datos[nombre] = df

            print(
                f"[OK] {archivo} -> "
                f"{df.shape[0]} filas, "
                f"{df.shape[1]} columnas"
            )

        except Exception as error:

            print(
                f"[ERROR] No fue posible cargar "
                f"{archivo}: {error}"
            )

    return datos


# ============================================================
# 2. MOSTRAR INFORMACIÓN DE LOS DATOS
# ============================================================

def mostrar_informacion_datos(datos):
    """
    Muestra la información básica de cada dataset.
    """

    print("\n" + "=" * 70)
    print("INFORMACIÓN DE LOS DATASETS")
    print("=" * 70)

    for nombre, df in datos.items():

        print(f"\nDataset: {nombre}")
        print(f"Filas: {len(df)}")
        print(f"Columnas: {len(df.columns)}")

        print("\nColumnas disponibles:")

        for columna in df.columns:

            print(
                f"  - {columna} "
                f"({df[columna].dtype})"
            )


# ============================================================
# 3. CREAR DIMENSIÓN FECHA
# ============================================================

def crear_dim_fecha(df, columna_fecha):
    """
    Construye la dimensión fecha.

    Cada fecha recibe una clave subrogada fecha_sk.
    """

    fechas = pd.to_datetime(
        df[columna_fecha],
        errors="coerce"
    )

    fechas = (
        fechas
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    dim_fecha = pd.DataFrame({
        "fecha": fechas
    })

    # Clave subrogada
    dim_fecha["fecha_sk"] = range(
        1,
        len(dim_fecha) + 1
    )

    # Atributos de calendario
    dim_fecha["año"] = (
        dim_fecha["fecha"].dt.year
    )

    dim_fecha["mes"] = (
        dim_fecha["fecha"].dt.month
    )

    dim_fecha["nombre_mes"] = (
        dim_fecha["fecha"].dt.month_name()
    )

    dim_fecha["trimestre"] = (
        dim_fecha["fecha"].dt.quarter
    )

    dim_fecha["dia"] = (
        dim_fecha["fecha"].dt.day
    )

    dim_fecha["dia_semana"] = (
        dim_fecha["fecha"].dt.day_name()
    )

    # Reordenar columnas
    dim_fecha = dim_fecha[
        [
            "fecha_sk",
            "fecha",
            "año",
            "mes",
            "nombre_mes",
            "trimestre",
            "dia",
            "dia_semana"
        ]
    ]

    return dim_fecha


# ============================================================
# 4. CREAR DIMENSIONES GENERALES
# ============================================================

def crear_dimension(
    df,
    columna_origen,
    nombre_sk
):
    """
    Crea una dimensión a partir de una columna de origen.

    La dimensión contiene:
    - clave subrogada
    - clave natural/original
    """

    valores = (
        df[[columna_origen]]
        .dropna()
        .drop_duplicates()
        .sort_values(columna_origen)
        .reset_index(drop=True)
    )

    # Crear clave subrogada
    valores[nombre_sk] = range(
        1,
        len(valores) + 1
    )

    # Renombrar clave proveniente del origen
    valores = valores.rename(
        columns={
            columna_origen:
            f"{columna_origen}_origen"
        }
    )

    # La clave subrogada queda primero
    columnas = [
        nombre_sk
    ] + [
        columna
        for columna in valores.columns
        if columna != nombre_sk
    ]

    return valores[columnas]


# ============================================================
# 5. CONSTRUIR TABLA DE HECHOS
# ============================================================

def construir_hechos(
    df,
    dim_fecha,
    dim_medidor,
    dim_sector,
    columna_fecha,
    columna_medidor,
    columna_sector
):
    """
    Construye la tabla de hechos a partir del dataset original
    y las dimensiones creadas.
    """

    hechos = df.copy()

    # --------------------------------------------------------
    # Convertir fecha
    # --------------------------------------------------------

    hechos[columna_fecha] = pd.to_datetime(
        hechos[columna_fecha],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Relacionar con dimensión fecha
    # --------------------------------------------------------

    hechos = hechos.merge(
        dim_fecha[
            [
                "fecha_sk",
                "fecha"
            ]
        ],
        left_on=columna_fecha,
        right_on="fecha",
        how="left",
        suffixes=(
            "",
            "_dim"
        )
    )

    # --------------------------------------------------------
    # Relacionar con dimensión medidor
    # --------------------------------------------------------

    hechos = hechos.merge(
        dim_medidor,
        left_on=columna_medidor,
        right_on=(
            f"{columna_medidor}_origen"
        ),
        how="left"
    )

    # --------------------------------------------------------
    # Relacionar con dimensión sector
    # --------------------------------------------------------

    hechos = hechos.merge(
        dim_sector,
        left_on=columna_sector,
        right_on=(
            f"{columna_sector}_origen"
        ),
        how="left"
    )

    # --------------------------------------------------------
    # Crear clave subrogada de la tabla de hechos
    # --------------------------------------------------------

    hechos.insert(
        0,
        "lectura_sk",
        range(
            1,
            len(hechos) + 1
        )
    )

    return hechos


# ============================================================
# 6. VALIDAR EL GRANO
# ============================================================

def validar_grano(
    df,
    columnas_grano
):
    """
    Verifica que la combinación de columnas que define el grano
    sea única.

    Ejemplo:

    medidor + fecha

    representa una lectura única del medidor en una fecha/hora.
    """

    resultado = {}

    total_filas = len(df)

    duplicados = df.duplicated(
        subset=columnas_grano
    ).sum()

    resultado["total_filas"] = (
        int(total_filas)
    )

    resultado["duplicados_grano"] = (
        int(duplicados)
    )

    resultado["grano_unico"] = (
        duplicados == 0
    )

    resultado["columnas_grano"] = (
        columnas_grano
    )

    return resultado


# ============================================================
# 7. VALIDAR CLAVES FORÁNEAS
# ============================================================

def validar_claves_foraneas(
    fact,
    dimensiones
):
    """
    Verifica que las claves foráneas de la tabla de hechos
    no tengan valores nulos.
    """

    resultados = {}

    for fk, dimension in dimensiones.items():

        nulos = int(
            fact[fk].isna().sum()
        )

        total = len(fact)

        resultados[fk] = {

            "nulos": nulos,

            "total": total,

            "valida": (
                nulos == 0
            )
        }

    return resultados


# ============================================================
# 8. GENERAR INFORME DE VALIDACIÓN
# ============================================================

def generar_informe_validacion(
    validacion_grano,
    validacion_fk
):
    """
    Genera un informe de validación en formato DataFrame.
    """

    filas = []

    # Validación del grano
    filas.append({
        "validacion": "Unicidad del grano",
        "resultado": (
            "OK"
            if validacion_grano[
                "grano_unico"
            ]
            else "ERROR"
        ),
        "detalle": (
            f"Columnas: "
            f"{', '.join(validacion_grano['columnas_grano'])}; "
            f"duplicados: "
            f"{validacion_grano['duplicados_grano']}"
        )
    })

    # Validaciones de claves foráneas
    for fk, resultado in validacion_fk.items():

        filas.append({
            "validacion": (
                f"Clave foránea {fk}"
            ),

            "resultado": (
                "OK"
                if resultado["valida"]
                else "ERROR"
            ),

            "detalle": (
                f"Nulos: "
                f"{resultado['nulos']} "
                f"de "
                f"{resultado['total']}"
            )
        })

    return pd.DataFrame(filas)


# ============================================================
# 9. GUARDAR TABLAS DIMENSIONALES
# ============================================================

def guardar_tablas(
    dim_fecha,
    dim_medidor,
    dim_sector,
    fact_lecturas,
    resultados
):
    """
    Guarda las dimensiones, la tabla de hechos y las validaciones.
    """

    ruta = Path(resultados)

    ruta.mkdir(
        parents=True,
        exist_ok=True
    )

    # Dimensiones
    dim_fecha.to_csv(
        ruta / "dim_fecha.csv",
        index=False
    )

    dim_medidor.to_csv(
        ruta / "dim_medidor.csv",
        index=False
    )

    dim_sector.to_csv(
        ruta / "dim_sector.csv",
        index=False
    )

    # Tabla de hechos
    fact_lecturas.to_csv(
        ruta / "fact_lecturas.csv",
        index=False
    )

    print("\n[OK] Tablas dimensionales guardadas.")

    print(
        f"[OK] Dimensión fecha: "
        f"{len(dim_fecha)} registros"
    )

    print(
        f"[OK] Dimensión medidor: "
        f"{len(dim_medidor)} registros"
    )

    print(
        f"[OK] Dimensión sector: "
        f"{len(dim_sector)} registros"
    )

    print(
        f"[OK] Tabla de hechos: "
        f"{len(fact_lecturas)} registros"
    )


# ============================================================
# 10. PROCESAMIENTO PRINCIPAL
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("T10 - MODELO LÓGICO DIMENSIONAL")
    print("=" * 70)

    # --------------------------------------------------------
    # Cargar datos
    # --------------------------------------------------------

    datos = cargar_datos(
        RUTA_DATOS
    )

    if not datos:

        print(
            "\nNo existen datos para procesar."
        )

        return

    # --------------------------------------------------------
    # Mostrar información
    # --------------------------------------------------------

    mostrar_informacion_datos(
        datos
    )

    # --------------------------------------------------------
    # Seleccionar dataset principal
    # --------------------------------------------------------

    nombre_dataset = list(
        datos.keys()
    )[0]

    df = datos[
        nombre_dataset
    ].copy()

    print("\n")
    print("=" * 70)
    print(
        f"DATASET SELECCIONADO: "
        f"{nombre_dataset}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Validar columnas necesarias
    # --------------------------------------------------------

    columnas_necesarias = [
        COLUMNA_FECHA,
        COLUMNA_MEDIDOR,
        COLUMNA_SECTOR
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if columnas_faltantes:

        print("\n[ERROR]")
        print(
            "Faltan las siguientes columnas "
            "en el dataset:"
        )

        for columna in columnas_faltantes:
            print(
                f"  - {columna}"
            )

        print(
            "\nDebes modificar las variables "
            "de configuración del programa "
            "para utilizar los nombres reales "
            "de las columnas."
        )

        return

    # --------------------------------------------------------
    # Crear dimensión fecha
    # --------------------------------------------------------

    print("\nCreando dimensión fecha...")

    dim_fecha = crear_dim_fecha(
        df,
        COLUMNA_FECHA
    )

    # --------------------------------------------------------
    # Crear dimensión medidor
    # --------------------------------------------------------

    print(
        "Creando dimensión medidor..."
    )

    dim_medidor = crear_dimension(
        df,
        COLUMNA_MEDIDOR,
        "medidor_sk"
    )

    # --------------------------------------------------------
    # Crear dimensión sector
    # --------------------------------------------------------

    print(
        "Creando dimensión sector..."
    )

    dim_sector = crear_dimension(
        df,
        COLUMNA_SECTOR,
        "sector_sk"
    )

    # --------------------------------------------------------
    # Construir tabla de hechos
    # --------------------------------------------------------

    print(
        "Construyendo tabla de hechos..."
    )

    fact_lecturas = construir_hechos(
        df,
        dim_fecha,
        dim_medidor,
        dim_sector,
        COLUMNA_FECHA,
        COLUMNA_MEDIDOR,
        COLUMNA_SECTOR
    )

    # --------------------------------------------------------
    # Validar grano
    # --------------------------------------------------------

    print(
        "\nValidando grano..."
    )

    validacion_grano = validar_grano(
        df,
        COLUMNAS_GRANO
    )

    # --------------------------------------------------------
    # Mostrar resultado del grano
    # --------------------------------------------------------

    print(
        "\nResultado de validación del grano:"
    )

    print(
        f"Total de filas: "
        f"{validacion_grano['total_filas']}"
    )

    print(
        f"Duplicados del grano: "
        f"{validacion_grano['duplicados_grano']}"
    )

    if validacion_grano["grano_unico"]:

        print(
            "Estado: OK - El grano es único."
        )

    else:

        print(
            "Estado: ERROR - "
            "Existen registros duplicados "
            "para el grano definido."
        )

    # --------------------------------------------------------
    # Validar claves foráneas
    # --------------------------------------------------------

    print(
        "\nValidando claves foráneas..."
    )

    dimensiones = {

        "fecha_sk": dim_fecha,

        "medidor_sk": dim_medidor,

        "sector_sk": dim_sector
    }

    validacion_fk = validar_claves_foraneas(
        fact_lecturas,
        dimensiones
    )

    for fk, resultado in validacion_fk.items():

        estado = (
            "OK"
            if resultado["valida"]
            else "ERROR"
        )

        print(
            f"{fk}: {estado} "
            f"(nulos: "
            f"{resultado['nulos']})"
        )

    # --------------------------------------------------------
    # Generar informe
    # --------------------------------------------------------

    informe = generar_informe_validacion(
        validacion_grano,
        validacion_fk
    )

    # --------------------------------------------------------
    # Guardar resultados
    # --------------------------------------------------------

    guardar_tablas(
        dim_fecha,
        dim_medidor,
        dim_sector,
        fact_lecturas,
        RUTA_RESULTADOS
    )

    informe.to_csv(
        Path(RUTA_RESULTADOS)
        / "validacion_grano.csv",
        index=False
    )

    # --------------------------------------------------------
    # Mostrar resumen
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RESUMEN DEL MODELO DIMENSIONAL")
    print("=" * 70)

    print(
        "\nGrano:"
    )

    print(
        "Una lectura de un medidor "
        "en una hora."
    )

    print(
        "\nTabla de hechos:"
    )

    print(
        "fact_lecturas"
    )

    print(
        "\nDimensiones:"
    )

    print(
        "  1. dim_fecha"
    )

    print(
        "  2. dim_medidor"
    )

    print(
        "  3. dim_sector"
    )

    print(
        "\nClaves subrogadas:"
    )

    print(
        "  fecha_sk"
    )

    print(
        "  medidor_sk"
    )

    print(
        "  sector_sk"
    )

    print(
        "\nArchivos generados:"
    )

    print(
        "  resultados/dim_fecha.csv"
    )

    print(
        "  resultados/dim_medidor.csv"
    )

    print(
        "  resultados/dim_sector.csv"
    )

    print(
        "  resultados/fact_lecturas.csv"
    )

    print(
        "  resultados/validacion_grano.csv"
    )

    print("\n")
    print("=" * 70)
    print("PROCESO FINALIZADO")
    print("=" * 70)


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()
