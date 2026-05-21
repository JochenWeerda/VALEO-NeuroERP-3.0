"""
Lohn-Connector API – Lohn-Import-Läufe (LEXWARE / externe Lohnbuchhaltung).
CRUD für Import-Läufe, Handler zum Auslösen eines Imports (erzeugt Journal-Einträge oder markiert Run).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.fibu_audit import log_fibu_audit

router = APIRouter(prefix="/lohn-connector", tags=["finance", "lohn", "connectors"])


class LohnImportRunCreate(BaseModel):
    period: str = Field(..., description="Periode YYYY-MM")
    source: str = Field(default="LEXWARE", max_length=50)


class LohnImportRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    period: str
    source: str
    status: str
    journal_entry_count: int
    total_debit: Optional[Decimal] = None
    total_credit: Optional[Decimal] = None
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class LohnImportTrigger(BaseModel):
    period: str = Field(..., description="Periode YYYY-MM für Lohnabrechnung")
    dry_run: bool = Field(default=False, description="Nur Vorschau, keine Buchungen")


def _row_to_run(row) -> LohnImportRun:
    return LohnImportRun(
        id=row[0],
        tenant_id=row[1],
        period=row[2],
        source=row[3],
        status=row[4],
        journal_entry_count=row[5] or 0,
        total_debit=row[6],
        total_credit=row[7],
        message=row[8],
        created_at=row[9],
        updated_at=row[10],
        created_by=row[11],
    )


@router.get("/runs", response_model=List[LohnImportRun])
async def list_lohn_import_runs(
    tenant_id: str = Depends(get_tenant_id),
    period: Optional[str] = Query(None, description="Filter Periode YYYY-MM"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Liste aller Lohn-Import-Läufe des Mandanten."""
    q = """
        SELECT id, tenant_id, period, source, status, journal_entry_count,
               total_debit, total_credit, message, created_at, updated_at, created_by
        FROM domain_erp.lohn_import_runs
        WHERE tenant_id = :tenant_id
    """
    params: dict = {"tenant_id": tenant_id, "limit": limit, "skip": skip}
    if period:
        q += " AND period = :period"
        params["period"] = period
    q += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    rows = db.execute(text(q), params).fetchall()
    return [_row_to_run(r) for r in rows]


@router.get("/runs/{run_id}", response_model=LohnImportRun)
async def get_lohn_import_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelnen Lohn-Import-Lauf abrufen."""
    row = db.execute(
        text("""
            SELECT id, tenant_id, period, source, status, journal_entry_count,
                   total_debit, total_credit, message, created_at, updated_at, created_by
            FROM domain_erp.lohn_import_runs
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lohn-Import-Lauf nicht gefunden")
    return _row_to_run(row)


@router.post("/runs", response_model=LohnImportRun, status_code=201)
async def create_lohn_import_run(
    payload: LohnImportRunCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neuen Lohn-Import-Lauf anlegen (Status pending)."""
    if len(payload.period) != 7 or payload.period[4] != "-":
        raise HTTPException(status_code=400, detail="Periode muss YYYY-MM sein")
    run_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO domain_erp.lohn_import_runs
            (id, tenant_id, period, source, status, journal_entry_count, created_at, updated_at)
            VALUES (:id, :tenant_id, :period, :source, 'pending', 0, NOW(), NOW())
        """),
        {
            "id": run_id,
            "tenant_id": tenant_id,
            "period": payload.period,
            "source": payload.source,
        },
    )
    db.commit()
    row = db.execute(
        text("""
            SELECT id, tenant_id, period, source, status, journal_entry_count,
                   total_debit, total_credit, message, created_at, updated_at, created_by
            FROM domain_erp.lohn_import_runs WHERE id = :id
        """),
        {"id": run_id},
    ).fetchone()
    return _row_to_run(row)


@router.post("/runs/trigger", response_model=dict)
async def trigger_lohn_import(
    payload: LohnImportTrigger,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Lohn-Import auslösen (Stub: erstellt einen Run und optional eine Platzhalter-Buchung).
    In Produktion: Anbindung an LEXWARE/API oder Datei-Upload, dann Journal-Einträge erzeugen.
    """
    if len(payload.period) != 7 or payload.period[4] != "-":
        raise HTTPException(status_code=400, detail="Periode muss YYYY-MM sein")
    run_id = str(uuid4())
    status = "completed" if not payload.dry_run else "dry_run"
    journal_entry_count = 0
    total_debit = total_credit = None
    message = "Trockenlauf – keine Buchungen erstellt." if payload.dry_run else "Import ausgeführt (Stub: keine echten Buchungen)."
    if not payload.dry_run:
        journal_entry_count = 0
        message = "Lohn-Connector: Keine externen Daten angebunden. Bitte LEXWARE/Datei-Import konfigurieren."
    db.execute(
        text("""
            INSERT INTO domain_erp.lohn_import_runs
            (id, tenant_id, period, source, status, journal_entry_count, total_debit, total_credit, message, created_at, updated_at)
            VALUES (:id, :tenant_id, :period, 'LEXWARE', :status, :journal_entry_count, :total_debit, :total_credit, :message, NOW(), NOW())
        """),
        {
            "id": run_id,
            "tenant_id": tenant_id,
            "period": payload.period,
            "status": status,
            "journal_entry_count": journal_entry_count,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "message": message,
        },
    )
    db.commit()
    log_fibu_audit(
        db, tenant_id, "trigger", "lohn_import_run", run_id,
        {"period": payload.period, "dry_run": payload.dry_run, "status": status},
        request=None,
    )
    return {
        "run_id": run_id,
        "period": payload.period,
        "status": status,
        "journal_entry_count": journal_entry_count,
        "message": message,
    }


@router.delete("/runs/{run_id}", status_code=204, response_class=Response, response_model=None)
async def delete_lohn_import_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lohn-Import-Lauf löschen (nur pending)."""
    row = db.execute(
        text("SELECT id, status FROM domain_erp.lohn_import_runs WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lohn-Import-Lauf nicht gefunden")
    if row[1] != "pending":
        raise HTTPException(status_code=400, detail="Nur Läufe mit Status 'pending' können gelöscht werden.")
    db.execute(text("DELETE FROM domain_erp.lohn_import_runs WHERE id = :id AND tenant_id = :tenant_id"), {"id": run_id, "tenant_id": tenant_id})
    db.commit()
    return None
