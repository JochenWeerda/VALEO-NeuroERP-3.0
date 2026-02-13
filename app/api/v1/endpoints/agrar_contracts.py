"""
Agrar contract endpoints with remaining quantity and allocation logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.models import AgrarContract, AgrarContractAllocation
from app.api.v1.schemas.base import BaseSchema, PaginatedResponse

router = APIRouter()
DEFAULT_TENANT = "system"

ContractStatus = Literal["open", "partially_allocated", "fulfilled", "cancelled"]
PricingModel = Literal["fixed", "follow", "pool"]
ContractType = Literal["buy", "sell"]


def _compute_status(total_quantity: Decimal, remaining_quantity: Decimal, current_status: str) -> str:
    if current_status == "cancelled":
        return "cancelled"
    if remaining_quantity <= Decimal("0"):
        return "fulfilled"
    if remaining_quantity < total_quantity:
        return "partially_allocated"
    return "open"


class AgrarContractOut(BaseSchema):
    id: str
    contract_number: str
    contract_type: ContractType
    harvest_year: int
    partner_id: str
    article_id: str
    pricing_model: PricingModel
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = None
    currency: str = "EUR"
    total_quantity_kg: float
    remaining_quantity_kg: float
    status: ContractStatus
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AgrarContractCreate(BaseModel):
    contract_number: str = Field(..., min_length=3, max_length=50)
    contract_type: ContractType
    harvest_year: int = Field(..., ge=2000, le=2100)
    partner_id: str
    article_id: str
    pricing_model: PricingModel
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = Field(default=None, ge=0)
    currency: str = "EUR"
    total_quantity_kg: float = Field(..., gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AgrarContractUpdate(BaseModel):
    partner_id: Optional[str] = None
    article_id: Optional[str] = None
    pricing_model: Optional[PricingModel] = None
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = Field(default=None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: Optional[ContractStatus] = None


class ContractAllocationCreate(BaseModel):
    allocation_quantity_kg: float = Field(..., gt=0)
    ticket_id: Optional[str] = None
    note: Optional[str] = None


class ContractAllocationOut(BaseSchema):
    id: str
    contract_id: str
    ticket_id: Optional[str] = None
    allocation_quantity_kg: float
    allocated_at: Optional[datetime] = None
    note: Optional[str] = None


def _to_contract_out(obj: AgrarContract) -> AgrarContractOut:
    return AgrarContractOut(
        id=obj.id,
        contract_number=obj.contract_number,
        contract_type=obj.contract_type,
        harvest_year=obj.harvest_year,
        partner_id=obj.partner_id,
        article_id=obj.article_id,
        pricing_model=obj.pricing_model,
        pool_group_id=obj.pool_group_id,
        fixed_price=float(obj.fixed_price) if obj.fixed_price is not None else None,
        currency=obj.currency,
        total_quantity_kg=float(obj.total_quantity_kg),
        remaining_quantity_kg=float(obj.remaining_quantity_kg),
        status=obj.status,
        valid_from=obj.valid_from,
        valid_until=obj.valid_until,
    )


@router.get("/", response_model=PaginatedResponse[AgrarContractOut])
async def list_agrar_contracts(
    tenant_id: Optional[str] = Query(None),
    status: Optional[ContractStatus] = Query(None),
    pricing_model: Optional[PricingModel] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    tid = tenant_id or DEFAULT_TENANT
    query = db.query(AgrarContract).filter(AgrarContract.tenant_id == tid)
    if status:
        query = query.filter(AgrarContract.status == status)
    if pricing_model:
        query = query.filter(AgrarContract.pricing_model == pricing_model)
    total = query.count()
    items = query.order_by(AgrarContract.created_at.desc()).offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[AgrarContractOut](
        items=[_to_contract_out(i) for i in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{contract_id}", response_model=AgrarContractOut)
async def get_agrar_contract(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(AgrarContract).filter(AgrarContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return _to_contract_out(contract)


@router.post("/", response_model=AgrarContractOut, status_code=201)
async def create_agrar_contract(
    payload: AgrarContractCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    tid = tenant_id or DEFAULT_TENANT
    exists = (
        db.query(AgrarContract)
        .filter(AgrarContract.tenant_id == tid, AgrarContract.contract_number == payload.contract_number)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="contract_number already exists")

    contract = AgrarContract(
        id=str(uuid.uuid4()),
        contract_number=payload.contract_number,
        contract_type=payload.contract_type,
        harvest_year=payload.harvest_year,
        partner_id=payload.partner_id,
        article_id=payload.article_id,
        pricing_model=payload.pricing_model,
        pool_group_id=payload.pool_group_id,
        fixed_price=payload.fixed_price,
        currency=payload.currency,
        total_quantity_kg=payload.total_quantity_kg,
        remaining_quantity_kg=payload.total_quantity_kg,
        status="open",
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        tenant_id=tid,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return _to_contract_out(contract)


@router.patch("/{contract_id}", response_model=AgrarContractOut)
async def update_agrar_contract(
    contract_id: str,
    payload: AgrarContractUpdate,
    db: Session = Depends(get_db),
):
    contract = db.query(AgrarContract).filter(AgrarContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] == "cancelled":
        contract.status = "cancelled"
        db.commit()
        db.refresh(contract)
        return _to_contract_out(contract)

    for field, value in data.items():
        setattr(contract, field, value)

    contract.status = _compute_status(
        Decimal(str(contract.total_quantity_kg)),
        Decimal(str(contract.remaining_quantity_kg)),
        contract.status,
    )
    db.commit()
    db.refresh(contract)
    return _to_contract_out(contract)


@router.post("/{contract_id}/allocations", response_model=ContractAllocationOut, status_code=201)
async def allocate_contract_quantity(
    contract_id: str,
    payload: ContractAllocationCreate,
    db: Session = Depends(get_db),
):
    contract = db.query(AgrarContract).filter(AgrarContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.status == "cancelled":
        raise HTTPException(status_code=400, detail="Contract is cancelled")
    if contract.status == "fulfilled":
        raise HTTPException(status_code=400, detail="Contract already fulfilled")

    quantity = Decimal(str(payload.allocation_quantity_kg))
    remaining = Decimal(str(contract.remaining_quantity_kg))
    if quantity > remaining:
        raise HTTPException(status_code=400, detail="Allocation exceeds remaining quantity")

    contract.remaining_quantity_kg = remaining - quantity
    contract.status = _compute_status(
        Decimal(str(contract.total_quantity_kg)),
        Decimal(str(contract.remaining_quantity_kg)),
        contract.status,
    )

    allocation = AgrarContractAllocation(
        id=str(uuid.uuid4()),
        contract_id=contract.id,
        ticket_id=payload.ticket_id,
        allocation_quantity_kg=payload.allocation_quantity_kg,
        note=payload.note,
        tenant_id=contract.tenant_id,
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)

    return ContractAllocationOut(
        id=allocation.id,
        contract_id=allocation.contract_id,
        ticket_id=allocation.ticket_id,
        allocation_quantity_kg=float(allocation.allocation_quantity_kg),
        allocated_at=allocation.allocated_at,
        note=allocation.note,
    )


@router.get("/{contract_id}/allocations", response_model=list[ContractAllocationOut])
async def list_contract_allocations(contract_id: str, db: Session = Depends(get_db)):
    contract = db.query(AgrarContract).filter(AgrarContract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    rows = (
        db.query(AgrarContractAllocation)
        .filter(AgrarContractAllocation.contract_id == contract_id)
        .order_by(AgrarContractAllocation.allocated_at.desc())
        .all()
    )
    return [
        ContractAllocationOut(
            id=row.id,
            contract_id=row.contract_id,
            ticket_id=row.ticket_id,
            allocation_quantity_kg=float(row.allocation_quantity_kg),
            allocated_at=row.allocated_at,
            note=row.note,
        )
        for row in rows
    ]

