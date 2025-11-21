"""Pydantic schemas for Communication."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class EmailBase(BaseModel):
    """Base email schema."""
    from_address: str = Field(..., max_length=255)
    to_addresses: List[str] = Field(..., min_items=1)
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None
    subject: str = Field(..., max_length=500)
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    priority: str = "normal"


class EmailCreate(EmailBase):
    """Schema for creating emails."""
    tenant_id: str = Field(..., max_length=64)
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    case_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class EmailSend(EmailCreate):
    """Schema for sending emails."""
    attachments: Optional[List[dict]] = None  # File attachments


class Email(EmailBase):
    """Full email schema."""
    id: UUID
    tenant_id: str
    message_id: str
    thread_id: str
    direction: str
    status: str
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    case_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="email, sms, letter")
    subject_template: Optional[str] = Field(None, max_length=500)
    body_template: str
    variables: dict = Field(default_factory=dict)
    sample_data: dict = Field(default_factory=dict)
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)


class TemplateCreate(TemplateBase):
    """Schema for creating templates."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class TemplateUpdate(BaseModel):
    """Schema for updating templates."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    subject_template: Optional[str] = Field(None, max_length=500)
    body_template: Optional[str] = None
    variables: Optional[dict] = None
    sample_data: Optional[dict] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Template(TemplateBase):
    """Full template schema."""
    id: UUID
    tenant_id: str
    is_active: bool = True
    is_default: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    template_id: UUID
    target_filters: dict = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    """Schema for creating campaigns."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class CampaignUpdate(BaseModel):
    """Schema for updating campaigns."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    template_id: Optional[UUID] = None
    target_filters: Optional[dict] = None
    scheduled_at: Optional[datetime] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Campaign(CampaignBase):
    """Full campaign schema."""
    id: UUID
    tenant_id: str
    status: str = "draft"
    target_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    bounced_count: int = 0
    unsubscribed_count: int = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttachmentBase(BaseModel):
    """Base attachment schema."""
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=100)
    size: int
    inline: bool = False
    content_id: Optional[str] = Field(None, max_length=255)


class Attachment(AttachmentBase):
    """Full attachment schema."""
    id: UUID
    email_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AutomationBase(BaseModel):
    """Base automation schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    trigger_conditions: dict = Field(..., description="When to trigger")
    actions: List[dict] = Field(..., description="What to do")
    priority: int = 0


class AutomationCreate(AutomationBase):
    """Schema for creating automations."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class AutomationUpdate(BaseModel):
    """Schema for updating automations."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    trigger_conditions: Optional[dict] = None
    actions: Optional[List[dict]] = None
    priority: Optional[int] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Automation(AutomationBase):
    """Full automation schema."""
    id: UUID
    tenant_id: str
    is_active: bool = True
    trigger_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationAnalytics(BaseModel):
    """Communication analytics response."""
    total_emails: int
    sent_emails: int
    delivered_emails: int
    opened_emails: int
    clicked_emails: int
    bounced_emails: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    bounce_rate: float
    response_time_avg: Optional[float] = None
    customer_satisfaction: Optional[float] = None
    period: str = "last_30_days"