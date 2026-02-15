"""
Weighing tickets endpoints (l3c-wiegeschein)
GET/POST/PUT for weighing tickets.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....domains.shared.events import IntegrationEvent, get_event_publisher
from ....infrastructure.eventbus.outbox import OutboxPublisher
from ....infrastructure.models import AgrarContract, AgrarContractAllocation, WeighingTicket
from modules.agrar.services.weighing_domain import (
    derive_billing_weight as _derive_billing_weight_impl,
    resolve_ticket_allocation_quantity as _resolve_ticket_allocation_quantity_impl,
    validate_and_compute_weights as _validate_and_compute_weights_impl,
)
from .agrar_contracts import _compute_status
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = "system"


class WeighingTicketOut(BaseSchema):
    id: str
    ticket_number: str
    scale_id: Optional[str] = None
    vehicle_plate: Optional[str] = None
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = None
    protein_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight: Optional[float] = None
    billing_weight: Optional[float] = None
    quality_data: Optional[dict[str, Any]] = None
    contract_id: Optional[str] = None
    allocated_quantity_kg: Optional[float] = None
    allocation_status: Optional[str] = "unallocated"
    status: str = "open"
    direction: str = "in"
    reference_doc: Optional[str] = None


class WeighingTicketCreate(BaseModel):
    ticket_number: str
    scale_id: Optional[str] = None
    vehicle_plate: Optional[str] = None
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    protein_pct: Optional[float] = Field(default=None, ge=0, le=100)
    impurities_pct: Optional[float] = Field(default=None, ge=0, le=100)
    hl_weight: Optional[float] = Field(default=None, ge=0)
    billing_weight: Optional[float] = Field(default=None, ge=0)
    quality_data: Optional[dict[str, Any]] = None
    direction: str = "in"
    reference_doc: Optional[str] = None


class WeighingTicketUpdate(BaseModel):
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    protein_pct: Optional[float] = Field(default=None, ge=0, le=100)
    impurities_pct: Optional[float] = Field(default=None, ge=0, le=100)
    hl_weight: Optional[float] = Field(default=None, ge=0)
    billing_weight: Optional[float] = Field(default=None, ge=0)
    quality_data: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    vehicle_plate: Optional[str] = None


class WeighingTicketContractAllocationRequest(BaseModel):
    contract_id: str
    allocation_quantity_kg: Optional[float] = Field(default=None, gt=0)
    note: Optional[str] = None


class WeighingTicketContractAllocationOut(BaseSchema):
    ticket_id: str
    contract_id: str
    allocation_id: str
    allocation_quantity_kg: float
    contract_remaining_quantity_kg: float
    contract_status: str


def _validate_and_compute_weights(gross_weight: Optional[float], tare_weight: Optional[float], net_weight: Optional[float]) -> float | None:
    return _validate_and_compute_weights_impl(gross_weight, tare_weight, net_weight)


def _resolve_ticket_allocation_quantity(ticket: WeighingTicket, requested_quantity: Optional[float]) -> Decimal:
    return _resolve_ticket_allocation_quantity_impl(ticket, requested_quantity)


def _derive_billing_weight(
    *,
    net_weight: Optional[float],
    billing_weight: Optional[float],
    moisture_pct: Optional[float],
    impurities_pct: Optional[float],
    quality_data: Optional[dict[str, Any]],
) -> Optional[float]:
    return _derive_billing_weight_impl(
        net_weight=net_weight,
        billing_weight=billing_weight,
        moisture_pct=moisture_pct,
        impurities_pct=impurities_pct,
        quality_data=quality_data,
    )


@router.get("/", response_model=PaginatedResponse[WeighingTicketOut])
async def list_weighing_tickets(
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET Wiegescheine ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(WeighingTicket).filter(WeighingTicket.tenant_id == tid)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[WeighingTicketOut](
        items=[WeighingTicketOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=WeighingTicketOut, status_code=201)
async def create_weighing_ticket(
    payload: WeighingTicketCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Wiegescheine anlegen"""
    import uuid
    tid = tenant_id or DEFAULT_TENANT
    ticket = WeighingTicket(
        id=str(uuid.uuid4()),
        ticket_number=payload.ticket_number,
        scale_id=payload.scale_id,
        vehicle_plate=payload.vehicle_plate,
        gross_weight=payload.gross_weight,
        tare_weight=payload.tare_weight,
        net_weight=_validate_and_compute_weights(payload.gross_weight, payload.tare_weight, payload.net_weight),
        first_weighing_at=payload.first_weighing_at,
        second_weighing_at=payload.second_weighing_at,
        moisture_pct=payload.moisture_pct,
        protein_pct=payload.protein_pct,
        impurities_pct=payload.impurities_pct,
        hl_weight=payload.hl_weight,
        billing_weight=_derive_billing_weight(
            net_weight=_validate_and_compute_weights(payload.gross_weight, payload.tare_weight, payload.net_weight),
            billing_weight=payload.billing_weight,
            moisture_pct=payload.moisture_pct,
            impurities_pct=payload.impurities_pct,
            quality_data=payload.quality_data,
        ),
        quality_data=payload.quality_data,
        direction=payload.direction,
        reference_doc=payload.reference_doc,
        tenant_id=tid,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return WeighingTicketOut.model_validate(ticket)


@router.put("/{ticket_id}", response_model=WeighingTicketOut)
async def update_weighing_ticket(
    ticket_id: str,
    payload: WeighingTicketUpdate,
    db: Session = Depends(get_db),
):
    """PUT Wiegescheine ändern"""
    ticket = db.query(WeighingTicket).filter(WeighingTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Weighing ticket not found")
    data = payload.model_dump(exclude_unset=True)
    gross_weight = data.get("gross_weight", ticket.gross_weight)
    tare_weight = data.get("tare_weight", ticket.tare_weight)
    net_weight = data.get("net_weight", ticket.net_weight)
    data["net_weight"] = _validate_and_compute_weights(gross_weight, tare_weight, net_weight)
    data["billing_weight"] = _derive_billing_weight(
        net_weight=data.get("net_weight"),
        billing_weight=data.get("billing_weight", ticket.billing_weight),
        moisture_pct=data.get("moisture_pct", ticket.moisture_pct),
        impurities_pct=data.get("impurities_pct", ticket.impurities_pct),
        quality_data=data.get("quality_data", ticket.quality_data),
    )

    for field, val in data.items():
        setattr(ticket, field, val)
    db.commit()
    db.refresh(ticket)
    return WeighingTicketOut.model_validate(ticket)


@router.post("/{ticket_id}/allocate-contract", response_model=WeighingTicketContractAllocationOut, status_code=201)
async def allocate_ticket_to_contract(
    ticket_id: str,
    payload: WeighingTicketContractAllocationRequest,
    db: Session = Depends(get_db),
):
    ticket = db.query(WeighingTicket).filter(WeighingTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Weighing ticket not found")
    contract = db.query(AgrarContract).filter(AgrarContract.id == payload.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if ticket.tenant_id != contract.tenant_id:
        raise HTTPException(status_code=400, detail="Ticket and contract tenant mismatch")
    if contract.status in {"cancelled", "fulfilled"}:
        raise HTTPException(status_code=400, detail=f"Contract cannot be allocated in status {contract.status}")

    allocation_quantity = _resolve_ticket_allocation_quantity(ticket, payload.allocation_quantity_kg)
    remaining = Decimal(str(contract.remaining_quantity_kg))
    if allocation_quantity > remaining:
        raise HTTPException(status_code=400, detail="Allocation exceeds remaining contract quantity")

    publisher = get_event_publisher()
    outbox = OutboxPublisher(db, publisher)

    try:
        contract.remaining_quantity_kg = remaining - allocation_quantity
        contract.status = _compute_status(
            Decimal(str(contract.total_quantity_kg)),
            Decimal(str(contract.remaining_quantity_kg)),
            contract.status,
        )

        allocation = AgrarContractAllocation(
            id=str(uuid.uuid4()),
            contract_id=contract.id,
            ticket_id=ticket.id,
            allocation_quantity_kg=float(allocation_quantity),
            note=payload.note,
            tenant_id=ticket.tenant_id,
        )
        db.add(allocation)

        ticket.contract_id = contract.id
        ticket.allocated_quantity_kg = float(allocation_quantity)
        ticket.allocation_status = "allocated"

        now = datetime.utcnow()
        event_payload = {
            "ticket_id": ticket.id,
            "contract_id": contract.id,
            "allocation_id": allocation.id,
            "allocation_quantity_kg": float(allocation_quantity),
            "remaining_quantity_kg": float(contract.remaining_quantity_kg),
        }

        await outbox.store_event(
            IntegrationEvent(
                aggregate_id=ticket.id,
                timestamp=now,
                event_type="agrar.weighing_ticket.allocated",
                payload=event_payload,
            ),
            tenant_id=ticket.tenant_id,
        )
        await outbox.store_event(
            IntegrationEvent(
                aggregate_id=contract.id,
                timestamp=now,
                event_type="agrar.contract.allocated",
                payload=event_payload,
            ),
            tenant_id=ticket.tenant_id,
        )

        db.commit()
        db.refresh(contract)
        db.refresh(allocation)
    except Exception:
        db.rollback()
        raise

    return WeighingTicketContractAllocationOut(
        ticket_id=ticket.id,
        contract_id=contract.id,
        allocation_id=allocation.id,
        allocation_quantity_kg=float(allocation.allocation_quantity_kg),
        contract_remaining_quantity_kg=float(contract.remaining_quantity_kg),
        contract_status=contract.status,
    )
