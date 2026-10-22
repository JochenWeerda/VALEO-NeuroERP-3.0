"""GAP Pipeline API Endpoints.

Dünne Adapter-Schicht für die Ausführung der GAP-ETL-Pipeline über das Frontend.
Die gesamte Orchestrierung liegt in :class:`GapPipelineService`
(``app/services/gap_pipeline_service.py``); diese Datei kümmert sich nur um
Request-Parsing, Dependencies und Response-Modelle.

Nur die vom Frontend genutzten Endpunkte sind hier verfügbar; frühere
Debug-/Test-/Einmal-SQL-Sonden wurden entfernt.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.schemas.base import BaseSchema
from app.services.gap_pipeline_service import GapPipelineService


class GapOut(BaseSchema):
    """Typed response schema for GapOut endpoints (extra fields forwarded)."""

    model_config = ConfigDict(extra="allow")


router = APIRouter(prefix="/gap", tags=["gap", "prospecting"])


class GapPipelineRequest(BaseModel):
    """Request-Modell für GAP-Pipeline-Ausführung."""

    year: int
    csv_path: Optional[str] = None
    batch_id: Optional[str] = None


class GapPipelineResponse(BaseModel):
    """Response-Modell für GAP-Pipeline-Ausführung."""

    success: bool
    message: str
    job_id: Optional[str] = None


class PipelineProgressResponse(BaseModel):
    """Response-Modell für Pipeline-Progress."""

    job_id: str
    year: int
    current_step: str
    progress: int
    total_steps: int
    percentage: int
    message: str
    status: str  # running, completed, error
    updated_at: str
    steps: Dict[str, Dict[str, Any]]


# ── Pipeline-Ausführung ───────────────────────────────────────────────────────


@router.post("/pipeline/run-year", response_model=GapPipelineResponse, summary="Gap pipeline year ausführen")
async def run_gap_pipeline_year(
    request: GapPipelineRequest,
    plz_filter: Optional[str] = Query(None, description="PLZ-Filter (z.B. '26500-26999' oder '49,48')"),
):
    """Führt die komplette GAP-Pipeline für ein Jahr aus (optional PLZ-gefiltert)."""
    job_id, message = GapPipelineService().start_year_pipeline(
        year=request.year,
        csv_path=request.csv_path,
        batch_id=request.batch_id,
        plz_filter=plz_filter,
    )
    return GapPipelineResponse(success=True, message=message, job_id=job_id)


@router.post("/pipeline/import", response_model=GapPipelineResponse, summary="Gap import ausführen")
async def run_gap_import(request: GapPipelineRequest, background_tasks: BackgroundTasks):
    """Führt nur den GAP-Import aus."""
    message = GapPipelineService().queue_import(
        background_tasks,
        year=request.year,
        csv_path=request.csv_path,
        batch_id=request.batch_id,
    )
    return GapPipelineResponse(success=True, message=message)


@router.post("/pipeline/fetch-external", response_model=GapPipelineResponse, summary="Gap external abrufen")
async def fetch_gap_external(
    background_tasks: BackgroundTasks,
    year: int = Query(..., description="Jahr (z.B. 2024)"),
):
    """Lädt die GAP-Daten von agrarzahlungen.de herunter."""
    message = GapPipelineService().queue_external_download(background_tasks, year)
    return GapPipelineResponse(success=True, message=message)


@router.post("/pipeline/upload", response_model=GapOut, summary="Gap csv hochladen")
async def upload_gap_csv(
    file: UploadFile = File(..., description="GAP CSV-Datei"),
    year: Optional[int] = Query(None, description="Jahr (wird aus Dateiname extrahiert, falls nicht angegeben)"),
):
    """Lädt eine GAP-CSV-Datei hoch und speichert sie im data/gap-Verzeichnis."""
    return GapPipelineService.store_upload(file, year)


@router.get("/pipeline/status", response_model=GapOut, summary="Pipeline status abrufen")
async def get_pipeline_status(
    year: int = Query(..., description="Referenzjahr"),
    db: Session = Depends(get_db),
):
    """Prüft den Status der GAP-Pipeline für ein Jahr."""
    return GapPipelineService(db).pipeline_status(year)


@router.get("/pipeline/progress/{job_id}", response_model=PipelineProgressResponse, summary="Pipeline progress abrufen")
async def get_pipeline_progress(job_id: str):
    """Holt den aktuellen Fortschritt einer Pipeline-Ausführung."""
    progress_data = GapPipelineService.pipeline_progress(job_id)
    if not progress_data:
        raise HTTPException(status_code=404, detail=f"Kein Pipeline-Progress für Job-ID {job_id} gefunden")
    return PipelineProgressResponse(**progress_data)


@router.post("/pipeline/{command}", response_model=GapPipelineResponse, summary="Gap command ausführen")
async def run_gap_command(
    command: str,
    background_tasks: BackgroundTasks,
    year: int = Query(..., description="Referenzjahr"),
):
    """Führt einen einzelnen GAP-Pipeline-Befehl aus (aggregate/match/snapshot/hydrate-customers/import).

    Diese Catch-all-Route ist bewusst *nach* den spezifischen ``/pipeline/*``-Routen
    deklariert, damit z.B. ``/pipeline/upload`` nicht fälschlich hier landet.
    """
    message = GapPipelineService().queue_command(background_tasks, command, year)
    return GapPipelineResponse(success=True, message=message)


# ── Lead-Generierung (Komfort-Endpoint) ───────────────────────────────────────


@router.get("/leads/generate-from-gap", response_model=GapOut, summary="Leads from gap generieren")
async def generate_leads_from_gap(
    year: int = Query(2024, description="Referenzjahr (EU-GAP-Liste wird jährlich neu publiziert)"),
    plz_min: Optional[str] = Query(None, description="Min PLZ"),
    plz_max: Optional[str] = Query(None, description="Max PLZ"),
    min_potential_eur: int = Query(50, description="Mindest-Potenzial in EUR"),
    max_leads: int = Query(500, description="Maximale Anzahl Leads"),
    segment: Optional[str] = Query(None, description="Segment-Filter (A, B, C)"),
    db: Session = Depends(get_db),
):
    """Erstellt Kampagnen-Leads aus den GAP-Potenzial-Snapshots eines Jahres.

    Komfort-Direktzugang; die CRM-Maske (LeadExplorer) nutzt regulär
    ``/api/v1/prospecting/lead-candidates`` auf denselben Snapshot-Tabellen.
    """
    return GapPipelineService(db).generate_leads_from_snapshots(
        year=year,
        plz_min=plz_min,
        plz_max=plz_max,
        min_potential_eur=min_potential_eur,
        max_leads=max_leads,
        segment=segment,
    )


# ── Daten-Reset ───────────────────────────────────────────────────────────────


@router.delete("/reset-gap-data", response_model=GapOut, summary="Gap data zurücksetzen")
async def reset_gap_data(
    year: int = Query(2024, description="Jahr für Daten-Reset"),
    confirm: bool = Query(False, description="Bestätigung erforderlich"),
    tables: str = Query("all", description="Tabellen: all, payments, snapshots, matches"),
    all_years: bool = Query(False, description="Alle Jahre löschen statt nur ein Jahr"),
    db: Session = Depends(get_db),
):
    """Löscht GAP-Zahlungen, Snapshots und Matches für einen Neustart."""
    if not confirm:
        return {
            "success": False,
            "message": "Reset erfordert Bestätigung: ?confirm=true",
            "warning": "Diese Aktion löscht GAP-Daten unwiderruflich!",
            "available_tables": ["all", "payments", "snapshots", "matches"],
        }
    return GapPipelineService(db).reset_gap_data(year=year, tables=tables, all_years=all_years)
