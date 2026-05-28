"""Auto-generated domain schemas for silo operations api.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class SiloOperationsApiOut(BaseSchema):
    """Response schema for silo operations api endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SiloZelleCreateRequest(BaseModel):
    tenant_id: str
    bezeichnung: str
    kapazitaet_t: float


class EinlagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    sorte: str
    beleg_nr: Optional[str] = None


class AuslagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    beleg_nr: Optional[str] = None

