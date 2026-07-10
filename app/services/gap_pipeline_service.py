"""Service layer for the GAP (Gemeinsame Agrarpolitik) ETL pipeline endpoints.

Orchestriert Start, Status und Reset der GAP-Datenpipeline. Die eigentliche
ETL-Engine liegt in ``app.services.gap_progress`` (Job-/Fortschritts-Tracking)
und ``app.services.gap_pipeline`` (Import-/Aggregations-/Matching-Schritte).
Diese beiden Module werden bewusst *lazy* (innerhalb der Methoden) importiert,
damit der Router auch dann lädt, wenn die Engine in einer Umgebung (noch) nicht
installiert ist — ein fehlender Import schlägt dann erst beim konkreten Aufruf
fehl statt beim App-Start.

Die Worker-Funktionen (`execute_*`) sind die Ziele für Background-Tasks bzw.
Hintergrund-Threads und laufen ohne Request-DB-Session.
"""

from __future__ import annotations

import logging
import re
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError

logger = logging.getLogger("gap.pipeline")

VALID_COMMANDS = ["aggregate", "match", "snapshot", "hydrate-customers", "import"]
PIPELINE_STEP_COUNT = 6
GAP_STATUS_COUNT_QUERIES = {
    ("gap_payments", "ref_year = :year"): text(
        "SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"
    ),
    ("customer_potential_snapshot", "ref_year = :year"): text(
        "SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"
    ),
    ("customers", "analytics_gap_ref_year = :year"): text(
        "SELECT COUNT(*) FROM customers WHERE analytics_gap_ref_year = :year"
    ),
}


# ── Background workers (thread / BackgroundTask targets) ──────────────────────


def execute_pipeline_with_plz_filter(
    year: int,
    csv_path: Optional[str] = None,
    batch_id: Optional[str] = None,
    plz_filter: Optional[list[str]] = None,
) -> None:
    """Führt die komplette GAP-Pipeline (optional PLZ-gefiltert) aus."""
    if not batch_id:
        logger.error("[GAP PIPELINE] Kein batch_id übergeben — Abbruch.")
        return

    from app.services.gap_progress import PipelineProgress

    progress = PipelineProgress(batch_id, year)
    filter_info = f" mit PLZ-Filter {plz_filter}" if plz_filter else ""
    progress.update_status("starting", 1, PIPELINE_STEP_COUNT, f"Pipeline-Thread gestartet{filter_info}...", "running")

    try:
        from app.services.gap_pipeline import run_year_pipeline
    except Exception as import_error:  # noqa: BLE001 — Engine evtl. nicht installiert; an Progress melden
        progress.error(f"Import-Fehler: {import_error}")
        logger.exception("[GAP PIPELINE] Import von run_year_pipeline fehlgeschlagen")
        return

    def progress_callback(step: str, step_num: int, message: str) -> None:
        try:
            if step == "error":
                progress.error(message)
            elif step == "completed":
                progress.complete(message)
            else:
                progress.update_status(step, step_num, PIPELINE_STEP_COUNT, message, "running")
        except Exception:  # noqa: BLE001 — Progress-Reporting ist best-effort
            logger.exception("[GAP PIPELINE] Progress-Callback-Fehler")

    try:
        progress.update_status("initializing", 2, PIPELINE_STEP_COUNT, "Initialisiere Pipeline-Parameter...", "running")
        result = run_year_pipeline(
            year=year,
            csv_path=csv_path,
            batch_id=batch_id,
            progress_callback=progress_callback,
            plz_filter=plz_filter,
        )
        progress.complete(f"Pipeline erfolgreich abgeschlossen{filter_info}")
        logger.info("[GAP PIPELINE] Abgeschlossen (batch=%s): %s", batch_id, result)
    except Exception as exc:  # noqa: BLE001 — Worker-Thread; Fehler an Progress melden und loggen
        try:
            progress.error(f"Pipeline-Fehler: {exc}")
        except Exception:  # noqa: BLE001 — Progress-Reporting ist best-effort
            pass
        logger.exception("[GAP PIPELINE] Pipeline fehlgeschlagen (batch=%s)", batch_id)


def execute_command(
    command: str,
    year: int,
    csv_path: Optional[str] = None,
    batch_id: Optional[str] = None,
) -> None:
    """Führt einen einzelnen GAP-Pipeline-Schritt aus."""
    from app.services.gap_pipeline import (
        run_aggregate,
        run_hydrate_customers,
        run_import,
        run_match,
        run_snapshot,
    )

    try:
        if command == "import":
            if not csv_path:
                default_path = Path(f"data/gap/impdata{year}.csv")
                if default_path.exists():
                    csv_path = str(default_path)
                else:
                    try:
                        from app.services.gap_pipeline import download_gap_csv

                        csv_path = download_gap_csv(year)
                    except Exception as dl_err:  # noqa: BLE001 — Download-Fallback fehlgeschlagen
                        raise ValueError(
                            f"csv_path ist erforderlich für Import und Download fehlgeschlagen: {dl_err}"
                        ) from dl_err
            result = run_import(year=year, csv_path=csv_path, batch_id=batch_id)
        elif command == "aggregate":
            result = run_aggregate(year=year)
        elif command == "match":
            result = run_match(year=year)
        elif command == "snapshot":
            result = run_snapshot(year=year)
        elif command == "hydrate-customers":
            result = run_hydrate_customers(year=year)
        else:
            raise ValueError(f"Unbekannter Command: {command}")
        logger.info("[GAP COMMAND] %s erfolgreich für Jahr %s: %s", command, year, result)
    except Exception:  # noqa: BLE001 — Worker; Fehler wird geloggt, kein Re-Raise im Hintergrund
        logger.exception("[GAP COMMAND] Fehler bei %s für Jahr %s", command, year)


def execute_download(year: int) -> None:
    """Lädt die externe GAP-CSV für ein Jahr herunter."""
    from app.services.gap_pipeline import download_gap_csv

    try:
        path = download_gap_csv(year)
        logger.info("[GAP DOWNLOAD] Erfolgreich: %s", path)
    except Exception:  # noqa: BLE001 — Worker; Fehler wird geloggt
        logger.exception("[GAP DOWNLOAD] Fehler beim Download für Jahr %s", year)


# ── Service ───────────────────────────────────────────────────────────────────


class GapPipelineService:
    """Orchestriert Start/Status/Reset der GAP-Pipeline.

    ``db`` wird nur für die DB-gebundenen Operationen (Status, Reset) benötigt;
    die Start-Methoden delegieren an Background-Tasks bzw. Threads.
    """

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db

    @staticmethod
    def _parse_plz_filter(plz_filter: Optional[str]) -> Optional[list[str]]:
        if not plz_filter:
            return None
        parsed = [plz.strip() for plz in plz_filter.split(",") if plz.strip()]
        return parsed or None

    def start_year_pipeline(
        self,
        year: int,
        csv_path: Optional[str],
        batch_id: Optional[str],
        plz_filter: Optional[str],
    ) -> tuple[str, str]:
        """Startet die Jahres-Pipeline in einem Hintergrund-Thread.

        Returns ``(job_id, message)``.
        """
        from app.services.gap_progress import create_pipeline_job

        job_id = batch_id or create_pipeline_job(year)
        plz_list = self._parse_plz_filter(plz_filter)

        thread = threading.Thread(
            target=execute_pipeline_with_plz_filter,
            args=(year, csv_path, job_id, plz_list),
            daemon=True,
        )
        thread.start()

        filter_info = f" (PLZ-Filter: {plz_filter})" if plz_filter else ""
        logger.info("[GAP] Pipeline-Thread gestartet (job=%s)%s", job_id, filter_info)
        return job_id, f"GAP-Pipeline für Jahr {year} wurde gestartet{filter_info}"

    def queue_import(
        self,
        background_tasks: BackgroundTasks,
        year: int,
        csv_path: Optional[str],
        batch_id: Optional[str],
    ) -> str:
        """Stellt den Import als Background-Task ein und liefert die Statusmeldung."""
        resolved_path = csv_path
        if not resolved_path:
            default_path = Path(f"data/gap/impdata{year}.csv")
            if default_path.exists():
                resolved_path = str(default_path)
        background_tasks.add_task(
            execute_command,
            command="import",
            year=year,
            csv_path=resolved_path,
            batch_id=batch_id,
        )
        return f"GAP-Import für Jahr {year} wurde gestartet"

    def queue_external_download(self, background_tasks: BackgroundTasks, year: int) -> str:
        background_tasks.add_task(execute_download, year=year)
        return f"Download der GAP-Daten für Jahr {year} gestartet."

    def queue_command(self, background_tasks: BackgroundTasks, command: str, year: int) -> str:
        if command not in VALID_COMMANDS:
            raise BadRequestError(f"Ungültiger Command. Verfügbar: {', '.join(VALID_COMMANDS)}")

        csv_path = None
        if command == "import":
            default_path = Path(f"data/gap/impdata{year}.csv")
            if default_path.exists():
                csv_path = str(default_path)

        background_tasks.add_task(execute_command, command=command, year=year, csv_path=csv_path)
        return f"GAP-{command} für Jahr {year} wurde gestartet"

    @staticmethod
    def store_upload(file: UploadFile, year: Optional[int]) -> dict[str, Any]:
        """Speichert eine hochgeladene GAP-CSV unter ``data/gap/impdata{year}.csv``."""
        if year is None:
            if file.filename:
                match = re.search(r"(\d{4})", file.filename)
                if match:
                    year = int(match.group(1))
            if year is None:
                year = datetime.now().year
                logger.info("[GAP UPLOAD] Kein Jahr angegeben, verwende aktuelles Jahr: %s", year)

        if year < 2020 or year > 2030:
            raise BadRequestError(f"Ungültiges Jahr: {year}. Muss zwischen 2020 und 2030 liegen.")

        data_dir = Path("data/gap")
        data_dir.mkdir(parents=True, exist_ok=True)
        target_path = data_dir / f"impdata{year}.csv"

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "stored_path": str(target_path),
            "year": year,
            "filename": file.filename,
            "size_bytes": target_path.stat().st_size,
            "message": f"Datei erfolgreich gespeichert: {target_path}",
        }

    def pipeline_status(self, year: int) -> dict[str, Any]:
        """Liefert Roh-Zählerstände der Pipeline-Tabellen für ein Jahr."""
        assert self.db is not None, "pipeline_status benötigt eine DB-Session"
        gap_count = self._safe_count("gap_payments", "ref_year = :year", {"year": year})
        snapshot_count = self._safe_count("customer_potential_snapshot", "ref_year = :year", {"year": year})
        customer_count = self._safe_count("customers", "analytics_gap_ref_year = :year", {"year": year})

        return {
            "year": year,
            "gap_payments_count": gap_count or 0,
            "snapshot_count": snapshot_count or 0,
            "customers_with_analytics_count": customer_count or 0,
            "pipeline_complete": bool(gap_count and snapshot_count and customer_count),
        }

    def _safe_count(self, table: str, where_sql: str, params: dict[str, Any]) -> int:
        statement = GAP_STATUS_COUNT_QUERIES.get((table, where_sql))
        if statement is None:
            raise ValueError(f"Unsupported GAP status count query: {table} / {where_sql}")
        try:
            return int(
                self.db.execute(
                    statement,
                    params,
                ).scalar()
                or 0
            )
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            logger.info("[GAP STATUS] Tabelle nicht verfuegbar: %s", table)
            return 0

    @staticmethod
    def pipeline_progress(job_id: str) -> Optional[dict[str, Any]]:
        from app.services.gap_progress import get_pipeline_progress

        return get_pipeline_progress(job_id)

    # ── Lead-Generierung aus GAP-Snapshots ───────────────────────────────────

    @staticmethod
    def _lead_priority(potential_eur: float) -> str:
        if potential_eur >= 100_000:
            return "Hoch"
        if potential_eur >= 50_000:
            return "Mittel"
        return "Niedrig"

    def generate_leads_from_snapshots(
        self,
        year: int,
        plz_min: Optional[str],
        plz_max: Optional[str],
        min_potential_eur: int,
        max_leads: int,
        segment: Optional[str],
    ) -> dict[str, Any]:
        """Erzeugt Kampagnen-Leads aus den GAP-Potenzial-Snapshots eines Jahres.

        Komfort-Endpoint: Da die EU-GAP-Empfängerliste jährlich neu von Brüssel
        publiziert wird, kann hiermit pro Referenzjahr direkt eine gefilterte
        Lead-Liste (PLZ-Bereich, Segment, Mindest-Potenzial) gezogen werden.
        Liest dieselben Tabellen wie ``/prospecting/lead-candidates``
        (``customer_potential_snapshot`` JOIN ``customers``).
        """
        assert self.db is not None, "generate_leads_from_snapshots benötigt eine DB-Session"

        params: dict[str, Any] = {
            "year": year,
            "min_potential": min_potential_eur,
            "max_leads": max_leads,
        }
        plz_clause = ""
        if plz_min and plz_max:
            plz_clause = "AND c.postal_code BETWEEN :plz_min AND :plz_max"
            params["plz_min"], params["plz_max"] = plz_min, plz_max
        elif plz_min:
            plz_clause = "AND c.postal_code >= :plz_min"
            params["plz_min"] = plz_min
        elif plz_max:
            plz_clause = "AND c.postal_code <= :plz_max"
            params["plz_max"] = plz_max

        segment_clause = ""
        if segment and segment in ("A", "B", "C"):
            segment_clause = "AND s.segment = :segment"
            params["segment"] = segment

        query = text(
            f"""
            SELECT
                s.customer_id,
                c.name AS customer_name,
                c.postal_code,
                c.city,
                s.potential_total_eur,
                s.gap_direct_total_eur,
                s.gap_estimated_area_ha,
                s.segment,
                s.share_of_wallet_total_pct,
                COALESCE(c.status, 'lead') AS customer_status
            FROM customer_potential_snapshot s
            JOIN customers c ON c.id = s.customer_id
            WHERE s.ref_year = :year
              AND s.potential_total_eur >= :min_potential
              {plz_clause}
              {segment_clause}
            ORDER BY s.potential_total_eur DESC
            LIMIT :max_leads
            """  # noqa: S608 — Filter-Klauseln sind code-kontrolliert, alle Werte parametrisiert
        )

        try:
            rows = self.db.execute(query, params).mappings().all()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            logger.exception("[GAP LEADS] Snapshot-Tabellen nicht verfügbar für Jahr %s", year)
            return {
                "success": False,
                "leads": [],
                "total_leads": 0,
                "available_farmers": False,
                "message": "Lead-Generierung fehlgeschlagen — keine GAP-Snapshots verfügbar. Pipeline für dieses Jahr zuerst ausführen.",
            }

        leads: list[dict[str, Any]] = []
        for row in rows:
            potential = float(row["potential_total_eur"] or 0)
            area = float(row["gap_estimated_area_ha"] or 0)
            status = row["customer_status"]
            leads.append(
                {
                    "id": f"gap_{year}_{row['customer_id']}",
                    "customer_id": str(row["customer_id"]),
                    "name": row["customer_name"],
                    "company": row["customer_name"],
                    "postal_code": row["postal_code"],
                    "city": row["city"],
                    "potential_eur": potential,
                    "gap_amount_eur": float(row["gap_direct_total_eur"] or 0),
                    "estimated_hectares": area,
                    "segment": row["segment"] or "C",
                    "priority": self._lead_priority(potential),
                    "share_of_wallet_pct": float(row["share_of_wallet_total_pct"] or 0),
                    "source": f"GAP-Pipeline {year}",
                    "description": f"Landwirtschafts-Potenzial: {round(potential)} EUR ({round(area, 1)} ha)",
                    "lead_type": "Agricultural GAP Lead",
                    "industry": "Agriculture",
                    "year": year,
                    "customer_status": status,
                    "is_lead": status in (None, "lead"),
                    "is_customer": status in ("active", "inactive"),
                    "is_blocked": status == "blocked",
                    "created_from_gap": True,
                    "status": "lead" if status in (None, "lead") else "customer",
                }
            )

        return {
            "success": True,
            "leads": leads,
            "total_leads": len(leads),
            "available_farmers": len(leads) > 0,
            "filters_applied": {
                "year": year,
                "plz_range": f"{plz_min}-{plz_max}" if plz_min and plz_max else None,
                "min_potential_eur": min_potential_eur,
                "max_leads": max_leads,
                "segment": segment,
            },
            "message": (
                f"{len(leads)} Landwirtschafts-Leads generiert"
                if leads
                else "Noch keine Landwirte verfügbar — Pipeline/Snapshot für dieses Jahr erforderlich"
            ),
        }

    def reset_gap_data(self, year: int, tables: str, all_years: bool) -> dict[str, Any]:
        """Löscht GAP-Zahlungen/Snapshots/Matches für einen Neustart.

        ``tables`` ∈ {all, payments, snapshots, matches}. Der View
        ``gap_payments_direct_agg`` wird automatisch aktualisiert.
        """
        assert self.db is not None, "reset_gap_data benötigt eine DB-Session"
        db = self.db

        before_stats: dict[str, Any] = {}
        if tables in ("all", "payments"):
            if all_years:
                before_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
                before_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg")).scalar()
            else:
                before_stats["gap_payments"] = db.execute(
                    text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}
                ).scalar()
                try:
                    before_stats["gap_payments_agg"] = db.execute(
                        text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}
                    ).scalar()
                except Exception:  # noqa: BLE001 — View evtl. nicht vorhanden; nur Statistik
                    before_stats["gap_payments_agg"] = 0
        if tables in ("all", "snapshots"):
            before_stats["snapshots"] = db.execute(
                text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}
            ).scalar()
        if tables in ("all", "matches"):
            before_stats["matches"] = db.execute(
                text("SELECT COUNT(*) FROM gap_customer_match WHERE ref_year = :year"), {"year": year}
            ).scalar()

        deleted_counts: dict[str, Any] = {}
        if tables in ("all", "snapshots"):
            if all_years:
                deleted_counts["snapshots"] = db.execute(text("DELETE FROM customer_potential_snapshot")).rowcount
            else:
                deleted_counts["snapshots"] = db.execute(
                    text("DELETE FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}
                ).rowcount
        if tables in ("all", "matches"):
            if all_years:
                deleted_counts["matches"] = db.execute(text("DELETE FROM gap_customer_match")).rowcount
            else:
                deleted_counts["matches"] = db.execute(
                    text("DELETE FROM gap_customer_match WHERE ref_year = :year"), {"year": year}
                ).rowcount
        if tables in ("all", "payments"):
            if all_years:
                deleted_counts["gap_payments"] = db.execute(text("DELETE FROM gap_payments")).rowcount
                deleted_counts["reset_scope"] = "ALLE Jahre gelöscht"
            else:
                deleted_counts["gap_payments"] = db.execute(
                    text("DELETE FROM gap_payments WHERE ref_year = :year"), {"year": year}
                ).rowcount
                deleted_counts["reset_scope"] = f"Nur Jahr {year} gelöscht"
            deleted_counts["gap_payments_agg"] = "VIEW - automatisch aktualisiert"
            remaining = db.execute(
                text("SELECT ref_year, COUNT(*) FROM gap_payments GROUP BY ref_year ORDER BY ref_year")
            ).fetchall()
            deleted_counts["debug_remaining_years"] = [{"year": r[0], "count": r[1]} for r in remaining]

        db.commit()

        after_stats: dict[str, Any] = {}
        if tables in ("all", "payments"):
            if all_years:
                after_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
                after_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg")).scalar()
            else:
                after_stats["gap_payments"] = db.execute(
                    text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}
                ).scalar()
                try:
                    after_stats["gap_payments_agg"] = db.execute(
                        text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}
                    ).scalar()
                except Exception:  # noqa: BLE001 — View evtl. nicht vorhanden; nur Statistik
                    after_stats["gap_payments_agg"] = 0
        if tables in ("all", "snapshots"):
            if all_years:
                after_stats["snapshots"] = db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot")).scalar()
            else:
                after_stats["snapshots"] = db.execute(
                    text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}
                ).scalar()
        if tables in ("all", "matches"):
            if all_years:
                after_stats["matches"] = db.execute(text("SELECT COUNT(*) FROM gap_customer_match")).scalar()
            else:
                after_stats["matches"] = db.execute(
                    text("SELECT COUNT(*) FROM gap_customer_match WHERE ref_year = :year"), {"year": year}
                ).scalar()

        return {
            "success": True,
            "year": year,
            "tables_reset": tables,
            "deleted_counts": deleted_counts,
            "before_stats": before_stats,
            "after_stats": after_stats,
            "message": f"GAP-Daten-Reset erfolgreich abgeschlossen ({deleted_counts.get('reset_scope', f'Jahr {year}')})",
            "next_steps": [
                "Pipeline kann jetzt neu gestartet werden",
                "Alle Zähler sind auf 0 zurückgesetzt",
                "Frontend zeigt aktualisierte Werte",
            ],
        }
