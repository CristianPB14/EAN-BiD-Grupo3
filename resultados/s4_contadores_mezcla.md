# S4 · Contadores del trabajo MapReduce

> Requiere el clúster extendido corriendo (`docker compose up -d`, con `resourcemanager`,
> `nodemanager` y `historyserver` ya incluidos en `docker-compose.yml`). No se puede fabricar sin
> ejecutar el trabajo real.

## Ejecución sin combinador (nivel 1)

```bash
docker compose exec namenode hdfs dfs -mkdir -p /entrada
docker compose exec namenode hdfs dfs -put /muestra/muestra.csv /entrada/
docker compose exec namenode bash -c '
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /muestra/mapper.py,/muestra/reducer.py \
  -mapper mapper.py -reducer reducer.py \
  -input /entrada/muestra.csv -output /salida'
```

`COMPLETAR` — pegar los contadores del trabajo (registros de entrada, de salida, **bytes de
mezcla**), disponibles en la salida de la ejecución o en `http://localhost:8188`.

## Ejecución con combinador (nivel 2)

```bash
docker compose exec namenode bash -c '
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /muestra/mapper.py,/muestra/combiner.py,/muestra/reducer2.py \
  -mapper mapper.py -combiner combiner.py -reducer reducer2.py \
  -input /entrada/muestra.csv -output /salida2'
```

`COMPLETAR` — pegar los contadores. Comparar con la ejecución anterior:

| Métrica | Sin combinador | Con combinador | Reducción |
|---|---|---|---|
| Bytes de mezcla | `COMPLETAR` | `COMPLETAR` | `COMPLETAR` % |
| Resultado por sector idéntico al nivel 1 | — | `COMPLETAR` (sí/no, verificado) | — |

## Agregación propia (nivel 3)

`COMPLETAR` — ver `docs/T4_agregacion_mapreduce.md`, sección 3, para la predicción y el contraste con
lo medido.
