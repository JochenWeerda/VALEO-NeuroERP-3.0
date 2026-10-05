"""JSON-first adapters into canonical VALEO ration target contracts."""
from __future__ import annotations
from datetime import date
from hashlib import sha256
import json
from typing import Any

AGRIRouter_TYPES = {"iso:11783:-10:time_log:protobuf", "iso:11783:-10:taskdata:zip"}

def payload_hash(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def _number(value: Any, *, default: float | None = None) -> float | None:
    if value is None or value == "": return default
    try: return float(value)
    except (TypeError, ValueError): return default

def agrirouter_to_feeding_log(payload: dict[str, Any]) -> dict[str, Any]:
    """Map an already decoded EFDI/TaskData mixer message to F1 FeedingControlIn."""
    message_type = str(payload.get("message_type") or payload.get("technical_message_type") or "")
    if message_type not in AGRIRouter_TYPES:
        raise ValueError(f"Nicht unterstuetzter agrirouter message_type: {message_type}")
    context_id = str(payload.get("context_id") or payload.get("message_id") or "").strip()
    group_id = str(payload.get("group_id") or "").strip()
    if not context_id or not group_id:
        raise ValueError("agrirouter context_id und group_id sind erforderlich.")
    raw_components = payload.get("components") or payload.get("loaded_components") or []
    components = []
    for item in raw_components:
        feed_id = str(item.get("feed_id") or item.get("ddi") or "").strip()
        name = str(item.get("name") or item.get("label") or feed_id).strip()
        target = _number(item.get("target_kg", item.get("soll_kg")))
        actual = _number(item.get("actual_kg", item.get("ist_kg")))
        if not feed_id or target is None or actual is None:
            raise ValueError("Jede Mischwagenkomponente braucht feed_id/DDI, target_kg und actual_kg.")
        components.append({"feed_id": feed_id, "name": name, "soll_kg": target, "ist_kg": actual})
    if not components:
        raise ValueError("agrirouter-Nachricht enthaelt keine Mischwagenkomponenten.")
    animal_count = int(_number(payload.get("animal_count"), default=0) or 0)
    if animal_count <= 0:
        raise ValueError("agrirouter animal_count muss groesser als 0 sein.")
    feeding_date = str(payload.get("feeding_date") or payload.get("recorded_at") or date.today().isoformat())[:10]
    return {"external_id": context_id, "source": "agrirouter", "source_version": "2.0-http-sse",
        "target_model": "FeedingControlIn", "target": {"group_id": group_id, "feeding_date": feeding_date,
        "ration_ref": payload.get("ration_ref") or f"agrirouter:{context_id}", "komponenten": components,
        "restfutter_kg": _number(payload.get("rest_feed_kg"), default=0.0), "tierzahl": animal_count,
        "tm_pct": _number(payload.get("dry_matter_pct"), default=40.0), "milch_kg_kuh": _number(payload.get("milk_kg_cow")),
        "milchpreis_eur_kg": _number(payload.get("milk_price_eur_kg")), "futterkosten_eur_kuh": _number(payload.get("feed_cost_eur_cow")),
        "futtertisch_temp_c": _number(payload.get("feed_temp_c")), "umgebung_temp_c": _number(payload.get("ambient_temp_c"))}}

def icar_ade_to_cow_profile(payload: dict[str, Any]) -> dict[str, Any]:
    """Map ICAR ADE JSON milk-recording/group statistics to the existing CowProfile."""
    version = str(payload.get("ade_version") or payload.get("version") or "1.5.0")
    external_id = str(payload.get("event_id") or payload.get("id") or payload.get("recording_id") or "").strip()
    if not external_id: raise ValueError("ICAR-ADE event_id/recording_id ist erforderlich.")
    data = payload.get("milk_recording") or payload.get("milkRecordingStatistics") or payload.get("data") or payload
    milk = _number(data.get("milk_kg_day", data.get("milkYield")))
    if milk is None: raise ValueError("ICAR-ADE Milchmenge fehlt.")
    profile = {"breed": str(data.get("breed") or "dairy"), "body_weight_kg": _number(data.get("body_weight_kg", data.get("liveWeight")), default=650.0),
        "milk_kg_day": milk, "milk_fat_pct": _number(data.get("milk_fat_pct", data.get("fatPercent")), default=4.0),
        "milk_protein_pct": _number(data.get("milk_protein_pct", data.get("proteinPercent")), default=3.4),
        "milk_lactose_pct": _number(data.get("milk_lactose_pct", data.get("lactosePercent")), default=4.8),
        "lactation_stage_days": int(_number(data.get("lactation_stage_days", data.get("daysInMilk")), default=120) or 120),
        "parity": int(_number(data.get("parity"), default=2) or 2)}
    return {"external_id": external_id, "source": "icar_ade", "source_version": version, "target_model": "CowProfile", "target": profile,
        "control_context": {"milk_urea_mg_dl": _number(data.get("milk_urea_mg_dl", data.get("ureaMgDl"))), "recorded_at": data.get("recorded_at") or data.get("recordedAt")}}

def laboratory_to_feed_ingredient(payload: dict[str, Any]) -> dict[str, Any]:
    """Map LKS/LUFA/Eurofins-style normalized JSON to existing FeedIngredient fields."""
    sample_id = str(payload.get("sample_id") or payload.get("sampleId") or payload.get("id") or "").strip()
    name = str(payload.get("feed_name") or payload.get("feedName") or payload.get("material") or "").strip()
    if not sample_id or not name: raise ValueError("Labor sample_id und feed_name sind erforderlich.")
    dm_pct = _number(payload.get("dry_matter_pct", payload.get("dryMatterPercent")))
    if dm_pct is None or not 0 < dm_pct <= 100: raise ValueError("Labor-TM muss in Prozent zwischen 0 und 100 vorliegen.")
    def n(*keys: str, default: float = 0.0) -> float:
        for key in keys:
            value = _number(payload.get(key))
            if value is not None: return value
        return default
    target = {"id": f"lab_{sample_id}", "name": name, "group": str(payload.get("group") or "Betriebseigenes Laborfutter"),
        "dm_frac": dm_pct / 100.0, "price_eur_kgdm": n("price_eur_kgdm"), "me_mj_kgdm": n("me_mj_kgdm", "metabolizableEnergyMjKgDm"),
        "sidp_g_kgdm": n("sidp_g_kgdm", "sidProteinGKgDm"), "andfom_g_kgdm": n("andfom_g_kgdm", "ndfGKgDm"),
        "starch_g_kgdm": n("starch_g_kgdm", "starchGKgDm"), "sugar_g_kgdm": n("sugar_g_kgdm", "sugarGKgDm"),
        "fat_g_kgdm": n("fat_g_kgdm", "crudeFatGKgDm"), "ca_g_kgdm": n("ca_g_kgdm", "calciumGKgDm"),
        "p_g_kgdm": n("p_g_kgdm", "phosphorusGKgDm"), "na_g_kgdm": n("na_g_kgdm", "sodiumGKgDm"), "min_kgdm": 0.0, "max_kgdm": n("max_kgdm", default=20.0), "active": True}
    return {"external_id": sample_id, "source": str(payload.get("laboratory") or "laboratory"), "source_version": str(payload.get("format_version") or "normalized-json-v1"), "target_model": "FeedIngredient", "target": target,
        "analysis_context": {"sampled_at": payload.get("sampled_at") or payload.get("sampledAt"), "batch_id": payload.get("batch_id") or payload.get("batchId")}}