"""
Finance Models
SQLAlchemy models for finance operations, E-Invoicing, and advanced features
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, Numeric, Date, func
from app.core.database import Base


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
# GOBD COMPLIANCE - AUFBEWAHRUNGSFRISTEN (Operative Tabelle)
# ============================================================================

class AufbewahrungsFristRecord(Base):
    """Operative Aufbewahrungsfristen-Tabelle pro Dokumenttyp und Tenant."""
    __tablename__ = "aufbewahrungsfristen"
    __table_args__ = {"schema": "domain_finance"}

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    dokument_typ = Column(String(100), nullable=False)
    gesetzliche_grundlage = Column(String(100), nullable=True)   # "§147 AO", "§257 HGB"
    aufbewahrungs_jahre = Column(Integer, nullable=False)
    aeltestes_dokument_datum = Column(Date, nullable=True)
    anzahl_dokumente = Column(Integer, default=0)
    ablauf_datum = Column(Date, nullable=True)
    status = Column(String(20), default="AKTIV")  # AKTIV / ABGELAUFEN
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
