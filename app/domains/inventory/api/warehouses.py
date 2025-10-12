"""
Warehouse API endpoints
Full CRUD for warehouse management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import Warehouse as WarehouseModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.inventory import Warehouse, WarehouseCreate, WarehouseUpdate

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Warehouse])
async def list_warehouses(
    tenant_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return a paginated list of warehouses."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(WarehouseModel).filter(WarehouseModel.tenant_id == effective_tenant)
    
    if is_active is not None:
        query = query.filter(WarehouseModel.is_active == is_active)

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[Warehouse.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
    )


@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse(
    warehouse_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single warehouse by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    warehouse = (
        db.query(WarehouseModel)
        .filter(
            WarehouseModel.id == warehouse_id,
            WarehouseModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    return Warehouse.model_validate(warehouse)


@router.post("/", response_model=Warehouse, status_code=201)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new warehouse."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    warehouse = WarehouseModel(
        **warehouse_data.model_dump(),
        tenant_id=effective_tenant
    )
    
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    
    return Warehouse.model_validate(warehouse)


@router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse(
    warehouse_id: str,
    warehouse_data: WarehouseUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing warehouse."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    warehouse = (
        db.query(WarehouseModel)
        .filter(
            WarehouseModel.id == warehouse_id,
            WarehouseModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    update_data = warehouse_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(warehouse, key, value)
    
    db.commit()
    db.refresh(warehouse)
    
    return Warehouse.model_validate(warehouse)


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a warehouse (soft delete)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    warehouse = (
        db.query(WarehouseModel)
        .filter(
            WarehouseModel.id == warehouse_id,
            WarehouseModel.tenant_id == effective_tenant
        )
        .first()
    )
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    warehouse.is_active = False
    db.commit()
    
    return None

