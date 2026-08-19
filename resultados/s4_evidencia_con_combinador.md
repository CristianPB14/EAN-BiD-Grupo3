# Evidencia: Ejecución CON Combinador

**Comando ejecutado:**
`hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar -D mapreduce.framework.name=local -files /muestra/mapper.py,/muestra/reducer2.py,/muestra/combiner.py -mapper 'python3 mapper.py' -combiner 'python3 combiner.py' -reducer 'python3 reducer2.py' -input /entrada/muestra.csv -output /salida`

**Métricas extraídas de los contadores (Counters):**
*   `Map input records`: 320001
*   `Map output records`: 320000
*   `Combine input records`: 320000
*   `Combine output records`: 500
*   `Reduce shuffle bytes`: 13583

**Conclusión:**
La implementación del combinador (`combiner.py`) actuó como una etapa de pre-agregación local en el nodo mapeador. Logró consolidar 320,000 registros en tan solo 500 antes de la fase de mezcla (shuffle). Esto se tradujo en una caída dramática del tráfico de red, pasando de ~3.4 MB (en la ejecución sin combinador) a escasos 13.5 KB, validando la eficiencia de procesar localmente antes de transmitir en arquitecturas distribuidas.