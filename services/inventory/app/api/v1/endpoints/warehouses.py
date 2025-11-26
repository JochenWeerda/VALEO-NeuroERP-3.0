"""Warehouse API Endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response

from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.schemas import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services import InventoryService

router = APIRouter()


@router.post("/", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> WarehouseRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.create_warehouse(payload)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/", response_model=list[WarehouseRead])
async def list_warehouses(
    is_active: bool | None = Query(default=None),
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> list[WarehouseRead]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    return await service.list_warehouses(only_active=is_active)


@router.get("/{warehouse_id}", response_model=WarehouseRead)
async def get_warehouse(
    warehouse_id: UUID,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> WarehouseRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.get_warehouse(warehouse_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{warehouse_id}", response_model=WarehouseRead)
async def update_warehouse(
    warehouse_id: UUID,
    payload: WarehouseUpdate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> WarehouseRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.update_warehouse(warehouse_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_warehouse(
    warehouse_id: UUID,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> Response:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        await service.delete_warehouse(warehouse_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
