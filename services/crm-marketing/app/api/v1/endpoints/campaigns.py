"""Campaign management endpoints."""

from datetime import datetime
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Campaign,
    CampaignTemplate,
    CampaignRecipient,
    CampaignEvent,
    CampaignPerformance,
    CampaignType,
    CampaignStatus,
    RecipientStatus,
    CampaignEventType,
)
from app.db.session import get_db
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    Campaign as CampaignSchema,
    CampaignTemplateCreate,
    CampaignTemplateUpdate,
    CampaignTemplate as CampaignTemplateSchema,
    CampaignRecipient as CampaignRecipientSchema,
    CampaignEventCreate,
    CampaignEvent as CampaignEventSchema,
    CampaignPerformance as CampaignPerformanceSchema,
    CampaignScheduleRequest,
    CampaignTestRequest,
)
from app.services.events import get_event_publisher

router = APIRouter()


# Campaign CRUD
@router.post("", response_model=CampaignSchema, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    campaign = Campaign(
        tenant_id=campaign_data.tenant_id,
        name=campaign_data.name,
        description=campaign_data.description,
        type=CampaignType(campaign_data.type),
        status=CampaignStatus(campaign_data.status),
        segment_id=campaign_data.segment_id,
        template_id=campaign_data.template_id,
        scheduled_at=campaign_data.scheduled_at,
        sender_name=campaign_data.sender_name,
        sender_email=campaign_data.sender_email,
        subject=campaign_data.subject,
        budget=campaign_data.budget,
        settings=campaign_data.settings,
        created_by="system",  # TODO: Get from auth context
    )
    
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_campaign_created(
        campaign_id=campaign.id,
        tenant_id=campaign.tenant_id,
        campaign_name=campaign.name,
    )
    
    return campaign


@router.get("", response_model=List[CampaignSchema])
async def list_campaigns(
    tenant_id: str = Query(..., description="Tenant ID"),
    type: str | None = Query(None, description="Filter by type"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """List campaigns with optional filters."""
    filters = [Campaign.tenant_id == tenant_id]
    
    if type:
        filters.append(Campaign.type == CampaignType(type))
    if status:
        filters.append(Campaign.status == CampaignStatus(status))
    
    stmt = select(Campaign).where(and_(*filters)).order_by(Campaign.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignSchema)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get campaign details."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    if campaign_data.name:
        campaign.name = campaign_data.name
    if campaign_data.description is not None:
        campaign.description = campaign_data.description
    if campaign_data.status:
        campaign.status = CampaignStatus(campaign_data.status)
    if campaign_data.segment_id is not None:
        campaign.segment_id = campaign_data.segment_id
    if campaign_data.template_id is not None:
        campaign.template_id = campaign_data.template_id
    if campaign_data.scheduled_at is not None:
        campaign.scheduled_at = campaign_data.scheduled_at
    if campaign_data.sender_name is not None:
        campaign.sender_name = campaign_data.sender_name
    if campaign_data.sender_email is not None:
        campaign.sender_email = campaign_data.sender_email
    if campaign_data.subject is not None:
        campaign.subject = campaign_data.subject
    if campaign_data.budget is not None:
        campaign.budget = campaign_data.budget
    if campaign_data.settings is not None:
        campaign.settings = campaign_data.settings
    
    campaign.updated_by = "system"  # TODO: Get from auth context
    campaign.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(campaign)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_campaign_updated(
        campaign_id=campaign.id,
        tenant_id=campaign.tenant_id,
    )
    
    return campaign


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    await db.delete(campaign)
    await db.commit()
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_campaign_deleted(
        campaign_id=campaign_id,
        tenant_id=campaign.tenant_id,
    )
    
    return None


# Campaign Actions
@router.post("/{campaign_id}/schedule", response_model=CampaignSchema)
async def schedule_campaign(
    campaign_id: UUID,
    request: CampaignScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Schedule a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.scheduled_at = request.scheduled_at
    campaign.status = CampaignStatus.SCHEDULED
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.post("/{campaign_id}/start", response_model=CampaignSchema)
async def start_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Start a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED, CampaignStatus.PAUSED]:
        raise HTTPException(status_code=400, detail="Campaign cannot be started in current status")
    
    campaign.status = CampaignStatus.RUNNING
    campaign.started_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(campaign)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_campaign_started(
        campaign_id=campaign.id,
        tenant_id=campaign.tenant_id,
    )
    
    return campaign


@router.post("/{campaign_id}/pause", response_model=CampaignSchema)
async def pause_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Pause a running campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Only running campaigns can be paused")
    
    campaign.status = CampaignStatus.PAUSED
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.post("/{campaign_id}/cancel", response_model=CampaignSchema)
async def cancel_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Campaign is already completed or cancelled")
    
    campaign.status = CampaignStatus.CANCELLED
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.get("/{campaign_id}/recipients", response_model=List[CampaignRecipientSchema])
async def list_campaign_recipients(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List recipients of a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    stmt = (
        select(CampaignRecipient)
        .where(CampaignRecipient.campaign_id == campaign_id)
        .offset(skip)
        .limit(limit)
        .order_by(CampaignRecipient.sent_at.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{campaign_id}/performance", response_model=List[CampaignPerformanceSchema])
async def get_campaign_performance(
    campaign_id: UUID,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get performance metrics for a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    filters = [CampaignPerformance.campaign_id == campaign_id]
    
    if start_date:
        filters.append(CampaignPerformance.date >= start_date)
    if end_date:
        filters.append(CampaignPerformance.date <= end_date)
    
    stmt = (
        select(CampaignPerformance)
        .where(and_(*filters))
        .order_by(CampaignPerformance.date.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{campaign_id}/events", response_model=List[CampaignEventSchema])
async def get_campaign_events(
    campaign_id: UUID,
    event_type: str | None = Query(None, description="Filter by event type"),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get events for a campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    filters = [CampaignEvent.campaign_id == campaign_id]
    
    if event_type:
        filters.append(CampaignEvent.event_type == CampaignEventType(event_type))
    
    stmt = (
        select(CampaignEvent)
        .where(and_(*filters))
        .offset(skip)
        .limit(limit)
        .order_by(CampaignEvent.timestamp.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{campaign_id}/test", status_code=200)
async def test_campaign(
    campaign_id: UUID,
    request: CampaignTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a test campaign."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # TODO: Implement test send logic
    # This would send a test email to the specified recipient_email
    
    return {"message": "Test campaign sent", "recipient_email": request.recipient_email}


# Campaign Templates
@router.post("/templates", response_model=CampaignTemplateSchema, status_code=201)
async def create_campaign_template(
    template_data: CampaignTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign template."""
    template = CampaignTemplate(
        tenant_id=template_data.tenant_id,
        name=template_data.name,
        description=template_data.description,
        type=CampaignType(template_data.type),
        subject=template_data.subject,
        body_html=template_data.body_html,
        body_text=template_data.body_text,
        variables=template_data.variables,
        is_active=template_data.is_active,
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.get("/templates", response_model=List[CampaignTemplateSchema])
async def list_campaign_templates(
    tenant_id: str = Query(..., description="Tenant ID"),
    type: str | None = Query(None, description="Filter by type"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """List campaign templates with optional filters."""
    filters = [CampaignTemplate.tenant_id == tenant_id]
    
    if type:
        filters.append(CampaignTemplate.type == CampaignType(type))
    if is_active is not None:
        filters.append(CampaignTemplate.is_active == is_active)
    
    stmt = select(CampaignTemplate).where(and_(*filters)).order_by(CampaignTemplate.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/templates/{template_id}", response_model=CampaignTemplateSchema)
async def get_campaign_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get campaign template details."""
    template = await db.get(CampaignTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Campaign template not found")
    return template


@router.put("/templates/{template_id}", response_model=CampaignTemplateSchema)
async def update_campaign_template(
    template_id: UUID,
    template_data: CampaignTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign template."""
    template = await db.get(CampaignTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Campaign template not found")
    
    # Update fields
    if template_data.name:
        template.name = template_data.name
    if template_data.description is not None:
        template.description = template_data.description
    if template_data.subject is not None:
        template.subject = template_data.subject
    if template_data.body_html is not None:
        template.body_html = template_data.body_html
    if template_data.body_text is not None:
        template.body_text = template_data.body_text
    if template_data.variables is not None:
        template.variables = template_data.variables
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    
    template.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/templates/{template_id}", status_code=204)
async def delete_campaign_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a campaign template."""
    template = await db.get(CampaignTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Campaign template not found")
    
    await db.delete(template)
    await db.commit()
    
    return None


# Public Tracking Endpoints
@router.post("/tracking/open", status_code=200)
async def track_campaign_open(
    campaign_id: UUID = Query(..., description="Campaign ID"),
    recipient_id: UUID = Query(..., description="Recipient ID"),
    db: AsyncSession = Depends(get_db),
):
    """Track campaign email open (public endpoint for tracking pixel)."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    recipient = await db.get(CampaignRecipient, recipient_id)
    if not recipient or recipient.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create event
    event = CampaignEvent(
        campaign_id=campaign_id,
        recipient_id=recipient_id,
        event_type=CampaignEventType.OPENED,
    )
    db.add(event)
    
    # Update recipient
    if not recipient.opened_at:
        recipient.opened_at = datetime.utcnow()
    recipient.open_count += 1
    recipient.status = RecipientStatus.DELIVERED
    
    # Update campaign metrics
    campaign.open_count += 1
    
    await db.commit()
    
    # Return 1x1 transparent pixel
    from fastapi.responses import Response
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3B'
    return Response(content=pixel, media_type="image/gif")


@router.post("/tracking/click", status_code=307)
async def track_campaign_click(
    campaign_id: UUID = Query(..., description="Campaign ID"),
    recipient_id: UUID = Query(..., description="Recipient ID"),
    url: str = Query(..., description="Target URL"),
    db: AsyncSession = Depends(get_db),
):
    """Track campaign link click (public endpoint for link redirect)."""
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    recipient = await db.get(CampaignRecipient, recipient_id)
    if not recipient or recipient.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create event
    event = CampaignEvent(
        campaign_id=campaign_id,
        recipient_id=recipient_id,
        event_type=CampaignEventType.CLICKED,
        details={"url": url},
    )
    db.add(event)
    
    # Update recipient
    if not recipient.clicked_at:
        recipient.clicked_at = datetime.utcnow()
    recipient.click_count += 1
    
    # Update campaign metrics
    campaign.click_count += 1
    
    await db.commit()
    
    # Redirect to target URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url, status_code=307)
