"""Agrar contract endpoints — thin handlers, all logic in AgrarContractService."""

from datetime import datetime
from typing import Literal, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema, PaginatedResponse
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.infrastructure.models.l3c_models import AgrarContract, AgrarContractAllocation  # noqa: F401
from app.services.agrar_contract_service import AgrarContractService
from app.api.v1.schemas.agrar_contracts_schemas import (
    AgrarContractCreate,
    AgrarContractOut,
    AgrarContractUpdate,
    ContractAllocationCreate,
    ContractAllocationOut,
)

router = APIRouter()

ContractStatus = Literal["open", "partially_allocated", "fulfilled", "cancelled"]
PricingModel = Literal["fixed", "follow", "pool"]
ContractType = Literal["buy", "sell"]


# ── Pydantic schemas ──────────────────────────────────────────────────────────

# ── serialiser ────────────────────────────────────────────────────────────────

def _to_out(obj) -> AgrarContractOut:
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


def _to_alloc_out(row) -> ContractAllocationOut:
    return ContractAllocationOut(
        id=row.id,
        contract_id=row.contract_id,
        ticket_id=row.ticket_id,
        allocation_quantity_kg=float(row.allocation_quantity_kg),
        allocated_at=row.allocated_at,
        note=row.note,
    )


def _svc_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, EntityNotFoundError):
        return HTTPException(status_code=404, detail=exc.detail)
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail=exc.detail)
    if isinstance(exc, ValidationFailedError):
        return HTTPException(status_code=422, detail=exc.detail)
    raise exc


def _get_contract_or_404(db: Session, contract_id: str, tenant_id: str) -> AgrarContract:
    """Helper used by route handlers and tests: fetch contract or raise 404."""
    contract = (
        db.query(AgrarContract)
        .filter(AgrarContract.tenant_id == tenant_id, AgrarContract.id == contract_id)
        .first()
    )
    if contract is None:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id!r} not found")
    return contract


# ── route handlers ────────────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[AgrarContractOut], summary="Agrar contracts auflisten")
async def list_agrar_contracts(
    status: Optional[ContractStatus] = Query(None),
    pricing_model: Optional[PricingModel] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    svc = AgrarContractService(db, tenant_id)
    items, total = svc.list_contracts(status=status, pricing_model=pricing_model, skip=skip, limit=limit)
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[AgrarContractOut](
        items=[_to_out(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.get("/{contract_id}", response_model=AgrarContractOut, summary="Agrar contract abrufen")
async def get_agrar_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _to_out(AgrarContractService(db, tenant_id).get_contract(contract_id))
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.post("/", response_model=AgrarContractOut, status_code=201, summary="Agrar contract anlegen")
async def create_agrar_contract(
    payload: AgrarContractCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _to_out(AgrarContractService(db, tenant_id).create_contract(payload.model_dump()))
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.patch("/{contract_id}", response_model=AgrarContractOut, summary="Agrar contract aktualisieren")
async def update_agrar_contract(
    contract_id: str,
    payload: AgrarContractUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _to_out(AgrarContractService(db, tenant_id).update_contract(contract_id, payload.model_dump(exclude_unset=True)))
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.post("/{contract_id}/allocations", response_model=ContractAllocationOut, status_code=201, summary="Contract quantity zuweisen")
async def allocate_contract_quantity(
    contract_id: str,
    payload: ContractAllocationCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        alloc = AgrarContractService(db, tenant_id).allocate(
            contract_id, payload.allocation_quantity_kg, payload.ticket_id, payload.note
        )
        return _to_alloc_out(alloc)
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.get("/{contract_id}/allocations", response_model=list[ContractAllocationOut], summary="Contract allocations auflisten")
async def list_contract_allocations(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_contract_or_404(db, contract_id, tenant_id)
    rows = (
        db.query(AgrarContractAllocation)
        .filter(
            AgrarContractAllocation.contract_id == contract_id,
            AgrarContractAllocation.tenant_id == tenant_id,
        )
        .order_by(AgrarContractAllocation.allocated_at.desc())
        .all()
    )
    return [_to_alloc_out(r) for r in rows]


@router.delete("/{contract_id}", status_code=204, response_class=Response, response_model=None, summary="Contract löschen")
async def delete_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        AgrarContractService(db, tenant_id).delete_contract(contract_id)
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.post("/{contract_id}/cancel", response_model=AgrarContractOut, summary="Contract stornieren")
async def cancel_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _to_out(AgrarContractService(db, tenant_id).cancel_contract(contract_id))
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)


@router.post("/{contract_id}/close", response_model=AgrarContractOut, summary="Contract abschließen")
async def close_contract(
    contract_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _to_out(AgrarContractService(db, tenant_id).close_contract(contract_id))
    except (EntityNotFoundError, ConflictError, ValidationFailedError) as exc:
        raise _svc_errors(exc)
