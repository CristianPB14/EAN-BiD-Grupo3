# T1 · Ficha técnica de la fuente de datos

**Sesión 1 · Naturaleza de los datos masivos**

> Criterio de aceptación de la guía: *"otra persona debe poder reproducir su cifra de umbral usando
> únicamente los datos declarados en su propia ficha. Si para llegar al número hace falta algo que no
> escribió, la ficha está incompleta."* Todos los campos con `COMPLETAR` deben quedar llenos antes de
> entregar.

## 0. Fuente elegida

SECOP II (Sistema Electrónico para la Contratación Pública). Es la fuente ideal para auditar y ejercer control normativo sobre los procesos de selección, modalidades de contratación y el cumplimiento de la Ley 80 de 1993 a nivel nacional.

---

## 1. Los siete elementos (sección 4 de la guía de sesión 1)

| # | Elemento | Respuesta |
|---|---|---|
| 1 | **Origen y responsable** — quién publica y bajo qué mandato | Agencia Nacional de Contratación Pública (Colombia Compra Eficiente), bajo el mandato de transparencia estatal. |
| 2 | **Licencia y condiciones de uso** — qué se permite hacer con el dato | Datos Abiertos de Colombia (Ley 1712 de 2014 de Transparencia y del Derecho de Acceso a la Información Pública). Uso libre, público y sin restricciones comerciales. |
| 3 | **Volumen actual y tasa de crecimiento** — con el método de estimación declarado | Volumen local de 304.5 MB para la muestra de 200.000 filas. Se declara una tasa de crecimiento (g) supuesta del 5% mensual (g=0.05), fundamentada en la apertura constante de nuevos procesos y la obligación legal de las entidades de reportar en la plataforma. |
| 4 | **Frecuencia declarada frente a frecuencia observada** | Declarada como continua/diaria en el portal. Observada ejecutando un agrupamiento sobre la columna `fecha_de_firma` en la muestra, confirmando 182,511 registros el mismo día y 2,932 saltos de un día. |
| 5 | **Formato y mecanismo de publicación** — descarga manual, API, archivo por período | API de Socrata (datos.gov.co) utilizando el identificador estable `jbjy-vk9h`. Descarga en formato CSV controlada mediante el parámetro `$limit`. |
| 6 | **Estabilidad del esquema** — ¿cambian las columnas entre períodos? | Altamente estable. Los pliegos de condiciones y formularios del Estado están estandarizados legalmente, aunque contiene una alta proporción de campos de texto libre (76.5%) que expanden la memoria. |
| 7 | **Identificador estable de registro** — ¿existe una clave para carga incremental? | Sí, existe el `proceso_de_compra` y la identificación única del contrato, lo que permite la carga de nuevos expedientes sin duplicidad. |

---

## 2. Las tres mediciones (sección 3 de la guía de sesión 1)

Estos valores deben salir de `resultados/mediciones.csv`, que genera automáticamente
`notebooks/s01_perfilamiento.ipynb` (celda de medición). **Vuelvan a ejecutar el notebook después de
corregir el entorno** (ver README, sección 4.3) para asegurarse de que las cifras están frescas y de
que `resultados/` ya no está bloqueado por el `.gitignore`.

| Parámetro | Símbolo | Valor | Cómo se obtuvo |
|---|---|---|---|
| Tamaño en disco | `S0` | 0.3045 GB | `os.path.getsize(...)`, ver `get_file_size_gb`. |
| Factor de expansión | `k` | 3.37 | `df.memory_usage(deep=True).sum() / tamaño_disco`, ver `measure_expansion_factor`. |
| Memoria útil | `M` | 11.20 GB | `psutil.virtual_memory().available`, calculada asumiendo un escenario de 16 GB nominales donde se reservó el 30% para procesos del sistema operativo. |
| Tasa de crecimiento | `g` | 0.05 | Declarada y supuesta (5% mensual) para la proyección a futuro de los expedientes contractuales. |

> Referencia de la última corrida, tomada de `resultados/mediciones.csv`:
> SECOP II → 200.000 filas, 85 columnas, 76,5 % columnas de texto, k = 3.37.
> IDEAM → 150.000 filas, 13 columnas, 61,5 % columnas de texto, k = 3.24.
> GEIH → 29.611 filas, 202 columnas, 5,4 % columnas de texto, k = 5.37.

## 3. Cálculo del umbral de saturación

$$t_{umbral} = \frac{\ln\left(\dfrac{M}{k \cdot S_0}\right)}{\ln(1+g)}$$

```python
t_umbral = compute_threshold_periods(
    memory_useful_gb=11.20,
    expansion_factor=3.37,
    initial_size_gb=0.3045,
    growth_rate=0.05,
)
print(f"t_umbral = {t_umbral:.1f} periodos")
```

**Resultado:** 49,0 períodos (meses). **Interpretación:** con la muestra actual de 200.000
filas y un crecimiento supuesto del 5 % mensual, SECOP II tardaría poco más de cuatro años
en desbordar los 11,20 GB de memoria útil de un equipo de 16 GB. El umbral es positivo, así
que la saturación está en el futuro y no en el pasado: hoy la fuente todavía cabe en un solo
computador, y esa es precisamente la cifra que impide justificar un clúster por anticipado.