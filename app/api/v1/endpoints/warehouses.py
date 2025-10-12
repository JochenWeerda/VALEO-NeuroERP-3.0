"""
Warehouse management endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import Warehouse as WarehouseModel
from ..schemas.base import PaginatedResponse
from ..schemas.inventory import Warehouse

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Warehouse])
async def list_warehouses(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in warehouse code or name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of warehouses."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(WarehouseModel).filter(WarehouseModel.is_active == True)  # noqa: E712
    query = query.filter(WarehouseModel.tenant_id == effective_tenant)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (WarehouseModel.warehouse_code.ilike(like)) | (WarehouseModel.name.ilike(like))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[Warehouse](
        items=[Warehouse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse(warehouse_id: str, db: Session = Depends(get_db)):
    """Fetch a single warehouse by identifier."""
    warehouse = db.query(WarehouseModel).filter(WarehouseModel.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return Warehouse.model_validate(warehouse)

