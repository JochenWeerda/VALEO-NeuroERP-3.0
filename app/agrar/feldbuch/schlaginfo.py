"""Schlaginformation / Gesamtdokumentation (Lastenheft Kap. 19)."""
from __future__ import annotations

from typing import Any, Optional


_TYP_SECTION = {
    "aussaat": "aussaat",
    "duengung": "duengung",
    "psm": "pflanzenschutz",
    "bodenbearbeitung": "bodenbearbeitung",
    "beregnung": "beregnung",
    "ernte": "ernte",
    "aum": "aum",
    "sonstiges": "sonstiges",
}


def build_schlaginfo(
    schlag: dict[str, Any],
    massnahmen: list[dict[str, Any]],
    *,
    wirtschaftsjahr: Optional[int] = None,
) -> dict[str, Any]:
    """Aggregiert Register + Direktkostenfreie Leistung für einen Schlag."""
    sections: dict[str, list[dict[str, Any]]] = {
        "aussaat": [],
        "duengung": [],
        "pflanzenschutz": [],
        "bodenbearbeitung": [],
        "beregnung": [],
        "ernte": [],
        "aum": [],
        "sonstiges": [],
    }
    direktkosten = 0.0
    erloes = 0.0
    nebenleistung = 0.0

    for m in massnahmen:
        typ = str(m.get("typ") or "sonstiges")
        key = _TYP_SECTION.get(typ, "sonstiges")
        sections[key].append(m)
        direktkosten += float(m.get("kosten_eur") or 0.0)
        erloes += float(m.get("erloes_eur") or 0.0)
        nebenleistung += float(m.get("nebenleistung_eur") or 0.0)

    ha = float(schlag.get("flaeche") or 0.0)
    dfl = erloes + nebenleistung - direktkosten
    return {
        "schlag": {
            "id": schlag.get("id"),
            "name": schlag.get("name"),
            "flik": schlag.get("flik"),
            "flaecheHa": ha,
            "kultur": schlag.get("kultur"),
            "vorkultur": schlag.get("vorkultur"),
            "nSollwertKgHa": schlag.get("n_sollwert_kg_ha"),
            "nminFruehjahrKgHa": schlag.get("nmin_fruehjahr_kg_ha"),
            "versorgungsstufe": schlag.get("versorgungsstufe"),
        },
        "wirtschaftsjahr": wirtschaftsjahr,
        "aussaat": sections["aussaat"],
        "duengung": sections["duengung"],
        "pflanzenschutz": sections["pflanzenschutz"],
        "bodenbearbeitung": sections["bodenbearbeitung"],
        "beregnung": sections["beregnung"],
        "ernte": sections["ernte"],
        "aum": sections["aum"],
        "sonstiges": sections["sonstiges"],
        "kosten": {
            "direktkostenEur": round(direktkosten, 2),
            "erloesEur": round(erloes + nebenleistung, 2),
            "nebenleistungEur": round(nebenleistung, 2),
            "direktkostenfreieLeistungEur": round(dfl, 2),
            "direktkostenfreieLeistungEurHa": round(dfl / ha, 2) if ha > 0 else None,
        },
    }
