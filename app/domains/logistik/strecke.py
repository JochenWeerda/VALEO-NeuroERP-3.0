"""Fahrtposition und Strecke.

Webfleet ist die laufende Fahrzeugposition. Solange davon nichts vorliegt,
ist der Zielort die einzige Koordinate: die des Kunden in ``public.kunden_geo``.
Eine Strecke gibt es erst ab zwei Punkten. Ein einzelner Zielort ist kein Kilometerwert.
"""

from __future__ import annotations

import math
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

_LAT = 90.0
_LNG = 180.0


def _punkt(wert: tuple[float, float] | None) -> tuple[float, float] | None:
    if wert is None or len(wert) != 2:
        return None
    lat, lng = wert
    if isinstance(lat, bool) or isinstance(lng, bool):
        return None
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(lat_f) or not math.isfinite(lng_f):
        return None
    if abs(lat_f) > _LAT or abs(lng_f) > _LNG:
        return None
    return (lat_f, lng_f)


def webfleet_punkt(
    lat_mikro: float | None,
    lng_mikro: float | None,
    status: str | None,
) -> tuple[float, float] | None:
    """Nur GPS-Status A ist ein gültiger Fix. Webfleet liefert Mikrogramm (10**-6 Grad)."""
    if status != "A" or lat_mikro is None or lng_mikro is None:
        return None
    return _punkt((float(lat_mikro) / 1_000_000, float(lng_mikro) / 1_000_000))


def fahrtposition(
    webfleet: tuple[float, float] | None,
    zielort: tuple[float, float] | None,
) -> tuple[float, float] | None:
    """Gültige Webfleet-Position, sonst die Koordinate des Zielorts."""
    live = _punkt(webfleet)
    if live is not None:
        return live
    return _punkt(zielort)


def luftlinie_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    erde_km = 6371.0
    lat1, lng1 = a
    lat2, lng2 = b
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
    return erde_km * 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def strecke_km(punkte: list[tuple[float, float]]) -> float | None:
    """Summe der Luftlinie in Stoppreihenfolge. Ein Punkt ist keine Strecke."""
    gueltig = [p for p in (_punkt(x) for x in punkte) if p is not None]
    if len(gueltig) < 2:
        return None
    summe = 0.0
    for links, rechts in zip(gueltig, gueltig[1:]):
        summe += luftlinie_km(links, rechts)
    return round(summe, 1)


def streckenpunkte(
    webfleet: tuple[float, float] | None,
    zielorte: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Fahrzeugposition zuerst, danach die Zielorte. Ohne Webfleet bleiben nur die Zielorte."""
    live = _punkt(webfleet)
    ziele = [p for p in (_punkt(z) for z in zielorte) if p is not None]
    if live is not None:
        return [live, *ziele]
    return ziele


def touren_mit_stopps(touren: list[dict[str, Any]], stopps: list[Any]) -> None:
    """Stoppzahl und Luftlinie je Tour. Stopps ohne Koordinate zählen mit, sie strecken nicht."""
    zaehler: dict[str, int] = {}
    punkte: dict[str, list[tuple[float, float]]] = {}
    for stopp in stopps:
        tour_id = str(stopp["tour_id"])
        zaehler[tour_id] = zaehler.get(tour_id, 0) + 1
        lat, lng = stopp["lat"], stopp["lng"]
        if lat is None or lng is None:
            continue
        punkte.setdefault(tour_id, []).append((float(lat), float(lng)))
    for tour in touren:
        tour_id = str(tour.get("id"))
        tour["stop_count"] = zaehler.get(tour_id, 0)
        tour["distance_km"] = strecke_km(punkte.get(tour_id, []))


def stopp_mit_zielort(db: Session, tenant_id: str | None, stopp: dict[str, Any]) -> dict[str, Any]:
    """Fehlende Koordinate und Platzhalteradresse kommen vom Kunden, nicht vom Disponenten."""
    lage = zielort_des_kunden(db, tenant_id, stopp.get("customer_id"))
    return anreichern_stopp(
        stopp,
        ziel_lat=lage["lat"],
        ziel_lng=lage["lng"],
        ziel_adresse=lage["address"],
    )


def anreichern_stopp(
    stopp: dict[str, Any],
    *,
    ziel_lat: float | None,
    ziel_lng: float | None,
    ziel_adresse: str | None,
) -> dict[str, Any]:
    """Stopp ohne eigene Koordinate übernimmt den Zielort. Die Belegnummer bleibt die Referenz."""
    if stopp.get("lat") is None or stopp.get("lng") is None:
        ziel = (ziel_lat, ziel_lng) if ziel_lat is not None and ziel_lng is not None else None
        pos = fahrtposition(None, ziel)
        if pos is not None:
            stopp["lat"], stopp["lng"] = pos
    adresse = str(stopp.get("address") or "").strip()
    platzhalter = not adresse or adresse.lower().startswith("lieferschein")
    if platzhalter and (ziel_adresse or "").strip():
        stopp["address"] = ziel_adresse.strip()
    return stopp


def zielort_des_kunden(db: Session, tenant_id: str | None, customer_id: str | None) -> dict[str, Any]:
    """Adresse aus dem Kundenstamm, Koordinate aus ``public.kunden_geo``."""
    leer: dict[str, Any] = {"address": None, "lat": None, "lng": None}
    if not customer_id or not tenant_id:
        return leer
    try:
        with db.begin_nested():
            return _zielort_lesen(db, tenant_id, customer_id)
    except Exception:
        return leer


def _zielort_lesen(db: Session, tenant_id: str, customer_id: str) -> dict[str, Any]:
    row = db.execute(
        text(
            """
            SELECT customer_number, address, postal_code, city
            FROM domain_crm.customers
            WHERE tenant_id = :tid
              AND (id::text = :cid OR customer_number = :cid)
            LIMIT 1
            """
        ),
        {"tid": tenant_id, "cid": customer_id},
    ).mappings().first()
    if row is None:
        return {"address": None, "lat": None, "lng": None}
    teile = [str(row[k]).strip() for k in ("address", "postal_code", "city") if row[k]]
    geo = db.execute(
        text("SELECT lat, lon FROM public.kunden_geo WHERE kunden_nr = :nr LIMIT 1"),
        {"nr": row["customer_number"]},
    ).mappings().first()
    lat = float(geo["lat"]) if geo and geo["lat"] is not None else None
    lng = float(geo["lon"]) if geo and geo["lon"] is not None else None
    return {"address": ", ".join(teile) or None, "lat": lat, "lng": lng}
