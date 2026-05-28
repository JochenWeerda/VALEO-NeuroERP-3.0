"""DSGVO Löschkonzept — Erasure request management (Art. 17 DSGVO)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/compliance/dsgvo", tags=["compliance", "dsgvo"])

ERASURE_STATUSES = {"EINGEGANGEN", "IN_BEARBEITUNG", "ABGESCHLOSSEN", "ABGELEHNT"}
SUBJECT_TYPES = {"CUSTOMER", "EMPLOYEE", "LEAD"}


class ErasureRequestIn(BaseModel):
    requester_name: str = Field(..., max_length=200)
    requester_email: str = Field(..., max_length=200)
    subject_id: str = Field(..., description="ID des betroffenen Datensatzes")
    subject_type: str = Field(..., description="CUSTOMER/EMPLOYEE/LEAD")


class ErasureProcessIn(BaseModel):
    deletion_notes: str | None = None


class ErasureRejectIn(BaseModel):
    reason: str = Field(..., max_length=1000, description="z.B. gesetzliche Aufbewahrungspflicht")


def _anonymize_subject(db: Session, subject_type: str, subject_id: str, tenant_id: str) -> list[dict]:
    """Anonymisiert/löscht Datensätze und gibt ein Protokoll zurück."""
    log: list[dict] = []
    anon_name = "ANONYM (DSGVO Art.17)"
    anon_email = "geloescht@dsgvo.invalid"

    table_map = {
        "CUSTOMER": [
            ("domain_crm.crm_customers", "UPDATE domain_crm.crm_customers SET name = :anon_name, email = :anon_email, telefon = NULL, adresse = NULL WHERE id = :sid AND tenant_id = :tid"),
            ("domain_crm.contacts", "DELETE FROM domain_crm.contacts WHERE customer_id = :sid AND tenant_id = :tid"),
            ("domain_crm.activities", "DELETE FROM domain_crm.activities WHERE customer_id = :sid AND tenant_id = :tid"),
        ],
        "EMPLOYEE": [
            ("domain_hr.employees", "UPDATE domain_hr.employees SET name = :anon_name, email = :anon_email, telefon = NULL WHERE id = :sid AND tenant_id = :tid"),
        ],
        "LEAD": [
            ("domain_crm.leads", "UPDATE domain_crm.leads SET name = :anon_name, email = :anon_email, telefon = NULL WHERE id = :sid AND tenant_id = :tid"),
            ("domain_crm.activities", "DELETE FROM domain_crm.activities WHERE lead_id = :sid AND tenant_id = :tid"),
        ],
    }

    for table, sql in table_map.get(subject_type, []):
        try:
            result = db.execute(
                text(sql),
                {"anon_name": anon_name, "anon_email": anon_email, "sid": subject_id, "tid": tenant_id},
            )
            log.append({"table": table, "rows_affected": result.rowcount, "action": "anonymized_or_deleted"})
        except Exception as exc:
            log.append({"table": table, "rows_affected": 0, "error": str(exc)})
    return log


@router.post("/erasure-requests", status_code=201, summary="Erasure request anlegen",
    response_model=CompatFlexOut
)
async def create_erasure_request(
    payload: ErasureRequestIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag (Art. 17 DSGVO) einreichen."""
    if payload.subject_type not in SUBJECT_TYPES:
        raise HTTPException(status_code=400, detail=f"subject_type must be one of: {', '.join(SUBJECT_TYPES)}")
    req_id = str(uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_compliance.data_erasure_requests
                    (id, requester_name, requester_email, subject_id, subject_type,
                     request_date, status, deletion_log, tenant_id)
                VALUES
                    (:id, :requester_name, :requester_email, :subject_id, :subject_type,
                     NOW(), 'EINGEGANGEN', '[]'::jsonb, :tenant_id)
            """),
            {
                "id": req_id,
                "requester_name": payload.requester_name,
                "requester_email": payload.requester_email,
                "subject_id": payload.subject_id,
                "subject_type": payload.subject_type,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return {"id": req_id, "status": "EINGEGANGEN"}


@router.get("/erasure-requests", summary="Erasure requests auflisten",
    response_model=list[CompatFlexOut]
)
async def list_erasure_requests(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Löschanträge auflisten, optional nach Status filtern."""
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if status:
        if status not in ERASURE_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(ERASURE_STATUSES)}")
        where.append("status = :status")
        params["status"] = status
    try:
        rows = db.execute(
            text(f"SELECT * FROM domain_compliance.data_erasure_requests WHERE {' AND '.join(where)} ORDER BY request_date DESC"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params,
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return [dict(r._mapping) for r in rows]


@router.get("/erasure-requests/{request_id}", summary="Erasure request abrufen",
    response_model=CompatFlexOut
)
async def get_erasure_request(
    request_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Detail eines Löschantrags."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_compliance.data_erasure_requests WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": request_id, "tenant_id": tenant_id},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    if not row:
        raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found")
    return dict(row._mapping)


@router.post("/erasure-requests/{request_id}/process", summary="Erasure request verarbeiten",
    response_model=CompatFlexOut
)
async def process_erasure_request(
    request_id: str,
    payload: ErasureProcessIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag ausführen: Daten anonymisieren/löschen und protokollieren."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_compliance.data_erasure_requests WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": request_id, "tenant_id": tenant_id},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    if not row:
        raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found")
    r = dict(row._mapping)
    if r["status"] == "ABGESCHLOSSEN":
        raise HTTPException(status_code=409, detail="Erasure request already completed")
    if r["status"] == "ABGELEHNT":
        raise HTTPException(status_code=409, detail="Erasure request was rejected")

    deletion_log = _anonymize_subject(db, r["subject_type"], r["subject_id"], tenant_id)
    if payload.deletion_notes:
        deletion_log.append({"note": payload.deletion_notes})

    try:
        db.execute(
            text("""
                UPDATE domain_compliance.data_erasure_requests
                SET status = 'ABGESCHLOSSEN', completion_date = NOW(),
                    deletion_log = :deletion_log::jsonb
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {"deletion_log": json.dumps(deletion_log), "id": request_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Failed to update erasure request")
    return {"id": request_id, "status": "ABGESCHLOSSEN", "deletion_log": deletion_log}


@router.post("/erasure-requests/{request_id}/reject", summary="Erasure request ablehnen",
    response_model=CompatFlexOut
)
async def reject_erasure_request(
    request_id: str,
    payload: ErasureRejectIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löschantrag ablehnen (z.B. gesetzliche Aufbewahrungspflicht)."""
    try:
        result = db.execute(
            text("""
                UPDATE domain_compliance.data_erasure_requests
                SET status = 'ABGELEHNT',
                    deletion_log = jsonb_build_array(jsonb_build_object('rejected_reason', :reason, 'rejected_at', NOW()::text))
                WHERE id = :id AND tenant_id = :tenant_id AND status NOT IN ('ABGESCHLOSSEN', 'ABGELEHNT')
            """),
            {"reason": payload.reason, "id": request_id, "tenant_id": tenant_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"ErasureRequest {request_id} not found or already finalized")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="data_erasure_requests table not available")
    return {"id": request_id, "status": "ABGELEHNT", "reason": payload.reason}
