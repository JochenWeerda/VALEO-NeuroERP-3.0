"""
Finance Models
SQLAlchemy models for finance operations, E-Invoicing, and advanced features
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
