"""Pydantic schemas for the stuecklisten domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class StuecklistenPositionCreate(BaseModel):
    pos_nr: int
    komponente_nr: str
    komponente_bez: Optional[str] = None
    menge: Decimal = Field(..., gt=0)
    einheit: Optional[str] = None
    anteil_prozent: Optional[Decimal] = Field(None, ge=0, le=100)
    optional: bool = False


class StuecklisteCreate(BaseModel):
    stueckliste_nr: str = Field(..., max_length=30)
    artikel_nr: str
    bezeichnung: Optional[str] = None
    menge_basis: Decimal = Field(default=Decimal("1"), gt=0)
    einheit: str = Field(default="Stk", max_length=10)
    variable_komp: bool = False
    positionen: list[StuecklistenPositionCreate] = []

    @model_validator(mode="after")
    def check_pos_nummern(self) -> "StuecklisteCreate":
        nummern = [p.pos_nr for p in self.positionen]
        if len(nummern) != len(set(nummern)):
            raise ValueError("Positionsnummern müssen eindeutig sein.")
        return self


class StuecklistenPositionOut(BaseModel):
    id: str
    pos_nr: int
    komponente_nr: str
    komponente_bez: Optional[str]
    menge: Decimal
    einheit: Optional[str]
    anteil_prozent: Optional[Decimal]
    optional: bool


class StuecklisteOut(BaseModel):
    id: str
    stueckliste_nr: str
    artikel_nr: str
    bezeichnung: Optional[str]
    menge_basis: Decimal
    einheit: str
    variable_komp: bool
    aktiv: bool
    created_at: datetime
    positionen: list[StuecklistenPositionOut] = []

