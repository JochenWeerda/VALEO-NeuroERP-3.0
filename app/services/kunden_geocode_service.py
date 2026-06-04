"""Befüllt public.kunden_geo mit präzisen Koordinaten je Kunde.

Strategie (beste verfügbare Genauigkeit, ohne Zufalls-Streuung):
1. **Adress-Match** gegen die adressgenau geokodierten gap_map_points über
   Tokenset(Name)+PLZ (reihenfolge-robust) → precision='address'.
2. **Eigene Straße** des Kunden (falls vorhanden) via Nominatim → precision='address'.
3. **Orts-/PLZ-Zentrum** via Nominatim (regionsbegrenzt, gecacht) → precision='place'.

Schritt 1 ist offline (kein Netz); Schritte 2/3 nutzen den bestehenden
geo_pipeline-Geocoder (rate-limitiert). So liegt jeder Kunde am realen Ort statt
am gejitterten PLZ-Zentroid.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.gap_pipeline import tokenset
from app.services.geo_pipeline import _geocode_one

logger = logging.getLogger("crm.geocode")


class KundenGeocodeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Schritt 1: Offline-Match gegen adressgenaue gap_map_points ─────────
    def match_address_points(self) -> dict:
        """Setzt precision='address' für Kunden, die per Tokenset(Name)+PLZ einen
        adressgenauen gap_map_points-Treffer haben. Idempotent (überschreibt nur
        nicht-manuelle Einträge)."""
        points = self.db.execute(
            text("SELECT name_norm, postal_code, lat, lon FROM gap_map_points "
                 "WHERE lat IS NOT NULL AND lon IS NOT NULL")
        ).all()
        idx: dict[tuple, tuple] = {}
        for nn, pc, lat, lon in points:
            if nn and pc:
                idx.setdefault((tokenset(nn), pc), (float(lat), float(lon)))

        kunden = self.db.execute(
            text("SELECT kunden_nr, name1, plz FROM public.kunden WHERE coalesce(geloescht, FALSE) = FALSE")
        ).mappings().all()
        matched = 0
        for k in kunden:
            key = (tokenset(k["name1"] or ""), k["plz"])
            hit = idx.get(key)
            if not hit:
                continue
            self._upsert(k["kunden_nr"], hit[0], hit[1], "address", "map_points",
                         f"map_points:{key[0]}|{key[1]}")
            matched += 1
        self.db.commit()
        return {"kunden": len(kunden), "address_points": len(idx), "matched": matched}

    # ── Schritt 2/3: Geocoding der Restlichen (Straße bzw. Ort/PLZ) ────────
    def geocode_pending(self, limit: int = 50, sleep_seconds: float = 1.1) -> dict:
        """Geocodiert Kunden ohne Koordinate: eigene Straße falls vorhanden,
        sonst Ort/PLZ-Zentrum. Rate-limitiert (Nominatim), resumable."""
        import time

        rows = self.db.execute(
            text(
                """
                SELECT k.kunden_nr, k.strasse, k.plz, k.ort
                FROM public.kunden k
                LEFT JOIN public.kunden_geo g ON g.kunden_nr = k.kunden_nr
                WHERE coalesce(k.geloescht, FALSE) = FALSE
                  AND (g.kunden_nr IS NULL OR g.precision = 'none')
                  AND k.plz IS NOT NULL
                ORDER BY k.kunden_nr
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        done = ok = 0
        # In-Run-Cache: identische "Straße|PLZ|Ort" nur einmal bei Nominatim anfragen
        # (viele Kunden teilen denselben Ort) — schonend + schnell.
        cache: dict[tuple, tuple] = {}
        for r in rows:
            strasse = (r["strasse"] or "").strip() or None
            ckey = (strasse, r["plz"], (r["ort"] or "").strip())
            if ckey in cache:
                lat, lon, status, query = cache[ckey]
            else:
                lat, lon, status, query = _geocode_one(strasse, r["plz"], r["ort"])
                cache[ckey] = (lat, lon, status, query)
                time.sleep(sleep_seconds)  # nur bei echtem Nominatim-Request warten
            if status == "ok":
                precision = "address" if strasse else "place"
                source = "nominatim_address" if strasse else "nominatim_place"
                self._upsert(r["kunden_nr"], lat, lon, precision, source, query)
                ok += 1
            else:
                self._upsert(r["kunden_nr"], None, None, "none", "nominatim_place", query)
            self.db.commit()
            done += 1
        remaining = self.db.execute(
            text("SELECT count(*) FROM public.kunden k WHERE coalesce(k.geloescht, FALSE) = FALSE AND k.plz IS NOT NULL "
                 "AND NOT EXISTS (SELECT 1 FROM public.kunden_geo g WHERE g.kunden_nr = k.kunden_nr AND g.precision <> 'none')")
        ).scalar()
        return {"processed": done, "geocoded_ok": ok, "remaining": int(remaining or 0)}

    # ── Upgrade: Kunden mit nur Ortsgenauigkeit auf Adressgenauigkeit heben ──
    def upgrade_to_address(self, limit: int = 500, sleep_seconds: float = 1.1) -> dict:
        """Für Kunden ohne Adressgenauigkeit: passende gap_map_points-Adresse
        (Straße, aus KMZ/CSV) über Tokenset(Name)+PLZ finden und die VOLLE Adresse
        geocodieren → precision='address'. Nur kundenrelevante Adressen, dedupliziert."""
        import time

        pts = self.db.execute(
            text("SELECT name_norm, postal_code, ortsteil, adresse, ort FROM gap_map_points "
                 "WHERE adresse IS NOT NULL AND adresse <> ''")
        ).mappings().all()
        idx: dict[tuple, dict] = {}
        for p in pts:
            key = (tokenset(p["name_norm"] or ""), p["postal_code"])
            # vollständigste Adresse je Schlüssel bevorzugen
            cur = idx.get(key)
            if cur is None or len(p["adresse"] or "") > len(cur["adresse"] or ""):
                idx[key] = dict(p)

        kunden = self.db.execute(
            text(
                """
                SELECT k.kunden_nr, k.name1, k.plz, k.ort
                FROM public.kunden k
                LEFT JOIN public.kunden_geo g ON g.kunden_nr = k.kunden_nr
                WHERE coalesce(k.geloescht, FALSE) = FALSE AND k.plz IS NOT NULL
                  AND (g.kunden_nr IS NULL OR g.precision <> 'address')
                  AND (g.source IS NULL OR g.source <> 'manuell')
                ORDER BY k.kunden_nr
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()

        cache: dict[str, tuple] = {}
        done = ok = 0
        for k in kunden:
            hit = idx.get((tokenset(k["name1"] or ""), k["plz"]))
            if not hit:
                continue
            strasse = " ".join(p for p in [hit.get("ortsteil"), hit.get("adresse")] if p).strip()
            query = ", ".join(p for p in [strasse, f"{k['plz']} {hit.get('ort') or k['ort'] or ''}".strip(), "Deutschland"] if p)
            if query in cache:
                lat, lon, status = cache[query]
            else:
                lat, lon, status, _q = _geocode_one(strasse, k["plz"], hit.get("ort") or k["ort"])
                cache[query] = (lat, lon, status)
                time.sleep(sleep_seconds)
            done += 1
            if status == "ok":
                self._upsert(k["kunden_nr"], lat, lon, "address", "kmz_geocode", query)
                ok += 1
                self.db.commit()
        return {"geprueft": done, "adressgenau_neu": ok}

    def _upsert(self, kunden_nr: str, lat: Optional[float], lon: Optional[float],
                precision: str, source: str, query: str) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO public.kunden_geo (kunden_nr, lat, lon, precision, source, geocode_query, geocoded_at, updated_at)
                VALUES (:k, :lat, :lon, :p, :s, :q, now(), now())
                ON CONFLICT (kunden_nr) DO UPDATE SET
                  lat = EXCLUDED.lat, lon = EXCLUDED.lon, precision = EXCLUDED.precision,
                  source = EXCLUDED.source, geocode_query = EXCLUDED.geocode_query,
                  geocoded_at = now(), updated_at = now()
                WHERE public.kunden_geo.source <> 'manuell'
                """
            ),
            {"k": kunden_nr, "lat": lat, "lon": lon, "p": precision, "s": source, "q": query},
        )

    def stats(self) -> dict:
        rows = self.db.execute(
            text("SELECT precision, count(*) FROM public.kunden_geo GROUP BY precision")
        ).all()
        return {p: int(n) for p, n in rows}
