from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db.models import Activity, Contact, Customer
from app.db.session import get_session
from app.schemas import ActivityCreate, ActivityListResponse, ActivityRead, ActivityUpdate

router = APIRouter()


def _attach_names(records: list[Activity]) -> None:
    for activity in records:
        setattr(activity, "customer_name", activity.customer.display_name if activity.customer else None)


@router.get("/", response_model=ActivityListResponse)
async def list_activities(
    activity_type: Optional[str] = Query(default=None, alias="type"),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> ActivityListResponse:
    filters = [Activity.tenant_id == settings.DEFAULT_TENANT_ID]
    if activity_type:
        filters.append(Activity.type == activity_type)
    if status_filter:
        filters.append(Activity.status == status_filter)

    total_stmt = select(func.count()).select_from(Activity).where(*filters)
    total = await session.scalar(total_stmt)

    stmt = (
        select(Activity)
        .options(selectinload(Activity.customer))
        .where(*filters)
        .offset(skip)
        .limit(limit)
        .order_by(Activity.created_at.desc())
    )
    result = await session.execute(stmt)
    activities = result.scalars().all()
    _attach_names(activities)
    items = [ActivityRead.model_validate(row) for row in activities]
    return ActivityListResponse(items=items, total=total or 0)


@router.post("/", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_activity(payload: ActivityCreate, session: AsyncSession = Depends(get_session)) -> ActivityRead:
    customer = None
    if payload.customer_id:
        customer = await session.get(Customer, payload.customer_id)
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")
    if payload.contact_id:
        contact = await session.get(Contact, payload.contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

    activity = Activity(
        tenant_id=settings.DEFAULT_TENANT_ID,
        type=payload.type,
        title=payload.title,
        status=payload.status,
        scheduled_at=payload.scheduled_at,
        assigned_to=payload.assigned_to,
        description=payload.description,
        customer_id=payload.customer_id,
        contact_id=payload.contact_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(activity)
    await session.commit()
    await session.refresh(activity, attribute_names=["customer"])
    setattr(activity, "customer_name", customer.display_name if customer else None)
    return ActivityRead.model_validate(activity)


@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity(activity_id: UUID, session: AsyncSession = Depends(get_session)) -> ActivityRead:
    activity = await session.get(Activity, activity_id, options=[selectinload(Activity.customer)])
    if not activity or activity.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Activity not found")
    setattr(activity, "customer_name", activity.customer.display_name if activity.customer else None)
    return ActivityRead.model_validate(activity)


@router.patch("/{activity_id}", response_model=ActivityRead)
async def update_activity(activity_id: UUID, payload: ActivityUpdate, session: AsyncSession = Depends(get_session)) -> ActivityRead:
    activity = await session.get(Activity, activity_id, options=[selectinload(Activity.customer)])
    if not activity or activity.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Activity not found")

    updates = payload.model_dump(exclude_unset=True)
    if "customer_id" in updates and updates["customer_id"] is not None:
        customer = await session.get(Customer, updates["customer_id"])
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")
    if "contact_id" in updates and updates["contact_id"] is not None:
        contact = await session.get(Contact, updates["contact_id"])
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

    for field, value in updates.items():
        setattr(activity, field, value)
    activity.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(activity, attribute_names=["customer"])
    setattr(activity, "customer_name", activity.customer.display_name if activity.customer else None)
    return ActivityRead.model_validate(activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(activity_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    activity = await session.get(Activity, activity_id)
    if not activity or activity.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Activity not found")
    await session.delete(activity)
    await session.commit()
