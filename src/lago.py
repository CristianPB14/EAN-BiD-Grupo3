import os
import boto3
from dotenv import load_dotenv

# Cargamos las contraseñas desde tu archivo .env
load_dotenv()

def cliente():
    """Cliente S3 apuntando al MinIO local.
    OJO: puerto 9000 (API), no 9001 (consola)."""
    return boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
        region_name="us-east-1",
    )

def crear_cubos(s3, cubos=("cruda", "refinada", "consolidada")):
    for cubo in cubos:
        try:
            s3.create_bucket(Bucket=cubo)
            print("Cubo creado:", cubo)
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print("Ya existe:", cubo)

if __name__ == "__main__":
    s3 = cliente()
    print("Conectando a MinIO...")
    crear_cubos(s3)

    # Comprobación conceptual del nivel 1: 
    # Crear una "ruta" que en realidad es solo parte del nombre del archivo
    clave = "secop/anio=2026/mes=08/dia=19/secop_sample.csv"
    print(f"\nSubiendo archivo de prueba como: {clave}")
    
    # Subimos el archivo crudo de SECOP II al cubo 'cruda'
    s3.upload_file("data/raw/secop_sample.csv", "cruda", clave)

    # Le pedimos a MinIO que busque todo lo que empiece por un prefijo
    print("\nBuscando objetos por prefijo 'secop/anio=2026/':")
    resp = s3.list_objects_v2(Bucket="cruda", Prefix="secop/anio=2026/")
    for obj in resp.get("Contents", []):
        print(f" -> {obj['Key']} | Tamaño: {obj['Size']} bytes")

    # --- PASO 3: PRUEBA DE VERSIONADO ---
    print("\n--- INICIANDO PRUEBA DE VERSIONADO ---")
    
    # 1. Activamos el versionado en el cubo cruda
    s3.put_bucket_versioning(
        Bucket="cruda",
        VersioningConfiguration={"Status": "Enabled"},
    )
    print("Versionado activado en el cubo 'cruda'.")

    # 2. Simulamos un error: alguien sobrescribe el archivo en LA MISMA CLAVE
    print("Sobrescribiendo el archivo para generar una nueva versión...")
    s3.upload_file("data/raw/secop_sample.csv", "cruda", clave)

    # 3. Listamos el historial para demostrar que nada se borró
    print("\nHistorial de versiones en el sistema:")
    versiones = s3.list_object_versions(Bucket="cruda", Prefix=clave).get("Versions", [])
    for v in versiones:
        print(f"ID Versión: {v['VersionId']} | ¿Es la actual?: {v['IsLatest']} | Fecha: {v['LastModified']}")