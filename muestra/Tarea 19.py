# ============================================================
# T19 - MATERIALIZACIÓN DEL MODELO DIMENSIONAL
# Proyecto: Plataforma de datos del acueducto
# Motor destino: PostgreSQL
# ============================================================

import os
import hashlib
from datetime import datetime, date, timedelta

import psycopg2
from psycopg2.extras import execute_values


# ------------------------------------------------------------
# 1. CONFIGURACIÓN
# ------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "database": os.getenv("PGDATABASE", "acueducto"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}

SCHEMA = "dw"


# ------------------------------------------------------------
# 2. CONEXIÓN
# ------------------------------------------------------------

def conectar():
    """Crea una conexión con PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


# ------------------------------------------------------------
# 3. CREACIÓN DEL MODELO
# ------------------------------------------------------------

def crear_modelo(conn):
    """Crea las tablas dimensionales y de hechos."""

    sql = f"""
    CREATE SCHEMA IF NOT EXISTS {SCHEMA};

    -- ======================================================
    -- DIMENSIÓN SECTOR
    -- Tipo 1: conserva únicamente el valor actual.
    -- ======================================================

    CREATE TABLE IF NOT EXISTS {SCHEMA}.dim_sector (
        sector_sk BIGSERIAL PRIMARY KEY,
        sector_id VARCHAR(30) NOT NULL UNIQUE,
        nombre_sector VARCHAR(100) NOT NULL
    );

    -- ======================================================
    -- DIMENSIÓN MEDIDOR
    -- Tipo 2: conserva las diferentes versiones.
    -- ======================================================

    CREATE TABLE IF NOT EXISTS {SCHEMA}.dim_medidor (
        medidor_sk BIGSERIAL PRIMARY KEY,
        meter_id VARCHAR(30) NOT NULL,
        sector_sk BIGINT NOT NULL,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE,
        es_actual BOOLEAN NOT NULL DEFAULT TRUE,

        CONSTRAINT fk_medidor_sector
            FOREIGN KEY (sector_sk)
            REFERENCES {SCHEMA}.dim_sector(sector_sk),

        CONSTRAINT uq_medidor_version
            UNIQUE (meter_id, fecha_inicio)
    );

    -- ======================================================
    -- TABLA DE HECHOS
    -- ======================================================

    CREATE TABLE IF NOT EXISTS {SCHEMA}.hechos_lectura (
        medidor_sk BIGINT NOT NULL,
        sector_sk BIGINT NOT NULL,
        fecha_hora TIMESTAMP NOT NULL,
        consumo_m3 NUMERIC(14,4) NOT NULL,
        presion_bar NUMERIC(10,4),
        quality_flag VARCHAR(20) NOT NULL,

        PRIMARY KEY (medidor_sk, fecha_hora),

        CONSTRAINT fk_hecho_medidor
            FOREIGN KEY (medidor_sk)
            REFERENCES {SCHEMA}.dim_medidor(medidor_sk),

        CONSTRAINT fk_hecho_sector
            FOREIGN KEY (sector_sk)
            REFERENCES {SCHEMA}.dim_sector(sector_sk),

        CONSTRAINT ck_quality
            CHECK (
                quality_flag IN
                ('OK', 'ESTIMADO', 'SIN_SENAL')
            )
    );

    -- ======================================================
    -- TABLA DE CONTROL DEL PROCESO
    -- ======================================================

    CREATE TABLE IF NOT EXISTS {SCHEMA}.control_carga (
        id BIGSERIAL PRIMARY KEY,
        fecha_ejecucion TIMESTAMP NOT NULL,
        filas_cargadas BIGINT NOT NULL,
        suma_consumo NUMERIC(18,4) NOT NULL,
        checksum VARCHAR(64) NOT NULL,
        observacion VARCHAR(250)
    );
    """

    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()


# ------------------------------------------------------------
# 4. CARGA DE DIMENSIÓN SECTOR
# ------------------------------------------------------------

def cargar_sectores(conn):
    """
    Carga la dimensión de sectores.
    Al ser Tipo 1, una modificación actualiza el registro
    existente sin crear una nueva versión histórica.
    """

    sectores = [
        ("S-NORTE", "Sector Norte"),
        ("S-CENTRO", "Sector Centro"),
        ("S-SUR", "Sector Sur"),
    ]

    sql = f"""
    INSERT INTO {SCHEMA}.dim_sector
        (sector_id, nombre_sector)
    VALUES %s
    ON CONFLICT (sector_id)
    DO UPDATE SET
        nombre_sector = EXCLUDED.nombre_sector;
    """

    with conn.cursor() as cur:
        execute_values(cur, sql, sectores)

    conn.commit()


# ------------------------------------------------------------
# 5. FUNCIONES DE DIMENSIÓN TIPO 2
# ------------------------------------------------------------

def obtener_sector_sk(conn, sector_id):
    """Obtiene la clave subrogada de un sector."""

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT sector_sk
            FROM {SCHEMA}.dim_sector
            WHERE sector_id = %s
            """,
            (sector_id,)
        )

        row = cur.fetchone()

    return row[0] if row else None


def cargar_medidor_tipo2(
    conn,
    meter_id,
    sector_id,
    fecha_inicio,
    fecha_fin=None
):
    """
    Carga una versión de un medidor.

    Si el medidor ya tiene una versión vigente y cambia de sector,
    se cierra la versión anterior y se crea una nueva.
    """

    sector_sk = obtener_sector_sk(conn, sector_id)

    if sector_sk is None:
        raise ValueError(
            f"No existe el sector {sector_id}"
        )

    with conn.cursor() as cur:

        # Buscar versión actual
        cur.execute(
            f"""
            SELECT medidor_sk, sector_sk, fecha_inicio
            FROM {SCHEMA}.dim_medidor
            WHERE meter_id = %s
              AND es_actual = TRUE
            """,
            (meter_id,)
        )

        actual = cur.fetchone()

        # Caso 1: el medidor no existe
        if actual is None:

            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.dim_medidor
                    (
                        meter_id,
                        sector_sk,
                        fecha_inicio,
                        fecha_fin,
                        es_actual
                    )
                VALUES (%s, %s, %s, %s, TRUE)
                RETURNING medidor_sk
                """,
                (
                    meter_id,
                    sector_sk,
                    fecha_inicio,
                    fecha_fin
                )
            )

        # Caso 2: existe pero cambia de sector
        else:

            medidor_sk_actual = actual[0]
            sector_sk_actual = actual[1]

            if sector_sk_actual != sector_sk:

                # La versión anterior deja de estar vigente
                fecha_cierre = fecha_inicio - timedelta(days=1)

                cur.execute(
                    f"""
                    UPDATE {SCHEMA}.dim_medidor
                    SET fecha_fin = %s,
                        es_actual = FALSE
                    WHERE medidor_sk = %s
                    """,
                    (
                        fecha_cierre,
                        medidor_sk_actual
                    )
                )

                # Nueva versión
                cur.execute(
                    f"""
                    INSERT INTO {SCHEMA}.dim_medidor
                        (
                            meter_id,
                            sector_sk,
                            fecha_inicio,
                            fecha_fin,
                            es_actual
                        )
                    VALUES (%s, %s, %s, %s, TRUE)
                    """,
                    (
                        meter_id,
                        sector_sk,
                        fecha_inicio,
                        fecha_fin
                    )
                )

    conn.commit()


# ------------------------------------------------------------
# 6. BÚSQUEDA DE CLAVE POR VIGENCIA
# ------------------------------------------------------------

def buscar_clave_vigente(
    conn,
    meter_id,
    fecha_lectura
):
    """
    Busca la versión correcta del medidor para una fecha
    específica.

    Regla:

        fecha_inicio <= fecha_lectura
        y
        fecha_fin es NULL o fecha_lectura <= fecha_fin
    """

    with conn.cursor() as cur:

        cur.execute(
            f"""
            SELECT
                medidor_sk,
                sector_sk
            FROM {SCHEMA}.dim_medidor
            WHERE meter_id = %s
              AND fecha_inicio <= %s
              AND (
                    fecha_fin IS NULL
                    OR %s <= fecha_fin
                  )
            ORDER BY fecha_inicio DESC
            LIMIT 1
            """,
            (
                meter_id,
                fecha_lectura,
                fecha_lectura
            )
        )

        return cur.fetchone()


# ------------------------------------------------------------
# 7. MIEMBRO INFERIDO
# ------------------------------------------------------------

def crear_miembro_inferido(
    conn,
    meter_id,
    fecha_lectura
):
    """
    Crea un miembro inferido cuando llega una lectura para
    un medidor que todavía no tiene dimensión completa.

    El objetivo es conservar la lectura y no perderla.
    """

    sector_sk = obtener_sector_sk(
        conn,
        "S-DESCONOCIDO"
    )

    if sector_sk is None:

        with conn.cursor() as cur:

            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.dim_sector
                    (sector_id, nombre_sector)
                VALUES
                    ('S-DESCONOCIDO', 'Sector desconocido')
                ON CONFLICT (sector_id) DO NOTHING
                """
            )

        conn.commit()

        sector_sk = obtener_sector_sk(
            conn,
            "S-DESCONOCIDO"
        )

    with conn.cursor() as cur:

        cur.execute(
            f"""
            SELECT medidor_sk
            FROM {SCHEMA}.dim_medidor
            WHERE meter_id = %s
              AND fecha_inicio = %s
            """,
            (
                meter_id,
                fecha_lectura
            )
        )

        existe = cur.fetchone()

        if existe:
            return existe[0]

        cur.execute(
            f"""
            INSERT INTO {SCHEMA}.dim_medidor
                (
                    meter_id,
                    sector_sk,
                    fecha_inicio,
                    fecha_fin,
                    es_actual
                )
            VALUES (%s, %s, %s, NULL, TRUE)
            RETURNING medidor_sk
            """,
            (
                meter_id,
                sector_sk,
                fecha_lectura
            )
        )

        medidor_sk = cur.fetchone()[0]

    conn.commit()

    return medidor_sk


# ------------------------------------------------------------
# 8. CARGA DE HECHOS
# ------------------------------------------------------------

def cargar_hechos(conn, lecturas):
    """
    Carga lecturas resolviendo primero la clave subrogada
    mediante vigencia.
    """

    cargadas = 0
    sin_dimension = 0

    with conn.cursor() as cur:

        for lectura in lecturas:

            meter_id = lectura["meter_id"]
            fecha_hora = lectura["fecha_hora"]

            fecha = fecha_hora.date()

            clave = buscar_clave_vigente(
                conn,
                meter_id,
                fecha
            )

            # ------------------------------------------------
            # Si existe dimensión
            # ------------------------------------------------

            if clave:

                medidor_sk = clave[0]
                sector_sk = clave[1]

            # ------------------------------------------------
            # Si no existe dimensión:
            # crear miembro inferido
            # ------------------------------------------------

            else:

                medidor_sk = crear_miembro_inferido(
                    conn,
                    meter_id,
                    fecha
                )

                with conn.cursor() as cur2:

                    cur2.execute(
                        f"""
                        SELECT sector_sk
                        FROM {SCHEMA}.dim_medidor
                        WHERE medidor_sk = %s
                        """,
                        (medidor_sk,)
                    )

                    sector_sk = cur2.fetchone()[0]

                sin_dimension += 1

            # ------------------------------------------------
            # Insertar hecho
            # ------------------------------------------------

            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.hechos_lectura
                    (
                        medidor_sk,
                        sector_sk,
                        fecha_hora,
                        consumo_m3,
                        presion_bar,
                        quality_flag
                    )
                VALUES
                    (%s, %s, %s, %s, %s, %s)
                ON CONFLICT
                    (medidor_sk, fecha_hora)
                DO UPDATE SET
                    sector_sk = EXCLUDED.sector_sk,
                    consumo_m3 = EXCLUDED.consumo_m3,
                    presion_bar = EXCLUDED.presion_bar,
                    quality_flag = EXCLUDED.quality_flag
                """,
                (
                    medidor_sk,
                    sector_sk,
                    fecha_hora,
                    lectura["consumo_m3"],
                    lectura["presion_bar"],
                    lectura["quality_flag"]
                )
            )

            cargadas += 1

    conn.commit()

    print("Filas procesadas:", cargadas)
    print("Filas con miembro inferido:", sin_dimension)


# ------------------------------------------------------------
# 9. RECARGA TRANSACCIONAL DE UNA VENTANA
# ------------------------------------------------------------

def recargar_ventana(
    conn,
    fecha_inicio,
    fecha_fin,
    lecturas
):
    """
    Reprocesa una ventana de fechas de forma atómica.

    1. Elimina los hechos de la ventana.
    2. Inserta nuevamente las lecturas.
    3. Si ocurre un error, hace rollback.
    """

    try:

        with conn.cursor() as cur:

            # ----------------------------------------------
            # Eliminar únicamente la ventana
            # ----------------------------------------------

            cur.execute(
                f"""
                DELETE FROM {SCHEMA}.hechos_lectura
                WHERE fecha_hora::DATE
                      BETWEEN %s AND %s
                """,
                (
                    fecha_inicio,
                    fecha_fin
                )
            )

            eliminadas = cur.rowcount

            # ----------------------------------------------
            # Insertar nuevamente
            # ----------------------------------------------

            for lectura in lecturas:

                fecha = lectura["fecha_hora"].date()

                if not (
                    fecha_inicio <= fecha <= fecha_fin
                ):
                    continue

                clave = buscar_clave_vigente(
                    conn,
                    lectura["meter_id"],
                    fecha
                )

                if clave:

                    medidor_sk = clave[0]
                    sector_sk = clave[1]

                else:

                    medidor_sk = crear_miembro_inferido(
                        conn,
                        lectura["meter_id"],
                        fecha
                    )

                    cur.execute(
                        f"""
                        SELECT sector_sk
                        FROM {SCHEMA}.dim_medidor
                        WHERE medidor_sk = %s
                        """,
                        (medidor_sk,)
                    )

                    sector_sk = cur.fetchone()[0]

                cur.execute(
                    f"""
                    INSERT INTO {SCHEMA}.hechos_lectura
                        (
                            medidor_sk,
                            sector_sk,
                            fecha_hora,
                            consumo_m3,
                            presion_bar,
                            quality_flag
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        medidor_sk,
                        sector_sk,
                        lectura["fecha_hora"],
                        lectura["consumo_m3"],
                        lectura["presion_bar"],
                        lectura["quality_flag"]
                    )
                )

        conn.commit()

        print(
            f"Ventana recargada correctamente. "
            f"Filas eliminadas: {eliminadas}"
        )

    except Exception as error:

        conn.rollback()

        print(
            "ERROR: la transacción fue revertida."
        )

        raise error


# ------------------------------------------------------------
# 10. RECONCILIACIÓN
# ------------------------------------------------------------

def reconciliar(conn):

    with conn.cursor() as cur:

        cur.execute(
            f"""
            SELECT
                COUNT(*),
                COALESCE(SUM(consumo_m3), 0)
            FROM {SCHEMA}.hechos_lectura
            """
        )

        filas, suma = cur.fetchone()

    print("\nRECONCILIACIÓN")
    print("----------------------------")
    print("Filas:", filas)
    print("Suma consumo:", round(float(suma), 4))

    return filas, float(suma)


# ------------------------------------------------------------
# 11. CHECKSUM
# ------------------------------------------------------------

def calcular_checksum(conn):

    with conn.cursor() as cur:

        cur.execute(
            f"""
            SELECT
                medidor_sk,
                sector_sk,
                fecha_hora,
                consumo_m3,
                presion_bar,
                quality_flag
            FROM {SCHEMA}.hechos_lectura
            ORDER BY
                fecha_hora,
                medidor_sk
            """
        )

        filas = cur.fetchall()

    texto = "\n".join(
        str(fila)
        for fila in filas
    )

    checksum = hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()

    print("Checksum:", checksum)

    return checksum


# ------------------------------------------------------------
# 12. CONTRATO DEL MODELO
# ------------------------------------------------------------

def verificar_contrato(conn):

    resultados = {}

    with conn.cursor() as cur:

        # ----------------------------------------------
        # Conteo
        # ----------------------------------------------

        cur.execute(
            f"""
            SELECT COUNT(*)
            FROM {SCHEMA}.hechos_lectura
            """
        )

        resultados["conteo"] = cur.fetchone()[0] > 0

        # ----------------------------------------------
        # Integridad referencial
        # ----------------------------------------------

        cur.execute(
            f"""
            SELECT COUNT(*)
            FROM {SCHEMA}.hechos_lectura h
            LEFT JOIN {SCHEMA}.dim_medidor m
                ON h.medidor_sk = m.medidor_sk
            WHERE m.medidor_sk IS NULL
            """
        )

        resultados["integridad_referencial"] = (
            cur.fetchone()[0] == 0
        )

        # ----------------------------------------------
        # Unicidad del grano
        # ----------------------------------------------

        cur.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT
                    medidor_sk,
                    fecha_hora,
                    COUNT(*) AS n
                FROM {SCHEMA}.hechos_lectura
                GROUP BY
                    medidor_sk,
                    fecha_hora
                HAVING COUNT(*) > 1
            ) duplicados
            """
        )

        resultados["unicidad_grano"] = (
            cur.fetchone()[0] == 0
        )

        # ----------------------------------------------
        # Vigencia
        # ----------------------------------------------

        cur.execute(
            f"""
            SELECT COUNT(*)
            FROM {SCHEMA}.dim_medidor
            WHERE fecha_fin IS NOT NULL
              AND fecha_inicio > fecha_fin
            """
        )

        resultados["vigencia"] = (
            cur.fetchone()[0] == 0
        )

    print("\nCONTRATO DEL MODELO")
    print("----------------------------")

    for nombre, resultado in resultados.items():

        estado = "OK" if resultado else "FALLA"

        print(
            f"{nombre}: {estado}"
        )

    return resultados


# ------------------------------------------------------------
# 13. PROCESO PRINCIPAL
# ------------------------------------------------------------

def main():

    print("=" * 60)
    print("T19 - MATERIALIZACIÓN DEL MODELO DIMENSIONAL")
    print("=" * 60)

    conn = conectar()

    try:

        # Paso 1
        print("\n[1] Creando modelo...")
        crear_modelo(conn)

        # Paso 2
        print("\n[2] Cargando dimensión sector...")
        cargar_sectores(conn)

        # Paso 3
        print("\n[3] Cargando dimensiones de medidores...")

        cargar_medidor_tipo2(
            conn,
            "MED-001",
            "S-NORTE",
            date(2026, 1, 1)
        )

        cargar_medidor_tipo2(
            conn,
            "MED-002",
            "S-CENTRO",
            date(2026, 1, 1)
        )

        # Cambio histórico del medidor
        cargar_medidor_tipo2(
            conn,
            "MED-001",
            "S-SUR",
            date(2026, 3, 1)
        )

        # Paso 4
        print("\n[4] Buscando versiones por vigencia...")

        ejemplos = [
            ("MED-001", date(2026, 2, 15)),
            ("MED-001", date(2026, 3, 15)),
        ]

        for meter_id, fecha in ejemplos:

            resultado = buscar_clave_vigente(
                conn,
                meter_id,
                fecha
            )

            print(
                meter_id,
                fecha,
                "=>",
                resultado
            )

        # ----------------------------------------------------
        # Datos de ejemplo
        # ----------------------------------------------------

        lecturas = []

        fecha_actual = datetime(
            2026, 2, 20, 0, 0
        )

        for hora in range(24):

            lecturas.append(
                {
                    "meter_id": "MED-001",
                    "fecha_hora":
                        fecha_actual +
                        timedelta(hours=hora),
                    "consumo_m3": 4.2 + (hora % 5) * 0.2,
                    "presion_bar": 3.1,
                    "quality_flag": "OK"
                }
            )

        # Paso 5
        print("\n[5] Cargando hechos...")
        cargar_hechos(
            conn,
            lecturas
        )

        # Paso 6
        print("\n[6] Reconciliando...")
        reconciliar(conn)

        # Paso 7
        print("\n[7] Calculando checksum...")
        calcular_checksum(conn)

        # Paso 8
        print("\n[8] Verificando contrato...")
        resultados = verificar_contrato(conn)

        if all(resultados.values()):

            print(
                "\nRESULTADO FINAL: CONTRATO APROBADO"
            )

        else:

            print(
                "\nRESULTADO FINAL: CONTRATO CON FALLAS"
            )

    finally:

        conn.close()


if __name__ == "__main__":
    main()
