"""OPERATOR-AGENT-001 — API fuer den ERP-Operator-Agent (Proposal + LOW-Risiko-Execute)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.tenant import get_tenant_id
from app.services.operator_agent_service import (
    AgentActionType,
    ApprovalStatus,
    OperatorAgentPermissionError,
    OperatorAgentService,
    ProposalNotFoundError,
    operator_agent_service,
)

router = APIRouter(prefix="/agent/operator", tags=["agent", "operator"])


def _roles(x_valeo_roles: str | None = Header(default=None, alias="X-VALEO-Roles")) -> set[str]:
    if not x_valeo_roles:
        return set()
    return {r.strip() for r in x_valeo_roles.split(",") if r.strip()}


class ContextRequest(BaseModel):
    action_type: AgentActionType
    query_params: dict[str, Any] = Field(default_factory=dict)


class ProposalRequest(BaseModel):
    action_type: AgentActionType
    context_summary: str
    proposed_action: str
    rationale: str


class ApproveRequest(BaseModel):
    approved_by: str


class RejectRequest(BaseModel):
    rejected_by: str
    reason: str


class ExecuteRequest(BaseModel):
    executed_by: str


@router.post("/context", summary="Kontext fuer Agent-Aktion lesen", response_model=dict[str, Any])
async def read_context(
    req: ContextRequest,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        return operator_agent_service.read_context(
            tenant_id=tenant_id,
            action_type=req.action_type,
            roles=roles,
            query_params=req.query_params,
        )
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/proposals", summary="Agent-Proposal erstellen", response_model=dict[str, Any])
async def create_proposal(
    req: ProposalRequest,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        proposal = operator_agent_service.create_proposal(
            tenant_id=tenant_id,
            action_type=req.action_type,
            roles=roles,
            context_summary=req.context_summary,
            proposed_action=req.proposed_action,
            rationale=req.rationale,
        )
        return proposal.to_dict()
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/proposals", summary="Agent-Proposals listen", response_model=list[dict[str, Any]])
async def list_proposals(
    status: ApprovalStatus | None = None,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> list[dict[str, Any]]:
    try:
        operator_agent_service._require_role(roles, "agent:read")
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return [p.to_dict() for p in operator_agent_service.list_proposals(tenant_id=tenant_id, status=status)]


@router.get("/proposals/summary", summary="Proposal-Zusammenfassung", response_model=dict[str, Any])
async def get_summary(
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        operator_agent_service._require_role(roles, "agent:read")
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return operator_agent_service.summary(tenant_id=tenant_id)


@router.get("/proposals/{proposal_id}", summary="Agent-Proposal Detail", response_model=dict[str, Any])
async def get_proposal(
    proposal_id: str,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        operator_agent_service._require_role(roles, "agent:read")
        return operator_agent_service.get_proposal(tenant_id=tenant_id, proposal_id=proposal_id).to_dict()
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/proposals/{proposal_id}/approve",
    summary="Agent-Proposal freigeben (Human Approval)",
    response_model=dict[str, Any],
)
async def approve_proposal(
    proposal_id: str,
    req: ApproveRequest,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        return operator_agent_service.approve_proposal(
            tenant_id=tenant_id,
            proposal_id=proposal_id,
            approved_by=req.approved_by,
            roles=roles,
        ).to_dict()
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/proposals/{proposal_id}/reject",
    summary="Agent-Proposal ablehnen",
    response_model=dict[str, Any],
)
async def reject_proposal(
    proposal_id: str,
    req: RejectRequest,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        return operator_agent_service.reject_proposal(
            tenant_id=tenant_id,
            proposal_id=proposal_id,
            rejected_by=req.rejected_by,
            reason=req.reason,
            roles=roles,
        ).to_dict()
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/proposals/{proposal_id}/execute",
    summary="Genehmigte LOW-Risiko-Aktion direkt ausfuehren",
    response_model=dict[str, Any],
)
async def execute_proposal(
    proposal_id: str,
    req: ExecuteRequest,
    tenant_id: str = Depends(get_tenant_id),
    roles: set[str] = Depends(_roles),
) -> dict[str, Any]:
    try:
        return operator_agent_service.execute_approved_action(
            tenant_id=tenant_id,
            proposal_id=proposal_id,
            executed_by=req.executed_by,
            roles=roles,
        )
    except OperatorAgentPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ProposalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
