"""Pydantic schemas for the vertreterprovisionen domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ProvisionsGruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = "vk"
    provisionstyp: str = "fix"
    provisionssatz: Optional[Decimal] = Field(None, ge=0, le=100)

    def model_post_init(self, __context):
        if self.richtung not in GUELTIGE_RICHTUNG:
            raise ValueError(f"Ungültige Richtung: {self.richtung}")
        if self.provisionstyp not in GUELTIGE_PROVISIONSTYPEN:
            raise ValueError(f"Ungültiger Provisionstyp: {self.provisionstyp}")
        if self.provisionstyp == "fix" and self.provisionssatz is None:
            raise ValueError("provisionssatz erforderlich bei provisionstyp='fix'.")


class ProvisionsGruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    richtung: str
    provisionstyp: str
    provisionssatz: Optional[Decimal]
    aktiv: bool
    created_at: datetime


class ProvisionsStaffelZeileCreate(BaseModel):
    zeile_nr: int = Field(..., ge=1)
    ab_wert: Decimal
    provisionssatz: Decimal = Field(..., ge=0, le=100)


class ProvisionsStaffelCreate(BaseModel):
    gruppe_id: str
    vertreterklasse: Optional[str] = None
    zeilen: list[ProvisionsStaffelZeileCreate] = Field(default_factory=list)


class ProvisionsStaffelZeileOut(BaseModel):
    id: str
    staffel_id: str
    zeile_nr: int
    ab_wert: Decimal
    provisionssatz: Decimal


class ProvisionsStaffelOut(BaseModel):
    id: str
    gruppe_id: str
    vertreterklasse: Optional[str]
    zeilen: list[ProvisionsStaffelZeileOut]
    created_at: datetime

