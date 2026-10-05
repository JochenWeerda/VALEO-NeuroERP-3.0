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
    Column, String, Integer, Boolean, DateTime, Date, Text,
    ForeignKey, DECIMAL, Index, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
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
    inventory_article_id = Column(String(64), nullable=True, comment="FEED-CHAIN-004: Link zu domain_inventory.articles")
    einheit = Column(String(10), default="t")
    min_bestand_t = Column(DECIMAL(12, 2), nullable=True, comment="Mindestbestand in Tonnen")
    preis_pro_t = Column(DECIMAL(12, 2), nullable=True, comment="Preis pro Tonne EUR")
    aktiv = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GrundfutterAnalyse(Base):
    """Grundfutter-Laboranalyse (LUFA / VDLUFA-Standard).

    Speichert alle Parameter eines LUFA-Prüfberichts inkl. GfE-2023-Kennwerte.
    Werte beziehen sich auf Trockensubstanz (TS) sofern nicht anders angegeben.
    """
    __tablename__ = "grundfutter_analysen"
    __table_args__ = (
        Index("ix_gfa_tenant", "tenant_id"),
        Index("ix_gfa_tenant_probe", "tenant_id", "probe_nr"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)

    # --- Metadaten ---
    labor = Column(String(255), nullable=True, comment="Labor (z.B. LUFA Nord-West)")
    probe_nr = Column(String(50), nullable=True, comment="Probe-Nr. des Labors")
    auftragsnummer = Column(String(50), nullable=True)
    kundennummer = Column(String(50), nullable=True)
    bezeichnung = Column(String(255), nullable=False, comment="Probenbezeichnung (Einsender)")
    probenart = Column(String(100), nullable=True, comment="z.B. Grassilage, Maissilage, Heu")
    erntetermin = Column(Date, nullable=True)
    eingangsdatum = Column(Date, nullable=True)
    analyse_datum = Column(Date, nullable=True)
    probenahme_ort = Column(String(255), nullable=True)
    schnitt = Column(Integer, nullable=True, comment="Schnitt-Nr (1. Schnitt etc.)")
    quelle_datei = Column(String(500), nullable=True, comment="Originaldateiname (PDF/CSV)")
    feed_id = Column(String, nullable=True, comment="Kanonisches Futtermittel")
    scope_code = Column(String(80), nullable=False, default="default")
    status = Column(String(32), nullable=False, default="draft")
    is_active = Column(Boolean, nullable=False, default=False)
    method = Column(String(255), nullable=True)
    sampled_at = Column(DateTime(timezone=True), nullable=True)
    valid_from = Column(Date, nullable=False, server_default=func.current_date())
    valid_until = Column(Date, nullable=True)
    original_document_id = Column(String, nullable=True)
    original_sha256 = Column(String(64), nullable=True)
    revision = Column(Integer, nullable=False, default=1)
    released_at = Column(DateTime(timezone=True), nullable=True)
    released_by = Column(String, nullable=True)
    changed_by = Column(String, nullable=False, default="legacy-ground-feed-api")

    # --- Sensorik (Originalsubstanz) ---
    aussehen = Column(String(100), nullable=True)
    geruch = Column(String(100), nullable=True)
    ph_wert = Column(DECIMAL(4, 2), nullable=True, comment="pH-Wert (Originalsubstanz)")

    # --- Grundnährstoffe (% Originalsubstanz / % TS) ---
    trockensubstanz_os = Column(DECIMAL(6, 2), nullable=True, comment="Trockensubstanz % (Originalsubstanz)")
    rohprotein_ts = Column(DECIMAL(6, 2), nullable=True, comment="Rohprotein % (TS)")
    rohfaser_ts = Column(DECIMAL(6, 2), nullable=True, comment="Rohfaser % (TS)")
    rohfett_ts = Column(DECIMAL(6, 2), nullable=True, comment="Rohfett % (TS)")
    rohasche_ts = Column(DECIMAL(6, 2), nullable=True, comment="Rohasche % (TS)")
    gesamtzucker_ts = Column(DECIMAL(6, 2), nullable=True, comment="Gesamtzucker % (TS)")
    sand_ts = Column(DECIMAL(6, 2), nullable=True, comment="Sand % (TS)")
    nfc_ts = Column(DECIMAL(6, 2), nullable=True, comment="NFC Nicht-Faser-Kohlenhydrate % (TS)")

    # --- Faseranalytik (% TS) ---
    adfom_ts = Column(DECIMAL(6, 2), nullable=True, comment="ADFom % (TS)")
    andfom_ts = Column(DECIMAL(6, 2), nullable=True, comment="aNDFom % (TS)")
    adl_ts = Column(DECIMAL(6, 2), nullable=True, comment="ADL Lignin % (TS)")
    hemicellulose_ts = Column(DECIMAL(6, 2), nullable=True, comment="Hemicellulose % (TS)")

    # --- Gasbildung / Verdaulichkeit ---
    gasbildung_ts = Column(DECIMAL(6, 2), nullable=True, comment="Gasbildung ml/200mg (TS)")
    omd_ts = Column(DECIMAL(6, 2), nullable=True, comment="Verdaulichkeit org. Masse OMD % (TS)")

    # --- Energiebewertung ---
    me_rind_gfe2008_ts = Column(DECIMAL(6, 3), nullable=True, comment="ME-Rind GfE 2008 MJ/kg (TS)")
    nel_ts = Column(DECIMAL(6, 3), nullable=True, comment="NEL MJ/kg (TS)")
    me_gfe2023_ts = Column(DECIMAL(6, 3), nullable=True, comment="Umsetzbare Energie ME GfE 2023 MJ/kg (TS)")
    bruttoenergie_ts = Column(DECIMAL(6, 3), nullable=True, comment="Bruttoenergie GE MJ/kg (TS)")
    strukturwert_ts = Column(DECIMAL(5, 2), nullable=True, comment="Strukturwert (DLG 01|2023)")

    # --- Proteinbewertung GfE (g/kg TS) ---
    nxp_ts = Column(DECIMAL(7, 1), nullable=True, comment="Nutzbares Rohprotein nXP g/kg (TS)")
    nxp_udp_ts = Column(DECIMAL(7, 1), nullable=True, comment="nXP (UDP aus XP-Fraktionierung) g/kg (TS)")
    rnb_ts = Column(DECIMAL(6, 2), nullable=True, comment="Ruminale N-Bilanz RNB g/kg (TS)")
    rnb_udp_ts = Column(DECIMAL(6, 2), nullable=True, comment="RNB (UDP-Fraktionierung) g/kg (TS)")
    reineiweis_ts = Column(DECIMAL(6, 2), nullable=True, comment="Reineiweiß % (TS)")
    anteil_reineiweis_ts = Column(DECIMAL(6, 2), nullable=True, comment="Anteil Reineiweiß an XP % (TS)")

    # --- XP-Fraktionierung (% TS) ---
    xp_fraktion_a_ts = Column(DECIMAL(6, 2), nullable=True, comment="A: NPN % (TS)")
    xp_fraktion_b1_ts = Column(DECIMAL(6, 2), nullable=True, comment="B1: Pufferlösl. Reinprotein % (TS)")
    xp_fraktion_b2_ts = Column(DECIMAL(6, 2), nullable=True, comment="B2: Pufferunlösl. Reinprotein % (TS)")
    xp_fraktion_b3_ts = Column(DECIMAL(6, 2), nullable=True, comment="B3: Zellwandgeb. lösl. Reinprotein % (TS)")
    xp_fraktion_c_ts = Column(DECIMAL(6, 2), nullable=True, comment="C: Zellwandgeb. unlösl. Reinprotein % (TS)")
    udp2_ts = Column(DECIMAL(7, 1), nullable=True, comment="UDP 2 g/kg XP (TS)")
    udp5_ts = Column(DECIMAL(7, 1), nullable=True, comment="UDP 5 g/kg XP (TS)")
    udp8_ts = Column(DECIMAL(7, 1), nullable=True, comment="UDP 8 g/kg XP (TS)")

    # --- GfE 2023 dünndarmverdauliche Amino- und Gesamtproteine (g/kg TS) ---
    sidp_ts = Column(DECIMAL(6, 2), nullable=True, comment="sidP g/kg (TS)")
    sidlys_ts = Column(DECIMAL(6, 3), nullable=True, comment="sidLys g/kg (TS)")
    sidmet_ts = Column(DECIMAL(6, 3), nullable=True, comment="sidMet g/kg (TS)")
    rmd_ts = Column(DECIMAL(6, 2), nullable=True, comment="RMD Ruminale Mikrobielle Differenz g N/kg (TS)")

    # --- CP-Abbau-Kinetik (DLG-Tabelle 2025) ---
    cp_abbau_a_ts = Column(DECIMAL(5, 1), nullable=True, comment="a: rasch abbaubare CP-Fraktion % (TS)")
    cp_abbau_b_ts = Column(DECIMAL(5, 1), nullable=True, comment="b: potentiell abbaubare CP-Fraktion % (TS)")
    cp_abbau_c_ts = Column(DECIMAL(5, 2), nullable=True, comment="c: Abbaurate Fraktion b %/h (TS)")
    cp_abbau_lag_ts = Column(DECIMAL(5, 2), nullable=True, comment="lag: Verzögerungszeit ruminaler CP-Abbau h (TS)")

    # --- Mineralstoffe (% TS) — aus Durchschnittswerten / Seite 4 ---
    calcium_ts = Column(DECIMAL(5, 3), nullable=True, comment="Ca % (TS)")
    phosphor_ts = Column(DECIMAL(5, 3), nullable=True, comment="P % (TS)")
    natrium_ts = Column(DECIMAL(5, 3), nullable=True, comment="Na % (TS)")
    magnesium_ts = Column(DECIMAL(5, 3), nullable=True, comment="Mg % (TS)")
    kalium_ts = Column(DECIMAL(5, 3), nullable=True, comment="K % (TS)")

    # --- Verwaltung ---
    notizen = Column(Text, nullable=True)
    verifiziert = Column(Boolean, default=False, comment="Durch Nutzer geprüft/freigegeben")
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
    verbrauch = Column(JSONB, nullable=True,
                       comment="Snapshot des Komponentenverbrauchs bei Freigabe (Mischprotokoll)")
    charge_id = Column(String(64), nullable=True,
                       comment="Referenz auf domain_ops.ops_chargen.id der Fertigwaren-Charge")
    erstellt_von = Column(String(255), nullable=True)
    freigegeben_von = Column(String(255), nullable=True)
    freigegeben_am = Column(DateTime(timezone=True), nullable=True)
    fertig_am = Column(DateTime(timezone=True), nullable=True)
    fibu_journal_ref = Column(String(128), nullable=True,
                              comment="JournalEntry-Referenz nach Produktionsabschluss (PROD-FIBU-001)")
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


class RationsZugang(Base):
    """
    Zugangsliste für betriebsspezifische Rations- und Grundfutterdaten.

    Datenschutzmodell (DSGVO-konform):
    - Betriebseigene Grundfutter und Rationen sind mandantenspezifisch und
      dürfen nur von explizit berechtigten Personen eingesehen werden.
    - DLG-Futterdaten (öffentlich) sind von dieser Einschränkung ausgenommen.

    Berechtigte Rollen:
    - 'admin'           – systemweiter Admin, immer berechtigt
    - 'vertriebsberater'– dem Betrieb zugeordneter Berater (durch Admin/Betrieb)
    - 'portal_user'     – durch Betrieb eingeladener Portal-Nutzer
    - 'share_link'      – zeitlich begrenzter Token-Zugang (z.B. Beratungsbesuch)

    CRUD-Berechtigungen pro Datensatz:
    - darf_lesen              – Grundfutter und Rationen lesen
    - darf_rationen_anlegen   – neue Optimierung starten / speichern
    - darf_grundfutter_anlegen– eigene Analysen hochladen
    - darf_zugang_verwalten   – Zugangsliste bearbeiten (nur admin/betrieb)
    """
    __tablename__ = "rations_zugang"
    __table_args__ = (
        Index("ix_rz_tenant", "tenant_id"),
        Index("ix_rz_token", "share_token"),
        Index("ix_rz_email", "empfaenger_email"),
        {"schema": "domain_shared"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False, comment="Betrieb / Mandant, dem dieser Zugang gilt")

    # ── Empfänger ──────────────────────────────────────────────────────────────
    empfaenger_email = Column(String(255), nullable=False, comment="E-Mail-Adresse des Zugangangs-Inhabers")
    empfaenger_name  = Column(String(255), nullable=True,  comment="Anzeigename (optional)")

    # ── Typ & Token ────────────────────────────────────────────────────────────
    zugang_typ = Column(
        String(50), nullable=False, default="portal_user",
        comment="admin | vertriebsberater | portal_user | share_link"
    )
    share_token = Column(String(64), nullable=True, unique=True,
                         comment="UUID-Token für Link-basierten Zugang (nur typ=share_link)")

    # ── Gültigkeit ─────────────────────────────────────────────────────────────
    gueltig_ab  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    gueltig_bis = Column(DateTime(timezone=True), nullable=True,
                         comment="None = unbegrenzt; nur für share_link empfohlen zu setzen")

    # ── Datenschutz-Berechtigungen ─────────────────────────────────────────────
    darf_lesen               = Column(Boolean, nullable=False, default=True)
    darf_rationen_anlegen    = Column(Boolean, nullable=False, default=False)
    darf_grundfutter_anlegen = Column(Boolean, nullable=False, default=False)
    darf_zugang_verwalten    = Column(Boolean, nullable=False, default=False,
                                      comment="Darf selbst weitere Zugänge erteilen/entziehen")

    # ── Status ─────────────────────────────────────────────────────────────────
    ist_aktiv    = Column(Boolean, nullable=False, default=True)
    gesperrt_am  = Column(DateTime(timezone=True), nullable=True)
    gesperrt_durch = Column(String(255), nullable=True)
    sperrgrund   = Column(Text, nullable=True)

    # ── Verwaltung / Audit ─────────────────────────────────────────────────────
    erstellt_von_email = Column(String(255), nullable=False)
    erstellt_von_name  = Column(String(255), nullable=True)
    notizen    = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
