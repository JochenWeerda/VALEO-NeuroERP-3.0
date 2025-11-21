"""CRM Sales Opportunities API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.opportunity import Opportunity, OpportunityCreate, OpportunityUpdate
from ....schemas.base import PaginatedResponse
from ....db.models import Opportunity as OpportunityModel

router = APIRouter()


@router.post("/", response_model=Opportunity, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new sales opportunity."""
    opportunity = OpportunityModel(**opportunity_data.model_dump())
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return Opportunity.model_validate(opportunity)


@router.get("/", response_model=PaginatedResponse[Opportunity])
async def list_opportunities(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List sales opportunities with pagination and filtering."""
    filters = []
    if tenant_id:
        filters.append(OpportunityModel.tenant_id == tenant_id)
    if status:
        filters.append(OpportunityModel.status == status)
    if assigned_to:
        filters.append(OpportunityModel.assigned_to == assigned_to)

    count_stmt = select(func.count()).select_from(OpportunityModel)
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(OpportunityModel)
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    opportunities = result.scalars().all()

    current_page = (skip // limit) + 1
    total_pages = max(1, (total + limit - 1) // limit) if total else 1

    return PaginatedResponse[Opportunity](
        items=[Opportunity.model_validate(opportunity) for opportunity in opportunities],
        total=total,
        page=current_page,
        size=limit,
        pages=total_pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{opportunity_id}", response_model=Opportunity)
async def get_opportunity(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific sales opportunity by ID."""
    opportunity = await db.get(OpportunityModel, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return Opportunity.model_validate(opportunity)


@router.put("/{opportunity_id}", response_model=Opportunity)
async def update_opportunity(
    opportunity_id: UUID,
    opportunity_data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a sales opportunity."""
    opportunity = await db.get(OpportunityModel, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    update_data = opportunity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)

    await db.commit()
    await db.refresh(opportunity)
    return Opportunity.model_validate(opportunity)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a sales opportunity."""
    opportunity = await db.get(OpportunityModel, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    await db.delete(opportunity)
    await db.commit()
