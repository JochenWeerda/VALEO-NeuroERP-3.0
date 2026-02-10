"""
Agrar Domain Models
Models for Saatgut, Dünger, PSM, and other agricultural products
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


# Saatgut Models
class Saatgut(Base):
    """Saatgut-Stammdaten"""
    __tablename__ = "agrar_saatgut"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artikelnummer = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    sorte = Column(String(100), nullable=False)
    art = Column(String(50), nullable=False)  # Weizen, Gerste, etc.
    zuechter = Column(String(100), nullable=True)
    zulassungsnummer = Column(String(50), nullable=True)
    bsa_zulassung = Column(Boolean, default=False)
    eu_zulassung = Column(Boolean, default=False)
    ablauf_zulassung = Column(DateTime(timezone=True), nullable=True)

    # Agronomische Daten
    tkm = Column(DECIMAL(8, 2), nullable=True)  # Tausendkornmasse
    keimfaehigkeit = Column(DECIMAL(5, 2), nullable=True)  # in %
    aussaatstaerke = Column(DECIMAL(8, 2), nullable=True)  # kg/ha

    # Preise und Konditionen
    ek_preis = Column(DECIMAL(8, 2), nullable=True)
    vk_preis = Column(DECIMAL(8, 2), nullable=True)
    waehrung = Column(String(3), default="EUR")
    mindestabnahme = Column(DECIMAL(8, 2), nullable=True)

    # Lager und Verfügbarkeit
    lagerbestand = Column(DECIMAL(10, 2), default=0)
    reserviert = Column(DECIMAL(10, 2), default=0)
    verfuegbar = Column(DECIMAL(10, 2), default=0)
    lagerort = Column(String(100), nullable=True)

    # Status und Meta
    ist_aktiv = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SaatgutLizenz(Base):
    """Saatgut-Lizenzen und Gebühren"""
    __tablename__ = "agrar_saatgut_lizenzen"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    saatgut_id = Column(String, ForeignKey("domain_agrar.agrar_saatgut.id"), nullable=False)
    typ = Column(String(50), nullable=False)  # Nachbaugebühr, Z-Saatgut, etc.
    saison = Column(String(9), nullable=False)  # 2024/2025
    gebuehr_pro_tonne = Column(DECIMAL(8, 2), nullable=True)
    gesamt_gebuehr = Column(DECIMAL(10, 2), nullable=True)
    bezahlt = Column(Boolean, default=False)
    bezahlt_am = Column(DateTime(timezone=True), nullable=True)

    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Dünger Models
class Duenger(Base):
    """Dünger-Stammdaten"""
    __tablename__ = "agrar_duenger"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artikelnummer = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    typ = Column(String(50), nullable=False)  # Mineraldünger, Organisch, etc.
    hersteller = Column(String(100), nullable=True)

    # Inhaltsstoffe (NPK)
    n_gehalt = Column(DECIMAL(5, 2), nullable=True)  # Stickstoff %
    p_gehalt = Column(DECIMAL(5, 2), nullable=True)  # Phosphor %
    k_gehalt = Column(DECIMAL(5, 2), nullable=True)  # Kalium %
    s_gehalt = Column(DECIMAL(5, 2), nullable=True)  # Schwefel %
    mg_gehalt = Column(DECIMAL(5, 2), nullable=True)  # Magnesium %

    # Zulassungen
    dmv_nummer = Column(String(50), nullable=True)
    eu_zulassung = Column(String(50), nullable=True)
    ablauf_zulassung = Column(DateTime(timezone=True), nullable=True)

    # Sicherheit
    gefahrstoff_klasse = Column(String(10), nullable=True)
    wassergefaehrdend = Column(Boolean, default=False)
    lagerklasse = Column(String(10), nullable=True)

    # Erklärung des Landwirts (für Ausgangsstoffe für Explosivstoffe)
    ausgangsstoff_explosivstoffe = Column(Boolean, default=False)
    erklaerung_landwirt_erforderlich = Column(Boolean, default=False)
    erklaerung_landwirt_status = Column(String(20), nullable=True)  # eingegangen, geprueft, abgelehnt

    # Anwendung
    kultur_typ = Column(String(100), nullable=True)  # Getreide, Raps, etc.
    dosierung_min = Column(DECIMAL(6, 2), nullable=True)  # kg/ha
    dosierung_max = Column(DECIMAL(6, 2), nullable=True)  # kg/ha
    zeitpunkt = Column(String(100), nullable=True)  # Herbstanwendung, etc.

    # Preise und Lager
    ek_preis = Column(DECIMAL(8, 2), nullable=True)
    vk_preis = Column(DECIMAL(8, 2), nullable=True)
    waehrung = Column(String(3), default="EUR")
    lagerbestand = Column(DECIMAL(10, 2), default=0)

    # Status und Meta
    ist_aktiv = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DuengerMischung(Base):
    """Dünger-Mischungen und Rezepte"""
    __tablename__ = "agrar_duenger_mischungen"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    beschreibung = Column(Text, nullable=True)

    # Rezeptur als JSON
    komponenten = Column(JSONB, nullable=True)  # [{"duenger_id": "...", "anteil": 30.5}, ...]

    # Berechnete Werte
    gesamt_n = Column(DECIMAL(5, 2), nullable=True)
    gesamt_p = Column(DECIMAL(5, 2), nullable=True)
    gesamt_k = Column(DECIMAL(5, 2), nullable=True)
    kosten_pro_tonne = Column(DECIMAL(8, 2), nullable=True)

    # Status
    ist_aktiv = Column(Boolean, default=True)
    freigegeben = Column(Boolean, default=False)
    freigegeben_am = Column(DateTime(timezone=True), nullable=True)
    freigegeben_durch = Column(String, nullable=True)

    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# PSM Models
class PSM(Base):
    """Pflanzenschutzmittel-Stammdaten"""
    __tablename__ = "agrar_psm"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artikelnummer = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    wirkstoff = Column(String(100), nullable=False)
    mittel_typ = Column(String(50), nullable=False)  # Herbizid, Fungizid, etc.

    # Zulassung
    bvl_nummer = Column(String(50), nullable=False)
    zulassung_ablauf = Column(DateTime(timezone=True), nullable=False)
    eu_zulassung = Column(Boolean, default=False)

    # Anwendung
    kulturen = Column(JSONB, nullable=True)  # ["Weizen", "Gerste", ...]
    indikationen = Column(JSONB, nullable=True)  # ["Mehltau", "Braunrost", ...]
    dosierung_min = Column(DECIMAL(6, 2), nullable=True)  # l/ha oder kg/ha
    dosierung_max = Column(DECIMAL(6, 2), nullable=True)
    wartezeit = Column(Integer, nullable=True)  # Tage bis Ernte

    # Sicherheit und Auflagen
    bienenschutz = Column(Boolean, default=False)
    wasserschutz_gebiet = Column(Boolean, default=False)
    abstand_wohngebaeude = Column(Integer, nullable=True)  # Meter
    abstand_gewaesser = Column(Integer, nullable=True)  # Meter

    # Auflagen (NT, NW, B, etc.)
    auflagen = Column(JSONB, nullable=True)  # ["NT", "NW", "B", ...]

    # Erklärung des Landwirts (für Ausgangsstoffe für Explosivstoffe)
    ausgangsstoff_explosivstoffe = Column(Boolean, default=False)
    erklaerung_landwirt_erforderlich = Column(Boolean, default=False)
    erklaerung_landwirt_status = Column(String(20), nullable=True)  # eingegangen, geprueft, abgelehnt

    # Resistenz-Management
    wirkstoff_gruppe = Column(String(50), nullable=True)
    rotations_empfehlung = Column(Text, nullable=True)

    # Preise und Lager
    ek_preis = Column(DECIMAL(8, 2), nullable=True)
    vk_preis = Column(DECIMAL(8, 2), nullable=True)
    waehrung = Column(String(3), default="EUR")
    lagerbestand = Column(DECIMAL(10, 2), default=0)

    # Status und Meta
    ist_aktiv = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Sachkunde(Base):
    """Sachkunde-Nachweise für PSM"""
    __tablename__ = "agrar_sachkunde"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String, nullable=False)  # Verknüpfung zu CRM/Contact
    sachkunde_typ = Column(String(50), nullable=False)  # PSM, Dünger, etc.
    zertifikat_nummer = Column(String(50), nullable=True)
    ausgestellt_am = Column(DateTime(timezone=True), nullable=False)
    gueltig_bis = Column(DateTime(timezone=True), nullable=False)
    aussteller = Column(String(100), nullable=True)

    # Status
    ist_gueltig = Column(Boolean, default=True)
    erinnerung_versendet = Column(Boolean, default=False)

    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Biostimulanzien & Sonstiges
class Biostimulanz(Base):
    """Biostimulanzien und Sonstige Agrarprodukte"""
    __tablename__ = "agrar_biostimulanzien"
    __table_args__ = {"schema": "domain_agrar", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artikelnummer = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    typ = Column(String(50), nullable=False)  # Biostimulanz, Kalk, Substrat, etc.
    hersteller = Column(String(100), nullable=True)

    # Spezifische Eigenschaften je Typ
    zusammensetzung = Column(JSONB, nullable=True)
    anwendungsbereich = Column(JSONB, nullable=True)  # ["Blatt", "Boden", "Saatgut"]
    dosierung = Column(String(100), nullable=True)

    # Zulassungen
    eu_zulassung = Column(String(50), nullable=True)
    ablauf_zulassung = Column(DateTime(timezone=True), nullable=True)

    # Preise und Lager
    ek_preis = Column(DECIMAL(8, 2), nullable=True)
    vk_preis = Column(DECIMAL(8, 2), nullable=True)
    waehrung = Column(String(3), default="EUR")
    lagerbestand = Column(DECIMAL(10, 2), default=0)

    # Status und Meta
    ist_aktiv = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())