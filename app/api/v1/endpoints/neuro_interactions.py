"""Interaction State Manager — REST API (NC-002)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.interaction_state_manager import (
    create_interaction, transition_interaction, get_interaction, list_interactions,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/neuro/interactions", tags=["neuro-core", "interactions"])


class CreateInteractionRequest(BaseModel):
    channel: str = Field(..., description="Kanal (chat/whatsapp/voice/email)")
    entity_id: Optional[str] = Field(None, description="Zugehoerige Entity-ID (Kunde, Lead, ...)")


class TransitionRequest(BaseModel):
    target_state: str = Field(..., description="Zielzustand")


@router.post("", summary="Anlegen",
    response_model=CompatFlexOut
)
async def create(
    request: CreateInteractionRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return create_interaction(request.channel, request.entity_id, tenant_id, db)


@router.put("/{interaction_id}/transition", summary="Transition",
    response_model=CompatFlexOut
)
async def transition(
    interaction_id: str,
    request: TransitionRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = transition_interaction(interaction_id, request.target_state, tenant_id, db)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/{interaction_id}", summary="One abrufen",
    response_model=CompatFlexOut
)
async def get_one(
    interaction_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = get_interaction(interaction_id, tenant_id, db)
    if not result:
        raise HTTPException(404, "Interaction not found")
    return result


@router.get("", summary="All auflisten",
    response_model=CompatFlexOut
)
async def list_all(
    state: Optional[str] = None,
    limit: int = 50,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_interactions(tenant_id, db, state, limit)}
