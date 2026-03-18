from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class DeadlineTyp(str, Enum):
    HART = "HART"               # Must be met; breach = failure
    WEICH = "WEICH"             # Target; breach = warning only
    GESETZLICH = "GESETZLICH"   # Legally mandated
    SLA = "SLA"                 # Contractual SLA


class DeadlineStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    ERFUELLT = "ERFUELLT"
    VERLETZT = "VERLETZT"
    ESKALIERT = "ESKALIERT"


class EskalationsStufe(str, Enum):
    STUFE_1 = "STUFE_1"     # Notify owner
    STUFE_2 = "STUFE_2"     # Notify manager
    STUFE_3 = "STUFE_3"     # Notify director
    KRITISCH = "KRITISCH"   # Immediate action required


@dataclass
class WorkflowDeadline:
    deadline_id: str
    workflow_instanz_id: str
    deadline_typ: DeadlineTyp
    faellig_am: datetime
    status: DeadlineStatus = DeadlineStatus.AUSSTEHEND
    eskalations_stufe: Optional[EskalationsStufe] = None
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    erfuellt_am: Optional[datetime] = None
    verantwortlich: str = ""

    def verbleibende_minuten(self, jetzt: datetime) -> float:
        """Positive = time remaining; negative = overdue."""
        return (self.faellig_am - jetzt).total_seconds() / 60

    def ist_verletzt(self, jetzt: datetime) -> bool:
        """True if status==AUSSTEHEND and jetzt >= faellig_am."""
        return self.status == DeadlineStatus.AUSSTEHEND and jetzt >= self.faellig_am

    def berechne_eskalations_stufe(self, jetzt: datetime) -> Optional[EskalationsStufe]:
        """
        Only for violated deadlines (ist_verletzt):
        Overdue < 60 min → STUFE_1
        Overdue 60–240 min → STUFE_2
        Overdue 240–1440 min → STUFE_3
        Overdue >= 1440 min → KRITISCH
        Not violated → None
        """
        if not self.ist_verletzt(jetzt):
            return None
        ueberfaellig_min = abs(self.verbleibende_minuten(jetzt))
        if ueberfaellig_min < 60:
            return EskalationsStufe.STUFE_1
        elif ueberfaellig_min < 240:
            return EskalationsStufe.STUFE_2
        elif ueberfaellig_min < 1440:
            return EskalationsStufe.STUFE_3
        return EskalationsStufe.KRITISCH


@dataclass
class DeadlineMonitor:
    monitor_id: str
    deadlines: list = field(default_factory=list)  # list[WorkflowDeadline]

    def verletzte_deadlines(self, jetzt: datetime) -> list:
        return [d for d in self.deadlines if d.ist_verletzt(jetzt)]

    def kritische_deadlines(self, jetzt: datetime) -> list:
        """Deadlines where berechne_eskalations_stufe returns KRITISCH."""
        return [d for d in self.deadlines
                if d.berechne_eskalations_stufe(jetzt) == EskalationsStufe.KRITISCH]

    def sla_einhaltungs_rate_pct(self) -> float:
        """
        ERFUELLT / (ERFUELLT + VERLETZT + ESKALIERT) * 100.
        100.0 if no completed deadlines.
        AUSSTEHEND not counted.
        """
        erfuellt = sum(1 for d in self.deadlines if d.status == DeadlineStatus.ERFUELLT)
        verletzt = sum(1 for d in self.deadlines if d.status in (DeadlineStatus.VERLETZT, DeadlineStatus.ESKALIERT))
        gesamt = erfuellt + verletzt
        if gesamt == 0:
            return 100.0
        return (erfuellt / gesamt) * 100


def get_default_deadline_monitor() -> DeadlineMonitor:
    now = datetime(2026, 3, 16, 10, 0, 0)
    monitor = DeadlineMonitor("DM-001")
    monitor.deadlines = [
        WorkflowDeadline("DL-001", "WI-K-001", DeadlineTyp.SLA,
                          now + timedelta(hours=2), DeadlineStatus.AUSSTEHEND,
                          None, now - timedelta(hours=1), None, "user-001"),
        WorkflowDeadline("DL-002", "WI-AP-002", DeadlineTyp.HART,
                          now - timedelta(minutes=30), DeadlineStatus.AUSSTEHEND,
                          None, now - timedelta(hours=3), None, "user-002"),
        WorkflowDeadline("DL-003", "WI-S-003", DeadlineTyp.WEICH,
                          now - timedelta(hours=5), DeadlineStatus.AUSSTEHEND,
                          None, now - timedelta(hours=8), None, "user-003"),
        WorkflowDeadline("DL-004", "WI-Q-004", DeadlineTyp.GESETZLICH,
                          now - timedelta(days=2), DeadlineStatus.AUSSTEHEND,
                          None, now - timedelta(days=3), None, "user-004"),
        WorkflowDeadline("DL-005", "WI-E-005", DeadlineTyp.SLA,
                          now - timedelta(hours=1), DeadlineStatus.ERFUELLT,
                          None, now - timedelta(hours=2), now - timedelta(minutes=30), "user-005"),
        WorkflowDeadline("DL-006", "WI-F-006", DeadlineTyp.HART,
                          now + timedelta(days=1), DeadlineStatus.AUSSTEHEND,
                          None, now, None, "user-006"),
    ]
    return monitor
