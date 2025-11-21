from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db.models import Customer, Lead
from app.db.session import get_session
from app.schemas import LeadCreate, LeadListResponse, LeadRead, LeadUpdate

router = APIRouter()


def _with_customer_name(leads: list[Lead]) -> None:
    for lead in leads:
        setattr(lead, "customer_name", lead.customer.display_name if lead.customer else None)


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> LeadListResponse:
    filters = [Lead.tenant_id == settings.DEFAULT_TENANT_ID]
    if status_filter:
        filters.append(Lead.status == status_filter)
    if search:
        like = f"%{search.strip()}%"
        filters.append(
            sa.or_(  # type: ignore[attr-defined]
                Lead.company_name.ilike(like),
                Lead.contact_person.ilike(like),
                Lead.email.ilike(like),
            )
        )

    total_stmt = select(func.count()).select_from(Lead).where(*filters)
    total = await session.scalar(total_stmt)

    stmt = (
        select(Lead)
        .options(selectinload(Lead.customer))
        .where(*filters)
        .offset(skip)
        .limit(limit)
        .order_by(Lead.created_at.desc())
    )
    result = await session.execute(stmt)
    leads = result.scalars().all()
    _with_customer_name(leads)
    items = [LeadRead.model_validate(row) for row in leads]
    return LeadListResponse(items=items, total=total or 0)


@router.post("/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreate, session: AsyncSession = Depends(get_session)) -> LeadRead:
    customer = None
    if payload.customer_id:
        customer = await session.get(Customer, payload.customer_id)
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")

    lead = Lead(
        tenant_id=settings.DEFAULT_TENANT_ID,
        company_name=payload.company_name,
        contact_person=payload.contact_person,
        email=payload.email,
        phone=payload.phone,
        status=payload.status,
        priority=payload.priority,
        source=payload.source,
        estimated_value=payload.estimated_value,
        assigned_to=payload.assigned_to,
        notes=payload.notes,
        customer_id=payload.customer_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead, attribute_names=["customer"])
    setattr(lead, "customer_name", lead.customer.display_name if lead.customer else None)
    return LeadRead.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(lead_id: UUID, session: AsyncSession = Depends(get_session)) -> LeadRead:
    lead = await session.get(Lead, lead_id, options=[selectinload(Lead.customer)])
    if not lead or lead.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Lead not found")
    setattr(lead, "customer_name", lead.customer.display_name if lead.customer else None)
    return LeadRead.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadRead)
async def update_lead(lead_id: UUID, payload: LeadUpdate, session: AsyncSession = Depends(get_session)) -> LeadRead:
    lead = await session.get(Lead, lead_id, options=[selectinload(Lead.customer)])
    if not lead or lead.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Lead not found")

    updates = payload.model_dump(exclude_unset=True)
    if "customer_id" in updates and updates["customer_id"] is not None:
        customer = await session.get(Customer, updates["customer_id"])
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in updates.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(lead, attribute_names=["customer"])
    setattr(lead, "customer_name", lead.customer.display_name if lead.customer else None)
    return LeadRead.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    lead = await session.get(Lead, lead_id)
    if not lead or lead.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Lead not found")
    await session.delete(lead)
    await session.commit()
