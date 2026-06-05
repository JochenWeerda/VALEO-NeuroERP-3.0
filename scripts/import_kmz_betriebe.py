"""Importiert die Betriebsliste aus einer Google-My-Maps-KMZ in gap_map_points.

Zwei Ausbaustufen, beide von dieser Datei abgedeckt:

1. **Adress-KMZ** (alter Export "Futtermittelbetriebe PLZ 26"): je Placemark
   Name + strukturierte ExtendedData (Ortsteil, Adresse, PLZ, Ort), aber KEINE
   Koordinaten (My Maps geokodiert die Adresse live). Wir spielen die sauberen
   Adressen nach gap_map_points; geocode_pending kodiert sie offline nach.

2. **Koordinaten-KMZ** (Re-Export, NACHDEM My Maps die angereicherte CSV
   geokodiert hat): jedes Placemark trägt zusätzlich
   ``<Point><coordinates>lon,lat,0</coordinates></Point>``. Diese Koordinaten
   sind hofgenau (Google-Geocoder, deutlich besser als Nominatim). Wir schreiben
   sie in gap_map_points (geocode_status='ok', source_layer='kmz_coords') und
   heben anschließend die zugehörigen Kunden über den vorhandenen Offline-Match
   (KundenGeocodeService.match_address_points) auf precision='address' — das
   schließt den Hofgenauigkeits-Loop ohne Nominatim.

Encoding: ältere Adress-KMZ ist cp1252 (trotz UTF-8-Deklaration); My-Maps-
Koordinaten-Re-Exporte sind i.d.R. UTF-8. Wir probieren UTF-8, dann cp1252.

Aufruf:
  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend \
    python scripts/import_kmz_betriebe.py "Futtermittelbetriebe PLZ 26.kmz"
  # Koordinaten-Loop nicht automatisch schließen (nur gap_map_points füllen):
  ... python scripts/import_kmz_betriebe.py export.kmz --no-match
"""

from __future__ import annotations

import html
import re
import sys
import zipfile

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.gap_pipeline import normalize_name
from app.services.geo_pipeline import (
    GEO_LAT_MAX,
    GEO_LAT_MIN,
    GEO_LON_MAX,
    GEO_LON_MIN,
    ensure_geo_schema,
)
from app.services.kunden_geocode_service import KundenGeocodeService

_PLACE = re.compile(r"<Placemark>(.*?)</Placemark>", re.S)
_NAME = re.compile(r"<name>(.*?)</name>", re.S)
# KML-Koordinaten: lon,lat[,elevation] innerhalb <Point>. Reihenfolge ist lon,lat!
_COORD = re.compile(r"<Point>.*?<coordinates>\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", re.S)


def _data(block: str, key: str) -> str:
    m = re.search(rf'<Data name="{key}">\s*<value>(.*?)</value>', block, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def _coords(block: str) -> tuple[float, float] | None:
    """(lat, lon) aus dem Placemark, falls vorhanden und im PLZ-26-Gebiet.

    My Maps liefert lon,lat; wir drehen auf (lat, lon). Koordinaten außerhalb der
    Region (Geocoder-Ausreißer/falsche Adresse) werden verworfen."""
    m = _COORD.search(block)
    if not m:
        return None
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (GEO_LAT_MIN <= lat <= GEO_LAT_MAX and GEO_LON_MIN <= lon <= GEO_LON_MAX):
        return None
    return lat, lon


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    path = args[0] if args else "Futtermittelbetriebe PLZ 26.kmz"
    auto_match = "--no-match" not in flags

    with zipfile.ZipFile(path) as z:
        raw = z.read("doc.kml")
    for enc in ("utf-8", "cp1252"):
        try:
            kml = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        kml = raw.decode("utf-8", errors="replace")

    db = SessionLocal()
    inserted = 0
    seen = 0
    with_coords = 0
    outside = 0
    try:
        ensure_geo_schema(db)
        # COALESCE bewahrt vorhandene Koordinaten, wenn der neue Datensatz keine
        # trägt; ein Koordinaten-Re-Import überschreibt eine reine Adresszeile.
        ins = text(
            """
            INSERT INTO gap_map_points
                (name, name_norm, ortsteil, adresse, postal_code, ort,
                 source_layer, lat, lon, geocode_status, geocode_query, geocoded_at)
            VALUES
                (:name, :name_norm, :ortsteil, :adresse, :postal_code, :ort,
                 :layer, :lat, :lon,
                 CASE WHEN :lat IS NULL THEN NULL ELSE 'ok' END,
                 CASE WHEN :lat IS NULL THEN NULL ELSE 'kmz_coords' END,
                 CASE WHEN :lat IS NULL THEN NULL ELSE now() END)
            ON CONFLICT (name_norm, postal_code, adresse) DO UPDATE SET
                lat = COALESCE(EXCLUDED.lat, gap_map_points.lat),
                lon = COALESCE(EXCLUDED.lon, gap_map_points.lon),
                ortsteil = COALESCE(gap_map_points.ortsteil, EXCLUDED.ortsteil),
                ort = COALESCE(gap_map_points.ort, EXCLUDED.ort),
                geocode_status = CASE WHEN EXCLUDED.lat IS NOT NULL THEN 'ok'
                                      ELSE gap_map_points.geocode_status END,
                geocode_query = CASE WHEN EXCLUDED.lat IS NOT NULL THEN 'kmz_coords'
                                     ELSE gap_map_points.geocode_query END,
                geocoded_at = CASE WHEN EXCLUDED.lat IS NOT NULL THEN now()
                                   ELSE gap_map_points.geocoded_at END
            """
        )
        for block in _PLACE.findall(kml):
            nm = _NAME.search(block)
            name = html.unescape(nm.group(1)).strip() if nm else ""
            plz = _data(block, "PLZ")
            if not name or not re.match(r"^\d{5}$", plz):
                continue
            seen += 1
            coords = _coords(block)
            if _COORD.search(block) and coords is None:
                outside += 1  # Koordinate vorhanden, aber außerhalb der Region
            lat, lon = (coords if coords else (None, None))
            if coords:
                with_coords += 1
            layer = "kmz_coords" if coords else "kmz_futtermittel"
            res = db.execute(ins, {
                "name": name, "name_norm": normalize_name(name),
                "ortsteil": _data(block, "Ortsteil") or None,
                "adresse": _data(block, "Adresse") or None,
                "postal_code": plz, "ort": _data(block, "Ort") or None,
                "layer": layer, "lat": lat, "lon": lon,
            })
            inserted += res.rowcount or 0
            if seen % 1000 == 0:
                db.commit()
        db.commit()
        total = db.execute(text("SELECT count(*) FROM gap_map_points")).scalar()
        pending = db.execute(text("SELECT count(*) FROM gap_map_points WHERE lat IS NULL")).scalar()
        print(
            f"import_kmz: {seen} Placemarks, {inserted} eingefügt/aktualisiert, "
            f"{with_coords} mit Koordinaten ({outside} außerhalb der Region verworfen); "
            f"gap_map_points={total}, offen(geocode)={pending}"
        )

        # Hofgenauigkeits-Loop schließen: Kunden auf die frisch importierten,
        # adressgenauen gap_map_points heben (offline, kein Nominatim).
        if with_coords and auto_match:
            res = KundenGeocodeService(db).match_address_points()
            print(f"kunden_geo match: {res}")
            print(f"kunden_geo stats: {KundenGeocodeService(db).stats()}")
        elif with_coords:
            print("Hinweis: --no-match gesetzt → kunden_geo nicht aktualisiert "
                  "(manuell: python scripts/geocode_kunden.py match)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
