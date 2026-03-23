
/* ============================================================================
FASE 4 - SQL base del funnel Afore
Motor asumido: SQLite
Grano principal de análisis: 1 fila por journey_id

Objetivo:
1) Validar calidad básica de las tablas fuente
2) Preparar vistas limpias con lógica de deduplicación
3) Construir una tabla maestra del funnel a nivel journey
4) Calcular métricas base por etapa y conversión general

Tablas fuente utilizadas:
- users
- sessions
- campaigns
- funnel_events
- conversions
============================================================================ */

/* ---------------------------------------------------------------------------
1. PERFILADO RÁPIDO DE TABLAS
--------------------------------------------------------------------------- */
SELECT 'users'        AS table_name, COUNT(*) AS rows FROM users
UNION ALL
SELECT 'sessions'     AS table_name, COUNT(*) AS rows FROM sessions
UNION ALL
SELECT 'campaigns'    AS table_name, COUNT(*) AS rows FROM campaigns
UNION ALL
SELECT 'funnel_events' AS table_name, COUNT(*) AS rows FROM funnel_events
UNION ALL
SELECT 'conversions'  AS table_name, COUNT(*) AS rows FROM conversions;

/* ---------------------------------------------------------------------------
2. VALIDACIONES DE CALIDAD
--------------------------------------------------------------------------- */

/* 2.1 Validación de unicidad de llaves esperadas */
SELECT 'users.prospect_id' AS validation_name, COUNT(*) AS duplicated_keys
FROM (
    SELECT prospect_id
    FROM users
    GROUP BY prospect_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'sessions.session_id' AS validation_name, COUNT(*) AS duplicated_keys
FROM (
    SELECT session_id
    FROM sessions
    GROUP BY session_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'campaigns.campaign_id' AS validation_name, COUNT(*) AS duplicated_keys
FROM (
    SELECT campaign_id
    FROM campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'funnel_events.journey_stage_id' AS validation_name, COUNT(*) AS duplicated_keys
FROM (
    SELECT journey_stage_id
    FROM funnel_events
    GROUP BY journey_stage_id
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'conversions.journey_id' AS validation_name, COUNT(*) AS duplicated_keys
FROM (
    SELECT journey_id
    FROM conversions
    GROUP BY journey_id
    HAVING COUNT(*) > 1
);

/* 2.2 Nulos en campos críticos */
SELECT 'users.prospect_id' AS field_name, COUNT(*) AS null_rows
FROM users WHERE prospect_id IS NULL
UNION ALL
SELECT 'sessions.session_id', COUNT(*) FROM sessions WHERE session_id IS NULL
UNION ALL
SELECT 'sessions.journey_id', COUNT(*) FROM sessions WHERE journey_id IS NULL
UNION ALL
SELECT 'sessions.prospect_id', COUNT(*) FROM sessions WHERE prospect_id IS NULL
UNION ALL
SELECT 'campaigns.campaign_id', COUNT(*) FROM campaigns WHERE campaign_id IS NULL
UNION ALL
SELECT 'funnel_events.journey_id', COUNT(*) FROM funnel_events WHERE journey_id IS NULL
UNION ALL
SELECT 'funnel_events.stage_id', COUNT(*) FROM funnel_events WHERE stage_id IS NULL
UNION ALL
SELECT 'conversions.journey_id', COUNT(*) FROM conversions WHERE journey_id IS NULL
UNION ALL
SELECT 'conversions.prospect_id', COUNT(*) FROM conversions WHERE prospect_id IS NULL;

/* 2.3 Integridad referencial base */
SELECT 'sessions without user' AS validation_name, COUNT(*) AS broken_rows
FROM sessions s
LEFT JOIN users u
    ON s.prospect_id = u.prospect_id
WHERE u.prospect_id IS NULL

UNION ALL

SELECT 'sessions without campaign' AS validation_name, COUNT(*) AS broken_rows
FROM sessions s
LEFT JOIN campaigns c
    ON s.campaign_id = c.campaign_id
WHERE c.campaign_id IS NULL

UNION ALL

SELECT 'conversions without user' AS validation_name, COUNT(*) AS broken_rows
FROM conversions cv
LEFT JOIN users u
    ON cv.prospect_id = u.prospect_id
WHERE u.prospect_id IS NULL

UNION ALL

SELECT 'funnel_events without user' AS validation_name, COUNT(*) AS broken_rows
FROM funnel_events fe
LEFT JOIN users u
    ON fe.prospect_id = u.prospect_id
WHERE u.prospect_id IS NULL

UNION ALL

SELECT 'funnel_events without session (review only)' AS validation_name, COUNT(*) AS broken_rows
FROM funnel_events fe
LEFT JOIN sessions s
    ON fe.session_id = s.session_id
WHERE fe.session_id IS NOT NULL
  AND s.session_id IS NULL;

/* 2.4 Consistencia del orden del funnel:
   una journey no debe repetir la misma stage_order */
SELECT
    COUNT(*) AS journeys_with_repeated_stage_order
FROM (
    SELECT journey_id, stage_order
    FROM funnel_events
    GROUP BY journey_id, stage_order
    HAVING COUNT(*) > 1
);

/* 2.5 Consistencia entre current_stage_id y la última etapa observada */
WITH stage_map AS (
    SELECT DISTINCT stage_id, stage_order
    FROM funnel_events
),
max_stage_by_journey AS (
    SELECT
        journey_id,
        MAX(stage_order) AS max_stage_order
    FROM funnel_events
    GROUP BY journey_id
)
SELECT COUNT(*) AS journeys_with_stage_mismatch
FROM conversions cv
JOIN stage_map sm
    ON cv.current_stage_id = sm.stage_id
JOIN max_stage_by_journey ms
    ON cv.journey_id = ms.journey_id
WHERE sm.stage_order <> ms.max_stage_order;

/* ---------------------------------------------------------------------------
3. LIMPIEZA Y DEDUPLICACIÓN
Nota: aunque la base sintética no muestra duplicados duros, se generan vistas
limpias para dejar la lógica lista para un caso productivo.
--------------------------------------------------------------------------- */

DROP VIEW IF EXISTS VW_SQLBASE_USERS_CLEAN;
CREATE TEMP VIEW VW_SQLBASE_USERS_CLEAN AS
WITH ranked AS (
    SELECT
        u.*,
        ROW_NUMBER() OVER (
            PARTITION BY prospect_id
            ORDER BY first_identified_ts ASC
        ) AS rn
    FROM users u
)
SELECT
    prospect_id,
    hashed_email,
    hashed_phone,
    curp_hash,
    first_identified_ts,
    geo_state,
    age_band,
    income_band,
    segment_label,
    intent_band,
    lead_quality_score,
    is_existing_customer
FROM ranked
WHERE rn = 1;

DROP VIEW IF EXISTS VW_SQLBASE_SESSIONS_CLEAN;
CREATE TEMP VIEW VW_SQLBASE_SESSIONS_CLEAN AS
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY session_id
            ORDER BY session_start_ts ASC
        ) AS rn
    FROM sessions s
)
SELECT
    session_id,
    journey_id,
    anonymous_visitor_id,
    prospect_id,
    campaign_id,
    channel_id,
    device_id,
    session_start_ts,
    session_end_ts,
    landing_page_url,
    pageviews_qty,
    cta_click_qty,
    qualified_interaction_flag,
    bounce_flag
FROM ranked
WHERE rn = 1;

DROP VIEW IF EXISTS VW_SQLBASE_CAMPAIGNS_CLEAN;
CREATE TEMP VIEW VW_SQLBASE_CAMPAIGNS_CLEAN AS
WITH ranked AS (
    SELECT
        c.*,
        ROW_NUMBER() OVER (
            PARTITION BY campaign_id
            ORDER BY start_date ASC
        ) AS rn
    FROM campaigns c
)
SELECT
    campaign_id,
    channel_id,
    platform_campaign_key,
    campaign_name,
    campaign_type,
    objective,
    platform_name,
    start_date,
    end_date,
    budget_amount,
    cost_model,
    landing_page_url,
    campaign_status,
    channel_group,
    channel_name,
    source,
    medium,
    is_paid,
    channel_status
FROM ranked
WHERE rn = 1;

DROP VIEW IF EXISTS VW_SQLBASE_FUNNEL_EVENTS_CLEAN;
CREATE TEMP VIEW VW_SQLBASE_FUNNEL_EVENTS_CLEAN AS
WITH ranked AS (
    SELECT
        fe.*,
        ROW_NUMBER() OVER (
            PARTITION BY journey_stage_id
            ORDER BY stage_ts ASC
        ) AS rn
    FROM funnel_events fe
),
dedup AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
),
stage_fix AS (
    SELECT
        journey_stage_id,
        journey_id,
        stage_id,
        prospect_id,
        session_id,
        stage_ts,
        stage_status,
        previous_stage_id,
        time_from_previous_stage_minutes,
        stage_source,
        stage_name,
        stage_order,
        stage_group
    FROM dedup
)
SELECT *
FROM stage_fix;

DROP VIEW IF EXISTS VW_SQLBASE_CONVERSIONS_CLEAN;
CREATE TEMP VIEW VW_SQLBASE_CONVERSIONS_CLEAN AS
WITH ranked AS (
    SELECT
        cv.*,
        ROW_NUMBER() OVER (
            PARTITION BY journey_id
            ORDER BY COALESCE(second_key_action_ts,
                              first_login_ts,
                              registration_completed_ts,
                              registration_started_ts,
                              lead_created_ts) DESC
        ) AS rn
    FROM conversions cv
)
SELECT
    journey_id,
    prospect_id,
    primary_campaign_id,
    primary_channel_id,
    current_stage_id,
    lead_id,
    registration_id,
    activation_id,
    lead_created_ts,
    registration_started_ts,
    registration_completed_ts,
    first_login_ts,
    second_key_action_ts,
    qualification_status,
    registration_status,
    activation_status,
    is_lead,
    is_registered,
    is_activated,
    is_consolidated,
    estimated_monthly_contribution,
    estimated_12m_balance,
    estimated_annual_revenue
FROM ranked
WHERE rn = 1;

/* ---------------------------------------------------------------------------
4. JOINS PRINCIPALES AUXILIARES
--------------------------------------------------------------------------- */

/* 4.1 Primera sesión por journey: se usa como touchpoint de adquisición */
DROP VIEW IF EXISTS VW_SQLBASE_FIRST_SESSION;
CREATE TEMP VIEW VW_SQLBASE_FIRST_SESSION AS
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY journey_id
            ORDER BY session_start_ts ASC, session_id ASC
        ) AS rn
    FROM VW_SQLBASE_SESSIONS_CLEAN s
)
SELECT
    journey_id,
    session_id AS first_session_id,
    anonymous_visitor_id,
    prospect_id,
    campaign_id,
    channel_id,
    device_id,
    session_start_ts AS first_session_start_ts,
    session_end_ts AS first_session_end_ts,
    landing_page_url AS first_landing_page_url,
    pageviews_qty AS first_session_pageviews,
    cta_click_qty AS first_session_cta_clicks,
    qualified_interaction_flag AS first_session_qualified_interaction_flag,
    bounce_flag AS first_session_bounce_flag
FROM ranked
WHERE rn = 1;

/* 4.2 Rollup de sesiones por journey */
DROP VIEW IF EXISTS VW_SQLBASE_SESSION_ROLLUP;
CREATE TEMP VIEW VW_SQLBASE_SESSION_ROLLUP AS
SELECT
    journey_id,
    COUNT(DISTINCT session_id) AS total_sessions,
    MIN(session_start_ts) AS min_session_start_ts,
    MAX(session_end_ts) AS max_session_end_ts,
    SUM(pageviews_qty) AS total_pageviews,
    SUM(cta_click_qty) AS total_cta_clicks,
    MAX(qualified_interaction_flag) AS any_qualified_interaction_flag,
    MAX(bounce_flag) AS any_bounce_flag
FROM VW_SQLBASE_SESSIONS_CLEAN
GROUP BY journey_id;

/* 4.3 Pivot de etapas del funnel a nivel journey */
DROP VIEW IF EXISTS VW_SQLBASE_STAGE_FLAGS;
CREATE TEMP VIEW VW_SQLBASE_STAGE_FLAGS AS
SELECT
    journey_id,
    MAX(CASE WHEN stage_order >= 1 THEN 1 ELSE 0 END) AS reached_attraction,
    MAX(CASE WHEN stage_order >= 2 THEN 1 ELSE 0 END) AS reached_interaction,
    MAX(CASE WHEN stage_order >= 3 THEN 1 ELSE 0 END) AS reached_lead,
    MAX(CASE WHEN stage_order >= 4 THEN 1 ELSE 0 END) AS reached_qualified_lead,
    MAX(CASE WHEN stage_order >= 5 THEN 1 ELSE 0 END) AS reached_registration_start,
    MAX(CASE WHEN stage_order >= 6 THEN 1 ELSE 0 END) AS reached_registration_completed,
    MAX(CASE WHEN stage_order >= 7 THEN 1 ELSE 0 END) AS reached_activation,
    MAX(CASE WHEN stage_order >= 8 THEN 1 ELSE 0 END) AS reached_consolidation,
    MIN(CASE WHEN stage_order = 1 THEN stage_ts END) AS ts_attraction,
    MIN(CASE WHEN stage_order = 2 THEN stage_ts END) AS ts_interaction,
    MIN(CASE WHEN stage_order = 3 THEN stage_ts END) AS ts_lead,
    MIN(CASE WHEN stage_order = 4 THEN stage_ts END) AS ts_qualified_lead,
    MIN(CASE WHEN stage_order = 5 THEN stage_ts END) AS ts_registration_start,
    MIN(CASE WHEN stage_order = 6 THEN stage_ts END) AS ts_registration_completed,
    MIN(CASE WHEN stage_order = 7 THEN stage_ts END) AS ts_activation,
    MIN(CASE WHEN stage_order = 8 THEN stage_ts END) AS ts_consolidation
FROM VW_SQLBASE_FUNNEL_EVENTS_CLEAN
GROUP BY journey_id;

/* ---------------------------------------------------------------------------
5. TABLA MAESTRA DEL FUNNEL
Grano: 1 fila por journey_id
--------------------------------------------------------------------------- */
DROP VIEW IF EXISTS VW_SQLBASE_FUNNEL_MASTER;
CREATE TEMP VIEW VW_SQLBASE_FUNNEL_MASTER AS
SELECT
    cv.journey_id,
    cv.prospect_id,

    /* dimensión de usuario */
    u.first_identified_ts,
    u.geo_state,
    u.age_band,
    u.income_band,
    u.segment_label,
    u.intent_band,
    u.lead_quality_score,
    u.is_existing_customer,

    /* dimensión de adquisición */
    cv.primary_campaign_id,
    cv.primary_channel_id,
    cp.campaign_name,
    cp.campaign_type,
    cp.objective,
    cp.platform_name,
    cp.channel_group,
    cp.channel_name,
    cp.source,
    cp.medium,
    cp.is_paid,
    cp.campaign_status,

    /* primera sesión y comportamiento agregado */
    fs.first_session_id,
    fs.anonymous_visitor_id,
    fs.device_id AS first_device_id,
    fs.first_session_start_ts,
    fs.first_session_end_ts,
    fs.first_landing_page_url,
    fs.first_session_pageviews,
    fs.first_session_cta_clicks,
    fs.first_session_qualified_interaction_flag,
    fs.first_session_bounce_flag,
    sr.total_sessions,
    sr.total_pageviews,
    sr.total_cta_clicks,
    sr.any_qualified_interaction_flag,
    sr.any_bounce_flag,

    /* estatus operativos del journey */
    cv.current_stage_id,
    cv.lead_id,
    cv.registration_id,
    cv.activation_id,
    cv.qualification_status,
    cv.registration_status,
    cv.activation_status,

    /* timestamps operativos */
    cv.lead_created_ts,
    cv.registration_started_ts,
    cv.registration_completed_ts,
    cv.first_login_ts,
    cv.second_key_action_ts,

    /* flags de conversión */
    cv.is_lead,
    cv.is_registered,
    cv.is_activated,
    cv.is_consolidated,

    /* flags de avance por etapa */
    sf.reached_attraction,
    sf.reached_interaction,
    sf.reached_lead,
    sf.reached_qualified_lead,
    sf.reached_registration_start,
    sf.reached_registration_completed,
    sf.reached_activation,
    sf.reached_consolidation,

    /* tiempos entre hitos */
    ROUND((julianday(cv.lead_created_ts) - julianday(fs.first_session_start_ts)) * 24 * 60, 2)
        AS minutes_session_to_lead,
    ROUND((julianday(cv.registration_started_ts) - julianday(cv.lead_created_ts)) * 24 * 60, 2)
        AS minutes_lead_to_registration_start,
    ROUND((julianday(cv.registration_completed_ts) - julianday(cv.registration_started_ts)) * 24 * 60, 2)
        AS minutes_registration_start_to_complete,
    ROUND((julianday(cv.first_login_ts) - julianday(cv.registration_completed_ts)) * 24 * 60, 2)
        AS minutes_registration_complete_to_activation,

    /* valor económico estimado */
    cv.estimated_monthly_contribution,
    cv.estimated_12m_balance,
    cv.estimated_annual_revenue

FROM VW_SQLBASE_CONVERSIONS_CLEAN cv
LEFT JOIN VW_SQLBASE_USERS_CLEAN u
    ON cv.prospect_id = u.prospect_id
LEFT JOIN VW_SQLBASE_CAMPAIGNS_CLEAN cp
    ON cv.primary_campaign_id = cp.campaign_id
LEFT JOIN VW_SQLBASE_FIRST_SESSION fs
    ON cv.journey_id = fs.journey_id
LEFT JOIN VW_SQLBASE_SESSION_ROLLUP sr
    ON cv.journey_id = sr.journey_id
LEFT JOIN VW_SQLBASE_STAGE_FLAGS sf
    ON cv.journey_id = sf.journey_id;

/* Consulta rápida de la tabla maestra */
SELECT *
FROM VW_SQLBASE_FUNNEL_MASTER
LIMIT 20;

/* ---------------------------------------------------------------------------
6. MÉTRICAS BASE DEL FUNNEL
--------------------------------------------------------------------------- */

/* 6.1 Volumen por etapa, conversión desde etapa previa y abandono */
WITH stage_counts AS (
    SELECT
        stage_order,
        stage_id,
        stage_name,
        COUNT(DISTINCT journey_id) AS journeys_in_stage,
        SUM(CASE WHEN stage_status = 'completed' THEN 1 ELSE 0 END) AS completed_stage,
        SUM(CASE WHEN stage_status = 'abandoned' THEN 1 ELSE 0 END) AS abandoned_stage
    FROM VW_SQLBASE_FUNNEL_EVENTS_CLEAN
    GROUP BY stage_order, stage_id, stage_name
),
stage_metrics AS (
    SELECT
        stage_order,
        stage_id,
        stage_name,
        journeys_in_stage,
        completed_stage,
        abandoned_stage,
        LAG(journeys_in_stage) OVER (ORDER BY stage_order) AS previous_stage_volume
    FROM stage_counts
)
SELECT
    stage_order,
    stage_id,
    stage_name,
    journeys_in_stage,
    completed_stage,
    abandoned_stage,
    previous_stage_volume,
    ROUND(
        CASE
            WHEN previous_stage_volume IS NULL THEN 1.0
            ELSE 1.0 * journeys_in_stage / previous_stage_volume
        END
    , 4) AS conversion_from_previous_stage,
    ROUND(1.0 * abandoned_stage / journeys_in_stage, 4) AS abandonment_rate
FROM stage_metrics
ORDER BY stage_order;

/* 6.2 Conversión general end-to-end */
SELECT
    COUNT(*) AS total_journeys,
    SUM(is_lead) AS total_leads,
    SUM(is_registered) AS total_registered,
    SUM(is_activated) AS total_activated,
    SUM(is_consolidated) AS total_consolidated,
    ROUND(1.0 * SUM(is_lead) / COUNT(*), 4) AS lead_conversion_rate,
    ROUND(1.0 * SUM(is_registered) / COUNT(*), 4) AS registration_conversion_rate,
    ROUND(1.0 * SUM(is_activated) / COUNT(*), 4) AS activation_conversion_rate,
    ROUND(1.0 * SUM(is_consolidated) / COUNT(*), 4) AS consolidated_conversion_rate
FROM VW_SQLBASE_FUNNEL_MASTER;

/* 6.3 Abandono general antes del registro y activación */
SELECT
    COUNT(*) AS total_journeys,
    SUM(CASE WHEN is_lead = 0 THEN 1 ELSE 0 END) AS dropped_before_lead,
    SUM(CASE WHEN is_lead = 1 AND is_registered = 0 THEN 1 ELSE 0 END) AS dropped_between_lead_and_registration,
    SUM(CASE WHEN is_registered = 1 AND is_activated = 0 THEN 1 ELSE 0 END) AS dropped_between_registration_and_activation,
    ROUND(1.0 * SUM(CASE WHEN is_lead = 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS drop_rate_before_lead,
    ROUND(1.0 * SUM(CASE WHEN is_lead = 1 AND is_registered = 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS drop_rate_lead_to_registration,
    ROUND(1.0 * SUM(CASE WHEN is_registered = 1 AND is_activated = 0 THEN 1 ELSE 0 END) / COUNT(*), 4) AS drop_rate_registration_to_activation
FROM VW_SQLBASE_FUNNEL_MASTER;

/* 6.4 Sanity check rápido del master */
SELECT
    COUNT(*) AS rows_in_master,
    COUNT(DISTINCT journey_id) AS distinct_journeys,
    COUNT(DISTINCT prospect_id) AS distinct_prospects
FROM VW_SQLBASE_FUNNEL_MASTER;
