"""Auto-generated domain schemas for inventory operations.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class InventoryOperationsOut(BaseSchema):
    """Response schema for inventory operations endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class BestandskorrekturIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., description="Korrekturbetrag (positiv=Zugang, negativ=Abgang)")
    grund: str = Field(..., description="Grund-Code: schwund, bruch, mhd_verfall, diebstahl, messdifferenz, qualitaetsmangel, sonstige")
    bemerkung: Optional[str] = Field(None, description="Freitextbemerkung")
    charge: Optional[str] = Field(None, description="Chargen-Nummer (optional)")
    buchungsdatum: Optional[date] = Field(None, description="Buchungsdatum (default: heute)")


class BestandskorrekturOut(BaseModel):
    id: str
    article_id: str
    warehouse_id: str
    menge: float
    grund: str
    grund_text: str
    bemerkung: Optional[str]
    charge: Optional[str]
    buchungsdatum: date
    movement_id: str
    journal_entry_id: Optional[str]
    status: str


class SchwundBuchungIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., gt=0, description="Schwundmenge (positiv)")
    bemerkung: Optional[str] = Field(None)
    charge: Optional[str] = Field(None)
    buchungsdatum: Optional[date] = Field(None)


class MhdAbschreibungIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., gt=0, description="Abzuschreibende Menge")
    charge: str = Field(..., description="Chargen-Nummer der abgelaufenen Ware")
    mhd: date = Field(..., description="Mindesthaltbarkeitsdatum")
    bemerkung: Optional[str] = Field(None)
    buchungsdatum: Optional[date] = Field(None)

