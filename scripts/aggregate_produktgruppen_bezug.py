"""Aggregiert die ECHTE Ist-Seite (public.kunden_produktgruppen_bezug, quelle='verkauf')
aus den realen Verkaufsbelegen — löst die modellierten Seeds (quelle='geschaetzt') ab,
sobald Belege vorhanden sind.

Geschriebene Zeilen tragen quelle='verkauf'; Produktgruppen ohne Belege behalten
ihren bisherigen (ggf. geschätzten) Wert — die quelle-Spalte macht das transparent.

Aufruf:
  # Vorschau (nichts schreiben):
  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/aggregate_produktgruppen_bezug.py --dry-run
  # Schreiben:
  docker exec -e PYTHONPATH=/app valeo-neuro-erp-backend python scripts/aggregate_produktgruppen_bezug.py
"""

from __future__ import annotations

import sys

from app.core.database import SessionLocal
from app.services.ist_aggregation_service import IstAggregationService


def main() -> None:
    dry = "--dry-run" in sys.argv
    db = SessionLocal()
    try:
        res = IstAggregationService(db).aggregate(dry_run=dry)
        print("aggregate_produktgruppen_bezug:", res)
    finally:
        db.close()


if __name__ == "__main__":
    main()
