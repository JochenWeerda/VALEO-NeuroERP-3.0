from __future__ import annotations

from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.core.multi_context_agent import AgentContext, AgentContextStore, tenantbewusst_dispatch
from app.core.tenant_isolation_guard import TenantIsolationGuard

router = APIRouter(prefix="/agent-context", tags=["agent-context"])
_store = AgentContextStore()
_guard = TenantIsolationGuard()


class AgentContextCreateRequest(BaseModel):
    agent_id: str
    tenant_id: str
    delegated_roles: list[str]
    ttl_sekunden: int = 3600


class AgentDispatchRequest(BaseModel):
    command_name: str
    resource_tenant_id: str
    resource_type: str = "agent_command"
    issuer_role: str = "agent"


@router.post("", status_code=201)
def create_context(req: AgentContextCreateRequest) -> AgentContext:
    context = AgentContext(
        context_id=str(uuid.uuid4()),
        agent_id=req.agent_id,
        tenant_id=req.tenant_id,
        delegated_roles=req.delegated_roles,
        context_expires_at=datetime.utcnow() + timedelta(seconds=req.ttl_sekunden),
        erstellt_am=datetime.utcnow(),
    )
    _store.add(context)
    return context


@router.delete("/{context_id}", status_code=204)
def widerrufen(context_id: str) -> Response:
    ok = _store.widerrufen(context_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Kontext nicht gefunden")
    return Response(status_code=204)


@router.post("/{context_id}/dispatch")
def dispatch(context_id: str, req: AgentDispatchRequest):
    context = _store.get(context_id)
    if context is None:
        raise HTTPException(status_code=404, detail="Kontext nicht gefunden")
    return tenantbewusst_dispatch(
        context=context,
        command_name=req.command_name,
        resource_tenant_id=req.resource_tenant_id,
        resource_type=req.resource_type,
        issuer_role=req.issuer_role,
        isolation_guard=_guard,
    )
