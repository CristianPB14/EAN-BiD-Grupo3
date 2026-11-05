Script de ingesta

Archivo:

src/ingesta_incremental.py

Código:

import psycopg2
from datetime import datetime


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "acueducto",
    "user": "postgres",
    "password": "postgres"
}


def conectar():
    return psycopg2.connect(**DB_CONFIG)


def inicializar_estado(conn):
    sectores = [
        "S-NORTE",
        "S-SUR",
        "S-ESTE",
        "S-OESTE"
    ]

    with conn.cursor() as cur:
        for sector in sectores:
            cur.execute(
                """
                INSERT INTO estado_ingesta (
                    sector,
                    ultima_marca_agua,
                    ultima_ejecucion,
                    filas_cargadas
                )
                VALUES (
                    %s,
                    '2000-01-01 00:00:00',
                    NULL,
                    0
                )
                ON CONFLICT (sector) DO NOTHING;
                """,
                (sector,)
            )


def procesar_sector(conn, sector):
    with conn.cursor() as cur:

        # 1. Obtener la marca de agua actual
        cur.execute(
            """
            SELECT ultima_marca_agua
            FROM estado_ingesta
            WHERE sector = %s
            FOR UPDATE;
            """,
            (sector,)
        )

        resultado = cur.fetchone()

        if resultado is None:
            raise ValueError(
                f"No existe estado_ingesta para el sector {sector}"
            )

        watermark = resultado[0]

        # 2. Insertar solamente registros posteriores
        #    a la marca de agua.
        #
        #    lote_entrante representa la fuente/lote
        #    generado para la instancia del equipo.

        cur.execute(
            """
            INSERT INTO stg_lecturas (
                meter_id,
                "timestamp",
                sector,
                consumo_m3,
                presion_bar,
                quality_flag
            )
            SELECT
                meter_id,
                "timestamp",
                sector,
                consumo_m3,
                presion_bar,
                quality_flag
            FROM lote_entrante
            WHERE sector = %s
              AND "timestamp" > %s
            ON CONFLICT (meter_id, "timestamp")
            DO NOTHING;
            """,
            (sector, watermark)
        )

        # 3. Cantidad recibida en el lote
        cur.execute(
            """
            SELECT COUNT(*)
            FROM lote_entrante
            WHERE sector = %s;
            """,
            (sector,)
        )

        filas_recibidas = cur.fetchone()[0]

        # 4. Obtener la máxima marca temporal
        cur.execute(
            """
            SELECT MAX("timestamp")
            FROM lote_entrante
            WHERE sector = %s;
            """,
            (sector,)
        )

        nueva_marca = cur.fetchone()[0]

        # 5. Actualizar el estado
        if nueva_marca is not None:

            cur.execute(
                """
                UPDATE estado_ingesta
                SET
                    ultima_marca_agua = GREATEST(
                        ultima_marca_agua,
                        %s
                    ),
                    ultima_ejecucion = NOW(),
                    filas_cargadas = %s
                WHERE sector = %s;
                """,
                (
                    nueva_marca,
                    filas_recibidas,
                    sector
                )
            )


def ejecutar_ingesta():
    conn = conectar()

    try:
        # Todo el proceso se ejecuta como una
        # única transacción.
        conn.autocommit = False

        inicializar_estado(conn)

        sectores = [
            "S-NORTE",
            "S-SUR",
            "S-ESTE",
            "S-OESTE"
        ]

        for sector in sectores:
            procesar_sector(conn, sector)

        conn.commit()

        print("Ingesta completada correctamente.")

    except Exception as error:
        conn.rollback()
        print("Error durante la ingesta.")
        print(error)
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    ejecutar_ingesta()
