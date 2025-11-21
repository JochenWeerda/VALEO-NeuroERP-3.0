"""Pydantic schemas for Sales Activities."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SalesActivityBase(BaseModel):
    """Base sales activity schema."""
    opportunity_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    activity_type: str = Field(..., max_length=32)  # call, meeting, email, demo, etc.
    subject: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = "planned"  # planned, completed, cancelled
    priority: str = "medium"  # high, medium, low
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[float] = Field(None, ge=0)
    assigned_to: Optional[str] = Field(None, max_length=64)
    outcome: Optional[str] = None


class SalesActivityCreate(SalesActivityBase):
    """Schema for creating sales activities."""
    tenant_id: str = Field(..., max_length=64)


class SalesActivityUpdate(BaseModel):
    """Schema for updating sales activities."""
    opportunity_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    activity_type: Optional[str] = Field(None, max_length=32)
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[float] = Field(None, ge=0)
    assigned_to: Optional[str] = Field(None, max_length=64)
    outcome: Optional[str] = None


class SalesActivity(SalesActivityBase):
    """Full sales activity schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True