from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    code: str = Field(max_length=32)
    location_type: str = Field(default="STANDARD", max_length=32)
    capacity_units: int | None = None


class LocationRead(LocationCreate):
    id: UUID
    warehouse_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
