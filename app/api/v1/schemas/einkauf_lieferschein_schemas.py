"""Pydantic schemas for the einkauf lieferschein domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class LieferscheinPositionCreate(LieferscheinPositionBase):
    pass


class LieferscheinCreate(LieferscheinBase):
    positionen: list[LieferscheinPositionCreate] = []


class LieferscheinUpdate(BaseModel):
    lieferschein_datum: Optional[date] = None
    niederlassung: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    texte: Optional[str] = None
    zwischenhaendler: Optional[str] = None
    wie_vom_ls: Optional[bool] = None
    lieferanten_stamm: Optional[str] = None
    liefer_termin: Optional[date] = None
    lieferdatum: Optional[date] = None
    liefer_nr: Optional[str] = None
    bediener: Optional[str] = None
    erledigt: Optional[bool] = None
    verfuegbarer_bestand: Optional[Decimal] = None
    summe_gewicht: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    netto_betrag: Optional[Decimal] = None
    brutto_betrag: Optional[Decimal] = None


class FrachtauftragCreate(FrachtauftragBase):
    pass


class FrachtauftragUpdate(BaseModel):
    frachtauftrag_erzeugt: Optional[datetime] = None
    niederlassung: Optional[str] = None
    liefertermin: Optional[date] = None
    spediteur_nr: Optional[str] = None
    spediteur_name: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    belegnummer: Optional[str] = None
    lade_datum: Optional[date] = None
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    debitoren_filter: Optional[str] = None

