"""Segment management endpoints."""

from datetime import datetime
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Segment,
    SegmentRule,
    SegmentMember,
    SegmentPerformance,
    SegmentType,
    SegmentStatus,
    RuleOperator,
    LogicalOperator,
)
from app.db.session import get_db
from app.schemas.segment import (
    SegmentCreate,
    SegmentUpdate,
    Segment as SegmentSchema,
    SegmentRuleCreate,
    SegmentRuleUpdate,
    SegmentRule as SegmentRuleSchema,
    SegmentMemberCreate,
    SegmentMember as SegmentMemberSchema,
    SegmentPerformance as SegmentPerformanceSchema,
    SegmentCalculateRequest,
    SegmentExportRequest,
)
from app.services.events import get_event_publisher
from app.services.segment_calculator import SegmentCalculator

router = APIRouter()


@router.post("", response_model=SegmentSchema, status_code=201)
async def create_segment(
    segment_data: SegmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new segment."""
    segment = Segment(
        tenant_id=segment_data.tenant_id,
        name=segment_data.name,
        description=segment_data.description,
        type=SegmentType(segment_data.type),
        status=SegmentStatus(segment_data.status),
        rules=segment_data.rules,
        created_by="system",  # TODO: Get from auth context
    )
    
    db.add(segment)
    await db.commit()
    await db.refresh(segment)
    
    # If dynamic segment, calculate members
    if segment.type == SegmentType.DYNAMIC:
        calculator = SegmentCalculator(db)
        await calculator.calculate_segment(segment.id)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_created(
        segment_id=segment.id,
        tenant_id=segment.tenant_id,
        segment_name=segment.name,
    )
    
    return segment


@router.get("", response_model=List[SegmentSchema])
async def list_segments(
    tenant_id: str = Query(..., description="Tenant ID"),
    type: str | None = Query(None, description="Filter by type"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """List segments with optional filters."""
    filters = [Segment.tenant_id == tenant_id]
    
    if type:
        filters.append(Segment.type == SegmentType(type))
    if status:
        filters.append(Segment.status == SegmentStatus(status))
    
    stmt = select(Segment).where(and_(*filters)).order_by(Segment.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{segment_id}", response_model=SegmentSchema)
async def get_segment(
    segment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get segment details."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment


@router.put("/{segment_id}", response_model=SegmentSchema)
async def update_segment(
    segment_id: UUID,
    segment_data: SegmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a segment."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    # Update fields
    if segment_data.name:
        segment.name = segment_data.name
    if segment_data.description is not None:
        segment.description = segment_data.description
    if segment_data.status:
        segment.status = SegmentStatus(segment_data.status)
    if segment_data.rules is not None:
        segment.rules = segment_data.rules
    
    segment.updated_by = "system"  # TODO: Get from auth context
    segment.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(segment)
    
    # If dynamic segment and rules changed, recalculate
    if segment.type == SegmentType.DYNAMIC and segment_data.rules is not None:
        calculator = SegmentCalculator(db)
        await calculator.calculate_segment(segment.id)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_updated(
        segment_id=segment.id,
        tenant_id=segment.tenant_id,
    )
    
    return segment


@router.delete("/{segment_id}", status_code=204)
async def delete_segment(
    segment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a segment."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    await db.delete(segment)
    await db.commit()
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_deleted(
        segment_id=segment_id,
        tenant_id=segment.tenant_id,
    )
    
    return None


@router.post("/{segment_id}/calculate", response_model=SegmentSchema)
async def calculate_segment(
    segment_id: UUID,
    request: SegmentCalculateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Recalculate a dynamic segment."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    if segment.type != SegmentType.DYNAMIC:
        raise HTTPException(status_code=400, detail="Only dynamic segments can be calculated")
    
    calculator = SegmentCalculator(db)
    await calculator.calculate_segment(segment.id, force_full=request.force_full)
    
    await db.refresh(segment)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_calculated(
        segment_id=segment.id,
        tenant_id=segment.tenant_id,
        member_count=segment.member_count,
    )
    
    return segment


@router.get("/{segment_id}/members", response_model=List[SegmentMemberSchema])
async def list_segment_members(
    segment_id: UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List members of a segment."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    stmt = (
        select(SegmentMember)
        .where(
            and_(
                SegmentMember.segment_id == segment_id,
                SegmentMember.removed_at.is_(None)  # Only active members
            )
        )
        .offset(skip)
        .limit(limit)
        .order_by(SegmentMember.added_at.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{segment_id}/members", response_model=SegmentMemberSchema, status_code=201)
async def add_segment_member(
    segment_id: UUID,
    member_data: SegmentMemberCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a member to a segment (for static segments)."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    if segment.type == SegmentType.DYNAMIC:
        raise HTTPException(status_code=400, detail="Cannot manually add members to dynamic segments")
    
    # Check if member already exists
    existing = await db.execute(
        select(SegmentMember).where(
            and_(
                SegmentMember.segment_id == segment_id,
                SegmentMember.contact_id == member_data.contact_id,
                SegmentMember.removed_at.is_(None)
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Member already in segment")
    
    member = SegmentMember(
        segment_id=segment_id,
        contact_id=member_data.contact_id,
        added_by=member_data.added_by or "system",
    )
    
    db.add(member)
    
    # Update member count
    segment.member_count = await db.scalar(
        select(func.count(SegmentMember.id)).where(
            and_(
                SegmentMember.segment_id == segment_id,
                SegmentMember.removed_at.is_(None)
            )
        )
    )
    
    await db.commit()
    await db.refresh(member)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_member_added(
        segment_id=segment_id,
        contact_id=member_data.contact_id,
    )
    
    return member


@router.delete("/{segment_id}/members/{member_id}", status_code=204)
async def remove_segment_member(
    segment_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a segment."""
    member = await db.get(SegmentMember, member_id)
    if not member or member.segment_id != segment_id:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.removed_at:
        raise HTTPException(status_code=400, detail="Member already removed")
    
    member.removed_at = datetime.utcnow()
    member.removed_by = "system"  # TODO: Get from auth context
    
    # Update member count
    segment = await db.get(Segment, segment_id)
    if segment:
        segment.member_count = await db.scalar(
            select(func.count(SegmentMember.id)).where(
                and_(
                    SegmentMember.segment_id == segment_id,
                    SegmentMember.removed_at.is_(None)
                )
            )
        )
    
    await db.commit()
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_segment_member_removed(
        segment_id=segment_id,
        contact_id=member.contact_id,
    )
    
    return None


@router.get("/{segment_id}/performance", response_model=List[SegmentPerformanceSchema])
async def get_segment_performance(
    segment_id: UUID,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    period_type: str = Query("daily", description="daily, weekly, monthly"),
    db: AsyncSession = Depends(get_db),
):
    """Get performance metrics for a segment."""
    segment = await db.get(Segment, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    filters = [SegmentPerformance.segment_id == segment_id, SegmentPerformance.period_type == period_type]
    
    if start_date:
        filters.append(SegmentPerformance.date >= start_date)
    if end_date:
        filters.append(SegmentPerformance.date <= end_date)
    
    stmt = (
        select(SegmentPerformance)
        .where(and_(*filters))
        .order_by(SegmentPerformance.date.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()

