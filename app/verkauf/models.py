"""
SQLAlchemy Models für Verkauf
"""

from sqlalchemy import Column, String, Boolean, Text, Integer, DECIMAL, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Kunde(Base):
    """Kundenstamm Haupttabelle"""
    __tablename__ = "kunden"
    
    kunden_nr = Column(String(20), primary_key=True)
    name1 = Column(String(100), nullable=False)
    name2 = Column(String(100))
    name3 = Column(String(100))
    strasse = Column(String(100))
    plz = Column(String(10))
    ort = Column(String(100))
    land = Column(String(100))
    postfach = Column(String(10))
    postfach_plz = Column(String(10))
    postfach_ort = Column(String(100))
    tel = Column(String(50))
    fax = Column(String(50))
    email = Column(String(100))
    homepage = Column(String(200))
    
    # Rechnung/Kontoauszug
    kontonutzung_rechnung = Column(Boolean, default=False)
    kontoauszug_gewuenscht = Column(Boolean, default=False)
    saldo_druck_rechnung = Column(Boolean, default=False)
    druck_verbot_rechnung = Column(Boolean, default=False)
    druck_werbetext = Column(Boolean, default=False)
    versandpauschalen_berechnen = Column(Boolean, default=False)
    einzel_abrechnung = Column(String(20))
    sammel_abrechnung = Column(Boolean, default=False)
    sammel_abrechnung_ohne_einzel = Column(Boolean, default=False)
    sammel_abrechnungskennzeichen = Column(String(50))
    bonus_berechtigung = Column(Boolean, default=False)
    bonus_rechnungsempfaenger_id = Column(String(20), ForeignKey("kunden.kunden_nr"))
    bemerkenswerte_forderung = Column(Boolean, default=False)
    selbstabrechnung_durch_kunden = Column(Boolean, default=False)
    selbstabrechner_verkauf_zukauf = Column(String(50))
    kunden_zusatz = Column(Text)
    
    # Preise / Rabatte
    direktes_konto = Column(Boolean, default=False)
    rabatt_verrechnung = Column(String(20))
    selbstabholer_rabatt = Column(DECIMAL(5, 2), default=0)
    preisermittlung_sorten = Column(Boolean, default=False)
    direktabzug = Column(Boolean, default=False)
    wochenpreis_ec_basis = Column(Boolean, default=False)
    gueltig_ab = Column(Date)
    gueltig_bis = Column(Date)
    
    # Bank / Zahlungsverkehr
    zahlungsbedingungen_tage = Column(Integer)
    skonto = Column(DECIMAL(5, 2), default=0)
    netto_kasse = Column(Boolean, default=False)
    mahnwesen = Column(Boolean, default=False)
    lastschriftverfahren = Column(String(20))
    sepa_verfahren = Column(Boolean, default=False)
    mandat = Column(Boolean, default=False)
    bank = Column(String(200))
    iban = Column(String(34))
    bic = Column(String(11))
    umrechnung_euro = Column(Boolean, default=False)
    umrechnungskurs = Column(DECIMAL(10, 4))
    waehrung = Column(String(3), default='EUR')
    zinstabelle_id = Column(Integer, ForeignKey("zinstabellen.id"))
    letzter_zinstermin = Column(Date)
    saldo_letzte_zinsabrechnung = Column(DECIMAL(12, 2), default=0)
    verrechnung_automatisch = Column(Boolean, default=False)
    
    # Wegbeschreibung
    lade_information = Column(Text)
    allgemeine_angaben = Column(Text)
    
    # Sonstiges
    nachkalkulation = Column(Boolean, default=False)
    formular_id = Column(Integer, ForeignKey("formulare.id"))
    offene_posten_nicht_aufrufen = Column(Boolean, default=False)
    versicherung = Column(Boolean, default=False)
    sprachschluessel = Column(String(2), default='DE')
    statistik_kennzeichen = Column(String(50))
    landwirtschaftsamt_betriebsnummer = Column(String(50))
    marktpreis_auswertung = Column(Boolean, default=False)
    schwellenwert = Column(DECIMAL(12, 2), default=0)
    webshop_kunde = Column(Boolean, default=False)
    
    # Selektionen
    selektion_schluessel = Column(String(50))
    selektion_berechnung = Column(Text)
    
    # Schnittstelle
    tankkarte_ean_code = Column(String(50))
    kundenkarten_kennzeichen = Column(String(50))
    edifact_invoic = Column(Boolean, default=False)
    edifact_orders = Column(Boolean, default=False)
    edifact_desadv = Column(Boolean, default=False)
    rechnungs_sammeldruck = Column(Boolean, default=False)
    webshop_kunden_nr = Column(String(50))
    webshop_bezeichnung = Column(String(200))
    
    # Metadaten
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    geloescht = Column(Boolean, default=False)
    
    # Relations
    ansprechpartner = relationship("KundenAnsprechpartner", back_populates="kunde", cascade="all, delete-orphan")
    profil = relationship("KundenProfil", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    versand = relationship("KundenVersand", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    lieferung_zahlung = relationship("KundenLieferungZahlung", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    datenschutz = relationship("KundenDatenschutz", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    genossenschaft = relationship("KundenGenossenschaft", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    freitext = relationship("KundenFreitext", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    allgemein_erweitert = relationship("KundenAllgemeinErweitert", back_populates="kunde", uselist=False, cascade="all, delete-orphan")
    email_verteiler = relationship("KundenEmailVerteiler", back_populates="kunde", cascade="all, delete-orphan")
    betriebs_gemeinschaften = relationship(
        "KundenBetriebsgemeinschaft",
        back_populates="kunde",
        cascade="all, delete-orphan",
        primaryjoin="Kunde.kunden_nr==KundenBetriebsgemeinschaft.kunden_nr",
        foreign_keys="KundenBetriebsgemeinschaft.kunden_nr",
    )
    cpd_konten = relationship("KundenCpdKonto", back_populates="kunde", cascade="all, delete-orphan")
    rabatt_details = relationship("KundenRabatteDetail", back_populates="kunde", cascade="all, delete-orphan")
    preis_details = relationship("KundenPreiseDetail", back_populates="kunde", cascade="all, delete-orphan")


class KundenAnsprechpartner(Base):
    """Ansprechpartner (mehrfach)"""
    __tablename__ = "kunden_ansprechpartner"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    prioritaet = Column(Integer, default=0)
    vorname = Column(String(100))
    nachname = Column(String(100))
    position = Column(String(100))
    abteilung = Column(String(100))
    telefon1 = Column(String(50))
    telefon2 = Column(String(50))
    mobil = Column(String(50))
    email = Column(String(100))
    strasse = Column(String(100))
    plz = Column(String(10))
    ort = Column(String(100))
    anrede = Column(String(20))
    briefanrede = Column(String(50))
    geburtsdatum = Column(Date)
    hobbys = Column(Text)
    info1 = Column(Text)
    info2 = Column(Text)
    empfanger_rechnung_email = Column(Boolean, default=False)
    empfanger_mahnung_email = Column(Boolean, default=False)
    kontaktart = Column(String(50))
    erstanlage = Column(Date)
    cad_system = Column(String(100))
    softwaresysteme = Column(String(200))
    datenschutzbeauftragter = Column(Boolean, default=False)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="ansprechpartner")


class KundenProfil(Base):
    """Kundenprofil"""
    __tablename__ = "kunden_profil"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    firmenname = Column(String(200))
    gruendung = Column(Date)
    jahresumsatz = Column(DECIMAL(15, 2))
    berufsgenossenschaft = Column(String(100))
    berufsgen_nr = Column(String(50))
    branche = Column(String(100))
    mitbewerber = Column(String(200))
    engpaesse = Column(Text)
    organisationsstruktur = Column(Text)
    mitarbeiteranzahl = Column(Integer)
    wettbewerbsdifferenzierung = Column(Text)
    betriebsrat = Column(Boolean, default=False)
    unternehmensphilosophie = Column(Text)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="profil")


class KundenVersand(Base):
    """Versandinformationen"""
    __tablename__ = "kunden_versand"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    versandart_rechnung = Column(String(50))
    versandart_mahnung = Column(String(50))
    versandart_kontakt = Column(String(50))
    dispo_nummer = Column(String(50))
    initialisierungsweisung = Column(Text)
    versandmedium = Column(String(50))
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="versand")


class KundenLieferungZahlung(Base):
    """Lieferung/Zahlung"""
    __tablename__ = "kunden_lieferung_zahlung"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    lieferbedingung = Column(String(100))
    zahlungsbedingung = Column(String(100))
    faelligkeit_ab = Column(String(50))
    pro_forma_rechnung = Column(Boolean, default=False)
    pro_forma_rabatt1 = Column(DECIMAL(5, 2))
    pro_forma_rabatt2 = Column(DECIMAL(5, 2))
    einzel_sammelversand_avis = Column(String(50))
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="lieferung_zahlung")


class KundenDatenschutz(Base):
    """Datenschutz"""
    __tablename__ = "kunden_datenschutz"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    einwilligung = Column(Boolean, default=False)
    anlagedatum = Column(Date)
    anlagebearbeiter = Column(String(100))
    zusatzbemerkung = Column(Text)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="datenschutz")


class KundenGenossenschaft(Base):
    """Genossenschaftsanteile"""
    __tablename__ = "kunden_genossenschaft"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    geschaeftsguthaben_konto = Column(String(50))
    mitgliedschaft_gekuendigt = Column(Boolean, default=False)
    kuendigungsgrund = Column(Text)
    datum_kuendigung = Column(Date)
    datum_austritt = Column(Date)
    mitgliedsnummer = Column(String(50))
    pflichtanteile = Column(Integer, default=0)
    eintrittsdatum = Column(Date)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="genossenschaft")


class KundenFreitext(Base):
    """Freitext & Anweisungen"""
    __tablename__ = "kunden_freitext"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    chef_anweisung = Column(Text)
    langtext = Column(Text)
    bemerkungen = Column(Text)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="freitext")


class KundenAllgemeinErweitert(Base):
    """Allgemein Erweitert"""
    __tablename__ = "kunden_allgemein_erweitert"
    
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), primary_key=True)
    staat = Column(String(100))
    bundesland = Column(String(100))
    kunde_seit = Column(Date)
    debitoren_konto = Column(String(50))
    deb_kto_hauptkonto = Column(String(50))
    disponent = Column(String(100))
    vertriebsbeauftragter = Column(String(100))
    abc_umsatzstatus = Column(String(50))
    betriebsnummer = Column(String(50))
    ust_id_nr = Column(String(50))
    steuernummer = Column(String(50))
    sperrgrund = Column(Text)
    kundengruppe = Column(String(100))
    fax_sperre = Column(Boolean, default=False)
    infofeld4 = Column(Text)
    infofeld5 = Column(Text)
    infofeld6 = Column(Text)
    erstellt_am = Column(DateTime)
    geaendert_am = Column(DateTime)
    
    kunde = relationship("Kunde", back_populates="allgemein_erweitert")


class KundenEmailVerteiler(Base):
    """E-Mail Verteiler"""
    __tablename__ = "kunden_email_verteiler"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    verteilername = Column(String(100))
    bezeichnung = Column(String(200))
    email = Column(String(100))
    erstellt_am = Column(DateTime)

    kunde = relationship("Kunde", back_populates="email_verteiler")


class KundenBetriebsgemeinschaft(Base):
    """Betriebsgemeinschaften"""
    __tablename__ = "kunden_betriebsgemeinschaften"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    verbundnummer = Column(String(50))
    mitglieder_kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"))
    anteil_prozent = Column(DECIMAL(5, 2))
    erstellt_am = Column(DateTime)

    kunde = relationship("Kunde", back_populates="betriebs_gemeinschaften", foreign_keys=[kunden_nr])
    mitglied = relationship("Kunde", foreign_keys=[mitglieder_kunden_nr], viewonly=True)


class KundenCpdKonto(Base):
    """CPD Konten"""
    __tablename__ = "kunden_cpd_konto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    debitoren_konto = Column(String(50))
    suchbegriff = Column(String(100))
    rechnungsadresse = Column(Text)
    geschaeftsstelle = Column(String(100))
    kostenstelle = Column(String(100))
    rechnungsart = Column(String(50))
    sammelrechnung = Column(Boolean, default=False)
    rechnungsformular = Column(String(100))
    vb = Column(String(100))
    gebiet = Column(String(100))
    zahlungsbedingungen = Column(Text)
    erstellt_am = Column(DateTime)

    kunde = relationship("Kunde", back_populates="cpd_konten")


class KundenRabatteDetail(Base):
    """Kundenrabatte (Detail)"""
    __tablename__ = "kunden_rabatte_detail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    artikel_nr = Column(String(50))
    bezeichnung = Column(String(200))
    rabatt = Column(DECIMAL(5, 2))
    rabatt_gueltig_bis = Column(Date)
    rabatt_liste_id = Column(Integer, ForeignKey("rabatt_listen.id"))
    erstellt_am = Column(DateTime)

    kunde = relationship("Kunde", back_populates="rabatt_details")


class KundenPreiseDetail(Base):
    """Kundenpreise (Detail)"""
    __tablename__ = "kunden_preise_detail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kunden_nr = Column(String(20), ForeignKey("kunden.kunden_nr"), nullable=False)
    artikel_nr = Column(String(50))
    bezeichnung = Column(String(200))
    preis_netto = Column(DECIMAL(10, 2))
    preis_inkl_fracht = Column(DECIMAL(10, 2))
    preis_einheit = Column(String(20))
    rabatt_erlaubt = Column(Boolean, default=True)
    sonderfracht = Column(DECIMAL(10, 2))
    zahlungsbedingung = Column(String(100))
    gueltig_bis = Column(Date)
    bediener = Column(String(100))
    erstellt_am = Column(DateTime)

    kunde = relationship("Kunde", back_populates="preis_details")

