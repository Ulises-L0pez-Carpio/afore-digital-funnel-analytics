# Fase 4 · SQL base del funnel Afore

Esta carpeta contiene la **base analítica inicial en SQL** del caso de estudio **Afore Digital Funnel Analytics**.

El objetivo de esta fase es transformar las tablas fuente en una estructura limpia, consistente y reutilizable para analizar el funnel digital de captación, registro y activación a nivel de `journey`.

## Objetivo de la fase

Esta etapa resuelve cuatro necesidades fundamentales:

1. validar la calidad básica de las tablas fuente;
2. preparar vistas limpias con lógica de deduplicación;
3. construir una vista maestra del funnel a nivel `journey_id`;
4. calcular métricas base de conversión y abandono.

## Motor y grano de análisis

- **Motor asumido:** SQLite
- **Grano principal de análisis:** 1 fila por `journey_id`

Esta decisión permite reconstruir el recorrido principal del usuario dentro del funnel y consolidar en una sola estructura atributos de adquisición, comportamiento digital, estatus operativo y valor económico estimado.

## Archivo principal

- [`04_sql_base_funnel_afore.sql`](./04_sql_base_funnel_afore.sql)

## Tablas fuente utilizadas

El script trabaja con las siguientes tablas base:

- `users`
- `sessions`
- `campaigns`
- `funnel_events`
- `conversions`

## Estructura del script

El archivo está organizado en seis bloques principales.

### 1. Perfilado rápido de tablas

Se realiza un conteo inicial de registros por tabla para verificar volumen y consistencia básica de las fuentes.

Este bloque sirve para detectar rápidamente desviaciones evidentes antes de entrar a validaciones más detalladas.

### 2. Validaciones de calidad

Se ejecutan validaciones orientadas a detectar problemas estructurales y de consistencia, entre ellos:

- duplicados en llaves esperadas;
- nulos en campos críticos;
- rupturas de integridad referencial;
- repetición indebida de `stage_order` dentro de un mismo `journey_id`;
- inconsistencias entre `current_stage_id` y la última etapa observada del funnel.

Estas revisiones permiten confirmar que la base puede utilizarse como insumo analítico sin sesgos obvios por errores de estructura.

### 3. Limpieza y deduplicación

Se crean vistas temporales limpias para:

- `users`
- `sessions`
- `campaigns`
- `funnel_events`
- `conversions`

Aunque la base sintética no presenta duplicados duros severos, el script deja implementada la lógica de deduplicación como si se tratara de un entorno productivo.


### 4. Joins principales auxiliares

Se construyen vistas intermedias para facilitar el análisis del funnel, incluyendo:

- primera sesión por `journey`;
- agregados de sesiones por `journey`;
- flags de avance por etapa;
- timestamps mínimos por hito del funnel.

Este bloque prepara la información necesaria para consolidar una vista maestra sin repetir lógica en múltiples consultas posteriores.

### 5. Construcción de la vista maestra del funnel

Se genera la vista `VW_SQLBASE_FUNNEL_MASTER`.

Esta es la salida analítica central de la fase.

Su granularidad es **1 fila por `journey_id`** e integra:

- atributos del usuario/prospecto;
- información de campaña y canal;
- datos de la primera sesión;
- comportamiento agregado por `journey`;
- estatus operativos;
- timestamps clave;
- flags de conversión;
- flags de avance por etapa;
- tiempos entre hitos;
- valor económico estimado.

## Variables integradas en la vista maestra

La vista maestra concentra variables de cinco bloques principales.

### 1. Dimensión de usuario

Incluye variables como:

- `geo_state`
- `age_band`
- `income_band`
- `segment_label`
- `intent_band`
- `lead_quality_score`
- `is_existing_customer`

### 2. Dimensión de adquisición

Incluye información de:

- campaña;
- canal;
- fuente;
- medio;
- plataforma;
- tipo de campaña;
- estatus de campaña.

### 3. Comportamiento digital

Se integran variables como:

- primera sesión;
- landing page inicial;
- pageviews;
- clics en CTA;
- interacción calificada;
- bounce;
- total de sesiones por `journey`.

### 4. Estatus del funnel

Incluye variables relacionadas con:

- lead;
- registro;
- activación;
- consolidación;
- estatus actual del `journey`;
- identificadores operativos relacionados con lead, registro y activación.

### 5. Tiempos y valor económico

Se calculan métricas como:

- minutos de sesión a lead;
- minutos de lead a inicio de registro;
- minutos de inicio a registro completado;
- minutos de registro completado a activación;
- contribución mensual estimada;
- balance estimado a 12 meses;
- revenue anual estimado.

## 6. Métricas base del funnel

A partir de la vista maestra y de los eventos limpios se calculan métricas como:

- volumen por etapa;
- conversión desde etapa previa;
- abandono por etapa;
- conversión general end-to-end;
- abandono antes del lead, entre lead y registro, y entre registro y activación;
- validación final de consistencia del master.

Estas métricas constituyen la lectura inicial del funnel y sirven como base para el análisis ejecutivo posterior.

## Lógica del funnel

El funnel queda estructurado mediante flags y timestamps de avance por etapa, permitiendo reconstruir el paso del usuario por hitos como:

1. atracción  
2. interacción  
3. lead  
4. lead calificado  
5. inicio de registro  
6. registro completado  
7. activación  
8. consolidación

Esta estructura permite medir tanto conversión como abandono entre etapas consecutivas.

## Cómo ejecutar esta fase

1. Abrir la base ubicada en `../03_synthetic_data/`.
2. Ejecutar el archivo `04_sql_base_funnel_afore.sql` en SQLite.
3. Revisar primero las consultas de validación.
4. Verificar la construcción de las vistas temporales limpias.
5. Consultar la vista `VW_SQLBASE_FUNNEL_MASTER`.
6. Ejecutar las métricas base al final del script.

## Resultados esperados

Al ejecutar correctamente esta fase se obtiene:

- una revisión inicial de calidad de datos;
- vistas limpias y deduplicadas;
- una vista maestra analítica del funnel;
- métricas base de conversión y abandono;
- una estructura lista para alimentar fases posteriores de análisis.

## Valor dentro del portafolio

Esta fase demuestra capacidad para:

- validar calidad de datos en SQL;
- aplicar lógica de limpieza y deduplicación;
- integrar múltiples tablas del modelo;
- construir una vista maestra con criterio analítico;
- convertir eventos del funnel en métricas utilizables para negocio.

## Relación con otras fases del proyecto

La salida de esta fase se conecta directamente con:

- [`../05_sql_analytics/`](../05_sql_analytics/) para análisis ejecutivo por canal, segmento y revenue;
- [`../06_python_eda/`](../06_python_eda/) para exploración y visualizaciones;
- [`../07_powerbi_dashboard/`](../07_powerbi_dashboard/) para el dashboard ejecutivo.

## Archivo relacionado

- [Ver script SQL de la fase](./04_sql_base_funnel_afore.sql)

## Nota

Este análisis se desarrolló sobre una base sintética con fines de portafolio profesional.  
No representa datos internos de una institución financiera específica.

