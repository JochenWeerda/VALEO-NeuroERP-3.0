"""
Inventory Reports API endpoints
Analytics and reporting for inventory management
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ..application.services.inventory_service import InventoryService
from ..application.services.replenishment_service import ReplenishmentService
from .inventory_auth import require_inventory_access, get_current_tenant_id

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/stock-alerts")
async def get_stock_alerts(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get low stock alerts for all articles."""
    effective_tenant = tenant_id or effective_tenant

    service = InventoryService(db)
    alerts = service.check_low_stock_alerts(effective_tenant)

    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_count": len([a for a in alerts if a["current_stock"] <= 0])
    }


@router.get("/inventory-value")
async def get_inventory_value(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get total inventory value and statistics."""
    effective_tenant = tenant_id or effective_tenant

    service = InventoryService(db)
    value_data = service.calculate_inventory_value(effective_tenant)

    return value_data


@router.get("/replenishment-suggestions")
async def get_replenishment_suggestions(
    tenant_id: Optional[str] = Query(None),
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get automated replenishment suggestions."""
    effective_tenant = tenant_id or effective_tenant

    service = ReplenishmentService(db)
    suggestions = service.get_replenishment_suggestions(effective_tenant, days_ahead)

    # Group by priority
    by_priority = {}
    for suggestion in suggestions:
        priority = suggestion["priority"]
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(suggestion)

    return {
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "by_priority": by_priority,
        "estimated_total_cost": sum(s["estimated_cost"] or 0 for s in suggestions if s["estimated_cost"])
    }


@router.get("/slow-moving-inventory")
async def get_slow_moving_inventory(
    tenant_id: Optional[str] = Query(None),
    days_threshold: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get slow-moving inventory report."""
    effective_tenant = tenant_id or effective_tenant

    service = ReplenishmentService(db)
    slow_moving = service.get_slow_moving_inventory(effective_tenant, days_threshold)

    return {
        "slow_moving_items": slow_moving,
        "total_items": len(slow_moving),
        "total_value": sum(item["stock_value"] for item in slow_moving)
    }


@router.get("/purchase-order-suggestions")
async def get_purchase_order_suggestions(
    tenant_id: Optional[str] = Query(None),
    supplier_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get purchase order suggestions grouped by supplier."""
    effective_tenant = tenant_id or effective_tenant

    service = ReplenishmentService(db)
    suggestions_by_supplier = service.generate_purchase_order_suggestions(
        effective_tenant, supplier_filter
    )

    # Calculate totals
    total_suggestions = sum(len(items) for items in suggestions_by_supplier.values())
    total_cost = sum(
        sum(item["estimated_cost"] or 0 for item in items if item["estimated_cost"])
        for items in suggestions_by_supplier.values()
    )

    return {
        "suggestions_by_supplier": suggestions_by_supplier,
        "total_suggestions": total_suggestions,
        "total_suppliers": len(suggestions_by_supplier),
        "estimated_total_cost": total_cost
    }


@router.get("/turnover-analysis")
async def get_turnover_analysis(
    tenant_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get inventory turnover analysis."""
    effective_tenant = tenant_id or effective_tenant

    service = ReplenishmentService(db)
    analysis = service.get_inventory_turnover_report(effective_tenant, period_days)

    return analysis


@router.get("/stock-levels")
async def get_stock_levels_report(
    tenant_id: Optional[str] = Query(None),
    category_filter: Optional[str] = Query(None),
    warehouse_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get comprehensive stock levels report."""
    from ....infrastructure.models import Article as ArticleModel

    effective_tenant = tenant_id or effective_tenant

    query = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.tenant_id == effective_tenant,
            ArticleModel.is_active == True
        )
    )

    if category_filter:
        query = query.filter(ArticleModel.category == category_filter)

    articles = query.all()

    report = {
        "total_articles": len(articles),
        "categories": {},
        "stock_summary": {
            "total_current_stock": 0,
            "total_available_stock": 0,
            "total_reserved_stock": 0,
            "low_stock_count": 0,
            "out_of_stock_count": 0
        },
        "articles": []
    }

    for article in articles:
        current_stock = float(article.current_stock or 0)
        available_stock = float(article.available_stock or 0)
        reserved_stock = float(article.reserved_stock or 0)
        min_stock = float(article.min_stock or 0)

        # Update summary
        report["stock_summary"]["total_current_stock"] += current_stock
        report["stock_summary"]["total_available_stock"] += available_stock
        report["stock_summary"]["total_reserved_stock"] += reserved_stock

        if current_stock <= 0:
            report["stock_summary"]["out_of_stock_count"] += 1
        elif current_stock < min_stock:
            report["stock_summary"]["low_stock_count"] += 1

        # Update categories
        category = article.category or "Uncategorized"
        if category not in report["categories"]:
            report["categories"][category] = {
                "count": 0,
                "total_stock": 0,
                "total_value": 0
            }

        report["categories"][category]["count"] += 1
        report["categories"][category]["total_stock"] += current_stock
        if article.sales_price:
            report["categories"][category]["total_value"] += current_stock * float(article.sales_price)

        # Add article details
        report["articles"].append({
            "id": article.id,
            "article_number": article.article_number,
            "name": article.name,
            "category": category,
            "current_stock": current_stock,
            "available_stock": available_stock,
            "reserved_stock": reserved_stock,
            "min_stock": min_stock,
            "unit": article.unit,
            "sales_price": float(article.sales_price) if article.sales_price else None,
            "stock_status": "out_of_stock" if current_stock <= 0 else "low_stock" if current_stock < min_stock else "normal"
        })

    return report