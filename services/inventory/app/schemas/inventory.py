from __future__ import annotations

from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class ReceiptCreate(BaseModel):
    warehouse_id: UUID
    location_id: UUID
    sku: str = Field(max_length=64)
    lot_number: str = Field(max_length=64)
    quantity: float = Field(gt=0)
    production_date: datetime | None = None
    expiry_date: datetime | None = None
    reference: str | None = None


class TransferCreate(BaseModel):
    source_stock_item_id: UUID | None = None
    source_location_id: UUID | None = None
    source_warehouse_id: UUID
    destination_location_id: UUID
    destination_warehouse_id: UUID
    lot_id: UUID | None = None
    quantity: float = Field(gt=0)
    reference: str | None = None


class StockItemRead(BaseModel):
    id: UUID
    warehouse_id: UUID
    location_id: UUID
    lot_id: UUID
    sku: str
    lot_number: str
    quantity: float
    reserved_quantity: float

    class Config:
        from_attributes = True


class TransactionRecord(BaseModel):
    id: UUID
    transaction_type: str
    quantity: float
    reference: str | None
    created_at: datetime
    from_location_id: UUID | None
    to_location_id: UUID | None

    class Config:
        from_attributes = True


class LotTraceResponse(BaseModel):
    lot_id: UUID
    sku: str
    lot_number: str
    transactions: list[TransactionRecord]


class LotListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    lot_number: str = Field(alias="lotNumber")
    commodity: str
    quantity: float
    unit: str
    location: str
    quality_status: Literal["good", "blocked", "pending"] = Field(alias="qualityStatus")
    expiry_date: datetime = Field(alias="expiryDate")
    supplier: str | None = None


class LotListResponse(BaseModel):
    items: list[LotListItem]
    total: int
