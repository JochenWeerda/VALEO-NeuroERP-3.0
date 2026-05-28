"""Pydantic schemas for the fuhrpark domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class FuhrparkOut(BaseSchema):
    """Typed response schema for FuhrparkOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class FuhrparkFahrzeugPayload(BaseModel):
    ro_nummer: Optional[str] = None
    is_neu: bool = False
    betrieb: Optional[str] = None
    bereich: Optional[str] = None
    pol_kennzeichen: Optional[str] = None
    kennzeichen: str = Field(..., min_length=2, max_length=20)
    typ: str = Field(..., min_length=2, max_length=50)
    marke: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    verwendung: Optional[str] = None
    kfz_brief_nummer: Optional[str] = None
    schadstoffgruppe: Optional[str] = None
    leistung_kw: Optional[float] = None
    kraftstoff: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    erstzulassung: Optional[datetime] = None
    ausstattung: Optional[str] = None
    fahrtenschreiber_vorhanden: bool = False
    ahk_vorhanden: bool = False
    ladekran_vorhanden: bool = False
    fahrer_name: Optional[str] = None
    fahrer_vorname: Optional[str] = None
    kilometerstand: float = 0
    km_stand_alle_eintraege: bool = False
    bestellnummer: Optional[str] = None
    bestelldatum: Optional[datetime] = None
    haendler: Optional[str] = None
    zustand: Optional[str] = "neu"
    kaufsumme_eur: Optional[float] = None
    kaufdatum: Optional[datetime] = None
    verkaufsdatum: Optional[datetime] = None
    abmeldedatum: Optional[datetime] = None
    kostenstelle: Optional[str] = None
    abschreibungsart: Optional[str] = None
    afa_jahre: Optional[int] = None
    afa_eur_jaehrlich: Optional[float] = None
    afa_eur_monatlich: Optional[float] = None
    leasingdauer_monate: Optional[int] = None
    leasinggesellschaft: Optional[str] = None
    leasingrate_eur: Optional[float] = None
    kfz_steuer_eur: Optional[float] = None
    kfz_steuernummer: Optional[str] = None
    kontierung: Optional[str] = None
    finanzamt: Optional[str] = None
    versicherungs_gesellschaft: Optional[str] = None
    versicherungsschein_nr: Optional[str] = None
    versicherung_satz_eur_monat: Optional[float] = None
    versicherung_haftpflicht: bool = False
    versicherung_kasko: bool = False
    naechster_tuev_termin: Optional[datetime] = None
    naechster_asu_termin: Optional[datetime] = None
    naechste_inspektion: Optional[datetime] = None
    leergewicht_kg: Optional[float] = None
    nutzlast_kg: Optional[float] = None
    gesamtgewicht_kg: Optional[float] = None
    anhaengerlast_kg: Optional[float] = None
    winterreifen_vorhanden: bool = False
    winterreifen_eingelagert: bool = False
    handy_freisprecheinrichtung: bool = False
    handy_fabrikat: Optional[str] = None
    handy_rufnummer: Optional[str] = None
    status: Optional[str] = "verfuegbar"


class DruckerSetupPayload(BaseModel):
    drucker_name: str = Field(..., min_length=2, max_length=255)


class UnfallAnzeigePayload(BaseModel):
    datum: datetime
    ort: str = Field(..., min_length=2, max_length=255)
    beschreibung: str = Field(..., min_length=3)


class FuhrparkTerminartPayload(BaseModel):
    terminart: str = Field(..., min_length=2, max_length=120)
    intervall_monate: int = Field(0, ge=0, le=1200)
    intervall_km: int = Field(0, ge=0, le=2_000_000)


class FuhrparkRechnungPayload(BaseModel):
    rechnungs_nr: str = Field(..., min_length=3, max_length=80)
    datum: datetime
    fahrzeug_id: Optional[str] = None
    fahrzeug_kennzeichen: Optional[str] = None
    sachkonto: Optional[str] = None
    kostenart: Optional[str] = None
    betrag_eur: float = Field(..., ge=0)
    notiz: Optional[str] = None


class FuhrparkAusgehendesDokumentPayload(BaseModel):
    beleg_typ: str = Field(..., min_length=2, max_length=120)
    formular: Optional[str] = Field(default=None, max_length=80)
    ziel_modul: Optional[str] = Field(default=None, max_length=255)
    beschreibung: Optional[str] = None
    aktiv: bool = True
    letzter_druck: Optional[datetime] = None

