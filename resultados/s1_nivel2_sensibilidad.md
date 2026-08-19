# Nivel 2: Análisis de Sensibilidad

**1. ¿Duplicar `g` reduce el umbral a la mitad?**
No, no lo reduce exactamente a la mitad, y nuestra prueba de sensibilidad lo demuestra empíricamente. Según las mediciones en nuestro entorno, con un $g=4\%$ el umbral de saturación es de 37.7 períodos. Al duplicar la tasa a $g=8\%$, el umbral no cae matemáticamente a la mitad (18.85), sino a 19.2 períodos. Esta falta de proporcionalidad directa se explica porque la tasa de crecimiento ($g$) opera dentro de una función de logaritmo natural $\ln(1+g)$ en el denominador, lo que hace que la curva de saturación no sea una línea recta, sino que decrezca cada vez más lento.

**2. ¿Qué error en la estimación de `g` cambia su recomendación de arquitectura?**
Nuestra recomendación actual es mantener la infraestructura centralizada porque, asumiendo un $g=5\%$, tenemos un margen amplio de 51.3 meses. 

Un error de estimación leve (por ejemplo, que la contratación real crezca al 8%) reduciría el margen a 19.2 meses. Aunque es un recorte significativo, todavía nos deja más de año y medio de holgura operativa. El quiebre en la recomendación ocurriría si nos equivocamos dramáticamente y el crecimiento real fuera del 16% mensual; en ese escenario extremo, el sistema colapsaría en apenas 10.0 meses. Ese es el límite temporal que cambiaría nuestra recomendación técnica a "migrar inmediatamente a un clúster distribuido", ya que 10 meses es el margen mínimo prudente para aprovisionar servidores y realizar las pruebas de calidad sobre los expedientes públicos.

**3. ¿Qué es más grave para la decisión: equivocarse en `g` o equivocarse en `k`?**
Es matemáticamente y operativamente mucho más crítico equivocarse en el factor de expansión ($k$). 

La asimetría en la fórmula es clara: equivocarse en $g$ (en el denominador) solo altera la pendiente o la velocidad con la que nos acercamos al abismo a futuro. En cambio, el factor $k$ reside dentro del logaritmo del numerador $\ln(M / (k \cdot S_0))$. Equivocarse al medir $k$ —por ejemplo, omitir el peso real de los textos y objetos complejos en los registros del SECOP II— desplaza el cálculo completo de golpe y en una sola dirección. Un $k$ subestimado podría ocultarnos el hecho de que la memoria de la máquina ya está completamente saturada el día de hoy, dejándonos sin ningún margen de reacción.