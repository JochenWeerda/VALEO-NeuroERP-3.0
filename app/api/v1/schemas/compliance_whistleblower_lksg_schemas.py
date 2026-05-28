"""Auto-generated domain schemas for compliance whistleblower lksg.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ComplianceWhistleblowerLksgOut(BaseSchema):
    """Response schema for compliance whistleblower lksg endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class WhistleblowerReportIn(BaseModel):
    category: str = Field(..., max_length=80)
    description: str = Field(..., min_length=10, max_length=4000)
    contact_email: str | None = Field(default=None, max_length=200)
    anonymous: bool = True


class WhistleblowerStatusIn(BaseModel):
    status: str = Field(..., pattern="^(EINGEGANGEN|IN_PRUEFUNG|MASSNAHME|GESCHLOSSEN)$")
    note: str | None = Field(default=None, max_length=1000)


class LksgRiskAssessmentIn(BaseModel):
    supplier_id: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=2, max_length=2)
    spend_eur: float = Field(..., ge=0)
    sector_risk: int = Field(..., ge=0, le=5)
    human_rights_flags: int = Field(default=0, ge=0, le=5)
    environmental_flags: int = Field(default=0, ge=0, le=5)
    mitigation_note: str | None = Field(default=None, max_length=1000)

