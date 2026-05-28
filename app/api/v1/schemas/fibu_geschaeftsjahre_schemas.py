"""Auto-generated domain schemas for fibu geschaeftsjahre.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class FibuGeschaeftsjahreOut(BaseSchema):
    """Response schema for fibu geschaeftsjahre endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class GeschaeftsjahreCreate(BaseModel):
    jahr_nr: int = Field(..., ge=1990, le=2100)
    bezeichnung: str
    datum_beginn: date
    datum_ende: date
    kleinstes_datum: Optional[date] = None
    groesstes_datum: Optional[date] = None
    warndatum_von: Optional[date] = None
    warndatum_bis: Optional[date] = None
    anzahl_perioden_ware: int = Field(default=12, ge=1, le=14)
    anzahl_perioden_fibu: int = Field(default=12, ge=1, le=14)
    journal_nummernkreis: Optional[str] = None

    @model_validator(mode="after")
    def validate_datum(self) -> "GeschaeftsjahreCreate":
        if self.datum_ende <= self.datum_beginn:
            raise ValueError("datum_ende muss nach datum_beginn liegen.")
        return self


class GeschaeftsjahreOut(BaseModel):
    id: str
    jahr_nr: int
    bezeichnung: str
    datum_beginn: date
    datum_ende: date
    kleinstes_datum: Optional[date]
    groesstes_datum: Optional[date]
    warndatum_von: Optional[date]
    warndatum_bis: Optional[date]
    anzahl_perioden_ware: int
    anzahl_perioden_fibu: int
    journal_nummernkreis: Optional[str]
    status: str
    created_at: datetime


class FibuPeriodeOut(BaseModel):
    id: str
    jahr_nr: int
    periode_nr: int
    bezeichnung: Optional[str]
    datum_von: date
    datum_bis: date
    typ: str
    gesperrt: bool
    created_at: datetime


class PeriodischeBuchungCreate(BaseModel):
    bezeichnung: str
    soll_konto: str = Field(..., max_length=20)
    haben_konto: str = Field(..., max_length=20)
    betrag_eur: Decimal = Field(..., gt=0)
    buchungstext: Optional[str] = None
    intervall: str = Field(..., description="monatlich, quartalsweise, halbjaehrlich, jaehrlich")
    naechste_buchung: Optional[date] = None
    buchung_bis: Optional[date] = None
    alle_belege_erzeugen: bool = False

    def model_post_init(self, __context):
        if self.intervall not in INTERVALLE:
            raise ValueError(f"intervall muss eines von {INTERVALLE} sein.")


class PeriodischeBuchungOut(BaseModel):
    id: str
    bezeichnung: str
    soll_konto: str
    haben_konto: str
    betrag_eur: Decimal
    buchungstext: Optional[str]
    intervall: str
    naechste_buchung: Optional[date]
    buchung_bis: Optional[date]
    alle_belege_erzeugen: bool
    anzahl_erzeugte_belege: int
    letzter_beleg_datum: Optional[date]
    aktiv: bool
    created_at: datetime

