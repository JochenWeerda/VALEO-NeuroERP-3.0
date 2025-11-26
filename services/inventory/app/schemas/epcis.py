from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EpcisEventCreate(BaseModel):
    event_type: str = Field(pattern="^(ObjectEvent|AggregationEvent|TransformationEvent|TransactionEvent)$")
    event_time: datetime | None = None
    biz_step: str | None = None
    read_point: str | None = None
    lot_id: UUID | None = None
    sku: str | None = None
    quantity: float | None = None
    extensions: dict[str, Any] | None = None
    idempotency_key: str | None = Field(default=None, max_length=128, description="Optionaler Deduplikationsschlüssel")


class EpcisEventRead(BaseModel):
    id: UUID
    event_type: str
    event_time: datetime
    tenant_id: str
    biz_step: str | None
    read_point: str | None
    lot_id: UUID | None
    sku: str | None
    quantity: float | None
    extensions: dict[str, Any] | None
    created_at: datetime
    # Event-Key kann weggelassen werden; für Transparenz optional exponieren
    # event_key: str | None = None

    class Config:
        from_attributes = True


class EpcisEventsResponse(BaseModel):
    items: list[EpcisEventRead]
    total: int

