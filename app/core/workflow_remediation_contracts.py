from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class RemediationsTyp(str, Enum):
    AUTOMATISCH = "AUTOMATISCH"          # System executes without human
    HALBAUTOMATISCH = "HALBAUTOMATISCH"  # System proposes, human confirms
    MANUELL = "MANUELL"                  # Human must act

class RemediationsStatus(str, Enum):
    VORGESCHLAGEN = "VORGESCHLAGEN"
    GENEHMIGT = "GENEHMIGT"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    ABGELEHNT = "ABGELEHNT"

class RemediationsAktion(str, Enum):
    NEUSTART = "NEUSTART"
    ROLLBACK = "ROLLBACK"
    RETRY = "RETRY"
    ESKALIEREN = "ESKALIEREN"
    CACHE_LEEREN = "CACHE_LEEREN"
    VERBINDUNG_RESET = "VERBINDUNG_RESET"
    MANUELL_EINGREIFEN = "MANUELL_EINGREIFEN"

@dataclass
class RemediationsSchritt:
    schritt_id: str
    aktion: RemediationsAktion
    reihenfolge: int
    beschreibung: str = ""
    automatisch: bool = True
    timeout_sekunden: int = 60

@dataclass
class RemediationsPlaybook:
    playbook_id: str
    ausnahme_muster: str            # AusnahmeMuster value this handles
    typ: RemediationsTyp
    schritte: list = field(default_factory=list)  # list[RemediationsSchritt]
    erfolgreich_angewendet: int = 0
    fehlgeschlagen_angewendet: int = 0
    beschreibung: str = ""

    def erfolgsrate_pct(self) -> float:
        """erfolgreich / (erfolgreich + fehlgeschlagen) * 100. 100.0 if never applied."""
        gesamt = self.erfolgreich_angewendet + self.fehlgeschlagen_angewendet
        if gesamt == 0:
            return 100.0
        return (self.erfolgreich_angewendet / gesamt) * 100

    def automatische_schritte(self) -> list:
        """Returns steps where automatisch==True, sorted by reihenfolge."""
        return sorted([s for s in self.schritte if s.automatisch], key=lambda s: s.reihenfolge)

@dataclass
class RemediationsVorschlag:
    vorschlag_id: str
    workflow_instanz_id: str
    ausnahme_muster: str
    playbook_id: str
    status: RemediationsStatus = RemediationsStatus.VORGESCHLAGEN
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    genehmigt_von: Optional[str] = None
    abgeschlossen_am: Optional[datetime] = None

    def ist_aktiv(self) -> bool:
        return self.status in (RemediationsStatus.VORGESCHLAGEN, RemediationsStatus.GENEHMIGT, RemediationsStatus.LAUFEND)

def get_default_playbooks() -> list:
    pb1 = RemediationsPlaybook("PB-001", "TIMEOUT", RemediationsTyp.AUTOMATISCH,
                                erfolgreich_angewendet=45, fehlgeschlagen_angewendet=5,
                                beschreibung="Timeout Recovery")
    pb1.schritte = [
        RemediationsSchritt("RS-001", RemediationsAktion.VERBINDUNG_RESET, 1, "Reset connection", True, 30),
        RemediationsSchritt("RS-002", RemediationsAktion.RETRY, 2, "Retry operation", True, 60),
        RemediationsSchritt("RS-003", RemediationsAktion.ESKALIEREN, 3, "Escalate if retry fails", False, 0),
    ]

    pb2 = RemediationsPlaybook("PB-002", "DATENFEHLER", RemediationsTyp.HALBAUTOMATISCH,
                                erfolgreich_angewendet=20, fehlgeschlagen_angewendet=2,
                                beschreibung="Data Validation Fix")
    pb2.schritte = [
        RemediationsSchritt("RS-004", RemediationsAktion.ROLLBACK, 1, "Rollback invalid data", True, 30),
        RemediationsSchritt("RS-005", RemediationsAktion.MANUELL_EINGREIFEN, 2, "Manual data fix", False, 0),
    ]

    pb3 = RemediationsPlaybook("PB-003", "RESSOURCENENGPASS", RemediationsTyp.AUTOMATISCH,
                                erfolgreich_angewendet=0, fehlgeschlagen_angewendet=0,
                                beschreibung="Resource Exhaustion")
    pb3.schritte = [
        RemediationsSchritt("RS-006", RemediationsAktion.CACHE_LEEREN, 1, "Clear caches", True, 15),
        RemediationsSchritt("RS-007", RemediationsAktion.ESKALIEREN, 2, "Notify ops", False, 0),
    ]

    return [pb1, pb2, pb3]
