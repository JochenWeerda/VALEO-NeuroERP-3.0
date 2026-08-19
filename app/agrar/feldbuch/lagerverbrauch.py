"""Lagerverbrauch je Maßnahme (ASK-COST-001)."""
from __future__ import annotations

from typing import Any, Optional


def plane_lagerverbrauch(
    *,
    massnahme_id: str,
    artikel_id: str,
    charge: Optional[str],
    menge: float,
    einheit: str,
    kostentraeger_schlag_id: Optional[str],
    client_ref: Optional[str] = None,
) -> dict[str, Any]:
    if float(menge) <= 0:
        raise ValueError("menge muss positiv sein")
    if not artikel_id:
        raise ValueError("artikel_id ist Pflicht")
    if not massnahme_id:
        raise ValueError("massnahme_id ist Pflicht")
    return {
        "massnahme_id": massnahme_id,
        "artikel_id": artikel_id,
        "charge": charge,
        "menge": float(menge),
        "einheit": einheit or "kg",
        "richtung": "verbrauch",
        "kostentraeger_schlag_id": kostentraeger_schlag_id,
        "client_ref": client_ref,
    }
