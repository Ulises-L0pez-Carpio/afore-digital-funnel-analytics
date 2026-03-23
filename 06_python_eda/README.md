# Python: análisis exploratorio y visualizaciones



Esta carpeta contiene la fase de **análisis exploratorio de datos (EDA)** y visualización en Python del caso de estudio **Afore Digital Funnel Analytics**.



El objetivo de esta etapa es transformar la base analítica del funnel en hallazgos visuales y comparativos que ayuden a entender el comportamiento de usuarios, campañas, canales, segmentos y dispositivos dentro del proceso de captación, registro y activación digital.



## Objetivo de la fase



Esta fase busca responder preguntas como:



\- ¿Cómo se comporta el funnel completo de journeys a activación consolidada?

\- ¿Dónde se concentra la mayor fuga entre etapas?

\- ¿Qué canales muestran mejor desempeño?

\- ¿Qué dispositivos presentan mayor fricción?

\- ¿Qué segmentos convierten mejor?

\- ¿Qué campañas generan más activaciones y mejor eficiencia?

\- ¿Qué patrones de revenue y tiempo entre etapas pueden observarse?



## Fuente de datos



El análisis se ejecuta sobre la base SQLite del proyecto (renombrada para el notebook):



\- `synthetic_afore_funnel.db`



El script contempla dos rutas posibles para localizar la base y detiene la ejecución si el archivo no existe.



## Archivos principales



\- [`01\_eda\_funnel\_afore.ipynb`](./01\_eda\_funnel\_afore.ipynb)

\- [`02\_eda\_funnel\_afore.py`](./02\_eda\_funnel\_afore.py)





## Qué hace el script



El archivo `02_eda_funnel_afore.py` implementa un flujo completo de análisis exploratorio y visualización. La lógica está organizada en nueve bloques principales.



### 1. Carga de tablas



Se cargan las tablas principales del caso desde SQLite:



\- `users`

\- `sessions`

\- `campaigns`

\- `conversions`

\- `funnel_events`

\- `FACT_JOURNEY`

\- `DIM_CHANNEL`

\- `DIM_DEVICE`



También se genera una revisión inicial del tamaño de las tablas.



### 2. Parseo ligero de fechas



Se convierten columnas de fecha y timestamp a tipo datetime para permitir análisis temporal y cálculos de tiempos entre etapas.



### 3. Construcción del dataset maestro a nivel journey



Se construye un dataset llamado `journey_master` a partir de merges entre:



\- conversiones;

\- journeys;

\- usuarios;

\- dimensiones de canal;

\- dimensiones de dispositivo;

\- campañas.



La granularidad resultante es **1 fila por `journey_id`**.



Este dataset concentra en una sola estructura:



\- canal;

\- dispositivo;

\- campaña;

\- segmento;

\- intención;

\- flags de lead, registro y activación;

\- revenue anual estimado.



### 4. Limpieza ligera y métricas base



Se validan:



\- duplicados en `journey_id`;

\- nulos en columnas analíticas clave.



Además se construyen KPIs generales como:



\- journeys totales;

\- leads;

\- registros completados;

\- activaciones digitales;

\- activaciones consolidadas;

\- revenue anual estimado;

\- revenue promedio por activación.



### 5. Funnel visual



Se calcula el funnel completo a partir de `funnel_events`, incluyendo:



\- journeys por etapa;

\- conversión entre etapas;

\- conversión end-to-end;

\- caída absoluta;

\- caída porcentual.



Además se generan visualizaciones para:



\- volumen por etapa;

\- conversión entre etapas.



### 6. EDA de sesiones



Se analiza el comportamiento de sesiones mediante métricas como:



\- sesiones totales;

\- journeys con más de una sesión;

\- pageviews promedio;

\- clics promedio en CTA;

\- bounce rate;

\- tasa de interacción calificada.



También se construye un comparativo por canal para evaluar engagement.



### 7. Comparación por segmentos



A partir de `journey_master` se generan tablas de desempeño por:



\- canal;

\- dispositivo;

\- segmento;

\- banda de intención;

\- estado.



Para cada agrupación se calculan métricas como:



\- journeys;

\- leads;

\- registros;

\- activaciones;

\- consolidados;

\- revenue;

\- calidad promedio del lead;

\- tasas de lead, registro, activación y consolidación.



También se generan visualizaciones para:



\- activación por canal;

\- conversión por dispositivo;

\- activación por segmento;

\- activación por banda de intención;

\- heatmap de activación canal vs dispositivo.



### 8. Revenue y eficiencia de campañas



Se construye una tabla de desempeño de campañas con métricas como:



\- journeys;

\- activaciones;

\- activation rate;

\- budget amount;

\- cost per activation;

\- ROAS proxy;

\- revenue total.



Además se generan visualizaciones para:



\- revenue anual estimado por canal;

\- top campañas por activaciones;

\- campañas con menor costo por activación.



### 9. Tiempo entre etapas y hallazgos automáticos



Se calcula el tiempo promedio y mediano entre etapas usando `time_from_previous_stage_minutes`.



Finalmente, el script genera hallazgos automáticos sobre:



\- tamaño del funnel;

\- mayor fuga absoluta;

\- mejor y peor canal;

\- mejor y peor segmento;

\- mejor dispositivo;

\- canal con mayor revenue;

\- campaña con más activaciones.



## Principales variables analizadas



Entre las variables más relevantes del análisis se encuentran:



\- `channel_name`

\- `device_type`

\- `campaign_name`

\- `segment_label`

\- `intent_band`

\- `geo_state`

\- `lead_quality_score`

\- `is_lead`

\- `is_registered`

\- `is_activated`

\- `is_consolidated`

\- `estimated_annual_revenue`



## Visualizaciones generadas



El análisis produce visualizaciones orientadas a negocio, entre ellas:



\- funnel digital por etapa;

\- conversión entre etapas;

\- bounce rate por canal;

\- tasa de activación por canal;

\- conversión por dispositivo;

\- tasa de activación por segmento;

\- tasa de activación por banda de intención;

\- heatmap canal vs dispositivo;

\- revenue anual estimado por canal;

\- top campañas por activaciones;

\- campañas con menor costo por activación;

\- mediana de horas entre etapas.



## Valor analítico de esta fase



Esta etapa demuestra capacidad para:



\- cargar y manipular datos en Python;

\- integrar múltiples tablas del modelo;

\- construir un dataset maestro de análisis;

\- realizar exploración estructurada del funnel;

\- comparar segmentos y dimensiones de negocio;

\- traducir resultados cuantitativos a visualizaciones claras;

\- automatizar hallazgos relevantes para presentación ejecutiva o entrevista.



## Cómo ejecutar esta fase



1\. Colocar la base `synthetic_afore_funnel.db` en la ruta esperada.

2\. Instalar dependencias 

3\. Ejecutar el notebook o el script `02_eda_funnel_afore.py`.

4\. Revisar tablas resumen, gráficas y hallazgos finales.





## Relación con otras fases del proyecto



Esta fase se conecta directamente con:



\- [`../03\_synthetic\_data/`](../03\_synthetic\_data/) como origen de la base;

\- [`../04\_sql\_base/`](../04\_sql\_base/) como capa técnica base del funnel;

\- [`../05\_sql\_analytics/`](../05\_sql\_analytics/) como capa SQL ejecutiva;

\- [`../07\_powerbi\_dashboard/`](../07\_powerbi\_dashboard/) para visualización ejecutiva en Power BI.



## Archivo relacionado



\- [Ver script Python del EDA](./02\_eda\_funnel\_afore.py)

\- [Ver notebook del EDA](./01\_eda\_funnel\_afore.ipynb)



## Nota



Este análisis fue desarrollado sobre una base sintética con fines de portafolio profesional.  

No representa datos internos de una institución financiera específica.

