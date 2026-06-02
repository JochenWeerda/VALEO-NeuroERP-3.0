"""GAP Annual Sync Worker.

Zieht die aktuellste EU-GAP-Begünstigtenliste (agrarzahlungen.de) automatisch
einmal jährlich und fährt die Pipeline. Idempotent: läuft pro Haushaltsjahr nur
einmal durch (überspringt, wenn ``gap_payments`` für das Jahr bereits befüllt
ist), sodass ein täglicher Scheduler-Check gefahrlos ist und das neue Jahr
aufnimmt, sobald es (bis 31. Mai) veröffentlicht wird.

Konfiguration (Umgebungsvariablen):
    GAP_AUTO_PLZ_FILTER   – optionaler PLZ-Filter, z.B. "26" oder "26,49"
                            (leer = komplette Liste importieren)
    GAP_CSV_URL_TEMPLATE  – Download-URL-Muster (Default agrarzahlungen.de)
    GAP_EUR_PER_HA        – €/ha-Faktor der Flächenschätzung (Default 270)

Manueller Lauf (z.B. via OS-Cron / Windows-Aufgabenplanung jährlich ab 1. Juni):
    python -m app.workers.gap_sync_worker            # neuestes Jahr, idempotent
    python -m app.workers.gap_sync_worker --year 2025 --force --plz 26
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import text

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


def _plz_filter_from_env() -> Optional[list[str]]:
    raw = os.getenv("GAP_AUTO_PLZ_FILTER", "").strip()
    if not raw:
        return None
    return [p.strip() for p in raw.split(",") if p.strip()]


class GapAnnualSyncWorker(BaseWorker):
    def __init__(self, year: Optional[int] = None, force: bool = False, plz_filter: Optional[list[str]] = None) -> None:
        super().__init__()
        self.year = year
        self.force = force
        self.plz_filter = plz_filter if plz_filter is not None else _plz_filter_from_env()

    def _already_imported(self, year: int) -> bool:
        try:
            count = self.db.execute(
                text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}
            ).scalar()
            return bool(count and count > 0)
        except Exception:  # noqa: BLE001 — Tabelle existiert evtl. noch nicht → als „nicht importiert" werten
            self.db.rollback()
            return False

    async def run(self) -> Dict[str, Any]:
        result = self._base_result(downloaded=False, imported=False)
        try:
            await self._ensure_db()
            # Späte Imports: Engine erst zur Laufzeit laden.
            from app.services.gap_pipeline import (
                download_gap_csv,
                latest_published_year,
                run_year_pipeline,
            )

            year = self.year or latest_published_year()
            result["year"] = year
            result["plz_filter"] = self.plz_filter

            if not self.force and self._already_imported(year):
                result.update(skipped=True, reason=f"gap_payments für {year} bereits vorhanden")
                logger.info("[GAP SYNC] Jahr %s bereits importiert – übersprungen.", year)
                return result

            logger.info("[GAP SYNC] Starte Jahres-Sync %s (force=%s, plz=%s)", year, self.force, self.plz_filter)
            csv_path = download_gap_csv(year, force=self.force)
            result["downloaded"] = True
            result["csv_path"] = csv_path

            pipeline = run_year_pipeline(
                year, csv_path=csv_path, plz_filter=self.plz_filter
            )
            result["imported"] = True
            result["pipeline"] = pipeline
            logger.info("[GAP SYNC] Jahres-Sync %s abgeschlossen: %s", year, pipeline.get("import"))
        except Exception as exc:  # noqa: BLE001 — Worker meldet Fehler strukturiert
            self._error_result(result, exc)
        return result

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_gap_annual_sync(
    year: Optional[int] = None, force: bool = False, plz_filter: Optional[list[str]] = None
) -> Dict[str, Any]:
    worker = GapAnnualSyncWorker(year=year, force=force, plz_filter=plz_filter)
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:  # noqa: BLE001
        logger.error("Critical error in GAP annual sync worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_gap_annual_sync(
    year: Optional[int] = None, force: bool = False, plz_filter: Optional[list[str]] = None
) -> Dict[str, Any]:
    """Synchroner Einstieg für Scheduler/CLI."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_gap_annual_sync(year=year, force=force, plz_filter=plz_filter))
        finally:
            loop.close()
    except Exception as exc:  # noqa: BLE001
        logger.error("Error executing GAP annual sync: %s", exc)
        return {"success": False, "error": str(exc)}


if __name__ == "__main__":
    import argparse
    import json

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="GAP Annual Sync – lädt die EU-GAP-Liste und fährt die Pipeline.")
    parser.add_argument("--year", type=int, default=None, help="Haushaltsjahr (Default: neuestes verfügbares)")
    parser.add_argument("--force", action="store_true", help="Erneut laden/importieren, auch wenn schon vorhanden")
    parser.add_argument("--plz", type=str, default=None, help="PLZ-Filter (z.B. '26' oder '26,49'); leer = alle")
    args = parser.parse_args()
    plz = [p.strip() for p in args.plz.split(",")] if args.plz else None
    outcome = execute_gap_annual_sync(year=args.year, force=args.force, plz_filter=plz)
    print(json.dumps(outcome, indent=2, ensure_ascii=False, default=str))
