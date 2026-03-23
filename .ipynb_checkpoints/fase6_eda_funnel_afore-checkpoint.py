
# -*- coding: utf-8 -*-
"""
Fase 6. Python: análisis exploratorio y visualizaciones
Caso: Optimización del funnel digital de registro y activación de ahorro voluntario en una Afore

Este script:
1) carga la base SQLite del caso,
2) construye un dataset maestro a nivel journey,
3) analiza el funnel,
4) compara segmentos, canales y dispositivos,
5) evalúa revenue y eficiencia de campañas,
6) resume hallazgos clave.

Pensado para portafolio y entrevista técnica.
"""

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 160)

DB_PATH = Path("synthetic_afore_funnel.db")
if not DB_PATH.exists():
    alt_path = Path("/mnt/data/synthetic_afore_funnel.db")
    if alt_path.exists():
        DB_PATH = alt_path
    else:
        raise FileNotFoundError("No se encontró la base synthetic_afore_funnel.db")

conn = sqlite3.connect(DB_PATH)


def show_table(df: pd.DataFrame, title: str, n: int = 10) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    print(df.head(n).to_string(index=False))


def annotate_bars(ax, fmt="{:.1%}", is_pct=True) -> None:
    for p in ax.patches:
        val = p.get_width() if len(ax.containers) == 1 and hasattr(ax, "barh") else p.get_height()
        if np.isnan(val):
            continue
        label = fmt.format(val) if is_pct else fmt.format(val)
        if ax.name == "rectilinear":
            try:
                x = p.get_x() + p.get_width() / 2
                y = p.get_y() + p.get_height() / 2
                if p.get_width() > p.get_height():
                    ax.text(p.get_width(), p.get_y() + p.get_height()/2, f" {label}", va="center", fontsize=9)
                else:
                    ax.text(p.get_x() + p.get_width()/2, p.get_height(), label, ha="center", va="bottom", fontsize=9)
            except Exception:
                pass


# --------------------------------------------------------------------------------------
# 1. Carga de tablas
# --------------------------------------------------------------------------------------
tables = {
    "users": pd.read_sql_query("SELECT * FROM users", conn),
    "sessions": pd.read_sql_query("SELECT * FROM sessions", conn),
    "campaigns": pd.read_sql_query("SELECT * FROM campaigns", conn),
    "conversions": pd.read_sql_query("SELECT * FROM conversions", conn),
    "funnel_events": pd.read_sql_query("SELECT * FROM funnel_events", conn),
    "fact_journey": pd.read_sql_query("SELECT * FROM FACT_JOURNEY", conn),
    "dim_channel": pd.read_sql_query("SELECT * FROM DIM_CHANNEL", conn),
    "dim_device": pd.read_sql_query("SELECT * FROM DIM_DEVICE", conn),
}

table_sizes = pd.DataFrame(
    [{"table_name": name, "rows": len(df), "columns": df.shape[1]} for name, df in tables.items()]
).sort_values("rows", ascending=False)
show_table(table_sizes, "Tamaño de las tablas principales", n=len(table_sizes))

# Parseo ligero de fechas
date_columns = {
    "users": ["first_identified_ts"],
    "sessions": ["session_start_ts", "session_end_ts"],
    "campaigns": ["start_date", "end_date"],
    "conversions": [
        "lead_created_ts", "registration_started_ts", "registration_completed_ts",
        "first_login_ts", "second_key_action_ts"
    ],
    "funnel_events": ["stage_ts"],
    "fact_journey": ["journey_start_ts", "journey_end_ts"],
}

for table_name, cols in date_columns.items():
    for col in cols:
        tables[table_name][col] = pd.to_datetime(tables[table_name][col], errors="coerce")

users = tables["users"].copy()
sessions = tables["sessions"].copy()
campaigns = tables["campaigns"].copy()
conversions = tables["conversions"].copy()
funnel_events = tables["funnel_events"].copy()
fact_journey = tables["fact_journey"].copy()
dim_channel = tables["dim_channel"].copy()
dim_device = tables["dim_device"].copy()

# --------------------------------------------------------------------------------------
# 2. Construcción del dataset maestro a nivel journey
# --------------------------------------------------------------------------------------
journey_master = (
    conversions
    .merge(
        fact_journey[["journey_id", "first_device_id", "journey_start_ts", "journey_end_ts"]],
        how="left",
        on="journey_id"
    )
    .merge(users, how="left", on="prospect_id")
    .merge(
        dim_channel.rename(columns={"channel_id": "primary_channel_id"}),
        how="left",
        on="primary_channel_id"
    )
    .merge(
        dim_device.rename(columns={"device_id": "first_device_id"}),
        how="left",
        on="first_device_id"
    )
    .merge(
        campaigns.rename(columns={"campaign_id": "primary_campaign_id"}),
        how="left",
        on="primary_campaign_id",
        suffixes=("", "_campaign")
    )
)

journey_master = journey_master.rename(
    columns={
        "primary_campaign_id": "campaign_id",
        "primary_channel_id": "channel_id",
        "channel_name": "channel_name",
        "device_type": "device_type",
        "campaign_name": "campaign_name",
    }
)

show_table(journey_master[[
    "journey_id", "prospect_id", "channel_name", "device_type", "campaign_name",
    "segment_label", "intent_band", "is_lead", "is_registered", "is_activated",
    "estimated_annual_revenue"
]], "Vista previa del dataset maestro", n=5)

# --------------------------------------------------------------------------------------
# 3. Limpieza ligera y métricas base
# --------------------------------------------------------------------------------------
duplicate_journeys = journey_master["journey_id"].duplicated().sum()
null_review = (
    journey_master[[
        "journey_id", "campaign_id", "channel_name", "device_type",
        "segment_label", "intent_band", "estimated_annual_revenue"
    ]]
    .isna()
    .sum()
    .reset_index()
    .rename(columns={"index": "column", 0: "nulls"})
)

print(f"\nJourneys duplicados en dataset maestro: {duplicate_journeys:,}")
show_table(null_review, "Nulos en columnas analíticas clave", n=len(null_review))

overall_kpis = pd.DataFrame({
    "metric": [
        "Journeys totales", "Leads", "Registros completados",
        "Activaciones digitales", "Activaciones consolidadas",
        "Revenue anual estimado", "Revenue promedio por activación"
    ],
    "value": [
        len(journey_master),
        int(journey_master["is_lead"].sum()),
        int(journey_master["is_registered"].sum()),
        int(journey_master["is_activated"].sum()),
        int(journey_master["is_consolidated"].sum()),
        journey_master["estimated_annual_revenue"].sum(),
        journey_master.loc[journey_master["is_activated"] == 1, "estimated_annual_revenue"].mean()
    ]
})
show_table(overall_kpis, "KPIs generales del caso", n=len(overall_kpis))

# --------------------------------------------------------------------------------------
# 4. Funnel visual
# --------------------------------------------------------------------------------------
funnel = (
    funnel_events.groupby(["stage_order", "stage_name"], as_index=False)["journey_id"]
    .nunique()
    .rename(columns={"journey_id": "journeys"})
    .sort_values("stage_order")
)
funnel["step_conversion_rate"] = funnel["journeys"] / funnel["journeys"].shift(1)
funnel["end_to_end_rate"] = funnel["journeys"] / funnel["journeys"].iloc[0]
funnel["drop_abs"] = funnel["journeys"].shift(1) - funnel["journeys"]
funnel["drop_pct"] = 1 - funnel["step_conversion_rate"]

show_table(funnel, "Funnel completo", n=len(funnel))

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(funnel["stage_name"], funnel["journeys"])
ax.set_title("Funnel digital por etapa")
ax.set_xlabel("Journeys")
ax.invert_yaxis()
for i, v in enumerate(funnel["journeys"]):
    ax.text(v, i, f" {v:,}", va="center")
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(funnel["stage_name"][1:], funnel["step_conversion_rate"][1:])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Conversión entre etapas")
ax.set_ylabel("Tasa de conversión")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(funnel["step_conversion_rate"][1:]):
    ax.text(i, v, f"{v:.1%}", ha="center", va="bottom")
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------------------------
# 5. EDA de sesiones
# --------------------------------------------------------------------------------------
sessions = (
    sessions
    .merge(dim_channel, how="left", on="channel_id")
    .merge(dim_device, how="left", on="device_id")
    .merge(campaigns[["campaign_id", "campaign_name", "platform_name"]], how="left", on="campaign_id")
)

session_summary = pd.DataFrame({
    "metric": [
        "Sesiones totales", "Journeys con más de 1 sesión", "Pageviews promedio",
        "CTA clicks promedio", "Bounce rate", "Qualified interaction rate"
    ],
    "value": [
        sessions["session_id"].nunique(),
        int((sessions.groupby("journey_id")["session_id"].nunique() > 1).sum()),
        sessions["pageviews_qty"].mean(),
        sessions["cta_click_qty"].mean(),
        sessions["bounce_flag"].mean(),
        sessions["qualified_interaction_flag"].mean()
    ]
})
show_table(session_summary, "EDA de sesiones", n=len(session_summary))

session_by_channel = (
    sessions.groupby("channel_name", as_index=False)
    .agg(
        sessions=("session_id", "nunique"),
        avg_pageviews=("pageviews_qty", "mean"),
        avg_cta_clicks=("cta_click_qty", "mean"),
        bounce_rate=("bounce_flag", "mean"),
        qualified_interaction_rate=("qualified_interaction_flag", "mean")
    )
    .sort_values("sessions", ascending=False)
)
show_table(session_by_channel, "Sesiones por canal", n=len(session_by_channel))

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(session_by_channel["channel_name"], session_by_channel["bounce_rate"])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Bounce rate por canal")
ax.set_ylabel("Bounce rate")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(session_by_channel["bounce_rate"]):
    ax.text(i, v, f"{v:.1%}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------------------------
# 6. Comparación por segmentos
# --------------------------------------------------------------------------------------
def build_segment_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    out = (
        df.groupby(group_col, as_index=False)
        .agg(
            journeys=("journey_id", "nunique"),
            leads=("is_lead", "sum"),
            registrations=("is_registered", "sum"),
            activations=("is_activated", "sum"),
            consolidated=("is_consolidated", "sum"),
            revenue=("estimated_annual_revenue", "sum"),
            avg_lead_quality=("lead_quality_score", "mean")
        )
    )
    out["lead_rate"] = out["leads"] / out["journeys"]
    out["registration_rate"] = out["registrations"] / out["journeys"]
    out["activation_rate"] = out["activations"] / out["journeys"]
    out["consolidated_rate"] = out["consolidated"] / out["journeys"]
    return out.sort_values("journeys", ascending=False)

channel_perf = build_segment_table(journey_master, "channel_name")
device_perf = build_segment_table(journey_master, "device_type")
segment_perf = build_segment_table(journey_master, "segment_label")
intent_perf = build_segment_table(journey_master, "intent_band")
state_perf = build_segment_table(journey_master, "geo_state")

show_table(channel_perf, "Desempeño por canal", n=len(channel_perf))
show_table(device_perf, "Desempeño por dispositivo", n=len(device_perf))
show_table(segment_perf, "Desempeño por segmento", n=len(segment_perf))
show_table(intent_perf, "Desempeño por intención", n=len(intent_perf))
show_table(state_perf.sort_values("journeys", ascending=False), "Desempeño por estado", n=10)

fig, ax = plt.subplots(figsize=(10, 5))
tmp = channel_perf.sort_values("activation_rate", ascending=False)
ax.bar(tmp["channel_name"], tmp["activation_rate"])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Tasa de activación por canal")
ax.set_ylabel("Activation rate")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(tmp["activation_rate"]):
    ax.text(i, v, f"{v:.1%}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(10, 5))
tmp = device_perf.set_index("device_type")[["lead_rate", "registration_rate", "activation_rate"]]
tmp.plot(kind="bar", ax=ax)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Conversión por dispositivo")
ax.set_ylabel("Tasa")
ax.tick_params(axis="x", rotation=0)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(11, 5))
tmp = segment_perf.sort_values("activation_rate", ascending=False)
ax.bar(tmp["segment_label"], tmp["activation_rate"])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Tasa de activación por segmento")
ax.set_ylabel("Activation rate")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(tmp["activation_rate"]):
    ax.text(i, v, f"{v:.1%}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(8, 5))
tmp = intent_perf.sort_values("activation_rate", ascending=False)
ax.bar(tmp["intent_band"], tmp["activation_rate"])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_title("Tasa de activación por banda de intención")
ax.set_ylabel("Activation rate")
for i, v in enumerate(tmp["activation_rate"]):
    ax.text(i, v, f"{v:.1%}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

# Heatmap canal vs dispositivo
heatmap = journey_master.pivot_table(
    index="channel_name",
    columns="device_type",
    values="is_activated",
    aggfunc="mean"
).fillna(0)

fig, ax = plt.subplots(figsize=(8, 5))
im = ax.imshow(heatmap.values, aspect="auto")
ax.set_xticks(range(len(heatmap.columns)))
ax.set_xticklabels(heatmap.columns)
ax.set_yticks(range(len(heatmap.index)))
ax.set_yticklabels(heatmap.index)
ax.set_title("Activation rate: canal vs dispositivo")
for i in range(heatmap.shape[0]):
    for j in range(heatmap.shape[1]):
        ax.text(j, i, f"{heatmap.iloc[i, j]:.1%}", ha="center", va="center", fontsize=8)
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------------------------
# 7. Revenue y eficiencia de campañas
# --------------------------------------------------------------------------------------
campaign_perf = (
    journey_master.groupby(
        ["campaign_id", "campaign_name", "channel_name", "campaign_type", "objective"],
        as_index=False
    )
    .agg(
        journeys=("journey_id", "nunique"),
        leads=("is_lead", "sum"),
        registrations=("is_registered", "sum"),
        activations=("is_activated", "sum"),
        consolidated=("is_consolidated", "sum"),
        revenue=("estimated_annual_revenue", "sum"),
        budget_amount=("budget_amount", "max")
    )
)

campaign_perf["lead_rate"] = campaign_perf["leads"] / campaign_perf["journeys"]
campaign_perf["registration_rate"] = campaign_perf["registrations"] / campaign_perf["journeys"]
campaign_perf["activation_rate"] = campaign_perf["activations"] / campaign_perf["journeys"]
campaign_perf["cost_per_activation"] = np.where(
    campaign_perf["activations"] > 0,
    campaign_perf["budget_amount"] / campaign_perf["activations"],
    np.nan
)
campaign_perf["roas_proxy"] = np.where(
    campaign_perf["budget_amount"] > 0,
    campaign_perf["revenue"] / campaign_perf["budget_amount"],
    np.nan
)

show_table(
    campaign_perf.sort_values("activations", ascending=False)[[
        "campaign_name", "channel_name", "journeys", "activations",
        "activation_rate", "budget_amount", "cost_per_activation", "roas_proxy"
    ]],
    "Campañas ordenadas por activaciones",
    n=12
)

fig, ax = plt.subplots(figsize=(10, 5))
tmp = channel_perf.sort_values("revenue", ascending=False)
ax.bar(tmp["channel_name"], tmp["revenue"])
ax.set_title("Revenue anual estimado por canal")
ax.set_ylabel("Revenue")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(tmp["revenue"]):
    ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(12, 5))
tmp = campaign_perf.sort_values("activations", ascending=False).head(10)
ax.bar(tmp["campaign_name"], tmp["activations"])
ax.set_title("Top 10 campañas por activaciones")
ax.set_ylabel("Activaciones")
ax.tick_params(axis="x", rotation=35)
for i, v in enumerate(tmp["activations"]):
    ax.text(i, v, f"{int(v)}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(12, 5))
tmp = campaign_perf[campaign_perf["activations"] >= 10].sort_values("cost_per_activation").head(10)
ax.bar(tmp["campaign_name"], tmp["cost_per_activation"])
ax.set_title("Top campañas con menor costo por activación (mínimo 10 activaciones)")
ax.set_ylabel("Costo por activación")
ax.tick_params(axis="x", rotation=35)
for i, v in enumerate(tmp["cost_per_activation"]):
    ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------------------------
# 8. Tiempo entre etapas
# --------------------------------------------------------------------------------------
time_by_stage = (
    funnel_events[funnel_events["time_from_previous_stage_minutes"].notna()]
    .groupby(["stage_order", "stage_name"], as_index=False)["time_from_previous_stage_minutes"]
    .agg(avg_minutes="mean", median_minutes="median")
    .sort_values("stage_order")
)
time_by_stage["avg_hours"] = time_by_stage["avg_minutes"] / 60
time_by_stage["median_hours"] = time_by_stage["median_minutes"] / 60
show_table(time_by_stage, "Tiempo entre etapas", n=len(time_by_stage))

fig, ax = plt.subplots(figsize=(10, 5))
tmp = time_by_stage.copy()
ax.bar(tmp["stage_name"], tmp["median_hours"])
ax.set_title("Mediana de horas transcurridas desde la etapa previa")
ax.set_ylabel("Horas")
ax.tick_params(axis="x", rotation=30)
for i, v in enumerate(tmp["median_hours"]):
    ax.text(i, v, f"{v:,.1f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.show()

# --------------------------------------------------------------------------------------
# 9. Hallazgos principales automáticos
# --------------------------------------------------------------------------------------
valid_channels = channel_perf[channel_perf["journeys"] >= 1000].copy()
valid_segments = segment_perf[segment_perf["journeys"] >= 500].copy()

biggest_drop = funnel.loc[funnel["drop_abs"].idxmax()]
best_channel = valid_channels.sort_values("activation_rate", ascending=False).iloc[0]
worst_channel = valid_channels.sort_values("activation_rate").iloc[0]
best_segment = valid_segments.sort_values("activation_rate", ascending=False).iloc[0]
worst_segment = valid_segments.sort_values("activation_rate").iloc[0]
best_device = device_perf.sort_values("activation_rate", ascending=False).iloc[0]
top_revenue_channel = channel_perf.sort_values("revenue", ascending=False).iloc[0]
top_campaign = campaign_perf.sort_values("activations", ascending=False).iloc[0]

findings = [
    (
        f"El funnel inicia con {funnel['journeys'].iloc[0]:,} journeys y termina con "
        f"{int(journey_master['is_consolidated'].sum()):,} activaciones consolidadas "
        f"({journey_master['is_consolidated'].mean():.2%} del total)."
    ),
    (
        f"La mayor fuga absoluta del funnel ocurre entre "
        f"{funnel.iloc[biggest_drop.name - 1]['stage_name']} y {biggest_drop['stage_name']}, "
        f"con una pérdida de {int(biggest_drop['drop_abs']):,} journeys "
        f"({biggest_drop['drop_pct']:.2%} entre etapas)."
    ),
    (
        f"Entre canales con volumen relevante, {best_channel['channel_name']} muestra la mejor tasa "
        f"de activación ({best_channel['activation_rate']:.2%}), mientras que "
        f"{worst_channel['channel_name']} presenta la más baja ({worst_channel['activation_rate']:.2%})."
    ),
    (
        f"El segmento con mejor desempeño es {best_segment['segment_label']} "
        f"({best_segment['activation_rate']:.2%} de activación y revenue estimado de "
        f"{best_segment['revenue']:,.0f}), mientras que {worst_segment['segment_label']} "
        f"prácticamente no convierte."
    ),
    (
        f"El mejor dispositivo en tasa de activación es {best_device['device_type']} "
        f"({best_device['activation_rate']:.2%}), lo que sugiere revisar fricción comparativa "
        f"en mobile vs desktop."
    ),
    (
        f"El canal que más revenue aporta es {top_revenue_channel['channel_name']} "
        f"con {top_revenue_channel['revenue']:,.0f} de revenue anual estimado."
    ),
    (
        f"La campaña con más activaciones es {top_campaign['campaign_name']} "
        f"({int(top_campaign['activations'])} activaciones; activation rate de "
        f"{top_campaign['activation_rate']:.2%})."
    ),
]

print("\n" + "=" * 100)
print("HALLAZGOS PRINCIPALES")
print("=" * 100)
for idx, finding in enumerate(findings, start=1):
    print(f"{idx}. {finding}")

conn.close()
