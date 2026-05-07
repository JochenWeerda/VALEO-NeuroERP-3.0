from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db.models import Contact, Customer
from app.db.session import get_session
from app.schemas import ContactCreate, ContactListResponse, ContactRead, ContactUpdate

router = APIRouter()


def _effective_tenant(tenant_id: str | None) -> str:
    t = (tenant_id or "").strip()
    return t or settings.DEFAULT_TENANT_ID


def _ensure_contact_customer_name(records: List[Contact]) -> None:
    for contact in records:
        customer_name = contact.customer.display_name if contact.customer else None
        setattr(contact, "customer_name", customer_name)


@router.get("/", response_model=ContactListResponse)
async def list_contacts(
    customer_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None, description="Tenant-ID; Default aus Service-Config"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> ContactListResponse:
    tid = _effective_tenant(tenant_id)
    filters = [Customer.tenant_id == tid]
    if customer_id:
        filters.append(Contact.customer_id == customer_id)
    if search:
        like_pattern = f"%{search.strip()}%"
        filters.append(
            sa.or_(  # type: ignore[attr-defined]
                Contact.first_name.ilike(like_pattern),
                Contact.last_name.ilike(like_pattern),
                Contact.email.ilike(like_pattern),
            )
        )

    total_stmt = select(func.count()).select_from(Contact).join(Customer).where(*filters)
    total = await session.scalar(total_stmt)

    stmt = (
        select(Contact)
        .options(selectinload(Contact.customer))
        .join(Customer)
        .where(*filters)
        .offset(skip)
        .limit(limit)
        .order_by(Contact.created_at.desc())
    )
    result = await session.execute(stmt)
    contacts = result.scalars().all()
    _ensure_contact_customer_name(contacts)
    return ContactListResponse(items=[ContactRead.model_validate(row) for row in contacts], total=total or 0)


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    tenant_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ContactRead:
    tid = _effective_tenant(tenant_id)
    customer = await session.get(Customer, payload.customer_id)
    if not customer or customer.tenant_id != tid:
        raise HTTPException(status_code=404, detail="Customer not found")

    contact = Contact(**payload.model_dump())
    session.add(contact)
    await session.commit()
    await session.refresh(contact, attribute_names=["customer"])
    setattr(contact, "customer_name", customer.display_name)
    return ContactRead.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    tenant_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ContactRead:
    tid = _effective_tenant(tenant_id)
    contact = await session.get(Contact, contact_id, options=[selectinload(Contact.customer)])
    if not contact or (contact.customer and contact.customer.tenant_id != tid):
        raise HTTPException(status_code=404, detail="Contact not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    await session.commit()
    await session.refresh(contact, attribute_names=["customer"])
    setattr(contact, "customer_name", contact.customer.display_name if contact.customer else None)
    return ContactRead.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    tenant_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> None:
    tid = _effective_tenant(tenant_id)
    contact = await session.get(Contact, contact_id, options=[selectinload(Contact.customer)])
    if not contact or (contact.customer and contact.customer.tenant_id != tid):
        raise HTTPException(status_code=404, detail="Contact not found")

    await session.delete(contact)
    await session.commit()


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: UUID,
    tenant_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ContactRead:
    tid = _effective_tenant(tenant_id)
    contact = await session.get(Contact, contact_id, options=[selectinload(Contact.customer)])
    if not contact or (contact.customer and contact.customer.tenant_id != tid):
        raise HTTPException(status_code=404, detail="Contact not found")
    setattr(contact, "customer_name", contact.customer.display_name if contact.customer else None)
    return ContactRead.model_validate(contact)

