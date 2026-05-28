"""Pydantic schemas for the charges domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ChargeOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class ChargeCreate(BaseModel):
    artikel_id: str = Field(..., description="Article ID")
    artikel: str = Field(..., description="Article name")
    chargen_id: str = Field(..., description="Batch number")
    menge: float = Field(..., gt=0, description="Quantity in tons")
    lagerort: str = Field(..., description="Storage location")
    eingang: str = Field(..., description="Receipt date ISO format")
    herstellungsdatum: Optional[str] = Field(default=None, description="Production date ISO format")
    mhd: Optional[str] = Field(default=None, description="Best-before date ISO format")
    losnummer: Optional[str] = None
    produktbezeichnung: Optional[str] = None
    rueckverfolgbar_bis_stunden: int = Field(default=4, ge=1, le=24)
    herkunft: Optional[str] = None
    qualitaetsstatus: str = Field(default=ChargeStatus.IN_PRUEFUNG.value)
    bemerkungen: Optional[str] = None
    rohstoffe: Optional[list[dict]] = None
    lieferant_info: Optional[dict] = None
    kunden_info: Optional[dict] = None
    produktionsprozess: Optional[dict] = None
    digitales_mischbuch: Optional[dict] = None
    haccp_system: Optional[dict] = None
    eigenkontrollen: Optional[list[dict]] = None
    warentrennung_qs_nicht_qs: bool = False
    krisenmanagement: Optional[dict] = None
    futtermittelmonitoring: Optional[dict] = None
    qualitaetspersonal: Optional[dict] = None
    qs_datenbank: Optional[dict] = None


class ChargeUpdate(BaseModel):
    menge: Optional[float] = None
    lagerort: Optional[str] = None
    qualitaetsstatus: Optional[str] = None
    freigabe_datum: Optional[str] = None
    bemerkungen: Optional[str] = None
    status: Optional[str] = None
    herstellungsdatum: Optional[str] = None
    mhd: Optional[str] = None
    losnummer: Optional[str] = None
    produktbezeichnung: Optional[str] = None
    rueckverfolgbar_bis_stunden: Optional[int] = Field(default=None, ge=1, le=24)
    rohstoffe: Optional[list[dict]] = None
    lieferant_info: Optional[dict] = None
    kunden_info: Optional[dict] = None
    produktionsprozess: Optional[dict] = None
    digitales_mischbuch: Optional[dict] = None
    haccp_system: Optional[dict] = None
    eigenkontrollen: Optional[list[dict]] = None
    warentrennung_qs_nicht_qs: Optional[bool] = None
    krisenmanagement: Optional[dict] = None
    futtermittelmonitoring: Optional[dict] = None
    qualitaetspersonal: Optional[dict] = None
    qs_datenbank: Optional[dict] = None

