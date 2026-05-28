"""
Runtime module visibility endpoints.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.module_registry import registry
from modules.agrar.contracts.events_v1 import AGRAR_EVENT_CONTRACTS_V1
from modules.agrar.contracts.hooks_v1 import agrar_hooks_as_dict
from modules.bootstrap import initialize_module_registry

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.modules_schemas import ModulesOut


router = APIRouter(tags=["modules"])


@router.get("/modules", summary="Modules auflisten",
    response_model=ModulesOut
)
async def list_modules(tenant_id: Optional[str] = Query(None)):
    initialize_module_registry()
    return {"items": registry.as_dict(tenant_id=tenant_id), "tenant_id": tenant_id}


@router.get("/modules/{module_name}", summary="Module abrufen",
    response_model=ModulesOut
)
async def get_module(module_name: str, tenant_id: Optional[str] = Query(None)):
    initialize_module_registry()
    module = registry.get(module_name)
    if not module:
        raise HTTPException(status_code=404, detail=f"Unknown module: {module_name}")
    return {
        "name": module.name,
        "title": module.title,
        "version": module.version,
        "description": module.description,
        "required_modules": module.required_modules,
        "enabled": registry.is_enabled(module.name, tenant_id=tenant_id),
        "tenant_id": tenant_id,
    }


@router.get("/modules/agrar/contracts", summary="Agrar contracts abrufen",
    response_model=ModulesOut
)
async def get_agrar_contracts():
    initialize_module_registry()
    event_schemas = {
        event_name: model.model_json_schema()
        for event_name, model in AGRAR_EVENT_CONTRACTS_V1.items()
    }
    return {
        "event_contracts": event_schemas,
        "hook_contracts": agrar_hooks_as_dict(),
    }
