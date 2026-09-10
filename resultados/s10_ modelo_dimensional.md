## 1. Diagrama 

```text

                         ┌─────────────────────┐
                         │      dim_fecha      │
                         ├─────────────────────┤
                         │ fecha_sk PK         │
                         │ fecha                │
                         │ año                  │
                         │ mes                  │
                         │ nombre_mes           │
                         │ trimestre            │
                         │ día                  │
                         │ día_semana           │
                         └──────────┬──────────┘
                                    │
                                    │
┌─────────────────────┐             │             ┌─────────────────────┐
│    dim_medidor      │             │             │     dim_sector      │
├─────────────────────┤             │             ├─────────────────────┤
│ medidor_sk PK       │             │             │ sector_sk PK        │
│ id_medidor_origen   │             │             │ id_sector_origen    │
│ codigo_medidor      │             │             │ nombre_sector       │
│ tipo_medidor        │             │             │ zona                │
│ estado              │             │             │ localidad           │
└──────────┬──────────┘             │             └──────────┬──────────┘
           │                        │                        │
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   fact_lecturas     │
                         ├─────────────────────┤
                         │ lectura_sk PK       │
                         │ fecha_sk FK         │
                         │ medidor_sk FK       │
                         │ sector_sk FK        │
                         │ hora                │
                         │ consumo              │
                         │ presion             │
                         └─────────────────────┘

```
## 2. Objetivo

El objetivo de este modelo dimensional es organizar la información
consolidada del proyecto para facilitar el análisis de las lecturas,
permitiendo consultar las medidas por fecha, medidor y sector.

El modelo utiliza un esquema estrella, con una tabla de hechos en el
centro y dimensiones conformadas alrededor.



## 3. Tabla de hechos

### fact_lecturas

La tabla `fact_lecturas` representa una lectura individual de un
medidor para una hora determinada.

### Clave primaria

- `lectura_sk`

### Claves foráneas

- `fecha_sk`
- `medidor_sk`
- `sector_sk`

### Medidas

| Campo | Tipo | Descripción | Aditividad |
|---|---|---|---|
| consumo | DECIMAL | Consumo registrado en la lectura | Aditiva |
| presion | DECIMAL | Presión registrada en la lectura | No aditiva |

> Las medidas definitivas deben corresponder a las variables existentes
> en la capa consolidada del proyecto.



## 4. Dimensión fecha

### dim_fecha

| Campo | Tipo | Descripción |
|---|---|---|
| fecha_sk | INTEGER | Clave subrogada |
| fecha | DATE | Fecha calendario |
| año | INTEGER | Año |
| mes | INTEGER | Número del mes |
| nombre_mes | VARCHAR | Nombre del mes |
| trimestre | INTEGER | Trimestre |
| dia | INTEGER | Día |
| dia_semana | VARCHAR | Día de la semana |

### Clave subrogada

`fecha_sk`

La clave subrogada es independiente de la clave natural de la fecha.



## 5. Dimensión medidor

### dim_medidor

| Campo | Tipo | Descripción |
|---|---|---|
| medidor_sk | INTEGER | Clave subrogada |
| id_medidor_origen | VARCHAR | Identificador del sistema origen |
| codigo_medidor | VARCHAR | Código del medidor |
| tipo_medidor | VARCHAR | Tipo de medidor |
| estado | VARCHAR | Estado del medidor |

### Clave subrogada

`medidor_sk`

La clave `medidor_sk` pertenece al modelo dimensional y no corresponde
directamente al identificador del sistema origen.


## 6. Dimensión sector

### dim_sector

| Campo | Tipo | Descripción |
|---|---|---|
| sector_sk | INTEGER | Clave subrogada |
| id_sector_origen | VARCHAR | Identificador original |
| nombre_sector | VARCHAR | Nombre del sector |
| zona | VARCHAR | Zona |
| localidad | VARCHAR | Localidad |

### Clave subrogada

`sector_sk`


## 7. Esquema estrella

El modelo está compuesto por una tabla de hechos central y dimensiones
conectadas directamente a ella.

Las dimensiones son planas para favorecer las consultas analíticas y
evitar joins innecesarios.

```text
dim_fecha
    |
    |
dim_medidor ---- fact_lecturas ---- dim_sector
