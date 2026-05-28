"""Auto-generated domain schemas for payment runs.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class PaymentRunsOut(BaseSchema):
    """Response schema for payment runs endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class PaymentRunCreate(BaseModel):
    """Schema for creating a payment run"""
    run_number: str = Field(..., min_length=1, max_length=50, description="Payment run number")
    execution_date: date = Field(..., description="Execution date")
    initiator_name: str = Field(..., min_length=1, description="Initiator name")
    initiator_iban: str = Field(..., description="Initiator IBAN")
    initiator_bic: str = Field(..., description="Initiator BIC")
    payments: List[PaymentItem] = Field(..., min_length=1, description="Payment items")
    notes: Optional[str] = Field(None, description="Notes")


class PaymentRunResponse(BaseModel):
    """Response schema for payment run"""
    id: str
    run_number: str
    execution_date: date
    initiator_name: str
    initiator_iban: str
    initiator_bic: str
    total_amount: Decimal
    payment_count: int
    status: str  # draft, approved, executed, cancelled, returned
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    executed_at: Optional[datetime]
    sepa_file_id: Optional[str]
    notes: Optional[str]
    payments: List[Dict[str, Any]]
    approval_status: str | None = None
    approval_can_execute: bool = False
    approval_override_resolution: PolicyOverrideResolution | None = None
    approval_explainability: ExplainabilityView | None = None
    created_at: datetime
    updated_at: datetime


class ApprovePaymentRunRequest(BaseModel):
    """Request to approve a payment run"""
    approved_by: str = Field(default="api", description="User approving the run")


class ExecutePaymentRunRequest(BaseModel):
    """Request to execute a payment run"""
    executed_by: str = Field(..., description="User executing the run")


class ReturnPaymentRequest(BaseModel):
    """Request to process a returned payment"""
    payment_id: str = Field(..., description="Payment ID that was returned")
    return_reason: str = Field(..., description="Return reason code")
    return_date: date = Field(..., description="Return date")
    notes: Optional[str] = None


class PaymentRunPlanRequest(BaseModel):
    """Request to plan a payment run (suggest payments from open items)"""
    execution_date: date = Field(..., description="Geplantes Ausführungsdatum")
    creditor_ids: Optional[List[str]] = Field(None, description="Nur diese Kreditoren (optional)")
    tenant_id: str = Field(default="system")


class PaymentRunPlanResponse(BaseModel):
    """Suggested payment run from open items"""
    suggested_payments: List[Dict[str, Any]]
    total_amount: Decimal
    execution_date: date
    message: str

