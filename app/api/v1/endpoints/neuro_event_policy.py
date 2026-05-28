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

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.neuro_event_policy_schemas import (
    NeuroEventPolicyOut,
    RegisterPolicyRequest,
    SelectPolicyVariantRequest,
    ValidateEventRequest,
)
from pydantic import ConfigDict as _ConfigDict

router = APIRouter(tags=["neuro-core", "events", "policy"])


# ---------------------------------------------------------------------------
# Event Schema Registry
# ---------------------------------------------------------------------------

@router.get("/neuro/events/types", summary="Event types abrufen",
    response_model=NeuroEventPolicyOut
)
async def get_event_types():
    return {"types": list_event_types()}

@router.post("/neuro/events/validate", summary="Validate event do",
    response_model=NeuroEventPolicyOut
)
async def do_validate_event(request: ValidateEventRequest):
    return validate_event(request.event_type, request.payload)


# ---------------------------------------------------------------------------
# Policy Registry
# ---------------------------------------------------------------------------

@router.post("/neuro/policies", summary="Register policy do",
    response_model=NeuroEventPolicyOut
)
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


@router.get("/neuro/policies", summary="List policies do",
    response_model=NeuroEventPolicyOut
)
async def do_list_policies(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_policies(tenant_id, db)}


@router.get("/neuro/policies/{policy_id}", summary="Get policy do",
    response_model=NeuroEventPolicyOut
)
async def do_get_policy(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = get_active_policy(policy_id, tenant_id, db)
    if not result:
        raise HTTPException(404, "Policy not found")
    return result


@router.get("/neuro/policies/{policy_id}/variants", summary="List policy variants do",
    response_model=NeuroEventPolicyOut
)
async def do_list_policy_variants(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return {"items": list_active_variants(policy_id, tenant_id, db)}

@router.post("/neuro/policies/{policy_id}/select", summary="Select policy variant do",
    response_model=NeuroEventPolicyOut
)
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


@router.post("/neuro/policies/{policy_id}/rollback", summary="Rollback policy do",
    response_model=NeuroEventPolicyOut
)
async def do_rollback_policy(
    policy_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = rollback_policy(policy_id, tenant_id, db)
    if not result:
        raise HTTPException(400, "Kein Rollback moeglich -- weniger als 2 Versionen")
    return result
