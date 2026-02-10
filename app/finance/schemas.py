"""
Finance Schemas
Pydantic schemas for finance operations
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Zahlung(BaseModel):
    kreditor_id: str
    kreditor_name: str
    iban: str
    bic: str
    betrag: float = Field(gt=0)
    verwendungszweck: str
    skonto_genutzt: bool = False
    skonto_betrag: float = 0.0
    op_referenz: Optional[str] = None


class ZahlungslaufBase(BaseModel):
    lauf_nummer: str
    ausfuehrungs_datum: str  # ISO date string
    gesamt_betrag: float = Field(ge=0)
    anzahl_zahlungen: int = Field(ge=0)
    status: str = Field(pattern="^(entwurf|freigegeben|ausgefuehrt|storniert)$")

    # Freigabe/Ausführung
    freigegeben_am: Optional[str] = None
    freigegeben_durch: Optional[str] = None
    ausgefuehrt_am: Optional[str] = None

    # SEPA-Auftraggeber
    auftraggeber_name: str
    auftraggeber_iban: str = Field(pattern=r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$")
    auftraggeber_bic: str

    # Zahlungen
    zahlungen: List[Zahlung] = Field(min_length=1)

    # Meta
    notizen: Optional[str] = None


class ZahlungslaufCreate(ZahlungslaufBase):
    pass


class ZahlungslaufUpdate(BaseModel):
    lauf_nummer: Optional[str] = None
    ausfuehrungs_datum: Optional[str] = None
    gesamt_betrag: Optional[float] = Field(None, ge=0)
    anzahl_zahlungen: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(entwurf|freigegeben|ausgefuehrt|storniert)$")

    freigegeben_am: Optional[str] = None
    freigegeben_durch: Optional[str] = None
    ausgefuehrt_am: Optional[str] = None

    auftraggeber_name: Optional[str] = None
    auftraggeber_iban: Optional[str] = Field(None, pattern=r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$")
    auftraggeber_bic: Optional[str] = None

    zahlungen: Optional[List[Zahlung]] = None

    notizen: Optional[str] = None


class Zahlungslauf(ZahlungslaufBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True