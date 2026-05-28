"""Neuro Verification Engine — REST API (NC-001)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.neuro_verification_engine import verify_plan, VerificationResult

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/neuro/verify", tags=["neuro-core", "verification"])


class VerifyPlanRequest(BaseModel):
    action: str = Field(..., description="Geplante Aktion (create/update/delete/cancel/...)")
    entity_type: str = Field(..., description="Entitaetstyp (order/invoice/contract/...)")
    entity_id: Optional[str] = Field(None, description="ID der betroffenen Entitaet")
    current_state: Optional[str] = Field(None, description="Aktueller Zustand")
    target_state: Optional[str] = Field(None, description="Zielzustand")
    amount: Optional[float] = Field(None, description="Betrag (fuer Policy-Pruefung)")
    reason: Optional[str] = Field(None, description="Begruendung")
    approved_by: Optional[str] = Field(None, description="Freigebender Benutzer")
    four_eyes_approved: Optional[bool] = Field(None, description="4-Augen-Freigabe erteilt")
    requires_approval: Optional[bool] = Field(False)
    params: Optional[dict[str, Any]] = Field(default_factory=dict)
    required_fields: Optional[list[str]] = Field(default_factory=list)


class VerifyPlanResponse(BaseModel):
    trace_id: str
    status: str
    violations: list[dict]
    checked_at: str
    plan_summary: str


@router.post("", response_model=VerifyPlanResponse, summary="Verifizieren")
async def verify(
    request: VerifyPlanRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Plan vor Ausfuehrung verifizieren."""
    plan = request.model_dump(exclude_none=True)
    result: VerificationResult = verify_plan(plan, tenant_id, db)
    return VerifyPlanResponse(**result.to_dict())


@router.get("/{trace_id}", response_model=VerifyPlanResponse, summary="Verification abrufen")
async def get_verification(
    trace_id: str,
    db: Session = Depends(get_db),
):
    """Verifikationsergebnis per Trace-ID abrufen."""
    row = db.execute(text("""
        SELECT details FROM domain_shared.audit_logs
        WHERE id = :tid AND action LIKE 'verification.%%'
        LIMIT 1
    """), {"tid": trace_id}).fetchone()

    if not row:
        from fastapi import HTTPException
        raise HTTPException(404, "Verification trace not found")

    import json
    try:
        data = json.loads(row.details) if isinstance(row.details, str) else row.details
    except Exception:
        data = {"trace_id": trace_id, "status": "unknown", "violations": [], "checked_at": "", "plan_summary": ""}

    return VerifyPlanResponse(**data)
