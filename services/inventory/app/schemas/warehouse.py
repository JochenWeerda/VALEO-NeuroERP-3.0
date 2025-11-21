from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WarehouseBase(BaseModel):
    code: str = Field(max_length=32)
    name: str = Field(max_length=128)
    address: str | None = None


class WarehouseCreate(WarehouseBase):
    is_active: bool = True


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=128)
    address: str | None = None
    is_active: bool | None = None


class WarehouseRead(WarehouseBase):
    id: UUID
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
