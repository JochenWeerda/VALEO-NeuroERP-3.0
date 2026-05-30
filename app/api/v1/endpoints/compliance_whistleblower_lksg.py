"""Whistleblower and LkSG operating contracts for compliance."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.compliance_whistleblower_lksg_schemas import ComplianceWhistleblowerLksgOut


router = APIRouter(prefix="/compliance", tags=["compliance", "whistleblower", "lksg"])


class WhistleblowerReportIn(BaseModel):
    category: str = Field(..., max_length=80)
    description: str = Field(..., min_length=10, max_length=4000)
    contact_email: str | None = Field(default=None, max_length=200)
    anonymous: bool = True


class WhistleblowerStatusIn(BaseModel):
    status: str = Field(..., pattern="^(EINGEGANGEN|IN_PRUEFUNG|MASSNAHME|GESCHLOSSEN)$")
    note: str | None = Field(default=None, max_length=1000)


class LksgRiskAssessmentIn(BaseModel):
    supplier_id: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=2, max_length=2)
    spend_eur: float = Field(..., ge=0)
    sector_risk: int = Field(..., ge=0, le=5)
    human_rights_flags: int = Field(default=0, ge=0, le=5)
    environmental_flags: int = Field(default=0, ge=0, le=5)
    mitigation_note: str | None = Field(default=None, max_length=1000)


def _risk_score(payload: LksgRiskAssessmentIn) -> int:
    spend_factor = 0
    if payload.spend_eur >= 250_000:
        spend_factor = 2
    elif payload.spend_eur >= 50_000:
        spend_factor = 1
    return min(
        15,
        payload.sector_risk * 2
        + payload.human_rights_flags
        + payload.environmental_flags
        + spend_factor,
    )


def _risk_level(score: int) -> str:
    if score >= 10:
        return "HOCH"
    if score >= 5:
        return "MITTEL"
    return "NIEDRIG"


@router.post("/whistleblower/reports", status_code=201, summary="Whistleblower report anlegen",
    response_model=IDResponse
)
async def create_whistleblower_report(
    payload: WhistleblowerReportIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    report_id = str(uuid4())
    contact_email = None if payload.anonymous else payload.contact_email
    try:
        db.execute(
            text("""
                INSERT INTO domain_compliance.whistleblower_reports
                    (id, tenant_id, category, description, contact_email, anonymous, status, created_at)
                VALUES
                    (:id, :tenant_id, :category, :description, :contact_email, :anonymous, 'EINGEGANGEN', :created_at)
            """),
            {
                "id": report_id,
                "tenant_id": tenant_id,
                "category": payload.category,
                "description": payload.description,
                "contact_email": contact_email,
                "anonymous": payload.anonymous,
                "created_at": datetime.now(timezone.utc),
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="whistleblower_reports table not available") from exc
    return {"id": report_id, "status": "EINGEGANGEN", "anonymous": payload.anonymous}


@router.get("/whistleblower/reports", summary="Whistleblower reports auflisten",
    response_model=list[ComplianceWhistleblowerLksgOut]
)
async def list_whistleblower_reports(
    status: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    where = ["tenant_id = :tenant_id"]
    params = {"tenant_id": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status
    try:
        rows = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT id, category, anonymous, status, created_at, updated_at
                FROM domain_compliance.whistleblower_reports
                WHERE {' AND '.join(where)}
                ORDER BY created_at DESC
            """),
            params,
        ).mappings().all()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="whistleblower_reports table not available") from exc
    return [dict(row) for row in rows]


@router.patch("/whistleblower/reports/{report_id}/status", summary="Whistleblower status aktualisieren",
    response_model=IDResponse
)
async def update_whistleblower_status(
    report_id: str,
    payload: WhistleblowerStatusIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = db.execute(
            text("""
                UPDATE domain_compliance.whistleblower_reports
                SET status = :status, internal_note = :note, updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {"id": report_id, "tenant_id": tenant_id, "status": payload.status, "note": payload.note},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Hinweis nicht gefunden")
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="whistleblower_reports table not available") from exc
    return {"id": report_id, "status": payload.status}


@router.post("/lksg/supplier-risk-assessments", status_code=201, summary="Lksg supplier risk assessment anlegen",
    response_model=IDResponse
)
async def create_lksg_supplier_risk_assessment(
    payload: LksgRiskAssessmentIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    assessment_id = str(uuid4())
    score = _risk_score(payload)
    level = _risk_level(score)
    try:
        db.execute(
            text("""
                INSERT INTO domain_compliance.lksg_supplier_risk_assessments
                    (id, tenant_id, supplier_id, country_code, spend_eur, sector_risk,
                     human_rights_flags, environmental_flags, mitigation_note,
                     risk_score, risk_level, created_at)
                VALUES
                    (:id, :tenant_id, :supplier_id, :country_code, :spend_eur, :sector_risk,
                     :human_rights_flags, :environmental_flags, :mitigation_note,
                     :risk_score, :risk_level, NOW())
            """),
            {
                "id": assessment_id,
                "tenant_id": tenant_id,
                **payload.model_dump(),
                "risk_score": score,
                "risk_level": level,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="lksg_supplier_risk_assessments table not available") from exc
    return {"id": assessment_id, "risk_score": score, "risk_level": level}


@router.get("/lksg/supplier-risk-assessments", summary="Lksg supplier risk assessments auflisten",
    response_model=list[ComplianceWhistleblowerLksgOut]
)
async def list_lksg_supplier_risk_assessments(
    risk_level: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    where = ["tenant_id = :tenant_id"]
    params = {"tenant_id": tenant_id}
    if risk_level:
        where.append("risk_level = :risk_level")
        params["risk_level"] = risk_level
    try:
        rows = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT id, supplier_id, country_code, risk_score, risk_level, mitigation_note, created_at
                FROM domain_compliance.lksg_supplier_risk_assessments
                WHERE {' AND '.join(where)}
                ORDER BY risk_score DESC, created_at DESC
            """),
            params,
        ).mappings().all()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="lksg_supplier_risk_assessments table not available") from exc
    return [dict(row) for row in rows]


@router.get("/lksg/annual-report-preview", summary="Annual report preview lksg",
    response_model=ComplianceWhistleblowerLksgOut
)
async def lksg_annual_report_preview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        rows = db.execute(
            text("""
                SELECT risk_level, COUNT(*) AS count
                FROM domain_compliance.lksg_supplier_risk_assessments
                WHERE tenant_id = :tenant_id
                GROUP BY risk_level
            """),
            {"tenant_id": tenant_id},
        ).mappings().all()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="lksg_supplier_risk_assessments table not available") from exc
    counts = {str(row["risk_level"]): int(row["count"]) for row in rows}
    return {
        "tenant_id": tenant_id,
        "high_risk_suppliers": counts.get("HOCH", 0),
        "medium_risk_suppliers": counts.get("MITTEL", 0),
        "low_risk_suppliers": counts.get("NIEDRIG", 0),
        "next_action": "HOCH-Risiken mit Massnahmenplan pruefen" if counts.get("HOCH", 0) else "Jahresbericht vorbereiten",
    }
