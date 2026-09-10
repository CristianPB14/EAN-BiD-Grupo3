Análisis de Cumplimiento del Notebook T8_arquitectura.ipynb frente a los Criterios de Evaluación
1. Alcance del documento

El presente análisis describe la correspondencia entre el código implementado en el notebook T8_arquitectura.ipynb y los seis criterios de evaluación establecidos para el nivel "Sobresaliente". Se identifica, para cada criterio, el grado de cobertura que ofrece el código y los elementos adicionales requeridos fuera de este.

2. Derivación de la arquitectura desde el paradigma 

Cobertura del código: Parcial / indirecta.

El notebook no argumenta el paradigma arquitectónico en sí, pero genera evidencia cuantitativa (tamaño del dataset, número de bloques HDFS, volumen bajo réplica) que puede emplearse como insumo de justificación. La derivación explícita del paradigma de T7 y la coherencia requisito por requisito deben desarrollarse en el informe narrativo, apoyándose en estas cifras cuando corresponda (por ejemplo, al justificar la necesidad de procesamiento distribuido según el volumen calculado).

Pendiente fuera del código: Redacción argumentativa que conecte cada requisito del paradigma con la decisión arquitectónica tomada.

3. Justificación y descarte de alternativas 

Cobertura del código: Indirecta.

Las métricas de almacenamiento y escalabilidad (crecimiento del dataset, costo de réplica) constituyen evidencia de apoyo para argumentar la escala organizativa como criterio de descarte (por ejemplo, de una arquitectura de malla). El código no declara explícitamente ningún costo aceptado ni descarta alternativas; esta declaración es responsabilidad del texto que acompaña al notebook.

Pendiente fuera del código: Declaración explícita del costo aceptado de la arquitectura elegida y del argumento de escala usado para descartar la malla.

4. Corrección de la notación C4 

Cobertura del código: Nula.

Este criterio corresponde a artefactos gráficos independientes (diagramas de Contexto y Contenedor) que no se generan en este notebook. Los resultados de almacenamiento aquí calculados pueden usarse como contenido de apoyo dentro de un contenedor del diagrama (por ejemplo, un contenedor de "almacenamiento distribuido" anotado con su capacidad estimada), pero la construcción y corrección de la notación C4 debe realizarse con una herramienta de diagramación externa.

Pendiente fuera del código: Elaboración de los diagramas C4 con un nivel por diagrama, flechas dirigidas y etiquetadas, sin confundir "contenedor" (unidad desplegable en C4) con "contenedor" (Docker).

5. Consolidación de T1 a T8 

Cobertura del código: Potencial, condicionada a la redacción.

El notebook puede integrarse como el punto de cierre del relato de T1 a T8, aportando las métricas de almacenamiento y formato que dan continuidad a las tareas previas (perfilamiento de datos, procesamiento tipo MapReduce, etc.). El código por sí solo no cita ni referencia las tareas anteriores; esta vinculación debe hacerse explícita en el texto.

Pendiente fuera del código: Redacción que cite expresamente qué insumo de cada tarea previa (T1–T7) se retoma o dimensiona en T8.

6. Decisiones y compromisos fundamentados 

Cobertura del código: Alta / directa.

Este es el criterio con mayor respaldo directo del notebook. Se identifican los siguientes resultados calculados:

Elemento	Cálculo realizado en el código
Tamaño base del dataset	df.memory_usage(deep=True).sum(), convertido a MiB
Bloques HDFS requeridos	math.ceil(tamaño_mib / BLOCK_SIZE_MIB)
Almacenamiento total por réplica	Tamaño base × factor de réplica (1, 2, 3)
Comparación de formatos	Tiempo de lectura CSV vs. tiempo de escritura Parquet (time.perf_counter())
Eficiencia de codec	Porcentaje de reducción de tamaño CSV vs. Parquet (os.path.getsize())

Estas mediciones constituyen la base cuantitativa para fundamentar decisiones sobre almacenamiento, codec de compresión y modelo de procesamiento. El compromiso CAP no se calcula en el código y debe declararse por separado en el texto, apoyado en estas cifras cuando sea pertinente.

Pendiente fuera del código: Declaración explícita del compromiso CAP (Consistencia, Disponibilidad, Tolerancia a particiones) y su relación con la arquitectura elegida.

7. Comunicación técnica y citación APA 7 

Cobertura del código: Nula.

El código no incluye citas ni definiciones de glosario. Sin embargo, produce conceptos técnicos que deben ser citados y definidos en el informe final:

Bloque HDFS y su tamaño estándar (128 MiB)
Factor de réplica
Formato columnar (Parquet)
Codec de compresión

Pendiente fuera del código: Citación en formato APA 7 de fuentes oficiales (ej. documentación de Apache Hadoop, Apache Parquet) y alimentación del glosario con los términos técnicos listados.
