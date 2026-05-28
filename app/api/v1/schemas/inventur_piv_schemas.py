"""Auto-generated domain schemas for inventur piv.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class InventurPivOut(BaseSchema):
    """Response schema for inventur piv endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class PIVAbschlussCreate(BaseModel):
    abschluss_datum: date
    inventurgruppe_nr: Optional[str] = None
    lager_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class PIVPositionCreate(BaseModel):
    artikel_nr: str
    lagerplatz: Optional[str] = None
    buchbestand: Decimal
    bewertungspreis_eur: Optional[Decimal] = None


class PIVAbschlussOut(BaseModel):
    id: str
    abschluss_datum: date
    inventurgruppe_nr: Optional[str]
    lager_nr: Optional[str]
    status: str
    erfasst_von: Optional[str]
    abgeschlossen_von: Optional[str]
    abgeschlossen_am: Optional[datetime]
    anzahl_positionen: int
    differenzwert_eur: Optional[Decimal]
    bemerkung: Optional[str]
    created_at: datetime


class PIVPositionOut(BaseModel):
    id: str
    abschluss_id: str
    artikel_nr: str
    lagerplatz: Optional[str]
    buchbestand: Decimal
    zaehlmenge: Optional[Decimal]
    differenz: Optional[Decimal]
    bewertungspreis_eur: Optional[Decimal]
    differenzwert_eur: Optional[Decimal]
    erfasst: bool
    ignoriert: bool
    created_at: datetime

