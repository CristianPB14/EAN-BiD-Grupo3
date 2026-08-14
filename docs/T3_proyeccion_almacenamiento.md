# T3 · Proyección de almacenamiento con tres factores de réplica

**Sesión 3 · Sistemas de archivos distribuidos**

## 0. Consolidación del equipo

Antes de proyectar: `COMPLETAR` — qué fuente única eligió el equipo, o qué combinación de las tres
fichas individuales (T1) se unificó, y por qué.

## 1. Fórmulas de la sesión

- Almacenamiento físico = volumen lógico × factor de réplica `R`
- Número de bloques = tamaño del archivo ÷ tamaño de bloque, redondeado hacia arriba
- Tolerancia = `R − 1` nodos caídos simultáneamente sin perder dato

## 2. Proyección a doce meses

Partiendo de `S0` y `g` de la ficha T1 del equipo, el volumen proyectado a 12 meses es
`S0 · (1+g)^12`.

| Factor de réplica `R` | Almacenamiento físico proyectado | Nodos que puede perder |
|---|---|---|
| 1 | `COMPLETAR` | 0 · sin tolerancia |
| 2 | `COMPLETAR` | 1 |
| 3 | `COMPLETAR` | 2 |

> Ejemplo de referencia (caso del acueducto de la teoría de sesión, **no son las cifras del
> equipo**): con 7,8 GB lógicos mensuales, R=1 → 7,8 GB, R=2 → 15,6 GB, R=3 → 23,4 GB. Reemplacen
> con el volumen proyectado real de su fuente.

## 3. Tamaño de bloque

Usen el valor real de HDFS, 128 MB, no el didáctico de 1 MB de la práctica en clase.

- Número de bloques a 12 meses con bloque de 128 MB: `COMPLETAR`
- Tensión a nombrar: `COMPLETAR` — bloques muy grandes desperdician espacio con archivos pequeños;
  bloques muy pequeños multiplican los metadatos que el nodo maestro debe mantener en memoria.

## 4. Decisión y justificación

- **Factor de réplica elegido:** `COMPLETAR`
- **Por qué:** `COMPLETAR` — ¿el dato es crítico e irrecuperable (telemetría histórica) o se puede
  regenerar? Eso decide si el costo de triplicar el almacenamiento se justifica.
- **Tamaño de bloque elegido:** `COMPLETAR`
- **Por qué:** `COMPLETAR`

## 5. Evidencia práctica

Peguen aquí (o enlacen a `resultados/s3_evidencia_fsck.md`) la salida real de:

```bash
docker compose exec namenode hdfs dfs -du -h /datos
docker compose exec namenode hdfs fsck /datos/muestra_r3.csv -files -blocks
```

`COMPLETAR`

---

*Criterio de aceptación: otra persona, con los datos de la ficha T1, debe obtener las mismas cifras
de esta proyección.*
