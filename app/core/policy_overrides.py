"""
Policy-Overrides pro Tenant (Gap 014).
Tenant-spezifische Ausnahmen zu Policy-Regeln – regelbasiert dokumentiert.
Konfiguration aus domain_shared.tenants.settings.policy_overrides.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


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


def get_policy_override(
    db: Session,
    tenant_id: str,
    rule_id: str,
) -> Optional[dict[str, Any]]:
    """
    Policy-Override für eine Regel abrufen (Gap 014).

    Args:
        db: SQLAlchemy Session
        tenant_id: Mandanten-ID
        rule_id: Policy-Regel-ID

    Returns:
        Override-Dict mit keys: enabled?, reason, valid_until?, params_override?
        oder None wenn kein Override existiert
    """
    settings = _load_tenant_settings(db, tenant_id)
    overrides = settings.get("policy_overrides")
    if not isinstance(overrides, dict):
        return None
    override = overrides.get(rule_id)
    if not isinstance(override, dict):
        return None
    # Prüfen ob noch gültig (valid_until)
    valid_until = override.get("valid_until")
    if valid_until:
        try:
            if isinstance(valid_until, str):
                limit = date.fromisoformat(valid_until[:10])
            else:
                limit = valid_until
            if date.today() > limit:
                return None  # Abgelaufen
        except (ValueError, TypeError):
            pass
    return dict(override)


def is_rule_disabled_for_tenant(db: Session, tenant_id: str, rule_id: str) -> bool:
    """
    Prüft ob eine Policy-Regel für den Tenant deaktiviert ist (Gap 014).
    """
    override = get_policy_override(db, tenant_id, rule_id)
    if not override:
        return False
    return override.get("enabled") is False


def get_effective_params(
    db: Session,
    tenant_id: str,
    rule_id: str,
    base_params: dict[str, Any],
) -> dict[str, Any]:
    """
    Effektive Parameter für eine Regel (Base + Tenant-Override) (Gap 014).
    """
    override = get_policy_override(db, tenant_id, rule_id)
    if not override:
        return dict(base_params)
    params_override = override.get("params_override")
    if not isinstance(params_override, dict):
        return dict(base_params)
    return {**base_params, **params_override}
