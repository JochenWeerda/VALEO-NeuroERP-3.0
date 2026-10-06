"""Ein- und Ausgabe der Bewerbungspipeline.

Bis zum 06.10.2026 hingen alle vier Wege an `PersonalOut` mit ``extra="allow"`` —
einem Modell, das alles erlaubt und deshalb nichts beschreibt. Die Liste gab rohe
Datenbankzeilen zurueck, das Anlegen ``{id, status}``, der Stufenwechsel
``{id, stage, status}``: drei Formen unter einem Namen.
"""

from __future__ import annotations

from typing import Literal, Optional

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
