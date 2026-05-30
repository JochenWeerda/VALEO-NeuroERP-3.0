from __future__ import annotations

from typing import Any, List, Optional
from datetime import date
from pydantic import ConfigDict as _ConfigDict, BaseModel, ConfigDict, Field
from app.api.v1.schemas.base import BaseSchema


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

