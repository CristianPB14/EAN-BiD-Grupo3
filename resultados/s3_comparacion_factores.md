# S3 · Nivel 2 · Comparación de factores de réplica

```bash
# Repetir para factor 1, 2 y 3
docker compose exec namenode hdfs dfs -D dfs.replication=<R> -D dfs.blocksize=1048576 \
  -put /muestra/muestra.csv /datos/muestra_r<R>.csv

docker compose exec namenode hdfs dfs -du -h /datos
docker compose exec namenode hdfs fsck /datos/muestra_r<R>.csv -files -blocks
```

| Factor `R` | Almacenamiento físico medido (`hdfs dfs -du`) | ¿Coincide con volumen lógico × R? | Nodos que tolera |
|---|---|---|---|
| 1 | `COMPLETAR` | `COMPLETAR` | 0 |
| 2 | `COMPLETAR` | `COMPLETAR` | 1 |
| 3 | `COMPLETAR` | `COMPLETAR` | 2 |

> Referencia teórica del caso del acueducto (sesión 3, no reemplaza la medición propia): con 7,8 GB
> lógicos, R=1 → 7,8 GB, R=2 → 15,6 GB, R=3 → 23,4 GB.

## Prueba de pérdida con factor 1

`COMPLETAR` — al detener un nodo que tenga bloques del archivo con `R=1`, ¿qué reporta `fsck`? Debe
mostrar bloques corruptos o faltantes: sin réplica no hay tolerancia. Contrasten contra el mismo
experimento con `R=3`, donde el archivo debe seguir accesible.

## Relación factor–tolerancia, con números propios

`COMPLETAR` — expresen la relación con las cifras que acaban de medir, no como impresión general.
