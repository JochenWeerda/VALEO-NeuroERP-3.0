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


# ── Die Einwilligung zur laengeren Aufbewahrung ───────────────────────────────
# Art. 6 Abs. 1 lit. a DSGVO (Talentpool). Art. 7 Abs. 1 verlangt den **Nachweis**,
# Art. 7 Abs. 3 den jederzeit moeglichen Widerruf, der nicht schwerer sein darf als
# die Erteilung. Deshalb hat der Widerruf **kein** Eingabemodell: Ein Rumpf waere
# eine Angabe mehr als bei der Erteilung.

#: Deckungsgleich mit ``ck_beweinw_kanal``.
Kanal = Literal["WEB", "E_MAIL", "PAPIER", "MUENDLICH"]


class EinwilligungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    #: Bis wann die Erlaubnis reicht. Hoechstens drei Jahre ab heute — eine Erlaubnis
    #: ohne nahes Ende ist ein Vorrat und kann erneuert werden.
    gueltig_bis: date
    kanal: Kanal
    #: Die Fassung der Einwilligungserklaerung, der zugestimmt wurde — die Nummer auf
    #: dem Formular. Ohne sie ist nicht nachweisbar, **wozu** eingewilligt wurde. Kein
    #: freier Text: Zwei Quellen fuer den Wortlaut liefen still auseinander.
    fassung: int = Field(ge=1)
    erfasst_durch: Optional[str] = Field(default=None, max_length=120)


class EinwilligungVorgangOut(BaseModel):
    """Eine Zeile des Verzeichnisses — unveraenderlich.

    Ein Widerruf ist eine **neue** Zeile. Wer die Erteilung ueberschreibt,
    vernichtet den Nachweis, den Art. 7 Abs. 1 verlangt.
    """

    id: str
    tenant_id: str
    bewerbung_id: str
    vorgang: Literal["ERTEILT", "WIDERRUFEN"]
    erfolgt_am: Optional[str] = None
    gueltig_bis: Optional[str] = None
    #: Beim Widerruf leer: nicht erhoben, nicht erfunden.
    kanal: Optional[Kanal] = None
    #: Bei der Erteilung: welche Fassung, und ihr Wortlaut. Beim Widerruf leer.
    fassung: Optional[int] = None
    einwilligungstext: Optional[str] = None
    erfasst_durch: Optional[str] = None


class EinwilligungStandOut(BaseModel):
    bewerbung_id: str
    gueltig_bis: Optional[str] = None
    erteilt_am: Optional[str] = None
    #: Ob die Erlaubnis **heute** noch gilt. Ein blosses Datum liesse das offen, und
    #: eine abgelaufene Einwilligung schuetzt nicht mehr vor dem Loeschlauf.
    laeuft: bool
    vorgaenge: List[EinwilligungVorgangOut] = Field(default_factory=list)


# ── Die Einwilligungserklaerung in Fassungen ────────────────────────────────
# Nachweisbar ist eine Einwilligung erst, wenn feststeht, welchem Wortlaut
# zugestimmt wurde. Eine Fassung ist unveraenderlich; ein neuer Wortlaut ist eine
# neue Fassung.


class ErklaerungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    #: Randleerzeichen werden abgeschnitten; ein Text nur aus Leerraum ist keiner.
    #: Die Nummer vergibt das System — wer sie mitschickt, wird abgewiesen statt
    #: still ueberstimmt.
    wortlaut: str = Field(min_length=1)
    erstellt_durch: Optional[str] = Field(default=None, max_length=120)


class ErklaerungOut(BaseModel):
    id: str
    tenant_id: str
    fassung: int
    wortlaut: str
    erstellt_am: Optional[str] = None
    erstellt_durch: Optional[str] = None
