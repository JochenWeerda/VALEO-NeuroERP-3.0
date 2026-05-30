from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.compliance_whistleblower_schemas import ComplianceWhistleblowerOut


router = APIRouter()

_TABLE = "domain_compliance.whistleblower_reports"


def _ensure_table(db: Session) -> None:
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS domain_compliance.whistleblower_reports (
                id TEXT PRIMARY KEY,
                report_token TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                description_encrypted TEXT,
                severity TEXT DEFAULT 'MITTEL',
                status TEXT DEFAULT 'EINGEGANGEN',
                submitted_at TIMESTAMPTZ DEFAULT NOW(),
                notes JSONB DEFAULT '[]'
            )
        """))
        db.commit()
    except Exception:
        db.rollback()


class ReportIn(BaseModel):
    category: str  # BETRUG/BESTECHUNG/DISKRIMINIERUNG/SICHERHEIT/DATENSCHUTZ/SONSTIGE
    description: str
    severity: str = "MITTEL"


class NoteIn(BaseModel):
    note: str
    new_status: Optional[str] = None


@router.post("/reports", status_code=201, summary="Report einreichen",
    response_model=ComplianceWhistleblowerOut
)
async def submit_report(payload: ReportIn, db: Session = Depends(get_db)):
    _ensure_table(db)
    report_id = str(uuid4())
    token = secrets.token_urlsafe(9)[:12].upper()
    try:
        db.execute(text("""
            INSERT INTO domain_compliance.whistleblower_reports (id, report_token, category, description_encrypted, severity)
            VALUES (:id, :token, :cat, :desc, :sev)
        """), {"id": report_id, "token": token, "cat": payload.category,
               "desc": payload.description, "sev": payload.severity})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(503, f"Datenbank nicht erreichbar: {e}")
    return {
        "token": token,
        "message": "Ihr Hinweis wurde vertraulich erfasst. Bewahren Sie den Token zur Rückmeldung auf.",
    }


@router.get("/reports/status/{token}", summary="Status report",
    response_model=ComplianceWhistleblowerOut
)
async def report_status(token: str, db: Session = Depends(get_db)):
    _ensure_table(db)
    try:
        row = db.execute(
            text("SELECT status, submitted_at FROM domain_compliance.whistleblower_reports WHERE report_token = :token"),
            {"token": token},
        ).fetchone()
    except Exception:
        raise HTTPException(503, "Datenbank nicht erreichbar")
    if not row:
        raise HTTPException(404, "Token nicht gefunden")
    return {"status": row.status, "submitted_at": str(row.submitted_at)}


@router.get("/reports", summary="Reports auflisten",
    response_model=list[ComplianceWhistleblowerOut]
)
async def list_reports(db: Session = Depends(get_db)):
    _ensure_table(db)
    try:
        rows = db.execute(
            text("SELECT id, category, severity, status, submitted_at FROM domain_compliance.whistleblower_reports ORDER BY submitted_at DESC")
        ).fetchall()
    except Exception:
        raise HTTPException(503, "Datenbank nicht erreichbar")
    return [dict(r._mapping) for r in rows]


@router.patch("/reports/{report_id}/update", summary="Report aktualisieren",
    response_model=ComplianceWhistleblowerOut
)
async def update_report(report_id: str, payload: NoteIn, db: Session = Depends(get_db)):
    _ensure_table(db)
    try:
        if payload.new_status:
            db.execute(
                text("UPDATE domain_compliance.whistleblower_reports SET status = :st WHERE id = :id"),
                {"st": payload.new_status, "id": report_id},
            )
        db.execute(
            text("""
                UPDATE domain_compliance.whistleblower_reports
                SET notes = notes || :note::jsonb
                WHERE id = :id
            """),
            {"note": f'[{{"note": "{payload.note}", "ts": "{datetime.now(timezone.utc).isoformat()}"}}]',
             "id": report_id},
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(503, str(e))
    return {"updated": True}
