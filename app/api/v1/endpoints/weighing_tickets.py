"""
Weighing tickets endpoints (l3c-wiegeschein)
GET/POST/PUT for weighing tickets.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import WeighingTicket
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
    direction: str = "in"
    reference_doc: Optional[str] = None


class WeighingTicketUpdate(BaseModel):
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    status: Optional[str] = None
    vehicle_plate: Optional[str] = None


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
        net_weight=payload.net_weight,
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
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, val)
    db.commit()
    db.refresh(ticket)
    return WeighingTicketOut.model_validate(ticket)
