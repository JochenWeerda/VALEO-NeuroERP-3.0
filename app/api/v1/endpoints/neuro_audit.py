"""Audit Hardening + Decision Protocol — REST API (NC-D)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.audit_hardening import (
    validate_hash_chain, query_audit_trail,
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


@router.get("/neuro/kernel-step-audit/summary")
async def neuro_kernel_step_audit_summary(
    days: int = Query(7, ge=1, le=366),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Aggregierte Zeilen aus neuro_step_audit_trace fuer Monitoring (pro Tenant)."""
    try:
        total = db.execute(
            text(
                """
                SELECT COUNT(*) AS c
                FROM domain_shared.neuro_step_audit_trace
                WHERE tenant_id = :tid
                  AND recorded_at >= NOW() - make_interval(days => :days)
                """
            ),
            {"tid": tenant_id, "days": days},
        ).scalar()
        by_day = db.execute(
            text(
                """
                SELECT date_trunc('day', recorded_at AT TIME ZONE 'UTC') AS day, COUNT(*) AS cnt
                FROM domain_shared.neuro_step_audit_trace
                WHERE tenant_id = :tid
                  AND recorded_at >= NOW() - make_interval(days => :days)
                GROUP BY 1
                ORDER BY 1
                """
            ),
            {"tid": tenant_id, "days": days},
        ).fetchall()
        by_command = db.execute(
            text(
                """
                SELECT step_id, COUNT(*) AS cnt
                FROM domain_shared.neuro_step_audit_trace
                WHERE tenant_id = :tid
                  AND recorded_at >= NOW() - make_interval(days => :days)
                GROUP BY step_id
                ORDER BY cnt DESC
                LIMIT 50
                """
            ),
            {"tid": tenant_id, "days": days},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"neuro_step_audit_trace nicht lesbar: {exc}",
        ) from exc

    return {
        "tenant_id": tenant_id,
        "days": days,
        "total_rows": int(total or 0),
        "by_day": [
            {"day": (r.day.isoformat() if r.day else None), "count": int(r.cnt or 0)}
            for r in by_day
        ],
        "by_step_id": [
            {"step_id": r.step_id, "count": int(r.cnt or 0)} for r in by_command
        ],
    }
