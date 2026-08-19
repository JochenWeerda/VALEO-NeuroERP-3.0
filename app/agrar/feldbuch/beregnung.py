"""Beregnungs-Register (ASK-IRR-001)."""
from __future__ import annotations

from typing import Any


def validate_beregnung(data: dict[str, Any]) -> dict[str, Any]:
    mm = data.get("wassermenge_mm", data.get("menge"))
    if mm is None or float(mm) <= 0:
        raise ValueError("wassermenge muss positiv sein")
    return {
        "typ": "beregnung",
        "menge": float(mm),
        "einheit": "mm",
        "flaeche": float(data["flaeche"]) if data.get("flaeche") is not None else None,
        "bezeichnung": data.get("art") or data.get("bezeichnung") or "Beregnung",
        "register_daten": {
            "art": data.get("art") or "Beregnung",
            "wassermenge_mm": float(mm),
            "stadium": data.get("stadium"),
        },
    }
