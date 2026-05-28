"""Auto-generated domain schemas for einkauf bestellvorschlag."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class EinkaufBestellvorschlagOut(BaseSchema):
    """Response schema for einkauf bestellvorschlag endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class BestellvorschlagOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class LieferantCreate(BaseModel):
    lieferantennummer: str
    firmenname: str
    partner_id: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    fax: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: str = "Deutschland"
    steuernummer: Optional[str] = None
    ust_id: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    zahlungsziel_tage: Optional[int] = None
    skonto_prozent: Optional[float] = None
    lieferzeit_tage: Optional[int] = None
    mindestbestellwert: Optional[float] = None
    bewertung: Optional[int] = None
    edi_kennung: Optional[str] = None
    edi_format: Optional[str] = None
    email_bestellung: Optional[str] = None
    fax_bestellung: Optional[str] = None
    notiz: Optional[str] = None


class LieferantUpdate(LieferantCreate):
    lieferantennummer: Optional[str] = None  # type: ignore[assignment]
    firmenname: Optional[str] = None          # type: ignore[assignment]


class KontraktCreate(BaseModel):
    kontraktnummer: str
    lieferant_id: str
    bezeichnung: Optional[str] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    status: str = "aktiv"
    kontrakt_typ: str = "rahmen"
    waehrung: str = "EUR"
    gesamtmenge: Optional[float] = None
    niederlassung_id: Optional[str] = None
    notiz: Optional[str] = None


class KontraktPosCreate(BaseModel):
    pos_nr: int
    article_id: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    menge: float
    einheit: Optional[str] = None
    preis: Optional[float] = None
    preis_einheit: str = "100kg"
    preisbindung: str = "fix"
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    notiz: Optional[str] = None


class ArtikelLagerParamCreate(BaseModel):
    article_id: str
    warehouse_id: Optional[str] = None
    niederlassung_id: Optional[str] = None
    mindestbestand: float = 0.0
    maximalbestand: Optional[float] = None
    meldebestand: float = 0.0
    soll_bestand: Optional[float] = None
    std_lieferant_id: Optional[str] = None
    std_bestellmenge: Optional[float] = None
    std_einheit: Optional[str] = None
    wiederbeschaffungs_tage: int = 3
    durchschnitt_verbrauch_tag: Optional[float] = None
    notiz: Optional[str] = None


class ArtikelLagerParamUpdate(ArtikelLagerParamCreate):
    article_id: Optional[str] = None  # type: ignore[assignment]


class VorschlagSaveRequest(BaseModel):
    vorschlag_typ: str  # lager | verkauf | rohware
    positionen: list[dict[str, Any]]
    parameter: Optional[dict[str, Any]] = None
    niederlassung_id: Optional[str] = None
    bezeichnung: Optional[str] = None


class BestellungCreate(BaseModel):
    lieferant_id: str
    bestelldatum: date
    niederlassung_id: Optional[str] = None
    lieferdatum_wunsch: Optional[date] = None
    versand_art: str = "email"
    kontrakt_id: Optional[str] = None
    unsere_referenz: Optional[str] = None
    ihre_referenz: Optional[str] = None
    freitext_kopf: Optional[str] = None
    freitext_fuss: Optional[str] = None
    notiz: Optional[str] = None
    positionen: list[dict[str, Any]] = []


class LagerKontenzuordnungCreate(BaseModel):
    artikelgruppe: str
    niederlassung_id: Optional[str] = None
    bestandskonto: str
    gegenkonto_zugang: Optional[str] = None
    gegenkonto_abgang: Optional[str] = None
    paletten_konto: Optional[str] = None
    pfand_konto: Optional[str] = None
    fremdwaren_konto: Optional[str] = None
    einlagerung_konto: Optional[str] = None
    chargen_konto: Optional[str] = None
    ust_schluessel: Optional[str] = None
    notiz: Optional[str] = None


class PalettenBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    paletten_typ: str = "EUR-Palette"
    menge: int
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class PfandBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    gebinde_typ: str
    menge: float
    pfandwert_je_einheit: Optional[float] = None
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class FremdwarenCreate(BaseModel):
    einlagerungs_nr: str
    eigentuemer_id: str
    eigentuemer_name: Optional[str] = None
    niederlassung_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    lagerort: Optional[str] = None
    article_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    charge: Optional[str] = None
    einlagerungstyp: str = "fremdware"
    menge_eingelagert: float
    einheit: Optional[str] = None
    einlagerungsdatum: date
    geplante_auslagerung: Optional[date] = None
    gebuehr_pro_tag: Optional[float] = None
    gebuehr_einheit: str = "t"
    notiz: Optional[str] = None

