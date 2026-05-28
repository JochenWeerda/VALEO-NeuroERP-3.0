"""Auto-generated domain schemas for customer extensions.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class CustomerExtensionsOut(BaseSchema):
    """Response schema for customer extensions endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class GeoSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50.0


class ConvertLeadRequest(BaseModel):
    lead_id: str


class OperatorStatusUpdate(BaseModel):
    contact_id: str
    status: str  # "gelesen" | "erledigt"

