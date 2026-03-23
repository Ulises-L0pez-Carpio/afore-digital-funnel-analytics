
#!/usr/bin/env python3
"""
Generador de conjuntos de datos sintéticos para funnels digitales, para un caso de uso en este proyecto.

Resultados:
- Tablas completas con esquema de estrella, alineadas con el DER del proyecto.
- Tablas de conveniencia: usuarios, campañas, sesiones, eventos del embudo, conversiones.
- Base de datos SQLite con tablas principales y vistas analíticas.
- Exportaciones CSV para cada tabla.
- Resumen JSON con recuentos de filas y métricas del embudo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


def logistic(x: float | np.ndarray) -> float | np.ndarray:
    return 1 / (1 + np.exp(-x))


def random_ts_between(rng: np.random.Generator, start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.Timestamp:
    delta = (end_ts - start_ts).total_seconds()
    if delta <= 0:
        return start_ts
    return start_ts + pd.Timedelta(seconds=float(rng.uniform(0, delta)))


def response_time_minutes(rng: np.random.Generator, channel: str, quality_score: float) -> int:
    base = {
        "CH001": 180, "CH002": 420, "CH003": 240, "CH004": 360,
        "CH005": 90, "CH006": 150, "CH007": 120, "CH008": 45
    }[channel]
    factor = np.interp(quality_score, [0, 100], [1.2, 0.7])
    return int(max(5, rng.lognormal(np.log(base * factor), 0.45)))


def fmt_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        elif pd.api.types.is_bool_dtype(out[col]):
            out[col] = out[col].astype(int)
    return out


def build_dimensions(rng: np.random.Generator, n_prospects: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    states = {
        "CDMX": 0.16, "Jalisco": 0.09, "Nuevo León": 0.08, "Estado de México": 0.14,
        "Puebla": 0.05, "Guanajuato": 0.05, "Querétaro": 0.03, "Veracruz": 0.06,
        "Yucatán": 0.03, "Coahuila": 0.03, "Baja California": 0.04, "Chihuahua": 0.04,
        "Michoacán": 0.03, "San Luis Potosí": 0.03, "Otros": 0.14
    }
    channels = [
        dict(channel_id="CH001", channel_group="Search", channel_name="Paid Search", source="google", medium="cpc", is_paid=True, channel_status="active"),
        dict(channel_id="CH002", channel_group="Search", channel_name="Organic Search", source="google", medium="organic", is_paid=False, channel_status="active"),
        dict(channel_id="CH003", channel_group="Social", channel_name="Paid Social", source="meta", medium="paid_social", is_paid=True, channel_status="active"),
        dict(channel_id="CH004", channel_group="Display", channel_name="Programmatic Display", source="dv360", medium="display", is_paid=True, channel_status="active"),
        dict(channel_id="CH005", channel_group="CRM", channel_name="Email", source="crm", medium="email", is_paid=False, channel_status="active"),
        dict(channel_id="CH006", channel_group="Referral", channel_name="Referral", source="partners", medium="referral", is_paid=False, channel_status="active"),
        dict(channel_id="CH007", channel_group="Direct", channel_name="Direct", source="direct", medium="none", is_paid=False, channel_status="active"),
        dict(channel_id="CH008", channel_group="App", channel_name="App Push", source="app", medium="push", is_paid=False, channel_status="active"),
    ]
    devices = [
        ("DV001", "mobile", "Android", "Chrome", "web", True, 0.34),
        ("DV002", "mobile", "iOS", "Safari", "web", True, 0.20),
        ("DV003", "desktop", "Windows", "Chrome", "web", False, 0.18),
        ("DV004", "desktop", "Windows", "Edge", "web", False, 0.08),
        ("DV005", "desktop", "macOS", "Safari", "web", False, 0.06),
        ("DV006", "app", "Android", "InApp", "app", True, 0.06),
        ("DV007", "app", "iOS", "InApp", "app", True, 0.04),
        ("DV008", "tablet", "iOS", "Safari", "web", True, 0.04),
    ]
    stages = [
        ("ST01", 1, "Atracción", "Top Funnel", False, "Llegada inicial por canal digital"),
        ("ST02", 2, "Interacción", "Top Funnel", False, "Interacción relevante con contenidos o CTA"),
        ("ST03", 3, "Generación de lead", "Mid Funnel", False, "Captura de datos de contacto"),
        ("ST04", 4, "Lead calificado", "Mid Funnel", False, "Lead validado por intención y calidad"),
        ("ST05", 5, "Inicio de registro", "Bottom Funnel", False, "Inicio formal del proceso de alta"),
        ("ST06", 6, "Registro completado", "Bottom Funnel", False, "Registro finalizado con validaciones"),
        ("ST07", 7, "Activación digital", "Activation", False, "Primer login y primera acción de valor"),
        ("ST08", 8, "Activación consolidada", "Activation", True, "Segunda acción relevante o retención temprana"),
    ]

    campaign_templates = [
        ("CH001", "SEM Brand Captación", "search_brand", "lead_gen", "Google Ads", 0.18, 1.25, "CPC"),
        ("CH001", "SEM No Brand Retiro", "search_non_brand", "lead_gen", "Google Ads", 0.16, 1.10, "CPC"),
        ("CH001", "SEM Ahorro Voluntario", "search_non_brand", "conversion", "Google Ads", 0.14, 1.20, "CPC"),
        ("CH001", "SEM Competencia Afore", "search_competitor", "consideration", "Google Ads", 0.09, 0.95, "CPC"),
        ("CH002", "SEO Beneficios Afore", "seo", "awareness", "Google", 0.10, 0.85, "NA"),
        ("CH002", "SEO Ahorro Voluntario", "seo", "consideration", "Google", 0.09, 0.90, "NA"),
        ("CH003", "Meta Prospecting Jóvenes", "paid_social", "awareness", "Meta Ads", 0.10, 0.75, "CPM"),
        ("CH003", "Meta Lead Form Asalariados", "paid_social", "lead_gen", "Meta Ads", 0.11, 0.95, "CPL"),
        ("CH003", "Meta Remarketing Registro", "paid_social", "conversion", "Meta Ads", 0.06, 1.15, "CPC"),
        ("CH004", "Display Awareness Financiera", "display", "awareness", "DV360", 0.06, 0.60, "CPM"),
        ("CH004", "Display Remarketing Funnel", "display", "conversion", "DV360", 0.05, 0.95, "CPM"),
        ("CH005", "Email Reactivación Lead", "email", "reengagement", "CRM", 0.04, 1.35, "NA"),
        ("CH005", "Email Clientes Existentes", "email", "upsell", "CRM", 0.03, 1.40, "NA"),
        ("CH006", "Referral Nómina", "referral", "lead_gen", "Partners", 0.03, 1.10, "CPA"),
        ("CH006", "Referral Marketplace", "referral", "consideration", "Partners", 0.02, 0.95, "CPA"),
        ("CH007", "Tráfico Directo Sitio", "direct", "consideration", "Direct", 0.05, 1.00, "NA"),
        ("CH007", "Marca Directa", "direct", "conversion", "Direct", 0.03, 1.20, "NA"),
        ("CH008", "Push App Reactivación", "push", "reengagement", "App CRM", 0.02, 1.30, "NA"),
    ]

    channels_df = pd.DataFrame(channels)
    device_df = pd.DataFrame([{
        "device_id": a, "device_type": b, "os_name": c, "browser_name": d,
        "app_web_type": e, "is_mobile": f, "weight": g
    } for a, b, c, d, e, f, g in devices])
    stages_df = pd.DataFrame([{
        "stage_id": a, "stage_order": b, "stage_name": c, "stage_group": d,
        "is_terminal": e, "business_definition": f
    } for a, b, c, d, e, f in stages])

    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2025-12-31")
    campaign_rows = []
    for i, (ch_id, name, ctype, obj, platform, w, perf, cost_model) in enumerate(campaign_templates, start=1):
        sd = start + pd.Timedelta(days=int(rng.integers(0, 90)))
        ed = min(end, sd + pd.Timedelta(days=int(rng.integers(180, 365))))
        budget = float(np.round(rng.uniform(30000, 450000), 2)) if cost_model != "NA" else float(np.round(rng.uniform(10000, 120000), 2))
        campaign_rows.append({
            "campaign_id": f"CP{i:03d}",
            "channel_id": ch_id,
            "platform_campaign_key": f"{platform.lower().replace(' ', '_')}_{i:03d}",
            "campaign_name": name,
            "campaign_type": ctype,
            "objective": obj,
            "platform_name": platform,
            "start_date": sd.date().isoformat(),
            "end_date": ed.date().isoformat(),
            "budget_amount": budget,
            "cost_model": cost_model,
            "landing_page_url": f"https://www.aforesimulada.mx/{ctype}/{i:03d}",
            "campaign_status": "active" if ed >= pd.Timestamp("2025-10-01") else "completed",
            "traffic_weight": w,
            "performance_uplift": perf
        })
    campaigns_df = pd.DataFrame(campaign_rows)

    age_bands = ["18-24", "25-34", "35-44", "45-54", "55+"]
    age_probs = [0.16, 0.34, 0.25, 0.17, 0.08]
    income_bands = ["0-10k", "10k-20k", "20k-35k", "35k-50k", "50k+"]
    income_probs = [0.18, 0.30, 0.28, 0.15, 0.09]
    intent_bands = ["Baja", "Media", "Alta"]
    intent_probs = [0.40, 0.42, 0.18]

    def choice(arr, probs, size):
        return rng.choice(arr, size=size, p=np.array(probs) / np.sum(probs))

    prospects = pd.DataFrame({
        "prospect_id": [f"PR{i:06d}" for i in range(1, n_prospects + 1)],
        "geo_state": choice(list(states.keys()), list(states.values()), n_prospects),
        "age_band": choice(age_bands, age_probs, n_prospects),
        "income_band": choice(income_bands, income_probs, n_prospects),
        "intent_band": choice(intent_bands, intent_probs, n_prospects),
    })
    prospects["is_existing_customer"] = rng.random(n_prospects) < np.where(prospects["income_band"].isin(["35k-50k", "50k+"]), 0.16, 0.08)

    segments = []
    for _, r in prospects.iterrows():
        if r.is_existing_customer:
            seg = "Cliente existente digital"
        elif r.age_band in ["18-24", "25-34"] and r.intent_band in ["Media", "Alta"]:
            seg = "Joven digital"
        elif r.income_band in ["35k-50k", "50k+"] and r.intent_band == "Alta":
            seg = "Ahorro alto potencial"
        elif r.income_band in ["0-10k", "10k-20k"] and r.intent_band == "Baja":
            seg = "Baja intención masivo"
        elif r.age_band in ["35-44", "45-54"] and r.income_band in ["20k-35k", "35k-50k"]:
            seg = "Asalariado consolidado"
        else:
            seg = "Prospecto informativo"
        segments.append(seg)
    prospects["segment_label"] = segments

    def score_row(r) -> float:
        base = 45
        age_bonus = {"18-24": 1, "25-34": 8, "35-44": 10, "45-54": 7, "55+": 3}[r.age_band]
        inc_bonus = {"0-10k": -6, "10k-20k": 0, "20k-35k": 6, "35k-50k": 10, "50k+": 12}[r.income_band]
        intent_bonus = {"Baja": -12, "Media": 4, "Alta": 14}[r.intent_band]
        seg_bonus = {
            "Cliente existente digital": 10,
            "Joven digital": 6,
            "Ahorro alto potencial": 14,
            "Baja intención masivo": -10,
            "Asalariado consolidado": 8,
            "Prospecto informativo": 0
        }[r.segment_label]
        existing_bonus = 5 if r.is_existing_customer else 0
        noise = rng.normal(0, 7)
        return float(np.clip(base + age_bonus + inc_bonus + intent_bonus + seg_bonus + existing_bonus + noise, 5, 98))

    prospects["lead_quality_score"] = prospects.apply(score_row, axis=1).round(2)
    prospects["hashed_email"] = prospects["prospect_id"].map(lambda x: hashlib.sha256(f"{x}@mail.com".encode()).hexdigest()[:32])
    prospects["hashed_phone"] = prospects["prospect_id"].map(lambda x: hashlib.sha256(f"55{x[-6:]}".encode()).hexdigest()[:24])
    prospects["curp_hash"] = prospects["prospect_id"].map(lambda x: hashlib.sha256(f"CURP{x}".encode()).hexdigest()[:24])
    prospects["first_identified_ts"] = pd.NaT
    prospects = prospects[[
        "prospect_id", "hashed_email", "hashed_phone", "curp_hash", "first_identified_ts",
        "geo_state", "age_band", "income_band", "segment_label", "intent_band",
        "lead_quality_score", "is_existing_customer"
    ]]
    return prospects, channels_df, campaigns_df, device_df, stages_df


def generate_dataset(n_prospects: int = 24000, seed: int = 42) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    prospects, channels_df, campaigns_df, device_df, stages_df = build_dimensions(rng, n_prospects)

    campaign_meta = campaigns_df.set_index("campaign_id").to_dict("index")
    channel_meta = channels_df.set_index("channel_id").to_dict("index")
    device_meta = device_df.set_index("device_id").to_dict("index")

    landing_pages = [
        "/ahorro-voluntario", "/comparador-afores", "/registro-digital", "/beneficios-fiscales",
        "/simulador-retiro", "/cambio-afores", "/tramite-digital", "/faq-ahorro"
    ]
    page_names = {
        "awareness": ["home", "blog_beneficios", "blog_retiro", "comparador", "landing_awareness"],
        "consideration": ["comparador", "beneficios", "faq", "simulador", "landing_consideration"],
        "lead": ["landing_form", "lead_form", "beneficios", "simulador", "whatsapp_cta"],
        "registration": ["registro_inicio", "registro_datos", "documentos", "kyc", "biometrico", "confirmacion"],
        "activation": ["login", "dashboard", "ahorro_voluntario", "mi_cuenta", "movimientos", "simulador_aportacion"]
    }
    cta_names = ["Solicitar información", "Quiero ahorrar", "Iniciar registro", "Ver beneficios", "Abrir cuenta digital", "Hablar con asesor"]
    lead_source_map = {"CH001": "web_form", "CH002": "web_form", "CH003": "lead_ad", "CH004": "landing_form", "CH005": "email_click", "CH006": "partner_form", "CH007": "direct_form", "CH008": "app_cta"}
    activation_channel_map = {"CH001": "web", "CH002": "web", "CH003": "web", "CH004": "web", "CH005": "email", "CH006": "partner", "CH007": "web", "CH008": "app"}
    interest_map = {
        "Joven digital": "Ahorro voluntario",
        "Ahorro alto potencial": "Aportaciones complementarias",
        "Asalariado consolidado": "Cambio / registro Afore",
        "Cliente existente digital": "Ahorro voluntario",
        "Baja intención masivo": "Información general",
        "Prospecto informativo": "Simulador de retiro",
    }

    def choose_campaign(prospect_row: dict) -> str:
        w = campaigns_df["traffic_weight"].astype(float).to_numpy().copy()
        if prospect_row["segment_label"] == "Cliente existente digital":
            w[campaigns_df["channel_id"].isin(["CH005", "CH007", "CH008"]).to_numpy()] *= 2.5
            w[campaigns_df["channel_id"].eq("CH004").to_numpy()] *= 0.4
        if prospect_row["segment_label"] == "Joven digital":
            w[campaigns_df["channel_id"].isin(["CH003", "CH001"]).to_numpy()] *= 1.35
            w[campaigns_df["campaign_name"].str.contains("Jóvenes", regex=False).to_numpy()] *= 1.5
        if prospect_row["intent_band"] == "Alta":
            w[campaigns_df["objective"].isin(["conversion", "lead_gen", "reengagement", "upsell"]).to_numpy()] *= 1.4
        elif prospect_row["intent_band"] == "Baja":
            w[campaigns_df["objective"].eq("awareness").to_numpy()] *= 1.4
            w[campaigns_df["channel_id"].eq("CH004").to_numpy()] *= 1.3
            w[campaigns_df["objective"].eq("conversion").to_numpy()] *= 0.7
        w = w / w.sum()
        return rng.choice(campaigns_df["campaign_id"].to_numpy(), p=w)

    def choose_device(prospect_row: dict, channel_id: str) -> str:
        w = device_df["weight"].astype(float).to_numpy().copy()
        age = prospect_row["age_band"]
        seg = prospect_row["segment_label"]
        if age in ["18-24", "25-34"]:
            w[device_df["device_type"].isin(["mobile", "app"]).to_numpy()] *= 1.35
            w[device_df["device_type"].eq("desktop").to_numpy()] *= 0.75
        elif age in ["45-54", "55+"]:
            w[device_df["device_type"].eq("desktop").to_numpy()] *= 1.25
            w[device_df["device_type"].eq("app").to_numpy()] *= 0.65
        if channel_id == "CH008":
            w[device_df["app_web_type"].eq("app").to_numpy()] *= 6
        elif channel_id == "CH004":
            w[device_df["device_type"].eq("desktop").to_numpy()] *= 1.2
        if seg == "Cliente existente digital":
            w[device_df["app_web_type"].eq("app").to_numpy()] *= 1.6
        w = w / w.sum()
        return rng.choice(device_df["device_id"].to_numpy(), p=w)

    def calc_probabilities(prospect_row: dict, campaign_row: dict, device_row: dict) -> tuple[float, float, float, float, float, float, float]:
        q = prospect_row["lead_quality_score"]
        intent = prospect_row["intent_band"]
        seg = prospect_row["segment_label"]
        objective = campaign_row["objective"]
        perf = campaign_row["performance_uplift"]
        channel = campaign_row["channel_id"]
        device_type = device_row["device_type"]
        is_app = device_row["app_web_type"] == "app"
        is_mobile = device_row["is_mobile"]
        existing = prospect_row["is_existing_customer"]

        intent_term = {"Baja": -0.8, "Media": 0.0, "Alta": 0.8}[intent]
        objective_term = {"awareness": -0.35, "consideration": 0.0, "lead_gen": 0.55, "conversion": 0.75, "reengagement": 0.95, "upsell": 1.05}[objective]
        channel_term = {"CH001": 0.35, "CH002": 0.10, "CH003": 0.05, "CH004": -0.30, "CH005": 0.65, "CH006": 0.50, "CH007": 0.45, "CH008": 0.75}[channel]
        device_term = 0.15 if device_type == "desktop" else (-0.05 if is_mobile and not is_app else 0.10)
        seg_term = {
            "Cliente existente digital": 0.55,
            "Joven digital": 0.15,
            "Ahorro alto potencial": 0.45,
            "Baja intención masivo": -0.45,
            "Asalariado consolidado": 0.30,
            "Prospecto informativo": -0.10
        }[seg]

        p_interaction = logistic(-0.7 + q * 0.027 + intent_term * 0.35 + channel_term * 0.45 + perf * 0.12)
        p_lead = logistic(-4.55 + q * 0.034 + intent_term * 0.85 + objective_term * 0.85 + channel_term * 0.55 + device_term * 0.25 + seg_term * 0.45 + perf * 0.12)
        p_qual = logistic(-2.0 + q * 0.045 + (0.30 if objective in ["lead_gen", "conversion", "reengagement", "upsell"] else -0.10) + (0.15 if existing else 0))
        p_reg_start = logistic(-2.2 + q * 0.030 + objective_term * 0.55 + channel_term * 0.25 + seg_term * 0.35 + (0.15 if existing else 0))
        p_reg_complete = logistic(-1.1 + q * 0.022 + (0.25 if device_type == "desktop" else 0) + (0.10 if is_app else -0.05) + seg_term * 0.18)
        p_activate = logistic(-0.8 + q * 0.017 + (0.22 if existing else 0) + (0.20 if channel in ["CH005", "CH008", "CH007"] else 0) + (0.10 if is_app else 0))
        p_consolidate = logistic(-1.0 + q * 0.015 + seg_term * 0.22 + (0.25 if existing else 0) + (0.12 if channel in ["CH005", "CH008"] else 0))
        return p_interaction, p_lead, p_qual, p_reg_start, p_reg_complete, p_activate, p_consolidate

    journeys, sessions, events, leads, registrations, activations, journey_stages = [], [], [], [], [], [], []
    journey_counter = session_counter = event_counter = lead_counter = reg_counter = act_counter = journey_stage_counter = 1
    lead_count_by_prospect: dict[str, int] = {}

    for prospect in prospects.to_dict("records"):
        base_count = 1
        if rng.random() < (0.16 if prospect["intent_band"] == "Alta" else 0.08):
            base_count += 1
        if rng.random() < (0.05 if prospect["segment_label"] in ["Joven digital", "Cliente existente digital"] else 0.02):
            base_count += 1

        last_ts = None
        for _ in range(base_count):
            campaign_id = choose_campaign(prospect)
            campaign = campaign_meta[campaign_id]
            channel_id = campaign["channel_id"]
            device_id = choose_device(prospect, channel_id)
            device = device_meta[device_id]

            cstart = pd.Timestamp(campaign["start_date"])
            cend = pd.Timestamp(campaign["end_date"]) + pd.Timedelta(hours=23, minutes=59)
            start_ts = random_ts_between(rng, cstart, cend)
            if last_ts is not None and start_ts <= last_ts:
                start_ts = min(pd.Timestamp("2025-12-31 23:00:00"), last_ts + pd.Timedelta(days=int(rng.integers(5, 60)), hours=int(rng.integers(0, 12))))
            last_ts = start_ts

            p_interaction, p_lead, p_qual, p_reg_start, p_reg_complete, p_activate, p_consolidate = calc_probabilities(prospect, campaign, device)
            reached = ["ST01"]
            stage_ts = {"ST01": start_ts}
            current_stage_id = "ST01"

            if rng.random() < p_interaction:
                t2 = start_ts + pd.Timedelta(minutes=int(max(1, rng.lognormal(np.log(18), 0.7))))
                reached.append("ST02")
                stage_ts["ST02"] = t2
                current_stage_id = "ST02"

                if rng.random() < p_lead:
                    t3 = t2 + pd.Timedelta(minutes=int(max(1, rng.lognormal(np.log(240), 1.0))))
                    reached.append("ST03")
                    stage_ts["ST03"] = t3
                    current_stage_id = "ST03"

                    lead_score = float(np.clip(prospect["lead_quality_score"] + rng.normal(0, 8), 0, 100))
                    contactable = bool(rng.random() < np.interp(lead_score, [0, 100], [0.78, 0.98]))

                    if rng.random() < p_qual and contactable:
                        t4 = t3 + pd.Timedelta(minutes=response_time_minutes(rng, channel_id, lead_score))
                        reached.append("ST04")
                        stage_ts["ST04"] = t4
                        current_stage_id = "ST04"

                        if rng.random() < p_reg_start:
                            t5 = t4 + pd.Timedelta(minutes=int(max(5, rng.lognormal(np.log(720), 1.05))))
                            reached.append("ST05")
                            stage_ts["ST05"] = t5
                            current_stage_id = "ST05"

                            doc_flag = bool(rng.random() < np.interp(lead_score, [0, 100], [0.45, 0.90]))
                            kyc_flag = bool(doc_flag and (rng.random() < np.interp(lead_score, [0, 100], [0.52, 0.93])))
                            bio_flag = bool(kyc_flag and (rng.random() < np.interp(lead_score, [0, 100], [0.38, 0.84])))

                            if doc_flag and kyc_flag and bio_flag and rng.random() < p_reg_complete:
                                t6 = t5 + pd.Timedelta(minutes=int(max(15, rng.lognormal(np.log(900), 0.95))))
                                reached.append("ST06")
                                stage_ts["ST06"] = t6
                                current_stage_id = "ST06"

                                if rng.random() < p_activate:
                                    t7 = t6 + pd.Timedelta(minutes=int(max(5, rng.lognormal(np.log(2160), 1.1))))
                                    reached.append("ST07")
                                    stage_ts["ST07"] = t7
                                    current_stage_id = "ST07"

                                    if rng.random() < p_consolidate:
                                        t8 = t7 + pd.Timedelta(days=int(max(1, rng.lognormal(np.log(8), 0.6))))
                                        t8 = min(t8, pd.Timestamp("2025-12-31 23:59:00"))
                                        reached.append("ST08")
                                        stage_ts["ST08"] = t8
                                        current_stage_id = "ST08"

            journey_end_ts = stage_ts[current_stage_id] + pd.Timedelta(minutes=int(rng.integers(5, 120)))
            is_closed = not (journey_end_ts >= pd.Timestamp("2025-12-15") and current_stage_id in ["ST03", "ST04", "ST05"])

            journey_id = f"JR{journey_counter:07d}"
            anonymous_visitor_id = f"AV{journey_counter:09d}"

            max_stage_order = int(current_stage_id.replace("ST", ""))
            session_n_ranges = {1: (1, 1), 2: (1, 2), 3: (1, 2), 4: (1, 3), 5: (2, 4), 6: (2, 5), 7: (3, 5), 8: (3, 6)}
            lo, hi = session_n_ranges[max_stage_order]
            n_sessions = int(rng.integers(lo, hi + 1))
            anchor_times = sorted(stage_ts.values())
            if n_sessions == 1:
                session_times = [start_ts]
            else:
                full_start, full_end = anchor_times[0], journey_end_ts
                session_times = [full_start]
                for _ in range(max(0, n_sessions - 2)):
                    session_times.append(random_ts_between(rng, full_start, full_end))
                session_times.append(full_end - pd.Timedelta(minutes=int(rng.integers(10, 90))))
                session_times = sorted(session_times)

            session_ids = []
            lead_session_id = None
            reg_session_id = None

            for s_idx, s_ts in enumerate(session_times, start=1):
                sess_channel_id, sess_campaign_id, sess_device_id = channel_id, campaign_id, device_id
                if s_idx > 1:
                    drift = rng.random()
                    if current_stage_id in ["ST05", "ST06", "ST07", "ST08"] and drift < 0.28:
                        sess_channel_id, sess_campaign_id = "CH007", "CP016"
                    elif current_stage_id in ["ST04", "ST05", "ST06"] and drift < 0.20:
                        sess_channel_id, sess_campaign_id = "CH005", "CP012"
                    elif current_stage_id in ["ST07", "ST08"] and prospect["is_existing_customer"] and drift < 0.20:
                        sess_channel_id, sess_campaign_id = "CH008", "CP018"
                    if rng.random() < 0.22:
                        sess_device_id = choose_device(prospect, sess_channel_id)

                pv_base = 1 + max_stage_order // 2
                pageviews = int(np.clip(rng.poisson(pv_base + (1 if s_idx == n_sessions and max_stage_order >= 5 else 0)), 1, 15))
                cta_clicks = int(np.clip(rng.poisson(0.5 + (1 if max_stage_order >= 3 else 0) + (0.5 if s_idx == n_sessions and max_stage_order >= 5 else 0)), 0, 8))
                qualified_flag = bool((pageviews >= 3 or cta_clicks >= 1) and max_stage_order >= 2)
                bounce_flag = bool(pageviews == 1 and cta_clicks == 0 and s_idx == 1 and max_stage_order == 1)
                session_duration = int(np.clip(rng.lognormal(np.log(6 + pageviews * 2), 0.55), 2, 90))
                session_end_ts = min(journey_end_ts, s_ts + pd.Timedelta(minutes=session_duration))

                session_id = f"SS{session_counter:08d}"
                session_counter += 1
                session_ids.append(session_id)

                landing_page = campaign["landing_page_url"].replace("https://www.aforesimulada.mx", "") if s_idx == 1 else rng.choice(landing_pages)
                sessions.append({
                    "session_id": session_id,
                    "journey_id": journey_id,
                    "anonymous_visitor_id": anonymous_visitor_id,
                    "prospect_id": prospect["prospect_id"],
                    "campaign_id": sess_campaign_id,
                    "channel_id": sess_channel_id,
                    "device_id": sess_device_id,
                    "session_start_ts": s_ts,
                    "session_end_ts": session_end_ts,
                    "landing_page_url": landing_page,
                    "pageviews_qty": pageviews,
                    "cta_click_qty": cta_clicks,
                    "qualified_interaction_flag": qualified_flag,
                    "bounce_flag": bounce_flag
                })

                session_events = []
                event_ts_list = [s_ts + pd.Timedelta(minutes=float(x)) for x in sorted(rng.uniform(0, max(1, session_duration), size=max(pageviews, 2)))]
                category_key = "awareness" if max_stage_order <= 2 else ("lead" if max_stage_order <= 4 else ("registration" if max_stage_order <= 6 else "activation"))

                for ets in event_ts_list[:pageviews]:
                    session_events.append({"event_name": "page_view", "event_category": "navigation", "page_name": rng.choice(page_names[category_key]), "cta_name": None, "is_key_interaction": False, "event_ts": ets})
                for _ in range(cta_clicks):
                    ets = s_ts + pd.Timedelta(minutes=float(rng.uniform(0, max(1, session_duration))))
                    session_events.append({"event_name": "cta_click", "event_category": "engagement", "page_name": rng.choice(page_names["consideration"]), "cta_name": rng.choice(cta_names), "is_key_interaction": True, "event_ts": ets})

                milestones = [
                    ("ST02", "content_engagement", "engagement", "beneficios", None),
                    ("ST03", "form_submit", "lead", "lead_form", "Enviar datos"),
                    ("ST04", "lead_qualified", "lead", "lead_form", None),
                    ("ST05", "registration_start", "registration", "registro_inicio", "Comenzar registro"),
                    ("ST06", "registration_complete", "registration", "confirmacion", None),
                    ("ST07", "first_login", "activation", "login", None),
                    ("ST08", "second_key_action", "activation", "ahorro_voluntario", "Programar aportación"),
                ]
                for stg, ev_name, ev_cat, page_name, cta_name in milestones:
                    if stg in stage_ts and s_ts <= stage_ts[stg] <= session_end_ts:
                        session_events.append({
                            "event_name": ev_name, "event_category": ev_cat, "page_name": page_name,
                            "cta_name": cta_name, "is_key_interaction": True, "event_ts": stage_ts[stg]
                        })
                        if stg == "ST03":
                            lead_session_id = session_id
                        if stg == "ST05":
                            reg_session_id = session_id

                for er in sorted(session_events, key=lambda x: x["event_ts"]):
                    events.append({
                        "event_id": f"EV{event_counter:09d}",
                        "session_id": session_id,
                        "journey_id": journey_id,
                        "prospect_id": prospect["prospect_id"],
                        "campaign_id": sess_campaign_id,
                        "channel_id": sess_channel_id,
                        "device_id": sess_device_id,
                        "event_ts": er["event_ts"],
                        "event_name": er["event_name"],
                        "event_category": er["event_category"],
                        "page_name": er["page_name"],
                        "cta_name": er["cta_name"],
                        "is_key_interaction": er["is_key_interaction"]
                    })
                    event_counter += 1

            lead_id = None
            registration_id = None

            if "ST03" in reached:
                lead_id = f"LD{lead_counter:08d}"
                lead_counter += 1
                base_lead_score = float(np.clip(prospect["lead_quality_score"] + rng.normal(0, 8), 0, 100))
                is_contactable = bool(rng.random() < np.interp(base_lead_score, [0, 100], [0.80, 0.98]))
                is_duplicate = lead_count_by_prospect.get(prospect["prospect_id"], 0) > 0
                lead_count_by_prospect[prospect["prospect_id"]] = lead_count_by_prospect.get(prospect["prospect_id"], 0) + 1
                rt_minutes = response_time_minutes(rng, channel_id, base_lead_score)
                qualification_status = "qualified" if "ST04" in reached else ("unqualified" if is_contactable else "invalid_contact")
                qualification_reason = (
                    "Cumple score e intención mínima"
                    if qualification_status == "qualified"
                    else ("Datos no contactables" if qualification_status == "invalid_contact" else rng.choice(["Baja intención declarada", "Perfil no objetivo", "Duplicado operacional"]))
                )

                leads.append({
                    "lead_id": lead_id,
                    "journey_id": journey_id,
                    "prospect_id": prospect["prospect_id"],
                    "session_id": lead_session_id or session_ids[0],
                    "lead_created_ts": stage_ts["ST03"],
                    "lead_source_type": lead_source_map[channel_id],
                    "form_name": rng.choice(["lead_form_main", "lead_form_short", "simulator_capture", "contact_request"]),
                    "product_interest": interest_map[prospect["segment_label"]],
                    "lead_status": "converted_to_registration" if "ST05" in reached else ("nurtured" if "ST04" in reached else "lost"),
                    "lead_score": round(base_lead_score, 2),
                    "qualification_status": qualification_status,
                    "qualification_reason": qualification_reason,
                    "response_time_minutes": rt_minutes,
                    "is_duplicate": is_duplicate,
                    "is_contactable": is_contactable
                })

            if "ST05" in reached:
                registration_id = f"RG{reg_counter:08d}"
                reg_counter += 1
                completed = "ST06" in reached
                doc_flag = bool(completed or rng.random() < 0.74)
                kyc_flag = bool(completed or (doc_flag and rng.random() < 0.79))
                bio_flag = bool(completed or (kyc_flag and rng.random() < 0.69))
                rejection_reason = None
                abandonment_reason = None
                if not completed:
                    abandonment_reason = rng.choice(["Carga documental incompleta", "Validación KYC fallida", "Biometría no exitosa", "Tiempo de espera alto", "Usuario salió del flujo"])
                    if "fallida" in abandonment_reason:
                        rejection_reason = abandonment_reason

                registrations.append({
                    "registration_id": registration_id,
                    "journey_id": journey_id,
                    "prospect_id": prospect["prospect_id"],
                    "lead_id": lead_id,
                    "registration_started_ts": stage_ts["ST05"],
                    "registration_completed_ts": stage_ts.get("ST06", pd.NaT),
                    "registration_status": "completed" if completed else "abandoned",
                    "step_reached": "confirmation" if completed else rng.choice(["personal_data", "documents", "kyc", "biometric"]),
                    "document_upload_flag": doc_flag,
                    "kyc_validation_flag": kyc_flag,
                    "biometric_validation_flag": bio_flag,
                    "rejection_reason": rejection_reason,
                    "abandonment_reason": abandonment_reason
                })

            if "ST07" in reached:
                activation_id = f"AC{act_counter:08d}"
                act_counter += 1
                retained_7d = bool("ST08" in reached or rng.random() < np.interp(prospect["lead_quality_score"], [0, 100], [0.30, 0.72]))
                retained_30d = bool(retained_7d and (("ST08" in reached and rng.random() < 0.78) or rng.random() < np.interp(prospect["lead_quality_score"], [0, 100], [0.18, 0.50])))

                activations.append({
                    "activation_id": activation_id,
                    "journey_id": journey_id,
                    "prospect_id": prospect["prospect_id"],
                    "registration_id": registration_id,
                    "first_login_ts": stage_ts["ST07"],
                    "first_key_action_ts": stage_ts["ST07"] + pd.Timedelta(minutes=int(rng.integers(2, 120))),
                    "second_key_action_ts": stage_ts.get("ST08", pd.NaT),
                    "activation_status": "consolidated" if "ST08" in reached else "activated",
                    "activation_channel": activation_channel_map[channel_id],
                    "retained_7d_flag": retained_7d,
                    "retained_30d_flag": retained_30d
                })

            prev_stage = None
            prev_ts = None
            for idx, stg in enumerate(reached):
                st_ts = stage_ts[stg]
                stage_status = "completed" if idx < len(reached) - 1 or stg in ["ST06", "ST07", "ST08"] else "abandoned"
                journey_stages.append({
                    "journey_stage_id": f"JS{journey_stage_counter:09d}",
                    "journey_id": journey_id,
                    "stage_id": stg,
                    "prospect_id": prospect["prospect_id"],
                    "session_id": lead_session_id if stg in ["ST03", "ST04"] else reg_session_id if stg in ["ST05", "ST06"] else session_ids[min(idx, len(session_ids) - 1)],
                    "stage_ts": st_ts,
                    "stage_status": stage_status,
                    "previous_stage_id": prev_stage,
                    "time_from_previous_stage_minutes": None if prev_ts is None else int((st_ts - prev_ts).total_seconds() // 60),
                    "stage_source": channel_meta[channel_id]["channel_name"]
                })
                journey_stage_counter += 1
                prev_stage, prev_ts = stg, st_ts

            journeys.append({
                "journey_id": journey_id,
                "anonymous_visitor_id": anonymous_visitor_id,
                "prospect_id": prospect["prospect_id"],
                "primary_campaign_id": campaign_id,
                "primary_channel_id": channel_id,
                "first_device_id": device_id,
                "attribution_model": rng.choice(["last_non_direct", "first_touch", "position_based"], p=[0.55, 0.20, 0.25]),
                "journey_start_ts": start_ts,
                "journey_end_ts": journey_end_ts,
                "current_stage_id": current_stage_id,
                "is_closed": is_closed
            })
            journey_counter += 1

    journeys_df = pd.DataFrame(journeys)
    sessions_df = pd.DataFrame(sessions)
    events_df = pd.DataFrame(events)
    leads_df = pd.DataFrame(leads)
    regs_df = pd.DataFrame(registrations)
    acts_df = pd.DataFrame(activations)
    stages_fact_df = pd.DataFrame(journey_stages)

    first_ts = journeys_df.groupby("prospect_id")["journey_start_ts"].min()
    prospects["first_identified_ts"] = prospects["prospect_id"].map(first_ts)

    funnel_events_df = stages_fact_df.merge(stages_df[["stage_id", "stage_name", "stage_order", "stage_group"]], on="stage_id", how="left")

    income_base = {"0-10k": 200, "10k-20k": 450, "20k-35k": 900, "35k-50k": 1500, "50k+": 2500}
    segment_mult = {
        "Joven digital": 0.90,
        "Ahorro alto potencial": 1.80,
        "Asalariado consolidado": 1.20,
        "Cliente existente digital": 1.50,
        "Baja intención masivo": 0.60,
        "Prospecto informativo": 0.80
    }

    conv = journeys_df.merge(
        leads_df[["journey_id", "lead_id", "lead_created_ts", "lead_score", "qualification_status"]],
        on="journey_id", how="left"
    ).merge(
        regs_df[["journey_id", "registration_id", "registration_started_ts", "registration_completed_ts", "registration_status", "abandonment_reason"]],
        on="journey_id", how="left"
    ).merge(
        acts_df[["journey_id", "activation_id", "first_login_ts", "second_key_action_ts", "activation_status", "retained_7d_flag", "retained_30d_flag"]],
        on="journey_id", how="left"
    ).merge(
        prospects[["prospect_id", "income_band", "segment_label", "lead_quality_score"]],
        on="prospect_id", how="left"
    )

    retained_7 = conv["retained_7d_flag"].where(conv["retained_7d_flag"].notna(), False).astype(bool)
    retained_30 = conv["retained_30d_flag"].where(conv["retained_30d_flag"].notna(), False).astype(bool)

    conv["estimated_monthly_contribution"] = np.where(
        conv["activation_id"].notna(),
        conv["income_band"].map(income_base).astype(float) *
        conv["segment_label"].map(segment_mult).astype(float) *
        np.where(conv["activation_status"].eq("consolidated"), 1.15, 1.0) *
        np.clip((conv["lead_quality_score"].fillna(50) / 70), 0.7, 1.5),
        0.0
    ).round(2)
    conv["estimated_12m_balance"] = (
        conv["estimated_monthly_contribution"] * 12 *
        np.where(retained_30, 1.0, np.where(retained_7, 0.85, 0.70))
    ).round(2)
    conv["estimated_annual_revenue"] = (conv["estimated_12m_balance"] * 0.018).round(2)
    conv["is_lead"] = conv["lead_id"].notna()
    conv["is_registered"] = conv["registration_status"].eq("completed")
    conv["is_activated"] = conv["activation_id"].notna()
    conv["is_consolidated"] = conv["activation_status"].eq("consolidated")

    conversions_df = conv[[
        "journey_id", "prospect_id", "primary_campaign_id", "primary_channel_id", "current_stage_id",
        "lead_id", "registration_id", "activation_id", "lead_created_ts", "registration_started_ts",
        "registration_completed_ts", "first_login_ts", "second_key_action_ts", "qualification_status",
        "registration_status", "activation_status", "is_lead", "is_registered", "is_activated",
        "is_consolidated", "estimated_monthly_contribution", "estimated_12m_balance", "estimated_annual_revenue"
    ]].copy()

    campaigns_view = campaigns_df.merge(channels_df, on="channel_id", how="left").drop(columns=["traffic_weight", "performance_uplift"], errors="ignore")

    return {
        "DIM_PROSPECT": prospects,
        "DIM_CHANNEL": channels_df.drop(columns=["weight"], errors="ignore"),
        "DIM_CAMPAIGN": campaigns_df.drop(columns=["traffic_weight", "performance_uplift"], errors="ignore"),
        "DIM_DEVICE": device_df.drop(columns=["weight"], errors="ignore"),
        "DIM_FUNNEL_STAGE": stages_df,
        "FACT_JOURNEY": journeys_df,
        "FACT_SESSION": sessions_df,
        "FACT_INTERACTION_EVENT": events_df,
        "FACT_LEAD": leads_df,
        "FACT_REGISTRATION": regs_df,
        "FACT_ACTIVATION": acts_df,
        "FACT_JOURNEY_STAGE": stages_fact_df,
        "users": prospects.copy(),
        "campaigns": campaigns_view,
        "sessions": sessions_df.copy(),
        "funnel_events": funnel_events_df,
        "conversions": conversions_df,
    }


def write_outputs(tables: dict[str, pd.DataFrame], output_dir: Path, db_path: Path, seed: int, n_prospects: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = output_dir / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    for name, df in tables.items():
        fmt_df(df).to_csv(csv_dir / f"{name}.csv", index=False)

    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)

    core_names = [
        "DIM_PROSPECT", "DIM_CHANNEL", "DIM_CAMPAIGN", "DIM_DEVICE", "DIM_FUNNEL_STAGE",
        "FACT_JOURNEY", "FACT_SESSION", "FACT_INTERACTION_EVENT", "FACT_LEAD",
        "FACT_REGISTRATION", "FACT_ACTIVATION", "FACT_JOURNEY_STAGE"
    ]
    simple_names = ["users", "campaigns", "sessions", "funnel_events", "conversions"]

    for name in core_names + simple_names:
        fmt_df(tables[name]).to_sql(name, conn, index=False, if_exists="replace")

    cur = conn.cursor()
    cur.executescript("""
    CREATE INDEX IF NOT EXISTS idx_fact_journey_prospect ON FACT_JOURNEY(prospect_id);
    CREATE INDEX IF NOT EXISTS idx_fact_session_journey ON FACT_SESSION(journey_id);
    CREATE INDEX IF NOT EXISTS idx_fact_event_session ON FACT_INTERACTION_EVENT(session_id);
    CREATE INDEX IF NOT EXISTS idx_fact_lead_journey ON FACT_LEAD(journey_id);
    CREATE INDEX IF NOT EXISTS idx_fact_reg_journey ON FACT_REGISTRATION(journey_id);
    CREATE INDEX IF NOT EXISTS idx_fact_act_journey ON FACT_ACTIVATION(journey_id);
    CREATE INDEX IF NOT EXISTS idx_fact_stage_journey ON FACT_JOURNEY_STAGE(journey_id);

    DROP VIEW IF EXISTS VW_FUNNEL_STAGE_SUMMARY;
    CREATE VIEW VW_FUNNEL_STAGE_SUMMARY AS
    SELECT
        s.stage_id,
        s.stage_order,
        s.stage_name,
        COUNT(DISTINCT js.journey_id) AS journeys_reached
    FROM DIM_FUNNEL_STAGE s
    LEFT JOIN FACT_JOURNEY_STAGE js
      ON s.stage_id = js.stage_id
    GROUP BY 1,2,3
    ORDER BY s.stage_order;

    DROP VIEW IF EXISTS VW_CAMPAIGN_PERFORMANCE;
    CREATE VIEW VW_CAMPAIGN_PERFORMANCE AS
    SELECT
        c.campaign_id,
        c.campaign_name,
        ch.channel_name,
        COUNT(DISTINCT j.journey_id) AS journeys,
        COUNT(DISTINCT l.lead_id) AS leads,
        COUNT(DISTINCT r.registration_id) AS registrations_started,
        COUNT(DISTINCT a.activation_id) AS activations,
        ROUND(SUM(cv.estimated_annual_revenue), 2) AS estimated_annual_revenue
    FROM DIM_CAMPAIGN c
    LEFT JOIN DIM_CHANNEL ch ON c.channel_id = ch.channel_id
    LEFT JOIN FACT_JOURNEY j ON c.campaign_id = j.primary_campaign_id
    LEFT JOIN FACT_LEAD l ON j.journey_id = l.journey_id
    LEFT JOIN FACT_REGISTRATION r ON j.journey_id = r.journey_id
    LEFT JOIN FACT_ACTIVATION a ON j.journey_id = a.journey_id
    LEFT JOIN conversions cv ON j.journey_id = cv.journey_id
    GROUP BY 1,2,3;

    DROP VIEW IF EXISTS VW_ESTIMATED_REVENUE;
    CREATE VIEW VW_ESTIMATED_REVENUE AS
    SELECT
        activation_id,
        journey_id,
        prospect_id,
        estimated_monthly_contribution,
        estimated_12m_balance,
        estimated_annual_revenue
    FROM conversions
    WHERE activation_id IS NOT NULL;
    """)
    conn.commit()
    conn.close()

    stages = tables["FACT_JOURNEY_STAGE"].groupby("stage_id")["journey_id"].nunique().reindex(tables["DIM_FUNNEL_STAGE"]["stage_id"]).fillna(0).astype(int)
    stage_rates = (stages / len(tables["FACT_JOURNEY"]) * 100).round(2)
    checks = {
        "sessions_missing_journey": int((~tables["FACT_SESSION"]["journey_id"].isin(tables["FACT_JOURNEY"]["journey_id"])).sum()),
        "events_missing_session": int((~tables["FACT_INTERACTION_EVENT"]["session_id"].isin(tables["FACT_SESSION"]["session_id"])).sum()),
        "events_missing_journey": int((~tables["FACT_INTERACTION_EVENT"]["journey_id"].isin(tables["FACT_JOURNEY"]["journey_id"])).sum()),
        "leads_missing_session": int((~tables["FACT_LEAD"]["session_id"].isin(tables["FACT_SESSION"]["session_id"])).sum()),
        "regs_missing_lead": int((~tables["FACT_REGISTRATION"]["lead_id"].isin(tables["FACT_LEAD"]["lead_id"])).sum()),
        "acts_missing_reg": int((~tables["FACT_ACTIVATION"]["registration_id"].isin(tables["FACT_REGISTRATION"]["registration_id"])).sum()),
        "journey_stage_missing_stage": int((~tables["FACT_JOURNEY_STAGE"]["stage_id"].isin(tables["DIM_FUNNEL_STAGE"]["stage_id"])).sum()),
        "journey_end_before_start": int((tables["FACT_JOURNEY"]["journey_end_ts"] < tables["FACT_JOURNEY"]["journey_start_ts"]).sum())
    }

    summary = {
        "generation_parameters": {
            "seed": seed,
            "prospects": n_prospects,
            "date_start": "2025-01-01",
            "date_end": "2025-12-31"
        },
        "row_counts": {
            "prospects": int(len(tables["DIM_PROSPECT"])),
            "journeys": int(len(tables["FACT_JOURNEY"])),
            "sessions": int(len(tables["FACT_SESSION"])),
            "events": int(len(tables["FACT_INTERACTION_EVENT"])),
            "leads": int(len(tables["FACT_LEAD"])),
            "registrations_started": int(len(tables["FACT_REGISTRATION"])),
            "activations": int(len(tables["FACT_ACTIVATION"]))
        },
        "stage_counts": {k: int(v) for k, v in stages.to_dict().items()},
        "stage_rates_pct": {k: float(v) for k, v in stage_rates.to_dict().items()},
        "integrity_checks": checks
    }
    with open(output_dir / "dataset_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic Afore digital funnel dataset.")
    parser.add_argument("--prospects", type=int, default=24000, help="Number of synthetic prospects.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--output-dir", type=str, default="synthetic_afore_output", help="Folder for CSV and summary outputs.")
    parser.add_argument("--db-path", type=str, default="synthetic_afore_output/synthetic_afore_funnel.db", help="SQLite output path.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    db_path = Path(args.db_path)
    tables = generate_dataset(n_prospects=args.prospects, seed=args.seed)
    write_outputs(tables, output_dir=output_dir, db_path=db_path, seed=args.seed, n_prospects=args.prospects)
    print(f"Dataset generated in: {output_dir.resolve()}")
    print(f"SQLite DB: {db_path.resolve()}")


if __name__ == "__main__":
    main()
