"""
VALEO-NeuroERP - Einkauf Schemas
Pydantic Schemas für API
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class LieferantBase(BaseModel):
    lieferantennummer: str
    firmenname: str
    ansprechpartner: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: str = "Deutschland"
    zahlungsbedingungen: Optional[str] = None
    lieferzeit_tage: Optional[int] = None
    bewertung: Optional[int] = None
    aktiv: bool = True


class LieferantCreate(LieferantBase):
    pass


class LieferantUpdate(BaseModel):
    firmenname: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    lieferzeit_tage: Optional[int] = None
    bewertung: Optional[int] = None
    aktiv: Optional[bool] = None


class Lieferant(LieferantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BestellungBase(BaseModel):
    bestellnummer: str
    lieferant_id: int
    bestelldatum: date
    gewuenschtes_lieferdatum: Optional[date] = None
    status: str = "entwurf"
    netto_summe: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    brutto_summe: Optional[Decimal] = None
    erstellt_von: Optional[str] = None


class BestellungCreate(BestellungBase):
    pass


class BestellungUpdate(BaseModel):
    lieferant_id: Optional[int] = None
    bestelldatum: Optional[date] = None
    gewuenschtes_lieferdatum: Optional[date] = None
    status: Optional[str] = None
    netto_summe: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    brutto_summe: Optional[Decimal] = None


class Bestellung(BestellungBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

