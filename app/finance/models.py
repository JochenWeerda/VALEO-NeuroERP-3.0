"""
Finance Models
SQLAlchemy models for finance operations, E-Invoicing, and advanced features
"""

import enum
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Numeric, Date, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


# ============================================================================
# VAT TAX CODES - Germany/EU
# ============================================================================

class VatCodeCategory(str, enum.Enum):
    """VAT code categories"""
    DE_INLAND = "DE_INLAND"           # Domestic German
    DE_AGR_PAUSCHAL = "DE_AGR_PAUSCHAL"  # Agricultural §24
    DE_FORST = "DE_FORST"             # Forestry §24
    EU_IGL = "EU_IGL"                 # Intra-community delivery
    EU_ERWERB = "EU_ERWERB"           # Intra-community acquisition
    EU_OSS = "EU_OSS"                 # OSS B2C
    EXPORT = "EXPORT"                 # Export (third country)
    EXEMPT = "EXEMPT"                 # Exempt


class VatCode(Base):
    """VAT Tax Codes - configurable with audit trail"""
    
    __tablename__ = "vat_codes"
    
    # Primary key
    id = Column(String(50), primary_key=True)  # e.g., "DE_19", "DE_AGR_24_78"
    
    # Core fields
    name = Column(String(200), nullable=False)
    name_long = Column(String(500), nullable=True)
    category = Column(SQLEnum(VatCodeCategory), nullable=False)
    
    # Tax rate (percentage)
    rate = Column(Float, nullable=False)  # 19.0, 7.0, 7.8, 5.5, 0.0
    
    # German tax account (SKR03/SKR04)
    skr03_account = Column(String(10), nullable=True)
    skr04_account = Column(String(10), nullable=True)
    
    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Legal reference
    legal_basis = Column(String(200), nullable=True)
    legal_note = Column(Text, nullable=True)
    
    # Classification
    is_standard = Column(Boolean, default=False)
    is_reduced = Column(Boolean, default=False)
    is_zero = Column(Boolean, default=False)
    is_reverse_charge = Column(Boolean, default=False)
    
    # For agricultural Pauschalierung
    is_agricultural = Column(Boolean, default=False)
    paragraph_24 = Column(Boolean, default=False)
    
    # Tenant scoping
    tenant_id = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class VatCodeAudit(Base):
    """Audit trail for VAT code changes"""
    
    __tablename__ = "vat_codes_audit"
    
    id = Column(String(50), primary_key=True)
    vat_code_id = Column(String(50), nullable=False)
    
    # Change tracking
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    change_type = Column(String(50), nullable=True)
    
    # Old/new values (stored as JSON)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Who changed
    changed_by = Column(String(100), nullable=False)
    changed_at = Column(DateTime, default=func.now())
    
    # Reason for change
    reason = Column(Text, nullable=True)
    legal_reference = Column(String(200), nullable=True)
    
    # Tenant
    tenant_id = Column(String(50), nullable=True)


# Default VAT codes for Germany (seed data)
DEFAULT_VAT_CODES = [
    # Domestic standard
    {"id": "DE_19", "name": "USt 19%", "name_long": "Umsatzsteuer 19% Regelsteuersatz", 
     "category": VatCodeCategory.DE_INLAND, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 12 Abs. 1 UStG", "is_standard": True, "is_active": True},
    
    # Domestic reduced
    {"id": "DE_7", "name": "USt 7%", "name_long": "Umsatzsteuer 7% ermäßigter Steuersatz",
     "category": VatCodeCategory.DE_INLAND, "rate": 7.0, "skr03_account": "1771", "skr04_account": "1771",
     "legal_basis": "§ 12 Abs. 2 UStG Anlage 2", "is_reduced": True, "is_active": True},
    
    # Agricultural §24 - Durchschnittssatz
    {"id": "DE_AGR_24_78", "name": "Durchschnittssatz 7,8%", "name_long": "Landwirtschaftlicher Durchschnittssatz §24 UStG",
     "category": VatCodeCategory.DE_AGR_PAUSCHAL, "rate": 7.8, "skr03_account": "1773", "skr04_account": "1773",
     "legal_basis": "§ 24 Nr. 1 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # Forestry §24
    {"id": "DE_FORST_24_55", "name": "Forstwirtschaft 5,5%", "name_long": "Forstwirtschaftlicher Durchschnittssatz §24 Nr. 2 UStG",
     "category": VatCodeCategory.DE_FORST, "rate": 5.5, "skr03_account": "1774", "skr04_account": "1774",
     "legal_basis": "§ 24 Nr. 2 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # §24 certain deliveries
    {"id": "DE_AGR_24_19", "name": "§24 Lieferungen 19%", "name_long": "Bestimmte Lieferungen nach §24 UStG",
     "category": VatCodeCategory.DE_AGR_PAUSCHAL, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 24 Nr. 3 UStG", "is_agricultural": True, "paragraph_24": True, "is_active": True},
    
    # Zero rated
    {"id": "DE_0", "name": "0% USt", "name_long": "Steuerfreie Lieferung (0%)",
     "category": VatCodeCategory.EXEMPT, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 4 UStG", "is_zero": True, "is_active": True},
    
    # EU Intra-community delivery (0% - B2B)
    {"id": "EU_IGL_0", "name": "IG Lieferung 0%", "name_long": "Innergemeinschaftliche Lieferung §6a UStG",
     "category": VatCodeCategory.EU_IGL, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 6a UStG", "is_zero": True, "is_active": True},
    
    # EU Intra-community acquisition (reverse charge)
    {"id": "EU_ACQ_19", "name": "IG Erwerb 19%", "name_long": "Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge)",
     "category": VatCodeCategory.EU_ERWERB, "rate": 19.0, "skr03_account": "1776", "skr04_account": "1776",
     "legal_basis": "§ 1a UStG", "is_reverse_charge": True, "is_active": True},
    
    {"id": "EU_ACQ_7", "name": "IG Erwerb 7%", "name_long": "Innergemeinschaftlicher Erwerb §1a UStG (Reverse Charge) 7%",
     "category": VatCodeCategory.EU_ERWERB, "rate": 7.0, "skr03_account": "1771", "skr04_account": "1771",
     "legal_basis": "§ 1a UStG", "is_reverse_charge": True, "is_active": True},
    
    # Export (third country)
    {"id": "EXPORT_0", "name": "Export 0%", "name_long": "Ausfuhrlieferung §4 Nr. 1a UStG",
     "category": VatCodeCategory.EXPORT, "rate": 0.0, "skr03_account": None, "skr04_account": None,
     "legal_basis": "§ 4 Nr. 1a UStG", "is_zero": True, "is_active": True},
]


# ============================================================================
# WECHSELKURSE & FREMDWÄHRUNG
# ============================================================================

class Wechselkurs(Base):
    """Wechselkurse für Fremdwährungen"""
    __tablename__ = "wechselkurse"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Währungspaar
    waehrung_von = Column(String(3), nullable=False, index=True)  # ISO 4217
    waehrung_nach = Column(String(3), nullable=False, index=True)  # ISO 4217

    # Kurs
    kurs = Column(Float, nullable=False)
    kurs_datum = Column(Date, nullable=False)

    # Metadata
    quelle = Column(String(50), nullable=True)  # EZB, API, MANUELL
    gueltig_von = Column(Date, nullable=True)
    gueltig_bis = Column(Date, nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# BUCHUNGSSCHEMATA
# ============================================================================

class Buchungsschema(Base):
    """Automatisches Buchungsschema"""
    __tablename__ = "buchungsschemata"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Identifikation
    name = Column(String(200), nullable=False)
    beschreibung = Column(Text, nullable=True)
    belegart = Column(String(10), nullable=False)  # ER, EB, ZE, AB, RE, etc.

    # Konten-Zuordnung (kann Template-Platzhalter enthalten)
    soll_konto_schema = Column(String(50), nullable=False)
    haben_konto_schema = Column(String(50), nullable=False)

    # Steuer-Logik
    steuer_code = Column(String(20), nullable=True)  # VORSTEUER, MWST, KEINE
    steuer_satz = Column(Float, nullable=True)

    # Bedingungen (JSON)
    bedingungen = Column(JSON, nullable=True)

    # Status
    aktiv = Column(Boolean, default=True)
    priorität = Column(Integer, default=100)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# KOSTENRECHNUNG
# ============================================================================

class Kostenstelle(Base):
    """Kostenstellen für Kostenrechnung"""
    __tablename__ = "kostenstellen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Identifikation
    nummer = Column(String(20), nullable=False, index=True)
    bezeichnung = Column(String(200), nullable=False)

    # Hierarchie
    kostenstelle_art = Column(String(50), nullable=False)  # KOSTENSTELLE, KOSTENTRAEGER, PROJEKT, ABTEILUNG
    uebergeordnet = Column(String(36), ForeignKey("kostenstellen.id"), nullable=True)

    # Verantwortung
    verantwortlicher = Column(String(100), nullable=True)

    # Budget
    budget = Column(Float, nullable=True)
    budget_periode = Column(String(20), nullable=True)  # MONAT, QUARTAL, JAHR

    # Status
    aktiv = Column(Boolean, default=True)

    # Relations
    parent = relationship("Kostenstelle", remote_side=[id], backref="children")

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# ABSCHLUSSCHECKLISTEN
# ============================================================================

class AbschlussCheckliste(Base):
    """Monats-/Jahresabschluss Checklisten"""
    __tablename__ = "abschluss_checklisten"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Periode
    periode = Column(String(10), nullable=False, index=True)  # "2026-01" oder "2025"
    abschluss_art = Column(String(20), nullable=False)  # MONATLICH, QUARTALSWEISE, JAHRES

    # Status
    status = Column(String(20), default="OFFEN")  # OFFEN, IN_BEARBEITUNG, ABGESCHLOSSEN

    # Checklisten-Items (JSON)
    items = Column(JSON, nullable=True)

    # Meta
    verantwortlicher = Column(String(100), nullable=True)
    beginn_datum = Column(Date, nullable=True)
    abschluss_datum = Column(Date, nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# NEBENBUCH-ABSTIMMUNG
# ============================================================================

class NebenbuchAbstimmung(Base):
    """Abstimmung Nebenbuch ↔ Hauptbuch"""
    __tablename__ = "nebenbuch_abstimmungen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Abstimmungs-Details
    abstimmungs_datum = Column(Date, nullable=False)
    periode = Column(String(10), nullable=False, index=True)
    buchungskreis = Column(String(10), nullable=False)

    # Status
    status = Column(String(20), default="OFFEN")  # OFFEN, ABGESTIMMT, ABWEICHEND

    # Summen
    nebenbuch_saldo = Column(Float, default=0)
    hauptbuch_saldo = Column(Float, default=0)
    differenz = Column(Float, default=0)

    # Details
    nicht_abgestimmte = Column(JSON, nullable=True)

    # Meta
    abgestimmt_durch = Column(String(100), nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# INTERCOMPANY-BUCHUNGEN
# ============================================================================

class IntercompanyBuchung(Base):
    """Intercompany Buchungen zwischen Gesellschaften"""
    __tablename__ = "intercompany_buchungen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Buchungsnummer
    buchungsnr = Column(String(50), nullable=False, unique=True, index=True)

    # Gesellschaften
    gesellschaft_von = Column(String(10), nullable=False, index=True)  # Company Code
    gesellschaft_nach = Column(String(10), nullable=False, index=True)

    # Buchungsdaten
    belegnr = Column(String(50), nullable=False)
    datum = Column(Date, nullable=False)
    betrag = Column(Float, nullable=False)
    waehrung = Column(String(3), nullable=False)

    # Wechselkurs
    wechselkurs = Column(Float, nullable=True)
    betrag_local = Column(Float, nullable=True)

    # Konten
    konto_von = Column(String(10), nullable=False)
    konto_nach = Column(String(10), nullable=False)

    # Status
    status = Column(String(20), default="ERSTELLT")  # ERSTELLT, ABGESTIMMT, GEBUCHT, STORNIERT
    gegenbuchung_id = Column(String(36), nullable=True)

    # Referenz
    referenz = Column(String(200), nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# ZAHLUNGEN
# ============================================================================

class Zahlungslauf(Base):
    __tablename__ = "zahlungslauf_kreditoren"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True)

    # Grunddaten
    lauf_nummer = Column(String, unique=True, index=True)
    ausfuehrungs_datum = Column(String)  # ISO date string
    gesamt_betrag = Column(Float)
    anzahl_zahlungen = Column(Integer)
    status = Column(String)  # entwurf, freigegeben, ausgefuehrt, storniert

    # Freigabe/Ausführung
    freigegeben_am = Column(DateTime, nullable=True)
    freigegeben_durch = Column(String, nullable=True)
    ausgefuehrt_am = Column(DateTime, nullable=True)

    # SEPA-Auftraggeber
    auftraggeber_name = Column(String)
    auftraggeber_iban = Column(String)
    auftraggeber_bic = Column(String)

    # Zahlungen (als JSON gespeichert)
    zahlungen = Column(JSON)  # Array of payment objects

    # Meta
    notizen = Column(Text, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# BUCHHALTUNG (BESTEHEND)
# ============================================================================

class OffenerPosten(Base):
    """Offene Posten (Debitoren/Kreditoren)"""
    __tablename__ = "offene_posten"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Beleg-Info
    rechnungsnr = Column(String(50), nullable=False, index=True)
    datum = Column(Date, nullable=False)
    faelligkeit = Column(Date, nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    offen = Column(Numeric(10, 2), nullable=False)

    # Partner-Info
    kunde_id = Column(String(36), nullable=True)
    kunde_name = Column(String(100), nullable=True)
    lieferant_id = Column(String(36), nullable=True)
    lieferant_name = Column(String(100), nullable=True)

    # Mahnung/Skonto
    skonto_prozent = Column(Numeric(5, 2), nullable=True)
    skonto_bis = Column(Date, nullable=True)
    mahn_stufe = Column(Integer, default=0)
    zahlbar = Column(Boolean, default=True)

    # Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Buchung(Base):
    """Buchungsjournal"""
    __tablename__ = "buchungen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Beleg-Info
    belegnr = Column(String(50), nullable=False, index=True)
    datum = Column(Date, nullable=False)
    soll_konto = Column(String(10), nullable=False)
    haben_konto = Column(String(10), nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    text = Column(String(200), nullable=False)
    belegart = Column(String(10), nullable=False)  # ER, EB, ZE, etc.

    # Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Konto(Base):
    """Kontenplan"""
    __tablename__ = "konten"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Konto-Info
    kontonummer = Column(String(10), nullable=False, unique=True, index=True)
    bezeichnung = Column(String(100), nullable=False)
    kontoart = Column(String(50), nullable=False)  # Aktiv, Passiv, Aufwand, Ertrag
    typ = Column(String(20), nullable=False)  # aktiv, passiv, aufwand, ertrag
    saldo = Column(Numeric(10, 2), default=0)

    # Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Anlage(Base):
    """Anlagevermögen"""
    __tablename__ = "anlagen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Anlage-Info
    anlagennr = Column(String(20), nullable=False, unique=True, index=True)
    bezeichnung = Column(String(200), nullable=False)
    anschaffung = Column(Date, nullable=False)
    anschaffungswert = Column(Numeric(10, 2), nullable=False)
    nutzungsdauer = Column(Integer, nullable=False)  # Jahre
    afa_satz = Column(Numeric(5, 2), nullable=False)  # Prozent
    kumulierte_afa = Column(Numeric(10, 2), default=0)
    buchwert = Column(Numeric(10, 2), nullable=False)

    # Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


# ============================================================================
# GOBD COMPLIANCE - VERFAHRENSDOKUMENTATION
# ============================================================================

class ProcedureDoc(Base):
    """GoBD Verfahrensdokumentation"""
    __tablename__ = "gobd_verfahrensdokumentation"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Identifikation
    title = Column(String(200), nullable=False)
    version = Column(String(20), nullable=False)
    status = Column(String(20), default="DRAFT")  # DRAFT, RELEASED, ARCHIVED
    
    # Inhalt (GoBD-konforme Struktur)
    scope = Column(Text, nullable=True)  # Haupt-/Vor-/Nebensysteme
    anwenderbeschreibung = Column(JSON, nullable=True)  # Benutzerhandbuch
    technische_beschreibung = Column(JSON, nullable=True)  # Technische Doku
    betriebsanleitung = Column(JSON, nullable=True)  # Betriebshandbuch
    pruefwege = Column(JSON, nullable=True)  # Prüfpfade
    
    # System-Info
    software_name = Column(String(100), nullable=True)
    software_version = Column(String(50), nullable=True)
    datenbank = Column(String(100), nullable=True)
    betriebssystem = Column(String(100), nullable=True)
    
    # Freigabe
    released_by = Column(String(100), nullable=True)
    released_at = Column(DateTime, nullable=True)
    
    # Meta
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# ============================================================================
# GOBD COMPLIANCE - AUFBEWAHRUNGSFRISTEN
# ============================================================================

class RetentionPolicy(Base):
    """Aufbewahrungsrichtlinien"""
    __tablename__ = "gobd_aufbewahrungsrichtlinien"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Dokumenttyp
    dokument_typ = Column(String(100), nullable=False)  # z.B. Jahresabschluss, Buchungsbeleg
    beschreibung = Column(Text, nullable=True)
    
    # Aufbewahrungsfrist (Jahre) - GoBD §147 AO
    aufbewahrungs_jahre = Column(Integer, nullable=False, default=10)
    
    # Fristbeginn (Trigger)
    frist_trigger = Column(String(50), nullable=True)  # CREATION_DATE, FISCAL_YEAR_END, etc.
    
    # Legal Reference
    gesetzliche_grundlage = Column(String(200), nullable=True)  # §147 AO, §257 HGB, etc.
    
    # Status
    aktiv = Column(Boolean, default=True)
    
    # Meta
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class DocumentHold(Base):
    """Löschsperren / Aufbewahrungshalte"""
    __tablename__ = "gobd_loeschsperren"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Referenz auf Dokument/Beleg
    dokument_id = Column(String(36), nullable=False, index=True)
    dokument_typ = Column(String(50), nullable=False)  # RECHNUNG, BUCHUNG, etc.
    belegnr = Column(String(50), nullable=True)
    
    # Sperrgrund
    sperrgrund = Column(String(200), nullable=False)  # STEUERPRUEFUNG, RECHTSSTREIT, etc.
    beschreibung = Column(Text, nullable=True)
    
    # Sperrdatum
    hold_start_date = Column(Date, nullable=False)
    hold_end_date = Column(Date, nullable=True)  # NULL = unbefristet
    
    # Freigabe
    released_by = Column(String(100), nullable=True)
    released_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="ACTIVE")  # ACTIVE, RELEASED, EXPIRED
    
    # Meta
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# ============================================================================
# E-RECHNUNG (ZUGFeRD / XRechnung)
# ============================================================================

class ERechnung(Base):
    """E-Rechnung für ZUGFeRD/XRechnung Export"""
    __tablename__ = "finance_erechnungen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    # Rechnungsdaten
    rechnungsnummer = Column(String(50), nullable=False, index=True)
    rechnungsdatum = Column(Date, nullable=False)
    leistungsdatum = Column(Date, nullable=True)
    faelligkeitsdatum = Column(Date, nullable=False)

    # Lieferant (Absender)
    lieferant_name = Column(String(200), nullable=False)
    lieferant_adresse = Column(String(500), nullable=True)
    lieferant_ust_id = Column(String(20), nullable=True)
    lieferant_gln = Column(String(20), nullable=True)

    # Rechnungssteller (Empfänger)
    rechnungssteller_name = Column(String(200), nullable=False)
    rechnungssteller_adresse = Column(String(500), nullable=True)
    rechnungssteller_ust_id = Column(String(20), nullable=True)

    # Beträge
    gesamt_netto = Column(Numeric(10, 2), nullable=False)
    gesamt_mwst = Column(Numeric(10, 2), nullable=False)
    gesamt_brutto = Column(Numeric(10, 2), nullable=False)

    # Bezüge
    zugeordneter_auftrag = Column(String(50), nullable=True)
    zugeordneter_lieferschein = Column(String(50), nullable=True)

    # Status
    status = Column(String(20), default="ERSTELLT")  # ERSTELLT, VERSENDET, GEBUCHT

    # XML-Checksum
    checksum_sha256 = Column(String(64), nullable=True)

    # Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
