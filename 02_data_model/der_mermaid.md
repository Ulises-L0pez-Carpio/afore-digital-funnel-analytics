# DER del proyecto

```mermaid
erDiagram

    DIM_PROSPECT {
        string prospect_id PK
        string hashed_email
        string hashed_phone
        string curp_hash
        timestamp first_identified_ts
        string geo_state
        string age_band
        string income_band
        string segment_label
        string intent_band
        numeric lead_quality_score
        boolean is_existing_customer
    }

    DIM_CHANNEL {
        string channel_id PK
        string channel_group
        string channel_name
        string source
        string medium
        boolean is_paid
        string channel_status
    }

    DIM_CAMPAIGN {
        string campaign_id PK
        string channel_id FK
        string platform_campaign_key
        string campaign_name
        string campaign_type
        string objective
        string platform_name
        date start_date
        date end_date
        numeric budget_amount
        string cost_model
        string landing_page_url
        string campaign_status
    }

    DIM_DEVICE {
        string device_id PK
        string device_type
        string os_name
        string browser_name
        string app_web_type
        boolean is_mobile
    }

    DIM_FUNNEL_STAGE {
        string stage_id PK
        int stage_order
        string stage_name
        string stage_group
        boolean is_terminal
        string business_definition
    }

    FACT_JOURNEY {
        string journey_id PK
        string anonymous_visitor_id
        string prospect_id FK
        string primary_campaign_id FK
        string primary_channel_id FK
        string first_device_id FK
        string attribution_model
        timestamp journey_start_ts
        timestamp journey_end_ts
        string current_stage_id FK
        boolean is_closed
    }

    FACT_SESSION {
        string session_id PK
        string journey_id FK
        string anonymous_visitor_id
        string prospect_id FK
        string campaign_id FK
        string channel_id FK
        string device_id FK
        timestamp session_start_ts
        timestamp session_end_ts
        string landing_page_url
        int pageviews_qty
        int cta_click_qty
        boolean qualified_interaction_flag
        boolean bounce_flag
    }

    FACT_INTERACTION_EVENT {
        string event_id PK
        string session_id FK
        string journey_id FK
        string prospect_id FK
        string campaign_id FK
        string channel_id FK
        string device_id FK
        timestamp event_ts
        string event_name
        string event_category
        string page_name
        string cta_name
        boolean is_key_interaction
    }

    FACT_LEAD {
        string lead_id PK
        string journey_id FK
        string prospect_id FK
        string session_id FK
        timestamp lead_created_ts
        string lead_source_type
        string form_name
        string product_interest
        string lead_status
        numeric lead_score
        string qualification_status
        string qualification_reason
        int response_time_minutes
        boolean is_duplicate
        boolean is_contactable
    }

    FACT_REGISTRATION {
        string registration_id PK
        string journey_id FK
        string prospect_id FK
        string lead_id FK
        timestamp registration_started_ts
        timestamp registration_completed_ts
        string registration_status
        string step_reached
        boolean document_upload_flag
        boolean kyc_validation_flag
        boolean biometric_validation_flag
        string rejection_reason
        string abandonment_reason
    }

    FACT_ACTIVATION {
        string activation_id PK
        string journey_id FK
        string prospect_id FK
        string registration_id FK
        timestamp first_login_ts
        timestamp first_key_action_ts
        timestamp second_key_action_ts
        string activation_status
        string activation_channel
        boolean retained_7d_flag
        boolean retained_30d_flag
    }

    FACT_JOURNEY_STAGE {
        string journey_stage_id PK
        string journey_id FK
        string stage_id FK
        string prospect_id FK
        string session_id FK
        timestamp stage_ts
        string stage_status
        string previous_stage_id
        int time_from_previous_stage_minutes
        string stage_source
    }

    DIM_CHANNEL ||--o{ DIM_CAMPAIGN : agrupa
    DIM_CHANNEL ||--o{ FACT_SESSION : origina
    DIM_CHANNEL ||--o{ FACT_INTERACTION_EVENT : clasifica
    DIM_CHANNEL ||--o{ FACT_JOURNEY : atribuye

    DIM_CAMPAIGN ||--o{ FACT_SESSION : impulsa
    DIM_CAMPAIGN ||--o{ FACT_INTERACTION_EVENT : impulsa
    DIM_CAMPAIGN ||--o{ FACT_JOURNEY : atribuye

    DIM_DEVICE ||--o{ FACT_SESSION : registra
    DIM_DEVICE ||--o{ FACT_INTERACTION_EVENT : registra

    DIM_PROSPECT ||--o{ FACT_JOURNEY : recorre
    DIM_PROSPECT ||--o{ FACT_SESSION : participa
    DIM_PROSPECT ||--o{ FACT_INTERACTION_EVENT : interactua
    DIM_PROSPECT ||--o{ FACT_LEAD : genera
    DIM_PROSPECT ||--o{ FACT_REGISTRATION : inicia
    DIM_PROSPECT ||--o{ FACT_ACTIVATION : activa
    DIM_PROSPECT ||--o{ FACT_JOURNEY_STAGE : avanza

    DIM_FUNNEL_STAGE ||--o{ FACT_JOURNEY_STAGE : define

    FACT_JOURNEY ||--o{ FACT_SESSION : contiene
    FACT_JOURNEY ||--o{ FACT_INTERACTION_EVENT : registra
    FACT_JOURNEY ||--o{ FACT_LEAD : convierte
    FACT_JOURNEY ||--o{ FACT_REGISTRATION : deriva
    FACT_JOURNEY ||--o{ FACT_ACTIVATION : culmina
    FACT_JOURNEY ||--o{ FACT_JOURNEY_STAGE : traza

    FACT_SESSION ||--o{ FACT_INTERACTION_EVENT : contiene
    FACT_SESSION ||--o{ FACT_LEAD : origina

    FACT_LEAD ||--o{ FACT_REGISTRATION : evoluciona
    FACT_REGISTRATION ||--o| FACT_ACTIVATION : desemboca

