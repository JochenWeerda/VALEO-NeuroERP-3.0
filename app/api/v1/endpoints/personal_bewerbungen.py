"""Bewerbermanagement — die Recruiting-Pipeline.

Herausgenommen aus `personal.py` am 06.10.2026: Die Datei stand mit 3315 Zeilen
in der Godfile-Ratsche und wuchs auf 3342. Die Naht lag schon da — das
Bewerbermanagement teilt mit der Personalverwaltung nur den Prefix.

Der Code ist **unveraendert** uebernommen. Eine Zerlegung ist keine Gelegenheit,
Verhalten zu aendern; was hier noch zu tun ist, steht in
``docs/quality-assurance/personal-zerlegung-20261006.md``.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.personal_schemas import PersonalOut
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/personal", tags=["personal", "hr", "recruiting"])


APPLICATION_STAGES = {"EINGANG", "VORAUSWAHL", "ERSTGESPRAECH", "ENDGESPRAECH", "ANGEBOT", "EINGESTELLT", "ABGELEHNT"}


class ApplicationIn(BaseModel):
    applicant_name: str = Field(..., max_length=200)
    applicant_email: str = Field(..., max_length=200)
    position_id: str | None = None
    position_title: str | None = Field(default=None, max_length=200)
    source: str | None = Field(default=None, max_length=80)
    documents_ref: str | None = None


class ApplicationStagePatch(BaseModel):
    stage: str = Field(..., description="EINGANG/VORAUSWAHL/ERSTGESPRAECH/ENDGESPRAECH/ANGEBOT/EINGESTELLT/ABGELEHNT")
    note: str | None = None


@router.get("/applications", summary="Applications auflisten",
    response_model=list[PersonalOut]
)
async def list_applications(
    status: str | None = Query(None),
    position_id: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bewerbungen auflisten, optional nach Status oder Stelle filtern."""
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status
    if position_id:
        where.append("position_id = :position_id")
        params["position_id"] = position_id
    where_sql = " AND ".join(where)
    try:
        rows = db.execute(
            text(f"SELECT * FROM domain_hr.applications WHERE {where_sql} ORDER BY applied_at DESC"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="applications table not available")
    return [dict(r._mapping) for r in rows]


@router.post("/applications", status_code=201, summary="Application anlegen",
    response_model=PersonalOut
)
async def create_application(
    payload: ApplicationIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Bewerbung erfassen (Eingang in Pipeline)."""
    app_id = str(uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_hr.applications
                    (id, applicant_name, applicant_email, position_id, position_title, source, documents_ref, status, applied_at, tenant_id)
                VALUES
                    (:id, :applicant_name, :applicant_email, :position_id, :position_title, :source, :documents_ref, 'EINGANG', NOW(), :tenant_id)
            """),
            {
                "id": app_id,
                "applicant_name": payload.applicant_name,
                "applicant_email": payload.applicant_email,
                "position_id": payload.position_id,
                "position_title": payload.position_title,
                "source": payload.source,
                "documents_ref": payload.documents_ref,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="applications table not available")
    return {"id": app_id, "status": "EINGANG"}


@router.patch("/applications/{application_id}/stage", summary="Application stage aktualisieren",
    response_model=PersonalOut
)
async def update_application_stage(
    application_id: str,
    payload: ApplicationStagePatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Pipeline-Stufe einer Bewerbung ändern."""
    if payload.stage not in APPLICATION_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {', '.join(sorted(APPLICATION_STAGES))}")
    try:
        result = db.execute(
            text("""
                UPDATE domain_hr.applications
                SET status = :stage, last_updated = NOW(), notes = COALESCE(notes, '') || :note
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "stage": payload.stage,
                "note": f"\n[{datetime.utcnow().isoformat()}] {payload.note or ''}" if payload.note else "",
                "id": application_id,
                "tenant_id": tenant_id,
            },
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="applications table not available")
    return {"id": application_id, "stage": payload.stage, "status": "updated"}


@router.delete(
    "/applications/{application_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Application löschen",
)
async def delete_application(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht eine Bewerbung (nur eigener Mandant)."""
    try:
        deleted = db.execute(
            text("DELETE FROM domain_hr.applications WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": application_id, "tenant_id": tenant_id},
        ).rowcount
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="applications table not available")
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
    db.commit()
    return None
