"""
SQLAlchemy models for Futtermittel (Feed) domain.

Tables:
- futtermittel_einzelfutter: Einzelfuttermittel-Stammdaten (single feed ingredients)
- futtermittel_mischfutter: Mischfuttermittel-Stammdaten (compound feed products)
- futtermittel_rezepte: Rezepte (feed recipes/formulations)
- futtermittel_rezept_komponenten: Rezept-Komponenten (recipe components)
- futtermittel_produktionsauftraege: Produktionsaufträge (production orders)
- agrar_sorten: Sortenregister (variety register)
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    Text, ForeignKey, DECIMAL, Index, UniqueConstraint,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class Einzelfuttermittel(Base):
    """Single feed ingredient master data."""
    __tablename__ = "futtermittel_einzelfutter"
    __table_args__ = (
        Index("ix_ef_tenant", "tenant_id"),
        Index("ix_ef_tenant_artikel", "tenant_id", "artikel_nummer"),
        UniqueConstraint("tenant_id", "artikel_nummer", name="uq_ef_tenant_artikel"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    artikel_nummer = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    art = Column(String(100), nullable=False, comment="z.B. Eiweißfutter, Energiefutter, Mineralfutter")
    herkunft = Column(String(100), nullable=True)
    lieferant = Column(String(255), nullable=True)
    protein = Column(DECIMAL(6, 2), nullable=True, comment="Rohprotein %")
    energie = Column(DECIMAL(6, 2), nullable=True, comment="ME MJ/kg")
    faser = Column(DECIMAL(6, 2), nullable=True, comment="Rohfaser %")
    fett = Column(DECIMAL(6, 2), nullable=True, comment="Rohfett %")
    asche = Column(DECIMAL(6, 2), nullable=True, comment="Rohasche %")
    trockensubstanz = Column(DECIMAL(6, 2), nullable=True, comment="Trockensubstanz %")
    gvo_status = Column(String(50), nullable=True, comment="gvo-frei, gvo-frei-zertifiziert, gvo")
    qs_milch = Column(Boolean, default=False, comment="QS-Milch zertifiziert")
    gmp_plus = Column(Boolean, default=False, comment="GMP+ zertifiziert")
    bio_zertifiziert = Column(Boolean, default=False)
    verfuegbar_t = Column(DECIMAL(12, 2), default=0, comment="Verfügbarer Bestand in Tonnen")
    einheit = Column(String(10), default="t")
    min_bestand_t = Column(DECIMAL(12, 2), nullable=True, comment="Mindestbestand in Tonnen")
    preis_pro_t = Column(DECIMAL(12, 2), nullable=True, comment="Preis pro Tonne EUR")
    aktiv = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Mischfuttermittel(Base):
    """Compound feed product master data."""
    __tablename__ = "futtermittel_mischfutter"
    __table_args__ = (
        Index("ix_mf_tenant", "tenant_id"),
        Index("ix_mf_tenant_code", "tenant_id", "produkt_code"),
        UniqueConstraint("tenant_id", "produkt_code", name="uq_mf_tenant_code"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    produkt_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    tierart = Column(String(100), nullable=False, comment="z.B. Rind (Milch), Schwein (Mast)")
    leistungsstufe = Column(String(100), nullable=True, comment="z.B. Hochleistung (>30 l/Tag)")
    protein = Column(DECIMAL(6, 2), nullable=True, comment="Rohprotein % Zielwert")
    energie = Column(DECIMAL(6, 2), nullable=True, comment="ME MJ/kg Zielwert")
    beschreibung = Column(Text, nullable=True)
    aktiv = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    rezepte = relationship("FuttermittelRezept", back_populates="mischfutter", cascade="all, delete-orphan")


class FuttermittelRezept(Base):
    """Feed recipe / formulation."""
    __tablename__ = "futtermittel_rezepte"
    __table_args__ = (
        Index("ix_rez_tenant", "tenant_id"),
        Index("ix_rez_tenant_code", "tenant_id", "rezept_code"),
        UniqueConstraint("tenant_id", "rezept_code", name="uq_rez_tenant_code"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    rezept_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    tierart = Column(String(100), nullable=False)
    mischfutter_id = Column(String, ForeignKey("domain_shared.futtermittel_mischfutter.id"), nullable=True)
    version = Column(Integer, default=1)
    protein_ziel = Column(DECIMAL(6, 2), nullable=True)
    energie_ziel = Column(DECIMAL(6, 2), nullable=True)
    bemerkung = Column(Text, nullable=True)
    aktiv = Column(Boolean, default=True)
    gueltig_ab = Column(Date, nullable=True)
    gueltig_bis = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mischfutter = relationship("Mischfuttermittel", back_populates="rezepte")
    komponenten = relationship("RezeptKomponente", back_populates="rezept", cascade="all, delete-orphan")


class RezeptKomponente(Base):
    """Recipe component / ingredient line."""
    __tablename__ = "futtermittel_rezept_komponenten"
    __table_args__ = (
        Index("ix_rk_rezept", "rezept_id"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    rezept_id = Column(String, ForeignKey("domain_shared.futtermittel_rezepte.id", ondelete="CASCADE"), nullable=False)
    einzelfutter_id = Column(String, ForeignKey("domain_shared.futtermittel_einzelfutter.id"), nullable=True)
    komponente_name = Column(String(255), nullable=False, comment="Anzeigename, auch wenn kein FK")
    anteil = Column(DECIMAL(6, 4), nullable=False, comment="Anteil 0.0000 - 1.0000")
    min_anteil = Column(DECIMAL(6, 4), nullable=True, comment="Min-Anteil für Optimierung")
    max_anteil = Column(DECIMAL(6, 4), nullable=True, comment="Max-Anteil für Optimierung")
    sortierung = Column(Integer, default=0)

    rezept = relationship("FuttermittelRezept", back_populates="komponenten")


class ProduktionsAuftrag(Base):
    """Feed production order."""
    __tablename__ = "futtermittel_produktionsauftraege"
    __table_args__ = (
        Index("ix_pa_tenant", "tenant_id"),
        Index("ix_pa_tenant_status", "tenant_id", "status"),
        Index("ix_pa_chargen", "chargen_id"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    chargen_id = Column(String(50), nullable=False)
    rezept_id = Column(String, ForeignKey("domain_shared.futtermittel_rezepte.id"), nullable=True)
    rezept_name = Column(String(255), nullable=False, comment="Snapshot des Rezeptnamens")
    menge_t = Column(DECIMAL(12, 3), nullable=False, comment="Produktionsmenge in Tonnen")
    status = Column(String(30), nullable=False, default="erstellt",
                    comment="erstellt, freigegeben, in_produktion, fertig, storniert")
    bestands_abzug_erfolgt = Column(Boolean, default=False)
    erstellt_von = Column(String(255), nullable=True)
    freigegeben_von = Column(String(255), nullable=True)
    freigegeben_am = Column(DateTime(timezone=True), nullable=True)
    fertig_am = Column(DateTime(timezone=True), nullable=True)
    bemerkung = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AgrarSorte(Base):
    """Crop variety register — tenant-specific."""
    __tablename__ = "agrar_sorten"
    __table_args__ = (
        Index("ix_as_tenant", "tenant_id"),
        UniqueConstraint("tenant_id", "variety_number", name="uq_as_tenant_varnr"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    variety_number = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    crop_type = Column(String(50), nullable=True, comment="WHEAT, MAIZE, BARLEY, OATS, RAPESEED, ...")
    zuechter = Column(String(255), nullable=True, comment="Züchter / Breeder")
    zulassungsjahr = Column(Integer, nullable=True)
    reifezahl = Column(String(10), nullable=True, comment="Reifezahl / maturity rating")
    qualitaetsgruppe = Column(String(50), nullable=True, comment="E, A, B, C, K bei Weizen")
    aktiv = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
