"""
Einkauf-Domänen-Modelle (domain_einkauf)

Enthält:
  - EinkaufLieferant          — Lieferanten-Stamm (domain_einkauf, mit Schema)
  - EinkaufKontrakt           — Rahmenkontrakte/Lieferverträge
  - EinkaufKontraktPosition   — Positionen im Kontrakt
  - ArtikelLagerParameter     — Mindest-/Maximal-/Meldebestand je Artikel+Lager
  - EinkaufBestellvorschlag   — Bestell-Vorschlag-Kopf (3 Typen: lager/verkauf/rohware)
  - EinkaufBestellvorschlagPosition — Bestell-Vorschlag-Positionen
  - EinkaufBestellung         — Bestellungen (mit Schema domain_einkauf)
  - EinkaufBestellungPosition — Bestell-Positionen
  - LagerKontenzuordnung      — Artikel-Gruppe → SKR-Konto-Mapping
  - PalettenKonto             — Paletten-Bestand/Bewegungen (Tausch-Konto)
  - PfandKonto                — Pfand/Leergut-Buchungen (IBC, Fässer, Kannen)
  - FremdwarenEinlagerung     — Drittpartei-Ware im eigenen Lager
"""
from __future__ import annotations

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Index,
    Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


# ─────────────────────────────────────────────────────────────────────────────
# Lieferant (Stamm)
# ─────────────────────────────────────────────────────────────────────────────

class EinkaufLieferant(Base):
    """Lieferanten-Stammdaten mit vollem Schema-Kontext."""
    __tablename__ = "lieferanten"
    __table_args__ = (
        Index("ix_ek_lieferant_tenant_nr", "tenant_id", "lieferantennummer"),
        {"schema": "domain_einkauf"},
    )

    id                  = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id           = Column(String, nullable=False, index=True)
    lieferantennummer   = Column(String(50), nullable=False)
    partner_id          = Column(String)          # FK → domain_crm.business_partners (optional)
    firmenname          = Column(String(255), nullable=False, index=True)
    ansprechpartner     = Column(String(255))
    email               = Column(String(255))
    telefon             = Column(String(50))
    fax                 = Column(String(50))
    strasse             = Column(String(255))
    plz                 = Column(String(20))
    ort                 = Column(String(100))
    land                = Column(String(100), default="Deutschland")
    steuernummer        = Column(String(50))
    ust_id              = Column(String(30))
    zahlungsbedingungen = Column(String(50))      # z.B. "14T2%/30Netto"
    zahlungsziel_tage   = Column(Integer)
    skonto_prozent      = Column(Numeric(5, 2))
    lieferzeit_tage     = Column(Integer)
    mindestbestellwert  = Column(Numeric(12, 2))
    bewertung           = Column(Integer)          # 1–5
    aktiv               = Column(Boolean, default=True)
    notiz               = Column(Text)
    # Versandoptionen
    edi_kennung         = Column(String(50))       # EDIFACT-Absenderkennung
    edi_format          = Column(String(20))       # ORDERS05, ORDCHG, …
    email_bestellung    = Column(String(255))      # E-Mail für Bestellungen
    fax_bestellung      = Column(String(50))       # Fax für Bestellungen

    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())
    created_by          = Column(String(200))

    kontrakte           = relationship("EinkaufKontrakt",  back_populates="lieferant")
    bestellungen        = relationship("EinkaufBestellung", back_populates="lieferant")


# ─────────────────────────────────────────────────────────────────────────────
# Rahmen-Kontrakte
# ─────────────────────────────────────────────────────────────────────────────

class EinkaufKontrakt(Base):
    """Rahmenkontrakt / Liefervereinbarung mit einem Lieferanten."""
    __tablename__ = "kontrakte"
    __table_args__ = (
        Index("ix_ek_kontrakt_tenant_nr", "tenant_id", "kontraktnummer"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    kontraktnummer   = Column(String(50), nullable=False)
    lieferant_id     = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.lieferanten.id"), nullable=False, index=True)
    bezeichnung      = Column(String(300))
    gueltig_von      = Column(Date)
    gueltig_bis      = Column(Date)
    status           = Column(String(20), default="aktiv")
                       # aktiv | abgelaufen | storniert | entwurf
    kontrakt_typ     = Column(String(30), default="rahmen")
                       # rahmen | fest | option | preisgarantie
    waehrung         = Column(String(3), default="EUR")
    gesamtwert       = Column(Numeric(14, 2))
    gesamtmenge      = Column(Numeric(14, 3))
    offene_menge     = Column(Numeric(14, 3))
    niederlassung_id = Column(String)              # FK → domain_shared.branches
    notiz            = Column(Text)
    anhang_ids       = Column(JSONB)               # DMS-Anhang-IDs

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
    created_by       = Column(String(200))

    lieferant        = relationship("EinkaufLieferant",          back_populates="kontrakte")
    positionen       = relationship("EinkaufKontraktPosition",   back_populates="kontrakt",
                                    cascade="all, delete-orphan")


class EinkaufKontraktPosition(Base):
    """Position in einem Einkaufs-Kontrakt."""
    __tablename__ = "kontrakt_positionen"
    __table_args__ = {"schema": "domain_einkauf"}

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    kontrakt_id      = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.kontrakte.id"), nullable=False, index=True)
    pos_nr           = Column(Integer, nullable=False)
    article_id       = Column(String)              # FK → domain_inventory.articles
    artikel_bezeichnung = Column(String(300))
    menge            = Column(Numeric(14, 3), nullable=False)
    offene_menge     = Column(Numeric(14, 3))
    einheit          = Column(String(20))
    preis            = Column(Numeric(14, 4))
    preis_einheit    = Column(String(20), default="100kg")  # je kg, je t, je 100kg
    preisbindung     = Column(String(20), default="fix")    # fix | gleitend | markt
    gueltig_von      = Column(Date)
    gueltig_bis      = Column(Date)
    notiz            = Column(Text)

    kontrakt         = relationship("EinkaufKontrakt", back_populates="positionen")


# ─────────────────────────────────────────────────────────────────────────────
# Artikel-Lager-Parameter (Meldebestand, Min/Max)
# ─────────────────────────────────────────────────────────────────────────────

class ArtikelLagerParameter(Base):
    """
    Mindest-/Maximal-/Meldebestand je Artikel + Niederlassung/Lager.
    Grundlage für die Bestell-Vorschlag-Engine (lager-basiert).
    """
    __tablename__ = "artikel_lager_parameter"
    __table_args__ = (
        UniqueConstraint("tenant_id", "article_id", "warehouse_id",
                         name="uq_alp_tenant_article_warehouse"),
        Index("ix_alp_tenant_article", "tenant_id", "article_id"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False)
    article_id       = Column(String, nullable=False, index=True)  # → domain_inventory.articles
    warehouse_id     = Column(String, index=True)                  # → domain_inventory.warehouses
    niederlassung_id = Column(String)                              # → domain_shared.branches

    # Bestandsgrenzen
    mindestbestand   = Column(Numeric(14, 3), default=0)    # Absolutes Minimum
    maximalbestand   = Column(Numeric(14, 3))               # Maximale Einlagerung
    meldebestand     = Column(Numeric(14, 3), default=0)    # Trigger für Bestellvorschlag
    soll_bestand     = Column(Numeric(14, 3))               # Ziel nach Auffüllung
    # Beschaffungs-Defaults
    std_lieferant_id = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.lieferanten.id"))
    std_bestellmenge = Column(Numeric(14, 3))               # Standard-Bestellmenge
    std_einheit      = Column(String(20))
    wiederbeschaffungs_tage = Column(Integer, default=3)    # Beschaffungsdauer
    # Kalkulatorische Felder (befüllt durch Service)
    durchschnitt_verbrauch_tag = Column(Numeric(14, 4))     # Ø Tagesverbrauch
    reichweite_tage  = Column(Numeric(10, 1))               # Berechnete Reichweite

    aktiv            = Column(Boolean, default=True)
    notiz            = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by       = Column(String(200))


# ─────────────────────────────────────────────────────────────────────────────
# Bestell-Vorschlag (Workflow-Dokument)
# ─────────────────────────────────────────────────────────────────────────────

class EinkaufBestellvorschlag(Base):
    """
    Bestell-Vorschlag-Kopf.
    Wird durch eine der 3 Engines befüllt und kann dann in Bestellungen
    umgewandelt werden.
    """
    __tablename__ = "bestellvorschlaege"
    __table_args__ = {"schema": "domain_einkauf"}

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    vorschlag_typ    = Column(String(20), nullable=False)
                       # 'lager' | 'verkauf' | 'rohware'
    bezeichnung      = Column(String(300))
    datum            = Column(Date, nullable=False)
    niederlassung_id = Column(String)
    # Filterparameter der Berechnung (gespeichert für Reproduzierbarkeit)
    parameter        = Column(JSONB, default=dict)
                       # z.B. {stichtag, von_datum, bis_datum, artikelgruppe, …}
    status           = Column(String(20), default="entwurf")
                       # entwurf | freigegeben | in_bestellung | abgeschlossen
    erstellt_von     = Column(String(200))
    freigegeben_von  = Column(String(200))
    freigegeben_am   = Column(DateTime(timezone=True))
    notiz            = Column(Text)

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    positionen       = relationship("EinkaufBestellvorschlagPosition",
                                    back_populates="vorschlag",
                                    cascade="all, delete-orphan",
                                    order_by="EinkaufBestellvorschlagPosition.pos_nr")


class EinkaufBestellvorschlagPosition(Base):
    """Position in einem Bestell-Vorschlag."""
    __tablename__ = "bestellvorschlag_positionen"
    __table_args__ = {"schema": "domain_einkauf"}

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    vorschlag_id     = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.bestellvorschlaege.id"),
                             nullable=False, index=True)
    pos_nr           = Column(Integer, nullable=False)

    article_id       = Column(String, nullable=False)
    artikel_nr       = Column(String(50))
    artikel_bezeichnung = Column(String(300))
    artikel_gruppe   = Column(String(80))
    einheit          = Column(String(20))

    # Berechnungs-Basis
    ist_bestand      = Column(Numeric(14, 3), default=0)    # Aktueller Bestand
    offene_auftraege = Column(Numeric(14, 3), default=0)    # Offene VK-Aufträge
    bedarf           = Column(Numeric(14, 3), default=0)    # Berechneter Bedarf
    vorschlag_menge  = Column(Numeric(14, 3), nullable=False)  # Vorgeschlagene Menge
    bestell_menge    = Column(Numeric(14, 3))               # Manuell angepasste Menge

    # Lieferant & Preis
    lieferant_id     = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.lieferanten.id"))
    lieferant_name   = Column(String(255))
    kontrakt_id      = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.kontrakte.id"))
    letzter_preis    = Column(Numeric(14, 4))
    preis_einheit    = Column(String(20))
    letzter_kauf_datum = Column(Date)

    status           = Column(String(20), default="offen")
                       # offen | bestellt | ignoriert

    vorschlag        = relationship("EinkaufBestellvorschlag", back_populates="positionen")


# ─────────────────────────────────────────────────────────────────────────────
# Bestellungen (proper domain_einkauf schema)
# ─────────────────────────────────────────────────────────────────────────────

class EinkaufBestellung(Base):
    """
    Einkaufs-Bestellung mit vollem Schema-Kontext.
    Ersetzt/ergänzt die alte `einkauf_bestellungen`-Tabelle (public schema).
    """
    __tablename__ = "bestellungen"
    __table_args__ = (
        Index("ix_ek_bestellung_tenant_nr", "tenant_id", "bestellnummer"),
        Index("ix_ek_bestellung_tenant_status", "tenant_id", "status"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    bestellnummer    = Column(String(50), nullable=False)
    lieferant_id     = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.lieferanten.id"), nullable=False, index=True)
    vorschlag_id     = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.bestellvorschlaege.id"))
    niederlassung_id = Column(String)

    bestelldatum     = Column(Date, nullable=False)
    lieferdatum_wunsch = Column(Date)
    lieferdatum_zugesagt = Column(Date)
    lieferdatum_ist  = Column(Date)

    status           = Column(String(30), default="entwurf")
                       # entwurf | versandt | teilgeliefert | geliefert | storniert | abgeschlossen

    versand_art      = Column(String(20), default="email")
                       # email | fax | edi | post | telefon
    versandt_am      = Column(DateTime(timezone=True))
    versandt_von     = Column(String(200))

    netto_summe      = Column(Numeric(14, 2))
    mwst_betrag      = Column(Numeric(14, 2))
    brutto_summe     = Column(Numeric(14, 2))
    waehrung         = Column(String(3), default="EUR")

    zahlungsziel_tage = Column(Integer)
    skonto_prozent   = Column(Numeric(5, 2))
    skonto_frist_tage = Column(Integer)

    unsere_referenz  = Column(String(100))          # Interne Referenz
    ihre_referenz    = Column(String(100))          # Referenz beim Lieferanten
    kontrakt_id      = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.kontrakte.id"))
    freitext_kopf    = Column(Text)
    freitext_fuss    = Column(Text)
    notiz            = Column(Text)
    anhang_ids       = Column(JSONB)               # DMS-Anhang-IDs

    erstellt_von     = Column(String(200))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    lieferant        = relationship("EinkaufLieferant",    back_populates="bestellungen")
    positionen       = relationship("EinkaufBestellungPosition",
                                    back_populates="bestellung",
                                    cascade="all, delete-orphan",
                                    order_by="EinkaufBestellungPosition.pos_nr")


class EinkaufBestellungPosition(Base):
    """Position in einer Einkaufsbestellung."""
    __tablename__ = "bestellung_positionen"
    __table_args__ = {"schema": "domain_einkauf"}

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    bestellung_id    = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.bestellungen.id"),
                             nullable=False, index=True)
    pos_nr           = Column(Integer, nullable=False)

    article_id       = Column(String)              # → domain_inventory.articles
    artikel_nr       = Column(String(50), nullable=False)
    artikel_bezeichnung = Column(String(300), nullable=False)
    lieferanten_artnr = Column(String(50))         # Lieferanten-Artikelnummer

    menge            = Column(Numeric(14, 3), nullable=False)
    menge_geliefert  = Column(Numeric(14, 3), default=0)
    menge_offen      = Column(Numeric(14, 3))      # = menge - menge_geliefert
    einheit          = Column(String(20), nullable=False)

    einzelpreis      = Column(Numeric(14, 4))
    preis_einheit    = Column(String(20), default="100kg")  # je kg, je t, je 100kg
    rabatt_prozent   = Column(Numeric(5, 2), default=0)
    netto_betrag     = Column(Numeric(14, 2))
    mwst_satz        = Column(Numeric(5, 2))
    mwst_betrag      = Column(Numeric(14, 2))
    brutto_betrag    = Column(Numeric(14, 2))

    kontrakt_pos_id  = Column(PGUUID(as_uuid=False),
                             ForeignKey("domain_einkauf.kontrakt_positionen.id"))
    lieferdatum      = Column(Date)
    lagerort         = Column(String(100))
    notiz            = Column(Text)

    status           = Column(String(20), default="offen")
                       # offen | teilgeliefert | geliefert | storniert

    bestellung       = relationship("EinkaufBestellung", back_populates="positionen")


# ─────────────────────────────────────────────────────────────────────────────
# Lager-Konten-Zuordnung (Artikelgruppe → Sachkonto)
# ─────────────────────────────────────────────────────────────────────────────

class LagerKontenzuordnung(Base):
    """
    Zuordnung von Artikel-Gruppen zu Bewegungskonten (SKR-Konten).
    Steuert die automatische Buchung bei Warenbewegungen.
    """
    __tablename__ = "lager_kontenzuordnung"
    __table_args__ = (
        UniqueConstraint("tenant_id", "artikelgruppe", "niederlassung_id",
                         name="uq_lkz_tenant_gruppe_nl"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    artikelgruppe    = Column(String(80), nullable=False)
    niederlassung_id = Column(String)                # NULL = alle NL

    # Bilanz-Konten
    bestandskonto    = Column(String(20), nullable=False)   # z.B. 1500 Waren
    gegenkonto_zugang = Column(String(20))                  # z.B. 3200 Wareneingang
    gegenkonto_abgang = Column(String(20))                  # z.B. 3800 Wareneinsatz

    # Nebenkonten
    paletten_konto   = Column(String(20))                   # z.B. 0790 Paletten
    pfand_konto      = Column(String(20))                   # z.B. 0791 IBC/Leergut-Pfand
    fremdwaren_konto = Column(String(20))                   # z.B. 1600 Fremdware/Kommission
    einlagerung_konto = Column(String(20))                  # z.B. 8400 Einlagerungs-Erlöse
    chargen_konto    = Column(String(20))                   # z.B. 1505 Chargen-Unterkonto

    # Umsatzsteuer
    ust_schluessel   = Column(String(10))                   # Steuer-Schlüssel

    aktiv            = Column(Boolean, default=True)
    notiz            = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by       = Column(String(200))


# ─────────────────────────────────────────────────────────────────────────────
# Paletten-Konto (Tauschkonto)
# ─────────────────────────────────────────────────────────────────────────────

class PalettenKontoBuchung(Base):
    """
    Paletten-Tausch-Buchung.
    Verfolgt Paletten-Bestand je Geschäftspartner und Niederlassung.
    """
    __tablename__ = "paletten_konto_buchungen"
    __table_args__ = (
        Index("ix_pkl_tenant_partner", "tenant_id", "partner_id"),
        Index("ix_pkl_tenant_datum", "tenant_id", "buchungsdatum"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    partner_id       = Column(String, nullable=False, index=True)  # Kunde oder Lieferant
    partner_typ      = Column(String(10), nullable=False)          # 'kunde' | 'lieferant'
    niederlassung_id = Column(String)

    buchungsdatum    = Column(Date, nullable=False)
    buchungsart      = Column(String(20), nullable=False)
                       # ausgabe | ruecknahme | kauf | verkauf | differenz
    paletten_typ     = Column(String(30), default="EUR-Palette")
                       # EUR-Palette | Einwegpalette | Gitterbox | Großbox | sonstige
    menge            = Column(Integer, nullable=False)              # Anzahl Paletten
    saldo_vorher     = Column(Integer)
    saldo_nachher    = Column(Integer)

    referenz_typ     = Column(String(30))                          # lieferschein | bestellung | …
    referenz_id      = Column(String)
    referenz_nr      = Column(String(100))

    notiz            = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    created_by       = Column(String(200))


# ─────────────────────────────────────────────────────────────────────────────
# Pfand-Konto (IBC, Fässer, Kannen)
# ─────────────────────────────────────────────────────────────────────────────

class PfandKontoBuchung(Base):
    """
    Pfand-/Leergut-Buchung für IBC-Container, Fässer, Kannen etc.
    """
    __tablename__ = "pfand_konto_buchungen"
    __table_args__ = (
        Index("ix_pfk_tenant_partner", "tenant_id", "partner_id"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    partner_id       = Column(String, nullable=False, index=True)
    partner_typ      = Column(String(10), nullable=False)          # 'kunde' | 'lieferant'
    niederlassung_id = Column(String)

    buchungsdatum    = Column(Date, nullable=False)
    buchungsart      = Column(String(20), nullable=False)
                       # ausgabe | ruecknahme | kauf | verkauf | verlust
    gebinde_typ      = Column(String(50), nullable=False)
                       # IBC-1000l | IBC-600l | Fass-200l | Kanne-30l | Kanister-10l | sonstige
    menge            = Column(Numeric(10, 0), nullable=False)
    pfandwert_je_einheit = Column(Numeric(10, 2))                  # EUR je Gebinde
    gesamtpfandwert  = Column(Numeric(12, 2))

    saldo_menge      = Column(Numeric(10, 0))
    saldo_wert       = Column(Numeric(12, 2))

    referenz_typ     = Column(String(30))
    referenz_id      = Column(String)
    referenz_nr      = Column(String(100))

    notiz            = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    created_by       = Column(String(200))


# ─────────────────────────────────────────────────────────────────────────────
# Fremdwaren-Einlagerung
# ─────────────────────────────────────────────────────────────────────────────

class FremdwarenEinlagerung(Base):
    """
    Drittpartei-Ware, die im eigenen Lager eingelagert ist (Kommissionsware,
    Kunden-Ware, Poolware). Wird nicht als eigener Bestand geführt, aber
    Lagergebühren werden berechnet.
    """
    __tablename__ = "fremdwaren_einlagerung"
    __table_args__ = (
        Index("ix_fwe_tenant_partner", "tenant_id", "eigentuemer_id"),
        {"schema": "domain_einkauf"},
    )

    id               = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid7)
    tenant_id        = Column(String, nullable=False, index=True)
    einlagerungs_nr  = Column(String(50), nullable=False)
    eigentuemer_id   = Column(String, nullable=False, index=True)  # Partner-ID
    eigentuemer_name = Column(String(255))
    niederlassung_id = Column(String)
    warehouse_id     = Column(String)
    lagerort         = Column(String(100))

    article_id       = Column(String)
    artikel_nr       = Column(String(50))
    artikel_bezeichnung = Column(String(300))
    charge           = Column(String(64))
    einlagerungstyp  = Column(String(20), default="fremdware")
                       # fremdware | poolware | kommission | depot | sonstiges

    menge_eingelagert = Column(Numeric(14, 3), nullable=False)
    menge_aktuell    = Column(Numeric(14, 3), nullable=False)
    einheit          = Column(String(20))

    einlagerungsdatum = Column(Date, nullable=False)
    auslagerungsdatum = Column(Date)
    geplante_auslagerung = Column(Date)

    # Lagergebühren
    gebuehr_pro_tag  = Column(Numeric(10, 4))                      # EUR/t/Tag o. EUR/Stk/Tag
    gebuehr_einheit  = Column(String(20), default="t")
    letzte_abrechnung = Column(Date)

    status           = Column(String(20), default="eingelagert")
                       # eingelagert | teilausgelagert | ausgelagert
    notiz            = Column(Text)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
    created_by       = Column(String(200))
