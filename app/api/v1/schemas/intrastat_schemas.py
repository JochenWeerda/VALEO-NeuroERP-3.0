"""Auto-generated domain schemas for intrastat.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class IntrastatOut(BaseSchema):
    """Response schema for intrastat endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class IntrastatMeldungCreate(BaseModel):
    meldezeitraum: str = Field(..., description="YYYY-MM, z. B. 2026-04")
    meldungsart: str = Field(..., description="EINGANG | VERSENDUNG")
    cn8_warennummer: str = Field(..., min_length=8, max_length=8, description="8-stellige Kombinierte Nomenklatur")
    ursprungsland: str = Field(..., min_length=2, max_length=2)
    bestimmungsland: str = Field(..., min_length=2, max_length=2)
    statistischer_wert_eur: float = Field(..., gt=0)
    nettomasse_kg: float = Field(..., ge=0)
    menge: float = Field(..., gt=0)
    mengeneinheit: str = Field(..., max_length=10)
    geschaeftsvorgang_code: int = Field(
        ..., description="11=Kauf/Verkauf, 12=Lohnarbeit, 21=Rückware, …"
    )


class IntrastatMeldungOut(BaseModel):
    id: str
    meldenummer: str
    meldezeitraum: str
    meldungsart: str
    cn8_warennummer: str
    ursprungsland: str
    bestimmungsland: str
    statistischer_wert_eur: float
    nettomasse_kg: float
    menge: float
    mengeneinheit: str
    geschaeftsvorgang_code: int
    status: str  # ENTWURF | GEMELDET | KORRIGIERT


class IntrastatMeldungUpdate(BaseModel):
    cn8_warennummer: Optional[str] = Field(None, min_length=8, max_length=8)
    ursprungsland: Optional[str] = Field(None, min_length=2, max_length=2)
    bestimmungsland: Optional[str] = Field(None, min_length=2, max_length=2)
    statistischer_wert_eur: Optional[float] = None
    nettomasse_kg: Optional[float] = None
    menge: Optional[float] = None
    mengeneinheit: Optional[str] = None
    geschaeftsvorgang_code: Optional[int] = None
    status: Optional[str] = None

