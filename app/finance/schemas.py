"""
Finance Schemas
Pydantic schemas for finance operations, E-Invoicing (ZUGFeRD/XRechnung), and advanced features
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date


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
