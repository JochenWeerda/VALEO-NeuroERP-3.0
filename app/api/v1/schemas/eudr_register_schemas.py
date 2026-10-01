"""Schemata des EUDR-Sorgfaltserklaerungsregisters.

Feldsatz nach Verordnung (EU) 2023/1115: Inhalt der Sorgfaltserklaerung nach
**Anhang II**, Informationspflichten nach **Art. 9**, Risikobewertung und
-minderung nach **Art. 10/11**, Referenz- und Verifizierungsnummer des
EU-Informationssystems nach **Art. 33**.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.api.v1.schemas.base import BaseSchema

#: Anhang I der Verordnung: die relevanten Rohstoffe.
ROHSTOFFE = ("RIND", "KAKAO", "KAFFEE", "OELPALME", "KAUTSCHUK", "SOJA", "HOLZ")

#: Art. 10: Die Risikobewertung endet in einer dieser beiden Feststellungen.
RISIKOSTUFEN = ("VERNACHLAESSIGBAR", "NICHT_VERNACHLAESSIGBAR")

STAENDE = ("ENTWURF", "EINGEREICHT", "ZURUECKGEZOGEN")

#: Art. 9: Ab dieser Groesse ist die Geolokation als Polygon anzugeben.
POLYGONGRENZE_HA = 4


class GeolokationIn(BaseModel):
    """Ein Flurstueck (Art. 9).

    Ueber vier Hektar ist ein Polygon anzugeben; ein Punkt genuegt dann nicht.
    Die Datenbank haelt dieselbe Bedingung.
    """

    flurstueck_kennung: Optional[str] = None
    breitengrad: float = Field(..., ge=-90, le=90)
    laengengrad: float = Field(..., ge=-180, le=180)
    flaeche_ha: Optional[float] = Field(default=None, gt=0)
    polygon: Optional[dict] = Field(
        default=None, description="GeoJSON-Polygon; Pflicht ab vier Hektar"
    )


class GeolokationOut(BaseSchema):
    id: str
    flurstueck_kennung: Optional[str] = None
    breitengrad: float
    laengengrad: float
    flaeche_ha: Optional[float] = None
    polygon: Optional[dict] = None


class VorgelagerteErklaerungIn(BaseModel):
    """Anhang II Nr. 4: Referenznummer einer vorgelagerten Erklaerung."""

    referenznummer: str = Field(..., min_length=1)
    verifizierungsnummer: Optional[str] = None
    lieferant_name: Optional[str] = None


class VorgelagerteErklaerungOut(BaseSchema):
    id: str
    referenznummer: str
    verifizierungsnummer: Optional[str] = None
    lieferant_name: Optional[str] = None


class SorgfaltserklaerungIn(BaseModel):
    """Eine neue Sorgfaltserklaerung im Entwurf."""

    # Anhang II Nr. 1
    betreiber_name: str = Field(..., min_length=1)
    betreiber_adresse: str = Field(..., min_length=1)
    eori_nummer: Optional[str] = None

    # Anhang II Nr. 2
    rohstoff: str
    hs_code: str = Field(..., min_length=4, max_length=16)
    warenbeschreibung: str = Field(..., min_length=1)
    menge_netto_kg: float = Field(..., gt=0)
    menge_volumen_m3: Optional[float] = Field(default=None, gt=0)
    ergaenzende_einheit: Optional[str] = None

    # Anhang II Nr. 3 / Art. 9
    produktionsland: str = Field(..., min_length=2, max_length=2)
    produktion_von: date
    produktion_bis: date

    # Art. 9
    lieferant_name: str = Field(..., min_length=1)
    lieferant_adresse: Optional[str] = None
    lieferant_email: Optional[str] = None

    nachweis_abholzungsfrei: bool = False
    nachweis_abholzungsfrei_quelle: Optional[str] = None
    nachweis_rechtskonform: bool = False
    nachweis_rechtskonform_quelle: Optional[str] = None

    geolokationen: list[GeolokationIn] = Field(default_factory=list)
    vorgelagerte_erklaerungen: list[VorgelagerteErklaerungIn] = Field(
        default_factory=list
    )


class RisikobewertungIn(BaseModel):
    """Art. 10/11: die Feststellung und, wenn noetig, die Minderung."""

    risikostufe: str
    bewertet_durch: str = Field(..., min_length=1)
    minderungsmassnahmen: Optional[str] = None


class EinreichungIn(BaseModel):
    """Art. 33: Referenz- und Verifizierungsnummer aus dem EU-System.

    Dazu die Unterzeichnung nach Anhang II Nr. 6 — Name und Funktion der
    Person, die fuer den Marktteilnehmer erklaert.
    """

    referenznummer: str = Field(..., min_length=1)
    verifizierungsnummer: Optional[str] = None
    erklaerung_durch_name: str = Field(..., min_length=1)
    erklaerung_durch_funktion: str = Field(..., min_length=1)


class SorgfaltserklaerungOut(BaseSchema):
    id: str
    tenant_id: str
    status: str

    betreiber_name: str
    betreiber_adresse: str
    eori_nummer: Optional[str] = None

    rohstoff: str
    hs_code: str
    warenbeschreibung: str
    menge_netto_kg: float
    menge_volumen_m3: Optional[float] = None
    ergaenzende_einheit: Optional[str] = None

    produktionsland: str
    produktion_von: Optional[str] = None
    produktion_bis: Optional[str] = None

    lieferant_name: str
    lieferant_adresse: Optional[str] = None
    lieferant_email: Optional[str] = None

    nachweis_abholzungsfrei: bool = False
    nachweis_abholzungsfrei_quelle: Optional[str] = None
    nachweis_rechtskonform: bool = False
    nachweis_rechtskonform_quelle: Optional[str] = None

    risikostufe: Optional[str] = None
    risikobewertung_am: Optional[str] = None
    risikobewertung_durch: Optional[str] = None
    minderungsmassnahmen: Optional[str] = None

    erklaerung_abgegeben_am: Optional[str] = None
    erklaerung_durch_name: Optional[str] = None
    erklaerung_durch_funktion: Optional[str] = None

    referenznummer: Optional[str] = None
    verifizierungsnummer: Optional[str] = None
    eingereicht_am: Optional[str] = None

    created_at: Optional[str] = None


class SorgfaltserklaerungDetailOut(SorgfaltserklaerungOut):
    geolokationen: list[GeolokationOut] = Field(default_factory=list)
    vorgelagerte_erklaerungen: list[VorgelagerteErklaerungOut] = Field(
        default_factory=list
    )


class EudrRegisterStatusOut(BaseSchema):
    """Der Stand des Registers — ohne gruene Behauptung.

    ``status`` ist ``KONFORM`` nur dann, wenn jede Erklaerung des Hauses
    eingereicht ist und vernachlaessigbares Risiko traegt. Ist das Register
    leer, lautet der Stand ``OHNE_ERKLAERUNG`` — nicht ``KONFORM``: Nach
    Art. 3/4 ist das Inverkehrbringen ohne Sorgfaltserklaerung verboten, und
    "nichts erfasst" ist kein Nachweis.
    """

    status: str
    erklaerungen_gesamt: int = 0
    erklaerungen_eingereicht: int = 0
    erklaerungen_entwurf: int = 0
    risiko_nicht_vernachlaessigbar: int = 0
    ohne_risikobewertung: int = 0
    produktionslaender: list[str] = Field(default_factory=list)
    rohstoffe: list[str] = Field(default_factory=list)
    stand_am: Optional[str] = None
