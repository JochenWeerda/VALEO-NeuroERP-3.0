"""Pydantic schemas for Multi-Channel Integration."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Base channel schema."""
    name: str = Field(..., max_length=255)
    type: str = Field(..., description="facebook, twitter, linkedin, etc.")
    config: dict = Field(default_factory=dict)
    external_id: Optional[str] = Field(None, max_length=255)
    webhook_url: Optional[str] = Field(None, max_length=500)


class ChannelCreate(ChannelBase):
    """Schema for creating channels."""
    tenant_id: str = Field(..., max_length=64)
    credentials: dict = Field(default_factory=dict)
    created_by: Optional[str] = Field(None, max_length=64)


class ChannelUpdate(BaseModel):
    """Schema for updating channels."""
    name: Optional[str] = Field(None, max_length=255)
    config: Optional[dict] = None
    credentials: Optional[dict] = None
    external_id: Optional[str] = Field(None, max_length=255)
    webhook_url: Optional[str] = Field(None, max_length=500)
    updated_by: Optional[str] = Field(None, max_length=64)


class Channel(ChannelBase):
    """Full channel schema."""
    id: UUID
    tenant_id: str
    status: str = "pending"
    messages_sent: int = 0
    messages_received: int = 0
    last_activity: Optional[datetime] = None
    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema."""
    external_id: str = Field(..., max_length=255)
    thread_id: Optional[str] = Field(None, max_length=255)
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    subject: Optional[str] = Field(None, max_length=500)
    priority: str = "normal"
    tags: List[str] = Field(default_factory=list)


class ConversationCreate(ConversationBase):
    """Schema for creating conversations."""
    tenant_id: str = Field(..., max_length=64)
    channel_id: UUID


class ConversationUpdate(BaseModel):
    """Schema for updating conversations."""
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    subject: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[str] = None


class Conversation(ConversationBase):
    """Full conversation schema."""
    id: UUID
    tenant_id: str
    channel_id: UUID
    status: str = "open"
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    started_at: datetime
    last_message_at: datetime
    closed_at: Optional[datetime] = None
    message_count: int = 0
    customer_message_count: int = 0
    agent_message_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base message schema."""
    external_id: str = Field(..., max_length=255)
    external_parent_id: Optional[str] = Field(None, max_length=255)
    direction: str = Field(..., description="inbound, outbound")
    type: str = Field("text", description="text, image, video, file, link")
    content: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    sender_id: Optional[str] = Field(None, max_length=255)
    sender_name: Optional[str] = Field(None, max_length=255)
    sender_type: str = "customer"


class MessageCreate(MessageBase):
    """Schema for creating messages."""
    tenant_id: str = Field(..., max_length=64)
    conversation_id: UUID


class Message(MessageBase):
    """Full message schema."""
    id: UUID
    tenant_id: str
    conversation_id: UUID
    is_read: bool = False
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    handled_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebFormBase(BaseModel):
    """Base web form schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    fields: List[dict] = Field(..., min_items=1)
    settings: dict = Field(default_factory=dict)
    slug: str = Field(..., max_length=255)
    lead_source: Optional[str] = Field(None, max_length=64)
    auto_create_lead: bool = True
    notification_emails: List[str] = Field(default_factory=list)


class WebFormCreate(WebFormBase):
    """Schema for creating web forms."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class WebFormUpdate(BaseModel):
    """Schema for updating web forms."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    fields: Optional[List[dict]] = None
    settings: Optional[dict] = None
    slug: Optional[str] = Field(None, max_length=255)
    lead_source: Optional[str] = Field(None, max_length=64)
    auto_create_lead: Optional[bool] = None
    notification_emails: Optional[List[str]] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class WebForm(WebFormBase):
    """Full web form schema."""
    id: UUID
    tenant_id: str
    is_published: bool = False
    published_at: Optional[datetime] = None
    view_count: int = 0
    submission_count: int = 0
    conversion_rate: Optional[float] = None
    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormSubmissionBase(BaseModel):
    """Base form submission schema."""
    data: dict = Field(..., description="Form field values")
    metadata: dict = Field(default_factory=dict)
    source_url: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)
    utm_parameters: dict = Field(default_factory=dict)


class FormSubmissionCreate(FormSubmissionBase):
    """Schema for creating form submissions."""
    tenant_id: str = Field(..., max_length=64)
    form_id: UUID


class FormSubmission(FormSubmissionBase):
    """Full form submission schema."""
    id: UUID
    tenant_id: str
    form_id: UUID
    lead_created: bool = False
    lead_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    processing_status: str = "pending"
    created_at: datetime

    class Config:
        from_attributes = True


class IntegrationBase(BaseModel):
    """Base integration schema."""
    name: str = Field(..., max_length=255)
    type: str = Field(..., max_length=64, description="shopify, woocommerce, stripe, erp")
    config: dict = Field(default_factory=dict)
    sync_enabled: bool = True
    sync_frequency: int = 3600
    sync_entities: List[str] = Field(default_factory=list)


class IntegrationCreate(IntegrationBase):
    """Schema for creating integrations."""
    tenant_id: str = Field(..., max_length=64)
    credentials: dict = Field(default_factory=dict)
    created_by: Optional[str] = Field(None, max_length=64)


class IntegrationUpdate(BaseModel):
    """Schema for updating integrations."""
    name: Optional[str] = Field(None, max_length=255)
    config: Optional[dict] = None
    credentials: Optional[dict] = None
    sync_enabled: Optional[bool] = None
    sync_frequency: Optional[int] = None
    sync_entities: Optional[List[str]] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Integration(IntegrationBase):
    """Full integration schema."""
    id: UUID
    tenant_id: str
    status: str = "disconnected"
    last_sync: Optional[datetime] = None
    last_error: Optional[str] = None
    records_synced: int = 0
    last_record_count: int = 0
    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Request schema for sending messages."""
    conversation_id: UUID
    content: str = Field(..., max_length=4096)
    type: str = "text"
    metadata: dict = Field(default_factory=dict)
    attachments: Optional[List[dict]] = None


class SendMessageResponse(BaseModel):
    """Response schema for sending messages."""
    message_id: UUID
    external_id: str
    status: str = "sent"
    sent_at: datetime


class WebhookPayload(BaseModel):
    """Generic webhook payload schema."""
    platform: str
    event_type: str
    data: dict
    timestamp: datetime
    signature: Optional[str] = None


class ChannelAnalytics(BaseModel):
    """Channel performance analytics."""
    channel_id: UUID
    channel_type: str
    messages_sent: int
    messages_received: int
    response_time_avg: Optional[float] = None
    customer_satisfaction: Optional[float] = None
    conversion_rate: Optional[float] = None
    period: str = "last_30_days"


class OmnichannelAnalytics(BaseModel):
    """Omnichannel analytics overview."""
    total_conversations: int
    active_conversations: int
    avg_response_time: Optional[float] = None
    customer_satisfaction_avg: Optional[float] = None
    channel_breakdown: Dict[str, int] = Field(default_factory=dict)
    peak_hours: List[int] = Field(default_factory=list)
    period: str = "last_30_days"