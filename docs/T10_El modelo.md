# Descripción del trabajo realizado

En esta actividad se desarrolló el modelo lógico dimensional del proyecto, tomando como base el concepto principal de la sesión: definir primero el grano y, a partir de este, construir el resto del modelo. Para el proyecto se estableció el grano **“Una lectura de un medidor en una hora”**, lo que significa que cada registro de la tabla de hechos representa una lectura específica realizada por un medidor durante una hora determinada.

A partir de este grano se definieron la tabla de hechos y las dimensiones necesarias para organizar la información:

| Elemento | Función |
|---|---|
| `fact_lecturas` | Contiene las lecturas y medidas del proceso |
| `dim_fecha` | Permite analizar las lecturas por fecha, mes, año, trimestre, etc. |
| `dim_medidor` | Contiene la información descriptiva de cada medidor |
| `dim_sector` | Permite analizar las lecturas según el sector, zona o localidad |

La tabla de hechos `fact_lecturas` concentra las medidas del proyecto, como `consumo` y `presion`, junto con las claves que permiten relacionarla con las dimensiones. De esta forma, la información numérica queda separada de los datos descriptivos, haciendo que el modelo sea más fácil de consultar y analizar.

Las dimensiones cuentan con claves subrogadas, que son identificadores generados dentro del propio modelo y que no dependen directamente de las claves originales de la fuente.

| Dimensión | Clave subrogada | Clave de origen |
|---|---|---|
| `dim_fecha` | `fecha_sk` | `fecha` |
| `dim_medidor` | `medidor_sk` | `medidor_origen` |
| `dim_sector` | `sector_sk` | `sector_origen` |

También se desarrolló código en Python utilizando `pandas`, con el objetivo de automatizar parte del proceso. El código permite cargar los archivos CSV, identificar los datos disponibles, construir las dimensiones, generar las claves subrogadas, crear la tabla de hechos y realizar diferentes validaciones.

Entre las validaciones realizadas se encuentra la comprobación del grano, verificando que no existan registros duplicados para la combinación que identifica una lectura. También se revisan las claves foráneas para comprobar que cada registro de la tabla de hechos pueda relacionarse correctamente con sus dimensiones.

| Validación | Propósito |
|---|---|
| Validación del grano | Comprobar que no existan duplicados |
| Validación de claves foráneas | Verificar la relación entre hechos y dimensiones |
| Generación de resultados | Facilitar la revisión del modelo construido |

Como resultado, el proyecto queda preparado para generar archivos como:

```text
resultados/
├── dim_fecha.csv
├── dim_medidor.csv
├── dim_sector.csv
├── fact_lecturas.csv
└── validacion_grano.csv
