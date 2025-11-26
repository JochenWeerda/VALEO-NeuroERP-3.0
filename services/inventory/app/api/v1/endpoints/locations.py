"""Location Endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.schemas import LocationCreate, LocationRead
from app.services import InventoryService

router = APIRouter()


@router.post("/{warehouse_id}/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def add_location(
    warehouse_id: UUID,
    payload: LocationCreate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> LocationRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.add_location(warehouse_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
