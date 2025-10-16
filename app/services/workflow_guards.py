"""
Workflow Guards
Policy-basierte Guards für Workflow-Transitions
"""

from __future__ import annotations
from typing import Tuple


def guard_total_positive(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob Gesamtbetrag > 0

    Args:
        payload: Beleg-Daten

    Returns:
        (ok, reason)
    """
    total = payload.get("total")
    if total is None:
        total = sum((l.get("qty", 0) * l.get("price", 0)) for l in payload.get("lines", []))
    return (total > 0, "Total must be > 0")


def guard_price_not_below_cost(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob Preise nicht unter EK liegen

    Args:
        payload: Beleg-Daten

    Returns:
        (ok, reason)
    """
    for l in payload.get("lines", []):
        if isinstance(l.get("price"), (int, float)) and isinstance(l.get("cost"), (int, float)):
            if l["price"] < l["cost"]:
                return (False, f"Price below cost for article {l.get('article')}")
    return (True, "ok")


def guard_has_approval_role(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob User Approval-Rolle hat

    Args:
        payload: Beleg-Daten mit user_info

    Returns:
        (ok, reason)
    """
    user = payload.get("user_info", {})
    roles = user.get("roles", [])
    return ("controller" in roles or "admin" in roles, "Insufficient permissions for approval")


def guard_has_submit_role(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob User Submit-Rolle hat

    Args:
        payload: Beleg-Daten mit user_info

    Returns:
        (ok, reason)
    """
    user = payload.get("user_info", {})
    roles = user.get("roles", [])
    return ("sales" in roles or "purchase" in roles or "admin" in roles, "Insufficient permissions for submit")


def guard_psm_farmer_declaration_required(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob PSM eine Erklärung des Landwirts erfordert

    Args:
        payload: PSM-Daten

    Returns:
        (ok, reason)
    """
    psm = payload.get("psm", {})
    if psm.get("ausgangsstoff_explosivstoffe") and not psm.get("erklaerung_landwirt_status"):
        return (False, "Farmer declaration required for PSM with explosive precursors")
    return (True, "ok")


def guard_psm_approval_valid(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob PSM-Zulassung noch gültig ist

    Args:
        payload: PSM-Daten

    Returns:
        (ok, reason)
    """
    from datetime import datetime
    psm = payload.get("psm", {})
    ablauf = psm.get("zulassung_ablauf")
    if ablauf and isinstance(ablauf, str):
        ablauf_date = datetime.fromisoformat(ablauf.replace('Z', '+00:00'))
        if ablauf_date < datetime.now():
            return (False, "PSM approval has expired")
    return (True, "ok")


def guard_psm_expertise_required(payload: dict) -> tuple[bool, str]:
    """
    Prüft ob Sachkunde-Nachweis für PSM-Abgabe erforderlich ist

    Args:
        payload: Verkaufsdaten mit PSM-Artikeln

    Returns:
        (ok, reason)
    """
    user = payload.get("user_info", {})
    has_expertise = user.get("psm_sachkunde_gueltig", False)

    # Prüfe ob PSM im Warenkorb sind
    lines = payload.get("lines", [])
    has_psm = any(line.get("article_type") == "PSM" for line in lines)

    if has_psm and not has_expertise:
        return (False, "Valid PSM expertise certificate required for PSM sales")

    return (True, "ok")