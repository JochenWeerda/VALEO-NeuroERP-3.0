"""Auto-generated domain schemas for massebilanz.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class MassebilanzOut(BaseSchema):
    """Response schema for massebilanz endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class MassebilanzCreate(BaseModel):
    periode: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM")
    artikel_nr: Optional[str] = None
    lager_nr: Optional[str] = None
    anfangsbestand_kg: Decimal = Field(default=Decimal("0"))
    bemerkung: Optional[str] = None


class BewegungCreate(BaseModel):
    massebilanz_id: str
    beleg_nr: Optional[str] = None
    beleg_typ: Optional[str] = Field(None, description="lieferschein, abschlag, finale, storno")
    buchungsdatum: date
    menge_kg: Decimal
    vorzeichen: str = Field(default="+", pattern=r"^[+-]$")
    kontrakt_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class BewegungOut(BaseModel):
    id: str
    massebilanz_id: str
    beleg_nr: Optional[str]
    beleg_typ: Optional[str]
    buchungsdatum: date
    menge_kg: Decimal
    vorzeichen: str
    kontrakt_nr: Optional[str]
    lieferant_nr: Optional[str]
    storniert: bool
    created_at: datetime

