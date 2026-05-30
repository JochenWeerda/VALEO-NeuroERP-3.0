from __future__ import annotations

from typing import Any, List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.api.v1.schemas.base import BaseSchema

class StuecklistenPositionCreate(BaseModel):
    pos_nr: int
    komponente_nr: str
    komponente_bez: Optional[str] = None
    menge: Decimal = Field(..., gt=0)
    einheit: Optional[str] = None
    anteil_prozent: Optional[Decimal] = Field(None, ge=0, le=100)
    optional: bool = False


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

