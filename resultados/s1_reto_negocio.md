# S1 · Reto de negocio · Recomendación a la gerencia del acueducto

**Decisión recomendada:** Migrar a procesamiento por trozos o a un formato columnar comprimido antes
de considerar un clúster distribuido; el nodo único ya no alcanza, pero distribuir es la tercera
salida, no la primera.

**Cuál de las tres salidas ante la saturación aplica hoy:** con telemetría horaria, el archivo mensual
del acueducto pasó de 11 MB a cerca de 7,8 GB. Con `k ≈ 5,4` y un equipo de 12 GB de memoria útil,
el objeto en memoria pediría más de 42 GB — muy por encima de lo disponible. La primera salida,
reducir el dato (tipificar columnas, descartar las que nadie consulta, comprimir por columnas), ya no
basta por sí sola a este volumen; la segunda, procesar por trozos o con un motor apoyado en disco,
sí resuelve el problema inmediato sin el costo operativo de un clúster.

**La cifra que sostiene la recomendación, con supuestos visibles:** con `S0 = 7,8` GB, `k = 5,4`,
`M = 12` GB y `g = 4 %` mensual, el umbral de saturación del nodo único es
`t_umbral = ln(M / (k·S0)) / ln(1+g) ≈ −32` períodos: la fuente cruzó la frontera del nodo único hace
casi tres años, no en el futuro. Si en cambio se guardara el consolidado mensual por medidor en vez
de la lectura horaria (mismos medidores, mismo negocio, solo cambia la granularidad), `S0` baja a
`0,0108` GB y `t_umbral ≈ 136` períodos, cerca de once años de margen.

**Horizonte: cuándo esta recomendación deja de servir:** cuando el volumen mensual vuelva a acercarse
al límite de lo que un equipo de gama media puede procesar por trozos en la ventana operativa
disponible (hoy, con el crecimiento estimado, eso no está a la vista en el corto plazo si se adopta
la salida 2; sin ella, ya se cruzó).

**Qué cambiaría la recomendación si el crecimiento fuera el doble:** con `g = 8 %` en vez de `4 %`,
el umbral se acerca más rápido de lo que la fórmula sugiere a primera vista, porque `g` está dentro
de un logaritmo que crece más lento que `g` mismo — la sensibilidad no es lineal. Aun así, duplicar
`g` no cambiaría la urgencia inmediata (el escenario A ya está saturado), pero sí acortaría el margen
del escenario B de consolidado mensual, y ahí sí podría justificar adelantar la evaluación de
infraestructura distribuida.

---

### Declaración de uso de asistentes de inteligencia artificial

`COMPLETAR` — este borrador fue generado con apoyo de un asistente de IA a partir de las cifras que
ya aparecen en el material de la sesión 1 (no de una medición propia del equipo sobre su fuente
elegida). Antes de entregar: (1) verifiquen cada cifra citada aquí contra el material de la sesión,
(2) declaren aquí qué parte del documento usó IA y para qué, tal como exige la guía.
