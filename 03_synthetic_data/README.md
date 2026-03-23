#  Dataset sintético de funnel digital Afore

Este dataset fue generado con base en el brief del caso y el DER del proyecto. El objetivo es simular un funnel digital realista para análisis de campañas, conversión, segmentación y activación en una Afore.

## Qué incluye

* **Script principal:** `synthetic\\\_afore\\\_funnel\\\_generator.py`
* **Base SQLite:** `synthetic\\\_afore\\\_funnel.db`
* **CSVs del esquema completo del DER**
* **CSVs simplificados** para análisis rápido:

  * `users.csv`
  * `campaigns.csv`
  * `sessions.csv`
  * `funnel\\\_events.csv`
  * `conversions.csv`
* **Resumen de generación:** `dataset\\\_summary.json`

## Lógica de simulación

La simulación usa una ventana temporal de **2025-01-01 a 2025-12-31** y un enfoque probabilístico por journey:

1. Se generan prospectos con atributos de negocio:

   * estado
   * banda de edad
   * banda de ingreso
   * segmento
   * intención
   * lead quality score
   * cliente existente o no
2. Cada prospecto puede tener **1 a 3 journeys** dependiendo de intención y segmento.
3. Cada journey se asigna a:

   * campaña primaria
   * canal primario
   * dispositivo inicial
   * modelo de atribución
4. El avance por funnel se decide con probabilidades condicionadas por:

   * lead quality score
   * intención
   * segmento
   * objetivo de campaña
   * canal
   * dispositivo
   * uplift de campaña
5. El funnel simulado sigue estas etapas:

   * ST01 Atracción
   * ST02 Interacción
   * ST03 Generación de lead
   * ST04 Lead calificado
   * ST05 Inicio de registro
   * ST06 Registro completado
   * ST07 Activación digital
   * ST08 Activación consolidada
6. La activación consolidada genera un **proxy de revenue estimado** en la tabla/vista `conversions`:

   * `estimated\\\_monthly\\\_contribution`
   * `estimated\\\_12m\\\_balance`
   * `estimated\\\_annual\\\_revenue`

> Nota: ese revenue es una \\\*\\\*métrica proxy sintética\\\*\\\* para fines analíticos y de portafolio; no representa una economía real interna de una institución.

## Tamaño de esta corrida

* Prospectos: 24,000
* Journeys: 26,952
* Sessions: 40,059
* Events: 127,285
* Leads: 3,490
* Registrations started: 1,637
* Activations: 357

## Funnel alcanzado en esta corrida

|stage\_id|journeys\_reached|rate\_pct|
|-|-:|-:|
|ST01|26952|100|
|ST02|19364|71.85|
|ST03|3490|12.95|
|ST04|2595|9.63|
|ST05|1637|6.07|
|ST06|534|1.98|
|ST07|357|1.32|
|ST08|197|0.73|

## Cómo volver a generarlo

```bash
python synthetic\\\_afore\\\_funnel\\\_generator.py \\\\
  --prospects 24000 \\\\
  --seed 42 \\\\
  --output-dir synthetic\\\_afore\\\_output \\\\
  --db-path synthetic\\\_afore\\\_output/synthetic\\\_afore\\\_funnel.db
```

## Vistas útiles en SQLite

* `VW\\\_FUNNEL\\\_STAGE\\\_SUMMARY`
* `VW\\\_CAMPAIGN\\\_PERFORMANCE`
* `VW\\\_ESTIMATED\\\_REVENUE`

