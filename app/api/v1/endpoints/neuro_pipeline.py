"""Neuro-Core Pipeline — REST API (NC-A)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.agents.neuro_intent_engine import classify, get_supported_intents
from app.agents.neuro_planner import generate_plan, verify_plan
from app.agents.neuro_pipeline import run_pipeline

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/neuro", tags=["neuro-core", "pipeline"])


class ClassifyRequest(BaseModel):
    user_input: str = Field(..., description="Benutzer-Eingabe")
    context: Optional[dict[str, Any]] = Field(default_factory=dict)


class PipelineRequest(BaseModel):
    user_input: str = Field(..., description="Benutzer-Eingabe")
    context: Optional[dict[str, Any]] = Field(default_factory=dict)
    dry_run: bool = Field(False, description="Nur simulieren, nicht ausfuehren")


@router.post("/classify", summary="Classify do",
    response_model=CompatFlexOut
)
async def do_classify(request: ClassifyRequest):
    """Intent aus User-Input klassifizieren."""
    result = classify(request.user_input, request.context)
    return result.to_dict()


@router.get("/intents", summary="Intents auflisten",
    response_model=CompatFlexOut
)
async def list_intents():
    """Alle unterstuetzten Intents auflisten."""
    return {"intents": get_supported_intents()}


@router.post("/plan", summary="Plan do",
    response_model=CompatFlexOut
)
async def do_plan(
    request: ClassifyRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Intent klassifizieren und Plan generieren (ohne Ausfuehrung)."""
    intent_result = classify(request.user_input, request.context)
    plan = generate_plan(intent_result, request.context)
    plan = verify_plan(plan, tenant_id, db)
    return {
        "intent": intent_result.to_dict(),
        "plan": plan.to_dict(),
    }


@router.post("/execute", summary="Execute do",
    response_model=CompatFlexOut
)
async def do_execute(
    request: PipelineRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Vollstaendige Pipeline: Classify -> Plan -> Verify -> Execute."""
    return run_pipeline(
        user_input=request.user_input,
        context=request.context,
        tenant_id=tenant_id,
        db=db,
        dry_run=request.dry_run,
    )
