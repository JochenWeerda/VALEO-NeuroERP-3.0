"""Geo-Pipeline – Betriebsadressen → Koordinaten für den Außendienst-Viewer.

Importiert die PLZ-26-Betriebslisten (Name + Adresse, aus den My-Maps-Quell-CSVs)
in ``gap_map_points`` und geocodiert die Adressen über Nominatim/OSM (gecacht,
resumable, rate-limitiert). Die Potenzialdaten kommen NICHT aus diesen CSVs
(deren Euro-Spalten sind durch Tausender-Kommas zerbrochen), sondern aus den
authentischen ``gap_payments``/``dairy_herd_performance``-Tabellen – Join später
über name_norm + PLZ.

Quelle der Punkte: vom Nutzer exportierte Listen
``Futtermittelbetriebe PLZ 26- Landwirte PLZ 26*.xlsx.csv``.
"""

from __future__ import annotations

import csv
import glob
import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.gap_pipeline import normalize_name, tokenset as _tokenset

logger = logging.getLogger("geo.pipeline")

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CSV_GLOB = str(BASE_DIR / "Futtermittelbetriebe PLZ 26- Landwirte PLZ 26*.csv")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Nominatim-Nutzungsregeln: aussagekräftiger User-Agent + max 1 Request/Sekunde.
NOMINATIM_UA = "VALEO-NeuroERP-GeoSync/1.0 (jochen.weerda@gmail.com)"
_PLZ_RE = re.compile(r"^\d{5}$")

# Bounding-Box des PLZ-26-Gebiets (Ostfriesland/Oldenburger Land), env-überschreibbar.
# Dient (a) als Geocoder-viewbox (verhindert Fehl-Treffer gleichnamiger Orte
# außerhalb der Region) und (b) als Serve-Filter gegen Geocode-Ausreißer.
GEO_LAT_MIN = float(os.getenv("GAP_GEO_LAT_MIN", "52.7"))
GEO_LAT_MAX = float(os.getenv("GAP_GEO_LAT_MAX", "53.95"))
GEO_LON_MIN = float(os.getenv("GAP_GEO_LON_MIN", "6.5"))
GEO_LON_MAX = float(os.getenv("GAP_GEO_LON_MAX", "8.8"))


def ensure_geo_schema(db) -> None:
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS gap_map_points (
                id             BIGSERIAL PRIMARY KEY,
                name           TEXT             NOT NULL,
                name_norm      TEXT             NOT NULL,
                ortsteil       TEXT,
                adresse        TEXT,
                postal_code    TEXT,
                ort            TEXT,
                source_layer   TEXT,
                lat            DOUBLE PRECISION,
                lon            DOUBLE PRECISION,
                geocode_status TEXT,
                geocode_query  TEXT,
                geocoded_at    TIMESTAMPTZ,
                UNIQUE (name_norm, postal_code, adresse)
            )
            """
        )
    )
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_mappoints_name_plz ON gap_map_points (name_norm, postal_code)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_mappoints_geo ON gap_map_points (lat, lon)"))
    db.commit()


def _parse_row(row: list[str]) -> Optional[dict]:
    """Robustes Parsen: PLZ = erster 5-stelliger Token; Adresse = Felder davor.

    Verträgt Adressen mit Komma (die das Spaltenraster verschieben).
    """
    if len(row) < 5:
        return None
    plz_idx = next((i for i, v in enumerate(row) if _PLZ_RE.match((v or "").strip())), None)
    if plz_idx is None or plz_idx < 3:
        return None
    name = (row[0] or "").strip()
    if not name:
        return None
    ortsteil = (row[1] or "").strip()
    adresse = ", ".join(p.strip() for p in row[2:plz_idx] if p.strip())
    plz = row[plz_idx].strip()
    ort = (row[plz_idx + 1] if plz_idx + 1 < len(row) else "").strip()
    return {
        "name": name,
        "name_norm": normalize_name(name),
        "ortsteil": ortsteil or None,
        "adresse": adresse or None,
        "postal_code": plz,
        "ort": ort or None,
    }


def import_map_points(csv_glob: str = DEFAULT_CSV_GLOB, db=None) -> dict:
    """Importiert die Betriebslisten in ``gap_map_points`` (idempotent via UNIQUE)."""
    owns = db is None
    db = db or SessionLocal()
    inserted = 0
    skipped = 0
    files = sorted(glob.glob(csv_glob))
    try:
        ensure_geo_schema(db)
        insert_sql = text(
            """
            INSERT INTO gap_map_points (name, name_norm, ortsteil, adresse, postal_code, ort, source_layer)
            VALUES (:name, :name_norm, :ortsteil, :adresse, :postal_code, :ort, :source_layer)
            ON CONFLICT (name_norm, postal_code, adresse) DO NOTHING
            """
        )
        for f in files:
            layer = Path(f).stem
            with open(f, encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                next(reader, None)  # Header
                for raw in reader:
                    rec = _parse_row(raw)
                    if not rec:
                        skipped += 1
                        continue
                    rec["source_layer"] = layer
                    res = db.execute(insert_sql, rec)
                    inserted += res.rowcount or 0
            db.commit()
        return {"files": len(files), "inserted": inserted, "skipped": skipped}
    finally:
        if owns:
            db.close()


# Trend-Anpassung des Scores (relativer Anteilsgewinn/-verlust im Gebiet).
_TREND_DELTA = {
    "wachsend": +12.0,
    "neueinsteiger": +6.0,
    "stabil": 0.0,
    "schrumpfend": -12.0,
    "weichend": -25.0,
}


def _partner_score(
    area_ha: float,
    has_dairy: bool,
    dairy_fe_kg: Optional[float],
    trend: Optional[str] = None,
) -> int:
    """Erklärbarer Partner-Score 0–100 (Investitionspriorität).

    Basis = Betriebsgröße (GAP-Fläche, 300 ha ≙ 100). Milchvieh gibt Bonus
    (Futter-/Betriebsmittel-Potenzial), Spitzenherde zusätzlich. Der relative
    Wachstumstrend (Anteil am Gebiets-Prämienpool, 2024→2025) hebt wachsende
    Betriebe an und senkt schrumpfende/weichende – „in welche Partner investieren".
    """
    score = min(100.0, area_ha / 3.0)
    if has_dairy:
        score = min(100.0, score + 15.0)
        if (dairy_fe_kg or 0) >= 900:  # Spitzenherde
            score = min(100.0, score + 10.0)
    score += _TREND_DELTA.get(trend or "", 0.0)
    return int(round(max(0.0, min(100.0, score))))


# Verkaufsdaten-Quelle für Share-of-Wallet (env-überschreibbar für Produktiv-DB).
SALES_TABLE = os.getenv("SALES_TABLE", "domain_portal.customer_orders")
SALES_KUNDE_COL = os.getenv("SALES_KUNDE_COL", "customer_number")
SALES_AMOUNT_COL = os.getenv("SALES_AMOUNT_COL", "total_net")
SALES_DATE_COL = os.getenv("SALES_DATE_COL", "order_date")


def build_turnover_lookup(db, year: int) -> dict[str, float]:
    """{kunden_nr: Jahresumsatz} aus den Verkaufsdaten (für Share-of-Wallet).

    Quelle/Spalten via env konfigurierbar. Leeres Dict, wenn Tabelle fehlt.
    """
    if db.execute(text("SELECT to_regclass(:n)"), {"n": SALES_TABLE}).scalar() is None:
        logger.warning("[SOW] Verkaufstabelle %s nicht vorhanden – kein Share-of-Wallet.", SALES_TABLE)
        return {}
    rows = db.execute(
        text(
            f"""
            SELECT {SALES_KUNDE_COL} AS kunde, SUM({SALES_AMOUNT_COL}) AS umsatz
            FROM {SALES_TABLE}
            WHERE {SALES_KUNDE_COL} IS NOT NULL
              AND {SALES_DATE_COL} >= :start AND {SALES_DATE_COL} < :end
            GROUP BY {SALES_KUNDE_COL}
            """  # noqa: S608 — Bezeichner aus Config, Werte parametrisiert
        ),
        {"start": f"{year}-01-01", "end": f"{year + 1}-01-01"},
    ).all()
    return {str(k): float(u or 0) for k, u in rows if k}


def _build_trend_lookup(db, year_from: int, year_to: int) -> dict[tuple, dict]:
    """{(tokenset, plz): {trend, rel_change_pct}} aus dem GAP-Jahresvergleich.

    Liefert leeres Dict, wenn das Vorjahr (year_from) keine Daten hat – dann
    fließt kein (verzerrender) Trend in den Score ein.
    """
    from app.services.gap_analytics import growth_trend

    try:
        res = growth_trend(db, year_from, year_to, plz_filter=None)
    except Exception:  # noqa: BLE001 — Trend optional; Score funktioniert auch ohne
        logger.exception("[GEO] growth_trend fehlgeschlagen – Score ohne Trend")
        return {}
    if not res["summary"].get("pool_from_eur"):
        return {}  # kein Vorjahr importiert → kein Trend
    return {
        (_tokenset(r["name"]), r["postal_code"]): {"trend": r["trend"], "rel_change_pct": r["rel_change_pct"]}
        for r in res["rows"]
    }


def get_map_points(
    db=None, only_geocoded: bool = True, trend_years: tuple[int, int] = (2024, 2025)
) -> dict:
    """Join Karte ↔ GAP-Potenzial ↔ Milchleistung ↔ Wachstumstrend → GeoJSON.

    Match über Token-Set(Name)+PLZ (überbrückt unterschiedliche Namensreihenfolge).
    """
    from app.services.lkv_pipeline import build_kunden_lookup

    owns = db is None
    db = db or SessionLocal()
    try:
        from app.services.gap_pipeline import latest_gap_year

        trend_lookup = _build_trend_lookup(db, trend_years[0], trend_years[1])
        kunden_lookup = build_kunden_lookup(db)
        # GAP-Potenzial je (tokenset, plz) — nur das jüngste Jahr (Direktzahlung ist
        # eine Jahresgröße; über mehrere importierte Jahre zu summieren verdoppelt
        # Fläche/Potenzial).
        gap_year = latest_gap_year(db)
        gap: dict[tuple, float] = {}
        for nn, plz, direct in db.execute(
            text(
                """
                SELECT beneficiary_name_norm, postal_code, SUM(direct_total_eur)
                FROM gap_payments_direct_agg
                WHERE beneficiary_name_norm IS NOT NULL AND postal_code IS NOT NULL
                  AND (:y IS NULL OR ref_year = :y)
                GROUP BY beneficiary_name_norm, postal_code
                """
            ),
            {"y": gap_year},
        ).all():
            gap[(_tokenset(nn), plz)] = gap.get((_tokenset(nn), plz), 0.0) + float(direct or 0)

        # Milchleistung je (tokenset, plz) – beste (höchste F+E) je Betrieb
        dairy: dict[tuple, dict] = {}
        for nn, plz, milch, fe, grp in db.execute(
            text(
                """
                SELECT name_norm, postal_code, milch_kg, fett_eiweiss_kg, herd_size_group
                FROM dairy_herd_performance
                WHERE postal_code IS NOT NULL
                """
            )
        ).all():
            key = (_tokenset(nn), plz)
            if key not in dairy or (fe or 0) > (dairy[key]["fe"] or 0):
                dairy[key] = {"milch": float(milch or 0), "fe": float(fe or 0), "group": grp}

        if only_geocoded:
            where = (
                "WHERE lat IS NOT NULL AND lon IS NOT NULL "
                "AND lat BETWEEN :lat_min AND :lat_max AND lon BETWEEN :lon_min AND :lon_max"
            )
        else:
            where = ""
        points = db.execute(
            text(f"SELECT name, name_norm, postal_code, ort, lat, lon FROM gap_map_points {where}"),  # noqa: S608 — where ist code-kontrolliert
            {
                "lat_min": GEO_LAT_MIN, "lat_max": GEO_LAT_MAX,
                "lon_min": GEO_LON_MIN, "lon_max": GEO_LON_MAX,
            },
        ).all()

        features = []
        for name, nn, plz, ort, lat, lon in points:
            key = (_tokenset(nn), plz)
            direct = gap.get(key, 0.0)
            area_ha = round(direct / 270.0, 1) if direct else 0.0
            potential_eur = round(area_ha * 280.0)
            d = dairy.get(key)
            has_dairy = d is not None
            fe = d["fe"] if d else None
            t = trend_lookup.get(key)
            trend = t["trend"] if t else None
            kunden_nr = kunden_lookup.get(key)
            score = _partner_score(area_ha, has_dairy, fe, trend)
            segment = "A" if score >= 70 else "B" if score >= 40 else "C"
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {
                        "name": name.strip(),
                        "plz": plz,
                        "ort": ort,
                        "gap_area_ha": area_ha,
                        "gap_potential_eur": potential_eur,
                        "has_dairy": has_dairy,
                        "dairy_milch_kg": d["milch"] if d else None,
                        "dairy_fe_kg": fe,
                        "herd_size_group": d["group"] if d else None,
                        "trend": trend,
                        "trend_rel_pct": round(t["rel_change_pct"], 1) if (t and t["rel_change_pct"] is not None) else None,
                        "is_customer": kunden_nr is not None,
                        "kunden_nr": kunden_nr,
                        "score": score,
                        "segment": segment,
                    },
                }
            )
        return {"type": "FeatureCollection", "features": features}
    finally:
        if owns:
            db.close()


def _geocode_one(adresse: Optional[str], plz: str, ort: Optional[str]) -> tuple[Optional[float], Optional[float], str, str]:
    """Eine Adresse via Nominatim auflösen. Returns (lat, lon, status, query)."""
    import httpx

    query = ", ".join(p for p in [adresse, f"{plz} {ort or ''}".strip(), "Deutschland"] if p)
    try:
        resp = httpx.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "de",
                # Auf das PLZ-26-Gebiet begrenzen → keine gleichnamigen Orte anderswo.
                "viewbox": f"{GEO_LON_MIN},{GEO_LAT_MAX},{GEO_LON_MAX},{GEO_LAT_MIN}",
                "bounded": 1,
            },
            headers={"User-Agent": NOMINATIM_UA},
            timeout=httpx.Timeout(20.0),
            follow_redirects=True,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None, None, "not_found", query
        return float(data[0]["lat"]), float(data[0]["lon"]), "ok", query
    except Exception as exc:  # noqa: BLE001 — Geocoding best-effort; Fehler markieren, weitermachen
        logger.warning("[GEO] Geocoding fehlgeschlagen für %r: %s", query, exc)
        return None, None, "error", query


def geocode_pending(limit: int = 50, sleep_seconds: float = 1.1, retry_errors: bool = False, db=None) -> dict:
    """Geocodiert offene ``gap_map_points`` (lat IS NULL). Resumable, rate-limitiert.

    ``not_found`` wird nicht erneut versucht; ``error`` nur mit ``retry_errors``.
    """
    owns = db is None
    db = db or SessionLocal()
    done = 0
    ok = 0
    try:
        ensure_geo_schema(db)
        status_filter = "(geocode_status IS NULL OR geocode_status = 'error')" if retry_errors else "geocode_status IS NULL"
        rows = db.execute(
            text(
                f"""
                SELECT id, adresse, postal_code, ort
                FROM gap_map_points
                WHERE lat IS NULL AND {status_filter}
                ORDER BY id
                LIMIT :limit
                """  # noqa: S608 — status_filter ist code-kontrolliert (kein User-Input)
            ),
            {"limit": limit},
        ).all()
        for row_id, adresse, plz, ort in rows:
            lat, lon, status, query = _geocode_one(adresse, plz, ort)
            db.execute(
                text(
                    """
                    UPDATE gap_map_points
                    SET lat = :lat, lon = :lon, geocode_status = :status,
                        geocode_query = :query, geocoded_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"lat": lat, "lon": lon, "status": status, "query": query, "id": row_id},
            )
            db.commit()
            done += 1
            if status == "ok":
                ok += 1
            time.sleep(sleep_seconds)  # Nominatim: max 1 Request/Sekunde
        remaining = db.execute(text("SELECT COUNT(*) FROM gap_map_points WHERE lat IS NULL")).scalar()
        return {"processed": done, "geocoded_ok": ok, "remaining": int(remaining or 0)}
    finally:
        if owns:
            db.close()
