# T4 · Agregación en clave map y reduce, con estimación de mezcla

**Sesión 4 · El modelo MapReduce**

## 1. La agregación de referencia (nivel 1, ya en el repositorio)

- **Mapper:** `muestra/mapper.py` — emite `sector <tab> presion` por cada lectura.
- **Reducer:** `muestra/reducer.py` — promedia la presión por sector.
- **Clave:** el sector (aproximado por `sensor_id` en la muestra sintética).

## 2. Con combinador (nivel 2, ya en el repositorio)

- **Combinador:** `muestra/combiner.py` — agrega suma y conteo localmente antes de la mezcla.
- **Reducer adaptado:** `muestra/reducer2.py` — suma las sumas, suma los conteos, divide solo al final.

| Ejecución | Bytes de mezcla | Cómo se midió |
|---|---|---|
| Sin combinador (nivel 1) | 3,418,645 | Contadores del job, salida de ejecución por consola |
| Con combinador (nivel 2) | 13,583 | Contadores del job, salida de ejecución por consola |
| Reducción porcentual | 99.60 % | `(3418645 - 13583) / 3418645` |

**Verificación de correctitud:** Verificado matemáticamente. Se ejecutó `diff` en la terminal del NameNode sobre los archivos de salida `/salida/part-00000` y `/salida2/part-00000` debidamente ordenados, lo que arrojó el mensaje "IDENTICOS", confirmando que el combinador no altera el valor numérico final.

## 3. Agregación propia del equipo (nivel 3)

- **Pregunta de negocio que responde:** ¿Qué modalidad de contratación concentra el mayor volumen de presupuesto público y de procesos adjudicados en SECOP II? Esto permite auditar la proporción de adjudicaciones a dedo (excepcionales) frente a licitaciones abiertas.
- **Clave de agrupación elegida:** `modalidad_de_contratacion` (índice 16 de SECOP II). Se eligió esta clave categórica porque representa la figura jurídica que rige los fondos, y usarla permite agregar correctamente la columna `valor_del_contrato` (índice 34).
- **Predicción antes de ejecutar:** Dado que las modalidades de contratación son un catálogo cerrado muy pequeño (aprox. 15-20 categorías distintas dictadas por ley), predecimos que con el combinador el tráfico de red (`Reduce shuffle bytes`) colapsará masivamente a unos pocos bytes en comparación al volumen de entrada.
- **Medición real tras ejecutar:** `Map input records`: 906,128. `Map output records`: 2. `Reduce shuffle bytes`: 52. 
- **Contraste predicción vs. medición:** La predicción sobre el tráfico ultra-optimizado fue correcta (apenas 52 bytes de mezcla debido a la bajísima cardinalidad de la clave). Sin embargo, el clúster operó como un filtro estricto: la mayoría de los contratos se descartaron porque los campos de texto intermedios contenían comas internas que desplazaban la columna del valor (rompiendo el CSV). Esto evidencia por qué un archivo CSV crudo debe limpiarse primero en la capa Refinada de un Lago de Datos.

## 4. Sesgo de clave

Al agrupar presupuestos por Modalidad de Contratación se evidencia un sesgo masivo inherente a la contratación estatal. Categorías como "Mínima Cuantía" o "Contratación Directa" engloban la abrumadora mayoría del volumen de procesos de SECOP II. En este escenario, el reductor de la clave mayoritaria tardará mucho más en procesar que los demás. Para solucionarlo sin alterar la pregunta de negocio, se debería aplicar una técnica de "Salting" (agregar un valor aleatorio temporal a las claves para forzar su distribución uniforme en el clúster), o usar una clave secundaria (ej. Modalidad + Mes) para re-agregar el total en una fase posterior.

---

