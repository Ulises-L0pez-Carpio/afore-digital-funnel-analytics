# Fase 5 · SQL analítico: segmentación, campañas y KPIs ejecutivos



Esta carpeta contiene el bloque de **SQL analítico orientado a negocio** del caso de estudio **Afore Digital Funnel Analytics**.



El objetivo de esta fase es traducir la base técnica del funnel a preguntas ejecutivas sobre desempeño comercial, calidad de campañas, eficiencia de canales, comportamiento por segmento y generación estimada de valor.



## Objetivo de la fase



Después de construir la base del funnel en la fase 4, esta etapa busca responder preguntas como:



\- ¿Qué canales convierten mejor?

\- ¿Qué dispositivos muestran más fricción o mejor desempeño?

\- ¿Qué regiones presentan mejor activación?

\- ¿Qué segmentos generan más valor?

\- ¿Qué campañas son más eficientes en costo y revenue?

\- ¿Cómo evoluciona el funnel en el tiempo?

\- ¿Qué KPIs debería monitorear un dashboard ejecutivo?



## Motor y unidad de análisis



\- **Motor asumido:** SQLite

\- **Unidad base del análisis:** `journey\_id`



Aunque la mayor parte del análisis se resume a nivel de journey, el script también incorpora consultas específicas sobre sesiones para evaluar engagement digital por campaña.



## Archivo principal



\- [`05\_sql\_analytics\_funnel\_afore.sql`](./05\_sql\_analytics\_funnel\_afore.sql)



## Estructura del script



El archivo está dividido en doce bloques analíticos principales.



### 0. Capa base analítica reutilizable



Se crea una vista temporal llamada `vw_journey_base`.



Esta vista concentra, por `journey_id`:



\- fechas y periodización temporal;

\- campaña y canal;

\- atributos del prospecto;

\- tipo de usuario;

\- dispositivo del primer contacto;

\- flags de lead, registro, activación y consolidación;

\- revenue estimado;

\- timestamps para medir tiempos de conversión.



Esta vista sirve como capa base del resto del bloque y evita repetir la misma lógica de joins, estandarización y derivación de variables en cada consulta posterior.



## Bloques analíticos incluidos



### 1. Conversión por canal



Evalúa qué canales generan:



\- más journeys;

\- más leads;

\- más registros;

\- más activaciones;

\- mejor conversión end-to-end;

\- mayor revenue anual estimado.



Este bloque permite identificar qué fuentes de adquisición no solo aportan volumen, sino también eficiencia de conversión y valor potencial.



### 2. Conversión por dispositivo



Compara desempeño entre:



\- tipo de dispositivo;

\- sistema operativo;

\- entorno app/web.



Además incorpora:



\- calidad promedio del lead;

\- revenue anual estimado.



Este análisis ayuda a detectar fricciones de experiencia digital, especialmente en etapas sensibles como registro y activación.



### 3. Conversión por región



Analiza diferencias por `geo_state`, filtrando regiones con al menos 100 journeys para evitar conclusiones sobre muestras demasiado pequeñas.



Este bloque sirve para identificar variaciones geográficas en:



\- volumen;

\- generación de lead;

\- registro;

\- activación;

\- revenue.



### 4. Análisis por tipo de usuario y segmento



Compara:



\- cliente existente vs prospecto nuevo;

\- segmento comercial;

\- nivel de intención.



Mide:



\- volumen;

\- calidad de lead;

\- registro;

\- activación;

\- revenue.



Este análisis es especialmente útil para entender qué perfiles de usuario presentan mayor potencial de conversión y valor económico.



### 5. Revenue por canal



Estima el valor económico por canal a través de:



\- contribución mensual estimada;

\- balance estimado a 12 meses;

\- revenue anual estimado;

\- revenue por activación.



Este bloque permite pasar de una lectura de conversión a una lectura de \*\*valor de negocio\*\*, distinguiendo entre canales que convierten y canales que además generan mejor rendimiento económico.



### 6. Costo por conversión por campaña



Usa `budget_amount` como costo estimado de campaña para calcular:



\- costo por lead;

\- costo por registro;

\- costo por activación;

\- ROAS ratio.



Este bloque permite evaluar la eficiencia de inversión publicitaria de forma comparable entre campañas.



### 7. Calidad de campaña



Clasifica campañas con base en:



\- tasa de calificación;

\- `lead_quality_score` promedio;

\- tasa lead → activación;

\- revenue anual estimado.



Además crea buckets interpretables como:



\- `Top quality`

\- `Good`

\- `Average`

\- `Low quality`



Este bloque es muy valioso para separar campañas de alto volumen de campañas de verdadera calidad comercial.



### 8. Calidad de engagement por campaña



Mide interacción digital a nivel sesión mediante:



\- `pageviews` promedio;

\- clics promedio en CTA;

\- tasa de interacción calificada;

\- bounce rate.



Este análisis ayuda a evaluar si la campaña genera solo tráfico o también interacción relevante.



### 9. Comparativo temporal mensual



Resume la evolución mensual del funnel mediante:



\- journeys;

\- leads;

\- registros;

\- activaciones;

\- consolidación;

\- revenue anual estimado.



Este bloque permite observar tendencias y comparativos temporales en desempeño del funnel.



### 10. KPI ejecutivo general



Construye una lectura global del funnel con indicadores como:



\- volumen total;

\- conversión por etapa;

\- activación end-to-end;

\- consolidación;

\- revenue total;

\- revenue por activación;

\- tiempo promedio de lead a registro;

\- tiempo promedio de registro a activación.



Este bloque funciona como base conceptual para la página ejecutiva del dashboard.



### 11. Top campañas ejecutivas



Genera un ranking de campañas por:



\- revenue;

\- activaciones;

\- journeys;

\- revenue por activación.



Su propósito es identificar campañas prioritarias desde la perspectiva de negocio.



### 12. Resumen ejecutivo por segmento



Muestra qué segmentos y tipos de usuario combinan mejor:



\- volumen;

\- activación;

\- calidad de lead;

\- valor económico estimado.



Este bloque facilita una lectura estratégica sobre qué perfiles deberían recibir mayor atención comercial o mayor inversión de adquisición.



## Preguntas de negocio que responde esta fase



La fase 5 permite responder, de forma estructurada, preguntas clave como:



\- qué canales deben priorizarse por eficiencia;

\- qué campañas generan volumen pero no calidad;

\- qué segmentos aportan mayor valor;

\- dónde existe más fricción en la conversión;

\- qué tan rentable parece cada fuente de adquisición;

\- qué lectura temporal puede hacerse del funnel.



## Métricas principales utilizadas



Entre las métricas calculadas en este bloque destacan:



\- `visit_to_lead_rate_pct`

\- `lead_qualification_rate_pct`

\- `lead_to_registration_rate_pct`

\- `registration_to_activation_rate_pct`

\- `end_to_end_activation_rate_pct`

\- `activation_to_consolidation_rate_pct`

\- `annual_revenue`

\- `revenue_per_activation`

\- `cost_per_lead`

\- `cost_per_registration`

\- `cost_per_activation`

\- `roas_ratio`



## Valor analítico de esta fase



Esta fase demuestra capacidad para:



\- diseñar una capa reusable de análisis;

\- transformar variables operativas en KPIs ejecutivos;

\- comparar campañas, canales y segmentos;

\- analizar eficiencia comercial y calidad de adquisición;

\- traducir datos a decisiones de negocio.



## Cómo ejecutar esta fase



1\. Abrir la base sintética ubicada en `../03\_synthetic\_data/`.

2\. Asegurarse de que las tablas utilizadas por el script estén disponibles.

3\. Ejecutar `05\_sql\_analytics\_funnel\_afore.sql` en SQLite.

4\. Revisar primero la creación de la vista `vw\_journey\_base`.

5\. Ejecutar los bloques analíticos según la pregunta de negocio de interés.



## Resultados esperados



Al ejecutar correctamente esta fase se obtiene:



\- una vista base reutilizable para análisis ejecutivo;

\- comparativos de conversión por canal, dispositivo, región y segmento;

\- métricas de revenue y costo por conversión;

\- evaluación de calidad de campañas;

\- análisis temporal del funnel;

\- KPIs listos para traducirse a dashboard o storytelling ejecutivo.



## Relación con otras fases del proyecto



Esta fase se conecta directamente con:



\- \[`../04\_sql\_base/`](../04\_sql\_base/) como base técnica previa del funnel;

\- \[`../06\_python\_eda/`](../06\_python\_eda/) para exploración visual complementaria;

\- \[`../07\_powerbi\_dashboard/`](../08\_powerbi\_dashboard/) para el dashboard ejecutivo;



## Archivo relacionado



\- \[Ver script SQL analítico](./05\_sql\_analytics\_funnel\_afore.sql)



## Nota



Este análisis fue desarrollado sobre una base sintética con fines de portafolio profesional.  

No representa datos internos de una institución financiera específica.

