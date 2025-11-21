from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Customer
from app.db.session import get_session
from app.schemas import CustomerCreate, CustomerListResponse, CustomerRead, CustomerUpdate

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(default=None, description="Case-insensitive search in display_name"),
    session: AsyncSession = Depends(get_session),
) -> CustomerListResponse:
    filters = [Customer.tenant_id == settings.DEFAULT_TENANT_ID]
    if search:
        filters.append(Customer.display_name.ilike(f"%{search}%"))

    total_stmt = select(func.count()).select_from(Customer).where(*filters)
    total = await session.scalar(total_stmt)

    stmt = (
        select(Customer)
        .where(*filters)
        .offset(skip)
        .limit(limit)
        .order_by(Customer.created_at.desc())
    )
    result = await session.execute(stmt)
    items = [CustomerRead.model_validate(row) for row in result.scalars().all()]
    return CustomerListResponse(items=items, total=total or 0)


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate, session: AsyncSession = Depends(get_session)) -> CustomerRead:
    customer = Customer(
        tenant_id=settings.DEFAULT_TENANT_ID,
        display_name=payload.display_name,
        type=payload.type,
        status=payload.status,
        email=payload.email,
        phone=payload.phone,
        industry=payload.industry,
        region=payload.region,
        notes=payload.notes,
    )
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return CustomerRead.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: UUID, session: AsyncSession = Depends(get_session)) -> CustomerRead:
    customer = await session.get(Customer, customer_id)
    if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    session: AsyncSession = Depends(get_session),
) -> CustomerRead:
    customer = await session.get(Customer, customer_id)
    if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    await session.commit()
    await session.refresh(customer)
    return CustomerRead.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    customer = await session.get(Customer, customer_id)
    if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Customer not found")
    await session.delete(customer)
    await session.commit()
