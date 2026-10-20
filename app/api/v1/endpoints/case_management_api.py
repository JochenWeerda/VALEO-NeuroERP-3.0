"""Case Management REST API — NC-08."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional

from app.core.akteur import gepruefter_akteur_aus_request
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

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


class CaseManagementOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/neuro/cases", tags=["neuro-core", "case-management"])


class DecideRequest(BaseModel):
    decision: str = Field(..., description="GENEHMIGT | ABGELEHNT | ESKALIERT")
    # Wer entscheidet, kommt aus dem Token (bis 20.10.2026 frei waehlbar im Body); das Feld wird ignoriert.
    decided_by: Optional[str] = Field(None, description="veraltet, wird ignoriert")
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


@router.get("/", summary="All auflisten",
    response_model=CaseManagementOut
)
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


@router.get("/dashboard", summary="Dashboard",
    response_model=CaseManagementOut
)
async def dashboard(
    tenant_id: str = Depends(get_tenant_id),
):
    """Dashboard-Statistiken fuer Human Oversight."""
    return get_dashboard_stats(tenant_id)


def _eigener_fall(case_id: str, tenant_id: str):
    """Nur Faelle des eigenen Mandanten (bis 20.10.2026 jeder Fall jeder Kennung)."""
    case = get_case(case_id)
    if case is None or case.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Case nicht gefunden")
    return case


@router.get("/{case_id}", summary="Single abrufen",
    response_model=CaseManagementOut
)
async def get_single(case_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Einzelnen Case abrufen."""
    return _eigener_fall(case_id, tenant_id).to_dict()


@router.post("/{case_id}/assign", summary="Zuweisen",
    response_model=CaseManagementOut, dependencies=SCHREIBEN["FACHLICH"])
async def assign(case_id: str, request: AssignRequest, tenant_id: str = Depends(get_tenant_id)):
    """Case einem Benutzer zuweisen."""
    _eigener_fall(case_id, tenant_id)
    case = assign_case(case_id, request.user_id)
    if not case:
        return {"error": "Case nicht zuweisbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/decide", summary="Decide",
    response_model=CaseManagementOut, dependencies=SCHREIBEN["FACHLICH"])
async def decide(case_id: str, request: DecideRequest, http: Request, tenant_id: str = Depends(get_tenant_id)):
    """Case entscheiden (genehmigen/ablehnen)."""
    _eigener_fall(case_id, tenant_id)
    decision = ApprovalDecision(request.decision)
    case = decide_case(case_id, decision, gepruefter_akteur_aus_request(http), request.comment)
    if not case:
        return {"error": "Case nicht entscheidbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/escalate", summary="Escalate",
    response_model=CaseManagementOut, dependencies=SCHREIBEN["FACHLICH"])
async def escalate(case_id: str, request: EscalateRequest, tenant_id: str = Depends(get_tenant_id)):
    """Case eskalieren."""
    _eigener_fall(case_id, tenant_id)
    case = escalate_case(case_id, request.escalate_to, request.reason)
    if not case:
        return {"error": "Case nicht eskalierbar", "case_id": case_id}
    return case.to_dict()


@router.post("/{case_id}/close", summary="Abschließen",
    response_model=CaseManagementOut, dependencies=SCHREIBEN["FACHLICH"])
async def close(case_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Case schliessen."""
    _eigener_fall(case_id, tenant_id)
    case = close_case(case_id)
    if not case:
        return {"error": "Case nicht gefunden", "case_id": case_id}
    return case.to_dict()


@router.post("/escalate-overdue", summary="Overdue escalate",
    response_model=CaseManagementOut, dependencies=SCHREIBEN["FACHLICH"])
async def escalate_overdue(tenant_id: str = Depends(get_tenant_id)):
    """Ueberfaellige Cases des eigenen Mandanten eskalieren (bis 20.10.2026: aller Mandanten)."""
    escalated = check_and_escalate_overdue(tenant_id)
    return {"escalated_count": len(escalated), "cases": [c.to_dict() for c in escalated]}
