"""
GAP Pipeline API Endpoints
Endpoints für die Ausführung der GAP-ETL-Pipeline über das Frontend
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
import shutil
import re
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, UploadFile, File, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/gap", tags=["gap", "prospecting"])


class GapPipelineRequest(BaseModel):
    """Request-Modell für GAP-Pipeline-Ausführung"""
    year: int
    csv_path: Optional[str] = None
    batch_id: Optional[str] = None


class GapPipelineResponse(BaseModel):
    """Response-Modell für GAP-Pipeline-Ausführung"""
    success: bool
    message: str
    job_id: Optional[str] = None


class PipelineProgressResponse(BaseModel):
    """Response-Modell für Pipeline-Progress"""
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


@router.post("/pipeline/run-year", response_model=GapPipelineResponse)
async def run_gap_pipeline_year(
    request: GapPipelineRequest,
    plz_filter: Optional[str] = Query(None, description="PLZ-Filter (z.B. '26500-26999' oder '49,48')"),
    background_tasks: BackgroundTasks = None
):
    """
    Führt die komplette GAP-Pipeline für ein Jahr aus.
    JETZT MIT PLZ-FILTER UNTERSTÜTZUNG!
    """
    try:
        # Erstelle Job-ID falls nicht vorhanden
        from app.services.gap_progress import create_pipeline_job
        job_id = request.batch_id or create_pipeline_job(request.year)
        
        # Parse PLZ-Filter falls vorhanden
        plz_list = None
        if plz_filter:
            plz_list = [plz.strip() for plz in plz_filter.split(",") if plz.strip()]
            print(f"[GAP API] PLZ-Filter aktiviert: {plz_list}")
        
        # Führe Pipeline im Hintergrund aus - mit PLZ-Filter!
        import threading
        pipeline_thread = threading.Thread(
            target=_execute_gap_pipeline_with_plz_filter,
            args=(request.year, request.csv_path, job_id, plz_list),
            daemon=True
        )
        pipeline_thread.start()
        
        filter_info = f" (PLZ-Filter: {plz_filter})" if plz_filter else ""
        print(f"[GAP API] Pipeline thread started for job_id={job_id}{filter_info}")
        
        return GapPipelineResponse(
            success=True,
            message=f"GAP-Pipeline für Jahr {request.year} wurde gestartet{filter_info}",
            job_id=job_id
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim Starten der Pipeline: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.post("/pipeline/run-year-optimized", response_model=GapPipelineResponse)
async def run_gap_pipeline_year_optimized(
    year: int,
    plz_filter: str = Query(..., description="Komma-getrennte PLZ-Bereiche (z.B. '49,48,59')"),
    csv_path: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Führt die OPTIMIERTE GAP-Pipeline für heiße PLZ-Bereiche aus.
    Extrem schnell durch PLZ-Filterung!
    """
    try:
        from app.services.gap_progress import create_pipeline_job
        
        # Parse PLZ-Filter
        plz_list = [plz.strip() for plz in plz_filter.split(",") if plz.strip()]
        if not plz_list:
            raise HTTPException(status_code=400, detail="PLZ-Filter darf nicht leer sein")
        
        job_id = create_pipeline_job(year)
        
        # Führe OPTIMIERTE Pipeline im Hintergrund aus
        import threading
        pipeline_thread = threading.Thread(
            target=_execute_gap_pipeline_optimized,
            args=(year, csv_path, job_id, plz_list),
            daemon=True
        )
        pipeline_thread.start()
        
        print(f"[GAP API OPTIMIZED] Pipeline thread started for job_id={job_id}, PLZ-Filter: {plz_list}")
        
        return GapPipelineResponse(
            success=True,
            message=f"OPTIMIERTE GAP-Pipeline für Jahr {year} gestartet (heiße Bereiche: {plz_filter})",
            job_id=job_id
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim Starten der optimierten Pipeline: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.post("/pipeline/run-year-filtered", response_model=GapPipelineResponse)
async def run_gap_pipeline_year_filtered(
    year: int,
    background_tasks: BackgroundTasks = None
):
    """
    🚀 Führt die ULTRA-OPTIMIERTE GAP-Pipeline für vorgefilterte PLZ 26XXX CSV aus.
    
    Diese Pipeline ist speziell für die vom User mit LibreOffice vorgefilterte 
    CSV-Datei optimiert, die Header enthält und nur PLZ 26XXX Daten umfasst.
    
    Eigenschaften:
    - Extrem schnell durch Vorfilterung
    - Header-basiertes CSV-Parsing
    - Intelligente Flächenprämien-Erkennung
    - Betriebsgrößen-Klassifizierung
    """
    try:
        from app.services.gap_progress import create_pipeline_job
        
        job_id = create_pipeline_job(year)
        
        # Führe ULTRA-OPTIMIERTE Pipeline im Hintergrund aus
        import threading
        pipeline_thread = threading.Thread(
            target=_execute_gap_pipeline_filtered,
            args=(year, job_id),
            daemon=True
        )
        pipeline_thread.start()
        
        print(f"🚀 [GAP API FILTERED] Pipeline thread started for job_id={job_id} (PLZ 26XXX)")
        
        return GapPipelineResponse(
            success=True,
            message=f"🚀 ULTRA-OPTIMIERTE GAP-Pipeline für Jahr {year} gestartet (PLZ 26XXX vorgefiltert)",
            job_id=job_id
        )
    
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim Starten der ultra-optimierten Pipeline: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.post("/pipeline/csv-streaming-test")
async def test_csv_streaming_pipeline(
    plz_filter: str = Query("49,48", description="PLZ-Bereiche für CSV-Streaming Test (z.B. '49,48')"),
    background_tasks: BackgroundTasks = None
):
    """
    📁 CSV-STREAMING Test - User's geniale Variante 3!
    Liest 113MB CSV Zeile für Zeile, kein RAM-Problem!
    """
    try:
        from app.services.gap_progress import create_pipeline_job
        
        # Parse PLZ-Filter
        plz_list = [plz.strip() for plz in plz_filter.split(",") if plz.strip()]
        job_id = create_pipeline_job(2024)
        
        # CSV-STREAMING Pipeline starten
        import threading
        pipeline_thread = threading.Thread(
            target=_execute_gap_pipeline_optimized,
            args=(2024, None, job_id, plz_list),
            daemon=True
        )
        pipeline_thread.start()
        
        return {
            "success": True,
            "message": f"📁 CSV-STREAMING Test gestartet für PLZ: {plz_filter}",
            "job_id": job_id,
            "expected_duration": "~5-10 Minuten (nicht Stunden!)",
            "plz_areas": plz_list,
            "method": "LINE_BY_LINE_CSV_STREAMING",
            "advantage": "Kein RAM-Problem bei 113MB CSV!"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV-Streaming Test Fehler: {str(e)}")


@router.post("/pipeline/import", response_model=GapPipelineResponse)
async def run_gap_import(
    request: GapPipelineRequest,
    background_tasks: BackgroundTasks
):
    """Führt nur den GAP-Import aus"""
    if not request.csv_path:
        # Versuche lokalen Standardpfad
        default_path = Path(f"data/gap/impdata{request.year}.csv")
        if default_path.exists():
             request.csv_path = str(default_path)
        else:
            # Check if it's a URL or non-existent path, the background task will handle or fail
            pass
    
    background_tasks.add_task(
        _execute_gap_command,
        command="import",
        year=request.year,
        csv_path=request.csv_path,
        batch_id=request.batch_id
    )
    
    return GapPipelineResponse(
        success=True,
        message=f"GAP-Import für Jahr {request.year} wurde gestartet"
    )


@router.post("/pipeline/fetch-external", response_model=GapPipelineResponse)
async def fetch_gap_external(
    year: int = Query(..., description="Jahr (z.B. 2024)"),
    background_tasks: BackgroundTasks = None
):
    """
    Lädt die GAP-Daten von agrarzahlungen.de herunter.
    """
    try:
        background_tasks.add_task(
            _execute_gap_download,
            year=year
        )
        return GapPipelineResponse(
            success=True,
            message=f"Download der GAP-Daten für Jahr {year} gestartet."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/{command}", response_model=GapPipelineResponse)
async def run_gap_command(
    command: str,
    year: int = Query(..., description="Referenzjahr"),
    background_tasks: BackgroundTasks = None
):
    """
    Führt einen einzelnen GAP-Pipeline-Befehl aus.
    """
    valid_commands = ["aggregate", "match", "snapshot", "hydrate-customers", "import"]
    if command not in valid_commands:
        raise HTTPException(
            status_code=400,
            detail=f"Ungültiger Command. Verfügbar: {', '.join(valid_commands)}"
        )
    
    # Special handling for 'import' if called via this endpoint (fallback)
    # Usually 'import' should go to /pipeline/import, but if matched here:
    csv_path = None
    if command == "import":
        # Try to find default CSV path
        default_path = Path(f"data/gap/impdata{year}.csv")
        if default_path.exists():
            csv_path = str(default_path)
    
    background_tasks.add_task(
        _execute_gap_command,
        command=command,
        year=year,
        csv_path=csv_path
    )
    
    return GapPipelineResponse(
        success=True,
        message=f"GAP-{command} für Jahr {year} wurde gestartet"
    )


@router.post("/pipeline/upload", response_model=dict)
async def upload_gap_csv(
    file: UploadFile = File(..., description="GAP CSV-Datei"),
    year: Optional[int] = Query(None, description="Jahr (wird aus Dateiname extrahiert, falls nicht angegeben)")
):
    """
    Lädt eine GAP-CSV-Datei hoch und speichert sie im data/gap-Verzeichnis.
    """
    try:
        # Jahr aus Dateiname extrahieren, falls nicht angegeben
        if year is None:
            if file.filename:
                year_match = re.search(r'(\d{4})', file.filename)
                if year_match:
                    year = int(year_match.group(1))
            
            # Fallback: Aktuelles Jahr verwenden
            if year is None:
                from datetime import datetime
                year = datetime.now().year
                print(f"[Upload] Kein Jahr angegeben, verwende aktuelles Jahr: {year}")

        # Validierung
        if year < 2020 or year > 2030:
            raise HTTPException(
                status_code=400,
                detail=f"Ungültiges Jahr: {year}. Muss zwischen 2020 und 2030 liegen."
            )
        
        # Zielpfad erstellen
        data_dir = Path("data/gap")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = data_dir / f"impdata{year}.csv"
        
        # Datei speichern
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = target_path.stat().st_size
        
        return {
            "success": True,
            "stored_path": str(target_path),
            "year": year,
            "filename": file.filename,
            "size_bytes": file_size,
            "message": f"Datei erfolgreich gespeichert: {target_path}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Hochladen der Datei: {str(e)}"
        )


@router.get("/pipeline/status")
async def get_pipeline_status(year: int = Query(..., description="Referenzjahr")):
    """
    Prüft den Status der GAP-Pipeline für ein Jahr.
    """
    from app.core.database import get_db
    
    db = next(get_db())
    
    try:
        # Prüfe gap_payments
        gap_count = db.execute(
            text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"),
            {"year": year}
        ).scalar()
        
        # Prüfe customer_potential_snapshot
        snapshot_count = db.execute(
            text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"),
            {"year": year}
        ).scalar()
        
        # Prüfe customers mit Analytics
        customer_count = db.execute(
            text("SELECT COUNT(*) FROM customers WHERE analytics_gap_ref_year = :year"),
            {"year": year}
        ).scalar()
        
        return {
            "year": year,
            "gap_payments_count": gap_count or 0,
            "snapshot_count": snapshot_count or 0,
            "customers_with_analytics_count": customer_count or 0,
            "pipeline_complete": (
                gap_count > 0 and
                snapshot_count > 0 and
                customer_count > 0
            )
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen des Status: {str(e)}"
        )


@router.get("/pipeline/progress/{job_id}", response_model=PipelineProgressResponse)
async def get_pipeline_progress(job_id: str):
    """
    Holt den aktuellen Fortschritt einer Pipeline-Ausführung
    """
    try:
        from app.services.gap_progress import get_pipeline_progress
        
        progress_data = get_pipeline_progress(job_id)
        
        if not progress_data:
            raise HTTPException(
                status_code=404,
                detail=f"Kein Pipeline-Progress für Job-ID {job_id} gefunden"
            )
        
        return PipelineProgressResponse(**progress_data)
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim Abrufen des Pipeline-Progress: {str(e)}\n{traceback.format_exc()}"
        print(f"[GAP Progress Error] {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.get("/pipeline/test-direct")
async def test_pipeline_direct():
    """
    Test-Endpoint: Führt Pipeline-Funktionen direkt aus (ohne Background-Task)
    """
    try:
        from app.services.gap_progress import create_pipeline_job, PipelineProgress
        
        year = 2024  # Festes Jahr für Test
        
        # Erstelle Job-ID
        job_id = create_pipeline_job(year)
        progress = PipelineProgress(job_id, year)
        
        # Sofortiger Test-Update
        progress.update_status("testing", 1, 6, "Direkter Test gestartet...", "running")
        
        # Test der Progress-Funktion
        test_progress = progress.get_status()
        
        return {
            "success": True,
            "job_id": job_id,
            "test_message": "Direkter Pipeline-Test erfolgreich",
            "progress_data": test_progress,
            "notes": "Dieser Endpoint testet die Progress-Mechanismen direkt"
        }
    
    except Exception as e:
        import traceback
        error_detail = f"Fehler beim direkten Pipeline-Test: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.get("/pipeline/simple-test")
async def simple_test():
    """
    ✅ SUPER-EINFACHER Test - nur zum Checken ob Server läuft
    """
    try:
        from app.services.gap_progress import create_pipeline_job
        job_id = create_pipeline_job(2024)
        
        return {
            "success": True,
            "message": "✅ Server läuft perfekt!",
            "job_id": job_id,
            "status": "Server antwortet korrekt",
            "timestamp": str(datetime.now())
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "❌ Server-Problem"
        }


@router.get("/pipeline/csv-check")
async def check_csv_file():
    """
    📁 Checkt ob CSV-Datei existiert und lesbar ist
    """
    try:
        import os
        from pathlib import Path
        
        # Suche nach CSV-Dateien
        possible_paths = [
            "data/gap/impdata2024.csv",
            "./impdata2024.csv", 
            "impdata2024.csv",
            "data/impdata2024.csv"
        ]
        
        found_files = []
        for path in possible_paths:
            if Path(path).exists():
                size = Path(path).stat().st_size
                found_files.append({
                    "path": str(path),
                    "size_mb": round(size / (1024*1024), 1),
                    "exists": True
                })
        
        return {
            "success": True,
            "found_files": found_files,
            "total_found": len(found_files),
            "message": f"📁 {len(found_files)} CSV-Dateien gefunden"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "❌ CSV-Check Fehler"
        }


@router.post("/pipeline/run-snapshot-manual")
async def run_snapshot_manual(
    year: int = Query(2024, description="Jahr für Snapshot-Erstellung")
):
    """
    🔧 MANUELLER SNAPSHOT-SCHRITT
    Führt den fehlgeschlagenen Snapshot-Schritt manuell aus
    """
    try:
        from app.services.gap_pipeline import run_snapshot
        
        print(f"[MANUAL SNAPSHOT] Starting manual snapshot for year {year}")
        
        # Führe Snapshot-Schritt aus
        result = run_snapshot(year)
        
        print(f"[MANUAL SNAPSHOT] Snapshot completed: {result}")
        
        return {
            "success": True,
            "result": result,
            "message": f"✅ Snapshot für Jahr {year} manuell erstellt",
            "snapshots_created": result.get('snapshot_count', 0)
        }
        
    except Exception as e:
        import traceback
        error_detail = f"Snapshot-Fehler: {str(e)}\n{traceback.format_exc()}"
        print(f"[MANUAL SNAPSHOT] Error: {error_detail}")
        
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": f"❌ Manueller Snapshot fehlgeschlagen: {str(e)}"
        }


@router.delete("/reset-gap-data")
async def reset_gap_data(
    year: int = Query(2024, description="Jahr für Daten-Reset"),
    confirm: bool = Query(False, description="Bestätigung erforderlich"),
    tables: str = Query("all", description="Tabellen: all, payments, snapshots, matches"),
    all_years: bool = Query(False, description="Alle Jahre löschen statt nur ein Jahr")
):
    """
    🗑️ GAP-DATEN-RESET: Löscht GAP-Zahlungen, Snapshots und Matches für Neustart
    """
    try:
        if not confirm:
            return {
                "success": False,
                "message": "❌ Reset erfordert Bestätigung: ?confirm=true",
                "warning": "Diese Aktion löscht GAP-Daten unwiderruflich!",
                "available_tables": ["all", "payments", "snapshots", "matches"]
            }
        
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Statistiken vor Reset
            before_stats = {}
            
            if tables in ["all", "payments"]:
                if all_years:
                    before_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
                    before_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg")).scalar()
                else:
                    before_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}).scalar()
                    # Prüfe VIEW-Daten (kann nicht gelöscht werden, aber für Statistik)
                    try:
                        before_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}).scalar()
                    except Exception:
                        before_stats["gap_payments_agg"] = 0
            
            if tables in ["all", "snapshots"]:
                before_stats["snapshots"] = db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}).scalar()
            
            if tables in ["all", "matches"]:
                before_stats["matches"] = db.execute(text("SELECT COUNT(*) FROM gap_customer_match WHERE ref_year = :year"), {"year": year}).scalar()
            
            # Reset durchführen
            deleted_counts = {}
            
            if tables in ["all", "snapshots"]:
                if all_years:
                    deleted_counts["snapshots"] = db.execute(text("DELETE FROM customer_potential_snapshot")).rowcount
                else:
                    deleted_counts["snapshots"] = db.execute(text("DELETE FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}).rowcount
            
            if tables in ["all", "matches"]:
                if all_years:
                    deleted_counts["matches"] = db.execute(text("DELETE FROM gap_customer_match")).rowcount
                else:
                    deleted_counts["matches"] = db.execute(text("DELETE FROM gap_customer_match WHERE ref_year = :year"), {"year": year}).rowcount
            
            if tables in ["all", "payments"]:
                # Lösche nur die Basis-Tabelle, der VIEW wird automatisch aktualisiert
                if all_years:
                    delete_result = db.execute(text("DELETE FROM gap_payments"))
                    deleted_counts["gap_payments"] = delete_result.rowcount
                    deleted_counts["reset_scope"] = "ALLE Jahre gelöscht"
                else:
                    delete_result = db.execute(text("DELETE FROM gap_payments WHERE ref_year = :year"), {"year": year})
                    deleted_counts["gap_payments"] = delete_result.rowcount
                    deleted_counts["reset_scope"] = f"Nur Jahr {year} gelöscht"
                
                # gap_payments_direct_agg ist ein VIEW und wird automatisch aktualisiert
                deleted_counts["gap_payments_agg"] = "VIEW - automatisch aktualisiert"
                
                # DEBUG: Prüfe auch andere Jahre NACH dem Delete
                other_years = db.execute(text("SELECT ref_year, COUNT(*) FROM gap_payments GROUP BY ref_year ORDER BY ref_year")).fetchall()
                deleted_counts["debug_remaining_years"] = [{"year": r[0], "count": r[1]} for r in other_years]
            
            db.commit()
            
            # Statistiken nach Reset
            after_stats = {}
            
            if tables in ["all", "payments"]:
                if all_years:
                    after_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
                    after_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg")).scalar()
                else:
                    after_stats["gap_payments"] = db.execute(text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}).scalar()
                    try:
                        after_stats["gap_payments_agg"] = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}).scalar()
                    except Exception:
                        after_stats["gap_payments_agg"] = 0
            
            if tables in ["all", "snapshots"]:
                if all_years:
                    after_stats["snapshots"] = db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot")).scalar()
                else:
                    after_stats["snapshots"] = db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}).scalar()
            
            if tables in ["all", "matches"]:
                if all_years:
                    after_stats["matches"] = db.execute(text("SELECT COUNT(*) FROM gap_customer_match")).scalar()
                else:
                    after_stats["matches"] = db.execute(text("SELECT COUNT(*) FROM gap_customer_match WHERE ref_year = :year"), {"year": year}).scalar()
                
        finally:
            db.close()
        
        return {
            "success": True,
            "year": year,
            "tables_reset": tables,
            "deleted_counts": deleted_counts,
            "before_stats": before_stats,
            "after_stats": after_stats,
            "message": f"✅ GAP-Daten-Reset erfolgreich abgeschlossen ({deleted_counts.get('reset_scope', f'Jahr {year}')})",
            "next_steps": [
                "Pipeline kann jetzt neu gestartet werden",
                "Alle Zähler sind auf 0 zurückgesetzt",
                "Frontend zeigt aktualisierte Werte"
            ]
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": f"❌ GAP-Daten-Reset fehlgeschlagen: {str(e)}"
        }


@router.get("/leads/generate-from-gap")
async def generate_leads_from_gap_frontend(
    year: int = Query(2024, description="Jahr für Lead-Generation"),
    plz_min: Optional[str] = Query(None, description="Min PLZ"),
    plz_max: Optional[str] = Query(None, description="Max PLZ"), 
    min_potential_eur: int = Query(50, description="Mindest-Potenzial in EUR"),
    max_leads: int = Query(500, description="Maximale Anzahl Leads"),
    segment: Optional[str] = Query(None, description="Segment Filter (A, B, C)")
):
    """
    🎯 FRONTEND-LEAD-GENERATION: Erstellt Leads aus GAP-Snapshots für Frontend
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # PLZ Filter aufbauen
            plz_filter = ""
            if plz_min and plz_max:
                plz_filter = f"AND c.postal_code BETWEEN '{plz_min}' AND '{plz_max}'"
            elif plz_min:
                plz_filter = f"AND c.postal_code >= '{plz_min}'"
            elif plz_max:
                plz_filter = f"AND c.postal_code <= '{plz_max}'"
            
            # Segment Filter
            segment_filter = ""
            if segment and segment in ['A', 'B', 'C']:
                segment_filter = f"AND s.segment = '{segment}'"
            
            # Leads aus Snapshots generieren
            leads_query = f"""
                SELECT 
                    s.customer_id,
                    c.name as customer_name,
                    c.postal_code,
                    c.city,
                    s.potential_total_eur,
                    s.gap_direct_total_eur,
                    s.gap_estimated_area_ha,
                    s.segment,
                    s.share_of_wallet_total_pct,
                    COALESCE(c.status, 'lead') as customer_status,
                    CASE 
                        WHEN s.potential_total_eur >= 100000 THEN 'Hoch'
                        WHEN s.potential_total_eur >= 50000 THEN 'Mittel'
                        ELSE 'Niedrig'
                    END as priority,
                    'GAP-Pipeline {year}' as lead_source,
                    'Landwirtschafts-Potenzial: ' || ROUND(s.potential_total_eur, 0) || ' EUR (' || ROUND(s.gap_estimated_area_ha, 1) || ' ha)' as description
                FROM customer_potential_snapshot s
                JOIN customers c ON c.id = s.customer_id
                WHERE s.ref_year = :year
                AND s.potential_total_eur >= :min_potential
                {plz_filter}
                {segment_filter}
                ORDER BY s.potential_total_eur DESC
                LIMIT :max_leads
            """
            
            result = db.execute(
                text(leads_query),
                {
                    "year": year,
                    "min_potential": min_potential_eur,
                    "max_leads": max_leads
                }
            ).fetchall()
            
            # Frontend-kompatible Lead-Struktur
            leads = []
            for row in result:
                lead = {
                    "id": f"gap_{year}_{row.customer_id}",
                    "customer_id": str(row.customer_id),
                    "name": row.customer_name,
                    "company": row.customer_name,
                    "postal_code": row.postal_code,
                    "city": row.city,
                    "potential_eur": float(row.potential_total_eur or 0),
                    "gap_amount_eur": float(row.gap_direct_total_eur or 0),
                    "estimated_hectares": float(row.gap_estimated_area_ha or 0),
                    "segment": row.segment or 'C',
                    "priority": row.priority,
                    "share_of_wallet_pct": float(row.share_of_wallet_total_pct or 0),
                    "source": row.lead_source,
                    "description": row.description,
                    "lead_type": "Agricultural GAP Lead",
                    "industry": "Agriculture",
                    "year": year,
                    "customer_status": row.customer_status,
                    "is_lead": row.customer_status in [None, 'lead'],
                    "is_customer": row.customer_status in ['active', 'inactive'],
                    "is_blocked": row.customer_status == 'blocked',
                    "created_from_gap": True,
                    "status": "lead" if row.customer_status in [None, 'lead'] else "customer"
                }
                leads.append(lead)
            
        finally:
            db.close()
        
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
                "segment": segment
            },
            "message": f"✅ {len(leads)} Landwirtschafts-Leads generiert" if len(leads) > 0 else "❌ Noch keine Landwirte verfügbar - Datenmigration erforderlich"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "leads": [],
            "total_leads": 0,
            "available_farmers": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "❌ Lead-Generation fehlgeschlagen - möglicherweise keine Snapshots verfügbar"
        }


@router.get("/leads/check-farmers-available")
async def check_farmers_available():
    """
    🚜 FARMERS-CHECK: Prüft ob Landwirte für Lead-Generation verfügbar sind
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Prüfe Snapshots
            snapshot_count = db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = 2024")).scalar()
            
            # Prüfe Landwirtschafts-Kunden (mit relevanten Namen)
            agro_customers = db.execute(text("""
                SELECT COUNT(*) FROM customers c
                WHERE EXISTS (
                    SELECT 1 FROM customer_potential_snapshot s 
                    WHERE s.customer_id = c.id AND s.ref_year = 2024
                )
            """)).scalar()
            
            # Sample Landwirte mit Status
            if snapshot_count > 0:
                sample_farmers = db.execute(text("""
                    SELECT 
                        c.name,
                        c.postal_code,
                        c.city,
                        s.potential_total_eur,
                        s.gap_estimated_area_ha,
                        COALESCE(c.status, 'lead') as status
                    FROM customer_potential_snapshot s
                    JOIN customers c ON c.id = s.customer_id
                    WHERE s.ref_year = 2024
                    ORDER BY s.potential_total_eur DESC
                    LIMIT 5
                """)).fetchall()
                
                farmers_list = [
                    {
                        "name": f.name,
                        "location": f"{f.postal_code} {f.city}",
                        "potential_eur": float(f.potential_total_eur),
                        "hectares": float(f.gap_estimated_area_ha or 0),
                        "status": f.status,
                        "is_lead": f.status in [None, 'lead'],
                        "is_customer": f.status in ['active', 'inactive']
                    } for f in sample_farmers
                ]
            else:
                farmers_list = []
            
        finally:
            db.close()
        
        return {
            "success": True,
            "farmers_available": snapshot_count > 0,
            "total_snapshots": snapshot_count,
            "agricultural_customers": agro_customers,
            "sample_farmers": farmers_list,
            "message": f"✅ {agro_customers} Landwirte verfügbar für Lead-Generation" if agro_customers > 0 else "❌ Noch keine Landwirte verfügbar - Datenmigration erforderlich"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "farmers_available": False,
            "error": str(e),
            "message": "❌ Farmers-Check fehlgeschlagen"
        }


@router.get("/test-view-direct")
async def test_view_direct(year: int = Query(2024, description="Jahr für View-Test")):
    """
    🔍 VIEW-DIAGNOSE: Direkter Test der gap_payments_direct_agg View
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Test 1: Basis-Tabelle gap_payments
            base_count = db.execute(text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}).scalar()
            
            # Test 2: View gap_payments_direct_agg
            try:
                view_count = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}).scalar()
                view_error = None
            except Exception as e:
                view_count = None
                view_error = str(e)
            
            # Test 3: Sample-Daten aus der View
            try:
                sample = db.execute(text("SELECT * FROM gap_payments_direct_agg WHERE ref_year = :year LIMIT 3"), {"year": year}).fetchall()
                sample_data = [dict(row._mapping) for row in sample] if sample else []
            except Exception as e:
                sample_data = f"Error: {str(e)}"
            
        finally:
            db.close()
        
        return {
            "success": True,
            "year": year,
            "diagnostics": {
                "base_table_count": base_count,
                "view_count": view_count,
                "view_error": view_error,
                "sample_data": sample_data
            },
            "analysis": {
                "base_has_data": base_count > 0,
                "view_accessible": view_error is None,
                "view_has_data": view_count and view_count > 0,
                "potential_issue": "View leer obwohl Basis-Tabelle Daten hat" if base_count > 0 and (not view_count or view_count == 0) else None
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.get("/check-measure-codes")
async def check_measure_codes(year: int = Query(2024, description="Jahr für Code-Check")):
    """
    🔍 MEASURE-CODES: Prüft welche measure_code Werte in den Daten vorhanden sind
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Alle verschiedenen measure_code Werte zählen
            codes = db.execute(text("""
                SELECT 
                    measure_code,
                    measure_description,
                    COUNT(*) as count
                FROM gap_payments 
                WHERE ref_year = :year
                GROUP BY measure_code, measure_description
                ORDER BY COUNT(*) DESC
                LIMIT 20
            """), {"year": year}).fetchall()
            
            code_list = [{"code": row[0], "description": row[1], "count": row[2]} for row in codes]
            
            # Prüfe ob die View-Filter-Codes vorhanden sind
            view_codes = ['I.1', 'I.2', 'I.3']
            present_view_codes = db.execute(text("""
                SELECT measure_code, COUNT(*) as count
                FROM gap_payments 
                WHERE ref_year = :year AND measure_code IN ('I.1', 'I.2', 'I.3')
                GROUP BY measure_code
            """), {"year": year}).fetchall()
            
            view_code_list = [{"code": row[0], "count": row[1]} for row in present_view_codes]
            
        finally:
            db.close()
        
        return {
            "success": True,
            "year": year,
            "total_records": sum(item["count"] for item in code_list),
            "all_measure_codes": code_list,
            "view_filter_codes": view_codes,
            "view_codes_in_data": view_code_list,
            "analysis": {
                "total_unique_codes": len(code_list),
                "view_codes_present": len(view_code_list) > 0,
                "view_code_count": sum(item["count"] for item in view_code_list),
                "problem": "View filtert Codes die nicht in den Daten sind" if len(view_code_list) == 0 else None
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.post("/fix-view-definition")
async def fix_view_definition():
    """
    🔧 VIEW-FIX: Erstellt die gap_payments_direct_agg View mit korrigiertem Filter neu
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Drop old view (falls vorhanden)
            db.execute(text("DROP VIEW IF EXISTS gap_payments_direct_agg"))
            
            # Create new view mit korrigiertem Filter
            view_sql = """
            CREATE OR REPLACE VIEW gap_payments_direct_agg AS
            SELECT
              ref_year,
              beneficiary_name_norm,
              postal_code,
              city,
              SUM(COALESCE(amount_total, 0)) as direct_total_eur
            FROM gap_payments
            WHERE measure_code IN ('I.1', 'I.2', 'I.3') OR measure_code IS NULL OR measure_code = ''
            GROUP BY ref_year, beneficiary_name_norm, postal_code, city
            """
            
            db.execute(text(view_sql))
            db.commit()
            
            # Test die neue View
            test_count = db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = 2024")).scalar()
            
        finally:
            db.close()
        
        return {
            "success": True,
            "message": "✅ View gap_payments_direct_agg erfolgreich neu erstellt",
            "view_definition": "Erweitert um leere measure_code Werte (NULL oder '')",
            "test_count_2024": test_count,
            "changes": [
                "Filter erweitert: measure_code IN ('I.1', 'I.2', 'I.3') OR measure_code IS NULL OR measure_code = ''",
                "Spalte geändert: amount_egfl → amount_total",
                "View neu erstellt mit korrigierter Definition"
            ]
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "❌ View-Fix fehlgeschlagen"
        }


@router.get("/debug-gap-years")
async def debug_gap_years():
    """
    🔍 DEBUG: Zeigt alle Jahre mit GAP-Daten und deren Anzahl
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Alle Jahre mit GAP-Daten finden
            years = db.execute(text("""
                SELECT 
                    ref_year,
                    COUNT(*) as count
                FROM gap_payments 
                GROUP BY ref_year 
                ORDER BY ref_year DESC
            """)).fetchall()
            
            year_data = [{"year": row[0], "count": row[1]} for row in years]
            
            # Total über alle Jahre
            total = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
            
        finally:
            db.close()
        
        return {
            "success": True,
            "years_with_data": year_data,
            "total_gap_payments": total,
            "message": f"📊 {len(year_data)} Jahre mit GAP-Daten gefunden"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.get("/gap-statistics")
async def get_gap_statistics(year: int = Query(2024, description="Jahr für Statistiken")):
    """
    📊 GAP-STATISTIKEN: Zeigt aktuelle Zähler für GAP-Daten
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Zähle alle relevanten Tabellen
            stats = {
                "gap_payments": db.execute(text("SELECT COUNT(*) FROM gap_payments WHERE ref_year = :year"), {"year": year}).scalar(),
                "gap_payments_agg": db.execute(text("SELECT COUNT(*) FROM gap_payments_direct_agg WHERE ref_year = :year"), {"year": year}).scalar(),
                "customer_matches": db.execute(text("SELECT COUNT(*) FROM gap_customer_match WHERE ref_year = :year"), {"year": year}).scalar(),
                "snapshots": db.execute(text("SELECT COUNT(*) FROM customer_potential_snapshot WHERE ref_year = :year"), {"year": year}).scalar(),
                "total_customers": db.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            }
            
            # Zusätzliche Informationen
            if stats["gap_payments_agg"] > 0:
                agg_info = db.execute(text("""
                    SELECT 
                        SUM(direct_total_eur) as total_amount_eur,
                        COUNT(DISTINCT beneficiary_name_norm) as unique_beneficiaries,
                        COUNT(DISTINCT postal_code) as unique_postal_codes
                    FROM gap_payments_direct_agg 
                    WHERE ref_year = :year
                """), {"year": year}).fetchone()
                
                stats.update({
                    "total_amount_eur": float(agg_info.total_amount_eur or 0),
                    "unique_beneficiaries": agg_info.unique_beneficiaries or 0,
                    "unique_postal_codes": agg_info.unique_postal_codes or 0
                })
                
        finally:
            db.close()
        
        return {
            "success": True,
            "year": year,
            "statistics": stats,
            "status": {
                "has_payments": stats["gap_payments"] > 0,
                "has_aggregations": stats["gap_payments_agg"] > 0,
                "has_matches": stats["customer_matches"] > 0,
                "has_snapshots": stats["snapshots"] > 0,
                "pipeline_complete": all([
                    stats["gap_payments"] > 0,
                    stats["gap_payments_agg"] > 0,
                    stats["customer_matches"] > 0,
                    stats["snapshots"] > 0
                ])
            },
            "message": f"📊 GAP-Statistiken für Jahr {year}"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": f"❌ GAP-Statistiken Abfrage fehlgeschlagen: {str(e)}"
        }


def _execute_gap_pipeline_optimized(year: int, csv_path: Optional[str] = None, batch_id: Optional[str] = None, plz_filter: Optional[List[str]] = None):
    """Führt die OPTIMIERTE GAP-Pipeline mit PLZ-Filter aus"""
    try:
        print(f"[GAP OPTIMIZED PIPELINE] === STARTING OPTIMIZED PIPELINE EXECUTION ===")
        print(f"[GAP OPTIMIZED PIPELINE] Year: {year}, CSV: {csv_path}, Batch-ID: {batch_id}, PLZ-Filter: {plz_filter}")
        
        from app.services.gap_progress import PipelineProgress
        from app.services.gap_pipeline import run_year_pipeline_optimized
        
        if not batch_id:
            print(f"[GAP OPTIMIZED PIPELINE] ERROR: No batch_id provided!")
            return
        
        progress = PipelineProgress(batch_id, year)
        progress.update_status("starting", 1, 6, f"OPTIMIERTE Pipeline für heiße Bereiche {plz_filter} gestartet...", "running")
        
        def progress_callback(step: str, step_num: int, message: str):
            try:
                print(f"[GAP OPTIMIZED PIPELINE] >>> Progress: {step} (step {step_num}) - {message}")
                progress.update_status(step, step_num, 6, message, "running")
            except Exception as callback_error:
                print(f"[GAP OPTIMIZED PIPELINE] Progress callback error: {callback_error}")
        
        # Führe optimierte Pipeline aus
        result = run_year_pipeline_optimized(year=year, csv_path=csv_path, batch_id=batch_id, plz_filter=plz_filter, progress_callback=progress_callback)
        
        progress.complete("OPTIMIERTE Pipeline erfolgreich abgeschlossen - nur heiße Bereiche verarbeitet!")
        print(f"[GAP OPTIMIZED PIPELINE] === OPTIMIZED PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"[GAP OPTIMIZED PIPELINE] Result: {result}")
        
    except Exception as e:
        try:
            from app.services.gap_progress import PipelineProgress
            if batch_id:
                progress = PipelineProgress(batch_id, year)
                error_msg = f"Optimierte Pipeline-Fehler: {str(e)}"
                progress.error(error_msg)
        except:
            pass
            
        print(f"[GAP OPTIMIZED PIPELINE] === OPTIMIZED PIPELINE FAILED ===")
        print(f"[GAP OPTIMIZED PIPELINE] Error: {str(e)}")
        import traceback
        print(f"[GAP OPTIMIZED PIPELINE] Full traceback: {traceback.format_exc()}")


def _execute_gap_pipeline_with_plz_filter(year: int, csv_path: Optional[str] = None, batch_id: Optional[str] = None, plz_filter: Optional[List[str]] = None):
    """Führt die GAP-Pipeline mit PLZ-Filter aus"""
    try:
        print(f"[GAP PIPELINE] === STARTING PIPELINE WITH PLZ FILTER ===")
        print(f"[GAP PIPELINE] Year: {year}, CSV: {csv_path}, Batch-ID: {batch_id}, PLZ-Filter: {plz_filter}")
        
        from app.services.gap_progress import PipelineProgress
        
        if not batch_id:
            print(f"[GAP PIPELINE] ERROR: No batch_id provided!")
            return
        
        progress = PipelineProgress(batch_id, year)
        
        filter_info = f" mit PLZ-Filter {plz_filter}" if plz_filter else ""
        progress.update_status("starting", 1, 6, f"Pipeline-Thread gestartet{filter_info}...", "running")
        print(f"[GAP PIPELINE] Initial progress update sent for batch_id={batch_id}")
        
        try:
            from app.services.gap_pipeline import run_year_pipeline
            print(f"[GAP PIPELINE] Successfully imported run_year_pipeline")
        except Exception as import_error:
            error_msg = f"Import-Fehler: {str(import_error)}"
            progress.error(error_msg)
            print(f"[GAP PIPELINE] IMPORT ERROR: {error_msg}")
            return
        
        def progress_callback(step: str, step_num: int, message: str):
            try:
                print(f"[GAP PIPELINE] >>> Progress callback: {step} (step {step_num}) - {message}")
                if step == "error":
                    progress.error(message)
                elif step == "completed":
                    progress.complete(message)
                else:
                    progress.update_status(step, step_num, 6, message, "running")
            except Exception as callback_error:
                print(f"[GAP PIPELINE] Progress callback error: {callback_error}")
                import traceback
                print(f"[GAP PIPELINE] Callback traceback: {traceback.format_exc()}")
        
        progress.update_status("initializing", 2, 6, "Initialisiere Pipeline-Parameter...", "running")
        print(f"[GAP PIPELINE] About to call run_year_pipeline with PLZ filter...")
        
        # WICHTIG: PLZ-Filter wird jetzt korrekt übergeben!
        result = run_year_pipeline(year=year, csv_path=csv_path, batch_id=batch_id, progress_callback=progress_callback, plz_filter=plz_filter)
        
        progress.complete(f"Pipeline erfolgreich abgeschlossen{filter_info}")
        print(f"[GAP PIPELINE] === PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"[GAP PIPELINE] Result: {result}")
        
    except Exception as e:
        try:
            from app.services.gap_progress import PipelineProgress
            if batch_id:
                progress = PipelineProgress(batch_id, year)
                error_msg = f"Pipeline-Fehler: {str(e)}"
                progress.error(error_msg)
        except:
            pass
            
        print(f"[GAP PIPELINE] === PIPELINE FAILED ===")
        print(f"[GAP PIPELINE] Error: {str(e)}")
        import traceback
        print(f"[GAP PIPELINE] Full traceback: {traceback.format_exc()}")


def _execute_gap_pipeline(year: int, csv_path: Optional[str] = None, batch_id: Optional[str] = None):
    """Führt die komplette GAP-Pipeline aus (Python-Implementierung)"""
    try:
        print(f"[GAP Pipeline] === STARTING PIPELINE EXECUTION ===")
        print(f"[GAP Pipeline] Year: {year}, CSV: {csv_path}, Batch-ID: {batch_id}")
        
        from app.services.gap_progress import PipelineProgress
        
        # Verwende existierende Batch-ID (wurde bereits von create_pipeline_job erstellt)
        if not batch_id:
            print(f"[GAP Pipeline] ERROR: No batch_id provided!")
            return
        
        progress = PipelineProgress(batch_id, year)
        
        # SOFORTIGER Progress-Update beim Start der Background-Task
        progress.update_status("starting", 1, 6, "Pipeline-Thread gestartet - beginne Ausführung...", "running")
        print(f"[GAP Pipeline] Initial progress update sent for batch_id={batch_id}")
        
        # Import der Pipeline-Funktionen hier (späte Bindung)
        try:
            from app.services.gap_pipeline import run_year_pipeline
            print(f"[GAP Pipeline] Successfully imported run_year_pipeline")
        except Exception as import_error:
            error_msg = f"Import-Fehler: {str(import_error)}"
            progress.error(error_msg)
            print(f"[GAP Pipeline] IMPORT ERROR: {error_msg}")
            return
        
        def progress_callback(step: str, step_num: int, message: str):
            try:
                print(f"[GAP Pipeline] >>> Progress callback: {step} (step {step_num}) - {message}")
                if step == "error":
                    progress.error(message)
                elif step == "completed":
                    progress.complete(message)
                else:
                    progress.update_status(step, step_num, 6, message, "running")
            except Exception as callback_error:
                print(f"[GAP Pipeline] Progress callback error: {callback_error}")
                import traceback
                print(f"[GAP Pipeline] Callback traceback: {traceback.format_exc()}")
        
        # Weitere Progress-Updates während der Ausführung
        progress.update_status("initializing", 2, 6, "Initialisiere Pipeline-Parameter...", "running")
        print(f"[GAP Pipeline] About to call run_year_pipeline...")
        
        # Pipeline ausführen
        result = run_year_pipeline(year=year, csv_path=csv_path, batch_id=batch_id, progress_callback=progress_callback)
        
        progress.complete("Pipeline erfolgreich abgeschlossen")
        print(f"[GAP Pipeline] === PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"[GAP Pipeline] Result: {result}")
        
    except Exception as e:
        try:
            from app.services.gap_progress import PipelineProgress
            if batch_id:
                progress = PipelineProgress(batch_id, year)
                error_msg = f"Pipeline-Fehler: {str(e)}"
                progress.error(error_msg)
        except:
            pass  # Fallback wenn Progress-Update fehlschlägt
            
        print(f"[GAP Pipeline] === PIPELINE FAILED ===")
        print(f"[GAP Pipeline] Error: {str(e)}")
        import traceback
        print(f"[GAP Pipeline] Full traceback: {traceback.format_exc()}")


def _execute_gap_download(year: int):
    from app.services.gap_pipeline import download_gap_csv
    try:
        path = download_gap_csv(year)
        print(f"[GAP Download] Erfolgreich: {path}")
    except Exception as e:
         print(f"[GAP Download] Fehler: {e}")


def _execute_gap_command(
    command: str,
    year: int,
    csv_path: Optional[str] = None,
    batch_id: Optional[str] = None
):
    """Führt einen einzelnen GAP-Command aus (Python-Implementierung)"""
    from app.services.gap_pipeline import (
        run_import,
        run_aggregate,
        run_match,
        run_snapshot,
        run_hydrate_customers
    )
    
    try:
        if command == "import":
            if not csv_path:
                # Wenn kein csv_path übergeben wurde, suche nach Standarddatei
                default_path = Path(f"data/gap/impdata{year}.csv")
                if default_path.exists():
                    csv_path = str(default_path)
                else:
                    # Wenn auch Standarddatei nicht existiert, versuche Download
                    try:
                        from app.services.gap_pipeline import download_gap_csv
                        csv_path = download_gap_csv(year)
                    except Exception as dl_err:
                        raise ValueError(f"csv_path ist erforderlich für Import und Download fehlgeschlagen: {dl_err}")

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
        
        print(f"[GAP Command] {command} erfolgreich für Jahr {year}: {result}")
    except Exception as e:
        print(f"[GAP Command] Fehler bei {command} für Jahr {year}: {str(e)}")
        import traceback
        print(traceback.format_exc())


@router.get("/search-krummhoern")
async def search_krummhoern(db: Session = Depends(get_db)):
    """🔍 Suche spezifisch nach PLZ 26736 Krummhörn - Test für Spaltenverschiebung"""
    try:
        # Direkte Suche nach PLZ 26736
        plz_26736 = db.execute(text("""
            SELECT beneficiary_name_norm, postal_code, city, eur_amount 
            FROM gap_payments 
            WHERE postal_code = '26736'
            LIMIT 10
        """)).fetchall()
        
        # Suche nach "Krummhörn" im Ortsnamen
        krummhoern_city = db.execute(text("""
            SELECT beneficiary_name_norm, postal_code, city, eur_amount 
            FROM gap_payments 
            WHERE UPPER(city) LIKE '%KRUMM%' OR UPPER(city) LIKE '%HÖRN%'
            LIMIT 10
        """)).fetchall()
        
        # Suche nach "Krummhörn" in Begünstigten-Namen
        krummhoern_names = db.execute(text("""
            SELECT beneficiary_name_norm, postal_code, city, eur_amount 
            FROM gap_payments 
            WHERE UPPER(beneficiary_name_norm) LIKE '%KRUMM%'
            LIMIT 10
        """)).fetchall()
        
        # Breite Suche im PLZ-Bereich 267xx
        plz_267xx = db.execute(text("""
            SELECT postal_code, COUNT(*) as count
            FROM gap_payments 
            WHERE postal_code LIKE '267%'
            GROUP BY postal_code
            ORDER BY postal_code
        """)).fetchall()
        
        # Alle verfügbaren PLZ in der Nähe von 26736
        nearby_plz = db.execute(text("""
            SELECT postal_code, city, COUNT(*) as count
            FROM gap_payments 
            WHERE postal_code BETWEEN '26730' AND '26740'
            GROUP BY postal_code, city
            ORDER BY postal_code
        """)).fetchall()
        
        return {
            "search_results": {
                "plz_26736_exact": [
                    {
                        "name": row[0], 
                        "plz": row[1], 
                        "city": row[2], 
                        "amount": str(row[3])
                    } 
                    for row in plz_26736
                ],
                "krummhoern_by_city": [
                    {
                        "name": row[0], 
                        "plz": row[1], 
                        "city": row[2], 
                        "amount": str(row[3])
                    } 
                    for row in krummhoern_city
                ],
                "krummhoern_by_name": [
                    {
                        "name": row[0], 
                        "plz": row[1], 
                        "city": row[2], 
                        "amount": str(row[3])
                    } 
                    for row in krummhoern_names
                ],
                "plz_267xx_distribution": [
                    {"plz": row[0], "count": row[1]} 
                    for row in plz_267xx
                ],
                "nearby_plz_26730_26740": [
                    {"plz": row[0], "city": row[1], "count": row[2]} 
                    for row in nearby_plz
                ]
            },
            "analysis": {
                "found_exact_26736": len(plz_26736) > 0,
                "found_krummhoern_city": len(krummhoern_city) > 0,
                "found_krummhoern_names": len(krummhoern_names) > 0,
                "plz_267xx_count": len(plz_267xx),
                "nearby_plz_count": len(nearby_plz)
            }
        }
        
    except Exception as e:
        return {"error": str(e), "details": "Fehler bei Krummhörn-Suche"}


@router.get("/analyze-csv-structure")
async def analyze_csv_structure():
    """🔍 Direkte CSV-Struktur-Analyse für Spaltenverschiebungs-Diagnose"""
    try:
        import os
        import csv
        from pathlib import Path
        
        # Mögliche CSV-Pfade
        csv_paths = [
            "data/gap/impdata2024.csv",
            "./impdata2024.csv",
            "/app/data/gap/impdata2024.csv",
            "impdata2024.csv",
            "data/impdata2024.csv"
        ]
        
        analysis_result = {
            "csv_search": {
                "searched_paths": csv_paths,
                "found_path": None,
                "file_exists": False
            },
            "header_analysis": None,
            "sample_data": None,
            "krummhoern_analysis": None
        }
        
        # Suche nach CSV-Datei
        csv_path = None
        for path in csv_paths:
            if os.path.exists(path):
                csv_path = path
                analysis_result["csv_search"]["found_path"] = path
                analysis_result["csv_search"]["file_exists"] = True
                break
        
        if not csv_path:
            # Versuche alle CSV-Dateien zu finden
            try:
                all_csvs = []
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file.endswith('.csv'):
                            all_csvs.append(os.path.join(root, file))
                
                analysis_result["csv_search"]["all_csv_files_found"] = all_csvs[:10]  # Erste 10
                
                # Nimm die erste gefundene CSV als Test
                if all_csvs:
                    csv_path = all_csvs[0]
                    analysis_result["csv_search"]["using_first_found"] = csv_path
                    
            except Exception as e:
                analysis_result["csv_search"]["search_error"] = str(e)
        
        if csv_path and os.path.exists(csv_path):
            try:
                # CSV-Header analysieren
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    # Teste verschiedene Delimiter
                    delimiters = [';', ',', '\t', '|']
                    
                    for delimiter in delimiters:
                        f.seek(0)  # Reset file pointer
                        try:
                            reader = csv.DictReader(f, delimiter=delimiter)
                            headers = reader.fieldnames
                            
                            if headers and len(headers) > 5:  # Sinnvolle Header-Anzahl
                                analysis_result["header_analysis"] = {
                                    "delimiter_used": delimiter,
                                    "total_headers": len(headers),
                                    "all_headers": headers,
                                    "plz_like_headers": [h for h in headers if h and ('plz' in h.lower() or 'post' in h.lower() or 'zip' in h.lower())],
                                    "name_like_headers": [h for h in headers if h and ('name' in h.lower() or 'begün' in h.lower() or 'benefi' in h.lower())],
                                    "city_like_headers": [h for h in headers if h and ('ort' in h.lower() or 'stadt' in h.lower() or 'gemeinde' in h.lower() or 'city' in h.lower())]
                                }
                                
                                # Sample-Daten lesen
                                f.seek(0)
                                reader = csv.DictReader(f, delimiter=delimiter)
                                sample_rows = []
                                
                                for i, row in enumerate(reader):
                                    if i >= 3:  # Erste 3 Zeilen
                                        break
                                    sample_rows.append({
                                        "row_number": i + 1,
                                        "sample_data": dict(list(row.items())[:10])  # Erste 10 Spalten
                                    })
                                
                                analysis_result["sample_data"] = sample_rows
                                
                                # Krummhörn-Suche in CSV
                                f.seek(0)
                                reader = csv.DictReader(f, delimiter=delimiter)
                                krummhoern_found = []
                                
                                row_count = 0
                                for row in reader:
                                    row_count += 1
                                    if row_count > 1000:  # Maximal 1000 Zeilen durchsuchen
                                        break
                                        
                                    # Suche nach PLZ 26736 oder "Krummhörn" in allen Spalten
                                    for key, value in row.items():
                                        if value and (
                                            '26736' in str(value) or 
                                            'krumm' in str(value).lower() or 
                                            'hörn' in str(value).lower()
                                        ):
                                            krummhoern_found.append({
                                                "row_number": row_count,
                                                "found_in_column": key,
                                                "found_value": str(value)[:100],  # Erste 100 Zeichen
                                                "full_row_sample": dict(list(row.items())[:5])  # Erste 5 Spalten
                                            })
                                            
                                            if len(krummhoern_found) >= 10:  # Max 10 Treffer
                                                break
                                
                                analysis_result["krummhoern_analysis"] = {
                                    "total_rows_searched": row_count,
                                    "krummhoern_matches_found": len(krummhoern_found),
                                    "matches": krummhoern_found
                                }
                                
                                break  # Erfolgreicher Delimiter gefunden
                                
                        except Exception as e:
                            continue  # Nächsten Delimiter probieren
                            
            except Exception as e:
                analysis_result["csv_error"] = str(e)
        
        return analysis_result
        
    except Exception as e:
        return {"error": str(e), "details": "Fehler bei CSV-Struktur-Analyse"}


@router.get("/search-krummhoern-csv")
async def search_krummhoern_csv():
    """🔍 Direkte Suche nach Krummhörn in CSV mit korrigiertem Typo"""
    try:
        import csv
        import os
        
        csv_path = "data/gap/impdata2024.csv"
        
        if not os.path.exists(csv_path):
            return {"error": f"CSV-Datei nicht gefunden: {csv_path}"}
        
        results = {
            "csv_file": csv_path,
            "search_results": {
                "plz_26736_matches": [],
                "krummhoern_matches": [],
                "plz_267xx_matches": [],
                "header_analysis": None
            },
            "statistics": {
                "total_rows_scanned": 0,
                "plz_26736_count": 0,
                "krummhoern_count": 0,
                "plz_267xx_count": 0
            }
        }
        
        # CSV mit korrektem Typo lesen
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header analysieren
            headers = reader.fieldnames
            results["search_results"]["header_analysis"] = {
                "total_headers": len(headers) if headers else 0,
                "headers": headers,
                "name_header": None,
                "plz_header": None,
                "city_header": None
            }
            
            # Korrekte Header identifizieren (mit Typo!)
            for header in (headers or []):
                if 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                    results["search_results"]["header_analysis"]["name_header"] = header
                elif header.strip() == 'PLZ':
                    results["search_results"]["header_analysis"]["plz_header"] = header
                elif 'gemeinde' in header.lower():
                    results["search_results"]["header_analysis"]["city_header"] = header
            
            # Daten durchsuchen
            for row_num, row in enumerate(reader, 1):
                results["statistics"]["total_rows_scanned"] = row_num
                
                # Maximal 10.000 Zeilen scannen für Performance
                if row_num > 10000:
                    break
                    
                plz = row.get('PLZ', '').strip()
                name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()  # MIT TYPO!
                city = row.get('Gemeinde', '').strip()
                
                # Suche nach PLZ 26736
                if plz == '26736':
                    results["statistics"]["plz_26736_count"] += 1
                    if len(results["search_results"]["plz_26736_matches"]) < 10:
                        results["search_results"]["plz_26736_matches"].append({
                            "row": row_num,
                            "name": name,
                            "plz": plz,
                            "city": city,
                            "egfl_amount": row.get('EGFL- Gesamtbetrag für diesen Begünstigten', '')
                        })
                
                # Suche nach Krummhörn
                if ('krumm' in name.lower() or 'krumm' in city.lower() or 
                    'hörn' in name.lower() or 'hörn' in city.lower()):
                    results["statistics"]["krummhoern_count"] += 1
                    if len(results["search_results"]["krummhoern_matches"]) < 10:
                        results["search_results"]["krummhoern_matches"].append({
                            "row": row_num,
                            "name": name,
                            "plz": plz,
                            "city": city,
                            "match_type": "krummhörn_text"
                        })
                
                # Suche nach PLZ 267xx Bereich
                if plz.startswith('267'):
                    results["statistics"]["plz_267xx_count"] += 1
                    if len(results["search_results"]["plz_267xx_matches"]) < 20:
                        results["search_results"]["plz_267xx_matches"].append({
                            "row": row_num,
                            "name": name[:50],  # Erste 50 Zeichen
                            "plz": plz,
                            "city": city
                        })
        
        return results
        
    except Exception as e:
        import traceback
        return {
            "error": str(e), 
            "details": "Fehler bei Krummhörn-CSV-Suche",
            "traceback": traceback.format_exc()
        }


@router.get("/simple-plz-check")
async def simple_plz_check(db: Session = Depends(get_db)):
    """🔍 Einfacher Check der PLZ-Daten ohne komplexe Queries"""
    try:
        # Sehr einfache Abfragen
        total_count = db.execute(text("SELECT COUNT(*) FROM gap_payments")).scalar()
        
        # PLZ 26xxx speziell prüfen  
        plz_26_count = db.execute(text("SELECT COUNT(*) FROM gap_payments WHERE postal_code LIKE '26%'")).scalar()
        
        # Erste 3 Datensätze komplett anzeigen
        sample = db.execute(text("""
            SELECT beneficiary_name_norm, postal_code, city, eur_amount 
            FROM gap_payments 
            LIMIT 3
        """)).fetchall()
        
        # PLZ-Verteilung grob  
        plz_stats = db.execute(text("""
            SELECT 
                CASE 
                    WHEN postal_code LIKE '26%' THEN '26xxx'
                    WHEN postal_code LIKE '01%' THEN '01xxx' 
                    WHEN postal_code LIKE '10%' THEN '10xxx'
                    ELSE 'other'
                END as plz_group,
                COUNT(*) as count
            FROM gap_payments 
            WHERE postal_code IS NOT NULL
            GROUP BY plz_group
            ORDER BY count DESC
        """)).fetchall()
        
        return {
            "total_records": total_count,
            "plz_26_count": plz_26_count,
            "sample_records": [
                {
                    "name": row[0], 
                    "plz": row[1], 
                    "city": row[2], 
                    "amount": str(row[3])
                } 
                for row in sample
            ],
            "plz_distribution": [
                {"group": row[0], "count": row[1]} 
                for row in plz_stats
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/debug-plz-data")
async def debug_plz_data(db: Session = Depends(get_db)):
    """🔍 Debug endpoint to analyze postal code data distribution"""
    try:
        # PLZ-Verteilung analysieren
        plz_analysis = db.execute(text("""
            SELECT 
                SUBSTRING(postal_code, 1, 2) as plz_prefix,
                COUNT(*) as count,
                MIN(postal_code) as min_plz,
                MAX(postal_code) as max_plz
            FROM gap_payments 
            WHERE postal_code IS NOT NULL 
            AND postal_code != ''
            AND LENGTH(postal_code) >= 2
            GROUP BY SUBSTRING(postal_code, 1, 2)
            ORDER BY plz_prefix
        """)).fetchall()
        
        # Spezifische Analyse für PLZ 26xxx
        plz_26_data = db.execute(text("""
            SELECT 
                beneficiary_name_norm, 
                postal_code, 
                city, 
                eur_amount,
                ref_year
            FROM gap_payments 
            WHERE postal_code LIKE '26%' 
            LIMIT 10
        """)).fetchall()
        
        # Sample der ersten 5 Datensätze zur Überprüfung der Spaltenreihenfolge
        sample_data = db.execute(text("""
            SELECT 
                beneficiary_name_norm, 
                postal_code, 
                city, 
                eur_amount,
                measure_code,
                ref_year
            FROM gap_payments 
            LIMIT 5
        """)).fetchall()
        
        # CSV-Header analysieren
        csv_header_analysis = None
        try:
            import os
            import csv
            from pathlib import Path
            
            csv_paths = [
                "data/gap/impdata2024.csv",
                "./impdata2024.csv",
                "/app/data/gap/impdata2024.csv"
            ]
            
            csv_path = None
            for path in csv_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if csv_path:
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    csv_headers = reader.fieldnames
                    
                    # Erste 3 Zeilen als Sample
                    sample_rows = []
                    for i, row in enumerate(reader):
                        if i >= 3:
                            break
                        sample_rows.append(dict(row))
                    
                    csv_header_analysis = {
                        "csv_found": True,
                        "headers": csv_headers,
                        "header_count": len(csv_headers) if csv_headers else 0,
                        "sample_rows": sample_rows,
                        "plz_columns": [h for h in (csv_headers or []) if 'plz' in h.lower() or 'post' in h.lower()],
                        "name_columns": [h for h in (csv_headers or []) if 'name' in h.lower() or 'begün' in h.lower()]
                    }
            else:
                csv_header_analysis = {"csv_found": False, "searched_paths": csv_paths}
                
        except Exception as e:
            csv_header_analysis = {"csv_error": str(e)}

        return {
            "csv_analysis": csv_header_analysis,
            "plz_distribution": [
                {
                    "prefix": row[0],
                    "count": row[1], 
                    "min_plz": row[2],
                    "max_plz": row[3]
                }
                for row in plz_analysis
            ],
            "plz_26_samples": [
                {
                    "beneficiary": row[0],
                    "postal_code": row[1],
                    "city": row[2],
                    "amount": str(row[3]),
                    "ref_year": row[4]
                }
                for row in plz_26_data
            ],
            "sample_data": [
                {
                    "beneficiary": row[0],
                    "postal_code": row[1],
                    "city": row[2],
                    "amount": str(row[3]),
                    "measure_code": row[4],
                    "ref_year": row[5]
                }
                for row in sample_data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _execute_gap_pipeline_filtered(year: int, batch_id: Optional[str] = None):
    """🚀 Führt die ULTRA-OPTIMIERTE GAP-Pipeline für vorgefilterte PLZ 26XXX CSV aus"""
    try:
        print(f"🚀 [GAP FILTERED PIPELINE] === STARTING ULTRA-OPTIMIZED PIPELINE EXECUTION ===")
        print(f"🚀 [GAP FILTERED PIPELINE] Year: {year}, Batch-ID: {batch_id} (PLZ 26XXX Vorgefiltert)")
        
        from app.services.gap_progress import PipelineProgress
        from app.services.gap_pipeline import run_year_pipeline_filtered
        
        if not batch_id:
            print(f"🚀 [GAP FILTERED PIPELINE] ERROR: No batch_id provided!")
            return
        
        progress = PipelineProgress(batch_id, year)
        progress.update_status("starting", 1, 6, f"🎯 ULTRA-OPTIMIERTE Pipeline für PLZ 26XXX gestartet...", "running")
        
        def progress_callback(step: str, step_num: int, message: str):
            try:
                print(f"🚀 [GAP FILTERED PIPELINE] >>> Progress: {step} (step {step_num}) - {message}")
                progress.update_status(step, step_num, 6, message, "running")
            except Exception as callback_error:
                print(f"🚀 [GAP FILTERED PIPELINE] Progress callback error: {callback_error}")
        
        # Führe ultra-optimierte Pipeline aus
        result = run_year_pipeline_filtered(year=year, progress_callback=progress_callback)
        
        if result.get("success", False):
            summary = result.get("summary", {})
            completion_msg = f"🎉 ULTRA-OPTIMIERTE Pipeline erfolgreich abgeschlossen! {summary.get('total_payments', 0):,} Zahlungen in {summary.get('duration_seconds', 0):.1f}s verarbeitet"
            progress.complete(completion_msg)
            print(f"🚀 [GAP FILTERED PIPELINE] === ULTRA-OPTIMIZED PIPELINE COMPLETED SUCCESSFULLY ===")
        else:
            error_msg = result.get("error", "Unbekannter Fehler")
            progress.error(f"Pipeline-Fehler: {error_msg}")
            print(f"🚀 [GAP FILTERED PIPELINE] ERROR: {error_msg}")
        
        return result
        
    except Exception as e:
        import traceback
        error_message = f"ULTRA-OPTIMIZED Pipeline execution failed: {str(e)}"
        print(f"🚀 [GAP FILTERED PIPELINE] ERROR: {error_message}")
        print(f"🚀 [GAP FILTERED PIPELINE] Traceback: {traceback.format_exc()}")
        
        if 'progress' in locals():
            progress.error(f"Pipeline-Fehler: {error_message}")
        
        return {"error": error_message}
