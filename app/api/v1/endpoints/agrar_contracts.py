"""
Agrar contract endpoints with remaining quantity and allocation logic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_contract_datensatz,
)
from app.core.tenant import get_tenant_id
from app.infrastructure.models import AgrarContract, AgrarContractAllocation
from app.api.v1.schemas.base import BaseSchema, PaginatedResponse
from app.core.uuid7 import uuid7

router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID

ContractStatus = Literal["open", "partially_allocated", "fulfilled", "cancelled"]
PricingModel = Literal["fixed", "follow", "pool"]
ContractType = Literal["buy", "sell"]


def _build_contract_dq_datensatz(data: dict) -> dict:
    return {
        "kontrakt_nr": data.get("contract_number"),
        "lieferant_nr": data.get("partner_id"),
        "ware": data.get("article_id"),
        "menge_tonnen": (
            float(data["total_quantity_kg"]) / 1000.0
            if data.get("total_quantity_kg") is not None
            else None
        ),
        "preis_eur_pro_t": data.get("fixed_price"),
        "kontrakt_status": str(data.get("status") or "AKTIV").upper(),
        "preismodell": data.get("pricing_model"),
    }


def _compute_status(total_quantity: Decimal, remaining_quantity: Decimal, current_status: str) -> str:
    if current_status == "cancelled":
        return "cancelled"
    if remaining_quantity <= Decimal("0"):
        return "fulfilled"
    if remaining_quantity < total_quantity:
        return "partially_allocated"
    return "open"


def _get_contract_or_404(db: Session, contract_id: str, tenant_id: str) -> AgrarContract:
    contract = (
        db.query(AgrarContract)
        .filter(
            AgrarContract.id == contract_id,
            AgrarContract.tenant_id == tenant_id,
        )
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


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
    status: Optional[ContractStatus] = Query(None),
    pricing_model: Optional[PricingModel] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    query = db.query(AgrarContract).filter(AgrarContract.tenant_id == tenant_id)
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
async def get_agrar_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id, tenant_id)
    return _to_contract_out(contract)


@router.post("/", response_model=AgrarContractOut, status_code=201)
async def create_agrar_contract(
    payload: AgrarContractCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    dq_result = evaluate_contract_datensatz(_build_contract_dq_datensatz({
        **payload.model_dump(),
        "status": "AKTIV",
    }))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Kontrakt", dq_result))
    exists = (
        db.query(AgrarContract)
        .filter(AgrarContract.tenant_id == tenant_id, AgrarContract.contract_number == payload.contract_number)
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="contract_number already exists")

    contract = AgrarContract(
        id=uuid7(),
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
        tenant_id=tenant_id,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return _to_contract_out(contract)


@router.patch("/{contract_id}", response_model=AgrarContractOut)
async def update_agrar_contract(
    contract_id: str,
    payload: AgrarContractUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id, tenant_id)

    data = payload.model_dump(exclude_unset=True)
    effective_data = {
        "contract_number": contract.contract_number,
        "partner_id": data.get("partner_id", contract.partner_id),
        "article_id": data.get("article_id", contract.article_id),
        "total_quantity_kg": float(contract.total_quantity_kg),
        "fixed_price": data.get("fixed_price", float(contract.fixed_price) if contract.fixed_price is not None else None),
        "status": data.get("status", contract.status),
        "pricing_model": data.get("pricing_model", contract.pricing_model),
    }
    dq_result = evaluate_contract_datensatz(_build_contract_dq_datensatz(effective_data))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Kontrakt", dq_result))
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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id, tenant_id)
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
        id=uuid7(),
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
async def list_contract_allocations(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _contract = _get_contract_or_404(db, contract_id, tenant_id)  # noqa: F841
    rows = (
        db.query(AgrarContractAllocation)
        .filter(
            AgrarContractAllocation.contract_id == contract_id,
            AgrarContractAllocation.tenant_id == tenant_id,
        )
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



@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht einen Kontrakt (nur im Status 'open' ohne Allokationen)."""
    contract = _get_contract_or_404(db, contract_id, tenant_id)
    if contract.status not in ("open", "draft"):
        raise HTTPException(status_code=400, detail="Only open/draft contracts can be deleted")
    alloc_count = (
        db.query(AgrarContractAllocation)
        .filter(AgrarContractAllocation.contract_id == contract_id)
        .count()
    )
    if alloc_count > 0:
        raise HTTPException(status_code=400, detail="Contract has allocations; cancel instead of delete")
    db.delete(contract)
    db.commit()


@router.post("/{contract_id}/cancel", response_model=AgrarContractOut)
async def cancel_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Storniert einen aktiven Kontrakt."""
    contract = _get_contract_or_404(db, contract_id, tenant_id)
    if contract.status == "cancelled":
        raise HTTPException(status_code=400, detail="Contract is already cancelled")
    if contract.status == "fulfilled":
        raise HTTPException(status_code=400, detail="Fulfilled contracts cannot be cancelled")
    contract.status = "cancelled"
    db.commit()
    db.refresh(contract)
    return _to_contract_out(contract)


@router.post("/{contract_id}/close", response_model=AgrarContractOut)
async def close_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Schließt einen erfüllten Kontrakt ab."""
    contract = _get_contract_or_404(db, contract_id, tenant_id)
    if contract.status not in ("fulfilled", "partially_allocated"):
        raise HTTPException(status_code=400, detail=f"Cannot close contract in status '{contract.status}'")
    contract.status = "closed"
    db.commit()
    db.refresh(contract)
    return _to_contract_out(contract)
