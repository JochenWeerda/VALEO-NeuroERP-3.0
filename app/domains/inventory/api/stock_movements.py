"""
Stock Movements API endpoints
Full CRUD for stock movement management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from ....core.database import get_db
from ....infrastructure.models import StockMovement as StockMovementModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.inventory import StockMovement, StockMovementCreate
from .inventory_auth import require_inventory_access, get_current_tenant_id

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[StockMovement])
async def list_stock_movements(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    article_id: Optional[str] = Query(None, description="Filter by article ID"),
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse ID"),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    search: Optional[str] = Query(None, description="Search in reference number or notes"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Return a paginated list of stock movements."""
    effective_tenant = tenant_id or effective_tenant

    query = db.query(StockMovementModel).filter(StockMovementModel.tenant_id == effective_tenant)

    if article_id:
        query = query.filter(StockMovementModel.article_id == article_id)
    if warehouse_id:
        query = query.filter(StockMovementModel.warehouse_id == warehouse_id)
    if movement_type:
        query = query.filter(StockMovementModel.movement_type == movement_type)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                StockMovementModel.reference_number.ilike(like),
                StockMovementModel.notes.ilike(like),
            )
        )

    total = query.count()
    items = query.order_by(desc(StockMovementModel.created_at)).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[StockMovement.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{movement_id}", response_model=StockMovement)
async def get_stock_movement(
    movement_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get a single stock movement by ID."""
    effective_tenant = tenant_id or effective_tenant

    movement = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.id == movement_id,
            StockMovementModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")

    return StockMovement.model_validate(movement)


@router.post("/", response_model=StockMovement, status_code=201)
async def create_stock_movement(
    movement_data: StockMovementCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Create a new stock movement."""
    from ..application.services.inventory_service import InventoryService

    effective_tenant = tenant_id or effective_tenant

    # Use the inventory service to process the movement
    service = InventoryService(db)
    try:
        movement = service.process_stock_movement(
            article_id=movement_data.article_id,
            warehouse_id=movement_data.warehouse_id,
            movement_type=movement_data.movement_type,
            quantity=movement_data.quantity,
            unit_cost=movement_data.unit_cost,
            reference_number=movement_data.reference_number,
            notes=movement_data.notes,
            tenant_id=effective_tenant
        )
        return movement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary/article/{article_id}")
async def get_article_movement_summary(
    article_id: str,
    tenant_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Get movement summary for a specific article."""
    from datetime import datetime, timedelta

    effective_tenant = tenant_id or effective_tenant
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    movements = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.article_id == article_id,
            StockMovementModel.tenant_id == effective_tenant,
            StockMovementModel.created_at >= cutoff_date
        )
        .all()
    )

    summary = {
        "article_id": article_id,
        "period_days": days,
        "total_movements": len(movements),
        "movements_by_type": {},
        "total_quantity_in": 0,
        "total_quantity_out": 0,
        "net_quantity_change": 0
    }

    for movement in movements:
        qty = float(movement.quantity)
        movement_type = movement.movement_type

        if movement_type not in summary["movements_by_type"]:
            summary["movements_by_type"][movement_type] = 0

        summary["movements_by_type"][movement_type] += qty

        if qty > 0:
            summary["total_quantity_in"] += qty
        else:
            summary["total_quantity_out"] += abs(qty)

        summary["net_quantity_change"] += qty

    return summary