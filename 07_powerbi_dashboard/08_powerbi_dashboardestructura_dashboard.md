\# Estructura del dashboard



Este documento describe la lógica de construcción del dashboard en Power BI del caso \*\*Afore Digital Funnel Analytics\*\*.



\## Objetivo de la estructura



La estructura del dashboard fue diseñada para responder una secuencia lógica de análisis:



1\. entender el funnel completo;

2\. identificar qué campañas explican el desempeño;

3\. analizar qué segmentos convierten mejor;

4\. evaluar activación, retención y valor económico.



Por ello, el dashboard quedó organizado en cuatro páginas.



\---



\## Página 1 · Resumen ejecutivo del funnel digital



\### Propósito

Dar una lectura inmediata del funnel completo y de sus principales puntos de fuga.



\### Elementos visibles

\- selector de periodo;

\- tarjetas de KPI:

&#x20; - total de journeys;

&#x20; - total de leads;

&#x20; - total de registros;

&#x20; - total de activaciones;

&#x20; - tasa de activación final;

&#x20; - ingreso estimado total;

\- bloque de hallazgos clave;

\- gráfico de embudo por etapa;

\- gráfico temporal de leads, registros y activaciones por mes.



\### Qué responde esta página

\- ¿Qué tamaño tiene el funnel?

\- ¿Cuántos usuarios llegan hasta registro y activación?

\- ¿Cuál es la tasa final de activación?

\- ¿Dónde está la mayor fuga?

\- ¿Cómo evoluciona el funnel a lo largo del tiempo?



\### Lógica de lectura

La página abre con KPI de volumen y resultado.  

Después introduce hallazgos narrativos para resumir la interpretación principal.  

Finalmente muestra el funnel completo y la evolución mensual para combinar lectura estática y temporal.



\### Valor analítico

Esta página cumple la función de portada ejecutiva del dashboard.



\---



\## Página 2 · Desempeño de campañas digitales



\### Propósito

Evaluar la contribución de campañas y canales al funnel, tanto en volumen como en activación e ingreso estimado.



\### Elementos visibles

\- filtros por canal y campaña;

\- gráfico Top 5 campañas por ingreso estimado;

\- tabla de detalle por campaña con:

&#x20; - canal;

&#x20; - journeys;

&#x20; - leads;

&#x20; - registros;

&#x20; - activaciones;

&#x20; - tasa de activación;

&#x20; - ingreso estimado;

\- gráfico de leads por campaña;

\- gráfico de ingreso estimado por campaña;

\- gráfico de activaciones por campaña;

\- gráfico de journeys por campaña.



\### Qué responde esta página

\- ¿Qué campañas generan más ingreso estimado?

\- ¿Qué campañas generan más leads?

\- ¿Qué campañas logran más activaciones?

\- ¿Qué campañas aportan más journeys?

\- ¿Existe diferencia entre campañas de alto volumen y campañas de alta eficiencia?



\### Lógica de lectura

Primero se presenta una síntesis con el Top 5 por ingreso estimado.  

Después se incluye una tabla comparativa para lectura más detallada.  

Finalmente se abren comparativos separados por journeys, leads, activaciones e ingreso.



\### Decisiones de diseño

\- uso de \*\*Top 5\*\* en los rankings más ejecutivos;

\- tablas con formato condicional para ingreso estimado;

\- orden descendente en gráficos de barras;

\- filtros laterales para explorar campañas y canales sin saturar la página.



\### Valor analítico

Esta página conecta directamente el funnel con la lógica de adquisición y eficiencia comercial.



\---



\## Página 3 · Desempeño por segmentos



\### Propósito

Analizar cómo cambia la activación y el ingreso estimado según características del usuario y del contexto digital.



\### Elementos visibles

\- filtros por:

&#x20; - estado;

&#x20; - rango de edad;

&#x20; - segmento;

&#x20; - nivel de intención;

\- gráfico de tasa de activación por dispositivo;

\- gráfico de ingreso estimado por estado;

\- matriz de desempeño por canal y dispositivo con:

&#x20; - journeys;

&#x20; - activaciones;

&#x20; - tasa de activación;

\- gráfico de tasa de activación por rango de edad.



\### Qué responde esta página

\- ¿Qué dispositivo convierte mejor?

\- ¿Qué estados aportan más ingreso estimado?

\- ¿Qué rangos de edad muestran mejor activación?

\- ¿Qué combinaciones canal-dispositivo tienen mejor o peor desempeño?

\- ¿Cómo cambia el resultado cuando se filtra por segmento o nivel de intención?



\### Lógica de lectura

La página inicia con filtros de perfil y contexto.  

Después compara activación por dispositivo e ingreso por estado.  

La matriz central permite una lectura más rica al cruzar canal y dispositivo.  

Finalmente, el gráfico por rango de edad aporta una vista demográfica complementaria.



\### Decisiones de diseño

\- matriz con formato condicional para facilitar lectura comparativa;

\- combinación de análisis geográfico, demográfico y digital;

\- uso de segmentadores laterales para permitir exploración flexible.



\### Valor analítico

Esta página es la capa de segmentación del dashboard y ayuda a identificar perfiles y combinaciones con mayor valor analítico.



\---



\## Página 4 · Activación y valor de negocio



\### Propósito

Cerrar el dashboard con una lectura de resultado final, permanencia inicial y valor económico estimado.



\### Elementos visibles

\- selector de periodo;

\- tarjetas de KPI:

&#x20; - total de activaciones;

&#x20; - usuarios retenidos a 7 días;

&#x20; - retención a 7 días;

&#x20; - retención a 30 días;

\- gráfico de activaciones por mes;

\- tarjetas de valor:

&#x20; - ingreso anual estimado total;

&#x20; - ingreso anual estimado promedio por activación;

&#x20; - saldo estimado a 12 meses;

\- tabla de journeys con:

&#x20; - aportación mensual estimada;

&#x20; - saldo estimado a 12 meses;

&#x20; - ingreso anual estimado;

\- gráfico de activaciones por canal de activación.



\### Qué responde esta página

\- ¿Cuántos usuarios activados realmente se retienen?

\- ¿Cómo evoluciona la activación mes a mes?

\- ¿Cuál es el ingreso estimado total asociado a la activación?

\- ¿Cuál es el valor promedio por activación?

\- ¿Qué canal de activación concentra mayor volumen?



\### Lógica de lectura

La página abre con KPI de activación y retención.  

Después muestra la evolución temporal.  

Más abajo traduce la activación a indicadores de valor económico.  

Finalmente ofrece detalle a nivel journey y un comparativo por canal de activación.



\### Decisiones de diseño

\- separación visual entre KPI de activación y KPI de valor;

\- tabla inferior para detalle trazable;

\- gráfico horizontal para canal de activación por claridad de lectura.



\### Valor analítico

Esta página cierra el dashboard en términos de negocio: no solo cuántos activan, sino cuánto valor estimado generan y qué tan sostenible parece esa activación en el corto plazo.



\---



\## Relación entre páginas



La navegación del dashboard sigue esta secuencia:



\- \*\*Página 1:\*\* visión global del funnel;

\- \*\*Página 2:\*\* diagnóstico de campañas;

\- \*\*Página 3:\*\* diagnóstico por segmentos;

\- \*\*Página 4:\*\* resultado final y valor económico.



Esto permite que el usuario pase de una lectura descriptiva a una lectura explicativa y, finalmente, a una lectura orientada a valor.



\## Conclusión de diseño



La estructura del dashboard busca equilibrar:



\- claridad ejecutiva;

\- capacidad de exploración;

\- consistencia visual;

\- conexión con el caso de negocio.



No se diseñó como un tablero operativo de monitoreo en tiempo real, sino como un dashboard de análisis ejecutivo para presentar hallazgos y demostrar capacidades analíticas dentro del portafolio.

