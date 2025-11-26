from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import ORMModel


class LeadCreate(BaseModel):
    company_name: str = Field(..., max_length=255)
    contact_person: str = Field(..., max_length=150)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    status: str = Field(default="new", max_length=32)
    priority: str = Field(default="medium", max_length=16)
    source: str | None = Field(default=None, max_length=64)
    estimated_value: float | None = None
    assigned_to: str | None = Field(default=None, max_length=64)
    notes: str | None = None
    customer_id: UUID | None = None


class LeadUpdate(BaseModel):
    company_name: str | None = Field(default=None, max_length=255)
    contact_person: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=32)
    priority: str | None = Field(default=None, max_length=16)
    source: str | None = Field(default=None, max_length=64)
    estimated_value: float | None = None
    assigned_to: str | None = Field(default=None, max_length=64)
    notes: str | None = None
    customer_id: UUID | None = None


class LeadRead(ORMModel):
    id: UUID
    tenant_id: str
    company_name: str
    contact_person: str
    email: str | None
    phone: str | None
    status: str
    priority: str
    source: str | None
    estimated_value: float | None
    assigned_to: str | None
    notes: str | None
    customer_id: UUID | None
    customer_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class LeadListResponse(BaseModel):
    items: list[LeadRead]
    total: int
