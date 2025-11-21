"""Pydantic schemas for Opportunities."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    """Base opportunity schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    status: str = "prospecting"
    stage: str = "initial_contact"
    lead_source: Optional[str] = Field(None, max_length=128)
    assigned_to: Optional[str] = Field(None, max_length=64)
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating opportunities."""
    tenant_id: str = Field(..., max_length=64)


class OpportunityUpdate(BaseModel):
    """Schema for updating opportunities."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    lead_source: Optional[str] = Field(None, max_length=128)
    assigned_to: Optional[str] = Field(None, max_length=64)
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None


class Opportunity(OpportunityBase):
    """Full opportunity schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True