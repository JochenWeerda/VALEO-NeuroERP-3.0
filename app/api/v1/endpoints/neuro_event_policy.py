"""Event Schema Registry + Policy Registry -- REST API (NC-G)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.event_schema_registry import list_event_types, validate_event
from app.services.policy_registry import (
    register_policy,
    get_active_policy,
    list_policies,
    rollback_policy,
    list_active_variants,
    select_policy_variant,
)

router = APIRouter(tags=["neuro-core", "events", "policy"])


# ---------------------------------------------------------------------------
# Event Schema Registry
# ---------------------------------------------------------------------------

@router.get("/neuro/events/types")
async def get_event_types():
    return {"types": list_event_types()}


class ValidateEventRequest(BaseModel):
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("/neuro/events/validate")
async def do_validate_event(request: ValidateEventRequest):
    return validate_event(request.event_type, request.payload)


# ---------------------------------------------------------------------------
# Policy Registry
# ---------------------------------------------------------------------------

class RegisterPolicyRequest(BaseModel):
    policy_id: str
    name: str
    version: str = "1.0"
    rules: dict[str, Any] = Field(default_factory=dict)
    variant_key: Optional[str] = None
    traffic_weight: Optional[float] = None


@router.post("/neuro/policies")
async def do_register_policy(
    request: RegisterPolicyRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return register_policy(
        request.policy_id,
        request.name,
        request.rules,
        request.version,
        tenant_id,
        request.variant_key,
        request.traffic_weight,
        db,
    )


@router.get("/neuro/policies")
async def do_list_policies(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_policies(tenant_id, db)}


@router.get("/neuro/policies/{policy_id}")
async def do_get_policy(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = get_active_policy(policy_id, tenant_id, db)
    if not result:
        raise HTTPException(404, "Policy not found")
    return result


@router.get("/neuro/policies/{policy_id}/variants")
async def do_list_policy_variants(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_active_variants(policy_id, tenant_id, db)}


class SelectPolicyVariantRequest(BaseModel):
    seed: Optional[str] = None


@router.post("/neuro/policies/{policy_id}/select")
async def do_select_policy_variant(
    policy_id: str,
    request: SelectPolicyVariantRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = select_policy_variant(policy_id, tenant_id, request.seed, db)
    if not result:
        raise HTTPException(404, "Policy not found")
    return result


@router.post("/neuro/policies/{policy_id}/rollback")
async def do_rollback_policy(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = rollback_policy(policy_id, tenant_id, db)
    if not result:
        raise HTTPException(400, "Kein Rollback moeglich -- weniger als 2 Versionen")
    return result
