"""Auto-generated domain schemas for neuro consent.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class NeuroConsentOut(BaseSchema):
    """Response schema for neuro consent endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class ConsentCheckRequest(BaseModel):
    entity_id: str
    consent_type: str


class ConsentGrantRequest(BaseModel):
    entity_id: str
    consent_type: str
    purpose: str = Field("", description="Zweckbindung")


class ConsentRevokeRequest(BaseModel):
    entity_id: str
    consent_type: str

