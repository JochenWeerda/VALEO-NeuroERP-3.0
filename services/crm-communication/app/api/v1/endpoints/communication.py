"""CRM Communication API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.communication import (
    Email, EmailCreate, EmailSend, Template, TemplateCreate, TemplateUpdate,
    Campaign, CampaignCreate, CampaignUpdate, CommunicationAnalytics
)
from ....schemas.base import PaginatedResponse
from ....db.models import Email as EmailModel, Template as TemplateModel, Campaign as CampaignModel

router = APIRouter()


@router.post("/emails/send", response_model=Email, status_code=status.HTTP_201_CREATED)
async def send_email(
    email_data: EmailSend,
    db: AsyncSession = get_db
):
    """Send an email with optional template and attachments."""
    # For now, create the email record - actual sending would be handled by background task
    email = EmailModel(**email_data.model_dump())
    db.add(email)
    await db.commit()
    await db.refresh(email)

    # TODO: Queue email for sending via SMTP
    # TODO: Process attachments
    # TODO: Apply template if specified

    return Email.model_validate(email)


@router.get("/emails", response_model=PaginatedResponse[Email])
async def list_emails(
    tenant_id: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    lead_id: Optional[UUID] = Query(None),
    case_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = get_db
):
    """List emails with filtering and pagination."""
    query = db.query(EmailModel)

    if tenant_id:
        query = query.filter(EmailModel.tenant_id == tenant_id)
    if customer_id:
        query = query.filter(EmailModel.customer_id == customer_id)
    if lead_id:
        query = query.filter(EmailModel.lead_id == lead_id)
    if case_id:
        query = query.filter(EmailModel.case_id == case_id)
    if status:
        query = query.filter(EmailModel.status == status)
    if direction:
        query = query.filter(EmailModel.direction == direction)

    total = await query.count()
    emails = await query.offset(skip).limit(limit).all()

    return PaginatedResponse[Email](
        items=[Email.model_validate(email) for email in emails],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/emails/{email_id}", response_model=Email)
async def get_email(
    email_id: UUID,
    db: AsyncSession = get_db
):
    """Get a specific email by ID."""
    email = await db.get(EmailModel, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return Email.model_validate(email)


@router.get("/templates", response_model=PaginatedResponse[Template])
async def list_templates(
    tenant_id: Optional[str] = Query(None),
    type_filter: Optional[str] = Query(None, alias="type"),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = get_db
):
    """List email templates with filtering."""
    query = db.query(TemplateModel)

    if tenant_id:
        query = query.filter(TemplateModel.tenant_id == tenant_id)
    if type_filter:
        query = query.filter(TemplateModel.type == type_filter)
    if category:
        query = query.filter(TemplateModel.category == category)
    if is_active is not None:
        query = query.filter(TemplateModel.is_active == is_active)

    total = await query.count()
    templates = await query.offset(skip).limit(limit).all()

    return PaginatedResponse[Template](
        items=[Template.model_validate(template) for template in templates],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.post("/templates", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = get_db
):
    """Create a new email template."""
    template = TemplateModel(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return Template.model_validate(template)


@router.put("/templates/{template_id}", response_model=Template)
async def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    db: AsyncSession = get_db
):
    """Update an email template."""
    template = await db.get(TemplateModel, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return Template.model_validate(template)


@router.post("/campaigns", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = get_db
):
    """Create a new email campaign."""
    campaign = CampaignModel(**campaign_data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return Campaign.model_validate(campaign)


@router.get("/campaigns", response_model=PaginatedResponse[Campaign])
async def list_campaigns(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = get_db
):
    """List email campaigns."""
    query = db.query(CampaignModel)

    if tenant_id:
        query = query.filter(CampaignModel.tenant_id == tenant_id)
    if status:
        query = query.filter(CampaignModel.status == status)

    total = await query.count()
    campaigns = await query.offset(skip).limit(limit).all()

    return PaginatedResponse[Campaign](
        items=[Campaign.model_validate(campaign) for campaign in campaigns],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: UUID,
    db: AsyncSession = get_db
):
    """Send an email campaign."""
    campaign = await db.get(CampaignModel, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "scheduled":
        raise HTTPException(status_code=400, detail="Campaign must be scheduled to send")

    # TODO: Queue campaign for sending
    campaign.status = "running"
    await db.commit()

    return {"message": "Campaign queued for sending", "campaign_id": str(campaign_id)}


@router.get("/analytics", response_model=CommunicationAnalytics)
async def get_communication_analytics(
    tenant_id: Optional[str] = Query(None),
    period: str = Query("last_30_days", description="Time period for analytics")
):
    """Get communication analytics and metrics."""
    # Mock analytics data - in production this would aggregate from the database
    analytics = {
        "total_emails": 1250,
        "sent_emails": 1200,
        "delivered_emails": 1180,
        "opened_emails": 340,
        "clicked_emails": 85,
        "bounced_emails": 20,
        "delivery_rate": 0.983,
        "open_rate": 0.288,
        "click_rate": 0.071,
        "bounce_rate": 0.017,
        "response_time_avg": 2.5,
        "customer_satisfaction": 4.2,
        "period": period
    }

    return CommunicationAnalytics(**analytics)


@router.post("/webhooks/email")
async def email_webhook(
    webhook_data: dict
):
    """Webhook endpoint for receiving inbound emails."""
    # TODO: Process inbound email webhooks from email service provider
    # This would handle bounces, opens, clicks, and new inbound emails
    return {"status": "received", "processed": True}