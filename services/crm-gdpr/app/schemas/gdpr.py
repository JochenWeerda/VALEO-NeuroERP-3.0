"""Pydantic schemas for GDPR requests."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GDPRRequestBase(BaseModel):
    """Base GDPR request schema."""
    request_type: str = Field(..., description="Type: access, deletion, portability, objection")
    contact_id: UUID
    notes: str | None = None


class GDPRRequestCreate(GDPRRequestBase):
    """Schema for creating a GDPR request."""
    tenant_id: str
    requested_by: str = Field(..., description="User ID or contact email")
    is_self_request: bool = Field(default=True, description="Requested by data subject themselves")


class GDPRRequestUpdate(BaseModel):
    """Schema for updating a GDPR request."""
    status: str | None = None
    notes: str | None = None


class GDPRRequest(GDPRRequestBase):
    """Full GDPR request schema."""
    id: UUID
    tenant_id: str
    status: str
    requested_at: datetime
    completed_at: datetime | None = None
    rejected_at: datetime | None = None
    requested_by: str
    is_self_request: bool
    verified_at: datetime | None = None
    verification_method: str | None = None
    response_data: dict | None = None
    response_file_path: str | None = None
    response_file_format: str | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class GDPRRequestHistory(BaseModel):
    """GDPR request history entry."""
    id: UUID
    request_id: UUID
    action: str
    old_status: str | None = None
    new_status: str | None = None
    notes: str | None = None
    changed_by: str
    changed_at: datetime

    class Config:
        from_attributes = True


class GDPRRequestVerify(BaseModel):
    """Schema for verifying a GDPR request."""
    verification_method: str = Field(..., description="email, id_card, manual, other")
    verification_token: UUID | None = None  # For email verification


class GDPRRequestExport(BaseModel):
    """Schema for generating data export."""
    format: str = Field(default="json", description="json, csv, pdf")
    data_areas: list[str] = Field(default_factory=lambda: ["all"], description="Which data areas to include")


class GDPRRequestDelete(BaseModel):
    """Schema for deleting/anonymizing data."""
    reason: str | None = None
    anonymize_only: bool = Field(default=True, description="Anonymize instead of hard delete (GoBD compliance)")


class GDPRRequestReject(BaseModel):
    """Schema for rejecting a GDPR request."""
    rejection_reason: str = Field(..., description="Reason for rejection")


class GDPRCheckRequest(BaseModel):
    """Request to check if GDPR request exists for contact."""
    contact_id: UUID
    request_type: str | None = None  # If None, checks for any request type


class GDPRCheckResponse(BaseModel):
    """Response to GDPR check."""
    has_request: bool
    request_id: UUID | None = None
    status: str | None = None
    request_type: str | None = None

