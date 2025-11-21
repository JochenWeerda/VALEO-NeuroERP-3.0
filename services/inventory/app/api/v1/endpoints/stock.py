"""Endpoints für artikelbezogene Operationen und Bewegungen."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.schemas import ArticleSummary, StockMovementCreate, StockMovementRecord
from app.services import InventoryService

router = APIRouter()


@router.get("/articles", response_model=dict[str, list[ArticleSummary]])
async def list_articles(
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, list[ArticleSummary]]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    articles = await service.list_articles()
    return {"items": articles}


@router.get("/stock-movements", response_model=dict[str, list[StockMovementRecord]])
async def list_stock_movements(
    limit: int = Query(default=100, ge=1, le=500),
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, list[StockMovementRecord]]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    records = await service.list_stock_movements(limit=limit)
    return {"items": records}


@router.post(
    "/stock-movements",
    response_model=StockMovementRecord,
    status_code=status.HTTP_201_CREATED,
)
async def create_stock_movement(
    payload: StockMovementCreate,
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> StockMovementRecord:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    try:
        return await service.create_stock_movement(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

