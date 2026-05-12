"""Stock Movements API endpoints."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import desc, or_, text
from sqlalchemy.orm import Session

from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.inventory import StockMovement, StockMovementCreate, StockMovementUpdate
from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import StockMovement as StockMovementModel
from ....core.module_registry import registry
from modules.bootstrap import initialize_module_registry
from .inventory_auth import get_current_tenant_id, require_inventory_access

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


def _is_agrar_enabled(db: Session, tenant_id: str) -> bool:
    row = db.execute(
        text(
            """
            SELECT settings
            FROM domain_shared.tenants
            WHERE id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    ).first()
    if row and row[0]:
        raw = row[0]
        try:
            parsed = raw if isinstance(raw, dict) else json.loads(raw)
            modules = parsed.get("enabled_modules") if isinstance(parsed, dict) else None
            if isinstance(modules, list):
                return "agrar" in [str(m).strip() for m in modules]
        except Exception:
            pass

    initialize_module_registry()
    return registry.is_enabled("agrar", tenant_id=tenant_id)


def _assert_agrar_fields_allowed(
    db: Session,
    *,
    tenant_id: str,
    agrar_contract_id: Optional[str],
    weighing_ticket_id: Optional[str],
    lineage_sources_count: int = 0,
) -> None:
    has_agrar_payload = bool(agrar_contract_id or weighing_ticket_id or lineage_sources_count > 0)
    if has_agrar_payload and not _is_agrar_enabled(db, tenant_id):
        raise HTTPException(
            status_code=400,
            detail="Agrar module disabled for tenant; agrar fields/lineage are not allowed",
        )


def _to_schema(row: StockMovementModel) -> StockMovement:
    return StockMovement.model_validate(
        {
            "id": str(row.id),
            "article_id": str(row.article_id),
            "warehouse_id": str(row.warehouse_id),
            "movement_type": row.movement_type,
            "quantity": row.quantity,
            "unit_cost": row.unit_cost,
            "unit": row.unit,
            "movement_number": row.movement_number,
            "movement_date": row.movement_date,
            "movement_time": row.movement_time,
            "reference_number": row.reference_number,
            "notes": row.notes,
            "warehouse_location": row.warehouse_location,
            "charge": row.charge,
            "booking_user": row.booking_user,
            "auto_created": bool(row.auto_created),
            "linked_order_id": str(row.linked_order_id) if row.linked_order_id else None,
            "ownership_type": row.ownership_type or "owned",
            "owner_partner_id": row.owner_partner_id,
            "agrar_contract_id": row.agrar_contract_id,
            "weighing_ticket_id": row.weighing_ticket_id,
            "storage_fee_relevant": bool(row.storage_fee_relevant),
            "storage_fee_start_date": row.storage_fee_start_date,
            "storage_fee_monthly_rate": row.storage_fee_monthly_rate,
            "storage_fee_last_charged_until": row.storage_fee_last_charged_until,
            "previous_stock": row.previous_stock,
            "new_stock": row.new_stock,
            "total_cost": row.total_cost,
            "tenant_id": str(row.tenant_id),
            "created_at": row.created_at,
        }
    )


@router.get("/", response_model=PaginatedResponse[StockMovement])
async def list_stock_movements(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    article_id: Optional[str] = Query(None, description="Filter by article ID"),
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse ID"),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    search: Optional[str] = Query(None, description="Search in movement/reference/order fields"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Return a paginated list of stock movements."""
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT

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
                StockMovementModel.movement_number.ilike(like),
                StockMovementModel.reference_number.ilike(like),
                StockMovementModel.notes.ilike(like),
                StockMovementModel.charge.ilike(like),
                StockMovementModel.booking_user.ilike(like),
            )
        )

    total = query.count()
    items = query.order_by(desc(StockMovementModel.created_at)).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[_to_schema(item) for item in items],
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
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT

    movement = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.id == movement_id,
            StockMovementModel.tenant_id == effective_tenant,
        )
        .first()
    )

    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")

    return _to_schema(movement)


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

    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT

    service = InventoryService(db)
    _assert_agrar_fields_allowed(
        db,
        tenant_id=effective_tenant,
        agrar_contract_id=movement_data.agrar_contract_id,
        weighing_ticket_id=movement_data.weighing_ticket_id,
        lineage_sources_count=len(movement_data.lineage_sources or []),
    )
    try:
        movement = service.process_stock_movement(
            article_id=movement_data.article_id,
            warehouse_id=movement_data.warehouse_id,
            movement_type=movement_data.movement_type,
            quantity=movement_data.quantity,
            unit_cost=movement_data.unit_cost,
            unit=movement_data.unit,
            movement_number=movement_data.movement_number,
            movement_date=movement_data.movement_date,
            movement_time=movement_data.movement_time,
            reference_number=movement_data.reference_number,
            notes=movement_data.notes,
            warehouse_location=movement_data.warehouse_location,
            charge=movement_data.charge,
            booking_user=movement_data.booking_user,
            auto_created=movement_data.auto_created,
            linked_order_id=movement_data.linked_order_id,
            ownership_type=movement_data.ownership_type,
            owner_partner_id=movement_data.owner_partner_id,
            agrar_contract_id=movement_data.agrar_contract_id,
            weighing_ticket_id=movement_data.weighing_ticket_id,
            storage_fee_relevant=movement_data.storage_fee_relevant,
            storage_fee_start_date=movement_data.storage_fee_start_date,
            storage_fee_monthly_rate=movement_data.storage_fee_monthly_rate,
            storage_fee_last_charged_until=movement_data.storage_fee_last_charged_until,
            tenant_id=effective_tenant,
        )
        if not movement.movement_number:
            movement.movement_number = f"MOV-{str(movement.id)[:8]}"
            db.commit()
            db.refresh(movement)

        if movement_data.lineage_sources:
            if not movement_data.charge:
                raise HTTPException(status_code=400, detail="charge is required when lineage_sources are provided")
            if movement_data.process_type is None:
                raise HTTPException(status_code=400, detail="process_type is required when lineage_sources are provided")

            for src in movement_data.lineage_sources:
                db.execute(
                    text(
                        """
                        INSERT INTO domain_inventory.charge_lineage_links
                        (id, tenant_id, article_id, from_charge, to_charge, process_type, quantity_share, share_percent,
                         source_movement_id, target_movement_id, notes, created_by, created_at)
                        VALUES
                        (:id, :tenant_id, :article_id, :from_charge, :to_charge, :process_type, :quantity_share, :share_percent,
                         :source_movement_id, :target_movement_id, :notes, :created_by, NOW())
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tenant_id": effective_tenant,
                        "article_id": movement_data.article_id,
                        "from_charge": src.from_charge,
                        "to_charge": movement_data.charge,
                        "process_type": movement_data.process_type,
                        "quantity_share": src.quantity_share,
                        "share_percent": src.share_percent,
                        "source_movement_id": src.source_movement_id,
                        "target_movement_id": str(movement.id),
                        "notes": src.notes,
                        "created_by": movement_data.booking_user,
                    },
                )
            db.commit()
        return _to_schema(movement)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{movement_id}", response_model=StockMovement)
async def update_stock_movement(
    movement_id: str,
    movement_data: StockMovementUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    """Update stock movement metadata (non-stock impacting fields)."""
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT

    movement = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.id == movement_id,
            StockMovementModel.tenant_id == effective_tenant,
        )
        .first()
    )
    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")

    _assert_agrar_fields_allowed(
        db,
        tenant_id=effective_tenant,
        agrar_contract_id=movement_data.agrar_contract_id,
        weighing_ticket_id=movement_data.weighing_ticket_id,
    )

    payload = movement_data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(movement, key, value)

    movement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(movement)
    return _to_schema(movement)


@router.delete("/{movement_id}", status_code=204, response_class=Response)
async def delete_stock_movement(
    movement_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
) -> Response:
    """Delete a stock movement record."""
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT

    movement = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.id == movement_id,
            StockMovementModel.tenant_id == effective_tenant,
        )
        .first()
    )
    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")

    db.delete(movement)
    db.commit()
    return Response(status_code=204)


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

    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    movements = (
        db.query(StockMovementModel)
        .filter(
            StockMovementModel.article_id == article_id,
            StockMovementModel.tenant_id == effective_tenant,
            StockMovementModel.created_at >= cutoff_date,
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
        "net_quantity_change": 0,
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
