from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.multi_context_agent import AgentContext, tenantbewusst_dispatch
from app.core.tenant_isolation_guard import TenantIsolationGuard
from app.domains.operations.models import AgentContextDB

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.agent_context_api_schemas import AgentContextApiOut


router = APIRouter(prefix="/agent-context", tags=["agent-context"])
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


class AgentKnowledgePackRequest(BaseModel):
    rolle: str
    kanal: str = "CHAT"
    capability_key: Optional[str] = None
    query: str = ""
    limit: int = 4


def _row_to_context(row: AgentContextDB) -> AgentContext:
    return AgentContext(
        context_id=row.context_id,
        agent_id=row.agent_id,
        tenant_id=row.tenant_id,
        delegated_roles=row.delegated_roles or [],
        context_expires_at=row.context_expires_at,
        erstellt_am=row.erstellt_am,
    )


def _get_active_context(context_id: str, db: Session) -> AgentContextDB:
    row = db.query(AgentContextDB).filter(AgentContextDB.context_id == context_id).first()
    if not row:
        raise HTTPException(404, "Kontext nicht gefunden")
    if row.widerrufen:
        raise HTTPException(410, "Kontext wurde widerrufen")
    if row.context_expires_at.replace(tzinfo=timezone.utc) < datetime.now(tz=timezone.utc):
        raise HTTPException(410, "Kontext ist abgelaufen")
    return row


@router.post("", status_code=201, summary="Context anlegen",
    response_model=None
)
def create_context(req: AgentContextCreateRequest, db: Session = Depends(get_db)):
    expires = datetime.now(tz=timezone.utc) + timedelta(seconds=req.ttl_sekunden)
    row = AgentContextDB(
        context_id=str(uuid.uuid4()),
        agent_id=req.agent_id,
        tenant_id=req.tenant_id,
        delegated_roles=req.delegated_roles,
        context_expires_at=expires,
        widerrufen=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_context(row)


@router.delete("/{context_id}", status_code=204, response_class=Response, response_model=None, summary="Widerrufen")
def widerrufen(context_id: str, db: Session = Depends(get_db)):
    row = db.query(AgentContextDB).filter(AgentContextDB.context_id == context_id).first()
    if not row:
        raise HTTPException(404, "Kontext nicht gefunden")
    row.widerrufen = True
    db.commit()
    return Response(status_code=204)


@router.post("/{context_id}/dispatch", summary="Dispatch",
    response_model=None
)
def dispatch(context_id: str, req: AgentDispatchRequest, db: Session = Depends(get_db)):
    row = _get_active_context(context_id, db)
    context = _row_to_context(row)
    return tenantbewusst_dispatch(
        context=context,
        command_name=req.command_name,
        resource_tenant_id=req.resource_tenant_id,
        resource_type=req.resource_type,
        issuer_role=req.issuer_role,
        isolation_guard=_guard,
    )


@router.post("/{context_id}/knowledge-pack", summary="Pack knowledge",
    response_model=AgentContextApiOut
)
def knowledge_pack(context_id: str, req: AgentKnowledgePackRequest, db: Session = Depends(get_db)):
    from app.core.knowledge_core_contracts import KnowledgeChannel
    from app.core.knowledge_runtime import build_runtime_context_pack

    row = _get_active_context(context_id, db)
    context = _row_to_context(row)
    pack = build_runtime_context_pack(
        db=db,
        rolle=req.rolle,
        kanal=KnowledgeChannel(req.kanal),
        tenant_id=context.tenant_id,
        capability_key=req.capability_key,
        query=req.query,
        limit=req.limit,
    )
    return {
        "context_id": context.context_id,
        "agent_id": context.agent_id,
        "tenant_id": context.tenant_id,
        "knowledge_pack": pack.as_dict(),
    }
