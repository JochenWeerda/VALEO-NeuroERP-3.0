"""
VALEO-NeuroERP - Einkauf Models
SQLAlchemy Models für Einkauf
"""

from sqlalchemy import Column, Integer, String, Numeric, Date, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Lieferant(Base):
    """Lieferanten-Stammdaten"""
    __tablename__ = "einkauf_lieferanten"
    
    id = Column(Integer, primary_key=True, index=True)
    lieferantennummer = Column(String(50), unique=True, nullable=False, index=True)
    firmenname = Column(String(255), nullable=False, index=True)
    ansprechpartner = Column(String(255))
    email = Column(String(255))
    telefon = Column(String(50))
    strasse = Column(String(255))
    plz = Column(String(20))
    ort = Column(String(100))
    land = Column(String(100), default="Deutschland")
    zahlungsbedingungen = Column(Text)
    lieferzeit_tage = Column(Integer)
    bewertung = Column(Integer)  # 1-5
    aktiv = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Bestellung(Base):
    """Bestellungen"""
    __tablename__ = "einkauf_bestellungen"
    
    id = Column(Integer, primary_key=True, index=True)
    bestellnummer = Column(String(50), unique=True, nullable=False, index=True)
    lieferant_id = Column(Integer, ForeignKey("einkauf_lieferanten.id"))
    bestelldatum = Column(Date, nullable=False)
    gewuenschtes_lieferdatum = Column(Date)
    status = Column(String(50), default="entwurf", index=True)  # entwurf, bestellt, geliefert, storniert
    netto_summe = Column(Numeric(12, 2))
    mwst_betrag = Column(Numeric(12, 2))
    brutto_summe = Column(Numeric(12, 2))
    erstellt_von = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

