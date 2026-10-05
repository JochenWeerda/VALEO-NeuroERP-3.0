"""Provider-neutral normalization for dairy herd-data API payloads.

DDW/Optiherd is the first profile. The public product pages describe data marts
and KPI access, but do not publish a stable wire contract. Therefore all live
paths remain configurable and these mappers define VALEO's inbound contract.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

HerdDataKind = Literal["group_kpi", "health_alert", "genetic_profile"]


class HerdDataObservation(BaseModel):
    provider: str = Field(default="ddw", min_length=1, max_length=32)
    herd_id: str = Field(min_length=1, max_length=160)
    kind: HerdDataKind
    entity_id: str = Field(min_length=1, max_length=200)
    effective_at: datetime
    provider_updated_at: datetime
    group_id: str | None = Field(default=None, max_length=160)
    previous_group_id: str | None = Field(default=None, max_length=160)
    deleted: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


def _timestamp(value: Any, *, fallback: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min, tzinfo=timezone.utc)
    else:
        raw = str(value or "").strip()
        if not raw:
            return fallback or datetime.now(timezone.utc)
        try:
            if len(raw) == 10:
                parsed = datetime.combine(date.fromisoformat(raw), time.min, tzinfo=timezone.utc)
            else:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Ungueltiger Herd-Data-Zeitstempel: {raw}") from exc
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _required(payload: dict[str, Any], name: str) -> str:
    value = str(payload.get(name) or "").strip()
    if not value:
        raise ValueError(f"Herd-Data-Feld fehlt: {name}")
    return value


def normalize_group_kpis(payload: dict[str, Any], *, provider: str = "ddw") -> list[HerdDataObservation]:
    herd_id = _required(payload, "herd_id")
    effective = _timestamp(payload.get("currency_date") or payload.get("date"))
    updated = _timestamp(payload.get("sync_timestamp"), fallback=effective)
    observations: list[HerdDataObservation] = []
    for item in payload.get("group_metrics") or []:
        if not isinstance(item, dict):
            continue
        group_id = _required(item, "group_id")
        kpis = item.get("kpis") if isinstance(item.get("kpis"), dict) else {}
        observations.append(HerdDataObservation(
            provider=provider,
            herd_id=herd_id,
            kind="group_kpi",
            entity_id=f"{group_id}:{effective.date().isoformat()}",
            effective_at=effective,
            provider_updated_at=updated,
            group_id=group_id,
            payload={
                "group_name": item.get("group_name"),
                "cow_count": item.get("cow_count"),
                "kpis": kpis,
            },
        ))
    return observations


def normalize_health_alerts(payload: dict[str, Any], *, provider: str = "ddw") -> list[HerdDataObservation]:
    herd_id = _required(payload, "herd_id")
    bundle_updated = _timestamp(payload.get("sync_timestamp") or payload.get("updated_at"))
    observations: list[HerdDataObservation] = []
    for item in payload.get("alerts") or []:
        if not isinstance(item, dict):
            continue
        animal_id = _required(item, "animal_id")
        updated = _timestamp(item.get("updated_at"), fallback=bundle_updated)
        alert_id = str(item.get("alert_id") or f"{animal_id}:{updated.isoformat()}")
        status = str(item.get("status") or item.get("event_type") or "").lower()
        observations.append(HerdDataObservation(
            provider=provider,
            herd_id=herd_id,
            kind="health_alert",
            entity_id=alert_id,
            effective_at=_timestamp(item.get("detected_at"), fallback=updated),
            provider_updated_at=updated,
            group_id=str(item.get("group_id") or "").strip() or None,
            previous_group_id=str(item.get("previous_group_id") or "").strip() or None,
            deleted=bool(item.get("deleted")) or status in {"deleted", "culled", "sold", "removed"},
            payload=item,
        ))
    return observations


def normalize_genetic_profiles(payload: dict[str, Any], *, provider: str = "ddw") -> list[HerdDataObservation]:
    herd_id = _required(payload, "herd_id")
    bundle_updated = _timestamp(payload.get("sync_timestamp") or payload.get("updated_at"))
    observations: list[HerdDataObservation] = []
    for item in payload.get("animals") or []:
        if not isinstance(item, dict):
            continue
        animal_id = _required(item, "animal_id")
        updated = _timestamp(item.get("updated_at"), fallback=bundle_updated)
        status = str(item.get("status") or item.get("event_type") or "").lower()
        observations.append(HerdDataObservation(
            provider=provider,
            herd_id=herd_id,
            kind="genetic_profile",
            entity_id=animal_id,
            effective_at=_timestamp(item.get("effective_at") or item.get("birth_date"), fallback=updated),
            provider_updated_at=updated,
            group_id=str(item.get("group_id") or "").strip() or None,
            previous_group_id=str(item.get("previous_group_id") or "").strip() or None,
            deleted=bool(item.get("deleted")) or status in {"deleted", "culled", "sold", "removed"},
            payload=item,
        ))
    return observations


NORMALIZERS = {
    "group_kpi": normalize_group_kpis,
    "health_alert": normalize_health_alerts,
    "genetic_profile": normalize_genetic_profiles,
}


def normalize_herd_data_bundle(kind: HerdDataKind, payload: dict[str, Any], *, provider: str = "ddw") -> list[HerdDataObservation]:
    return NORMALIZERS[kind](payload, provider=provider)
