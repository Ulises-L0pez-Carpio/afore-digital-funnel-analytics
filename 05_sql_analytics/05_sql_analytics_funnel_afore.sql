/* =========================================================
   FASE 5. SQL ANALÍTICO
   Segmentación, campañas y KPIs ejecutivos
   Caso: Funnel digital de captación, registro y activación
   Motor: SQLite
   ========================================================= */

/* =========================================================
   0) CAPA BASE ANALÍTICA
   ---------------------------------------------------------
   Objetivo:
   Crear una vista temporal a nivel journey que concentre:
   - campaña y canal
   - segmento y tipo de usuario
   - región
   - dispositivo
   - métricas de conversión
   - revenue estimado

   Esta vista será la base reutilizable del resto del bloque.
   ========================================================= */

DROP VIEW IF EXISTS vw_journey_base;

CREATE TEMP VIEW vw_journey_base AS
SELECT
    c.journey_id,
    c.prospect_id,

    /* Fechas para análisis temporal */
    date(j.journey_start_ts) AS journey_date,
    strftime('%Y-%m', j.journey_start_ts) AS journey_month,
    strftime('%Y-W%W', j.journey_start_ts) AS journey_week,

    /* Identificadores de campaña/canal */
    c.primary_campaign_id AS campaign_id,
    c.primary_channel_id AS channel_id,

    /* Atributos de campaña */
    ca.campaign_name,
    ca.campaign_type,
    ca.objective,
    ca.platform_name,
    ca.budget_amount,
    ca.is_paid,
    ca.channel_group,
    ca.channel_name,
    ca.source,
    ca.medium,

    /* Atributos del usuario/prospecto */
    u.geo_state,
    u.age_band,
    u.income_band,
    u.segment_label,
    u.intent_band,
    u.lead_quality_score,

    /* Tipo de usuario: prospecto nuevo o cliente existente */
    CASE
        WHEN u.is_existing_customer = 1 THEN 'Cliente existente'
        ELSE 'Prospecto nuevo'
    END AS user_type,

    /* Dispositivo del primer contacto del journey */
    j.first_device_id AS device_id,
    d.device_type,
    d.os_name,
    d.app_web_type,

    /* Flags de conversión */
    c.is_lead,
    CASE
        WHEN c.qualification_status = 'qualified' THEN 1
        ELSE 0
    END AS is_qualified_lead,
    c.is_registered,
    c.is_activated,
    c.is_consolidated,

    /* Métricas de valor */
    COALESCE(c.estimated_monthly_contribution, 0) AS estimated_monthly_contribution,
    COALESCE(c.estimated_12m_balance, 0) AS estimated_12m_balance,
    COALESCE(c.estimated_annual_revenue, 0) AS estimated_annual_revenue,

    /* Timestamps para tiempos de conversión */
    c.lead_created_ts,
    c.registration_started_ts,
    c.registration_completed_ts,
    c.first_login_ts,
    c.second_key_action_ts

FROM conversions c
LEFT JOIN campaigns ca
    ON c.primary_campaign_id = ca.campaign_id
LEFT JOIN users u
    ON c.prospect_id = u.prospect_id
LEFT JOIN FACT_JOURNEY j
    ON c.journey_id = j.journey_id
LEFT JOIN DIM_DEVICE d
    ON j.first_device_id = d.device_id;


/* =========================================================
   1) CONVERSIÓN POR CANAL
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué canales generan más volumen, mejor conversión
   y mayor revenue?
   ========================================================= */

SELECT
    channel_group,
    channel_name,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_qualified_lead) AS qualified_leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,
    SUM(is_consolidated) AS consolidated,

    ROUND(100.0 * SUM(is_lead) / COUNT(*), 2) AS visit_to_lead_rate_pct,
    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / NULLIF(SUM(is_registered), 0), 2) AS registration_to_activation_rate_pct,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,

    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY channel_group, channel_name
ORDER BY end_to_end_activation_rate_pct DESC, annual_revenue DESC;


/* =========================================================
   2) CONVERSIÓN POR DISPOSITIVO
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Existen diferencias de desempeño entre mobile,
   desktop o app?
   ========================================================= */

SELECT
    device_type,
    os_name,
    app_web_type,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,

    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / NULLIF(SUM(is_registered), 0), 2) AS registration_to_activation_rate_pct,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,

    ROUND(AVG(lead_quality_score), 2) AS avg_lead_quality_score,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY device_type, os_name, app_web_type
ORDER BY end_to_end_activation_rate_pct DESC, journeys DESC;


/* =========================================================
   3) CONVERSIÓN POR REGIÓN
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué estados o regiones muestran mejor desempeño
   comercial y de activación?
   Nota:
   Se filtran regiones con al menos 100 journeys para
   evitar conclusiones sobre muestras demasiado pequeñas.
   ========================================================= */

SELECT
    geo_state,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,

    ROUND(100.0 * SUM(is_lead) / COUNT(*), 2) AS visit_to_lead_rate_pct,
    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,

    ROUND(AVG(lead_quality_score), 2) AS avg_lead_quality_score,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY geo_state
HAVING COUNT(*) >= 100
ORDER BY end_to_end_activation_rate_pct DESC, annual_revenue DESC;


/* =========================================================
   4) ANÁLISIS POR TIPO DE USUARIO Y SEGMENTO
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué segmentos convierten mejor?
   ¿Se comporta distinto un cliente existente frente a
   un prospecto nuevo?
   ========================================================= */

SELECT
    user_type,
    segment_label,
    intent_band,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_qualified_lead) AS qualified_leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,

    ROUND(100.0 * SUM(is_qualified_lead) / NULLIF(SUM(is_lead), 0), 2) AS lead_qualification_rate_pct,
    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,

    ROUND(AVG(lead_quality_score), 2) AS avg_lead_quality_score,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY user_type, segment_label, intent_band
HAVING COUNT(*) >= 50
ORDER BY end_to_end_activation_rate_pct DESC, annual_revenue DESC;


/* =========================================================
   5) REVENUE POR CANAL
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué canales generan más valor económico y cuánto
   revenue aporta cada activación?
   ========================================================= */

SELECT
    channel_group,
    channel_name,
    COUNT(*) AS journeys,
    SUM(is_activated) AS activations,

    ROUND(SUM(estimated_monthly_contribution), 2) AS monthly_contribution,
    ROUND(SUM(estimated_12m_balance), 2) AS balance_12m,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue,

    ROUND(SUM(estimated_annual_revenue) / NULLIF(SUM(is_activated), 0), 2) AS revenue_per_activation
FROM vw_journey_base
GROUP BY channel_group, channel_name
ORDER BY annual_revenue DESC;


/* =========================================================
   6) COSTO POR CONVERSIÓN POR CAMPAÑA
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué campañas son más eficientes en costo por lead,
   registro y activación?
   Nota:
   Se usa budget_amount como costo total estimado de campaña.
   ========================================================= */

SELECT
    campaign_id,
    campaign_name,
    channel_name,
    campaign_type,
    objective,

    ROUND(MAX(budget_amount), 2) AS campaign_budget,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,

    ROUND(MAX(budget_amount) / NULLIF(SUM(is_lead), 0), 2) AS cost_per_lead,
    ROUND(MAX(budget_amount) / NULLIF(SUM(is_registered), 0), 2) AS cost_per_registration,
    ROUND(MAX(budget_amount) / NULLIF(SUM(is_activated), 0), 2) AS cost_per_activation,

    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue,
    ROUND(SUM(estimated_annual_revenue) / NULLIF(MAX(budget_amount), 0), 2) AS roas_ratio
FROM vw_journey_base
WHERE campaign_id IS NOT NULL
GROUP BY campaign_id, campaign_name, channel_name, campaign_type, objective
ORDER BY roas_ratio DESC, cost_per_activation ASC;


/* =========================================================
   7) CALIDAD DE CAMPAÑA
   ---------------------------------------------------------
   Pregunta de negocio:
   Más allá del volumen, ¿qué campañas traen leads de
   mejor calidad y con mayor probabilidad de activarse?
   ========================================================= */

WITH campaign_perf AS (
    SELECT
        campaign_id,
        campaign_name,
        channel_name,
        campaign_type,
        objective,
        COUNT(*) AS journeys,
        SUM(is_lead) AS leads,
        SUM(is_qualified_lead) AS qualified_leads,
        SUM(is_registered) AS registrations,
        SUM(is_activated) AS activations,

        ROUND(AVG(lead_quality_score), 2) AS avg_lead_quality_score,
        ROUND(100.0 * SUM(is_qualified_lead) / NULLIF(SUM(is_lead), 0), 2) AS qualification_rate_pct,
        ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
        ROUND(100.0 * SUM(is_activated) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_activation_rate_pct,

        ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
    FROM vw_journey_base
    WHERE campaign_id IS NOT NULL
    GROUP BY campaign_id, campaign_name, channel_name, campaign_type, objective
)
SELECT
    *,
    CASE
        WHEN qualification_rate_pct >= 75 AND lead_to_activation_rate_pct >= 12 THEN 'Top quality'
        WHEN qualification_rate_pct >= 60 AND lead_to_activation_rate_pct >= 8 THEN 'Good'
        WHEN qualification_rate_pct >= 45 THEN 'Average'
        ELSE 'Low quality'
    END AS campaign_quality_bucket
FROM campaign_perf
ORDER BY lead_to_activation_rate_pct DESC, avg_lead_quality_score DESC;


/* =========================================================
   8) CALIDAD DE ENGAGEMENT POR CAMPAÑA
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Qué campañas generan una mejor interacción digital?
   Métricas:
   - pageviews promedio
   - clics promedio
   - tasa de interacción calificada
   - bounce rate
   ========================================================= */

SELECT
    ca.campaign_id,
    ca.campaign_name,
    ca.channel_name,

    COUNT(*) AS sessions,
    ROUND(AVG(s.pageviews_qty), 2) AS avg_pageviews,
    ROUND(AVG(s.cta_click_qty), 2) AS avg_cta_clicks,

    ROUND(
        100.0 * AVG(
            CASE
                WHEN s.qualified_interaction_flag = 1 THEN 1.0
                ELSE 0
            END
        ),
        2
    ) AS qualified_interaction_rate_pct,

    ROUND(
        100.0 * AVG(
            CASE
                WHEN s.bounce_flag = 1 THEN 1.0
                ELSE 0
            END
        ),
        2
    ) AS bounce_rate_pct
FROM sessions s
LEFT JOIN campaigns ca
    ON s.campaign_id = ca.campaign_id
GROUP BY ca.campaign_id, ca.campaign_name, ca.channel_name
ORDER BY qualified_interaction_rate_pct DESC, bounce_rate_pct ASC;


/* =========================================================
   9) COMPARATIVO TEMPORAL MENSUAL
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Cómo evoluciona el funnel en el tiempo?
   Útil para cohortes simples o lectura mensual ejecutiva.
   ========================================================= */

SELECT
    journey_month,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,
    SUM(is_consolidated) AS consolidated,

    ROUND(100.0 * SUM(is_lead) / COUNT(*), 2) AS visit_to_lead_rate_pct,
    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / NULLIF(SUM(is_registered), 0), 2) AS registration_to_activation_rate_pct,
    ROUND(100.0 * SUM(is_consolidated) / NULLIF(SUM(is_activated), 0), 2) AS activation_to_consolidation_rate_pct,

    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY journey_month
ORDER BY journey_month;


/* =========================================================
   10) KPI EJECUTIVO GENERAL
   ---------------------------------------------------------
   Pregunta de negocio:
   ¿Cuál es el estado general del funnel?
   Este query resume los KPIs principales del proyecto.
   ========================================================= */

SELECT
    COUNT(*) AS total_journeys,
    SUM(is_lead) AS total_leads,
    SUM(is_qualified_lead) AS total_qualified_leads,
    SUM(is_registered) AS total_registrations,
    SUM(is_activated) AS total_activations,
    SUM(is_consolidated) AS total_consolidated,

    ROUND(100.0 * SUM(is_lead) / COUNT(*), 2) AS visit_to_lead_rate_pct,
    ROUND(100.0 * SUM(is_qualified_lead) / NULLIF(SUM(is_lead), 0), 2) AS lead_qualification_rate_pct,
    ROUND(100.0 * SUM(is_registered) / NULLIF(SUM(is_lead), 0), 2) AS lead_to_registration_rate_pct,
    ROUND(100.0 * SUM(is_activated) / NULLIF(SUM(is_registered), 0), 2) AS registration_to_activation_rate_pct,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,
    ROUND(100.0 * SUM(is_consolidated) / NULLIF(SUM(is_activated), 0), 2) AS activation_to_consolidation_rate_pct,

    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue,
    ROUND(SUM(estimated_annual_revenue) / NULLIF(SUM(is_activated), 0), 2) AS revenue_per_activation,

    ROUND(
        AVG(
            CASE
                WHEN registration_completed_ts IS NOT NULL
                 AND lead_created_ts IS NOT NULL
                THEN julianday(registration_completed_ts) - julianday(lead_created_ts)
            END
        ),
        2
    ) AS avg_days_lead_to_registration,

    ROUND(
        AVG(
            CASE
                WHEN first_login_ts IS NOT NULL
                 AND registration_completed_ts IS NOT NULL
                THEN julianday(first_login_ts) - julianday(registration_completed_ts)
            END
        ),
        2
    ) AS avg_days_registration_to_activation
FROM vw_journey_base;


/* =========================================================
   11) TOP CAMPAÑAS EJECUTIVAS
   ---------------------------------------------------------
   Query extra recomendado para presentación:
   ranking rápido de campañas por revenue y activación.
   ========================================================= */

SELECT
    campaign_name,
    channel_name,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue,
    ROUND(SUM(estimated_annual_revenue) / NULLIF(SUM(is_activated), 0), 2) AS revenue_per_activation
FROM vw_journey_base
WHERE campaign_name IS NOT NULL
GROUP BY campaign_name, channel_name
HAVING COUNT(*) >= 30
ORDER BY annual_revenue DESC, activations DESC
LIMIT 10;


/* =========================================================
   12) RESUMEN EJECUTIVO POR SEGMENTO
   ---------------------------------------------------------
   Query extra recomendado para storytelling:
   muestra qué segmentos combinan volumen y valor.
   ========================================================= */

SELECT
    segment_label,
    user_type,
    COUNT(*) AS journeys,
    SUM(is_lead) AS leads,
    SUM(is_registered) AS registrations,
    SUM(is_activated) AS activations,
    ROUND(100.0 * SUM(is_activated) / COUNT(*), 2) AS end_to_end_activation_rate_pct,
    ROUND(AVG(lead_quality_score), 2) AS avg_lead_quality_score,
    ROUND(SUM(estimated_annual_revenue), 2) AS annual_revenue
FROM vw_journey_base
GROUP BY segment_label, user_type
HAVING COUNT(*) >= 50
ORDER BY annual_revenue DESC, end_to_end_activation_rate_pct DESC;
