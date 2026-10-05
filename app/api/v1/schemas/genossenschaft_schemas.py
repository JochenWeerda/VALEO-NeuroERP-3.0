"""Antwortmodelle des Mitgliederregisters.

Bis zum 05.10.2026 stand hier ein einziges offenes Modell
(``GenossenschaftOut`` mit ``extra="allow"``), das an jedem Weg hing — an der
Mitgliederliste, an der Detailansicht und an der Kapitaluebersicht. Ein Modell,
das alles erlaubt, beschreibt nichts: Die Kapitaluebersicht gab Aggregatzahlen
zurueck und war trotzdem als Mitglied dokumentiert. Jetzt hat jeder Weg sein
Modell.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.base import BaseSchema

#: Deckungsgleich mit ``genossenschaft_service.STAENDE`` und der Pruefbedingung
#: ``ck_geno_mitglied_status``.
MitgliedsStatus = Literal["AKTIV", "RUHEND", "AUSGETRETEN"]

#: Deckungsgleich mit ``genossenschaft_service.BEWEGUNGSTYPEN`` und
#: ``ck_geno_bewegungstyp``. ``TRANSFER`` fehlt hier bewusst: Eine Uebertragung
#: hat zwei Seiten, also zwei gerichtete Typen.
Bewegungstyp = Literal[
    "ZEICHNUNG",
    "ERHOEHUNG",
    "TEILRUECKZAHLUNG",
    "VOLLRUECKZAHLUNG",
    "UEBERTRAGUNG_AB",
    "UEBERTRAGUNG_AN",
]


class GenossenschaftOut(BaseSchema):
    """Historisches offenes Modell.

    Bleibt bestehen, weil aeltere OpenAPI-Verweise darauf zeigen; an keinem Weg
    dieses Moduls haengt es noch.
    """

    model_config = ConfigDict(extra="allow")


class MitgliedCreate(BaseModel):
    """Beitritt nach § 15 GenG."""

    # Ein unbekanntes Feld wird abgewiesen und nicht verschluckt: Sonst ginge
    # ein Tippfehler als stille Nichtaenderung durch.
    model_config = ConfigDict(extra="forbid")

    mitglieds_nr: Optional[str] = Field(
        default=None, description="Wird vergeben, wenn nicht angegeben"
    )
    name: str = Field(min_length=1)
    adresse: str = Field(min_length=1)
    eintrittsdatum: date
    anteilswert_eur: float = Field(default=100.0, gt=0, description="Hoehe eines Geschaeftsanteils")
    genossenschaftsanteile: int = Field(
        default=0,
        ge=0,
        description=(
            "Erstzeichnung. Wird als Bewegung ZEICHNUNG gebucht, nicht als Zahl "
            "gespeichert — der Bestand folgt immer aus den Bewegungen."
        ),
    )
    status: MitgliedsStatus = "AKTIV"
    iban: str = Field(min_length=15, max_length=34)
    bank_name: str = Field(min_length=1)
    erfasst_durch: Optional[str] = None


class MitgliedPatch(BaseModel):
    """Stammdatenpflege.

    ``genossenschaftsanteile`` fehlt hier mit Absicht: Der Bestand aendert sich
    ausschliesslich durch eine Bewegung. Eine stille Korrektur der Zahl waere
    genau die unbelegte Aenderung, die GoBD Rz. 107 ff. ausschliesst.
    """

    # ``extra="forbid"``, damit ein PATCH auf ``genossenschaftsanteile``
    # als 422 auffaellt statt stillschweigend nichts zu tun.
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1)
    adresse: Optional[str] = Field(default=None, min_length=1)
    anteilswert_eur: Optional[float] = Field(default=None, gt=0)
    status: Optional[MitgliedsStatus] = None
    austrittsdatum: Optional[date] = None
    iban: Optional[str] = Field(default=None, min_length=15, max_length=34)
    bank_name: Optional[str] = Field(default=None, min_length=1)


class AnteilsbewegungCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bewegungstyp: Bewegungstyp
    anzahl_anteile: int = Field(gt=0, description="Immer positiv; die Richtung steckt im Typ")
    wert_eur: float = Field(gt=0)
    datum: date
    bemerkung: Optional[str] = None
    gegen_mitglieds_id: Optional[str] = Field(
        default=None, description="Pflicht bei UEBERTRAGUNG_AB / UEBERTRAGUNG_AN"
    )
    erfasst_durch: Optional[str] = None


class AnteilsbewegungOut(BaseModel):
    id: str
    bewegungstyp: str
    anzahl_anteile: int
    wert_eur: float
    datum: Optional[str] = None
    bemerkung: Optional[str] = None
    gegen_mitglieds_id: Optional[str] = None
    journal_entry_id: Optional[str] = None
    erfasst_durch: Optional[str] = None
    created_at: Optional[str] = None


class MitgliedOut(BaseModel):
    id: str
    tenant_id: str
    mitglieds_nr: str
    name: str
    adresse: str
    eintrittsdatum: Optional[str] = None
    austrittsdatum: Optional[str] = None
    anteilswert_eur: float
    status: str
    iban: str
    bank_name: str
    #: Abgeleitet aus den Bewegungen, nicht gespeichert.
    genossenschaftsanteile: int
    geschaeftsguthaben_eur: float
    created_at: Optional[str] = None


class MitgliedDetailOut(MitgliedOut):
    anteilsbewegungen: list[AnteilsbewegungOut] = Field(default_factory=list)


class MitgliedAngelegt(BaseModel):
    id: str
    mitglieds_nr: str
    genossenschaftsanteile: int
    status: str = "angelegt"


class MitgliedGeaendert(BaseModel):
    id: str
    geaenderte_felder: list[str]
    status: str = "aktualisiert"


class AnteilsbewegungGebucht(BaseModel):
    id: str
    mitglieds_id: str
    bewegungstyp: str
    #: Der Bestand **nach** der Buchung, abgeleitet.
    bestand_anteile: int
    gegenbewegung_id: Optional[str] = None
    journal_entry_id: Optional[str] = None
    status: str = "gebucht"


class KapitaluebersichtOut(BaseModel):
    """Geschaeftsguthaben der Mitglieder — Bilanzposition nach § 337 HGB."""

    total_mitglieder: int
    total_anteile: int
    total_kapital_eur: float
    aktiv: int
    ruhend: int
    ausgetreten: int
    #: Anteile, die auf ausgetretene Mitglieder entfallen und noch nicht
    #: abgewickelt sind (§ 73 GenG Auseinandersetzung).
    offene_auseinandersetzung_anteile: int
