# src/

Código reutilizable que deje de vivir solo dentro de un notebook: funciones que se repiten entre
sesiones (por ejemplo, `measure_expansion_factor`, `compute_threshold_periods`, `profile_source`,
hoy definidas dentro de `notebooks/s01_perfilamiento.ipynb`).

Está vacía por ahora — la guía de sesión 2 la incluye en la estructura estándar del proyecto desde
el principio, para que exista el lugar cuando haga falta moverse de "código en un cuaderno" a
"código importable". No hay obligación de llenarla en S1-S4; empieza a tener sentido cuando una
función se usa desde más de un notebook.
