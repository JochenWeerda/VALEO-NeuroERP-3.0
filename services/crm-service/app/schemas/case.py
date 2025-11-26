"""Pydantic schemas for Cases."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CaseBase(BaseModel):
    """Base case schema."""
    subject: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = "new"
    priority: str = "medium"
    case_type: str = "incident"
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    assigned_to: Optional[str] = Field(None, max_length=64)
    resolution: Optional[str] = None
    sla_id: Optional[UUID] = None
    category_id: Optional[UUID] = None


class CaseCreate(CaseBase):
    """Schema for creating cases."""
    tenant_id: str = Field(..., max_length=64)


class CaseUpdate(BaseModel):
    """Schema for updating cases."""
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    case_type: Optional[str] = None
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    assigned_to: Optional[str] = Field(None, max_length=64)
    resolution: Optional[str] = None
    sla_id: Optional[UUID] = None
    category_id: Optional[UUID] = None


class Case(CaseBase):
    """Full case schema."""
    id: UUID
    tenant_id: str
    case_number: str
    assigned_by: Optional[str] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    sla_breached: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseHistory(BaseModel):
    """Case history entry schema."""
    id: UUID
    case_id: UUID
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    field_name: Optional[str] = None
    performed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True