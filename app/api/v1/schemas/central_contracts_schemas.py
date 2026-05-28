"""Auto-generated domain schemas for central contracts.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class CentralContractsOut(BaseSchema):
    """Response schema for central contracts endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class ContractCreate(BaseModel):
    contract_number: Optional[str] = None
    contract_type: str
    title: str = Field(..., min_length=1)
    counterparty_id: str = Field(..., min_length=1)
    counterparty_type: str = "CUSTOMER"
    status: str = "ENTWURF"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None


class ContractOut(BaseModel):
    id: str
    contract_number: str
    contract_type: str
    title: str
    counterparty_id: str
    counterparty_type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_renewal_days: Optional[int] = None
    notice_period_days: Optional[int] = None
    total_value_eur: Optional[float] = None
    tenant_id: str
    created_at: Optional[datetime] = None


class ObligationCreate(BaseModel):
    obligation_type: str
    due_date: datetime
    description: str = Field(..., min_length=1)


class ObligationUpdate(BaseModel):
    status: str


class ObligationOut(BaseModel):
    id: str
    contract_id: str
    obligation_type: str
    due_date: datetime
    description: str
    status: str
    tenant_id: str

