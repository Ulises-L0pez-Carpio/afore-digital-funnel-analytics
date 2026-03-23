\# Medidas DAX clave



Este documento resume las medidas DAX principales del dashboard del caso \*\*Afore Digital Funnel Analytics\*\*.



\## Nota importante



Las medidas que aparecen a continuación están redactadas como una propuesta consistente con el dashboard construido.  

Es posible que en tu archivo `.pbix` cambien los nombres de tablas o columnas.  

Por ello, estas fórmulas deben adaptarse al modelo exacto cargado en Power BI.



Para efectos de documentación, se asume una tabla principal tipo `Journey\_Master` con granularidad de 1 fila por `journey\_id`.



\---



\## 1. Medidas base de volumen



\### Total de journeys



&#x20;   Total Journeys =

&#x20;   DISTINCTCOUNT ( Journey\_Master\[journey\_id] )



\### Total de leads



&#x20;   Total Leads =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[is\_lead] = 1

&#x20;   )



\### Total de registros



&#x20;   Total Registros =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[is\_registered] = 1

&#x20;   )



\### Total de activaciones



&#x20;   Total Activaciones =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[is\_activated] = 1

&#x20;   )



\### Total de activaciones consolidadas



&#x20;   Total Activaciones Consolidadas =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[is\_consolidated] = 1

&#x20;   )



\---



\## 2. Medidas de tasa



\### Tasa de lead



&#x20;   Tasa Lead =

&#x20;   DIVIDE ( \[Total Leads], \[Total Journeys] )



\### Tasa de registro



&#x20;   Tasa Registro =

&#x20;   DIVIDE ( \[Total Registros], \[Total Journeys] )



\### Tasa de activación final



&#x20;   Tasa Activación Final =

&#x20;   DIVIDE ( \[Total Activaciones], \[Total Journeys] )



\### Tasa de activación consolidada



&#x20;   Tasa Activación Consolidada =

&#x20;   DIVIDE ( \[Total Activaciones Consolidadas], \[Total Journeys] )



\### Tasa lead a registro



&#x20;   Tasa Lead a Registro =

&#x20;   DIVIDE ( \[Total Registros], \[Total Leads] )



\### Tasa registro a activación



&#x20;   Tasa Registro a Activación =

&#x20;   DIVIDE ( \[Total Activaciones], \[Total Registros] )



\---



\## 3. Medidas de ingreso y valor



\### Ingreso estimado total



&#x20;   Ingreso Estimado Total =

&#x20;   SUM ( Journey\_Master\[estimated\_annual\_revenue] )



\### Ingreso promedio por activación



&#x20;   Ingreso Promedio por Activación =

&#x20;   DIVIDE ( \[Ingreso Estimado Total], \[Total Activaciones] )



\### Saldo estimado a 12 meses



&#x20;   Saldo Estimado 12 Meses =

&#x20;   SUM ( Journey\_Master\[estimated\_balance\_12m] )



\### Aportación mensual estimada total



&#x20;   Aportación Mensual Estimada Total =

&#x20;   SUM ( Journey\_Master\[estimated\_monthly\_contribution] )



\---



\## 4. Medidas de retención



\### Usuarios retenidos a 7 días



&#x20;   Usuarios Retenidos 7d =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[retained\_7d\_flag] = 1

&#x20;   )



\### Usuarios retenidos a 30 días



&#x20;   Usuarios Retenidos 30d =

&#x20;   CALCULATE (

&#x20;       DISTINCTCOUNT ( Journey\_Master\[journey\_id] ),

&#x20;       Journey\_Master\[retained\_30d\_flag] = 1

&#x20;   )



\### Retención a 7 días



&#x20;   Retención 7d =

&#x20;   DIVIDE ( \[Usuarios Retenidos 7d], \[Total Activaciones] )



\### Retención a 30 días



&#x20;   Retención 30d =

&#x20;   DIVIDE ( \[Usuarios Retenidos 30d], \[Total Activaciones] )



\---



\## 5. Medidas para campañas



\### Ingreso estimado por campaña



&#x20;   Ingreso Estimado por Campaña =

&#x20;   SUM ( Journey\_Master\[estimated\_annual\_revenue] )



\### Tasa de activación por campaña



&#x20;   Tasa Activación por Campaña =

&#x20;   DIVIDE ( \[Total Activaciones], \[Total Journeys] )



\### Costo por activación



&#x20;   Costo por Activación =

&#x20;   DIVIDE (

&#x20;       SUM ( Journey\_Master\[budget\_amount] ),

&#x20;       \[Total Activaciones]

&#x20;   )



\### ROAS estimado



&#x20;   ROAS Estimado =

&#x20;   DIVIDE (

&#x20;       \[Ingreso Estimado Total],

&#x20;       SUM ( Journey\_Master\[budget\_amount] )

&#x20;   )



Si el presupuesto vive en una dimensión de campañas y no en la tabla maestra, esta medida debe recalcularse sobre esa tabla.



\---



\## 6. Medidas para segmentación



\### Tasa de activación



&#x20;   Tasa de Activación =

&#x20;   DIVIDE ( \[Total Activaciones], \[Total Journeys] )



Esta medida es la base de varios visuales de la página 3:



\- tasa de activación por dispositivo;

\- tasa de activación por rango de edad;

\- matriz canal × dispositivo.



\### Lead quality score promedio



&#x20;   Lead Quality Score Promedio =

&#x20;   AVERAGE ( Journey\_Master\[lead\_quality\_score] )



\### Ingreso estimado por estado



&#x20;   Ingreso Estimado por Estado =

&#x20;   SUM ( Journey\_Master\[estimated\_annual\_revenue] )



\---



\## 7. Medidas temporales



\### Activaciones por mes



&#x20;   Activaciones por Mes =

&#x20;   \[Total Activaciones]



Se utiliza junto con el eje temporal del modelo de fechas o con la columna de mes correspondiente.



\### Leads por mes



&#x20;   Leads por Mes =

&#x20;   \[Total Leads]



\### Registros por mes



&#x20;   Registros por Mes =

&#x20;   \[Total Registros]



\---



\## 8. Medida para funnel por etapa



Si el visual de embudo se alimenta de una tabla de etapas, puede usarse una medida tipo `SWITCH` como esta:



&#x20;   Journeys por Etapa =

&#x20;   SWITCH (

&#x20;       SELECTEDVALUE ( Dim\_Funnel\_Stage\[stage\_name] ),

&#x20;       "Atracción", \[Total Journeys],

&#x20;       "Interacción", CALCULATE ( DISTINCTCOUNT ( Journey\_Master\[journey\_id] ), Journey\_Master\[is\_interaction] = 1 ),

&#x20;       "Generación de lead", \[Total Leads],

&#x20;       "Lead calificado", CALCULATE ( DISTINCTCOUNT ( Journey\_Master\[journey\_id] ), Journey\_Master\[is\_qualified\_lead] = 1 ),

&#x20;       "Inicio de registro", CALCULATE ( DISTINCTCOUNT ( Journey\_Master\[journey\_id] ), Journey\_Master\[is\_registration\_started] = 1 ),

&#x20;       "Registro completado", \[Total Registros],

&#x20;       "Activación digital", \[Total Activaciones],

&#x20;       "Activación consolidada", \[Total Activaciones Consolidadas]

&#x20;   )



Esta medida debe adaptarse a las banderas reales de tu modelo.



\---



\## 9. Medidas de apoyo para tarjetas narrativas



\### Mayor ingreso por canal



&#x20;   Canal Top Ingreso =

&#x20;   TOPN (

&#x20;       1,

&#x20;       VALUES ( Journey\_Master\[channel\_name] ),

&#x20;       \[Ingreso Estimado Total],

&#x20;       DESC

&#x20;   )



\### Campaña top por activaciones



&#x20;   Campaña Top Activaciones =

&#x20;   TOPN (

&#x20;       1,

&#x20;       VALUES ( Journey\_Master\[campaign\_name] ),

&#x20;       \[Total Activaciones],

&#x20;       DESC

&#x20;   )



Estas medidas pueden requerir una versión textual adicional si quieres construir tarjetas o narrativas dinámicas.



\---



\## 10. Medidas más importantes por página



\### Página 1 · Resumen del funnel digital

\- `Total Journeys`

\- `Total Leads`

\- `Total Registros`

\- `Total Activaciones`

\- `Tasa Activación Final`

\- `Ingreso Estimado Total`

\- `Total Activaciones Consolidadas`

\- `Journeys por Etapa`



\### Página 2 · Desempeño de campañas digitales

\- `Total Journeys`

\- `Total Leads`

\- `Total Registros`

\- `Total Activaciones`

\- `Tasa Activación por Campaña`

\- `Ingreso Estimado por Campaña`

\- `Costo por Activación`

\- `ROAS Estimado`



\### Página 3 · Desempeño por segmentos

\- `Tasa de Activación`

\- `Ingreso Estimado por Estado`

\- `Lead Quality Score Promedio`

\- `Total Journeys`

\- `Total Activaciones`



\### Página 4 · Activación y valor de negocio

\- `Total Activaciones`

\- `Usuarios Retenidos 7d`

\- `Retención 7d`

\- `Retención 30d`

\- `Ingreso Estimado Total`

\- `Ingreso Promedio por Activación`

\- `Saldo Estimado 12 Meses`



\## Conclusión



Estas medidas resumen la lógica de negocio más importante del dashboard.  

Su propósito no es solo alimentar visuales, sino traducir el funnel digital a métricas comprensibles para negocio, adquisición, activación y valor económico final.

