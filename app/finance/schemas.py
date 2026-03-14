"""
Finance Schemas
Pydantic schemas for finance operations, E-Invoicing (ZUGFeRD/XRechnung), and advanced features
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# WECHSELKURSE & FREMDWÄHRUNG
# ============================================================================

class Wechselkurs(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Wechselkurs für Fremdwährungen"""
    id: str
    tenant_id: str
    waehrung_von: str  # z.B. "USD"
    waehrung_nach: str  # z.B. "EUR"
    kurs: float = Field(..., gt=0)
    kurs_datum: date
    quelle: Optional[str] = None  # z.B. "EZB", "API", "MANUELL"
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    created_at: datetime


class WechselkursCreate(BaseModel):
    """Wechselkurs erstellen"""
    waehrung_von: str = Field(..., min_length=3, max_length=3, description="ISO 4217 Währungscode")
    waehrung_nach: str = Field(..., min_length=3, max_length=3, description="ISO 4217 Währungscode")
    kurs: float = Field(..., gt=0, description="Kurs (1 Einheit Fremdwährung in Heimatwährung)")
    kurs_datum: date
    quelle: Optional[str] = None


class WechselkursResponse(Wechselkurs):
    pass


class Fremdwaehrungsbetrag(BaseModel):
    """Betrag mit Fremdwährung"""
    betrag: float
    waehrung: str = "EUR"
    wechselkurs: Optional[float] = None
    betrag_eur: Optional[float] = None


# ============================================================================
# BUCHUNGSSCHEMATA
# ============================================================================

class Buchungsschema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Automatisches Buchungsschema"""
    id: str
    tenant_id: str
    name: str
    beschreibung: Optional[str] = None
    belegart: str  # ER, EB, ZE, AB, RE, etc.
    
    # Konten-Zuordnung
    soll_konto_schema: str  # Template oder festes Konto
    haben_konto_schema: str
    
    # Steuer-Logik
    steuer_code: Optional[str] = None  # VORSTEUER, VORSTEUER_7, MWST, MWST_7, KEINE
    steuer_satz: Optional[float] = None
    
    # Bedingungen
    bedingungen: Optional[Dict[str, Any]] = None  # JSON für flexible Bedingungen
    
    aktiv: bool = True
    priorität: int = 100
    created_at: datetime
    updated_at: datetime


class BuchungsschemaCreate(BaseModel):
    """Buchungsschema erstellen"""
    name: str = Field(..., min_length=1, max_length=200)
    beschreibung: Optional[str] = None
    belegart: str = Field(..., pattern="^(ER|EB|ZE|AB|RE|GE|AZ|KZ|BA|ST)$")
    soll_konto_schema: str
    haben_konto_schema: str
    steuer_code: Optional[str] = None
    steuer_satz: Optional[float] = Field(None, ge=0, le=100)
    bedingungen: Optional[Dict[str, Any]] = None
    aktiv: bool = True
    priorität: int = 100


class BuchungsschemaResponse(Buchungsschema):
    pass


class Buchungsvorschlag(BaseModel):
    """Automatischer Buchungsvorschlag"""
    belegnr: str
    datum: date
    text: str
    betrag: float
    waehrung: str = "EUR"
    wechselkurs: Optional[float] = None
    soll_konto: str
    haben_konto: str
    steuer_code: Optional[str] = None
    steuer_betrag: Optional[float] = None
    konfidenz: float = Field(..., ge=0, le=1)  # Wie sicher ist die Zuordnung


# ============================================================================
# KOSTENRECHNUNG
# ============================================================================

class Kostenstelle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Kostenstelle"""
    id: str
    tenant_id: str
    nummer: str
    bezeichnung: str
    kostenstelle_art: str  # KOSTENSTELLE, KOSTENTRAEGER, PROJEKT, ABTEILUNG
    uebergeordnet: Optional[str] = None  # Parent Kostenstelle
    verantwortlicher: Optional[str] = None
    budget: Optional[float] = None
    budget_periode: Optional[str] = None  # MONAT, QUARTAL, JAHR
    aktiv: bool = True
    created_at: datetime
    updated_at: datetime


class KostenstelleCreate(BaseModel):
    """Kostenstelle erstellen"""
    nummer: str = Field(..., min_length=1, max_length=20)
    bezeichnung: str = Field(..., min_length=1, max_length=200)
    kostenstelle_art: str = Field(..., pattern="^(KOSTENSTELLE|KOSTENTRAEGER|PROJEKT|ABTEILUNG)$")
    uebergeordnet: Optional[str] = None
    verantwortlicher: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    budget_periode: Optional[str] = Field(None, pattern="^(MONAT|QUARTAL|JAHR)$")
    aktiv: bool = True


class KostenstelleResponse(Kostenstelle):
    pass


class KostentraegerReport(BaseModel):
    """Kostenträger-Auswertung"""
    kostentraeger_id: str
    kostentraeger_nummer: str
    kostentraeger_bezeichnung: str
    periode_von: date
    periode_bis: date
    
    # Summen
    gesamt_aufwand: float = 0
    gesamt_ertrag: float = 0
    saldo: float = 0
    
    # Details
    positionen: List[Dict[str, Any]] = []
    
    # Kalkulation
    deckungsbeitrag: Optional[float] = None


class KostenstellenReport(BaseModel):
    """Kostenstellen-Bericht"""
    periode_von: date
    periode_bis: date
    gesamt_budget: float = 0
    gesamt_verbraucht: float = 0
    gesamt_offen: float = 0
    
    kostenstellen: List[Kostenstelle] = []
    auswertungen: List[Dict[str, Any]] = []


# ============================================================================
# ABSCHLUSSCHECKLISTEN
# ============================================================================

class AbschlussCheckliste(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Monats-/Jahresabschluss Checkliste"""
    id: str
    tenant_id: str
    periode: str  # "2026-01" oder "2025"
    abschluss_art: str  # MONATLICH, QUARTALSWEISE, JAHRES
    status: str = "OFFEN"  # OFFEN, IN_BEARBEITUNG, ABGESCHLOSSEN
    
    # Checklisten-Items
    items: List[Dict[str, Any]] = []  # JSON mit {name, status, bearbeiter, datum, bemerkung}
    
    # Meta
    verantwortlicher: Optional[str] = None
    beginn_datum: Optional[date] = None
    abschluss_datum: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class AbschlussChecklisteCreate(BaseModel):
    """Checkliste erstellen"""
    periode: str = Field(..., pattern="^\\d{4}(-\\d{2})?$")
    abschluss_art: str = Field(..., pattern="^(MONATLICH|QUARTALSWEISE|JAHRES)$")
    items: List[Dict[str, Any]] = []
    verantwortlicher: Optional[str] = None


class AbschlussChecklisteUpdate(BaseModel):
    """Checkliste aktualisieren"""
    status: Optional[str] = Field(None, pattern="^(OFFEN|IN_BEARBEITUNG|ABGESCHLOSSEN)$")
    items: Optional[List[Dict[str, Any]]] = None
    verantwortlicher: Optional[str] = None
    beginn_datum: Optional[date] = None
    abschluss_datum: Optional[date] = None


class AbschlussChecklisteResponse(AbschlussCheckliste):
    pass


class ChecklistenItemUpdate(BaseModel):
    """Einzelnes Item in Checkliste aktualisieren"""
    item_id: str
    status: str  # OFFEN, ERLEDIGT, PROBLEM
    bearbeiter: Optional[str] = None
    bemerkung: Optional[str] = None


# ============================================================================
# NEBENBUCH-ABSTIMMUNG
# ============================================================================

class NebenbuchAbstimmung(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Abstimmung Nebenbuch ↔ Hauptbuch"""
    id: str
    tenant_id: str
    abstimmungs_datum: date
    periode: str
    
    # Buchungskreis
    buchungskreis: str
    
    # Status
    status: str = "OFFEN"  # OFFEN, ABGESTIMMT, ABWEICHEND
    
    # Summen
    nebenbuch_saldo: float
    hauptbuch_saldo: float
    differenz: float
    
    # Details
    nicht_abgestimmte: List[Dict[str, Any]] = []
    
    # Meta
    abgestimmt_durch: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class NebenbuchAbstimmungCreate(BaseModel):
    """Abstimmung erstellen"""
    abstimmungs_datum: date
    buchungskreis: str


class NebenbuchAbstimmungResponse(NebenbuchAbstimmung):
    pass


class DebitorenAbstimmung(BaseModel):
    """Debitoren-Nebenbuch Abstimmung"""
    kunde_id: str
    kunde_name: str
    offene_posten_summe: float
    saldierungen: float = 0
    bereinigter_saldo: float
    hauptbuch_saldo: float
    differenz: float
    status: str


class KreditorenAbstimmung(BaseModel):
    """Kreditoren-Nebenbuch Abstimmung"""
    lieferant_id: str
    lieferant_name: str
    offene_posten_summe: float
    saldierungen: float = 0
    bereinigter_saldo: float
    hauptbuch_saldo: float
    differenz: float
    status: str


# ============================================================================
# INTERCOMPANY-BUCHUNGEN
# ============================================================================

class IntercompanyBuchung(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Intercompany Buchung zwischen Gesellschaften"""
    id: str
    tenant_id: str
    buchungsnr: str
    
    # Gesellschaften
    gesellschaft_von: str  # Company Code
    gesellschaft_nach: str
    
    # Buchungsdaten
    belegnr: str
    datum: date
    betrag: float
    waehrung: str
    
    # Wechselkurs
    wechselkurs: Optional[float] = None
    betrag_local: Optional[float] = None
    
    # Konten
    konto_von: str
    konto_nach: str
    
    # Status
    status: str = "ERSTELLT"  # ERSTELLT, ABGESTIMMT, GEBUCHT, STORNIERT
    gegenbuchung_id: Optional[str] = None
    
    # Meta
    referenz: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class IntercompanyBuchungCreate(BaseModel):
    """Intercompany Buchung erstellen"""
    gesellschaft_von: str
    gesellschaft_nach: str
    belegnr: str
    datum: date
    betrag: float
    waehrung: str = "EUR"
    wechselkurs: Optional[float] = None
    konto_von: str
    konto_nach: str
    referenz: Optional[str] = None


class IntercompanyBuchungResponse(IntercompanyBuchung):
    pass


class IntercompanySaldo(BaseModel):
    """Intercompany Salden"""
    gesellschaft: str
    partner_gesellschaft: str
    waehrung: str
    saldo: float
    faelligkeiten: List[Dict[str, Any]] = []


# ============================================================================
# ZAHLUNGEN
# ============================================================================

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


# ============================================================================
# ZAHLUNGSLÄUFE
# ============================================================================

class ZahlungslaufBase(BaseModel):
    lauf_nummer: str
    ausfuehrungs_datum: str  # ISO date string
    gesamt_betrag: float = Field(ge=0)
    anzahl_zahlungen: int = Field(ge=0)
    status: str = Field(pattern="^(entwurf|freigegeben|ausgefuehrt|storniert)$")

    freigegeben_am: Optional[str] = None
    freigegeben_durch: Optional[str] = None
    ausgefuehrt_am: Optional[str] = None

    auftraggeber_name: str
    auftraggeber_iban: str = Field(pattern=r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$")
    auftraggeber_bic: str

    zahlungen: List[Zahlung] = Field(min_length=1)

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
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


# ============================================================================
# E-RECHNUNG (ZUGFeRD / XRechnung) - EN 16931
# ============================================================================

class ERechnungAdresse(BaseModel):
    """Lieferant oder Rechnungsempfänger Adresse"""
    name: str
    straße: Optional[str] = None
    postleitzahl: Optional[str] = None
    ort: Optional[str] = None
    land: str = "DE"
    gln: Optional[str] = None  # Global Location Number
    ust_id: Optional[str] = None  # Umsatzsteuer-ID


class ERechnungBankverbindung(BaseModel):
    """Bankverbindung für Zahlung"""
    iban: str
    bic: Optional[str] = None
    bank_name: Optional[str] = None


class ERechnungPosition(BaseModel):
    """Einzelne Rechnungsposition"""
    position_nr: int
    artikelnummer: Optional[str] = None
    beschreibung: str
    menge: float
    einheit: str = "C62"  # UN/ECE Rec 20 - Einheiten
    einzelpreis: float
    rabatt_prozent: float = 0.0
    steuersatz: float  # 0, 7, 19, etc.
    steuerkategorie: str = "S"  # S = Standard rate
    gesamtpreis_netto: float


class ERechnungBase(BaseModel):
    """Grunddaten für E-Rechnung"""
    rechnungsnummer: str
    rechnungsdatum: date
    leistungsdatum: Optional[date] = None
    faelligkeitsdatum: date

    # Absender (Lieferant)
    lieferant: ERechnungAdresse
    lieferant_bank: Optional[ERechnungBankverbindung] = None

    # Empfänger (Rechnungssteller)
    rechnungssteller: ERechnungAdresse
    rechnungssteller_bank: Optional[ERechnungBankverbindung] = None

    # Positions
    positionen: List[ERechnungPosition]

    # Summen
    gesamt_netto: float
    gesamt_mwst: float
    gesamt_brutto: float

    # Zahlungsbedingungen
    zahlungsbedingungen: Optional[str] = " sofort fällig"
    skonto_prozent: Optional[float] = None
    skonto_tage: Optional[int] = None

    # Notizen
    bemerkungen: Optional[str] = None


class ERechnungCreate(ERechnungBase):
    """Erstellung einer E-Rechnung"""
    zugeordneter_auftrag: Optional[str] = None
    zugeordneter_lieferschein: Optional[str] = None


class ERechnungResponse(ERechnungBase):
    model_config = ConfigDict(from_attributes=True)

    """E-Rechnung mit generierten Metadaten"""
    id: str
    created_at: datetime
    zugeordneter_auftrag: Optional[str] = None
    zugeordneter_lieferschein: Optional[str] = None


class ZUGFeRDExportResponse(BaseModel):
    """ZUGFeRD XML Export"""
    id: str
    rechnungsnummer: str
    format: str = "ZUGFeRD 2.3.1"  # Aktuelle Version
    xml_content: str
    xml_length: int
    checksum_sha256: str
    generated_at: datetime


class XRechnungExportResponse(BaseModel):
    """XRechnung XML Export (EN 16931)"""
    id: str
    rechnungsnummer: str
    format: str = "XRechnung"
    xml_content: str
    xml_length: int
    checksum_sha256: str
    generated_at: datetime
