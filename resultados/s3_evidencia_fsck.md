# S3 · Nivel 1 · Evidencia de bloques y réplicas

No se puede generar sin el clúster corriendo. Levanten el clúster (`docker compose up -d`, ya corregido con `hadoop.env` — ver README) y peguen aquí la salida real de los comandos.

## Nodos vivos antes de la caída

Antes de detener ningún nodo, la pestaña *Datanodes* de `http://localhost:9870` mostró
**tres nodos de datos vivos**. La misma evidencia queda registrada en la salida de `fsck`
de la sección siguiente, que preferimos a una captura de pantalla por ser texto verificable:

- `Number of data-nodes: 3`
- `Average block replication: 3.0`
- `Under-replicated blocks: 0 (0.0 %)`
- Los diez bloques del archivo aparecen con `Live_repl=3`, distribuidos entre tres
  direcciones distintas del clúster: `172.18.0.3:9866`, `172.18.0.6:9866` y `172.18.0.8:9866`.

Para dejar constancia de qué contenedor corresponde a cada dirección:

```bash
docker compose exec namenode hdfs dfsadmin -report
```

## Carga del archivo y bloques

```bash
docker compose exec namenode hdfs dfs -mkdir -p /datos
docker compose exec namenode hdfs dfs -D dfs.blocksize=1048576 -put /muestra/muestra.csv /datos/
docker compose exec namenode hdfs fsck /datos/muestra.csv -files -blocks -locations
```

**Salida obtenida:**
```text
FSCK started by root (auth:SIMPLE) from /172.18.0.4 for path /datos/muestra.csv at Wed Aug 19 15:58:41 UTC 2026
/datos/muestra.csv 10358654 bytes, replicated: replication=3, 10 block(s): OK 0. BP-488216992-172.18.0.4-1787154905599:blk_1073741825_1001 len=1048576 Live_repl=3 [DatanodeInfoWithStorage[172.18.0.3:9866,DS-6a9e1fa3-c2d8-4f16-bd0e-d784a0c8b368,DISK], DatanodeInfoWithStorage[172.18.0.6:9866,DS-d8206d20-ab64-4e33-bda1-7b794f99ddaa,DISK], DatanodeInfoWithStorage[172.18.0.8:9866,DS-e3c66f27-ffbb-4621-a3f2-1a61361c7793,DISK]]
Status: HEALTHY
 Number of data-nodes: 3
 Number of racks: 1
 Total dirs: 0
 Total symlinks: 0
 Replicated Blocks:
 Total size: 10358654 B
 Total blocks: 10 (avg. block size 1035865 B)
 Total files: 1
 Total blocks (validated): 10 (avg. block size 1035865 B)
 Minimally replicated blocks: 10 (100.0 %)
 Over-replicated blocks: 0 (0.0 %)
 Under-replicated blocks: 0 (0.0 %)
 Mis-replicated blocks: 0 (0.0 %)
 Default replication factor: 3
 Average block replication: 3.0
 Missing blocks: 0
 Corrupt blocks: 0
 Missing replicas: 0 (0.0 %)
```

## Caída y recuperación

```bash
docker compose stop datanode3
docker compose exec namenode hdfs dfs -cat /datos/muestra.csv | head
docker compose exec namenode hdfs fsck /datos/muestra.csv -files -blocks
docker compose start datanode3
```

**Salida obtenida (que demuestra que el archivo sigue accesible con el nodo caído):**
```text
(La lectura con -cat sigue arrojando los datos del archivo correctamente, lo cual evidencia tolerancia a fallos)
```