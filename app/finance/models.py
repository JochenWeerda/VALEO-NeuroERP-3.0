"""
Finance Models
SQLAlchemy models for finance operations
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Zahlungslauf(Base):
    __tablename__ = "zahlungslauf_kreditoren"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True)

    ***REMOVED*** Grunddaten
    lauf_nummer = Column(String, unique=True, index=True)
    ausfuehrungs_datum = Column(String)  ***REMOVED*** ISO date string
    gesamt_betrag = Column(Float)
    anzahl_zahlungen = Column(Integer)
    status = Column(String)  ***REMOVED*** entwurf, freigegeben, ausgefuehrt, storniert

    ***REMOVED*** Freigabe/Ausführung
    freigegeben_am = Column(DateTime, nullable=True)
    freigegeben_durch = Column(String, nullable=True)
    ausgefuehrt_am = Column(DateTime, nullable=True)

    ***REMOVED*** SEPA-Auftraggeber
    auftraggeber_name = Column(String)
    auftraggeber_iban = Column(String)
    auftraggeber_bic = Column(String)

    ***REMOVED*** Zahlungen (als JSON gespeichert)
    zahlungen = Column(JSON)  ***REMOVED*** Array of payment objects

    ***REMOVED*** Meta
    notizen = Column(Text, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class OffenerPosten(Base):
    """Offene Posten (Debitoren/Kreditoren)"""
    __tablename__ = "offene_posten"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    ***REMOVED*** Beleg-Info
    rechnungsnr = Column(String(50), nullable=False, index=True)
    datum = Column(Date, nullable=False)
    faelligkeit = Column(Date, nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    offen = Column(Numeric(10, 2), nullable=False)

    ***REMOVED*** Partner-Info
    kunde_id = Column(String(36), nullable=True)
    kunde_name = Column(String(100), nullable=True)
    lieferant_id = Column(String(36), nullable=True)
    lieferant_name = Column(String(100), nullable=True)

    ***REMOVED*** Mahnung/Skonto
    skonto_prozent = Column(Numeric(5, 2), nullable=True)
    skonto_bis = Column(Date, nullable=True)
    mahn_stufe = Column(Integer, default=0)
    zahlbar = Column(Boolean, default=True)

    ***REMOVED*** Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Buchung(Base):
    """Buchungsjournal"""
    __tablename__ = "buchungen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    ***REMOVED*** Beleg-Info
    belegnr = Column(String(50), nullable=False, index=True)
    datum = Column(Date, nullable=False)
    soll_konto = Column(String(10), nullable=False)
    haben_konto = Column(String(10), nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    text = Column(String(200), nullable=False)
    belegart = Column(String(10), nullable=False)  ***REMOVED*** ER, EB, ZE, etc.

    ***REMOVED*** Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Konto(Base):
    """Kontenplan"""
    __tablename__ = "konten"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    ***REMOVED*** Konto-Info
    kontonummer = Column(String(10), nullable=False, unique=True, index=True)
    bezeichnung = Column(String(100), nullable=False)
    kontoart = Column(String(50), nullable=False)  ***REMOVED*** Aktiv, Passiv, Aufwand, Ertrag
    typ = Column(String(20), nullable=False)  ***REMOVED*** aktiv, passiv, aufwand, ertrag
    saldo = Column(Numeric(10, 2), default=0)

    ***REMOVED*** Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Anlage(Base):
    """Anlagevermögen"""
    __tablename__ = "anlagen"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)

    ***REMOVED*** Anlage-Info
    anlagennr = Column(String(20), nullable=False, unique=True, index=True)
    bezeichnung = Column(String(200), nullable=False)
    anschaffung = Column(Date, nullable=False)
    anschaffungswert = Column(Numeric(10, 2), nullable=False)
    nutzungsdauer = Column(Integer, nullable=False)  ***REMOVED*** Jahre
    afa_satz = Column(Numeric(5, 2), nullable=False)  ***REMOVED*** Prozent
    kumulierte_afa = Column(Numeric(10, 2), default=0)
    buchwert = Column(Numeric(10, 2), nullable=False)

    ***REMOVED*** Meta
    created_at = Column(DateTime)
    updated_at = Column(DateTime)