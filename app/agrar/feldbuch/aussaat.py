"""Aussaat-Register (ASK-SEED-001)."""
from __future__ import annotations

from typing import Any


def validate_aussaat(data: dict[str, Any]) -> dict[str, Any]:
    sorte = (data.get("sorte") or "").strip()
    if not sorte:
        raise ValueError("sorte ist Pflicht")
    menge = data.get("menge")
    if menge is None or float(menge) <= 0:
        raise ValueError("menge muss positiv sein")
    return {
        "typ": "aussaat",
        "sorte": sorte,
        "menge": float(menge),
        "einheit": data.get("einheit") or "kg/ha",
        "flaeche": float(data["flaeche"]) if data.get("flaeche") is not None else None,
        "saatgut_charge": data.get("saatgut_charge"),
        "mittel": data.get("mittel") or sorte,
        "register_daten": {
            "sorte": sorte,
            "saatgut_charge": data.get("saatgut_charge"),
            "vorkeimung": data.get("vorkeimung"),
        },
    }
