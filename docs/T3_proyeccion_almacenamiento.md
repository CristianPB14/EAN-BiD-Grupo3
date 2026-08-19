# T3 · Proyección de almacenamiento con tres factores de réplica

**Sesión 3 · Sistemas de archivos distribuidos**

## 0. Consolidación del equipo

Se eligió **SECOP II** como fuente única del proyecto. La decisión se basa en su relevancia para el análisis de la contratación pública y la transparencia estatal. Técnicamente, cuenta con múltiples variables categóricas (departamento, tipo de contrato, estado) numéricas (cuantía del contrato) y fechas estructuradas que permitirán realizar agrupaciones, cálculos de agregación y un particionamiento temporal eficiente en la arquitectura de datos posterior.

## 1. Fórmulas de la sesión

- Almacenamiento físico = volumen lógico × factor de réplica `R`
- Número de bloques = tamaño del archivo ÷ tamaño de bloque, redondeado hacia arriba
- Tolerancia = `R − 1` nodos caídos simultáneamente sin perder dato

## 2. Proyección a doce meses

Partiendo de la tasa de crecimiento mensual `g = 5%` (0.05) y un tamaño inicial `S0 = 0.3045 GB` medidos en la ficha T1 del equipo, el volumen proyectado a 12 meses es `S0 · (1+g)^12` = **0.5468 GB**.

| Factor de réplica `R` | Almacenamiento físico proyectado | Nodos que puede perder |
|---|---|---|
| 1 | **0.5468 GB** | 0 · sin tolerancia |
| 2 | **1.0937 GB** | 1 |
| 3 | **1.6405 GB** | 2 |

## 3. Tamaño de bloque

Usando el valor real de HDFS (128 MB):

- **Número de bloques a 12 meses:** 5 bloques.
- **Tensión estructural del sistema:** Existe un equilibrio crítico al definir este valor. Si configuramos bloques muy grandes frente a archivos pequeños, desperdiciamos espacio y anulamos la capacidad de procesamiento en paralelo. Por el contrario, si fragmentamos en bloques muy pequeños, multiplicamos drásticamente la cantidad de metadatos, lo que podría saturar la memoria RAM del nodo maestro (NameNode) y colapsar el control del clúster.

## 4. Decisión y justificación

- **Factor de réplica elegido:** 3
- **Por qué:** Tratándose de expedientes de contratación estatal (SECOP II), la información posee un carácter probatorio y de auditoría crítico. Aunque los datos puedan volver a descargarse del portal oficial en caso de desastre, una pérdida local paralizaría cualquier proceso de análisis en curso. El costo físico de triplicar el almacenamiento (pasando de ~0.55 GB a apenas 1.64 GB proyectados) es marginal y económicamente viable frente a la garantía absoluta de tolerar la caída simultánea de hasta dos servidores.
- **Tamaño de bloque elegido:** 128 MB
- **Por qué:** El volumen lógico proyectado a un año (0.5468 GB) es relativamente bajo, generando únicamente 5 bloques bajo este estándar. Reducir el tamaño del bloque aumentaría el tráfico de metadatos hacia el NameNode sin ofrecer una mejora significativa en el paralelismo de las consultas, por lo que el valor por defecto es la decisión más estable.

## 5. Evidencia práctica

Las pruebas físicas de tolerancia a fallos, la comprobación del particionamiento de bloques (`fsck`) y la medición en disco de los distintos factores de réplica (`-du -h`) ejecutadas sobre nuestro clúster local se encuentran documentadas exhaustivamente en los siguientes archivos de resultados:
* `resultados/s3_evidencia_fsck.md`
* `resultados/s3_comparacion_factores.md`