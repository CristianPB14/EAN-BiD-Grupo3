"""
T13 - Conector de ingesta API
Big Data e Ingeniería de Datos

Equipo de referencia: equipo-3

Funciones:
- Autenticación Bearer Token
- Paginación mediante hay_siguiente
- Manejo de 429 y 5xx
- Retry con backoff exponencial + jitter
- Respeto de Retry-After
- UPSERT en stg_estado_medidor
- Bitácora append-only en bitacora_ingesta_api
- Conciliación de registros
"""

import os
import sys
import time
import uuid
import random
import argparse
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "token_de_prueba")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

T0 = 1
T_MAX = 30
MAX_INTENTOS = 5

TIMEOUT_API = 10
MAX_PAGINAS = 10000


# ============================================================
# CONEXIÓN A POSTGRESQL
# ============================================================

def conectar_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ============================================================
# CREAR TABLAS SI NO EXISTEN
# ============================================================

def crear_tablas(conn):

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stg_estado_medidor (
            meter_id INTEGER PRIMARY KEY,
            estado VARCHAR(100),
            fecha_actualizacion TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bitacora_ingesta_api (
            id SERIAL PRIMARY KEY,
            corrida_id VARCHAR(100),
            equipo VARCHAR(50),
            pagina INTEGER,
            intento INTEGER,
            codigo_http INTEGER,
            duracion_ms INTEGER,
            resultado VARCHAR(50),
            timestamp_intento TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()


# ============================================================
# BITÁCORA
# ============================================================

def registrar_intento(
    conn,
    corrida_id,
    equipo,
    pagina,
    intento,
    codigo_http,
    duracion_ms,
    resultado
):

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bitacora_ingesta_api (
            corrida_id,
            equipo,
            pagina,
            intento,
            codigo_http,
            duracion_ms,
            resultado,
            timestamp_intento
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        corrida_id,
        equipo,
        pagina,
        intento,
        codigo_http,
        duracion_ms,
        resultado,
        datetime.now()
    ))

    conn.commit()
    cur.close()


# ============================================================
# UPSERT DE MEDIDORES
# ============================================================

def guardar_medidores(conn, datos):

    if not datos:
        return

    cur = conn.cursor()

    for medidor in datos:

        meter_id = medidor.get("meter_id")
        estado = medidor.get("estado")

        fecha_actualizacion = medidor.get(
            "fecha_actualizacion"
        )

        cur.execute("""
            INSERT INTO stg_estado_medidor (
                meter_id,
                estado,
                fecha_actualizacion
            )
            VALUES (%s, %s, %s)

            ON CONFLICT (meter_id)
            DO UPDATE SET
                estado = EXCLUDED.estado,
                fecha_actualizacion =
                    EXCLUDED.fecha_actualizacion
        """, (
            meter_id,
            estado,
            fecha_actualizacion
        ))

    conn.commit()
    cur.close()


# ============================================================
# BACKOFF EXPONENCIAL + JITTER
# ============================================================

def calcular_backoff(intento):

    espera_base = min(
        T0 * (2 ** (intento - 1)),
        T_MAX
    )

    jitter = random.uniform(0, 1)

    return espera_base + jitter


# ============================================================
# OBTENER RETRY-AFTER
# ============================================================

def obtener_retry_after(response):

    if response is None:
        return None

    valor = response.headers.get("Retry-After")

    if valor is None:
        return None

    try:
        return float(valor)
    except ValueError:
        return None


# ============================================================
# CLASIFICACIÓN DE RESPUESTAS
# ============================================================

def es_transitorio(codigo):

    return codigo == 429 or codigo in {
        500,
        502,
        503,
        504
    }


def es_permanente(codigo):

    return codigo in {
        400,
        403,
        404,
        422
    }


# ============================================================
# SOLICITUD DE UNA PÁGINA
# ============================================================

def solicitar_pagina(
    session,
    url,
    pagina,
    corrida_id,
    equipo,
    conn
):

    for intento in range(1, MAX_INTENTOS + 1):

        inicio = time.perf_counter()

        response = None
        codigo_http = None

        try:

            response = session.get(
                url,
                params={
                    "page": pagina
                },
                timeout=TIMEOUT_API
            )

            codigo_http = response.status_code

            duracion_ms = int(
                (time.perf_counter() - inicio) * 1000
            )

        except requests.exceptions.RequestException as e:

            duracion_ms = int(
                (time.perf_counter() - inicio) * 1000
            )

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                None,
                duracion_ms,
                "REINTENTABLE"
            )

            if intento >= MAX_INTENTOS:

                return {
                    "ok": False,
                    "agotado": True,
                    "autenticacion": False,
                    "datos": [],
                    "hay_siguiente": False
                }

            espera = calcular_backoff(intento)

            print(
                f"[Página {pagina}] "
                f"Timeout/error de red. "
                f"Reintento {intento + 1}/{MAX_INTENTOS} "
                f"en {espera:.2f}s"
            )

            time.sleep(espera)

            continue

        # ----------------------------------------------------
        # 200 OK
        # ----------------------------------------------------

        if codigo_http == 200:

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                codigo_http,
                duracion_ms,
                "EXITO"
            )

            return {
                "ok": True,
                "agotado": False,
                "autenticacion": False,
                "datos": response.json().get("datos", []),
                "hay_siguiente": response.json().get(
                    "hay_siguiente",
                    False
                ),
                "total": response.json().get(
                    "total_registros_informativo"
                )
            }

        # ----------------------------------------------------
        # 401
        # ----------------------------------------------------

        if codigo_http == 401:

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                codigo_http,
                duracion_ms,
                "FALLO_AUTENTICACION"
            )

            print(
                f"[Página {pagina}] "
                f"401 - autenticación inválida."
            )

            return {
                "ok": False,
                "agotado": False,
                "autenticacion": True,
                "datos": [],
                "hay_siguiente": False
            }

        # ----------------------------------------------------
        # 429
        # ----------------------------------------------------

        if codigo_http == 429:

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                codigo_http,
                duracion_ms,
                "REINTENTABLE"
            )

            if intento >= MAX_INTENTOS:

                print(
                    f"[Página {pagina}] "
                    f"429 - AGOTADO"
                )

                return {
                    "ok": False,
                    "agotado": True,
                    "autenticacion": False,
                    "datos": [],
                    "hay_siguiente": False
                }

            retry_after = obtener_retry_after(response)

            if retry_after is not None:

                espera = retry_after

                print(
                    f"[Página {pagina}] "
                    f"429 - Retry-After: "
                    f"{espera}s"
                )

            else:

                espera = calcular_backoff(intento)

                print(
                    f"[Página {pagina}] "
                    f"429 - backoff: "
                    f"{espera:.2f}s"
                )

            time.sleep(espera)

            continue

        # ----------------------------------------------------
        # 5XX
        # ----------------------------------------------------

        if codigo_http in {
            500,
            502,
            503,
            504
        }:

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                codigo_http,
                duracion_ms,
                "REINTENTABLE"
            )

            if intento >= MAX_INTENTOS:

                print(
                    f"[Página {pagina}] "
                    f"{codigo_http} - AGOTADO"
                )

                return {
                    "ok": False,
                    "agotado": True,
                    "autenticacion": False,
                    "datos": [],
                    "hay_siguiente": False
                }

            retry_after = obtener_retry_after(response)

            if retry_after is not None:
                espera = retry_after
            else:
                espera = calcular_backoff(intento)

            print(
                f"[Página {pagina}] "
                f"{codigo_http} - "
                f"Reintento {intento + 1}/"
                f"{MAX_INTENTOS} "
                f"en {espera:.2f}s"
            )

            time.sleep(espera)

            continue

        # ----------------------------------------------------
        # ERRORES PERMANENTES
        # ----------------------------------------------------

        if es_permanente(codigo_http):

            registrar_intento(
                conn,
                corrida_id,
                equipo,
                pagina,
                intento,
                codigo_http,
                duracion_ms,
                "FALLO_PERMANENTE"
            )

            print(
                f"[Página {pagina}] "
                f"{codigo_http} - "
                f"fallo permanente."
            )

            return {
                "ok": False,
                "agotado": False,
                "autenticacion": False,
                "datos": [],
                "hay_siguiente": False
            }

        # ----------------------------------------------------
        # OTROS CÓDIGOS
        # ----------------------------------------------------

        registrar_intento(
            conn,
            corrida_id,
            equipo,
            pagina,
            intento,
            codigo_http,
            duracion_ms,
            "FALLO_PERMANENTE"
        )

        return {
            "ok": False,
            "agotado": False,
            "autenticacion": False,
            "datos": [],
            "hay_siguiente": False
        }

    return {
        "ok": False,
        "agotado": True,
        "autenticacion": False,
        "datos": [],
        "hay_siguiente": False
    }


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def ejecutar(equipo, puerto):

    corrida_id = str(uuid.uuid4())

    url = (
        f"http://localhost:{puerto}"
        "/medidores/estado"
    )

    print("=" * 60)
    print("T13 - CONECTOR DE INGESTA API")
    print("=" * 60)
    print(f"Equipo: {equipo}")
    print(f"URL: {url}")
    print(f"Corrida: {corrida_id}")
    print("=" * 60)

    conn = conectar_db()

    crear_tablas(conn)

    session = requests.Session()

    # Nunca imprimir el token completo.
    session.headers.update({
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    })

    pagina = 1

    paginas_exitosas = 0
    paginas_incompletas = []
    total_informado = None
    total_cargado = 0

    estado_corrida = "COMPLETA"

    while pagina <= MAX_PAGINAS:

        print(
            f"\nSolicitando página {pagina}..."
        )

        resultado = solicitar_pagina(
            session=session,
            url=url,
            pagina=pagina,
            corrida_id=corrida_id,
            equipo=equipo,
            conn=conn
        )

        # ----------------------------------------------------
        # 401
        # ----------------------------------------------------

        if resultado["autenticacion"]:

            estado_corrida = (
                "ABORTADA_AUTENTICACION"
            )

            print(
                "\nLa corrida fue abortada "
                "por error de autenticación."
            )

            break

        # ----------------------------------------------------
        # PÁGINA AGOTADA
        # ----------------------------------------------------

        if resultado["agotado"]:

            paginas_incompletas.append(pagina)

            estado_corrida = (
                "CON_PAGINAS_INCOMPLETAS"
            )

            print(
                f"Página {pagina} agotó "
                f"los intentos."
            )

            # Se continúa con las siguientes páginas.
            pagina += 1

            continue

        # ----------------------------------------------------
        # FALLO PERMANENTE
        # ----------------------------------------------------

        if not resultado["ok"]:

            paginas_incompletas.append(pagina)

            estado_corrida = (
                "CON_PAGINAS_INCOMPLETAS"
            )

            pagina += 1

            continue

        # ----------------------------------------------------
        # ÉXITO
        # ----------------------------------------------------

        datos = resultado["datos"]

        guardar_medidores(
            conn,
            datos
        )

        paginas_exitosas += 1

        if resultado["total"] is not None:
            total_informado = resultado["total"]

        total_cargado += len(datos)

        print(
            f"Página {pagina} procesada: "
            f"{len(datos)} medidores."
        )

        # ----------------------------------------------------
        # PAGINACIÓN
        # ----------------------------------------------------

        if not resultado["hay_siguiente"]:

            break

        pagina += 1

    else:

        estado_corrida = "TOPE_PAGINAS"

    # ========================================================
    # CONCILIACIÓN
    # ========================================================

    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM stg_estado_medidor
    """)

    conteo_stg = cur.fetchone()[0]

    cur.close()

    if (
        total_informado is not None
        and conteo_stg != total_informado
        and estado_corrida == "COMPLETA"
    ):
        estado_corrida = (
            "CON_PAGINAS_INCOMPLETAS"
        )

    # ========================================================
    # RESULTADO
    # ========================================================

    print("\n")
    print("=" * 60)
    print("RESUMEN DE LA CORRIDA")
    print("=" * 60)

    print(
        f"Equipo:              {equipo}"
    )

    print(
        f"Corrida:             {corrida_id}"
    )

    print(
        f"Páginas procesadas:  {paginas_exitosas}"
    )

    print(
        f"Páginas incompletas: {paginas_incompletas}"
    )

    print(
        f"Total informado:     {total_informado}"
    )

    print(
        f"Total en staging:    {conteo_stg}"
    )

    if total_informado is not None:

        print(
            f"Diferencia:          "
            f"{total_informado - conteo_stg}"
        )

    print(
        f"Estado corrida:      {estado_corrida}"
    )

    print("=" * 60)

    conn.close()
    session.close()


# ============================================================
# ARGUMENTOS
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Conector T13 de ingesta desde API REST"
        )
    )

    parser.add_argument(
        "--equipo",
        required=True,
        choices=[
            "equipo-1",
            "equipo-2",
            "equipo-3",
            "equipo-4",
            "equipo-5",
            "equipo-6"
        ],
        help="Identificador del equipo"
    )

    parser.add_argument(
        "--puerto",
        type=int,
        default=8014,
        help="Puerto de la API simulada"
    )

    args = parser.parse_args()

    ejecutar(
        equipo=args.equipo,
        puerto=args.puerto
    )


if __name__ == "__main__":
    main()
