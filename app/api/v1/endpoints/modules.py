"""
Runtime module visibility endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.core.module_registry import registry
from modules.bootstrap import initialize_module_registry

router = APIRouter(tags=["modules"])


@router.get("/modules")
async def list_modules():
    initialize_module_registry()
    return {"items": registry.as_dict()}


@router.get("/modules/{module_name}")
async def get_module(module_name: str):
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
        "enabled": registry.is_enabled(module.name),
    }
