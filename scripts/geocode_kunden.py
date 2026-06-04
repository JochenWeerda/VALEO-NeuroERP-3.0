"""Befüllt public.kunden_geo: erst Offline-Adressmatch gegen gap_map_points,
dann Nominatim-Geocoding der Restlichen (Ort/PLZ bzw. eigene Straße).

Aufruf:
  # nur Adressmatch (offline, schnell):
  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/geocode_kunden.py match
  # Nominatim für den Rest (rate-limitiert, ggf. mehrfach):
  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/geocode_kunden.py geocode 500
"""

from __future__ import annotations

import sys

from app.core.database import SessionLocal
from app.services.kunden_geocode_service import KundenGeocodeService


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "match"
    db = SessionLocal()
    try:
        svc = KundenGeocodeService(db)
        if mode == "match":
            print("match:", svc.match_address_points())
        elif mode == "geocode":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200
            print("geocode:", svc.geocode_pending(limit=limit))
        elif mode == "upgrade":
            print("upgrade:", svc.upgrade_to_address(limit=int(sys.argv[2]) if len(sys.argv) > 2 else 1000))
        elif mode == "all":
            print("match:", svc.match_address_points())
            print("geocode:", svc.geocode_pending(limit=int(sys.argv[2]) if len(sys.argv) > 2 else 1000))
        print("stats:", svc.stats())
    finally:
        db.close()


if __name__ == "__main__":
    main()
