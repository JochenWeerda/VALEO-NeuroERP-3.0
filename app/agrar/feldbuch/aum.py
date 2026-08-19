"""Agrarumweltmaßnahmen (ASK-ENV-001)."""
from __future__ import annotations

from typing import Any


def validate_aum(data: dict[str, Any]) -> dict[str, Any]:
    code = (data.get("aum_code") or "").strip()
    if not code:
        raise ValueError("aum_code ist Pflicht")
    flaeche = data.get("flaeche")
    if flaeche is None or float(flaeche) <= 0:
        raise ValueError("flaeche muss positiv sein")
    bez = data.get("bezeichnung") or code
    return {
        "typ": "aum",
        "aum_code": code,
        "bezeichnung": bez,
        "flaeche": float(flaeche),
        "mittel": code,
        "register_daten": {
            "aum_code": code,
            "bezeichnung": bez,
            "verpflichtungsjahr": data.get("verpflichtungsjahr"),
        },
    }
