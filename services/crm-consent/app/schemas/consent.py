"""Pydantic schemas for Consent."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConsentBase(BaseModel):
    """Base consent schema."""
    contact_id: UUID
    channel: str = Field(..., description="Communication channel: email, sms, phone, postal")
    consent_type: str = Field(..., description="Type: marketing, service, required")
    source: str = Field(default="manual", description="Source: web_form, api, import, manual")
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime | None = None


class ConsentCreate(ConsentBase):
    """Schema for creating a consent."""
    tenant_id: str
    # Double opt-in will be handled automatically
    pass


class ConsentUpdate(BaseModel):
    """Schema for updating a consent."""
    status: str | None = None
    expires_at: datetime | None = None
    reason: str | None = None


class Consent(ConsentBase):
    """Full consent schema."""
    id: UUID
    tenant_id: str
    status: str
    granted_at: datetime | None = None
    denied_at: datetime | None = None
    revoked_at: datetime | None = None
    double_opt_in_token: UUID | None = None
    double_opt_in_confirmed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class ConsentHistory(BaseModel):
    """Consent history entry."""
    id: UUID
    consent_id: UUID
    action: str
    old_status: str | None = None
    new_status: str
    reason: str | None = None
    changed_by: str
    changed_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None

    class Config:
        from_attributes = True


class ConsentCheckRequest(BaseModel):
    """Request to check consent."""
    contact_id: UUID
    channel: str
    consent_type: str | None = None  # If None, checks for any consent type


class ConsentCheckResponse(BaseModel):
    """Response to consent check."""
    has_consent: bool
    consent_id: UUID | None = None
    status: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None
    is_expired: bool = False

