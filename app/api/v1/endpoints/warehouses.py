"""
Warehouse management endpoints

Der Mandant kommt aus dem Kontext. Bis 08.10.2026 lasen, aenderten und
stilllegten diese Wege jedes Lager ueber seine Id allein, das Anlegen nahm den
Mandanten aus dem Payload und die Liste aus dem Query — ohne Rollenpruefung.
Schreiben verlangt jetzt die Lager-Adminrolle (wie /inventory/warehouses).
"""

from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....domains.inventory.api.inventory_auth import get_current_tenant_id, require_inventory_admin
from ....infrastructure.models import Warehouse as WarehouseModel
from app.core.uuid7 import uuid7
from ..schemas.base import PaginatedResponse
from ..schemas.inventory import Warehouse, WarehouseCreate, WarehouseUpdate

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.warehouses_schemas import WarehousesOut


router = APIRouter()



@router.get("/integrations/superglue/carrier-rollout", response_model=WarehousesOut, summary="Superglue carrier rollout abrufen")
async def get_superglue_carrier_rollout(tenant_id: str = Depends(get_tenant_id)):
    """Thin logistics rollout surface for Superglue carrier connectors."""
    from app.integrations.services.superglue_domain_rollouts import build_superglue_domain_rollout_summary

    summary = build_superglue_domain_rollout_summary(tenant_id)
    domain = next((item for item in summary["domains"] if item["domain_key"] == "logistics"), None)
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_key": "logistics",
        "rollout": domain or {"domain_key": "logistics", "connector_count": 0, "connectors": []},
        "schema_version": 1,
    }


@router.get("/", response_model=PaginatedResponse[Warehouse], summary="Warehouses auflisten")
async def list_warehouses(
    search: Optional[str] = Query(None, description="Search in warehouse code or name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
    effective_tenant: str = Depends(get_tenant_id),
):
    """Return a paginated list of warehouses."""

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


@router.get("/{warehouse_id}", response_model=Warehouse, summary="Warehouse abrufen")
async def get_warehouse(
    warehouse_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Fetch a single warehouse by identifier."""
    warehouse = db.query(WarehouseModel).filter(
        WarehouseModel.id == warehouse_id, WarehouseModel.tenant_id == tenant_id
    ).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return Warehouse.model_validate(warehouse)


@router.post("/", response_model=Warehouse, status_code=201, summary="Warehouse anlegen")
async def create_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Neues Lager anlegen — im Mandanten aus dem Kontext, nicht aus dem Payload."""
    existing = db.query(WarehouseModel).filter(
        WarehouseModel.warehouse_code == payload.warehouse_code,
        WarehouseModel.tenant_id == tenant_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Warehouse code already exists for this tenant")
    wh = WarehouseModel(
        id=str(uuid7()),
        warehouse_code=payload.warehouse_code,
        name=payload.name,
        address=payload.address,
        city=payload.city,
        postal_code=payload.postal_code,
        country=payload.country,
        contact_person=payload.contact_person,
        phone=payload.phone,
        email=payload.email,
        warehouse_type=payload.warehouse_type,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return Warehouse.model_validate(wh)


@router.put("/{warehouse_id}", response_model=Warehouse, summary="Warehouse aktualisieren")
async def update_warehouse(
    warehouse_id: str,
    payload: WarehouseUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Lager aktualisieren."""
    wh = db.query(WarehouseModel).filter(
        WarehouseModel.id == warehouse_id, WarehouseModel.tenant_id == tenant_id
    ).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(wh, field, value)
    db.commit()
    db.refresh(wh)
    return Warehouse.model_validate(wh)


@router.delete("/{warehouse_id}", status_code=204, response_class=Response, response_model=None, summary="Warehouse löschen")
async def delete_warehouse(
    warehouse_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Lager deaktivieren (Soft-Delete)."""
    wh = db.query(WarehouseModel).filter(
        WarehouseModel.id == warehouse_id, WarehouseModel.tenant_id == tenant_id
    ).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    wh.is_active = False
    db.commit()

