# S4 · Contadores del trabajo MapReduce

> Requiere el clúster extendido corriendo (`docker compose up -d`, con `resourcemanager`, `nodemanager` y `historyserver` ya incluidos en `docker-compose.yml`). No se puede fabricar sin ejecutar el trabajo real.

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

**Métricas extraídas de los contadores (Counters):**
*   `Map input records`: 320001
*   `Map output records`: 320000
*   **`Reduce shuffle bytes`**: 3418645

## Ejecución con combinador (nivel 2)

```bash
docker compose exec namenode bash -c '
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /muestra/mapper.py,/muestra/combiner.py,/muestra/reducer2.py \
  -mapper mapper.py -combiner combiner.py -reducer reducer2.py \
  -input /entrada/muestra.csv -output /salida2'
```

**Métricas extraídas de los contadores (Counters):**
*   `Map input records`: 320001
*   `Map output records`: 320000
*   `Combine input records`: 320000
*   `Combine output records`: 500
*   **`Reduce shuffle bytes`**: 13583

| Métrica | Sin combinador | Con combinador | Reducción |
|---|---|---|---|
| Bytes de mezcla | 3418645 | 13583 | 99.60 % |
| Resultado por sector idéntico al nivel 1 | — | Sí (verificado mediante comando diff = IDENTICOS) | — |

## Agregación propia (nivel 3)

Se ejecutó exitosamente el diseño propio sobre la fuente SECOP II. Los detalles de la predicción, ejecución y contraste de la mezcla están documentados en la sección 3 del archivo `docs/T4_agregacion_mapreduce.md`.