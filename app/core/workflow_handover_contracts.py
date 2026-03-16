from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class UebergabeTyp(str, Enum):
    ESKALATION = "ESKALATION"           # Escalate up
    DELEGATION = "DELEGATION"           # Delegate down/sideways
    STELLVERTRETUNG = "STELLVERTRETUNG" # Substitute
    ABSCHLUSS = "ABSCHLUSS"             # Final handover to close


class UebergabeStatus(str, Enum):
    ANGEFRAGT = "ANGEFRAGT"
    ANGENOMMEN = "ANGENOMMEN"
    ABGELEHNT = "ABGELEHNT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    ZURUECKGEZOGEN = "ZURUECKGEZOGEN"


class DringlichkeitsStufe(str, Enum):
    NORMAL = "NORMAL"
    DRINGEND = "DRINGEND"
    SOFORT = "SOFORT"


@dataclass
class UebergabeAnfrage:
    anfrage_id: str
    workflow_instanz_id: str
    uebergabe_typ: UebergabeTyp
    von_rolle: str
    zu_rolle: str
    dringlichkeit: DringlichkeitsStufe = DringlichkeitsStufe.NORMAL
    status: UebergabeStatus = UebergabeStatus.ANGEFRAGT
    begruendung: str = ""
    angefragt_am: datetime = field(default_factory=datetime.utcnow)
    beantwortet_am: Optional[datetime] = None
    antwort_nachricht: str = ""

    def ist_offen(self) -> bool:
        """True if status is ANGEFRAGT."""
        return self.status == UebergabeStatus.ANGEFRAGT

    def reaktionszeit_minuten(self) -> Optional[float]:
        """Minutes from angefragt_am to beantwortet_am. None if not yet answered."""
        if self.beantwortet_am is None:
            return None
        return (self.beantwortet_am - self.angefragt_am).total_seconds() / 60


@dataclass
class UebergabeProtokoll:
    protokoll_id: str
    workflow_instanz_id: str
    anfragen: list = field(default_factory=list)  # list[UebergabeAnfrage]

    def offene_anfragen(self) -> list:
        return [a for a in self.anfragen if a.ist_offen()]

    def angenommene_anfragen(self) -> list:
        return [a for a in self.anfragen if a.status == UebergabeStatus.ANGENOMMEN]

    def durchschnittliche_reaktionszeit_minuten(self) -> Optional[float]:
        """
        Average reaction time of all answered requests (beantwortet_am is not None).
        None if no answered requests.
        """
        zeiten = [a.reaktionszeit_minuten() for a in self.anfragen if a.beantwortet_am is not None]
        if not zeiten:
            return None
        return sum(zeiten) / len(zeiten)

    def eskalations_quote_pct(self) -> float:
        """ESKALATION requests / total * 100. 0.0 for empty."""
        if not self.anfragen:
            return 0.0
        eskalationen = sum(1 for a in self.anfragen if a.uebergabe_typ == UebergabeTyp.ESKALATION)
        return (eskalationen / len(self.anfragen)) * 100


def get_default_uebergabe_protokolle() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    p1 = UebergabeProtokoll("UP-001", "WI-K-001")
    p1.anfragen = [
        UebergabeAnfrage("UA-001", "WI-K-001", UebergabeTyp.ESKALATION, "SACHBEARBEITER", "ABTEILUNGSLEITER",
                         DringlichkeitsStufe.DRINGEND, UebergabeStatus.ANGENOMMEN, "Sonderkonditionen",
                         now - timedelta(hours=2), now - timedelta(hours=1, minutes=45), "Genehmigt"),
        UebergabeAnfrage("UA-002", "WI-K-001", UebergabeTyp.DELEGATION, "ABTEILUNGSLEITER", "SACHBEARBEITER",
                         DringlichkeitsStufe.NORMAL, UebergabeStatus.ANGENOMMEN, "Rückdelegation",
                         now - timedelta(hours=1), now - timedelta(minutes=50), "OK"),
        UebergabeAnfrage("UA-003", "WI-K-001", UebergabeTyp.ABSCHLUSS, "SACHBEARBEITER", "ARCHIV",
                         DringlichkeitsStufe.NORMAL, UebergabeStatus.ANGEFRAGT, "Abschluss",
                         now - timedelta(minutes=10), None, ""),
    ]

    p2 = UebergabeProtokoll("UP-002", "WI-S-002")
    p2.anfragen = [
        UebergabeAnfrage("UA-004", "WI-S-002", UebergabeTyp.STELLVERTRETUNG, "BUCHHALTER-A", "BUCHHALTER-B",
                         DringlichkeitsStufe.SOFORT, UebergabeStatus.ABGELEHNT, "Urlaub",
                         now - timedelta(hours=3), now - timedelta(hours=2, minutes=55), "Nicht verfügbar"),
    ]

    return [p1, p2]
