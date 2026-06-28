"""Mask ScreenDefinition API — native generator payloads."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.screen_definitions import get_screen_definition
from ....core.tenant import get_tenant_id


router = APIRouter(prefix="/masks", tags=["ui", "masks", "screen-definition"])


@router.get("/{mask_id}/screen-definition", response_model=dict[str, Any], summary="Native ScreenDefinition abrufen")
async def get_mask_screen_definition(
    mask_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert die native ScreenDefinition fuer Generator-faehige Masken."""

    _ = tenant_id
    normalized = mask_id.strip("/")
    definition = get_screen_definition(normalized)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Keine ScreenDefinition fuer Maske {mask_id}")
    return definition
