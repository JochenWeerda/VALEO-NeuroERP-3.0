"""Auto-generated domain schemas for partiestamm."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class PartiestammOut(BaseSchema):
    """Response schema for partiestamm endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class PartiegruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str


class PartiegruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime


class PartiestammCreate(BaseModel):
    partie_nr: Optional[str] = Field(None, max_length=30)
    bezeichnung: Optional[str] = None
    artikel_nr: str
    lager_nr: Optional[str] = None
    partie_typ: str = "artikelstamm"
    gruppe_id: Optional[str] = None
    erntejahr: Optional[int] = Field(None, ge=1900, le=2100)
    herkunftsland: Optional[str] = Field(None, max_length=3)

    @model_validator(mode="after")
    def check_typ(self):
        if self.partie_typ not in GUELTIGE_TYP:
            raise ValueError(f"Ungültiger partie_typ: {self.partie_typ}. Erlaubt: {GUELTIGE_TYP}")
        if self.partie_typ == "artikel_lager" and not self.lager_nr:
            raise ValueError("lager_nr erforderlich bei partie_typ='artikel_lager'.")
        return self


class PartieUmbuchungCreate(BaseModel):
    ziel_lager_nr: str
    menge: Optional[float] = None
    bemerkung: Optional[str] = None

