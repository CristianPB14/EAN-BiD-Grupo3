# S3 · Nivel 1 · Evidencia de bloques y réplicas

> No se puede generar sin el clúster corriendo. Levanten el clúster (`docker compose up -d`, ya
> corregido con `hadoop.env` — ver README) y peguen aquí la salida real de los comandos.

## Nodos vivos antes de la caída

`COMPLETAR` — captura o salida de texto de `http://localhost:9870`, pestaña *Datanodes*.

## Carga del archivo y bloques

```bash
docker compose exec namenode hdfs dfs -mkdir -p /datos
docker compose exec namenode hdfs dfs -D dfs.blocksize=1048576 -put /muestra/muestra.csv /datos/
docker compose exec namenode hdfs fsck /datos/muestra.csv -files -blocks -locations
```

`COMPLETAR` — pegar la salida completa. Debe mostrar el archivo como `HEALTHY`, con varios bloques y
tres réplicas por bloque.

## Caída y recuperación de un nodo

```bash
docker compose stop datanode3
docker compose exec namenode hdfs dfs -cat /datos/muestra.csv | head
docker compose exec namenode hdfs fsck /datos/muestra.csv -files -blocks
docker compose start datanode3
```

`COMPLETAR` — pegar la salida de ambos `fsck` (durante la caída y tras reintegrar el nodo), y
confirmar que el archivo se siguió leyendo mientras el nodo estaba caído.
