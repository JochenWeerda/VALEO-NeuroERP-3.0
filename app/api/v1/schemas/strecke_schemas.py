from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.api.v1.schemas.base import BaseSchema

class StreckengeschaeftUpdate(BaseModel):
    datum: Optional[str] = None
    niederlassung: Optional[str] = None
    partie_nr: Optional[str] = None
    kostenstelle: Optional[str] = None
    lagerhalle: Optional[str] = None
    nls_nr: Optional[str] = None
    erledigt: Optional[bool] = None
    lieferant_name: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kontrakt_nr: Optional[str] = None
    artikel: Optional[str] = None
    netto: Optional[float] = None
    mwst: Optional[float] = None
    brutto: Optional[float] = None
    rechnungsnr: Optional[str] = None
    bediener: Optional[str] = None
    notiz: Optional[str] = None

