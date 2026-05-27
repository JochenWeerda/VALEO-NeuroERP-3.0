"""Case Management REST API — NC-08."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional

from app.core.tenant import get_tenant_id
from app.core.human_approval_gate import ApprovalDecision
from app.services.case_management import (
    CasePriority,
    CaseStatus,
    assign_case,
    close_case,
    decide_case,
    escalate_case,
    get_case,
    get_dashboard_stats,
    list_cases,
    check_and_escalate_overdue,
)

router = APIRouter(prefix="/neuro/cases", tags=["neuro-core", "case-management"])


class DecideRequest(BaseModel):
    decision: str = Field(..., description="GENEHMIGT | ABGELEHNT | ESKALIERT")
    decided_by: str = Field(...)
    comment: str = Field("")


class AssignRequest(BaseModel):
    user_id: str = Field(...)


class EscalateRequest(BaseModel):
    escalate_to: str = Field(...)
    reason: str = Field("")


class ListQuery(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    limit: int = Field(100, ge=1, le=500)


@router.get("/", summary="All auflisten")
async def list_all(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 100,
    tenant_id: str = Depends(get_tenant_id),
):
    """Offene Cases auflisten mit optionalen Filtern."""
    s = CaseStatus(status) if status else None
    p = CasePriority(priority) if priority else None
    cases = list_cases(status=s, priority=p, assigned_to=assigned_to, tenant_id=tenant_id, limit=limit)
    return {"count": len(cases), "cases": [c.to_dict() for c in cases]}


@router.get("/dashboard", summary="Dashboard")
async def dashboard(
    tenant_id: str = Depends(get_tenant_id),
):
    """Dashboard-Statistiken fuer Human Oversight."""
    return get_dashboard_stats(tenant_id)


@router.get("/{case_id}", summary="Single abrufen")
async def get_single(case_id: str):
    """Einzelnen Case abrufen."""
    case = get_case(case_id)
    if not case:
        return {"error": "Case nicht gefunden", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/assign", summary="Zuweisen")
async def assign(case_id: str, request: AssignRequest):
    """Case einem Benutzer zuweisen."""
    case = assign_case(case_id, request.user_id)
    if not case:
        return {"error": "Case nicht zuweisbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/decide", summary="Decide")
async def decide(case_id: str, request: DecideRequest):
    """Case entscheiden (genehmigen/ablehnen)."""
    decision = ApprovalDecision(request.decision)
    case = decide_case(case_id, decision, request.decided_by, request.comment)
    if not case:
        return {"error": "Case nicht entscheidbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/escalate", summary="Escalate")
async def escalate(case_id: str, request: EscalateRequest):
    """Case eskalieren."""
    case = escalate_case(case_id, request.escalate_to, request.reason)
    if not case:
        return {"error": "Case nicht eskalierbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/close", summary="Abschließen")
async def close(case_id: str):
    """Case schliessen."""
    case = close_case(case_id)
    if not case:
        return {"error": "Case nicht gefunden", "case_id": case_id}
    return case.to_dict()


@router.post("/escalate-overdue", summary="Overdue escalate")
async def escalate_overdue():
    """Alle ueberfaelligen Cases automatisch eskalieren."""
    escalated = check_and_escalate_overdue()
    return {"escalated_count": len(escalated), "cases": [c.to_dict() for c in escalated]}
