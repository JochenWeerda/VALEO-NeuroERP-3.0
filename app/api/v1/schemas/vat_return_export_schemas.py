"""Auto-generated domain schemas for vat return export.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class VatReturnExportOut(BaseSchema):
    """Response schema for vat return export endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class VATReturnCreate(BaseModel):
    """Schema for creating a VAT return"""
    period: str = Field(..., description="Period in YYYY-MM format")
    return_type: str = Field(default="monthly", description="monthly or quarterly")
    taxpayer_name: str = Field(..., description="Taxpayer name")
    tax_id: Optional[str] = Field(None, description="Tax ID (Steuernummer)")
    vat_id: Optional[str] = Field(None, description="VAT ID (USt-IdNr)")
    positions: List[VATReturnPosition] = Field(..., min_length=1, description="VAT return positions")
    notes: Optional[str] = None


class VATReturnResponse(BaseModel):
    """Response schema for VAT return"""
    id: str
    period: str
    return_type: str
    taxpayer_name: str
    tax_id: Optional[str]
    vat_id: Optional[str]
    total_sales_net: Decimal
    total_input_tax: Decimal
    total_output_tax: Decimal
    vat_payable: Decimal
    positions: List[Dict[str, Any]]
    status: str  # draft, calculated, validated, submitted
    calculated_at: Optional[datetime]
    validated_at: Optional[datetime]
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    submitted_at: Optional[datetime]
    elster_reference: Optional[str] = None
    approval_status: str | None = None
    approval_can_submit: bool = False
    approval_override_resolution: PolicyOverrideResolution | None = None
    approval_explainability: ExplainabilityView | None = None
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VATReturnCalculationRequest(BaseModel):
    """Request to calculate VAT return from journal entries"""
    period: str = Field(..., description="Period in YYYY-MM format")
    tenant_id: Optional[str] = Field(default=None)


class ELSTERExportRequest(BaseModel):
    """Request to export VAT return as ELSTER XML"""
    return_id: str = Field(..., description="VAT return ID")
    export_format: str = Field(default="elster_xml", description="Export format: elster_xml, csv, pdf")


class VATReturnApprovalRequest(BaseModel):
    approved_by: str = Field(..., min_length=1)


class VATReturnSubmitRequest(BaseModel):
    submitted_by: str = Field(..., min_length=1)

