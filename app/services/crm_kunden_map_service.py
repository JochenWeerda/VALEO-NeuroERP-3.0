"""CRM-Kundenkarte — alle Kunden (public.kunden) als GeoJSON-POIs.

Koordinaten: exakter Match (name_norm+PLZ) gegen ``gap_map_points``, sonst
PLZ-Zentroid + deterministischer Jitter (damit Kunden einer PLZ nicht
überlappen). Typ wird aus dem kunden_nr-Präfix abgeleitet
(GAP=Förderempfänger, MV=Milchvieh, L…=konvertierter Lead, sonst=Stammkunde).
Reine Lese-/Rechenschicht.
"""

from __future__ import annotations

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


class CrmKundenMapService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _resolver(self):
        exact: dict[tuple, tuple] = {}
        agg: dict[str, list] = {}
        try:
            rows = self.db.execute(
                text("SELECT name_norm, postal_code, lat, lon FROM gap_map_points WHERE lat IS NOT NULL AND lon IS NOT NULL")
            ).all()
        except Exception:  # noqa: BLE001 — Tabelle evtl. nicht vorhanden
            self.db.rollback()
            return {}, {}
        for nn, pc, lat, lon in rows:
            la, lo = float(lat), float(lon)
            if nn and pc:
                exact.setdefault((nn, pc), (la, lo))
            if pc:
                agg.setdefault(pc, []).append((la, lo))
        cent = {pc: (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) for pc, pts in agg.items()}
        return exact, cent

    def map_features(self, typ: Optional[str] = None) -> dict:
        import hashlib

        from app.services.gap_pipeline import normalize_name

        exact, cent = self._resolver()
        rows = self.db.execute(
            text(
                "SELECT kunden_nr, name1, plz, ort, business_partner_id, geloescht "
                "FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE"
            )
        ).mappings().all()
        feats = []
        for r in rows:
            kn = r["kunden_nr"]
            t = _kunden_typ(kn)
            if typ and t != typ:
                continue
            plz = r["plz"]
            nn = normalize_name(r["name1"] or "")
            latlon = exact.get((nn, plz)) or cent.get(plz)
            if not latlon:
                continue
            lat, lon = latlon
            if (nn, plz) not in exact:
                h = int(hashlib.md5(kn.encode()).hexdigest(), 16)
                lat += ((h % 1000) / 1000 - 0.5) * 0.02
                lon += (((h // 1000) % 1000) / 1000 - 0.5) * 0.03
            feats.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                "properties": {
                    "kunden_nr": kn, "name": r["name1"], "plz": plz, "ort": r["ort"],
                    "typ": t, "verbrueckt": r["business_partner_id"] is not None,
                },
            })
        return {"type": "FeatureCollection", "features": feats}
