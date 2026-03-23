# Fase 8 · Dashboard ejecutivo en Power BI



Esta carpeta contiene el dashboard en Power BI del caso de estudio \*\*Afore Digital Funnel Analytics\*\*.



El objetivo de esta fase es traducir el trabajo previo en SQL y Python a una herramienta visual, ejecutiva e interactiva que permita analizar el funnel digital de captación, registro, activación y valor estimado de negocio en un contexto financiero.



## Propósito del dashboard



El dashboard fue diseñado para responder cuatro niveles de lectura de negocio:



1\. \*\*visión general del funnel\*\*;

2\. \*\*desempeño de campañas\*\*;

3\. \*\*desempeño por segmentos\*\*;

4\. \*\*activación y valor económico final\*\*.



Esta estructura permite pasar de una lectura general a una lectura diagnóstica y, finalmente, a una lectura orientada a valor de negocio.



## Estructura del dashboard



El dashboard está compuesto por cuatro páginas:



### 1. Resumen ejecutivo del funnel digital

Presenta la lectura global del embudo, incluyendo:



\- journeys totales;

\- leads;

\- registros;

\- activaciones;

\- tasa final de activación;

\- ingreso estimado total;

\- funnel por etapa;

\- tendencia mensual de leads, registros y activaciones;

\- hallazgos clave resumidos.



### 2. Desempeño de campañas digitales

Se enfoca en campañas y canales, con comparativos sobre:



\- journeys;

\- leads;

\- registros;

\- activaciones;

\- tasa de activación;

\- ingreso estimado;

\- campañas top por ingreso;

\- campañas top por leads;

\- campañas top por activaciones;

\- campañas top por journeys.



### 3. Desempeño por segmentos

Profundiza en diferencias entre perfiles y dimensiones analíticas clave:



\- estado;

\- rango de edad;

\- segmento;

\- nivel de intención;

\- dispositivo;

\- canal.



Incluye además una matriz de desempeño por canal y dispositivo para detectar combinaciones con mejor o peor tasa de activación.



### 4. Activación y valor de negocio

Se concentra en la etapa final del funnel y en el valor estimado posterior a la conversión:



\- total de activaciones;

\- usuarios retenidos a 7 días;

\- retención a 7 días;

\- retención a 30 días;

\- activaciones por mes;

\- ingreso anual estimado total;

\- ingreso anual promedio por activación;

\- saldo estimado a 12 meses;

\- activaciones por canal de activación;

\- tabla de journeys con indicadores de valor.



## Enfoque visual



El dashboard fue construido con una lógica de lectura ejecutiva:



\- primero KPI y contexto;

\- después comparativos principales;

\- luego segmentación;

\- finalmente resultado y valor económico.



Se utilizaron además los siguientes criterios:



\- comparativos en \*\*Top 5\*\* cuando la visualización requería síntesis;

\- orden descendente en gráficos de barras;

\- filtros laterales o superiores según el tipo de análisis;

\- uso de tablas o matrices para detalle complementario;

\- consistencia entre títulos, métricas y narrativa visual.



## Principales métricas mostradas



Entre las métricas más relevantes del dashboard se encuentran:



\- total de journeys;

\- total de leads;

\- total de registros;

\- total de activaciones;

\- total de activaciones consolidadas;

\- tasa de activación final;

\- ingreso estimado total;

\- tasa de activación por canal;

\- tasa de activación por dispositivo;

\- ingreso estimado por campaña;

\- ingreso estimado por estado;

\- retención a 7 días;

\- retención a 30 días;

\- ingreso promedio por activación;

\- saldo estimado a 12 meses.



## Lógica analítica del dashboard



El dashboard se apoya en la lógica construida en fases previas del proyecto:



\- \*\*Fase 4\*\*: base SQL del funnel;

\- \*\*Fase 5\*\*: SQL analítico para campañas, segmentos y KPIs ejecutivos;

\- \*\*Fase 6\*\*: análisis exploratorio y visualizaciones en Python;

\- \*\*Fase 7\*\*: modelo predictivo básico.



Por tanto, este entregable no es una visualización aislada, sino la capa ejecutiva del caso de estudio completo.



## Público objetivo



El dashboard está pensado para:



\- reclutadores de perfiles de datos;

\- hiring managers;

\- líderes de BI o analytics;

\- perfiles de negocio interesados en funnel, campañas y activación.



## Archivos de esta carpeta



\- `afore\_funnel\_dashboard.pbix`

\- `README.md`

\- `estructura\_dashboard.md`

\- `medidas\_dax\_clave.md`


## Relación con otras fases del proyecto



Esta fase se conecta directamente con:



\- `../04\_sql\_base/`

\- `../05\_sql\_analytics/`

\- `../06\_python\_eda/`

## Nota



Este dashboard fue construido sobre una base sintética con fines de portafolio profesional.  

No representa datos internos de una institución financiera específica.

