"""Audit Hardening + Decision Protocol — REST API (NC-D)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.audit_hardening import (
    append_audit_entry, validate_hash_chain, query_audit_trail,
)
from app.services.neuro_decision_protocol import (
    record_decision, get_decision, list_decisions,
)

router = APIRouter(tags=["neuro-core", "audit"])


# ── Audit Trail ────────────────────────────────────────────────

@router.get("/audit/trail")
async def get_trail(
    aggregate_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 100,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": query_audit_trail(db, tenant_id, aggregate_id, from_date, to_date, limit)}


@router.get("/audit/trail/validate")
async def validate_trail(
    limit: int = 1000,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return validate_hash_chain(db, tenant_id, limit)


# ── Decision Protocol ──────────────────────────────────────────

class RecordDecisionRequest(BaseModel):
    intent: str
    plan_steps: list[dict] = Field(default_factory=list)
    verification_result: dict = Field(default_factory=dict)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    risk_class: str = Field("low")
    human_approval: Optional[str] = None
    execution_result: Optional[dict] = None
    explanation: str = ""


@router.post("/neuro/decisions")
async def create_decision(
    request: RecordDecisionRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return record_decision(
        db, tenant_id,
        intent=request.intent,
        plan_steps=request.plan_steps,
        verification_result=request.verification_result,
        confidence_score=request.confidence_score,
        risk_class=request.risk_class,
        human_approval=request.human_approval,
        execution_result=request.execution_result,
        explanation=request.explanation,
    )


@router.get("/neuro/decisions/{decision_id}")
async def get_one_decision(
    decision_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = get_decision(db, decision_id, tenant_id)
    if not result:
        raise HTTPException(404, "Decision not found")
    return result


@router.get("/neuro/decisions")
async def list_all_decisions(
    risk_class: Optional[str] = None,
    limit: int = 50,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_decisions(db, tenant_id, limit, risk_class)}
