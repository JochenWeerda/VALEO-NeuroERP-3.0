from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class PauseGrund(str, Enum):
    BENUTZER_ANGEFRAGT = "BENUTZER_ANGEFRAGT"
    EXTERNE_ABHAENGIGKEIT = "EXTERNE_ABHAENGIGKEIT"
    RESSOURCE_NICHT_VERFUEGBAR = "RESSOURCE_NICHT_VERFUEGBAR"
    WARTUNG = "WARTUNG"
    FEHLER_UNTERSUCHUNG = "FEHLER_UNTERSUCHUNG"
    GENEHMIGUNG_AUSSTEHEND = "GENEHMIGUNG_AUSSTEHEND"


class PauseStatus(str, Enum):
    AKTIV = "AKTIV"             # Currently paused
    FORTGESETZT = "FORTGESETZT" # Was paused, now resumed
    ABGEBROCHEN = "ABGEBROCHEN" # Paused and then cancelled


class ResumeAusloeser(str, Enum):
    MANUELL = "MANUELL"
    AUTOMATISCH = "AUTOMATISCH"     # Timer expired
    SIGNAL = "SIGNAL"               # External signal received
    ADMIN = "ADMIN"                 # Admin override


@dataclass
class WorkflowPause:
    pause_id: str
    workflow_instanz_id: str
    grund: PauseGrund
    status: PauseStatus = PauseStatus.AKTIV
    pausiert_am: datetime = field(default_factory=datetime.utcnow)
    max_pause_minuten: Optional[int] = None     # None = indefinite
    fortgesetzt_am: Optional[datetime] = None
    resume_ausloeser: Optional[ResumeAusloeser] = None
    notiz: str = ""

    def ist_aktiv(self) -> bool:
        return self.status == PauseStatus.AKTIV

    def ist_ueberfaellig(self, jetzt: datetime) -> bool:
        """
        True if AKTIV and max_pause_minuten is set and
        (jetzt - pausiert_am) > max_pause_minuten.
        """
        if not self.ist_aktiv() or self.max_pause_minuten is None:
            return False
        vergangen = (jetzt - self.pausiert_am).total_seconds() / 60
        return vergangen > self.max_pause_minuten

    def pause_dauer_minuten(self, jetzt: datetime) -> float:
        """
        If FORTGESETZT: (fortgesetzt_am - pausiert_am) in minutes.
        If AKTIV: (jetzt - pausiert_am) in minutes.
        If ABGEBROCHEN: 0.0.
        """
        if self.status == PauseStatus.ABGEBROCHEN:
            return 0.0
        ende = self.fortgesetzt_am if self.status == PauseStatus.FORTGESETZT and self.fortgesetzt_am else jetzt
        return (ende - self.pausiert_am).total_seconds() / 60


@dataclass
class PauseVerlauf:
    verlauf_id: str
    workflow_instanz_id: str
    pausen: list = field(default_factory=list)   # list[WorkflowPause]

    def aktive_pause(self) -> Optional[object]:
        """Returns the first AKTIV pause, None if none."""
        aktive = [p for p in self.pausen if p.ist_aktiv()]
        return aktive[0] if aktive else None

    def gesamt_pause_minuten(self, jetzt: datetime) -> float:
        """Sum of pause_dauer_minuten() for all non-ABGEBROCHEN pauses."""
        return sum(p.pause_dauer_minuten(jetzt) for p in self.pausen if p.status != PauseStatus.ABGEBROCHEN)

    def ueberfaellige_pausen(self, jetzt: datetime) -> list:
        """Returns all pauses where ist_ueberfaellig(jetzt) is True."""
        return [p for p in self.pausen if p.ist_ueberfaellig(jetzt)]


def get_default_pause_verlaeufe() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)

    # Verlauf 1: one completed pause + one active
    v1 = PauseVerlauf("PV-001", "WI-K-001")
    v1.pausen = [
        WorkflowPause("PA-001", "WI-K-001", PauseGrund.GENEHMIGUNG_AUSSTEHEND,
                      PauseStatus.FORTGESETZT, now - timedelta(hours=2), 60,
                      now - timedelta(hours=1), ResumeAusloeser.MANUELL, "Genehmigung erteilt"),
        WorkflowPause("PA-002", "WI-K-001", PauseGrund.EXTERNE_ABHAENGIGKEIT,
                      PauseStatus.AKTIV, now - timedelta(minutes=90), 60,
                      None, None, "Warte auf EDI"),
    ]

    # Verlauf 2: single cancelled pause
    v2 = PauseVerlauf("PV-002", "WI-S-002")
    v2.pausen = [
        WorkflowPause("PA-003", "WI-S-002", PauseGrund.WARTUNG,
                      PauseStatus.ABGEBROCHEN, now - timedelta(hours=1), None,
                      None, None, "Wartung abgebrochen"),
    ]

    return [v1, v2]
