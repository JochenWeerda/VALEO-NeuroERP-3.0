"""Auto-generated domain schemas for kontrakt mengenzeitraum.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class KontraktMengenzeitraumOut(BaseSchema):
    """Response schema for kontrakt mengenzeitraum endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class MengenzeitraumCreate(BaseModel):
    kontrakt_nr: str
    zeitraum_von: date
    zeitraum_bis: date
    menge_t: Decimal = Field(..., gt=0)
    variante: Optional[str] = Field(None,
        description="z.B. monatl. lin. Abnahme, quartalsweise, flexibel")
    bemerkung: Optional[str] = None


class MengenzeitraumUpdate(BaseModel):
    menge_t: Optional[Decimal] = None
    menge_bereits_geliefert_t: Optional[Decimal] = None
    status: Optional[str] = None
    bemerkung: Optional[str] = None


class MengenzeitraumOut(BaseModel):
    id: str
    kontrakt_nr: str
    zeitraum_von: date
    zeitraum_bis: date
    menge_t: Decimal
    menge_bereits_geliefert_t: Decimal
    menge_restmenge_t: Optional[Decimal]
    variante: Optional[str]
    status: str
    bemerkung: Optional[str]
    created_at: datetime


class ZuAbschlagsGruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    typ: str = Field(..., description="zuschlag oder abschlag")


class ZuAbschlagCreate(BaseModel):
    gruppe_id: str
    kontrakt_nr: Optional[str] = None
    bezeichnung: str
    betrag_eur: Optional[Decimal] = Field(None, description="EUR/t")
    prozent: Optional[Decimal] = None
    einheit: str = "t"
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None


class ZuAbschlagOut(BaseModel):
    id: str
    gruppe_id: str
    kontrakt_nr: Optional[str]
    bezeichnung: str
    betrag_eur: Optional[Decimal]
    prozent: Optional[Decimal]
    einheit: str
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    aktiv: bool
    created_at: datetime

