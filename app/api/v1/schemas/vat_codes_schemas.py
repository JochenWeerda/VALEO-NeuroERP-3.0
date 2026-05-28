"""Auto-generated domain schemas for vat codes.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class VatCodesOut(BaseSchema):
    """Response schema for vat codes endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class VatCodeCreate(BaseModel):
    id: str
    name: str
    name_long: Optional[str] = None
    category: VatCodeCategory
    rate: float
    skr03_account: Optional[str] = None
    skr04_account: Optional[str] = None
    legal_basis: Optional[str] = None
    legal_note: Optional[str] = None
    is_standard: bool = False
    is_reduced: bool = False
    is_zero: bool = False
    is_reverse_charge: bool = False
    is_agricultural: bool = False
    paragraph_24: bool = False
    valid_from: Optional[datetime] = None


class VatCodeUpdate(BaseModel):
    name: Optional[str] = None
    name_long: Optional[str] = None
    rate: Optional[float] = None
    skr03_account: Optional[str] = None
    skr04_account: Optional[str] = None
    legal_basis: Optional[str] = None
    legal_note: Optional[str] = None
    is_standard: Optional[bool] = None
    is_reduced: Optional[bool] = None
    is_zero: Optional[bool] = None
    is_reverse_charge: Optional[bool] = None
    is_agricultural: Optional[bool] = None
    paragraph_24: Optional[bool] = None
    is_active: Optional[bool] = None
    valid_to: Optional[datetime] = None


class VatCodeResponse(BaseModel):
    id: str
    name: str
    name_long: Optional[str]
    category: str
    rate: float
    skr03_account: Optional[str]
    skr04_account: Optional[str]
    legal_basis: Optional[str]
    legal_note: Optional[str]
    is_standard: bool
    is_reduced: bool
    is_zero: bool
    is_reverse_charge: bool
    is_agricultural: bool
    paragraph_24: bool
    is_active: bool
    valid_from: datetime
    valid_to: Optional[datetime]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class VatCodeAuditResponse(BaseModel):
    id: str
    vat_code_id: str
    action: str
    change_type: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: str
    changed_at: datetime
    reason: Optional[str]
    legal_reference: Optional[str]

