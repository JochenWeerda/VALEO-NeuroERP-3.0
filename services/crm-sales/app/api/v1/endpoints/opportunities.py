"""CRM Sales Opportunities API endpoints."""

import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityStage,
    OpportunityStageCreate,
    OpportunityStageUpdate,
    OpportunityHistory,
    OpportunityHistoryCreate,
    PipelineAggregation,
    ForecastData,
)
from ....schemas.base import PaginatedResponse
from ....db.models import (
    Opportunity as OpportunityModel,
    OpportunityStage as OpportunityStageModel,
    OpportunityHistory as OpportunityHistoryModel,
)
from ....services.events import get_event_publisher

router = APIRouter()


@router.post("/", response_model=Opportunity, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new sales opportunity."""
    data = opportunity_data.model_dump()
    
    # Generate number if not provided
    if not data.get("number"):
        # Get next number from sequence or count
        count_stmt = select(func.count()).select_from(OpportunityModel).where(
            OpportunityModel.tenant_id == data["tenant_id"]
        )
        count = (await db.execute(count_stmt)).scalar_one()
        data["number"] = f"OPP-{str(count + 1).zfill(6)}"
    
    # Calculate expected_revenue if amount and probability are provided
    if data.get("amount") and data.get("probability"):
        data["expected_revenue"] = data["amount"] * (data["probability"] / 100)
    
    # Set owner_id from assigned_to if not provided
    if not data.get("owner_id") and data.get("assigned_to"):
        data["owner_id"] = data["assigned_to"]
    
    opportunity = OpportunityModel(**data)
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_opportunity_created(
        opportunity.id,
        opportunity.tenant_id,
        data,
    )
    
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
    changed_by: Optional[str] = Query(None, description="User ID making the change"),
):
    """Update a sales opportunity."""
    opportunity = await db.get(OpportunityModel, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    update_data = opportunity_data.model_dump(exclude_unset=True)
    
    # Track old values for history
    old_stage = opportunity.stage.value if opportunity.stage else None
    old_status = opportunity.status.value if opportunity.status else None
    
    # Calculate expected_revenue if amount or probability changed
    if "amount" in update_data or "probability" in update_data:
        amount = update_data.get("amount", opportunity.amount)
        probability = update_data.get("probability", opportunity.probability)
        if amount and probability:
            update_data["expected_revenue"] = amount * (probability / 100)
    
    # Set owner_id from assigned_to if not provided
    if "assigned_to" in update_data and not update_data.get("owner_id"):
        update_data["owner_id"] = update_data["assigned_to"]
    
    # Create history entries for changed fields
    if changed_by:
        history_entries = []
        for field, new_value in update_data.items():
            if field in ["updated_at", "updated_by"]:
                continue
            old_value = getattr(opportunity, field, None)
            if old_value != new_value:
                # Convert enum to string for history
                if hasattr(old_value, "value"):
                    old_value = old_value.value
                if hasattr(new_value, "value"):
                    new_value = new_value.value
                if isinstance(old_value, UUID):
                    old_value = str(old_value)
                if isinstance(new_value, UUID):
                    new_value = str(new_value)
                history_entries.append(
                    OpportunityHistoryModel(
                        opportunity_id=opportunity_id,
                        field_name=field,
                        old_value=str(old_value) if old_value is not None else None,
                        new_value=str(new_value) if new_value is not None else None,
                        changed_by=changed_by,
                    )
                )
        if history_entries:
            db.add_all(history_entries)
    
    # Update fields
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    if changed_by:
        opportunity.updated_by = changed_by

    await db.commit()
    await db.refresh(opportunity)
    
    # Publish events for stage/status changes
    event_publisher = get_event_publisher()
    
    if old_stage and opportunity.stage.value != old_stage:
        await event_publisher.publish_opportunity_stage_changed(
            opportunity_id=opportunity.id,
            tenant_id=opportunity.tenant_id,
            old_stage=old_stage,
            new_stage=opportunity.stage.value,
            changed_by=changed_by,
        )
    
    if old_status and opportunity.status.value != old_status:
        if opportunity.status.value == "closed_won":
            await event_publisher.publish_opportunity_won(
                opportunity_id=opportunity.id,
                tenant_id=opportunity.tenant_id,
                amount=opportunity.amount,
                actual_close_date=opportunity.actual_close_date,
                won_by=changed_by,
            )
        elif opportunity.status.value == "closed_lost":
            await event_publisher.publish_opportunity_lost(
                opportunity_id=opportunity.id,
                tenant_id=opportunity.tenant_id,
                amount=opportunity.amount,
                lost_reason=update_data.get("notes"),  # Use notes as reason if available
                lost_by=changed_by,
            )
    
    # Publish general update event
    await event_publisher.publish_opportunity_updated(
        opportunity_id=opportunity.id,
        tenant_id=opportunity.tenant_id,
        changes=update_data,
        changed_by=changed_by,
    )
    
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

    tenant_id = opportunity.tenant_id
    opportunity_id_value = opportunity.id
    deleted_by = getattr(opportunity, "updated_by", None)
    
    await db.delete(opportunity)
    await db.commit()
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_opportunity_deleted(
        opportunity_id=opportunity_id_value,
        tenant_id=tenant_id,
        deleted_by=deleted_by,
    )


# Stages endpoints
@router.get("/stages", response_model=list[OpportunityStage])
async def list_stages(
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all opportunity stages."""
    filters = []
    if tenant_id:
        filters.append(OpportunityStageModel.tenant_id == tenant_id)
    
    stmt = select(OpportunityStageModel)
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.order_by(OpportunityStageModel.order)
    
    result = await db.execute(stmt)
    stages = result.scalars().all()
    return [OpportunityStage.model_validate(stage) for stage in stages]


@router.post("/stages", response_model=OpportunityStage, status_code=status.HTTP_201_CREATED)
async def create_stage(
    stage_data: OpportunityStageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new opportunity stage."""
    stage = OpportunityStageModel(**stage_data.model_dump())
    db.add(stage)
    await db.commit()
    await db.refresh(stage)
    return OpportunityStage.model_validate(stage)


@router.get("/stages/{stage_id}", response_model=OpportunityStage)
async def get_stage(
    stage_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific opportunity stage by ID."""
    stage = await db.get(OpportunityStageModel, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return OpportunityStage.model_validate(stage)


@router.put("/stages/{stage_id}", response_model=OpportunityStage)
async def update_stage(
    stage_id: UUID,
    stage_data: OpportunityStageUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an opportunity stage."""
    stage = await db.get(OpportunityStageModel, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)
    
    await db.commit()
    await db.refresh(stage)
    return OpportunityStage.model_validate(stage)


# History endpoints
@router.get("/{opportunity_id}/history", response_model=list[OpportunityHistory])
async def get_opportunity_history(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get history for a specific opportunity."""
    opportunity = await db.get(OpportunityModel, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    stmt = select(OpportunityHistoryModel).where(
        OpportunityHistoryModel.opportunity_id == opportunity_id
    ).order_by(OpportunityHistoryModel.changed_at.desc())
    
    result = await db.execute(stmt)
    history = result.scalars().all()
    return [OpportunityHistory.model_validate(h) for h in history]


# Pipeline aggregation endpoint
@router.get("/pipeline/aggregation", response_model=list[PipelineAggregation])
async def get_pipeline_aggregation(
    tenant_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get pipeline aggregation by stage."""
    filters = []
    if tenant_id:
        filters.append(OpportunityModel.tenant_id == tenant_id)
    filters.append(OpportunityModel.status != "closed_won")
    filters.append(OpportunityModel.status != "closed_lost")
    
    stmt = select(
        OpportunityModel.stage,
        func.count(OpportunityModel.id).label("count"),
        func.coalesce(func.sum(OpportunityModel.amount), 0).label("total_amount"),
        func.coalesce(func.sum(OpportunityModel.expected_revenue), 0).label("total_expected_revenue"),
        func.coalesce(func.avg(OpportunityModel.probability), 0).label("avg_probability"),
    ).group_by(OpportunityModel.stage)
    
    if filters:
        stmt = stmt.where(*filters)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        PipelineAggregation(
            stage=row.stage.value if hasattr(row.stage, "value") else str(row.stage),
            count=row.count,
            total_amount=float(row.total_amount or 0),
            total_expected_revenue=float(row.total_expected_revenue or 0),
            avg_probability=float(row.avg_probability or 0),
        )
        for row in rows
    ]


# Forecast endpoint
@router.get("/forecast", response_model=list[ForecastData])
async def get_forecast(
    tenant_id: Optional[str] = Query(None),
    period: Optional[str] = Query(None, description="Period in format YYYY-MM"),
    owner_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get forecast data."""
    filters = []
    if tenant_id:
        filters.append(OpportunityModel.tenant_id == tenant_id)
    if owner_id:
        filters.append(OpportunityModel.owner_id == owner_id)
    if period:
        # Filter by expected_close_date in period
        year, month = period.split("-")
        filters.append(
            func.extract("year", OpportunityModel.expected_close_date) == int(year)
        )
        filters.append(
            func.extract("month", OpportunityModel.expected_close_date) == int(month)
        )
    filters.append(OpportunityModel.status != "closed_lost")
    
    stmt = select(
        func.to_char(OpportunityModel.expected_close_date, "YYYY-MM").label("period"),
        OpportunityModel.stage,
        OpportunityModel.owner_id,
        func.count(OpportunityModel.id).label("count"),
        func.coalesce(func.sum(OpportunityModel.amount), 0).label("total_amount"),
        func.coalesce(func.sum(OpportunityModel.expected_revenue), 0).label("total_expected_revenue"),
    ).group_by(
        func.to_char(OpportunityModel.expected_close_date, "YYYY-MM"),
        OpportunityModel.stage,
        OpportunityModel.owner_id,
    )
    
    if filters:
        stmt = stmt.where(*filters)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        ForecastData(
            period=row.period or period or "unknown",
            stage=row.stage.value if hasattr(row.stage, "value") else (str(row.stage) if row.stage else None),
            owner_id=row.owner_id,
            count=row.count,
            total_amount=float(row.total_amount or 0),
            total_expected_revenue=float(row.total_expected_revenue or 0),
        )
        for row in rows
    ]
