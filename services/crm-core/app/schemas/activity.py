from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel


class ActivityCreate(BaseModel):
    type: str = Field(..., max_length=32)
    title: str = Field(..., max_length=255)
    status: str = Field(default="planned", max_length=32)
    scheduled_at: datetime | None = None
    assigned_to: str | None = Field(default=None, max_length=64)
    description: str | None = None
    customer_id: UUID | None = None
    contact_id: UUID | None = None


class ActivityUpdate(BaseModel):
    type: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=32)
    scheduled_at: datetime | None = None
    assigned_to: str | None = Field(default=None, max_length=64)
    description: str | None = None
    customer_id: UUID | None = None
    contact_id: UUID | None = None


class ActivityRead(ORMModel):
    id: UUID
    tenant_id: str
    type: str
    title: str
    status: str
    assigned_to: str | None
    scheduled_at: datetime | None
    description: str | None
    customer_id: UUID | None
    customer_name: str | None = None
    contact_id: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ActivityListResponse(BaseModel):
    items: list[ActivityRead]
    total: int
