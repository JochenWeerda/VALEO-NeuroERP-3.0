"""Auto-generated domain schemas for atlas zollausfuhr.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AtlasZollausfuhrOut(BaseSchema):
    """Response schema for atlas zollausfuhr endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class ZollausfuhrAnmeldungCreate(BaseModel):
    referenz_nr: str
    ausfuhrland_code: str = "DE"
    bestimmungsland_code: str
    anmelder_eori: str
    waren_positionen: list[WarenPosition]
    befoerderungsart: int = 30  # 10=See/20=Schiene/30=Strasse/40=Luft/50=Post
    ausfuehrender_nr: str
    ausfuhrdatum: str
    lieferbedingung: str


class ZollausfuhrAnmeldungOut(ZollausfuhrAnmeldungCreate):
    id: str
    status: str = "ENTWURF"  # ENTWURF/UEBERMITTELT/BEWILLIGT/ABGELEHNT/ERLEDIGT
    atlas_mrn: Optional[str] = None
    erstellt_am: str


class ZollausfuhrStatusUpdate(BaseModel):
    mrn: str
    neuer_status: str
    atlas_meldung: Optional[str] = None

