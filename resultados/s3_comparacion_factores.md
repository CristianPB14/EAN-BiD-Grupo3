# S3 · Nivel 2 · Comparación de factores de réplica

```bash
# Repetir para factor 1, 2 y 3
docker compose exec namenode hdfs dfs -D dfs.replication=<R> -D dfs.blocksize=1048576 \
  -put /muestra/muestra.csv /datos/muestra_r<R>.csv

docker compose exec namenode hdfs dfs -du -h /datos
docker compose exec namenode hdfs fsck /datos/muestra_r<R>.csv -files -blocks
```

| Archivo | Factor (R) | Tamaño Lógico | Tamaño Físico (Ocupado) | ¿Coincide con Lógico × R? |
| :--- | :---: | :--- | :--- | :--- |
| `muestra_r1.csv` | 1 | 9.9 M | 9.9 M | Sí |
| `muestra_r2.csv` | 2 | 9.9 M | 19.8 M | Sí |
| `muestra_r3.csv` | 3 | 9.9 M | 29.6 M | Sí |

> Referencia teórica del caso del acueducto (sesión 3, no reemplaza la medición propia): con 7,8 GB
> lógicos, R=1 → 7,8 GB, R=2 → 15,6 GB, R=3 → 23,4 GB.

## Prueba de pérdida con factor 1
## Prueba de pérdida con factor 1

Con `dfs.replication=1` cada bloque existe en un único nodo. Detuvimos el nodo que alojaba
los bloques de `muestra_r1.csv` e intentamos leer el archivo. **El fallo es el resultado
esperado y es la lección de la sesión**, no un error de configuración nuestro.

`hdfs dfs -cat` aborta con `java.nio.channels.UnresolvedAddressException`. La traza muestra
la secuencia exacta: el cliente solicita el bloque al `BlockReaderFactory`, este intenta
abrir una conexión TCP contra el único nodo que lo tiene (`nextTcpPeer` → `NetUtils.connect`)
y la dirección no resuelve porque el contenedor está detenido. Sin réplica no hay a quién
más preguntarle, así que el dato queda inaccesible mientras ese nodo esté caído.

El contraste con factor 3 está en `resultados/s3_evidencia_fsck.md`: allí, con un nodo
detenido, `hdfs dfs -cat` siguió devolviendo el contenido del archivo, porque cada bloque
conservaba otras dos copias vivas. **Esa diferencia —una excepción contra una lectura
exitosa sobre el mismo clúster— es toda la justificación del costo de la réplica.**

Traza completa de la ejecución:

```
java.nio.channels.UnresolvedAddressException
        at sun.nio.ch.Net.checkAddress(Net.java:101)
        ...(dejar aquí el volcado que ya tienen)...
```

## Relación factor–tolerancia, con números propios


Con el archivo de 9,9 MB lógicos medido sobre nuestro clúster:

| Factor `R` | Almacenamiento físico | Sobrecosto vs. R=1 | Nodos que tolera |
|---|---|---|---|
| 1 | 9,9 MB  | —      | 0 |
| 2 | 19,8 MB | +100 % | 1 |
| 3 | 29,6 MB | +199 % | 2 |

La relación es **lineal en las dos direcciones y sin economía de escala**: cada copia
adicional cuesta un 100 % del volumen lógico y compra exactamente un nodo más de
tolerancia (`tolerancia = R − 1`). Pasar de R=2 a R=3 cuesta los mismos 9,9 MB que costó
pasar de R=1 a R=2, mientras que el beneficio marginal es siempre el mismo: un nodo.

Llevado al volumen real proyectado en `docs/T3_proyeccion_almacenamiento.md`, donde SECOP II
alcanza **0,5468 GB lógicos a doce meses**, la decisión de factor 3 significa 1,6405 GB
físicos frente a los 0,5468 GB de factor 1: **1,09 GB adicionales de disco a cambio de
tolerar la caída simultánea de dos nodos**. Ese es el número que sostiene la recomendación
del reto de negocio, y a esta escala el costo es marginal frente a la garantía.
