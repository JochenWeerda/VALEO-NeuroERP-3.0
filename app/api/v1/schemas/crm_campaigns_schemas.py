"""Pydantic schemas for the crm campaigns domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CrmCampaignOut(BaseSchema):
    """Typed response schema for CrmCampaignOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str = Field("email", pattern=r"^(email|sms|post|event|webinar|push)$")
    subject_line: Optional[str] = Field(None, max_length=500)
    message_body: Optional[str] = None
    is_active: bool = True
    meta: Optional[dict] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    subject_line: Optional[str] = None
    message_body: Optional[str] = None
    is_active: Optional[bool] = None
    meta: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    campaign_type: str
    subject_line: Optional[str]
    message_body: Optional[str]
    is_active: bool
    created_by: Optional[str]
    meta: Optional[dict]
    created_at: str
    updated_at: str


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str = Field("email", pattern=r"^(email|sms|post|event|webinar|push)$")
    template_id: Optional[str] = None
    segment_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    owner_id: Optional[str] = None
    campaign_channel: Optional[str] = None
    target_customer_type: Optional[str] = None
    seasonal_context: Optional[str] = None
    meta: Optional[dict] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    template_id: Optional[str] = None
    segment_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    owner_id: Optional[str] = None
    campaign_channel: Optional[str] = None
    target_customer_type: Optional[str] = None
    seasonal_context: Optional[str] = None
    meta: Optional[dict] = None


class RecipientStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(queued|sent|bounced|opened|clicked|converted|unsubscribed)$")
    bounce_reason: Optional[str] = None

