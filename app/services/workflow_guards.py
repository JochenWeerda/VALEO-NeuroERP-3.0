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