"""Schemas for Goods Receipt (Wareneingang) against Purchase Orders."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class GoodsReceiptStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class GoodsReceiptLineCreate(BaseModel):
    """A single line item for a goods receipt."""
    po_line_number: int = Field(ge=1, description="Line number from the purchase order")
    sku: str = Field(max_length=64, description="Article/SKU number")
    description: str = Field(max_length=256, default="")
    ordered_quantity: float = Field(gt=0, description="Quantity originally ordered")
    received_quantity: float = Field(gt=0, description="Quantity actually received")
    unit: str = Field(max_length=16, default="ST", description="Unit of measure (ST, KG, L, etc.)")
    lot_number: Optional[str] = Field(None, max_length=64, description="Lot/batch number")
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    warehouse_id: UUID = Field(description="Target warehouse")
    location_id: UUID = Field(description="Target storage location")
    quality_status: str = Field(default="pending", description="Quality status: good, pending, blocked")
    notes: str = Field(default="", max_length=500)


class GoodsReceiptCreate(BaseModel):
    """Create a goods receipt (Wareneingang)."""
    po_number: str = Field(max_length=64, description="Purchase order number")
    po_id: Optional[UUID] = Field(None, description="Purchase order UUID")
    supplier_id: Optional[UUID] = Field(None, description="Supplier UUID")
    supplier_name: str = Field(max_length=256, default="")
    delivery_note_number: Optional[str] = Field(None, max_length=64, description="Lieferschein-Nr.")
    receipt_date: datetime = Field(default_factory=datetime.utcnow)
    lines: List[GoodsReceiptLineCreate] = Field(min_length=1)
    notes: str = Field(default="", max_length=1000)


class GoodsReceiptLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    po_line_number: int
    sku: str
    description: str
    ordered_quantity: float
    received_quantity: float
    unit: str
    lot_number: Optional[str]
    warehouse_id: UUID
    location_id: UUID
    quality_status: str
    notes: str


class GoodsReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    gr_number: str
    po_number: str
    po_id: Optional[UUID]
    supplier_id: Optional[UUID]
    supplier_name: str
    delivery_note_number: Optional[str]
    receipt_date: datetime
    status: GoodsReceiptStatus
    lines: List[GoodsReceiptLineRead]
    notes: str
    created_at: datetime
    created_by: str
    tenant_id: str


class GoodsReceiptListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    gr_number: str
    po_number: str
    supplier_name: str
    receipt_date: datetime
    status: GoodsReceiptStatus
    line_count: int
    total_received: float
    created_at: datetime


class GoodsReceiptListResponse(BaseModel):
    items: List[GoodsReceiptListItem]
    total: int


class MatchingStatus(str, Enum):
    MATCHED = "matched"
    QUANTITY_MISMATCH = "quantity_mismatch"
    PRICE_MISMATCH = "price_mismatch"
    NOT_MATCHED = "not_matched"
    PARTIAL = "partial"


class ThreeWayMatchLine(BaseModel):
    """Result of 3-way matching for a single line."""
    po_line_number: int
    sku: str
    description: str
    po_quantity: float
    gr_quantity: float
    invoice_quantity: Optional[float] = None
    po_unit_price: Optional[float] = None
    invoice_unit_price: Optional[float] = None
    quantity_match: bool
    price_match: Optional[bool] = None
    status: MatchingStatus
    variance_quantity: float = 0.0
    variance_price: float = 0.0
    tolerance_percent: float = Field(default=2.0, description="Allowed tolerance in %")


class ThreeWayMatchResult(BaseModel):
    """Result of 3-way matching for a complete PO."""
    po_number: str
    po_id: Optional[UUID] = None
    gr_number: Optional[str] = None
    invoice_number: Optional[str] = None
    overall_status: MatchingStatus
    lines: List[ThreeWayMatchLine]
    total_po_amount: float = 0.0
    total_gr_amount: float = 0.0
    total_invoice_amount: float = 0.0
    can_approve: bool = False
    notes: str = ""

