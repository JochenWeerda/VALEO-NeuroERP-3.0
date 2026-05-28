"""Auto-generated domain schemas for compliance dsgvo.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ComplianceDsgvoOut(BaseSchema):
    """Response schema for compliance dsgvo endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class ErasureRequestIn(BaseModel):
    requester_name: str = Field(..., max_length=200)
    requester_email: str = Field(..., max_length=200)
    subject_id: str = Field(..., description="ID des betroffenen Datensatzes")
    subject_type: str = Field(..., description="CUSTOMER/EMPLOYEE/LEAD")


class ErasureProcessIn(BaseModel):
    deletion_notes: str | None = None


class ErasureRejectIn(BaseModel):
    reason: str = Field(..., max_length=1000, description="z.B. gesetzliche Aufbewahrungspflicht")

