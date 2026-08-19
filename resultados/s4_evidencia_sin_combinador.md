# Evidencia: Ejecución SIN Combinador

**Comando ejecutado (en modo local por restricción de la imagen base):**
`hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar -D mapreduce.framework.name=local -files /muestra/mapper.py,/muestra/reducer.py -mapper 'python3 mapper.py' -reducer 'python3 reducer.py' -input /entrada/muestra.csv -output /salida`

**Métricas extraídas de los contadores (Counters):**
*   `Map input records`: 320001
*   `Map output records`: 320000
*   `Reduce shuffle bytes`: 3418645