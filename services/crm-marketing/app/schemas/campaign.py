"""Pydantic schemas for campaigns."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="email, sms, push, social")
    status: str = Field(default="draft", description="draft, scheduled, running, paused, completed, cancelled")
    segment_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    budget: Optional[float] = None
    settings: Optional[dict] = None


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    tenant_id: str


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    segment_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    budget: Optional[float] = None
    settings: Optional[dict] = None


class Campaign(CampaignBase):
    """Full campaign schema."""
    id: UUID
    tenant_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    spent: float = 0
    target_count: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    open_count: int = 0
    click_count: int = 0
    conversion_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignTemplateBase(BaseModel):
    """Base campaign template schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="email, sms, push")
    subject: Optional[str] = None  # For email
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    variables: Optional[dict] = None
    is_active: bool = True


class CampaignTemplateCreate(CampaignTemplateBase):
    """Schema for creating a campaign template."""
    tenant_id: str


class CampaignTemplateUpdate(BaseModel):
    """Schema for updating a campaign template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    variables: Optional[dict] = None
    is_active: Optional[bool] = None


class CampaignTemplate(CampaignTemplateBase):
    """Full campaign template schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignRecipientBase(BaseModel):
    """Base campaign recipient schema."""
    contact_id: UUID
    email: Optional[str] = None
    variant: Optional[str] = None


class CampaignRecipientCreate(CampaignRecipientBase):
    """Schema for creating a campaign recipient."""
    campaign_id: UUID


class CampaignRecipient(CampaignRecipientBase):
    """Full campaign recipient schema."""
    id: UUID
    campaign_id: UUID
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    open_count: int = 0
    click_count: int = 0
    bounce_reason: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignEventBase(BaseModel):
    """Base campaign event schema."""
    event_type: str = Field(..., description="sent, delivered, opened, clicked, bounced, converted")
    details: Optional[dict] = None
    ip_address: Optional[str] = None


class CampaignEventCreate(CampaignEventBase):
    """Schema for creating a campaign event."""
    campaign_id: UUID
    recipient_id: Optional[UUID] = None


class CampaignEvent(CampaignEventBase):
    """Full campaign event schema."""
    id: UUID
    campaign_id: UUID
    recipient_id: Optional[UUID] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class CampaignPerformance(BaseModel):
    """Campaign performance metrics."""
    id: UUID
    campaign_id: UUID
    date: datetime
    sent_count: int
    delivered_count: int
    open_count: int
    click_count: int
    conversion_count: int
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    revenue: Optional[float] = None
    roi: Optional[float] = None

    class Config:
        from_attributes = True


class CampaignScheduleRequest(BaseModel):
    """Request to schedule a campaign."""
    scheduled_at: datetime


class CampaignTestRequest(BaseModel):
    """Request to send a test campaign."""
    recipient_email: str = Field(..., description="Email address for test send")
