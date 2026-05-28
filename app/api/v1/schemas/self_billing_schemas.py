"""Auto-generated domain schemas for self billing.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class SelfBillingOut(BaseSchema):
    """Response schema for self billing endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SelfBillingInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Self-Billing Gutschrift."""
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str] = None
    invoice_number: str
    provisional_invoice_number: Optional[str] = None
    status: str
    dispute_status: Optional[str] = None
    dispute_reason: Optional[str] = None
    dispute_date: Optional[datetime] = None
    dispute_user_id: Optional[str] = None
    total_net_amount_eur: float
    total_vat_amount_eur: float
    total_gross_amount_eur: float
    vat_rate_percent: float
    einvoice_sent_at: Optional[datetime] = None
    einvoice_received_at: Optional[datetime] = None
    mandatory_texts: Optional[list[dict]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class CreditNoteCreateIn(BaseModel):
    """Input-Model für Gutschrift-Erstellung."""
    harvest_acceptance_id: str
    invoice_number: Optional[str] = None
    provisional_invoice_number: Optional[str] = None
    total_net_amount_eur: float = Field(..., gt=0)
    total_vat_amount_eur: float = Field(..., ge=0)
    total_gross_amount_eur: float = Field(..., gt=0)
    vat_rate_percent: float = Field(..., ge=0, le=100)
    mandatory_texts: Optional[list[dict]] = None
    taxation_type: str = "regular"  # regular / ustg24_flat_rate / small_business


class DisputeCreateIn(BaseModel):
    """Input-Model für Dispute-Erstellung."""
    dispute_type: str = Field(..., pattern="^(amount|quality|quantity|other)$")
    dispute_reason: str = Field(..., min_length=1)
    disputed_amount_eur: Optional[float] = Field(None, ge=0)


class EinvoiceGenerateIn(BaseModel):
    """Input-Model für E-Rechnung-Generierung."""
    supplier_data: dict = Field(..., description="Lieferantendaten (Name, Adresse, USt-ID, etc.)")
    customer_data: dict = Field(..., description="Kundendaten (Name, Adresse, USt-ID, etc.)")
    line_items: list[dict] = Field(..., description="Rechnungspositionen")
    format: str = Field("xrechnung", pattern="^(xrechnung|zugferd)$")


class PreviewIn(BaseModel):
    harvest_acceptance_id: str
    total_net_amount_eur: float = Field(0, ge=0)
    total_gross_amount_eur: float = Field(0, ge=0)
    vat_rate_percent: float = Field(0, ge=0, le=100)
    taxation_type: str = "regular"

