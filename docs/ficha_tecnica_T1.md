# T1 · Ficha técnica de la fuente de datos

**Sesión 1 · Naturaleza de los datos masivos**

> Criterio de aceptación de la guía: *"otra persona debe poder reproducir su cifra de umbral usando
> únicamente los datos declarados en su propia ficha. Si para llegar al número hace falta algo que no
> escribió, la ficha está incompleta."* Todos los campos con `COMPLETAR` deben quedar llenos antes de
> entregar.

## 0. Fuente elegida

`COMPLETAR`: SECOP II / IDEAM / GEIH del DANE / otra — la que el equipo consolidó como fuente única
en la S3, o la combinación acordada.

---

## 1. Los siete elementos (sección 4 de la guía de sesión 1)

| # | Elemento | Respuesta |
|---|---|---|
| 1 | **Origen y responsable** — quién publica y bajo qué mandato | `COMPLETAR` |
| 2 | **Licencia y condiciones de uso** — qué se permite hacer con el dato | `COMPLETAR` |
| 3 | **Volumen actual y tasa de crecimiento** — con el método de estimación declarado | `COMPLETAR` (ver sección 2) |
| 4 | **Frecuencia declarada frente a frecuencia observada** | `COMPLETAR` |
| 5 | **Formato y mecanismo de publicación** — descarga manual, API, archivo por período | `COMPLETAR` |
| 6 | **Estabilidad del esquema** — ¿cambian las columnas entre períodos? | `COMPLETAR` |
| 7 | **Identificador estable de registro** — ¿existe una clave para carga incremental? | `COMPLETAR` |

---

## 2. Las tres mediciones (sección 3 de la guía de sesión 1)

Estos valores deben salir de `resultados/mediciones.csv`, que genera automáticamente
`notebooks/s01_perfilamiento.ipynb` (celda de medición). **Vuelvan a ejecutar el notebook después de
corregir el entorno** (ver README, sección 4.3) para asegurarse de que las cifras están frescas y de
que `resultados/` ya no está bloqueado por el `.gitignore`.

| Parámetro | Símbolo | Valor | Cómo se obtuvo |
|---|---|---|---|
| Tamaño en disco | `S0` | `COMPLETAR` GB | `os.path.getsize(...)`, ver `get_file_size_gb` |
| Factor de expansión | `k` | `COMPLETAR` | `df.memory_usage(deep=True).sum() / tamaño_disco`, ver `measure_expansion_factor` |
| Memoria útil | `M` | `COMPLETAR` GB | `psutil.virtual_memory().available`, medida en su propio equipo, no la etiqueta del fabricante |
| Tasa de crecimiento | `g` | `COMPLETAR` | `COMPLETAR`: histórica, documentada por la fuente, o supuesta — decláre cuál |

> Referencia de la última corrida disponible en este repositorio (sujeta a cambiar al re-ejecutar):
> SECOP II → 200.000 filas, 85 columnas, 76,5 % columnas de texto, k = 3,38.
> IDEAM → 150.000 filas, 13 columnas, 61,5 % columnas de texto, k = 3,25.
> GEIH → 29.611 filas, **1 sola columna** detectada, k = 1,16 — esto último es sospechoso: una
> fuente con decenas de variables (según su diccionario) no debería perfilarse con una sola columna.
> Es probable que el separador de campo del archivo no sea una coma. Revísenlo antes de usar este
> número: es evidencia de **variedad**, no un resultado a copiar tal cual.

## 3. Cálculo del umbral de saturación

$$t_{umbral} = \frac{\ln\left(\dfrac{M}{k \cdot S_0}\right)}{\ln(1+g)}$$

```python
# Ejecutar con los valores de la sección 2, ya confirmados
t_umbral = compute_threshold_periods(
    memory_useful_gb=COMPLETAR,
    expansion_factor=COMPLETAR,
    initial_size_gb=COMPLETAR,
    growth_rate=COMPLETAR,
)
print(f"t_umbral = {t_umbral:.1f} periodos")
```

**Resultado:** `COMPLETAR` períodos. **Interpretación:** `COMPLETAR` — si es negativo, expliquen que
la saturación ya ocurrió en el pasado, no que el cálculo falló.

---

*T1 alimenta T2 (se versiona dentro de `docs/`) y T5 (ingesta a la capa cruda del lago de datos).*
