"""Reporting-Endpunkte für das Inventory-Frontend."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.services import InventoryService

router = APIRouter()


@router.get("/reports/stock-levels")
async def stock_levels(
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, object]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    articles = await service.list_articles()
    total = sum(item.current_stock for item in articles)
    return {
        "totalStock": total,
        "articles": articles,
    }


@router.get("/reports/stock-alerts")
async def stock_alerts(
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, object]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    articles = await service.list_articles()
    alerts = [
        {
            "articleNumber": article.article_number,
            "currentStock": article.current_stock,
            "minStock": article.min_stock or 0,
            "status": "low_stock",
        }
        for article in articles
        if article.min_stock and article.current_stock < article.min_stock
    ]
    return {"items": alerts}


@router.get("/reports/replenishment-suggestions")
async def replenishment_suggestions(
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, object]:
    service = InventoryService(session, event_bus=event_bus, tenant_id=tenant_id)
    articles = await service.list_articles()
    suggestions = [
        {
            "articleNumber": article.article_number,
            "suggestedQty": max((article.min_stock or 0) * 2 - article.current_stock, 0),
            "reason": "below_target",
        }
        for article in articles
        if article.min_stock and article.current_stock < article.min_stock
    ]
    return {"items": suggestions}


@router.get("/reports/turnover-analysis")
async def turnover_analysis(
    session=Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
    event_bus=Depends(get_event_bus),
) -> dict[str, object]:
    # Placeholder values until detailed analytics exist
    return {
        "period": "current_month",
        "throughput": {
            "inbound": 0,
            "outbound": 0,
            "transfers": 0,
        },
    }

