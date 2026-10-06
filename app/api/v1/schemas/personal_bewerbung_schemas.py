"""Ein- und Ausgabe der Bewerbungspipeline.

Bis zum 06.10.2026 hingen alle vier Wege an `PersonalOut` mit ``extra="allow"`` —
einem Modell, das alles erlaubt und deshalb nichts beschreibt. Die Liste gab rohe
Datenbankzeilen zurueck, das Anlegen ``{id, status}``, der Stufenwechsel
``{id, stage, status}``: drei Formen unter einem Namen.
"""

from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

#: Deckungsgleich mit ``bewerbung_service.STUFEN`` und ``ck_bewerbung_status``.
Stufe = Literal[
    "EINGANG",
    "VORAUSWAHL",
    "ERSTGESPRAECH",
    "ENDGESPRAECH",
    "ANGEBOT",
    "EINGESTELLT",
    "ABGELEHNT",
]


class BewerbungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicant_name: str = Field(min_length=1, max_length=200)
    applicant_email: str = Field(min_length=3, max_length=200)
    position_id: Optional[str] = None
    position_title: Optional[str] = Field(default=None, max_length=200)
    source: Optional[str] = Field(default=None, max_length=80)
    documents_ref: Optional[str] = None


class StufeIn(BaseModel):
    """Ein Stufenwechsel.

    ``ablehnungsgrund`` ist Pflicht, wenn nach ``ABGELEHNT`` gewechselt wird: Im
    Streitfall traegt der Arbeitgeber die Beweislast (§ 22 AGG).
    """

    model_config = ConfigDict(extra="forbid")

    stage: Stufe
    note: Optional[str] = None
    ablehnungsgrund: Optional[str] = None
    entschieden_durch: Optional[str] = Field(default=None, max_length=120)


class BewerbungOut(BaseModel):
    id: str
    tenant_id: str
    applicant_name: str
    applicant_email: str
    position_id: Optional[str] = None
    position_title: Optional[str] = None
    source: Optional[str] = None
    documents_ref: Optional[str] = None
    status: str
    notes: Optional[str] = None
    ablehnungsgrund: Optional[str] = None
    entschieden_am: Optional[str] = None
    entschieden_durch: Optional[str] = None
    applied_at: Optional[str] = None
    last_updated: Optional[str] = None
    #: Abgeleitet: Aus `EINGESTELLT` und `ABGELEHNT` fuehrt kein Weg heraus.
    endgueltig: bool = False
    #: Die Einwilligung zur laengeren Aufbewahrung (Talentpool, Art. 6 Abs. 1 lit. a
    #: DSGVO). Wer eingewilligt hat, wird vom Loeschlauf nicht mitgenommen.
    aufbewahrung_einwilligung_bis: Optional[str] = None
    aufbewahrung_einwilligung_am: Optional[str] = None


# ── Speicherbegrenzung: Frist, Trockenlauf, Lauf ─────────────────────────────
# Art. 5 Abs. 1 lit. e DSGVO. Die Frist steht in **Tagen**, nicht in Jahren: Sechs
# Monate sind kein Jahr, und eine Frist, die man aufrunden muss, haelt Daten
# laenger als noetig. Das Gegenstueck — die GoBD-Richtlinie — rechnet in Jahren und
# sagt "mindestens so lange"; hier gilt "hoechstens so lange".


class AufbewahrungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    #: Hoechstens drei Jahre; darueber waere es kein Aufbewahren, sondern ein Vorrat.
    aufbewahrung_tage: int = Field(ge=1, le=1095)
    gesetzliche_grundlage: str = Field(min_length=1, max_length=200)
    beschluss_am: Optional[date] = None
    beschluss_durch: Optional[str] = Field(default=None, max_length=120)


class AufbewahrungOut(BaseModel):
    id: str
    tenant_id: str
    aufbewahrung_tage: int
    gesetzliche_grundlage: str
    beschluss_am: Optional[str] = None
    beschluss_durch: Optional[str] = None
    aktiv: bool = True


class FaelligOut(BaseModel):
    """Eine Zeile des Trockenlaufs.

    Sie traegt den Namen noch — anders koennte niemand pruefen, was er loescht.
    Ins Protokoll kommt er **nicht**.
    """

    id: str
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    status: str
    entschieden_am: Optional[str] = None
    aufbewahrung_einwilligung_bis: Optional[str] = None
    wird_geloescht: bool
    #: ``LOESCHSPERRE`` oder ``EINWILLIGUNG`` — warum diese Zeile bleibt.
    bleibt_wegen: Optional[Literal["LOESCHSPERRE", "EINWILLIGUNG"]] = None


class TrockenlaufOut(BaseModel):
    aufbewahrung_tage: int
    stichtag: str
    gesetzliche_grundlage: str
    geprueft: int
    wird_geloescht: int
    uebersprungen_sperre: int
    uebersprungen_einwilligung: int
    #: Wahr, wenn die Grenze erreicht wurde — dann ist dies nicht alles.
    weitere_faellig: bool = False
    faellige: List[FaelligOut] = Field(default_factory=list)


class LoeschlaufIn(BaseModel):
    """Der Auftrag zum Lauf.

    Beide Felder sind Pflicht, und das ist Absicht: Ein Loeschlauf vernichtet
    personenbezogene Daten endgueltig. ``durchgefuehrt_durch`` macht den Eingriff
    einem Menschen zurechenbar, ``bestaetigung`` verhindert, dass ein versehentlich
    abgeschickter POST Daten vernichtet.
    """

    model_config = ConfigDict(extra="forbid")

    durchgefuehrt_durch: str = Field(min_length=1, max_length=120)
    bestaetigung: Literal["ENDGUELTIG LOESCHEN"]
    #: Obergrenze je Lauf. Ein abgeschnittener Lauf sagt das in ``weitere_faellig``.
    limit: int = Field(default=1000, ge=1, le=5000)


class LoeschlaufOut(BaseModel):
    """Der Nachweis: Zahlen, keine Namen.

    Man muss beweisen koennen, **dass** geloescht wurde, ohne zu behalten,
    **was** geloescht wurde.
    """

    id: str
    gestartet_am: Optional[str] = None
    aufbewahrung_tage: int
    stichtag: str
    geprueft: int
    geloescht: int
    uebersprungen_sperre: int
    uebersprungen_einwilligung: int
    durchgefuehrt_durch: Optional[str] = None
    hinweis: Optional[str] = None
    weitere_faellig: bool = False
