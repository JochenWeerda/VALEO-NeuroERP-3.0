"""
Operations Domain Models - Waage und Fuhrpark
Models für Waagen, Wiegungen, Fahrzeuge und Fahrer
"""

from uuid import uuid4

from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Text, ForeignKey, DECIMAL, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base
from app.core.uuid7 import uuid7, default_prefixed_id


def _new_flow_spine_instance_id() -> str:
    return str(uuid4())


def _new_flow_spine_event_id() -> str:
    return str(uuid4())


class WaageStatus(str, enum.Enum):
    """Waage Status Enum"""
    AKTIV = "aktiv"
    INAKTIV = "inaktiv"
    WARTUNG = "wartung"
    DEFEKT = "defekt"


class FahrzeugStatus(str, enum.Enum):
    """Fahrzeug Status Enum"""
    VERFUEGBAR = "verfuegbar"
    UNTERWEGS = "unterwegs"
    WARTUNG = "wartung"
    AUSSCHIECHEN = "ausgeschieden"


class FahrerStatus(str, enum.Enum):
    """Fahrer Status Enum"""
    VERFUEGBAR = "verfuegbar"
    UNTERWEGS = "unterwegs"
    PAUSE = "pause"
    URLAUB = "urlaub"
    KRANK = "krank"


class Waage(Base):
    """
    Waage Model für Waagen-Management
    """
    __tablename__ = "ops_waagen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("W"))
    
    # Stammdaten
    standort = Column(String(100), nullable=False)
    typ = Column(String(50), nullable=False)  # z.B. "LKW-Waage", "Palette-Waage"
    max_kapazitaet = Column(Float, nullable=False)  # in Tonnen
    
    # Eichung
    letzte_eichung = Column(DateTime(timezone=True))
    naechste_eichung = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default=WaageStatus.AKTIV.value)
    
    # Metadaten
    hersteller = Column(String(100))
    seriennummer = Column(String(50))
    installiert_am = Column(DateTime(timezone=True))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    weighings = relationship("Wiegung", back_populates="waage", cascade="all, delete-orphan")


class Wiegung(Base):
    """
    Wiegung Model für Waagen-Wiegungen
    """
    __tablename__ = "ops_wiegungen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("WG"))
    
    # Fahrzeugdaten
    kennzeichen = Column(String(20), nullable=False)
    fahrer_name = Column(String(100))
    
    # Wägedaten
    artikel = Column(String(100), nullable=False)
    brutto = Column(Float, nullable=False)
    tara = Column(Float, nullable=False)
    netto = Column(Float, nullable=False)  # berechnet: brutto - tara
    
    # Referenzen
    chargennummer = Column(String(50))
    lieferant = Column(String(100))
    kunde = Column(String(100))
    
    # Zeitstempel
    zeitstempel = Column(DateTime(timezone=True), nullable=False)
    
    # Waage Reference
    waage_id = Column(String, ForeignKey("domain_ops.ops_waagen.id", ondelete="SET NULL"))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # Relationships
    waage = relationship("Waage", back_populates="weighings")


class Fahrzeug(Base):
    """
    Fahrzeug Model fuer Fuhrpark-Management
    """
    __tablename__ = "ops_fahrzeuge"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("F"))

    # Stammdaten (zvoove Fuhrpark)
    ro_nummer = Column(String(50))
    is_neu = Column(Boolean, default=False)
    betrieb = Column(String(120))
    bereich = Column(String(120))
    pol_kennzeichen = Column(String(30))
    kennzeichen = Column(String(20), nullable=False, unique=True)
    typ = Column(String(50), nullable=False)
    marke = Column(String(50))
    modell = Column(String(50))
    baujahr = Column(Integer)
    verwendung = Column(String(255))
    kfz_brief_nummer = Column(String(120))
    schadstoffgruppe = Column(String(80))
    leistung_kw = Column(Float)
    kraftstoff = Column(String(80))
    fahrgestellnummer = Column(String(120))
    erstzulassung = Column(DateTime(timezone=True))
    ausstattung = Column(Text)
    fahrtenschreiber_vorhanden = Column(Boolean, default=False)
    ahk_vorhanden = Column(Boolean, default=False)
    ladekran_vorhanden = Column(Boolean, default=False)
    fahrer_name = Column(String(120))
    fahrer_vorname = Column(String(120))

    # Kilometer / Sicht
    kilometerstand = Column(Float, default=0)
    km_stand_alle_eintraege = Column(Boolean, default=False)

    # Erwerb / Wirtschaft
    bestellnummer = Column(String(80))
    bestelldatum = Column(DateTime(timezone=True))
    haendler = Column(String(160))
    zustand = Column(String(20), default="neu")
    kaufsumme_eur = Column(DECIMAL(14, 2))
    kaufdatum = Column(DateTime(timezone=True))
    verkaufsdatum = Column(DateTime(timezone=True))
    kostenstelle = Column(String(80))
    abschreibungsart = Column(String(80))
    afa_jahre = Column(Integer)
    afa_eur_jaehrlich = Column(DECIMAL(14, 2))
    afa_eur_monatlich = Column(DECIMAL(14, 2))
    leasingdauer_monate = Column(Integer)
    leasinggesellschaft = Column(String(160))
    leasingrate_eur = Column(DECIMAL(14, 2))
    kfz_steuer_eur = Column(DECIMAL(14, 2))
    kfz_steuernummer = Column(String(80))
    kontierung = Column(String(80))
    finanzamt = Column(String(160))
    versicherungs_gesellschaft = Column(String(160))
    versicherungsschein_nr = Column(String(120))
    versicherung_satz_eur_monat = Column(DECIMAL(14, 2))
    versicherung_haftpflicht = Column(Boolean, default=False)
    versicherung_kasko = Column(Boolean, default=False)

    # Termine / Inspektion
    versicherung = Column(String(100))
    naechste_pruefung = Column(DateTime(timezone=True))
    naechster_tuev_termin = Column(DateTime(timezone=True))
    naechster_asu_termin = Column(DateTime(timezone=True))
    naechste_inspektion = Column(DateTime(timezone=True))
    letzte_inspektion = Column(DateTime(timezone=True))

    # Status
    status = Column(String(20), default=FahrzeugStatus.VERFUEGBAR.value)

    # Tank
    tank_groesse = Column(Float)
    aktueller_tank = Column(Float, default=0)

    # Zulassung
    zulassungsdatum = Column(DateTime(timezone=True))
    abmeldedatum = Column(DateTime(timezone=True))

    # Lasten / Extras
    leergewicht_kg = Column(Float)
    nutzlast_kg = Column(Float)
    gesamtgewicht_kg = Column(Float)
    anhaengerlast_kg = Column(Float)
    winterreifen_vorhanden = Column(Boolean, default=False)
    winterreifen_eingelagert = Column(Boolean, default=False)
    handy_freisprecheinrichtung = Column(Boolean, default=False)
    handy_fabrikat = Column(String(120))
    handy_rufnummer = Column(String(80))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))

    # Relationships
    fahrer = relationship("Fahrer", back_populates="fahrzeug", foreign_keys="Fahrer.aktuelles_fahrzeug_id")
    tours = relationship("FahrzeugTour", back_populates="fahrzeug", cascade="all, delete-orphan")


class Fahrer(Base):
    """
    Fahrer Model für Fuhrpark
    """
    __tablename__ = "ops_fahrer"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("DR"))
    
    # Stammdaten
    personalnummer = Column(String(20), unique=True)
    name = Column(String(100), nullable=False)
    vorname = Column(String(100))
    geburtsdatum = Column(DateTime(timezone=True))
    
    # Kontakt
    telefon = Column(String(50))
    email = Column(String(200))
    
    # Führerschein
    fuehrerschein = Column(String(10), nullable=False)  # B, C, CE, etc.
    fuehrerschein_gueltig_bis = Column(DateTime(timezone=True))
    
    # ADR-Bescheinigung
    adr_bescheinigung = Column(Boolean, default=False)
    adr_gueltig_bis = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default=FahrerStatus.VERFUEGBAR.value)
    
    # Aktuelles Fahrzeug
    aktuelles_fahrzeug_id = Column(String, ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL"))
    
    # Statistik
    touren_heute = Column(Integer, default=0)
    touren_woche = Column(Integer, default=0)
    kilometer_heute = Column(Float, default=0)
    
    # Verfügbarkeit
    verfuegbar_ab = Column(DateTime(timezone=True))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    fahrzeug = relationship("Fahrzeug", back_populates="fahrer")
    tours = relationship("FahrzeugTour", back_populates="fahrer", cascade="all, delete-orphan")


class FahrzeugTour(Base):
    """
    Fahrzeug Tour/Planung
    """
    __tablename__ = "ops_fahrzeug_touren"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("TOUR"))
    
    # Referenzen
    fahrzeug_id = Column(String, ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="CASCADE"))
    fahrer_id = Column(String, ForeignKey("domain_ops.ops_fahrer.id", ondelete="SET NULL"))
    
    # Tourdaten
    tour_nummer = Column(String(50))
    start_zeit = Column(DateTime(timezone=True), nullable=False)
    ende_zeit = Column(DateTime(timezone=True))
    
    # Route
    start_adresse = Column(Text)
    ziel_adresse = Column(Text)
    kilometer = Column(Float, default=0)
    
    # Status
    status = Column(String(20), default="geplant")  # geplant, aktiv, abgeschlossen, storniert
    
    # Ladung
    artikel = Column(String(100))
    menge = Column(Float)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # Relationships
    fahrzeug = relationship("Fahrzeug", back_populates="tours")
    fahrer = relationship("Fahrer", back_populates="tours")


class FuhrparkTerminart(Base):
    """
    Stammdaten fuer Terminarten im Fuhrpark.
    """
    __tablename__ = "ops_fuhrpark_terminarten"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("FTA"))
    terminart = Column(String(120), nullable=False, unique=True)
    intervall_monate = Column(Integer, nullable=False, default=0)
    intervall_km = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FuhrparkRechnung(Base):
    """
    Fuhrpark-Rechnungen fuer Kosten-/Auswertungsdialoge.
    """
    __tablename__ = "ops_fuhrpark_rechnungen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("FR"))
    rechnungs_nr = Column(String(80), nullable=False, unique=True)
    datum = Column(DateTime(timezone=True), nullable=False)
    fahrzeug_id = Column(String, ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL"))
    fahrzeug_kennzeichen = Column(String(30))
    sachkonto = Column(String(40))
    kostenart = Column(String(120))
    betrag_eur = Column(DECIMAL(14, 2), nullable=False, default=0)
    notiz = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    fahrzeug = relationship("Fahrzeug")


class FuhrparkAusgehendesDokument(Base):
    """
    Konfiguration ausgehender Belege/Dokumente (Druck- und Versandstrecke).
    """
    __tablename__ = "ops_fuhrpark_ausgehende_dokumente"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("FAD"))
    beleg_typ = Column(String(120), nullable=False)
    formular = Column(String(80))
    ziel_modul = Column(String(255))
    beschreibung = Column(Text)
    aktiv = Column(Boolean, nullable=False, default=True)
    letzter_druck = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SpeditionFrachttarif(Base):
    """
    PLZ-basierte Frachttarife fuer Speditionen (Streckengeschaeft).
    """
    __tablename__ = "strecke_speditionen_frachttarife"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("SFT"))
    plz_von = Column(String(10), nullable=False)
    plz_bis = Column(String(10), nullable=False)
    spediteur = Column(String(255), nullable=False)
    preis_eur_t = Column(DECIMAL(10, 4), nullable=False, default=0)
    aktiv = Column(Boolean, nullable=False, default=True)
    notiz = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))


# â"€â"€ DOKUMENTE MODELS â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€

class DokumentStatus(str, enum.Enum):
    """Dokument Status Enum"""
    AKTIV = "aktiv"
    GELOESCHT = "geloescht"
    ARCHIVIERT = "archiviert"


class DokumentKategorie(str, enum.Enum):
    """Dokument Kategorie Enum"""
    LIEFERSCHEINE = "Lieferscheine"
    RECHNUNGEN = "Rechnungen"
    QUALITAET = "Qualität"
    VERTRAG = "Verträge"
    ZERTIFIKATE = "Zertifikate"
    SONSTIGE = "Sonstige"


class Dokument(Base):
    """
    Dokument Model für Dokumentenverwaltung
    """
    __tablename__ = "ops_dokumente"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("DOC"))
    
    # Stammdaten
    name = Column(String(255), nullable=False)
    typ = Column(String(20), nullable=False)  # PDF, Excel, Word, etc.
    kategorie = Column(String(100), nullable=False)
    
    # Datei-Informationen
    groesse = Column(Integer, default=0)  # in KB
    speicherpfad = Column(String(500))  # Pfad im Dateisystem oder S3
    mime_type = Column(String(100))
    
    # Metadaten
    beschreibung = Column(Text)
    schlagwoerter = Column(String(500))  # Komma-getrennt
    version = Column(Integer, default=1)
    
    # Referenzen
    referenz_typ = Column(String(50))  # z.B. "Bestellung", "Kunde", "Artikel"
    referenz_id = Column(String(100))
    
    # Status
    status = Column(String(20), default=DokumentStatus.AKTIV.value)
    
    # Audit
    hochgeladen_am = Column(DateTime(timezone=True), server_default=func.now())
    hochgeladen_von = Column(String(100))
    geloescht_am = Column(DateTime(timezone=True))
    geloescht_von = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))


class DokumentVersion(Base):
    """
    Dokument Version Model für Versionierung
    """
    __tablename__ = "ops_dokument_versionen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("VER"))
    
    # Referenz
    dokument_id = Column(String, ForeignKey("domain_ops.ops_dokumente.id", ondelete="CASCADE"))
    
    # Versionsdaten
    version = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    groesse = Column(Integer, default=0)
    speicherpfad = Column(String(500))
    
    # Änderungen
    aenderungsbemerkung = Column(Text)
    
    # Audit
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    erstellt_von = Column(String(100))
    
    # Relationships
    dokument = relationship("Dokument", backref="versionen")


class ChargeStatus(str, enum.Enum):
    ERFASST = "erfasst"
    FREIGEGEBEN = "freigegeben"
    IN_PRUEFUNG = "in-pruefung"
    GESPERRT = "gesperrt"


class Charge(Base):
    """
    Charge/Lot model for lot tracking and release workflows.
    """
    __tablename__ = "ops_chargen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("CH"))
    chargen_id = Column(String(50), nullable=False, unique=True)
    losnummer = Column(String(50), nullable=True)
    artikel = Column(String(100), nullable=False)
    artikel_id = Column(String(100), nullable=False)
    produktbezeichnung = Column(String(255), nullable=True)
    menge = Column(Float, nullable=False)
    lagerort = Column(String(100), nullable=False)
    eingang = Column(DateTime(timezone=True), nullable=False)
    herstellungsdatum = Column(DateTime(timezone=True), nullable=True)
    mhd = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default=ChargeStatus.ERFASST.value)
    qualitaetsstatus = Column(String(30), default=ChargeStatus.IN_PRUEFUNG.value)
    freigabe_datum = Column(DateTime(timezone=True))
    herkunft = Column(String(255))
    bemerkungen = Column(Text)
    rueckverfolgbar_bis_stunden = Column(Integer, default=4)
    rohstoffe = Column(JSONB, nullable=True)  # [{name, menge, einheit, lieferant_id}]
    lieferant_info = Column(JSONB, nullable=True)  # {name, anschrift, qs_id, qs_lieferberechtigt}
    kunden_info = Column(JSONB, nullable=True)  # {name, anschrift, qs_id, vvvo}
    produktionsprozess = Column(JSONB, nullable=True)  # {reihenfolge, spuelchargen, mischzeiten, anlage}
    digitales_mischbuch = Column(JSONB, nullable=True)  # {eintraege:[...], signatur}
    haccp_system = Column(JSONB, nullable=True)  # {gefahrenanalyse, ccp, ueberwachung, korrekturen, verifizierung}
    eigenkontrollen = Column(JSONB, nullable=True)  # [{datum, art, ergebnis, massnahme}]
    warentrennung_qs_nicht_qs = Column(Boolean, default=False)
    krisenmanagement = Column(JSONB, nullable=True)  # {krisenmanager, ereignisfallblatt, rueckrufverfahren}
    futtermittelmonitoring = Column(JSONB, nullable=True)  # {proben, freigabepruefungen, oele_fette_teilnahme}
    qualitaetspersonal = Column(JSONB, nullable=True)  # {qualitaetsbeauftragter, schulungsplan, schulungsnachweise}
    qs_datenbank = Column(JSONB, nullable=True)  # {anlagen, stammdaten_sync, auditberichte, korrekturmassnahmen}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))


class BankKonto(Base):
    """
    Bank account model for operational finance views.
    """
    __tablename__ = "ops_bankkonten"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("BK"))
    iban = Column(String(50), nullable=False, unique=True)
    bic = Column(String(20), nullable=False)
    bank = Column(String(255), nullable=False)
    kontoart = Column(String(100), nullable=False)
    saldo = Column(DECIMAL(14, 2), default=0)
    waehrung = Column(String(10), default="EUR")
    status = Column(String(20), default="aktiv")
    ist_aktiv = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))


class Rahmenvertrag(Base):
    """
    Framework contract model used by contract management pages.
    """
    __tablename__ = "ops_rahmenvertraege"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("RV"))
    nummer = Column(String(50), nullable=False, unique=True)
    partner = Column(String(255), nullable=False)
    partner_id = Column(String(100), nullable=False)
    typ = Column(String(50), nullable=False)
    artikel = Column(String(100), nullable=False)
    artikel_id = Column(String(100), nullable=False)
    menge = Column(Float, nullable=False)
    restmenge = Column(Float, nullable=False)
    preis = Column(DECIMAL(14, 2), nullable=False)
    laufzeit_bis = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="aktiv")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))


class KonContract(Base):
    """Valeo Kontrakt-Kopf."""
    __tablename__ = "kon_contract"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    contract_id = Column(String, primary_key=True, default=uuid7)
    contract_no = Column(String(50), nullable=False, unique=True, index=True)
    contract_type = Column(String(20), nullable=False)  # EINKAUF|ZUKAUF|VERKAUF
    branch_id = Column(String(64), nullable=True)
    clerk_id = Column(String(64), nullable=True)
    party_id = Column(String(64), nullable=False, index=True)
    debitor_kto = Column(String(64), nullable=True)
    kreditor_kto = Column(String(64), nullable=True)
    contract_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_to = Column(DateTime(timezone=True), nullable=True)
    quantity_type = Column(String(20), nullable=False, default="GESAMTKONTRAKT")
    total_quantity = Column(DECIMAL(14, 3), nullable=False, default=0)
    unit = Column(String(20), nullable=False, default="kg")
    allow_overdelivery = Column(Boolean, nullable=False, default=False)
    status = Column(String(20), nullable=False, default="OFFEN")
    notes = Column(Text, nullable=True)
    payment_terms = Column(Text, nullable=True)
    conditions_json = Column(JSONB, nullable=True)

    # Preis-/Marktvorbereitung
    pricing_model = Column(String(30), nullable=True)
    min_price = Column(DECIMAL(14, 4), nullable=True)
    premium_type = Column(String(30), nullable=True)
    premium_value = Column(DECIMAL(14, 4), nullable=True)
    basis_reference = Column(String(120), nullable=True)
    pricing_window_from = Column(DateTime(timezone=True), nullable=True)
    pricing_window_to = Column(DateTime(timezone=True), nullable=True)

    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class KonContractLine(Base):
    """Valeo Kontrakt-Position."""
    __tablename__ = "kon_contract_line"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    line_id = Column(String, primary_key=True, default=uuid7)
    contract_id = Column(String, ForeignKey("domain_ops.kon_contract.contract_id", ondelete="CASCADE"), nullable=False, index=True)
    position_no = Column(Integer, nullable=False)
    article_id = Column(String(64), nullable=False, index=True)
    description1 = Column(String(255), nullable=True)
    description2 = Column(String(255), nullable=True)
    qty_contract = Column(DECIMAL(14, 3), nullable=False, default=0)
    price_unit = Column(String(20), nullable=True)
    unit_price = Column(DECIMAL(14, 4), nullable=True)
    discount_pct = Column(DECIMAL(8, 4), nullable=True)
    surcharge = Column(DECIMAL(14, 4), nullable=True)
    rebate_type = Column(String(30), nullable=True)
    is_bio = Column(Boolean, nullable=False, default=False)
    is_matif = Column(Boolean, nullable=False, default=False)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class KonContractMovement(Base):
    """Valeo Kontrakt-Umsatzbewegung."""
    __tablename__ = "kon_contract_movement"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    movement_id = Column(String, primary_key=True, default=uuid7)
    contract_id = Column(String, ForeignKey("domain_ops.kon_contract.contract_id", ondelete="CASCADE"), nullable=False, index=True)
    line_id = Column(String, ForeignKey("domain_ops.kon_contract_line.line_id", ondelete="SET NULL"), nullable=True, index=True)
    order_no = Column(String(64), nullable=True)
    delivery_note_no = Column(String(64), nullable=True)
    invoice_no = Column(String(64), nullable=True)
    movement_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    quantity = Column(DECIMAL(14, 3), nullable=False, default=0)
    unit_price = Column(DECIMAL(14, 4), nullable=True)
    route_no = Column(String(64), nullable=True)
    is_invoiced = Column(Boolean, nullable=False, default=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)


class KonAuditLog(Base):
    """Valeo Kontrakt-Auditlog."""
    __tablename__ = "kon_audit_log"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    audit_id = Column(String, primary_key=True, default=uuid7)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(64), nullable=False, index=True)
    field_name = Column(String(120), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    action = Column(String(30), nullable=False)
    changed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    changed_by = Column(String(100), nullable=True)
    tenant_id = Column(String, nullable=False, index=True)


class KonNumberRange(Base):
    """Nummernkreis für Kontrakte."""
    __tablename__ = "kon_number_range"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    contract_type = Column(String(20), nullable=False, index=True)
    branch_id = Column(String(64), nullable=True, index=True)
    prefix = Column(String(20), nullable=False, default="KON")
    next_number = Column(Integer, nullable=False, default=1)
    padding = Column(Integer, nullable=False, default=6)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    tenant_id = Column(String, nullable=False, index=True)


class PosPositionRule(Base):
    """Commodity Position Rule (No-Speculation Guard) pro Artikel/Gruppe."""
    __tablename__ = "pos_position_rule"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    rule_id = Column(String, primary_key=True, default=uuid7)
    scope_type = Column(String(20), nullable=False)  # ARTICLE | GROUP
    scope_id = Column(String(64), nullable=False)
    neg_tolerance_qty = Column(DECIMAL(14, 3), nullable=False, default=0)
    max_short_days = Column(Integer, nullable=False, default=0)
    yellow_threshold = Column(DECIMAL(14, 3), nullable=True)
    red_threshold = Column(DECIMAL(14, 3), nullable=True)
    approval_required = Column(Boolean, nullable=False, default=False)
    approval_role = Column(String(30), nullable=True)  # teamleiter | gf
    active_from = Column(DateTime(timezone=True), nullable=True)
    active_to = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class PosPositionOverride(Base):
    """Freigabe/Audit fuer Short-Override (Commodity Position)."""
    __tablename__ = "pos_position_override"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    override_id = Column(String, primary_key=True, default=uuid7)
    branch_id = Column(String(64), nullable=True)
    article_id = Column(String(64), nullable=False)
    period_key = Column(String(20), nullable=False)
    requested_by = Column(String(100), nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="REQUESTED")  # REQUESTED | APPROVED | REJECTED
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    comment = Column(Text, nullable=True)
    related_doc_type = Column(String(50), nullable=True)
    related_doc_id = Column(String(64), nullable=True)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PosPositionSnapshot(Base):
    """Optionaler Cache fuer Commodity Position Matrix (Performance)."""
    __tablename__ = "pos_position_snapshot"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    snapshot_id = Column(String, primary_key=True, default=uuid7)
    branch_id = Column(String(64), nullable=True)
    as_of_date = Column(Date, nullable=False)
    period_mode = Column(String(5), nullable=False)  # W | M | Q
    article_id = Column(String(64), nullable=False)
    period_key = Column(String(20), nullable=False)
    qty_buy_open = Column(DECIMAL(14, 3), nullable=False, default=0)
    qty_sell_open = Column(DECIMAL(14, 3), nullable=False, default=0)
    qty_net = Column(DECIMAL(14, 3), nullable=False, default=0)
    qty_tolerance = Column(DECIMAL(14, 3), nullable=True)
    severity = Column(String(10), nullable=True)  # GREEN | YELLOW | RED
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ComplianceEintrag(Base):
    __tablename__ = "ops_compliance_items"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("CMP"))
    bereich = Column(String(120), nullable=False)
    anforderung = Column(String(255), nullable=False)
    erfuellt = Column(Boolean, default=False)
    nachweis = Column(String(255), default="")
    frist = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ENNIMeldung(Base):
    __tablename__ = "ops_enni_meldungen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("ENNI"))
    typ = Column(String(20), nullable=False)
    betrieb = Column(String(255), nullable=False)
    vvvo = Column(String(50), nullable=False)
    datum = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="entwurf")
    naehrstoff_n = Column(Float, default=0)
    naehrstoff_p = Column(Float, default=0)
    naehrstoff_k = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class QSCheckEintrag(Base):
    __tablename__ = "ops_qs_checks"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("QS"))
    bereich = Column(String(120), nullable=False)
    pruefpunkt = Column(String(255), nullable=False)
    erfuellt = Column(Boolean, default=False)
    bemerkung = Column(String(500), default="")
    geprueft_am = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ZulassungRegister(Base):
    __tablename__ = "ops_zulassungen_register"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("ZUL"))
    produkt = Column(String(255), nullable=False)
    typ = Column(String(50), nullable=False)
    nummer = Column(String(80), nullable=False)
    behoerde = Column(String(120), nullable=False)
    gueltig_bis = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="aktiv")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SachkundeEintrag(Base):
    __tablename__ = "ops_sachkunde_register"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("SACH"))
    kunde = Column(String(255), nullable=False)
    kundennr = Column(String(80), nullable=False)
    nachweis_nr = Column(String(120), nullable=False)
    ausstellungsdatum = Column(DateTime(timezone=True), nullable=True)
    gueltig_bis = Column(DateTime(timezone=True), nullable=True)
    ausstellende_stelle = Column(String(255), nullable=True)
    status = Column(String(30), default="gueltig")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SaatgutNachbauEintrag(Base):
    __tablename__ = "ops_saatgut_nachbau"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("NACH"))
    betrieb = Column(String(255), nullable=False)
    sorte = Column(String(120), nullable=False)
    kultur = Column(String(120), nullable=False)
    flaeche = Column(Float, default=0)
    erntejahr = Column(Integer, nullable=False)
    gebuehr = Column(DECIMAL(14, 2), default=0)
    status = Column(String(30), default="offen")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VVVOEintrag(Base):
    __tablename__ = "ops_vvvo_register"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("VVVO"))
    betriebsname = Column(String(255), nullable=False)
    vvvo = Column(String(50), nullable=False)
    bundesland = Column(String(80), nullable=True)
    tierart = Column(String(120), nullable=True)
    status = Column(String(30), default="aktiv")
    letzte_aktualisierung = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DispositionPosition(Base):
    __tablename__ = "ops_disposition"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("DIS"))
    artikel = Column(String(255), nullable=False)
    artikel_id = Column(String(100), nullable=False)
    bestand = Column(Float, default=0)
    mindestbestand = Column(Float, default=0)
    bedarf = Column(Float, default=0)
    empfehlung = Column(String(255), default="")
    prioritaet = Column(String(20), default="niedrig")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FoerderAntrag(Base):
    __tablename__ = "ops_foerderantraege"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("FA"))
    nummer = Column(String(80), nullable=False)
    programm = Column(String(120), nullable=False)
    antragsdatum = Column(DateTime(timezone=True), nullable=True)
    flaeche = Column(Float, default=0)
    betrag = Column(DECIMAL(14, 2), default=0)
    status = Column(String(30), default="entwurf")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LaborProbe(Base):
    __tablename__ = "ops_labor_proben"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("LB"))
    probennummer = Column(String(80), nullable=False)
    typ = Column(String(80), nullable=False)
    artikel = Column(String(255), nullable=False)
    datum = Column(DateTime(timezone=True), nullable=True)
    labor = Column(String(255), nullable=False)
    status = Column(String(30), default="ausstehend")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LaborAuftragEntry(Base):
    __tablename__ = "ops_labor_auftraege"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("LA"))
    chargen_id = Column(String(80), nullable=False)
    labor = Column(String(255), nullable=False)
    analysen = Column(Integer, default=0)
    auftragsdatum = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="offen")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MarketingKampagneEntry(Base):
    __tablename__ = "ops_marketing_kampagnen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("MK"))
    name = Column(String(255), nullable=False)
    typ = Column(String(80), nullable=False)
    zielgruppe = Column(String(120), nullable=True)
    startdatum = Column(DateTime(timezone=True), nullable=True)
    enddatum = Column(DateTime(timezone=True), nullable=True)
    budget = Column(DECIMAL(14, 2), default=0)
    status = Column(String(30), default="geplant")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ZertifikatEintrag(Base):
    __tablename__ = "ops_zertifikate"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("ZERT"))
    art = Column(String(120), nullable=False)
    standard = Column(String(120), nullable=False)
    nummer = Column(String(120), nullable=False)
    gueltig_bis = Column(DateTime(timezone=True), nullable=True)
    audit = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default="gueltig")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PCNMeldung(Base):
    """PCN-Meldung (Product Classification Notification / UFI) gemäß EU-VO 2017/542."""

    __tablename__ = "ops_pcn_meldungen"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("PCN"))
    produktname = Column(String(255), nullable=False, default="")
    ufi = Column(String(24), nullable=True)
    cas_nummern = Column(String(500), nullable=True)
    gefahrenklassen = Column(JSONB, nullable=False, default=list)
    verwendungskategorie = Column(String(120), nullable=True)
    pcn_status = Column(String(30), nullable=False, default="entwurf")
    tenant_id = Column(String(120), nullable=False, default="default", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowSpineInstance(Base):
    """Persistente Flow-Spine-Prozessinstanz (Wave 104 — ersetzt In-Memory-Dict)."""

    __tablename__ = "ops_flow_spine_instances"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=_new_flow_spine_instance_id)
    case_number = Column(String(64), nullable=False, index=True)
    process_key = Column(String(120), nullable=False, index=True)
    label = Column(String(255), nullable=False, default="")
    customer_id = Column(String(120), nullable=True)
    customer_name = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=True)
    entry_mode = Column(String(80), nullable=True)
    linked_document_id = Column(String(120), nullable=True)
    linked_document_type = Column(String(80), nullable=True)
    lifecycle_status = Column(String(32), nullable=False, default="draft", index=True)
    business_status = Column(String(120), nullable=True)
    node_statuses = Column(JSONB, nullable=False, default=dict)
    active_node_id = Column(String(120), nullable=True)
    resume_node_id = Column(String(120), nullable=True)
    resume_route = Column(String(255), nullable=True)
    resume_payload = Column(JSONB, nullable=False, default=dict)
    assigned_owner = Column(String(120), nullable=True)
    last_actor = Column(String(120), nullable=True)
    last_action_label = Column(String(255), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    blocked_until = Column(DateTime(timezone=True), nullable=True)
    completion_reason_code = Column(String(120), nullable=True)
    cancellation_reason_category = Column(String(80), nullable=True)
    cancellation_reason_code = Column(String(120), nullable=True)
    failure_reason_category = Column(String(80), nullable=True)
    failure_reason_code = Column(String(120), nullable=True)
    reason_note = Column(Text, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(String(120), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(String(120), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    failed_by = Column(String(120), nullable=True)
    version_no = Column(Integer, nullable=False, default=1)
    tenant_id = Column(String(120), nullable=False, default="default", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowSpineInstanceEvent(Base):
    """Timeline- und Auditspur fuer Flow-Spine-Instanzen."""

    __tablename__ = "ops_flow_spine_instance_events"
    __table_args__ = {"schema": "domain_ops", "extend_existing": True}

    id = Column(String, primary_key=True, default=_new_flow_spine_event_id)
    instance_id = Column(
        String(36),
        ForeignKey("domain_ops.ops_flow_spine_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    process_key = Column(String(120), nullable=False, index=True)
    tenant_id = Column(String(120), nullable=False, default="default", index=True)
    event_type = Column(String(60), nullable=False, index=True)
    from_lifecycle_status = Column(String(32), nullable=True)
    to_lifecycle_status = Column(String(32), nullable=True)
    from_business_status = Column(String(120), nullable=True)
    to_business_status = Column(String(120), nullable=True)
    node_id = Column(String(120), nullable=True)
    actor_id = Column(String(120), nullable=True)
    reason_category = Column(String(80), nullable=True)
    reason_code = Column(String(120), nullable=True)
    reason_note = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

