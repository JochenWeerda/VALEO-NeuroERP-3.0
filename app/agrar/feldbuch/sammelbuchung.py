"""Sammelbuchung über mehrere Schläge (Lastenheft Kap. 31)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from app.agrar.feldbuch.naehrstoff import NaehrstoffGehalt, reinnaehrstoffe_kg


def plane_sammel_duengung(
    *,
    schlaege: list[dict[str, Any]],
    datum: datetime,
    mittel: str,
    menge_kg_ha: float,
    einheit: str = "kg/ha",
    n_gehalt: float = 0.0,
    p2o5_gehalt: float = 0.0,
    k2o_gehalt: float = 0.0,
    mgo_gehalt: float = 0.0,
    s_gehalt: float = 0.0,
    duenger_form: str = "M",
    preis_je_einheit: Optional[float] = None,
    anwender: Optional[str] = None,
    begruendung: Optional[str] = None,
) -> dict[str, Any]:
    """Verteilt eine Düngung proportional je Schlagfläche (gleiche Aufwandmenge/ha)."""
    if not schlaege:
        raise ValueError("schlaege sind Pflicht")
    if float(menge_kg_ha) <= 0:
        raise ValueError("menge muss positiv sein")

    gehalt = NaehrstoffGehalt(
        n=float(n_gehalt or 0.0),
        p2o5=float(p2o5_gehalt or 0.0),
        k2o=float(k2o_gehalt or 0.0),
        mgo=float(mgo_gehalt or 0.0),
        s=float(s_gehalt or 0.0),
        organisch=(duenger_form == "O"),
    )
    massnahmen: list[dict[str, Any]] = []
    gesamt_ha = 0.0
    for s in schlaege:
        sid = s.get("id")
        if not sid:
            raise ValueError("jeder Schlag braucht eine id")
        ha = float(s.get("flaeche") or 0.0)
        if ha <= 0:
            raise ValueError(f"Schlag {sid}: flaeche muss positiv sein")
        gesamt_ha += ha
        rn = reinnaehrstoffe_kg(float(menge_kg_ha), ha, gehalt)
        kosten = None
        if preis_je_einheit is not None:
            kosten = round(float(preis_je_einheit) * float(menge_kg_ha) * ha, 2)
        massnahmen.append(
            {
                "schlag_id": sid,
                "datum": datum,
                "typ": "duengung",
                "bezeichnung": f"Sammeldüngung {mittel}",
                "mittel": mittel,
                "menge": float(menge_kg_ha),
                "einheit": einheit,
                "flaeche": ha,
                "anwender": anwender,
                "bemerkung": begruendung,
                "duenger_form": duenger_form,
                "n_kg": rn["n"],
                "p2o5_kg": rn["p2o5"],
                "k2o_kg": rn["k2o"],
                "mgo_kg": rn["mgo"],
                "s_kg": rn["s"],
                "kosten_eur": kosten,
                "quelle": "portal",
            }
        )
    return {
        "anzahl": len(massnahmen),
        "gesamtFlaecheHa": round(gesamt_ha, 2),
        "massnahmen": massnahmen,
    }
