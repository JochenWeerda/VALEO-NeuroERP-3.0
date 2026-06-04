"""CRM-Kundenkarte — alle Kunden (public.kunden) als GeoJSON-POIs.

Koordinaten kommen ausschließlich aus ``public.kunden_geo`` (autoritativ, einmal
geokodiert: adressgenau aus gap_map_points bzw. Orts-/PLZ-Zentrum via Nominatim).
KEIN Zufalls-Jitter mehr; mehrere Kunden am selben Ortszentrum werden minimal
(deterministischer Mini-Spiral, ~ wenige Dutzend Meter) entzerrt, ohne den Ort zu
verfälschen. Typ aus kunden_nr-Präfix (GAP/MV/L…/Stamm). Reine Leseschicht.
"""

from __future__ import annotations

import math
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def _kunden_typ(kn: str) -> str:
    if kn.startswith("GAP"):
        return "gap"
    if kn.startswith("MV"):
        return "milchvieh"
    if kn.startswith("L") and not kn.startswith("LEAD"):
        return "lead"
    return "stamm"


def deoverlap(features: list[dict]) -> None:
    """Entzerrt Features mit identischer Koordinate in-place per Mini-Spiral
    (~30 m Schrittweite), damit Punkte am selben Ortszentrum sichtbar bleiben.
    Adressgenaue Punkte (precision='address') werden NICHT verschoben."""
    groups: dict[tuple, list[dict]] = {}
    for f in features:
        if f["properties"].get("precision") == "address":
            continue
        lon, lat = f["geometry"]["coordinates"]
        groups.setdefault((round(lat, 5), round(lon, 5)), []).append(f)
    for (lat, lon), grp in groups.items():
        if len(grp) < 2:
            continue
        for i, f in enumerate(grp):
            # Spiral: Radius wächst, Winkel nach goldenem Winkel (gleichmäßige Verteilung)
            r = 0.0004 * math.sqrt(i)          # ~44 m * sqrt(i)
            ang = i * 2.399963                 # goldener Winkel (rad)
            dlat = r * math.cos(ang)
            dlon = r * math.sin(ang) / max(0.1, math.cos(math.radians(lat)))
            f["geometry"]["coordinates"] = [round(lon + dlon, 6), round(lat + dlat, 6)]


class CrmKundenMapService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def map_features(self, typ: Optional[str] = None) -> dict:
        rows = self.db.execute(
            text(
                """
                SELECT k.kunden_nr, k.name1, k.plz, k.ort, k.business_partner_id,
                       g.lat, g.lon, g.precision
                FROM public.kunden k
                JOIN public.kunden_geo g ON g.kunden_nr = k.kunden_nr
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                  AND g.lat IS NOT NULL AND g.lon IS NOT NULL AND g.precision <> 'none'
                """
            )
        ).mappings().all()
        feats = []
        for r in rows:
            kn = r["kunden_nr"]
            t = _kunden_typ(kn)
            if typ and t != typ:
                continue
            feats.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(float(r["lon"]), 6), round(float(r["lat"]), 6)]},
                "properties": {
                    "kunden_nr": kn, "name": r["name1"], "plz": r["plz"], "ort": r["ort"],
                    "typ": t, "verbrueckt": r["business_partner_id"] is not None,
                    "precision": r["precision"],
                },
            })
        deoverlap(feats)
        return {"type": "FeatureCollection", "features": feats}
