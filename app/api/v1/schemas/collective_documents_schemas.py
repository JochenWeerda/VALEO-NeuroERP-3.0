"""Auto-generated domain schemas for collective documents.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class CollectiveDocumentsOut(BaseSchema):
    """Response schema for collective documents endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class CollectiveInvoiceCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    delivery_note_ids: list[str] = Field(..., min_length=1)
    invoice_date: str  # ISO date string


class CollectiveDeliveryCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    order_ids: list[str] = Field(..., min_length=1)
    delivery_date: str  # ISO date string


class CollectiveInvoiceOut(BaseModel):
    id: str
    invoice_number: str
    customer_id: str
    invoice_date: str
    total_amount: float
    delivery_note_ids: list[str]
    status: str
    tenant_id: str
    created_at: Optional[datetime] = None


class CollectiveDeliveryOut(BaseModel):
    id: str
    delivery_note_number: str
    customer_id: str
    delivery_date: str
    total_amount: float
    order_ids: list[str]
    status: str
    tenant_id: str
    created_at: Optional[datetime] = None


class EligibleDeliveryNoteOut(BaseModel):
    id: str
    delivery_note_number: str
    delivery_date: Optional[str] = None
    total_amount: float
    status: str

