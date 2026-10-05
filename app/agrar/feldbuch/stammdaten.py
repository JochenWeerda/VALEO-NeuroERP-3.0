"""Betriebsmittel-/Kultur-Stammdaten für Portal-Auswahl (ASK-MST-001)."""
from __future__ import annotations

from typing import Any, Optional

from app.agrar.feldbuch.naehrstoff import NaehrstoffGehalt, reinnaehrstoffe_kg


def list_kulturen(
    schlaege: list[dict[str, Any]],
    extra: Optional[list[str]] = None,
) -> list[str]:
    names = {str(s.get("kultur")).strip() for s in schlaege if s.get("kultur")}
    if extra:
        names |= {str(x).strip() for x in extra if x}
    return sorted(n for n in names if n)


def _find(items: list[dict[str, Any]], mittel_id: str) -> dict[str, Any]:
    for item in items:
        if str(item.get("id")) == str(mittel_id):
            return item
    raise ValueError(f"Mittel nicht gefunden: {mittel_id}")


def resolve_mittel(
    catalog: dict[str, list[dict[str, Any]]],
    *,
    mittel_typ: str,
    mittel_id: str,
    menge: float,
    flaeche: float,
) -> dict[str, Any]:
    """Löst Stammdaten auf und leitet Nährstoffe/Kosten/Wartezeit ab."""
    key = {
        "duenger": "duenger",
        "psm": "psm",
        "saatgut": "saatgut",
    }.get(mittel_typ)
    if not key:
        raise ValueError(f"unbekannter mittel_typ: {mittel_typ}")
    item = _find(catalog.get(key) or [], mittel_id)
    out: dict[str, Any] = {
        "mittel_id": mittel_id,
        "mittel_typ": mittel_typ,
        "mittel": item.get("name"),
    }
    preis = item.get("vk_preis")
    if preis is not None and menge > 0 and flaeche > 0:
        out["kosten_eur"] = round(float(preis) * float(menge) * float(flaeche), 2)

    if mittel_typ == "duenger":
        typ = str(item.get("typ") or "").lower()
        organisch = "organ" in typ
        out["duenger_form"] = "O" if organisch else "M"
        out["n_gehalt"] = float(item.get("n_gehalt") or 0.0)
        out["p2o5_gehalt"] = float(item.get("p_gehalt") or item.get("p2o5_gehalt") or 0.0)
        out["k2o_gehalt"] = float(item.get("k_gehalt") or item.get("k2o_gehalt") or 0.0)
        out["mgo_gehalt"] = float(item.get("mg_gehalt") or item.get("mgo_gehalt") or 0.0)
        out["s_gehalt"] = float(item.get("s_gehalt") or 0.0)
        gehalt = NaehrstoffGehalt(
            n=out["n_gehalt"],
            p2o5=out["p2o5_gehalt"],
            k2o=out["k2o_gehalt"],
            mgo=out["mgo_gehalt"],
            s=out["s_gehalt"],
            organisch=organisch,
        )
        if menge > 0 and flaeche > 0:
            rn = reinnaehrstoffe_kg(float(menge), float(flaeche), gehalt)
            out["n_kg"] = rn["n"]
            out["p2o5_kg"] = rn["p2o5"]
            out["k2o_kg"] = rn["k2o"]
            out["mgo_kg"] = rn["mgo"]
            out["s_kg"] = rn["s"]
    elif mittel_typ == "psm":
        out["wirkungsbereich"] = item.get("mittel_typ") or item.get("wirkungsbereich")
        if item.get("wartezeit") is not None:
            out["wartezeit_tage"] = int(item["wartezeit"])
    elif mittel_typ == "saatgut":
        out["sorte"] = item.get("sorte") or item.get("name")
    return out
