from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db.models import Customer, FarmProfile
from app.db.session import get_session
from app.schemas import (
    FarmProfileCreate,
    FarmProfileListResponse,
    FarmProfileRead,
    FarmProfileUpdate,
)

router = APIRouter()


def _attach_customer(records: list[FarmProfile]) -> None:
    for profile in records:
        setattr(profile, "customer_name", profile.customer.display_name if profile.customer else None)


@router.get("/", response_model=FarmProfileListResponse)
async def list_farm_profiles(
    search: Optional[str] = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> FarmProfileListResponse:
    filters = [FarmProfile.tenant_id == settings.DEFAULT_TENANT_ID]
    stmt = select(FarmProfile).options(selectinload(FarmProfile.customer)).where(*filters)
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(FarmProfile.farm_name.ilike(like))

    total = await session.scalar(
        select(func.count()).select_from(FarmProfile).where(*filters)
    )

    stmt = stmt.offset(skip).limit(limit).order_by(FarmProfile.created_at.desc())
    result = await session.execute(stmt)
    profiles = result.scalars().all()
    _attach_customer(profiles)
    items = [FarmProfileRead.model_validate(row) for row in profiles]
    return FarmProfileListResponse(items=items, total=total or 0)


@router.post("/", response_model=FarmProfileRead, status_code=status.HTTP_201_CREATED)
async def create_farm_profile(payload: FarmProfileCreate, session: AsyncSession = Depends(get_session)) -> FarmProfileRead:
    if payload.customer_id:
        customer = await session.get(Customer, payload.customer_id)
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")

    profile = FarmProfile(
        tenant_id=settings.DEFAULT_TENANT_ID,
        farm_name=payload.farm_name,
        owner=payload.owner,
        total_area=payload.total_area,
        crops=[entry.model_dump() for entry in payload.crops] if payload.crops else None,
        livestock=[entry.model_dump() for entry in payload.livestock] if payload.livestock else None,
        location=payload.location.model_dump() if payload.location else None,
        certifications=payload.certifications,
        notes=payload.notes,
        customer_id=payload.customer_id,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile, attribute_names=["customer"])
    setattr(profile, "customer_name", profile.customer.display_name if profile.customer else None)
    return FarmProfileRead.model_validate(profile)


@router.get("/{profile_id}", response_model=FarmProfileRead)
async def get_farm_profile(profile_id: UUID, session: AsyncSession = Depends(get_session)) -> FarmProfileRead:
    profile = await session.get(FarmProfile, profile_id, options=[selectinload(FarmProfile.customer)])
    if not profile or profile.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    setattr(profile, "customer_name", profile.customer.display_name if profile.customer else None)
    return FarmProfileRead.model_validate(profile)


@router.patch("/{profile_id}", response_model=FarmProfileRead)
async def update_farm_profile(profile_id: UUID, payload: FarmProfileUpdate, session: AsyncSession = Depends(get_session)) -> FarmProfileRead:
    profile = await session.get(FarmProfile, profile_id, options=[selectinload(FarmProfile.customer)])
    if not profile or profile.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Farm profile not found")

    updates = payload.model_dump(exclude_unset=True)
    if "customer_id" in updates and updates["customer_id"] is not None:
        customer = await session.get(Customer, updates["customer_id"])
        if not customer or customer.tenant_id != settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=404, detail="Customer not found")

    if "crops" in updates and updates["crops"] is not None:
        updates["crops"] = [entry.model_dump() for entry in updates["crops"]]
    if "livestock" in updates and updates["livestock"] is not None:
        updates["livestock"] = [entry.model_dump() for entry in updates["livestock"]]
    if "location" in updates and updates["location"] is not None:
        updates["location"] = updates["location"].model_dump()

    for field, value in updates.items():
        setattr(profile, field, value)

    await session.commit()
    await session.refresh(profile, attribute_names=["customer"])
    setattr(profile, "customer_name", profile.customer.display_name if profile.customer else None)
    return FarmProfileRead.model_validate(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm_profile(profile_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    profile = await session.get(FarmProfile, profile_id)
    if not profile or profile.tenant_id != settings.DEFAULT_TENANT_ID:
        raise HTTPException(status_code=404, detail="Farm profile not found")
    await session.delete(profile)
    await session.commit()
