"""Auto-generated domain schemas for sales delivery notes.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class SalesDeliveryNotesOut(BaseSchema):
    """Response schema for sales delivery notes endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class DeliveryNotePositionCreate(DeliveryNotePositionBase):
    pass


class DeliveryNoteCreate(DeliveryNoteBase):
    positionen: list[DeliveryNotePositionCreate] = []


class DeliveryNoteUpdate(BaseModel):
    customer_id: Optional[str] = None
    branch_id: Optional[str] = None
    sales_rep_id: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[time] = None
    cost_center_id: Optional[str] = None
    truck_number: Optional[int] = None
    is_credit_note: Optional[bool] = None
    is_self_pickup: Optional[bool] = None
    is_early_payment: Optional[bool] = None
    reference_invoice_number: Optional[str] = None
    status: Optional[str] = None
    is_printed: Optional[bool] = None
    is_delivered: Optional[bool] = None
    invoice_number: Optional[str] = None
    positionen: Optional[list[DeliveryNotePositionCreate]] = None

