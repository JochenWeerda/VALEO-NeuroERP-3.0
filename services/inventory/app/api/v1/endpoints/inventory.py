"""Inventory Operations."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.schemas import LotListResponse, LotTraceResponse, ReceiptCreate, StockItemRead, TransferCreate
from app.services import InventoryService

router = APIRouter()


@router.get("/lots", response_model=LotListResponse)
async def list_lots(
    search: str | None = Query(default=None, description="Filter für SKU, Lot-Nummer, Lagerort oder Warehouse-Code"),
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> LotListResponse:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    return await service.list_lots(search=search)


@router.post("/receipts", response_model=StockItemRead, status_code=status.HTTP_201_CREATED)
async def receive_stock(
    payload: ReceiptCreate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> StockItemRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.receive_stock(payload)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/transfers", response_model=StockItemRead)
async def transfer_stock(
    payload: TransferCreate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> StockItemRead:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.transfer_stock(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/lots/{lot_id}", response_model=LotTraceResponse)
async def trace_lot(
    lot_id: UUID,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> LotTraceResponse:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.trace_lot(lot_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
