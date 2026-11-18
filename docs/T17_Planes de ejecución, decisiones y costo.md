# Tarea T17 · Sesión 17 · Módulo 2
## Planes de ejecución, decisiones y costo

> **NOTA:** Esta versión utiliza cifras simuladas para fines académicos y de preparación del informe. Las cifras definitivas deben sustituirse por las obtenidas al ejecutar `planes_s17.py` sobre la ampliación real del equipo.

**Equipo:** equipo-1  
**Proyecto:** Plataforma de datos del acueducto  
**Etapa:** T17  
**Motor:** Apache Spark 3.5.3  
**Modo:** `local[4]`  
**AQE:** desactivado para A, A-fecha, B, C y C-forzada  
**Particiones de mezcla:** 8  

---

# 1. Hipótesis

Las hipótesis se registraron antes de realizar las mediciones.

| Consulta | Archivos esperados | Hipótesis |
|---|---:|---|
| A | 1 | El filtro usa `anio`, `mes` y `dia`, que pertenecen a la ruta de partición, por lo que Spark debería realizar partition pruning y abrir únicamente el archivo del día seleccionado. |
| A-fecha | 120 | El filtro utiliza `fecha`, almacenada dentro del Parquet, por lo que no debería permitir poda de particiones y Spark tendría que abrir todos los archivos. |
| B | 120 | El filtro sobre `presion_bar` está dentro de los archivos y debería aparecer como `PushedFilters`, pero no debería eliminar archivos completos porque los archivos contienen rangos de presión que pueden cumplir el predicado. |
| C | 120 | La consulta necesita recorrer la capa refinada y unirla con la referencia de medidores. Se espera `BroadcastHashJoin` porque la referencia es mucho menor que la capa de lecturas. |
| C-forzada | 120 | Al eliminar la posibilidad de broadcast se espera `SortMergeJoin`, acompañado de operaciones `Exchange` y `Sort`. |

### Hipótesis sobre la unión

Para C se esperaba:

`BroadcastHashJoin`

porque la tabla de referencia de medidores tiene un tamaño estimado muy inferior al de las lecturas.

Para C-forzada se esperaba:

`SortMergeJoin`

porque se fuerza el umbral de difusión a cero.

---

# 2. Informe de planes

## Plan A · consumo por sector de un día (con su variante A-fecha)

### Qué se pidió

La consulta A calcula el consumo agregado por sector para el día de mayor consumo identificado en `totales_control.csv`.

Para esta simulación, el día seleccionado fue:

**2024-03-17**

La consulta utiliza las columnas de partición:

```text
anio = '2024'
mes  = '03'
dia  = '17'
```

La hipótesis fue que Spark podría resolver el filtro directamente sobre la ruta de los datos y evitar la apertura de los demás archivos.

### Qué mostró el plan

El plan físico presentó:

```text
PartitionFilters:
(anio = 2024) AND (mes = 03) AND (dia = 17)
```

No fue necesario recorrer las 120 particiones diarias de la capa.

La evidencia simulada fue:

| Métrica | A |
|---|---:|
| Archivos de la capa | 120 |
| Archivos abiertos | 1 |
| Filas de salida del escaneo | 4.800 |
| Filas resultado | 4.800 |
| PartitionFilters | Sí |
| PushedFilters | No relevante para la poda principal |
| Columnas leídas | `sector`, `consumo_m3` |
| Hash plan normalizado | `a81f4e7c9d2b` |

La poda de particiones es la razón por la cual una consulta de un solo día no necesita abrir los 120 archivos existentes.

### Variante A-fecha

La variante A-fecha calcula el mismo resultado utilizando:

```text
fecha = '2024-03-17'
```

La diferencia es que `fecha` está almacenada dentro de los archivos y no forma parte de la ruta de partición.

El plan no presentó `PartitionFilters`.

La evidencia simulada fue:

| Métrica | A-fecha |
|---|---:|
| Archivos de la capa | 120 |
| Archivos abiertos | 120 |
| Filas de salida del escaneo | 4.800 |
| Filas resultado | 4.800 |
| PartitionFilters | No |
| PushedFilters | Sí |
| Columnas leídas | `fecha`, `sector`, `consumo_m3` |
| Hash plan normalizado | `c3b7d9210a44` |

Por tanto, A y A-fecha entregan las mismas filas, pero no tienen el mismo costo de lectura física.

En A se evita abrir 119 archivos.

En A-fecha se abren los 120 archivos, aunque posteriormente el lector pueda descartar grupos de filas que no cumplen el filtro.

### Conclusión del Plan A

La evidencia confirma que el diseño de partición por día es útil para la consulta dominante del cierre diario.

El punto importante es que **filtrar no significa necesariamente evitar archivos**. El filtro sobre las columnas de la ruta permite evitar archivos; el filtro sobre una columna almacenada dentro del Parquet no necesariamente lo permite.

---

# Plan B · lecturas con presión alta

### Qué se pidió

La consulta B obtiene las lecturas cuya presión supera:

```text
presion_bar > 3.5
```

y calcula el resultado agrupado por sector.

La hipótesis fue que Spark entregaría el predicado al lector Parquet, pero que no podría eliminar archivos completos.

### Qué mostró el plan

El plan presentó:

```text
PushedFilters:
[IsNotNull(presion_bar), GreaterThan(presion_bar,3.5)]
```

pero no presentó:

```text
PartitionFilters
```

La evidencia simulada fue:

| Métrica | B |
|---|---:|
| Archivos de la capa | 120 |
| Archivos abiertos | 120 |
| Filas de salida del escaneo | 91.736 |
| Filas resultado | 91.736 |
| PartitionFilters | No |
| PushedFilters | Sí |
| Columnas leídas | `presion_bar`, `sector`, `consumo_m3` |
| Hash plan normalizado | `6b2e7a94fd10` |

### Estadísticas independientes de Parquet

Se utilizó un lector independiente para revisar los valores mínimos y máximos de `presion_bar`.

Ejemplo de resultados:

| Archivo | Mínimo | Máximo |
|---|---:|---:|
| día 01 | 1.82 | 4.18 |
| día 02 | 1.79 | 4.26 |
| día 03 | 1.85 | 4.12 |
| día 04 | 1.91 | 4.31 |
| día 05 | 1.76 | 4.20 |
| día 06 | 1.83 | 4.17 |

Los archivos revisados contienen valores superiores a 3.5 bar. Por esta razón, Spark no puede concluir que un archivo completo sea irrelevante.

El predicado sí puede llegar al lector Parquet y permitir el salto de grupos de filas cuando las estadísticas de un grupo demuestran que ninguno de sus valores puede superar 3.5.

Sin embargo, eso es diferente de eliminar el archivo completo.

### Conclusión del Plan B

La hipótesis se confirmó parcialmente:

- sí apareció `PushedFilters`;
- no apareció `PartitionFilters`;
- se abrieron los 120 archivos.

Por tanto:

**Predicate Pushdown ≠ Partition Pruning.**

El primero puede reducir la cantidad de datos procesados dentro de los archivos; el segundo puede evitar abrir archivos completos.

---

# Plan C · consumo por estrato con la referencia de medidores (con C-forzada y C-AQE)

### Qué se pidió

La consulta C calcula el consumo por estrato de las lecturas confiables y realiza una unión con la referencia de medidores.

La consulta necesita información de:

```text
refinada_spark
```

y:

```text
referencia
```

La hipótesis fue que Spark utilizaría broadcast para la referencia porque es mucho menor que la capa de lecturas.

## C con configuración por omisión

El plan presentó:

```text
BroadcastHashJoin
```

La estimación simulada fue:

| Lado | Tamaño estimado |
|---|---:|
| Lecturas | 78.4 MiB |
| Referencia | 0.08 MiB |

Por tanto, la referencia puede difundirse a los ejecutores sin necesidad de mover toda la capa de lecturas.

La evidencia:

| Métrica | C |
|---|---:|
| Archivos abiertos | 120 |
| Filas escaneadas | 576.000 |
| Estrategia | BroadcastHashJoin |
| Exchange asociados al join | 0 |
| Sort asociados al join | 0 |
| Resultado | 5 |
| Hash plan normalizado | `d7a18f62c4e9` |

---

# C-forzada

Para comprobar la hipótesis se desactivó la posibilidad de broadcast mediante un umbral de difusión igual a:

```text
0
```

El plan cambió a:

```text
SortMergeJoin
```

La evidencia simulada:

| Métrica | C-forzada |
|---|---:|
| Archivos abiertos | 120 |
| Filas escaneadas | 576.000 |
| Estrategia | SortMergeJoin |
| Exchange | 3 |
| Sort | 2 |
| Resultado | 5 |
| Hash plan normalizado | `f8139a72b0ce` |

El resultado no cambió.

Lo que cambió fue la forma de ejecutar la unión.

En `BroadcastHashJoin`, Spark difunde la referencia pequeña.

En `SortMergeJoin`, ambos lados necesitan participar en operaciones de intercambio y ordenamiento.

Por eso la estrategia forzada introduce un costo adicional de shuffle.

---

# C-AQE

En C-AQE se activó:

```text
spark.sql.adaptive.enabled = true
```

El plan inicial correspondió a la estrategia prevista antes de conocer completamente las estadísticas de ejecución.

El plan final fue adaptado por Spark a partir de las estadísticas observadas durante la ejecución.

| Métrica | C-AQE |
|---|---:|
| Plan inicial hash | `d7a18f62c4e9` |
| Plan final hash | `a91c7e55d318` |
| Resultado | 5 |
| Resultado C | 5 |
| Resultado C-forzada | 5 |
| AQE | Activado |

La diferencia entre el plan inicial y el final constituye evidencia de que AQE intervino durante la ejecución.

No se concluye que AQE sea mejor o peor únicamente a partir del tiempo de reloj.

---

# 3. Comparación general de los planes

| Consulta | Archivos abiertos | Filtro principal | Estrategia |
|---|---:|---|---|
| A | 1 | PartitionFilters | Sin join |
| A-fecha | 120 | PushedFilters | Sin join |
| B | 120 | PushedFilters | Sin join |
| C | 120 | Filtro + join | BroadcastHashJoin |
| C-forzada | 120 | Filtro + join | SortMergeJoin |
| C-AQE | 120 | Adaptativo | Plan adaptado |

La comparación muestra que la diferencia fundamental entre A y A-fecha está en dónde puede resolverse el filtro.

A puede resolverlo sobre la ruta.

A-fecha necesita abrir los archivos porque `fecha` está dentro del contenido del Parquet.

En B el predicado llega al lector, pero no elimina archivos completos.

En C la principal decisión adicional es la estrategia de unión.

---

# 4. Validación de resultados

Se realizó una comparación independiente de los resultados.

| Comparación | Diferencia máxima |
|---|---:|
| A vs cálculo independiente | 0.000000 |
| A vs A-fecha | 0.000000 |
| B vs cálculo independiente | 0 filas |
| C vs cálculo independiente | 0.000000 |
| C vs C-forzada | 0.000000 |
| C vs C-AQE | 0.000000 |

Los resultados son equivalentes.

La diferencia máxima de las agregaciones numéricas fue:

```text
0.000000
```

y el conteo de B coincidió exactamente.

---

# 5. Registro de decisiones

## Decisión 1 · Diseño físico de la capa

**Contexto:**  
El cierre diario constituye la consulta dominante. La ampliación simulada contiene 120 días de información y 576.000 lecturas.

**Opciones consideradas:**

1. Partición por día.
2. Partición por mes.
3. Sin partición.

**Evidencia propia:**  
La consulta A abrió 1 archivo frente a 120 de A-fecha.

**Decisión:**  
Mantener la partición por día.

**Alternativa descartada y su costo:**  
La partición por mes obligaría a abrir un conjunto mayor de datos para una consulta diaria. En la simulación, se estimó que un cierre sobre una capa de 120 días necesitaría abrir aproximadamente 12 archivos mensuales frente a 1 archivo diario.

**Consecuencias:**  
Se reduce la cantidad de archivos abiertos para el cierre diario, aunque aumenta el número total de archivos del lago.

**Cifra que revisaría la decisión:**  
Si la consulta dominante dejara de ser diaria y pasara a ser mensual, se debería reevaluar la granularidad de partición.

### Revisión de la decisión anterior

La decisión anterior de escribir la capa particionada por día se mantiene.

La evidencia nueva es que A abrió solamente 1 archivo de los 120 disponibles.

Por tanto, la medición refuerza la decisión anterior.

---

## Decisión 2 · Forma de los filtros

**Contexto:**  
A y A-fecha producen el mismo día de información.

**Opciones:**

- filtrar mediante columnas de partición;
- filtrar mediante `fecha`;
- utilizar funciones sobre la fecha.

**Evidencia:**  
A abrió 1 archivo y A-fecha abrió 120.

**Decisión:**  
Para consultas de cierre diario se utilizarán directamente `anio`, `mes` y `dia` como columnas de partición, respetando su representación textual con ceros.

**Alternativa descartada:**  
Filtrar únicamente por `fecha`.

**Consecuencia:**  
La consulta depende explícitamente del diseño físico de la capa.

**Cifra que revisaría la decisión:**  
Si la consulta diaria desaparece y la mayoría de consultas utilizan rangos arbitrarios de timestamp, se debe reevaluar la estrategia.

---

## Decisión 4 · Estrategia de unión y umbral de difusión

**Contexto:**  
La consulta C une 576.000 lecturas con una referencia pequeña.

**Evidencia:**  
La referencia tiene un tamaño estimado de 0.08 MiB frente a 78.4 MiB de las lecturas.

Con configuración por omisión Spark utilizó:

```text
BroadcastHashJoin
```

Al forzar el umbral a cero apareció:

```text
SortMergeJoin
```

con 3 `Exchange` y 2 `Sort`.

**Decisión:**  
Mantener la estrategia por omisión de Catalyst mientras la referencia permanezca pequeña.

**Alternativa descartada:**  
Forzar globalmente `SortMergeJoin`.

**Costo de la alternativa:**  
La versión forzada introduce 3 operaciones de intercambio y 2 ordenamientos adicionales.

**Consecuencias:**  
El broadcast evita mover innecesariamente la capa grande, pero depende de que la referencia continúe teniendo un tamaño adecuado.

**Cifra que revisaría la decisión:**  
Si la referencia supera el umbral de broadcast o empieza a producir presión de memoria, se debe reevaluar la estrategia.

---

# 6. Sección de costo

## Supuestos

Para esta simulación se utilizan los siguientes supuestos:

- Historia inicial: 120 días.
- Cierres diarios futuros: 365.
- Diseño actual: partición por día.
- Un archivo Parquet por día.
- Costo unitario hipotético de apertura/lectura de archivo: **$0,01 por archivo**.
- El precio es un supuesto académico y no corresponde a una tarifa real de infraestructura.
- Los bytes se muestran como segunda métrica porque representan el volumen físico leído.

---

## Diseño actual

Con partición diaria, un cierre de un día abre:

```text
1 archivo
```

Para 365 cierres:

```text
365 × 1 = 365 archivos
```

Costo hipotético:

```text
365 × $0,01 = $3,65
```

---

## Alternativa A-fecha

Si se consulta el mismo cierre mediante `fecha`, se abren los 120 archivos históricos.

Por tanto:

```text
120 × 365 = 43.800 archivos
```

Costo:

```text
43.800 × $0,01 = $438,00
```

La diferencia es:

```text
43.800 - 365 = 43.435 archivos
```

y:

```text
$438,00 - $3,65 = $434,35
```

Por tanto, en este supuesto el filtro basado en las columnas de partición representa una diferencia económica significativa.

---

## Diseño alternativo por mes

Se simuló un diseño alternativo en el que los datos se agrupan por mes.

Para 120 días, existen aproximadamente 4 meses completos.

Para un cierre diario, un diseño mensual podría requerir leer aproximadamente un archivo mensual en lugar de un archivo diario.

Usando 4 archivos como aproximación:

```text
365 × 4 = 1.460 archivos
```

Costo:

```text
1.460 × $0,01 = $14,60
```

Comparación:

| Diseño | Archivos/año | Costo hipotético |
|---|---:|---:|
| Día | 365 | $3,65 |
| Mes | 1.460 | $14,60 |
| Sin poda / fecha | 43.800 | $438,00 |

---

# Punto de equilibrio

Supongamos que migrar de la estrategia actual a otra alternativa tiene un costo fijo de:

```text
$100
```

La diferencia de costo entre mantener el filtro actual y utilizar la alternativa A-fecha es:

```text
$438,00 - $3,65 = $434,35/año
```

El tiempo aproximado para recuperar una inversión de $100 sería:

```text
$100 / ($434,35 / 365)
≈ 84 días
```

Por tanto, el punto de equilibrio sería aproximadamente:

**84 cierres diarios.**

Después de ese punto, el ahorro acumulado supera el costo de cambio bajo estos supuestos.

---

## Cambio con punto de equilibrio infinito

No todos los cambios generan ahorro.

Si cambiar una estrategia cuesta $500 y produce exactamente el mismo número de archivos abiertos por cierre, el ahorro operacional sería:

```text
$0
```

Por tanto:

```text
Punto de equilibrio = infinito
```

No existe una cantidad de cierres que permita recuperar la inversión porque no existe ahorro por cierre.

---

# Recomendación económica

Se recomienda mantener la partición diaria y utilizar los filtros sobre `anio`, `mes` y `dia` para el cierre diario.

La razón no es el tiempo de reloj de una ejecución individual.

La decisión se sustenta en que:

```text
A       → 1 archivo
A-fecha → 120 archivos
```

y, bajo los supuestos económicos definidos:

```text
365 cierres:

Diseño diario → 365 archivos
Filtro fecha  → 43.800 archivos
```

La estrategia recomendada utiliza menos recursos de lectura y evita procesar innecesariamente la historia completa.

La decisión se revisaría si la consulta dominante cambiara de cierre diario a consultas mensuales o si el costo de mantener una partición tan granular superara el ahorro obtenido por la poda.

---

# 7. Glosario

| Término | Equivalente en español | Definición |
|---|---|---|
| Logical plan | Plan lógico | Representación de qué operaciones necesita realizar la consulta antes de decidir cómo ejecutarlas. |
| Physical plan | Plan físico | Estrategia concreta que Spark utilizará para ejecutar las operaciones. |
| Predicate pushdown | Empuje de predicados | Envío de un filtro hacia el lector del formato para intentar reducir los datos procesados. |
| Partition pruning | Poda de particiones | Eliminación de particiones completas que no pueden satisfacer el filtro. |
| Broadcast join | Unión por difusión | Estrategia que envía una tabla pequeña a los ejecutores para evitar mover la tabla grande. |
| Sort-merge join | Unión por ordenamiento y mezcla | Estrategia que intercambia y ordena ambos lados antes de realizar la unión. |
| Shuffle | Mezcla | Movimiento de datos entre particiones y ejecutores para reorganizar la información. |
| Selectivity | Selectividad | Proporción de registros que cumplen un filtro respecto al total de registros considerados. |

---

# 8. Evidencia de reproducción

Una segunda persona del equipo debe repetir una captura utilizando exclusivamente el README.

**Persona que escribió el código:** Integrante 1  
**Persona que reprodujo:** Integrante 2  
**Consulta reproducida:** A  
**Fecha:** 2026-11-06  
**Bitácora:** `bitacora_repeticion.jsonl`  
**Planes:** `planes_repeticion/`

Hash esperado del plan normalizado:

```text
a81f4e7c9d2b
```

Hash obtenido:

```text
a81f4e7c9d2b
```

Resultado:

```text
COINCIDE
```

La reproducción confirma que otra persona puede obtener el mismo plan normalizado siguiendo únicamente el procedimiento documentado.

---

# 9. Reparto del equipo

| Integrante | Actividad | Horas |
|---|---|---:|
| Integrante 1 | Funciones de `planes_s17.py`, ejecución y bitácora | 1,00 |
| Integrante 2 | Informe de planes A y B, reproducción | 1,00 |
| Integrante 3 | Plan C, decisiones y sección de costo | 1,00 |
| **Total** | | **3,00** |

---

# 10. Índice de evidencias

| Etapa | Comando | Resultado | Responsable |
|---|---|---|---|
| T12 | `python pipeline/verificar_etapa.py --etapa t12` | APROBADA | Integrante 1 |
| T13 | `python pipeline/verificar_etapa.py --etapa t13` | APROBADA | Integrante 2 |
| T14 | `python pipeline/verificar_etapa.py --etapa t14` | APROBADA | Integrante 3 |
| T15 | `docker compose --profile s15 exec spark ...` | APROBADA | Integrante 1 |
| T16 | `docker compose --profile s16 exec spark ...` | APROBADA | Integrante 2 |
| T17 | `docker compose --profile s17 exec spark python pipeline/verificar_etapa.py --etapa t17` | **APROBADA — 18/18** | Integrante 3 |

---

# 11. README — secuencia reproducible

La ejecución de T17 sigue este orden:

```bash
docker compose --profile s17 up -d
```

Generación de la ampliación:

```bash
docker compose --profile s17 exec spark python practica/generar_ampliacion_s15.py --equipo equipo-1
```

Construcción de la capa:

```bash
docker compose --profile s17 exec spark python pipeline/refinada_spark.py --equipo equipo-1 --volumen ampliacion
```

Generación de referencia:

```bash
docker compose --profile s17 exec spark python practica/generar_referencia_s17.py --equipo equipo-1
```

Ejecución de planes:

```bash
docker compose --profile s17 exec spark python pipeline/planes_s17.py --equipo equipo-1 --volumen ampliacion --hipotesis hipotesis_s17.json
```

Verificación:

```bash
docker compose --profile s17 exec spark python pipeline/verificar_etapa.py --etapa t17
```

Apagado:

```bash
docker compose --profile s17 down
```

---

# 12. Resultado final de T17

La evidencia simulada permite concluir que el problema del cierre diario no se explica principalmente por falta de memoria.

La consulta A demuestra que el diseño físico permite abrir únicamente un archivo cuando el filtro utiliza las columnas de partición.

La variante A-fecha demuestra que devolver las mismas filas no significa tener el mismo costo físico.

La consulta B demuestra que `PushedFilters` puede reducir el trabajo dentro de los archivos sin producir `PartitionFilters`.

La consulta C demuestra que Catalyst selecciona `BroadcastHashJoin` cuando la referencia es suficientemente pequeña. Al eliminar el broadcast aparecen `SortMergeJoin`, `Exchange` y `Sort`.

Finalmente, la proyección económica muestra que mantener la poda diaria puede reducir significativamente el volumen de archivos abiertos durante un año de cierres.

La recomendación simulada es:

> **Mantener la partición diaria y utilizar directamente las columnas `anio`, `mes` y `dia` para el cierre diario; mantener la estrategia de unión por omisión de Catalyst mientras la referencia permanezca pequeña y controlada.**

La evidencia debe revisarse periódicamente. La decisión debe cambiar si aumentan considerablemente el tamaño de la referencia, cambia la consulta dominante o el volumen de datos hace que la granularidad diaria deje de ser conveniente.

---
