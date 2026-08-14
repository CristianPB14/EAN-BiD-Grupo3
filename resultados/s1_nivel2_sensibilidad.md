# S1 · Nivel 2 · Análisis de sensibilidad a `g`

> Este archivo es el entregable en texto plano que pide la sección 8 de la guía de sesión 1
> (`resultados/nivel2_sensibilidad.md`). El cálculo que lo sostiene vive en
> `notebooks/s01_perfilamiento.ipynb` (celda de barrido de `g`); este documento recoge las
> respuestas escritas a las tres preguntas.

## 1. ¿Duplicar `g` reduce el umbral a la mitad?

No. La relación no es lineal: `g` aparece dentro de un logaritmo en el denominador (`ln(1+g)`),
mientras que `k` y `S0` aparecen dentro de un logaritmo en el numerador. Duplicar `g` de 4 % a 8 %
no reduce `t_umbral` a la mitad — lo reduce de forma menos que proporcional cuando `g` es bajo, y de
forma más agresiva cuando `g` ya es alto, porque `ln(1+g)` crece más lento que `g` mismo.

## 2. ¿Qué error en la estimación de `g` cambia la recomendación de arquitectura?

`COMPLETAR` con la cifra concreta de su fuente, leyendo la salida de la celda de barrido: comparen
`t_umbral` entre `g=1%` y `g=2%`. Si esa diferencia ya mueve la recomendación (por ejemplo, de "hay
años de margen" a "hay meses de margen"), entonces un solo punto porcentual de error en `g` es
suficiente para cambiar la decisión.

## 3. ¿Qué es más grave para la decisión: equivocarse en `g` o en `k`?

Equivocarse en `k` es más grave. `k` multiplica directamente a `S0` dentro del logaritmo del
numerador, así que un `k` subestimado (por ejemplo, medido sin `deep=True`) desplaza el umbral
completo de forma inmediata y en una sola dirección: hace parecer que hay más margen del que
realmente hay. `g` solo afecta la pendiente con la que se llega al umbral, no si se llega.

---

**Nota de origen:** las respuestas 1 y 3 son generales, se sostienen en la forma de la fórmula y no
dependen de la fuente elegida. La respuesta 2 sí depende de las cifras concretas de su fuente —
complétenla con la salida real de la celda de barrido antes de entregar.
