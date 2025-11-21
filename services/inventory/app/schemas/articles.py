from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ArticleSummary(BaseModel):
    id: str
    article_number: str
    name: str
    category: str = "default"
    unit: str = Field(default="PCS")
    current_stock: float
    available_stock: float
    reserved_stock: float
    min_stock: float | None = None
    max_stock: float | None = None
    sales_price: float = 0.0
    is_active: bool = True


class StockMovementCreate(BaseModel):
    article_id: str
    warehouse_id: UUID
    location_id: UUID
    movement_type: str = Field(pattern="^(in|out|transfer|adjustment)$")
    quantity: float = Field(gt=0)
    lot_id: UUID | None = None
    lot_number: str | None = None
    destination_warehouse_id: UUID | None = None
    destination_location_id: UUID | None = None
    reference_number: str | None = None
    notes: str | None = None


class StockMovementRecord(BaseModel):
    id: UUID
    movement_type: str
    quantity: float
    reference: str | None
    warehouse_id: UUID
    location_id: UUID | None
    lot_id: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True

