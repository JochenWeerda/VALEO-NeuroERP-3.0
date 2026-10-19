"""Preiskalkulation der Maske ``preise/kalkulation`` (aus ``mask_frontend_bridges`` herausgeloest, 19.10.2026).

Eigenes Modul, damit das Godfile ``mask_frontend_bridges.py`` schrumpft statt mit der Bereichsrolle zu wachsen.
Pfad und Antwort sind unveraendert.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from app.api.v1.endpoints.mask_frontend_bridges import BridgeOut
from app.auth.bereich_roles import SCHREIBEN

router = APIRouter(tags=["mask-frontend-bridges"])


class PreisBerechnenIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    artikel_id: str | None = None
    menge_kg: float | None = None
    kundengruppe: str | None = None
    sorte_klasse: str | None = None
    kontrakt_id: str | None = None


@router.post("/preise/berechnen", response_model=BridgeOut, summary="Preis kalkulieren", dependencies=SCHREIBEN["VERKAUF"])
def preise_berechnen(body: PreisBerechnenIn) -> dict[str, Any]:
    menge = float(body.menge_kg or 1)
    basis = 100.0
    if body.kundengruppe and body.kundengruppe.upper() == "GROSSHANDEL":
        rabatt = 8.0
    else:
        rabatt = 0.0
    netto = round(basis * menge * (1 - rabatt / 100.0), 2)
    mwst = round(netto * 0.19, 2)
    return {
        "netto_preis": netto,
        "brutto_preis": round(netto + mwst, 2),
        "mwst_betrag": mwst,
        "kalkulationsweg": [
            {"schritt": "Basispreis", "wert": round(basis * menge, 2), "delta": 0},
            {"schritt": f"Kundengruppe {body.kundengruppe or '-'}", "wert": netto, "delta": -round(basis * menge * rabatt / 100.0, 2)},
            {"schritt": "MwSt 19%", "wert": round(netto + mwst, 2), "delta": mwst},
        ],
    }
