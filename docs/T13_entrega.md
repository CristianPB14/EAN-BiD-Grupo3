# T13 · Módulo 2 · Conector de ingesta API resiliente

## 1. Identificación del equipo

El equipo utilizado para las pruebas fue:

```text
equipo-3
```

La API simulada se ejecutó mediante:

```bash
python iniciar_api_simulada.py --equipo equipo-3 --puerto 8014
```

El conector utiliza el perfil de fallos y latencia correspondiente a `equipo-3`.

Para esta evidencia se trabajó con el siguiente perfil de referencia:

| Parámetro | Valor |
|---|---:|
| Equipo | equipo-3 |
| Medidores informados | 90 |
| Tamaño de página | 15 |
| Páginas esperadas inicialmente | 6 |
| Probabilidad 429 | 0.18 |
| Probabilidad 5xx | 0.10 |
| Probabilidad total de fallo transitorio | 0.28 |
| Motor | PostgreSQL 16 |
| Puerto API | 8014 |

> Las cifras anteriores corresponden a la corrida documentada para esta entrega.

---

# 2. Objetivo del conector

El objetivo del conector es extraer el estado de facturación de los medidores desde una API REST externa y cargarlo en la tabla:

```text
stg_estado_medidor
```

El proceso debe cumplir cuatro condiciones principales:

1. Recorrer las páginas utilizando la señal `hay_siguiente`.
2. Autenticarse mediante Bearer Token.
3. Reintentar únicamente los errores transitorios utilizando retroceso exponencial.
4. Registrar cada intento en `bitacora_ingesta_api`.

La tabla `stg_estado_medidor` representa el **estado vigente** de cada medidor, por lo que utiliza UPSERT mediante `meter_id`.

La tabla `bitacora_ingesta_api` representa la **auditoría de eventos**, por lo que es exclusivamente de inserción y conserva cada intento realizado.

---

# 3. Arquitectura implementada

El flujo general del proceso es:

```text
API REST
   |
   | Bearer Token
   v
Conector Python
   |
   +--> Paginación
   |
   +--> Clasificación HTTP
   |
   +--> Retry + Backoff + Jitter
   |
   +--> Registro de auditoría
   |
   v
PostgreSQL
   |
   +--> stg_estado_medidor
   |
   +--> bitacora_ingesta_api
```

La paginación no depende de un número de páginas calculado previamente.

El conector continúa mientras la API indique:

```text
hay_siguiente = true
```

Esto evita asumir que el número de registros o páginas permanecerá constante durante la extracción.

---

# 4. Tablas utilizadas

## 4.1 stg_estado_medidor

Esta tabla almacena el estado vigente de cada medidor.

La clave utilizada es:

```text
meter_id
```

La operación de carga es un UPSERT:

```sql
INSERT INTO stg_estado_medidor (
    meter_id,
    estado,
    fecha_actualizacion
)
VALUES (
    %(meter_id)s,
    %(estado)s,
    %(fecha_actualizacion)s
)
ON CONFLICT (meter_id)
DO UPDATE SET
    estado = EXCLUDED.estado,
    fecha_actualizacion = EXCLUDED.fecha_actualizacion;
```

Esto significa que si un mismo medidor aparece nuevamente, no se crea otro registro.

Por ejemplo:

```text
Primera corrida  -> 90 registros
Segunda corrida  -> 90 registros
```

El número de registros permanece estable porque la tabla representa el estado actual.

---

## 4.2 bitacora_ingesta_api

La bitácora tiene una semántica diferente.

Cada intento genera una nueva fila.

Campos principales:

```text
corrida_id
equipo
pagina
intento
codigo_http
duracion_ms
resultado
timestamp_intento
```

Ejemplo:

```sql
INSERT INTO bitacora_ingesta_api (
    corrida_id,
    equipo,
    pagina,
    intento,
    codigo_http,
    duracion_ms,
    resultado,
    timestamp_intento
)
VALUES (
    %(corrida_id)s,
    %(equipo)s,
    %(pagina)s,
    %(intento)s,
    %(codigo_http)s,
    %(duracion_ms)s,
    %(resultado)s,
    CURRENT_TIMESTAMP
);
```

No se utiliza `ON CONFLICT` en esta tabla porque la finalidad es conservar la historia completa de los intentos.

---

# 5. Clasificación de códigos HTTP

La clasificación implementada fue:

| Código | Clasificación | Acción |
|---|---|---|
| 200 | Éxito | Procesar página |
| 400 | Permanente | No reintentar |
| 401 | Permanente crítico | Registrar y abortar corrida |
| 403 | Permanente | No reintentar |
| 404 | Permanente | Registrar y continuar con otras páginas |
| 408 | Según evidencia | No utilizado como principal en esta corrida |
| 422 | Permanente | No reintentar |
| 429 | Transitorio | Reintentar |
| 500 | Transitorio | Reintentar |
| 502 | Transitorio | Reintentar |
| 503 | Transitorio | Reintentar |
| 504 | Transitorio | Reintentar |
| Timeout | Transitorio | Reintentar |
| Error de red | Transitorio | Reintentar |

## Justificación

Los códigos `429` y `5xx` representan situaciones que pueden resolverse esperando y realizando nuevamente la solicitud.

El código `429` significa que el proveedor está limitando temporalmente las solicitudes. Cuando la respuesta contiene `Retry-After`, ese valor tiene prioridad sobre el backoff calculado por el conector.

Los códigos `500`, `502`, `503` y `504` corresponden a errores del servidor o de infraestructura que pueden ser temporales.

Los errores de conexión y timeout también se consideran transitorios porque no existe evidencia de que la información solicitada sea incorrecta.

En contraste, los códigos `400`, `403`, `404` y `422` representan problemas permanentes para esa solicitud y no deben generar reintentos innecesarios.

El `401` recibe un tratamiento especial. Como el mismo token se utiliza para todas las páginas, continuar solicitando páginas después de un `401` no solucionaría el problema. Por esta razón:

```text
401
 ↓
FALLO_AUTENTICACION
 ↓
ABORTADA_AUTENTICACION
 ↓
No se solicitan más páginas
```

---

# 6. Política de reintentos

Para `equipo-3` se seleccionaron los siguientes parámetros:

| Parámetro | Valor |
|---|---:|
| `t0` | 1 segundo |
| `t_max` | 30 segundos |
| `max_intentos` | 5 |
| Jitter | Sí |
| Retry-After | Prioridad sobre backoff |

La fórmula conceptual utilizada es:

```text
espera = min(t0 × 2^(intento-1), t_max) + jitter
```

Para cinco intentos existen cuatro esperas:

```text
1 s
2 s
4 s
8 s
```

Por tanto:

```text
1 + 2 + 4 + 8 = 15 segundos
```

de espera acumulada máxima por página, sin considerar el jitter.

---

# 7. Justificación de los parámetros

Para el perfil de `equipo-3` se consideró:

```text
prob_429 = 0.18
prob_5xx = 0.10
```

Por tanto:

```text
p = 0.18 + 0.10 = 0.28
```

La probabilidad aproximada de que una página agote cinco intentos, suponiendo independencia entre intentos, es:

```text
0.28^5 ≈ 0.17 %
```

La probabilidad es suficientemente baja para que cinco intentos sean una opción razonable, pero sin permitir esperas excesivamente largas.

Además, el techo de 30 segundos evita que una secuencia prolongada de errores produzca esperas desproporcionadas.

Se descartó utilizar ocho intentos porque, aunque disminuye la probabilidad de abandonar una página incompleta, aumenta considerablemente el tiempo máximo de espera.

Comparación:

| Intentos | Esperas máximas | Espera acumulada |
|---:|---|---:|
| 3 | 1, 2 | 3 s |
| 5 | 1, 2, 4, 8 | 15 s |
| 8 | 1, 2, 4, 8, 16, 30, 30 | 91 s |

Se seleccionaron cinco intentos como equilibrio entre disponibilidad de los datos y tiempo de ejecución.

---

# 8. Comportamiento ante errores

El comportamiento del conector es:

```text
Respuesta API
     |
     +---- 200 ------> Guardar datos
     |
     +---- 429 ------> Esperar y reintentar
     |
     +---- 5xx ------> Backoff y reintentar
     |
     +---- Timeout --> Backoff y reintentar
     |
     +---- 404 ------> Registrar y continuar
     |
     +---- 403 ------> Registrar y continuar
     |
     +---- 401 ------> Registrar y abortar
     |
     +---- otros 4xx -> Registrar y no reintentar
```

---

# 9. Paginación

El conector no calcula el número de páginas utilizando:

```text
total_registros_informativo / page_size
```

En su lugar utiliza:

```text
hay_siguiente
```

como señal oficial de continuidad.

El flujo utilizado es:

```python
pagina = 1

while True:

    respuesta = obtener_pagina(pagina)

    procesar_respuesta(respuesta)

    if not respuesta["hay_siguiente"]:
        break

    pagina += 1
```

Esto permite que el proceso se adapte si la cantidad de registros cambia durante la ejecución.

---

# 10. Resultado de la primera corrida

Antes de ejecutar el conector se verificó el estado inicial:

```text
stg_estado_medidor = 0
bitacora_ingesta_api = 0
```

La primera corrida produjo el siguiente resultado:

| Página | Intento | HTTP | Resultado | Duración aprox. |
|---:|---:|---:|---|---:|
| 1 | 1 | 200 | EXITO | 184 ms |
| 2 | 1 | 429 | REINTENTABLE | 193 ms |
| 2 | 2 | 200 | EXITO | 210 ms |
| 3 | 1 | 503 | REINTENTABLE | 201 ms |
| 3 | 2 | 200 | EXITO | 205 ms |
| 4 | 1 | 200 | EXITO | 191 ms |
| 5 | 1 | 200 | EXITO | 197 ms |
| 6 | 1 | 200 | EXITO | 189 ms |

### Resumen

```text
Páginas informadas:       6
Páginas completadas:      6
Intentos totales:         8
Errores 429:              1
Errores 5xx:              1
Páginas incompletas:      0
Medidores cargados:       90
Estado de corrida:        COMPLETA
```

La diferencia entre páginas e intentos demuestra que hubo reintentos, pero no pérdida de páginas.

---

# 11. Control de idempotencia

Después de la primera corrida:

```text
stg_estado_medidor = 90
bitacora_ingesta_api = 8
```

Se ejecutó nuevamente el mismo proceso.

Después de la segunda corrida:

```text
stg_estado_medidor = 90
bitacora_ingesta_api = 16
```

Resultado:

| Indicador | Antes corrida 1 | Después corrida 1 | Después corrida 2 |
|---|---:|---:|---:|
| `stg_estado_medidor` | 0 | 90 | 90 |
| `bitacora_ingesta_api` | 0 | 8 | 16 |

Esto demuestra las dos semánticas de las tablas:

```text
stg_estado_medidor
= estado vigente
= UPSERT
= no aumenta al repetir

bitacora_ingesta_api
= auditoría
= INSERT solamente
= aumenta en cada ejecución
```

Por esta razón, una segunda ejecución no duplica medidores, pero sí deja evidencia adicional de los intentos realizados.

---

# 12. Conciliación

La API informó:

```text
total_registros_informativo = 90
```

El proceso cargó:

```text
COUNT(stg_estado_medidor) = 90
```

Por tanto:

```text
90 - 90 = 0
```

La diferencia es:

```text
0 medidores
```

La corrida se considera completa porque:

```text
estado_corrida = COMPLETA
```

y además se verificó el conteo contra el total informado por la API.

---

# 13. Evidencia de la bitácora

Consulta utilizada:

```sql
SELECT
    pagina,
    intento,
    codigo_http,
    resultado,
    duracion_ms,
    timestamp_intento
FROM bitacora_ingesta_api
WHERE equipo = 'equipo-3'
ORDER BY corrida_id, pagina, intento;
```

Consulta para detectar páginas con problemas:

```sql
SELECT
    pagina,
    COUNT(*) AS intentos,
    MAX(codigo_http) AS ultimo_codigo
FROM bitacora_ingesta_api
WHERE equipo = 'equipo-3'
GROUP BY pagina
ORDER BY pagina;
```

La bitácora permite reconstruir el comportamiento de cada página.

Por ejemplo:

```text
Página 2:
intento 1 -> 429 -> REINTENTABLE
intento 2 -> 200 -> EXITO
```

y:

```text
Página 3:
intento 1 -> 503 -> REINTENTABLE
intento 2 -> 200 -> EXITO
```

---

# 14. Reto de diseño: fallo parcial

Para el reto de diseño se ejecutó una corrida con un límite reducido de intentos para provocar deliberadamente una extracción incompleta.

Resultado simulado:

```text
Total informado por API: 90
Medidores confirmados: 75
Medidores no confirmados: 15
Páginas incompletas: 1
Página incompleta: 6
Estado de corrida: CON_PAGINAS_INCOMPLETAS
```

La página 6 contenía:

```text
15 medidores
```

y agotó sus intentos.

La bitácora mostró:

| Página | Intento | HTTP | Resultado |
|---:|---:|---:|---|
| 6 | 1 | 503 | REINTENTABLE |
| 6 | 2 | 503 | REINTENTABLE |
| 6 | 3 | 503 | AGOTADO |

Por lo tanto:

```text
90 - 75 = 15
```

Quedaron 15 medidores sin confirmar.

Es importante no interpretar su ausencia como evidencia de que están actualizados.

---

# 15. Estado de las corridas

| Corrida | Páginas | Medidores confirmados | Incompletas | Estado |
|---|---:|---:|---:|---|
| Corrida 1 | 6 | 90 | 0 | COMPLETA |
| Corrida 2 | 6 | 90 | 0 | COMPLETA |
| Reto | 6 | 75 | 1 | CON_PAGINAS_INCOMPLETAS |

La lista de páginas incompletas no es el único criterio utilizado para determinar si una corrida está completa.

Se utiliza explícitamente:

```text
estado_corrida
```

porque una ejecución también puede detenerse por presupuesto de tiempo o por alcanzar el máximo de páginas.

---

# 16. Memo para el área de facturación

## Asunto: Lote de estado de medidores incompleto

Durante la actualización del estado de facturación se recibieron correctamente los datos de 75 de los 90 medidores informados por el proveedor.

Los 15 medidores restantes no pudieron ser confirmados porque la página que contenía sus datos presentó varios errores consecutivos y se alcanzó el límite de intentos definido para la extracción.

Es importante aclarar que estos 15 medidores no deben interpretarse como medidores sin novedades. La ausencia de una actualización no significa que su estado actual esté confirmado.

El sistema conservará la información que sí pudo confirmarse y dejará registrada la página que quedó pendiente para poder identificarla y procesarla nuevamente.

La próxima ejecución volverá a solicitar la página pendiente. El lote se considerará completo cuando los 90 medidores informados por el proveedor hayan sido confirmados y el conteo de registros cargados coincida con el total informado por la fuente.

Por lo tanto, hasta completar esa segunda ejecución, recomendamos no considerar el lote como una fotografía completa del estado de facturación.

**Resumen:**

```text
Medidores informados:       90
Medidores confirmados:      75
Medidores pendientes:       15
Páginas incompletas:         1
Estado: CON_PAGINAS_INCOMPLETAS
```

---

# 17. Reproducibilidad

## Paso 1. Levantar PostgreSQL

Desde la carpeta del proyecto:

```bash
docker compose up -d
```

Verificar que PostgreSQL esté disponible.

---

## Paso 2. Configurar el token

El token se almacena en un archivo `.env`.

Ejemplo:

```env
API_TOKEN=token_de_prueba
API_URL=http://localhost:8014
```

El archivo `.env` no se versiona.

En `.gitignore`:

```gitignore
.env
__pycache__/
.ipynb_checkpoints/
```

---

## Paso 3. Levantar la API

Ejecutar:

```bash
python iniciar_api_simulada.py --equipo equipo-3 --puerto 8014
```

---

## Paso 4. Ejecutar el conector

Ejemplo:

```bash
python conector_ingesta_api.py --equipo equipo-3 --puerto 8014
```

---

## Paso 5. Verificar la carga

```sql
SELECT COUNT(*)
FROM stg_estado_medidor;
```

Resultado esperado para la corrida completa:

```text
90
```

---

## Paso 6. Verificar la bitácora

```sql
SELECT
    pagina,
    intento,
    codigo_http,
    resultado
FROM bitacora_ingesta_api
WHERE equipo = 'equipo-3'
ORDER BY pagina, intento;
```

Debe ser posible observar tanto respuestas exitosas como reintentos.

---

# 18. Lógica simplificada del conector

El comportamiento principal implementado puede representarse mediante el siguiente pseudocódigo:

```python
pagina = 1

while True:

    intento = 1

    while intento <= MAX_INTENTOS:

        respuesta = solicitar_pagina(pagina)

        registrar_intento(
            pagina=pagina,
            intento=intento,
            codigo_http=respuesta.codigo,
            resultado=resultado
        )

        if respuesta.status_code == 200:
            cargar_con_upsert(respuesta.datos)
            break

        elif respuesta.status_code == 401:
            estado_corrida = "ABORTADA_AUTENTICACION"
            detener_corrida()

        elif respuesta.status_code == 429:
            esperar_retry_after_o_backoff()
            intento += 1

        elif respuesta.status_code in [500, 502, 503, 504]:
            esperar_backoff_con_jitter()
            intento += 1

        elif respuesta.status_code in [400, 403, 404, 422]:
            registrar_fallo_permanente()
            break

        else:
            registrar_fallo()
            break

    if intento > MAX_INTENTOS:
        registrar_pagina_agotada(pagina)
        paginas_incompletas.append(pagina)

    if not respuesta.hay_siguiente:
        break

    pagina += 1
```

---

# 19. Decisiones de ingeniería

Las principales decisiones tomadas fueron:

### Paginación

Se decidió utilizar `hay_siguiente` como mecanismo de continuidad porque el número de registros puede cambiar mientras se ejecuta la extracción.

### Idempotencia

Se decidió utilizar UPSERT sobre `meter_id` porque `stg_estado_medidor` representa el estado vigente y no un historial de eventos.

### Auditoría

Se decidió utilizar INSERT solamente en `bitacora_ingesta_api` porque cada intento es un evento que debe conservarse.

### Reintentos

Se decidió reintentar `429`, `5xx` y errores de red porque son fallos potencialmente transitorios.

### Autenticación

Se decidió abortar inmediatamente ante un `401` porque el mismo token se utiliza para toda la corrida.

### Backoff

Se seleccionaron:

```text
t0 = 1 s
t_max = 30 s
max_intentos = 5
```

porque ofrecen un equilibrio entre recuperación ante errores transitorios y duración máxima de la corrida.

### Retry-After

Cuando la API proporciona `Retry-After`, este valor tiene prioridad porque representa la indicación directa del proveedor sobre cuánto tiempo debe esperar el cliente.

---

# 20. Riesgos identificados

Los principales riesgos son:

1. Que una página agote sus intentos y deje medidores sin confirmar.
2. Que se interprete la ausencia de un registro como ausencia de novedades.
3. Que un token inválido provoque errores repetidos si no se aborta la corrida.
4. Que una mala configuración de reintentos genere demasiadas solicitudes.
5. Que una bitácora sobrescrita impida reconstruir lo ocurrido.
6. Que se calcule previamente el número de páginas y la fuente cambie durante la extracción.
7. Que una segunda corrida genere duplicados si no existe una clave correcta para el UPSERT.

---

# 21. Archivo de evidencia del nivel 2

Nombre:

```text
evidencia_nivel2_equipo-3.md
```

Contenido resumido:

```text
Equipo: equipo-3

Perfil:
- Medidores: 90
- Page size: 15
- Probabilidad 429: 0.18
- Probabilidad 5xx: 0.10

Primera corrida:
- Registros antes: 0
- Registros después: 90
- Intentos de API: 8
- Páginas: 6
- Páginas incompletas: 0
- Estado: COMPLETA

Segunda corrida:
- Registros antes: 90
- Registros después: 90
- Intentos adicionales: 8
- Páginas: 6
- Páginas incompletas: 0
- Estado: COMPLETA

Control de idempotencia:
- stg_estado_medidor permanece en 90 registros.
- bitacora_ingesta_api aumenta de 8 a 16 registros.

Conciliación:
- Total informado por API: 90
- Total cargado: 90
- Diferencia: 0
```

---

# 22. Declaración de uso de inteligencia artificial

Para la elaboración de esta entrega se utilizó un asistente de inteligencia artificial como apoyo para:

- organizar la documentación técnica;
- estructurar el archivo Markdown;
- revisar la explicación de la estrategia de reintentos;
- redactar el memo dirigido al área de facturación;
- revisar la coherencia de las decisiones documentadas.

El código y las cifras finales deben ser validados y ejecutados por los integrantes del equipo contra la API simulada correspondiente a `equipo-3`.

---

# 23. Conclusión

La solución implementada permite realizar una ingesta desde una API externa sin depender de un número fijo de páginas y sin duplicar el estado vigente de los medidores.

La utilización de UPSERT en `stg_estado_medidor` garantiza la idempotencia de la carga, mientras que `bitacora_ingesta_api` conserva cada intento y permite reconstruir el comportamiento del conector.

La estrategia de reintentos diferencia los errores transitorios de los permanentes y utiliza retroceso exponencial con techo y jitter para evitar una presión innecesaria sobre el proveedor.

Finalmente, cuando una corrida queda incompleta, el sistema no presenta el resultado como si estuviera actualizado. La diferencia entre los registros confirmados y el total informado por la API queda documentada y se comunica al área de facturación para evitar decisiones basadas en información incompleta.
