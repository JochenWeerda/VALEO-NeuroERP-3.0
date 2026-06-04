"""Importiert die Betriebsliste aus einer Google-My-Maps-KMZ in gap_map_points.

Die KMZ (Futtermittelbetriebe PLZ 26) enthält je Placemark Name + strukturierte
ExtendedData (Ortsteil, Adresse, PLZ, Ort) — aber KEINE Koordinaten (My Maps
geokodiert die Adresse live). Die Adressen sind sauberer/vollständiger als die
CSV-Quelle (deren Spalten durch Tausender-Kommas zerbrachen). Wir spielen sie nach
gap_map_points ein; das vorhandene geocode_pending kodiert die offenen Adressen.

Encoding: die Datei ist cp1252 (trotz UTF-8-Deklaration).

Aufruf: docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/import_kmz_betriebe.py "Futtermittelbetriebe PLZ 26.kmz"
"""

from __future__ import annotations

import html
import re
import sys
import zipfile

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.gap_pipeline import normalize_name
from app.services.geo_pipeline import ensure_geo_schema

_PLACE = re.compile(r"<Placemark>(.*?)</Placemark>", re.S)
_NAME = re.compile(r"<name>(.*?)</name>", re.S)


def _data(block: str, key: str) -> str:
    m = re.search(rf'<Data name="{key}">\s*<value>(.*?)</value>', block, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "Futtermittelbetriebe PLZ 26.kmz"
    with zipfile.ZipFile(path) as z:
        kml = z.read("doc.kml").decode("cp1252")

    db = SessionLocal()
    inserted = 0
    seen = 0
    try:
        ensure_geo_schema(db)
        ins = text(
            """
            INSERT INTO gap_map_points (name, name_norm, ortsteil, adresse, postal_code, ort, source_layer)
            VALUES (:name, :name_norm, :ortsteil, :adresse, :postal_code, :ort, 'kmz_futtermittel')
            ON CONFLICT (name_norm, postal_code, adresse) DO NOTHING
            """
        )
        for block in _PLACE.findall(kml):
            nm = _NAME.search(block)
            name = html.unescape(nm.group(1)).strip() if nm else ""
            plz = _data(block, "PLZ")
            if not name or not re.match(r"^\d{5}$", plz):
                continue
            seen += 1
            res = db.execute(ins, {
                "name": name, "name_norm": normalize_name(name),
                "ortsteil": _data(block, "Ortsteil") or None,
                "adresse": _data(block, "Adresse") or None,
                "postal_code": plz, "ort": _data(block, "Ort") or None,
            })
            inserted += res.rowcount or 0
            if seen % 1000 == 0:
                db.commit()
        db.commit()
        total = db.execute(text("SELECT count(*) FROM gap_map_points")).scalar()
        pending = db.execute(text("SELECT count(*) FROM gap_map_points WHERE lat IS NULL")).scalar()
        print(f"import_kmz: {seen} Placemarks, {inserted} neu eingefügt; gap_map_points={total}, offen(geocode)={pending}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
