"""
Prozesskonfiguration pro Tenant (Gap 009, 013).
Hilfsfunktionen für Prozessschritte, SLA/Timeout und Eskalation.
Konfiguration aus domain_shared.tenants.settings.process_variants.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Default-Prozessschritte + SLA/Eskalation (Gap 009, 013)
DEFAULT_PROCESS_VARIANTS: dict[str, dict[str, Any]] = {
    "annahme": {
        "steps": ["lkw-registrierung", "warteschlange", "qualitaets-check", "abrechnung"],
        "required_roles": {
            "warteschlange": ["annahme"],
            "qualitaets-check": ["annahme", "qs"],
            "abrechnung": ["annahme", "fibu"],
        },
        "step_sla": {
            "warteschlange": {"timeout_hours": 4, "escalation_roles": ["annahme_leiter"]},
            "qualitaets-check": {"timeout_hours": 2, "escalation_roles": ["qs_leiter"]},
            "abrechnung": {"timeout_hours": 24, "escalation_roles": ["fibu_leiter"]},
        },
        "description": "Ernteannahme: LKW-Registrierung → Warteschlange → Qualitätsprüfung → Abrechnung",
    },
    "settlement": {
        "steps": ["erfassung", "trocknung", "abzuege", "freigabe", "buchung"],
        "required_roles": {"freigabe": ["fibu", "leitung"], "buchung": ["fibu"]},
        "step_sla": {
            "freigabe": {"timeout_hours": 48, "escalation_roles": ["leitung", "fibu"]},
            "buchung": {"timeout_hours": 24, "escalation_roles": ["fibu_leiter"]},
        },
        "description": "Settlement: Erfassung → Trocknung/Abzüge → Freigabe → Buchung",
    },
}

# Erntefenster-Vorlagen (Gap 005: Saisonale Kampagnenprozesse)
# Typische Erntefenster mit Start/Ende (MM-DD), Prozess-Bindung und Produktgruppen
DEFAULT_ERNTEFENSTER_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "raps",
        "name": "Raps-Ernte",
        "description": "Rapsannahme mit Qualitätsprüfung und Settlement",
        "process_key": "annahme",
        "default_start_mmdd": "06-15",
        "default_end_mmdd": "07-31",
        "product_groups": ["raps", "oelsaaten"],
    },
    {
        "id": "weizen",
        "name": "Weizen-Ernte",
        "description": "Weizenannahme mit Trocknungsregeln",
        "process_key": "annahme",
        "default_start_mmdd": "07-01",
        "default_end_mmdd": "08-31",
        "product_groups": ["weizen", "getreide"],
    },
    {
        "id": "gerste",
        "name": "Gersten-Ernte",
        "description": "Gerstenannahme (Brau- und Futtergerste)",
        "process_key": "annahme",
        "default_start_mmdd": "06-20",
        "default_end_mmdd": "08-15",
        "product_groups": ["gerste", "getreide"],
    },
    {
        "id": "mais",
        "name": "Mais-Ernte",
        "description": "Maisannahme mit Feuchteprüfung",
        "process_key": "annahme",
        "default_start_mmdd": "09-15",
        "default_end_mmdd": "11-30",
        "product_groups": ["mais", "futter"],
    },
    {
        "id": "zuckerruebe",
        "name": "Zuckerrüben-Kampagne",
        "description": "Zuckerrübenannahme mit Kampagnenlogistik",
        "process_key": "annahme",
        "default_start_mmdd": "09-15",
        "default_end_mmdd": "01-15",
        "product_groups": ["zuckerrueben"],
    },
]


def _load_tenant_settings(db: Session, tenant_id: str) -> dict[str, Any]:
    """Tenant-Settings aus DB laden."""
    row = db.execute(
        text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id},
    ).first()
    if not row or not row[0]:
        return {}
    raw = row[0]
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def get_process_variant(
    db: Session,
    tenant_id: str,
    process_key: str,
    *,
    default: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Prozessvarianten-Konfiguration für einen Prozess abrufen (Gap 009).

    Args:
        db: SQLAlchemy Session
        tenant_id: Mandanten-ID
        process_key: Prozess-Code (z.B. 'annahme', 'settlement')
        default: Optionaler Fallback, wenn weder Tenant noch DEFAULT_PROCESS_VARIANTS

    Returns:
        Dict mit keys: steps, required_roles?, description?, etc.
    """
    settings = _load_tenant_settings(db, tenant_id)
    custom = settings.get("process_variants")
    base = DEFAULT_PROCESS_VARIANTS.get(process_key) or default or {}
    if isinstance(custom, dict) and process_key in custom:
        tenant_cfg = custom[process_key]
        if isinstance(tenant_cfg, dict):
            return {**base, **tenant_cfg}
    return dict(base)


def get_process_steps(db: Session, tenant_id: str, process_key: str) -> list[str]:
    """
    Prozessschritte für einen Prozess abrufen (Gap 009).
    Kurzform von get_process_variant(...)["steps"].
    """
    cfg = get_process_variant(db, tenant_id, process_key)
    steps = cfg.get("steps")
    if isinstance(steps, list):
        return [str(s) for s in steps]
    return []


def get_step_sla(
    db: Session,
    tenant_id: str,
    process_key: str,
    step_key: str,
) -> dict[str, Any] | None:
    """
    SLA/Eskalations-Konfiguration für einen Prozessschritt (Gap 013).

    Returns:
        {"timeout_hours": int, "escalation_roles": list[str]} oder None
    """
    cfg = get_process_variant(db, tenant_id, process_key)
    step_sla = cfg.get("step_sla")
    if isinstance(step_sla, dict) and step_key in step_sla:
        s = step_sla[step_key]
        if isinstance(s, dict):
            return s
    return None


def is_step_overdue(step_started_at: datetime, timeout_hours: int) -> bool:
    """
    Prüft, ob ein Prozessschritt die SLA überschritten hat (Gap 013).
    """
    if timeout_hours <= 0:
        return False
    now = datetime.now(timezone.utc)
    started = step_started_at.astimezone(timezone.utc) if step_started_at.tzinfo else step_started_at.replace(tzinfo=timezone.utc)
    delta_hours = (now - started).total_seconds() / 3600
    return delta_hours > timeout_hours
