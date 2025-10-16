"""
Agrar Domain Schemas
Pydantic schemas for Saatgut, Dünger, PSM, and other agricultural products
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import Field, validator

from .base import BaseSchema, TimestampMixin, SoftDeleteMixin


# Saatgut Schemas
class SaatgutBase(BaseSchema):
    """Base Saatgut schema"""
    artikelnummer: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    sorte: str = Field(..., min_length=1, max_length=100, description="Variety")
    art: str = Field(..., min_length=1, max_length=50, description="Type (Weizen, Gerste, etc.)")
    zuechter: Optional[str] = Field(None, max_length=100, description="Breeder")
    zulassungsnummer: Optional[str] = Field(None, max_length=50, description="Approval number")
    bsa_zulassung: bool = Field(default=False, description="BSA approval")
    eu_zulassung: bool = Field(default=False, description="EU approval")
    ablauf_zulassung: Optional[datetime] = Field(None, description="Approval expiry date")

    # Agronomische Daten
    tkm: Optional[Decimal] = Field(None, ge=0, description="Thousand grain mass")
    keimfaehigkeit: Optional[Decimal] = Field(None, ge=0, le=100, description="Germination capacity %")
    aussaatstaerke: Optional[Decimal] = Field(None, ge=0, description="Sowing strength kg/ha")

    # Preise und Konditionen
    ek_preis: Optional[Decimal] = Field(None, ge=0, description="Purchase price")
    vk_preis: Optional[Decimal] = Field(None, ge=0, description="Sales price")
    waehrung: str = Field(default="EUR", max_length=3, description="Currency")
    mindestabnahme: Optional[Decimal] = Field(None, ge=0, description="Minimum order quantity")

    # Lager
    lagerbestand: Decimal = Field(default=0, ge=0, description="Stock quantity")
    reserviert: Decimal = Field(default=0, ge=0, description="Reserved quantity")
    verfuegbar: Decimal = Field(default=0, ge=0, description="Available quantity")
    lagerort: Optional[str] = Field(None, max_length=100, description="Storage location")


class SaatgutCreate(SaatgutBase):
    """Schema for creating Saatgut"""
    tenant_id: str = Field(..., description="Tenant ID")


class SaatgutUpdate(BaseSchema):
    """Schema for updating Saatgut"""
    artikelnummer: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sorte: Optional[str] = Field(None, min_length=1, max_length=100)
    art: Optional[str] = Field(None, min_length=1, max_length=50)
    zuechter: Optional[str] = Field(None, max_length=100)
    zulassungsnummer: Optional[str] = Field(None, max_length=50)
    bsa_zulassung: Optional[bool] = Field(None)
    eu_zulassung: Optional[bool] = Field(None)
    ablauf_zulassung: Optional[datetime] = Field(None)
    tkm: Optional[Decimal] = Field(None, ge=0)
    keimfaehigkeit: Optional[Decimal] = Field(None, ge=0, le=100)
    aussaatstaerke: Optional[Decimal] = Field(None, ge=0)
    ek_preis: Optional[Decimal] = Field(None, ge=0)
    vk_preis: Optional[Decimal] = Field(None, ge=0)
    waehrung: Optional[str] = Field(None, max_length=3)
    mindestabnahme: Optional[Decimal] = Field(None, ge=0)
    lagerbestand: Optional[Decimal] = Field(None, ge=0)
    reserviert: Optional[Decimal] = Field(None, ge=0)
    verfuegbar: Optional[Decimal] = Field(None, ge=0)
    lagerort: Optional[str] = Field(None, max_length=100)
    ist_aktiv: Optional[bool] = Field(None)


class Saatgut(SaatgutBase, TimestampMixin, SoftDeleteMixin):
    """Full Saatgut schema"""
    id: str = Field(..., description="Saatgut ID")
    tenant_id: str = Field(..., description="Tenant ID")


class SaatgutLizenzBase(BaseSchema):
    """Base Saatgut-Lizenz schema"""
    saatgut_id: str = Field(..., description="Saatgut ID")
    typ: str = Field(..., min_length=1, max_length=50, description="License type")
    saison: str = Field(..., min_length=9, max_length=9, description="Season (YYYY/YYYY)")
    gebuehr_pro_tonne: Optional[Decimal] = Field(None, ge=0, description="Fee per tonne")
    gesamt_gebuehr: Optional[Decimal] = Field(None, ge=0, description="Total fee")


class SaatgutLizenzCreate(SaatgutLizenzBase):
    """Schema for creating Saatgut-Lizenz"""
    tenant_id: str = Field(..., description="Tenant ID")


class SaatgutLizenz(SaatgutLizenzBase, TimestampMixin):
    """Full Saatgut-Lizenz schema"""
    id: str = Field(..., description="License ID")
    tenant_id: str = Field(..., description="Tenant ID")
    bezahlt: bool = Field(default=False, description="Payment status")
    bezahlt_am: Optional[datetime] = Field(None, description="Payment date")


# Dünger Schemas
class DuengerBase(BaseSchema):
    """Base Dünger schema"""
    artikelnummer: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    typ: str = Field(..., min_length=1, max_length=50, description="Type (Mineraldünger, Organisch, etc.)")
    hersteller: Optional[str] = Field(None, max_length=100, description="Manufacturer")

    # Inhaltsstoffe (NPK)
    n_gehalt: Optional[Decimal] = Field(None, ge=0, le=100, description="Nitrogen content %")
    p_gehalt: Optional[Decimal] = Field(None, ge=0, le=100, description="Phosphorus content %")
    k_gehalt: Optional[Decimal] = Field(None, ge=0, le=100, description="Potassium content %")
    s_gehalt: Optional[Decimal] = Field(None, ge=0, le=100, description="Sulfur content %")
    mg_gehalt: Optional[Decimal] = Field(None, ge=0, le=100, description="Magnesium content %")

    # Zulassungen
    dmv_nummer: Optional[str] = Field(None, max_length=50, description="DüMV number")
    eu_zulassung: Optional[str] = Field(None, max_length=50, description="EU approval")
    ablauf_zulassung: Optional[datetime] = Field(None, description="Approval expiry")

    # Sicherheit
    gefahrstoff_klasse: Optional[str] = Field(None, max_length=10, description="Hazard class")
    wassergefaehrdend: bool = Field(default=False, description="Water hazardous")
    lagerklasse: Optional[str] = Field(None, max_length=10, description="Storage class")

    # Anwendung
    kultur_typ: Optional[str] = Field(None, max_length=100, description="Crop type")
    dosierung_min: Optional[Decimal] = Field(None, ge=0, description="Min dosage kg/ha")
    dosierung_max: Optional[Decimal] = Field(None, ge=0, description="Max dosage kg/ha")
    zeitpunkt: Optional[str] = Field(None, max_length=100, description="Application time")

    # Preise und Lager
    ek_preis: Optional[Decimal] = Field(None, ge=0, description="Purchase price")
    vk_preis: Optional[Decimal] = Field(None, ge=0, description="Sales price")
    waehrung: str = Field(default="EUR", max_length=3, description="Currency")
    lagerbestand: Decimal = Field(default=0, ge=0, description="Stock quantity")


class DuengerCreate(DuengerBase):
    """Schema for creating Dünger"""
    tenant_id: str = Field(..., description="Tenant ID")


class DuengerUpdate(BaseSchema):
    """Schema for updating Dünger"""
    artikelnummer: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    typ: Optional[str] = Field(None, min_length=1, max_length=50)
    hersteller: Optional[str] = Field(None, max_length=100)
    n_gehalt: Optional[Decimal] = Field(None, ge=0, le=100)
    p_gehalt: Optional[Decimal] = Field(None, ge=0, le=100)
    k_gehalt: Optional[Decimal] = Field(None, ge=0, le=100)
    s_gehalt: Optional[Decimal] = Field(None, ge=0, le=100)
    mg_gehalt: Optional[Decimal] = Field(None, ge=0, le=100)
    dmv_nummer: Optional[str] = Field(None, max_length=50)
    eu_zulassung: Optional[str] = Field(None, max_length=50)
    ablauf_zulassung: Optional[datetime] = Field(None)
    gefahrstoff_klasse: Optional[str] = Field(None, max_length=10)
    wassergefaehrdend: Optional[bool] = Field(None)
    lagerklasse: Optional[str] = Field(None, max_length=10)
    kultur_typ: Optional[str] = Field(None, max_length=100)
    dosierung_min: Optional[Decimal] = Field(None, ge=0)
    dosierung_max: Optional[Decimal] = Field(None, ge=0)
    zeitpunkt: Optional[str] = Field(None, max_length=100)
    ek_preis: Optional[Decimal] = Field(None, ge=0)
    vk_preis: Optional[Decimal] = Field(None, ge=0)
    waehrung: Optional[str] = Field(None, max_length=3)
    lagerbestand: Optional[Decimal] = Field(None, ge=0)
    ist_aktiv: Optional[bool] = Field(None)


class Duenger(DuengerBase, TimestampMixin, SoftDeleteMixin):
    """Full Dünger schema"""
    id: str = Field(..., description="Dünger ID")
    tenant_id: str = Field(..., description="Tenant ID")


class DuengerMischungBase(BaseSchema):
    """Base Dünger-Mischung schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Mixture name")
    beschreibung: Optional[str] = Field(None, description="Description")
    komponenten: List[Dict[str, Any]] = Field(default_factory=list, description="Components list")
    kosten_pro_tonne: Optional[Decimal] = Field(None, ge=0, description="Cost per tonne")


class DuengerMischungCreate(DuengerMischungBase):
    """Schema for creating Dünger-Mischung"""
    tenant_id: str = Field(..., description="Tenant ID")


class DuengerMischungUpdate(BaseSchema):
    """Schema for updating Dünger-Mischung"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    beschreibung: Optional[str] = Field(None)
    komponenten: Optional[List[Dict[str, Any]]] = Field(None)
    kosten_pro_tonne: Optional[Decimal] = Field(None, ge=0)
    ist_aktiv: Optional[bool] = Field(None)
    freigegeben: Optional[bool] = Field(None)


class DuengerMischung(DuengerMischungBase, TimestampMixin):
    """Full Dünger-Mischung schema"""
    id: str = Field(..., description="Mixture ID")
    tenant_id: str = Field(..., description="Tenant ID")
    gesamt_n: Optional[Decimal] = Field(None, ge=0, description="Total N %")
    gesamt_p: Optional[Decimal] = Field(None, ge=0, description="Total P %")
    gesamt_k: Optional[Decimal] = Field(None, ge=0, description="Total K %")
    ist_aktiv: bool = Field(default=True, description="Active status")
    freigegeben: bool = Field(default=False, description="Approved status")
    freigegeben_am: Optional[datetime] = Field(None, description="Approval date")
    freigegeben_durch: Optional[str] = Field(None, description="Approved by")


# PSM Schemas
class PSMBase(BaseSchema):
    """Base PSM schema"""
    artikelnummer: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    wirkstoff: str = Field(..., min_length=1, max_length=100, description="Active ingredient")
    mittel_typ: str = Field(..., min_length=1, max_length=50, description="Product type")

    # Zulassung
    bvl_nummer: str = Field(..., min_length=1, max_length=50, description="BVL number")
    zulassung_ablauf: datetime = Field(..., description="Approval expiry")
    eu_zulassung: bool = Field(default=False, description="EU approval")

    # Anwendung
    kulturen: List[str] = Field(default_factory=list, description="Applicable crops")
    indikationen: List[str] = Field(default_factory=list, description="Indications")
    dosierung_min: Optional[Decimal] = Field(None, ge=0, description="Min dosage")
    dosierung_max: Optional[Decimal] = Field(None, ge=0, description="Max dosage")
    wartezeit: Optional[int] = Field(None, ge=0, description="Waiting period days")

    # Sicherheit und Auflagen
    bienenschutz: bool = Field(default=False, description="Bee protection")
    wasserschutz_gebiet: bool = Field(default=False, description="Water protection area")
    abstand_wohngebaeude: Optional[int] = Field(None, ge=0, description="Distance to buildings m")
    abstand_gewaesser: Optional[int] = Field(None, ge=0, description="Distance to water m")
    auflagen: List[str] = Field(default_factory=list, description="Restrictions")

    # Erklärung des Landwirts (für Ausgangsstoffe für Explosivstoffe)
    ausgangsstoff_explosivstoffe: bool = Field(default=False, description="Contains explosive precursors")
    erklaerung_landwirt_erforderlich: bool = Field(default=False, description="Farmer's declaration required")
    erklaerung_landwirt_status: Optional[str] = Field(None, max_length=20, description="Declaration status")

    # Resistenz-Management
    wirkstoff_gruppe: Optional[str] = Field(None, max_length=50, description="Active ingredient group")
    rotations_empfehlung: Optional[str] = Field(None, description="Rotation recommendation")

    # Preise und Lager
    ek_preis: Optional[Decimal] = Field(None, ge=0, description="Purchase price")
    vk_preis: Optional[Decimal] = Field(None, ge=0, description="Sales price")
    waehrung: str = Field(default="EUR", max_length=3, description="Currency")
    lagerbestand: Decimal = Field(default=0, ge=0, description="Stock quantity")


class PSMCreate(PSMBase):
    """Schema for creating PSM"""
    tenant_id: str = Field(..., description="Tenant ID")


class PSMUpdate(BaseSchema):
    """Schema for updating PSM"""
    artikelnummer: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    wirkstoff: Optional[str] = Field(None, min_length=1, max_length=100)
    mittel_typ: Optional[str] = Field(None, min_length=1, max_length=50)
    bvl_nummer: Optional[str] = Field(None, min_length=1, max_length=50)
    zulassung_ablauf: Optional[datetime] = Field(None)
    eu_zulassung: Optional[bool] = Field(None)
    kulturen: Optional[List[str]] = Field(None)
    indikationen: Optional[List[str]] = Field(None)
    dosierung_min: Optional[Decimal] = Field(None, ge=0)
    dosierung_max: Optional[Decimal] = Field(None, ge=0)
    wartezeit: Optional[int] = Field(None, ge=0)
    bienenschutz: Optional[bool] = Field(None)
    wasserschutz_gebiet: Optional[bool] = Field(None)
    abstand_wohngebaeude: Optional[int] = Field(None, ge=0)
    abstand_gewaesser: Optional[int] = Field(None, ge=0)
    auflagen: Optional[List[str]] = Field(None)
    ausgangsstoff_explosivstoffe: Optional[bool] = Field(None)
    erklaerung_landwirt_erforderlich: Optional[bool] = Field(None)
    erklaerung_landwirt_status: Optional[str] = Field(None, max_length=20)
    wirkstoff_gruppe: Optional[str] = Field(None, max_length=50)
    rotations_empfehlung: Optional[str] = Field(None)
    ek_preis: Optional[Decimal] = Field(None, ge=0)
    vk_preis: Optional[Decimal] = Field(None, ge=0)
    waehrung: Optional[str] = Field(None, max_length=3)
    lagerbestand: Optional[Decimal] = Field(None, ge=0)
    ist_aktiv: Optional[bool] = Field(None)


class PSM(PSMBase, TimestampMixin, SoftDeleteMixin):
    """Full PSM schema"""
    id: str = Field(..., description="PSM ID")
    tenant_id: str = Field(..., description="Tenant ID")


class SachkundeBase(BaseSchema):
    """Base Sachkunde schema"""
    person_id: str = Field(..., description="Person ID")
    sachkunde_typ: str = Field(..., min_length=1, max_length=50, description="Expertise type")
    zertifikat_nummer: Optional[str] = Field(None, max_length=50, description="Certificate number")
    ausgestellt_am: datetime = Field(..., description="Issue date")
    gueltig_bis: datetime = Field(..., description="Expiry date")
    aussteller: Optional[str] = Field(None, max_length=100, description="Issuer")


class SachkundeCreate(SachkundeBase):
    """Schema for creating Sachkunde"""
    tenant_id: str = Field(..., description="Tenant ID")


class Sachkunde(SachkundeBase, TimestampMixin):
    """Full Sachkunde schema"""
    id: str = Field(..., description="Sachkunde ID")
    tenant_id: str = Field(..., description="Tenant ID")
    ist_gueltig: bool = Field(default=True, description="Valid status")
    erinnerung_versendet: bool = Field(default=False, description="Reminder sent")


# Biostimulanzien Schemas
class BiostimulanzBase(BaseSchema):
    """Base Biostimulanz schema"""
    artikelnummer: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    typ: str = Field(..., min_length=1, max_length=50, description="Type")
    hersteller: Optional[str] = Field(None, max_length=100, description="Manufacturer")

    # Spezifische Eigenschaften
    zusammensetzung: Dict[str, Any] = Field(default_factory=dict, description="Composition")
    anwendungsbereich: List[str] = Field(default_factory=list, description="Application areas")
    dosierung: Optional[str] = Field(None, max_length=100, description="Dosage")

    # Zulassungen
    eu_zulassung: Optional[str] = Field(None, max_length=50, description="EU approval")
    ablauf_zulassung: Optional[datetime] = Field(None, description="Approval expiry")

    # Preise und Lager
    ek_preis: Optional[Decimal] = Field(None, ge=0, description="Purchase price")
    vk_preis: Optional[Decimal] = Field(None, ge=0, description="Sales price")
    waehrung: str = Field(default="EUR", max_length=3, description="Currency")
    lagerbestand: Decimal = Field(default=0, ge=0, description="Stock quantity")


class BiostimulanzCreate(BiostimulanzBase):
    """Schema for creating Biostimulanz"""
    tenant_id: str = Field(..., description="Tenant ID")


class BiostimulanzUpdate(BaseSchema):
    """Schema for updating Biostimulanz"""
    artikelnummer: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    typ: Optional[str] = Field(None, min_length=1, max_length=50)
    hersteller: Optional[str] = Field(None, max_length=100)
    zusammensetzung: Optional[Dict[str, Any]] = Field(None)
    anwendungsbereich: Optional[List[str]] = Field(None)
    dosierung: Optional[str] = Field(None, max_length=100)
    eu_zulassung: Optional[str] = Field(None, max_length=50)
    ablauf_zulassung: Optional[datetime] = Field(None)
    ek_preis: Optional[Decimal] = Field(None, ge=0)
    vk_preis: Optional[Decimal] = Field(None, ge=0)
    waehrung: Optional[str] = Field(None, max_length=3)
    lagerbestand: Optional[Decimal] = Field(None, ge=0)
    ist_aktiv: Optional[bool] = Field(None)


class Biostimulanz(BiostimulanzBase, TimestampMixin, SoftDeleteMixin):
    """Full Biostimulanz schema"""
    id: str = Field(..., description="Biostimulanz ID")
    tenant_id: str = Field(..., description="Tenant ID")