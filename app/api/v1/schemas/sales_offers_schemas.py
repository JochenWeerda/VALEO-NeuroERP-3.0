"""Auto-generated domain schemas for sales offers.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class SalesOffersOut(BaseSchema):
    """Response schema for sales offers endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SalesOfferItemOut(SalesOfferItemInput):
    id: str
    line_number: int
    line_total: float


class SalesOfferCreate(SalesOfferBase):
    tenant_id: Optional[str] = None


class SalesOfferUpdate(BaseModel):
    offer_number: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    contact_person: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    is_pauschale: Optional[bool] = None
    items: Optional[list[SalesOfferItemInput]] = None

