# S7 · Reto de negocio · Por qué no ponemos todo por lotes

**Competencia: TECH IA MAKER · Dirigido a la gerencia del acueducto**

**La respuesta corta:** de los cinco requerimientos de datos que tiene el acueducto, **cuatro ya van
por lotes**. Solo uno funciona en tiempo real, y es el único donde llegar tarde no produce un informe
desactualizado sino una tubería reventada.

---

## El requisito crítico

La alerta de presión fuera de rango. Es el único caso en que el dato no sirve para *saber* algo, sino
para *hacer* algo antes de que ocurra: cerrar una válvula, bajar la presión de un tramo, enviar una
cuadrilla. Su valor caduca en segundos, porque una sobrepresión que se detecta después de la rotura
ya no es una alerta, es un reporte.

Los otros cuatro requerimientos —el informe mensual de consumo, el tablero del centro de control, la
detección de fugas nocturnas y la carga del histórico— alimentan decisiones que se toman en horas o
en días. Ninguno gana nada con frescura de segundos.

## El costo de no tenerla

Si esa alerta llegara por lotes, la secuencia sería: la presión sube, la tubería revienta, y el
sistema se entera en el siguiente ciclo de procesamiento. **La detección dejaría de depender del
sensor y pasaría a depender de que alguien vea el agua en la calle y llame.**

En términos operativos, eso significa pagar tres cosas que hoy no pagamos:

- El **agua perdida** durante todas las horas que la rotura corre sin detectarse.
- La **reparación de una rotura consumada**, que cuesta más que la corrección preventiva de una
  sobrepresión.
- El **desabastecimiento del sector** mientras dura la reparación, con el costo reputacional y de
  atención al usuario que eso arrastra.

> **Supuesto declarado.** No tenemos aún la cifra en pesos de estos tres rubros. La recomendación se
> sostiene en la asimetría, no en el monto: mantener un flujo encendido tiene un costo *conocido y
> acotado*, mientras que el costo de una rotura no detectada es *variable y potencialmente mucho
> mayor*. Para convertir esto en una cifra bastaría con el histórico de roturas del último año y el
> costo medio de reparación, que el área de operaciones ya tiene.

## Por qué el resto sí puede ir por lotes, y qué se ahorra

Un proceso por lotes se enciende, corre y se apaga. Un flujo permanece encendido siempre, aunque no
llegue un solo dato. Esa es la diferencia de costo, y aplica todo el año.

Poner los cinco requerimientos en tiempo real significaría mantener cinco procesos encendidos de
forma permanente para atender necesidades que, en cuatro de los cinco casos, se satisfacen con un
proceso que corre unos minutos al día. **Se estaría pagando frescura de segundos para un informe que
se lee una vez al mes.**

El tablero del centro de control ilustra bien el punto intermedio: necesita frescura de minutos, no
de segundos, y eso se resuelve con tandas pequeñas y frecuentes. Obtiene lo que el operador necesita
sin el costo ni la complejidad de un flujo verdadero.

## La conclusión

El híbrido cuesta menos que todo flujo porque **paga tiempo real una sola vez, donde hace falta**, en
lugar de cinco veces. Y arriesga menos que todo lotes porque **no traslada a un informe mensual la
lógica de una alerta de seguridad**.

La pregunta que ordena la decisión no es cuál tecnología es mejor. Es: *¿qué se rompe si este dato
llega una hora tarde?* Para cuatro de los cinco requerimientos, la respuesta es nada. Para la alerta
de presión, la respuesta es una tubería.

**Nuestra recomendación es mantener la arquitectura híbrida tal como está.** Si se decidiera pasar la
alerta de presión a lotes para reducir ese costo, pedimos que la decisión quede documentada junto con
el tiempo de detección resultante, para que la organización sepa cuántas horas puede correr una
rotura antes de que el sistema la note.

---

*Sesión 7 · Taller de decisión · Competencia TECH IA MAKER: la decisión de arquitectura se sostiene
en la consecuencia de negocio de cada asignación, no en las propiedades de la tecnología.*
