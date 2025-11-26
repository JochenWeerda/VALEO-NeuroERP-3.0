"""
Pydantic Schemas für den Verkauf / Kundenstamm
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class KundeBase(BaseModel):
    """Grundschema für Kunden"""

    kunden_nr: str = Field(..., max_length=20)
    name1: str = Field(..., max_length=100)
    name2: Optional[str] = Field(None, max_length=100)
    name3: Optional[str] = Field(None, max_length=100)
    strasse: Optional[str] = Field(None, max_length=100)
    plz: Optional[str] = Field(None, max_length=10)
    ort: Optional[str] = Field(None, max_length=100)
    land: Optional[str] = Field(None, max_length=100)
    tel: Optional[str] = Field(None, max_length=50)
    fax: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    homepage: Optional[str] = Field(None, max_length=200)


class KundeCreate(KundeBase):
    """Schema für Kunde-Erstellung"""

    pass


class KundeUpdate(BaseModel):
    """Schema für Kunde-Änderungen"""

    name1: Optional[str] = None
    name2: Optional[str] = None
    name3: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    tel: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[EmailStr] = None
    homepage: Optional[str] = None


class KundeResponse(KundeBase):
    """Antwortschema für Kunden"""

    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None
    geloescht: bool = False

    class Config:
        from_attributes = True


class KundenAnsprechpartnerBase(BaseModel):
    """Basis für Ansprechpartner"""

    vorname: Optional[str] = Field(None, max_length=100)
    nachname: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    abteilung: Optional[str] = Field(None, max_length=100)
    telefon1: Optional[str] = Field(None, max_length=50)
    telefon2: Optional[str] = Field(None, max_length=50)
    mobil: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    empfanger_rechnung_email: bool = False
    empfanger_mahnung_email: bool = False
    kontaktart: Optional[str] = None


class KundenAnsprechpartnerCreate(KundenAnsprechpartnerBase):
    kunden_nr: str


class KundenAnsprechpartnerResponse(KundenAnsprechpartnerBase):
    id: int
    kunden_nr: str
    erstanlage: Optional[date] = None
    datenschutzbeauftragter: bool = False

    class Config:
        from_attributes = True


class KundenProfilBase(BaseModel):
    firmenname: Optional[str] = Field(None, max_length=200)
    gruendung: Optional[date] = None
    jahresumsatz: Optional[float] = None
    berufsgenossenschaft: Optional[str] = Field(None, max_length=100)
    berufsgen_nr: Optional[str] = Field(None, max_length=50)
    branche: Optional[str] = Field(None, max_length=100)
    mitbewerber: Optional[str] = Field(None, max_length=200)
    engpaesse: Optional[str] = None
    organisationsstruktur: Optional[str] = None
    mitarbeiteranzahl: Optional[int] = None
    wettbewerbsdifferenzierung: Optional[str] = None
    betriebsrat: bool = False
    unternehmensphilosophie: Optional[str] = None


class KundenProfilCreate(KundenProfilBase):
    kunden_nr: str


class KundenProfilResponse(KundenProfilBase):
    kunden_nr: str
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenVersandResponse(BaseModel):
    kunden_nr: str
    versandart_rechnung: Optional[str] = None
    versandart_mahnung: Optional[str] = None
    versandart_kontakt: Optional[str] = None
    dispo_nummer: Optional[str] = None
    initialisierungsweisung: Optional[str] = None
    versandmedium: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenLieferungZahlungResponse(BaseModel):
    kunden_nr: str
    lieferbedingung: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    faelligkeit_ab: Optional[str] = None
    pro_forma_rechnung: bool = False
    pro_forma_rabatt1: Optional[float] = None
    pro_forma_rabatt2: Optional[float] = None
    einzel_sammelversand_avis: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenDatenschutzResponse(BaseModel):
    kunden_nr: str
    einwilligung: bool = False
    anlagedatum: Optional[date] = None
    anlagebearbeiter: Optional[str] = None
    zusatzbemerkung: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenGenossenschaftResponse(BaseModel):
    kunden_nr: str
    geschaeftsguthaben_konto: Optional[str] = None
    mitgliedschaft_gekuendigt: bool = False
    kuendigungsgrund: Optional[str] = None
    datum_kuendigung: Optional[date] = None
    datum_austritt: Optional[date] = None
    mitgliedsnummer: Optional[str] = None
    pflichtanteile: Optional[int] = None
    eintrittsdatum: Optional[date] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenFreitextResponse(BaseModel):
    kunden_nr: str
    chef_anweisung: Optional[str] = None
    langtext: Optional[str] = None
    bemerkungen: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenAllgemeinErweitertResponse(BaseModel):
    kunden_nr: str
    staat: Optional[str] = None
    bundesland: Optional[str] = None
    kunde_seit: Optional[date] = None
    debitoren_konto: Optional[str] = None
    deb_kto_hauptkonto: Optional[str] = None
    disponent: Optional[str] = None
    vertriebsbeauftragter: Optional[str] = None
    abc_umsatzstatus: Optional[str] = None
    betriebsnummer: Optional[str] = None
    ust_id_nr: Optional[str] = None
    steuernummer: Optional[str] = None
    sperrgrund: Optional[str] = None
    kundengruppe: Optional[str] = None
    fax_sperre: bool = False
    infofeld4: Optional[str] = None
    infofeld5: Optional[str] = None
    infofeld6: Optional[str] = None
    erstellt_am: Optional[datetime] = None
    geaendert_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenEmailVerteilerResponse(BaseModel):
    id: int
    kunden_nr: str
    verteilername: Optional[str] = None
    bezeichnung: Optional[str] = None
    email: Optional[EmailStr] = None
    erstellt_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenBetriebsgemeinschaftResponse(BaseModel):
    id: int
    kunden_nr: str
    verbundnummer: Optional[str] = None
    mitglieder_kunden_nr: Optional[str] = None
    anteil_prozent: Optional[float] = None
    erstellt_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenCpdKontoResponse(BaseModel):
    id: int
    kunden_nr: str
    debitoren_konto: Optional[str] = None
    suchbegriff: Optional[str] = None
    rechnungsadresse: Optional[str] = None
    geschaeftsstelle: Optional[str] = None
    kostenstelle: Optional[str] = None
    rechnungsart: Optional[str] = None
    sammelrechnung: bool = False
    rechnungsformular: Optional[str] = None
    vb: Optional[str] = None
    gebiet: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    erstellt_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenRabatteDetailResponse(BaseModel):
    id: int
    kunden_nr: str
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    rabatt: Optional[float] = None
    rabatt_gueltig_bis: Optional[date] = None
    rabatt_liste_id: Optional[int] = None
    erstellt_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenPreiseDetailResponse(BaseModel):
    id: int
    kunden_nr: str
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    preis_netto: Optional[float] = None
    preis_inkl_fracht: Optional[float] = None
    preis_einheit: Optional[str] = None
    rabatt_erlaubt: bool = True
    sonderfracht: Optional[float] = None
    zahlungsbedingung: Optional[str] = None
    gueltig_bis: Optional[date] = None
    bediener: Optional[str] = None
    erstellt_am: Optional[datetime] = None

    class Config:
        from_attributes = True


class KundenStammAggregatedResponse(BaseModel):
    """Aggregierter Kundenstamm (alle Tabellen)"""

    kunde: KundeResponse
    profil: Optional[KundenProfilResponse] = None
    versand: Optional[KundenVersandResponse] = None
    lieferung_zahlung: Optional[KundenLieferungZahlungResponse] = None
    datenschutz: Optional[KundenDatenschutzResponse] = None
    genossenschaft: Optional[KundenGenossenschaftResponse] = None
    freitext: Optional[KundenFreitextResponse] = None
    allgemein_erweitert: Optional[KundenAllgemeinErweitertResponse] = None
    ansprechpartner: List[KundenAnsprechpartnerResponse] = Field(default_factory=list)
    email_verteiler: List[KundenEmailVerteilerResponse] = Field(default_factory=list)
    betriebs_gemeinschaften: List[KundenBetriebsgemeinschaftResponse] = Field(default_factory=list)
    cpd_konten: List[KundenCpdKontoResponse] = Field(default_factory=list)
    rabatte_detail: List[KundenRabatteDetailResponse] = Field(default_factory=list)
    preise_detail: List[KundenPreiseDetailResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
