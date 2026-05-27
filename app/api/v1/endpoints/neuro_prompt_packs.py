"""Prompt Pack Registry -- REST API (NC-G5)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.agents.neuroassist_contracts import PromptPack
from app.core.tenant import get_tenant_id
from app.services.prompt_pack_registry import (
    register_prompt_pack,
    list_prompt_packs,
    get_active_prompt_pack,
    rollback_prompt_pack,
    list_active_variants,
    select_prompt_pack_variant,
)

router = APIRouter(tags=["neuro-core", "prompt-packs"])


class RegisterPromptPackRequest(BaseModel):
    prompt_pack_key: str
    role_key: str
    mission: str
    scope: str
    constraints: list[str] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    decision_policy: list[str] = Field(default_factory=list)
    output_schema: str
    handover_rules: list[str] = Field(default_factory=list)
    version: str = "1.0"
    variant_key: Optional[str] = None
    traffic_weight: Optional[float] = None


@router.post("/neuro/prompt-packs", summary="Register prompt pack do",
    response_model=dict
)
async def do_register_prompt_pack(
    request: RegisterPromptPackRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    pack = PromptPack(
        prompt_pack_key=request.prompt_pack_key,
        role_key=request.role_key,
        mission=request.mission,
        scope=request.scope,
        constraints=request.constraints,
        inputs=request.inputs,
        decision_policy=request.decision_policy,
        output_schema=request.output_schema,
        handover_rules=request.handover_rules,
    )
    return register_prompt_pack(
        pack,
        request.version,
        tenant_id,
        request.variant_key,
        request.traffic_weight,
    )


@router.get("/neuro/prompt-packs", summary="List prompt packs do",
    response_model=dict
)
async def do_list_prompt_packs(
    tenant_id: str = Depends(get_tenant_id),
):
    return {"items": list_prompt_packs(tenant_id)}


@router.get("/neuro/prompt-packs/{prompt_pack_key}", summary="Get prompt pack do",
    response_model=dict
)
async def do_get_prompt_pack(
    prompt_pack_key: str,
    tenant_id: str = Depends(get_tenant_id),
):
    result = get_active_prompt_pack(prompt_pack_key, tenant_id)
    if not result:
        raise HTTPException(404, "Prompt pack not found")
    return result


@router.get("/neuro/prompt-packs/{prompt_pack_key}/variants", summary="List prompt pack variants do",
    response_model=dict
)
async def do_list_prompt_pack_variants(
    prompt_pack_key: str,
    tenant_id: str = Depends(get_tenant_id),
):
    return {"items": list_active_variants(prompt_pack_key, tenant_id)}


class SelectPromptPackRequest(BaseModel):
    seed: Optional[str] = None


@router.post("/neuro/prompt-packs/{prompt_pack_key}/select", summary="Select prompt pack do",
    response_model=dict
)
async def do_select_prompt_pack(
    prompt_pack_key: str,
    request: SelectPromptPackRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    result = select_prompt_pack_variant(prompt_pack_key, tenant_id, request.seed)
    if not result:
        raise HTTPException(404, "Prompt pack not found")
    return result


@router.post("/neuro/prompt-packs/{prompt_pack_key}/rollback", summary="Rollback prompt pack do",
    response_model=dict
)
async def do_rollback_prompt_pack(
    prompt_pack_key: str,
    tenant_id: str = Depends(get_tenant_id),
):
    result = rollback_prompt_pack(prompt_pack_key, tenant_id)
    if not result:
        raise HTTPException(400, "Kein Rollback moeglich -- weniger als 2 Versionen")
    return result
