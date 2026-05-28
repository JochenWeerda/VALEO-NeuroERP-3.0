"""Auto-generated domain schemas for artikel stamm ext.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ArtikelStammExtOut(BaseSchema):
    """Response schema for artikel stamm ext endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class FolgeartikelCreate(BaseModel):
    artikel_nr: str
    folge_artikel_nr: str
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    grund: Optional[str] = Field(None, description="Auslauf, Sortimentswechsel, Umbenennung")
    automatisch_ersetzen: bool = False


class FolgeartikelOut(BaseModel):
    id: str
    artikel_nr: str
    folge_artikel_nr: str
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    grund: Optional[str]
    automatisch_ersetzen: bool
    aktiv: bool
    created_at: datetime


class InventurgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    inventur_zyklus: Optional[str] = Field(None,
        description="jaehrlich, halbjaehrlich, quartalsweise, rollierend")
    naechste_inventur: Optional[date] = None


class InventurgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    inventur_zyklus: Optional[str]
    naechste_inventur: Optional[date]
    aktiv: bool
    created_at: datetime


class WiegungsgruppeCreate(BaseModel):
    typ: str = Field(..., description="gerafft oder aufgeteilt")
    wiegeschein_ids: list[str] = Field(default_factory=list)
    kontrakt_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class WiegungsgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    typ: str
    wiegeschein_ids: Optional[list]
    gesamt_netto_kg: Optional[Decimal]
    kontrakt_nr: Optional[str]
    beleg_nr: Optional[str]
    status: str
    bemerkung: Optional[str]
    created_at: datetime

