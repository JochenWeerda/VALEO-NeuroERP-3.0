from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class RollbackTyp(str, Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"     # Undo all steps
    TEILWEISE = "TEILWEISE"           # Undo up to a specific step
    SCHRITT = "SCHRITT"               # Undo single step

class RollbackStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    NICHT_MOEGLICH = "NICHT_MOEGLICH"  # Step cannot be undone

class UmkehrbarkeitsGrad(str, Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"     # Can be fully undone
    TEILWEISE = "TEILWEISE"           # Partially undoable
    NICHT_UMKEHRBAR = "NICHT_UMKEHRBAR"  # Cannot be undone (e.g. sent email)

@dataclass
class RollbackSchritt:
    schritt_id: str
    workflow_schritt_id: str
    rollback_typ: RollbackTyp
    umkehrbarkeit: UmkehrbarkeitsGrad
    status: RollbackStatus = RollbackStatus.AUSSTEHEND
    beschreibung: str = ""
    ausgefuehrt_am: Optional[datetime] = None

    def kann_ausgefuehrt_werden(self) -> bool:
        """True if umkehrbarkeit != NICHT_UMKEHRBAR and status == AUSSTEHEND."""
        return (self.umkehrbarkeit != UmkehrbarkeitsGrad.NICHT_UMKEHRBAR
                and self.status == RollbackStatus.AUSSTEHEND)

@dataclass
class RollbackPlan:
    plan_id: str
    workflow_instanz_id: str
    rollback_typ: RollbackTyp
    schritte: list = field(default_factory=list)  # list[RollbackSchritt], ordered newest-first
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    erstellt_von: str = ""

    def ausfuehrbare_schritte(self) -> list:
        """Returns steps where kann_ausgefuehrt_werden() is True."""
        return [s for s in self.schritte if s.kann_ausgefuehrt_werden()]

    def ist_vollstaendig_ausfuehrbar(self) -> bool:
        """True if all steps kann_ausgefuehrt_werden() — i.e. none are NICHT_UMKEHRBAR."""
        if not self.schritte:
            return True
        return all(s.umkehrbarkeit != UmkehrbarkeitsGrad.NICHT_UMKEHRBAR for s in self.schritte)

    def rollback_fortschritt_pct(self) -> float:
        """
        Percentage of steps completed (ABGESCHLOSSEN / total).
        0.0 for empty.
        """
        if not self.schritte:
            return 0.0
        abgeschlossen = sum(1 for s in self.schritte if s.status == RollbackStatus.ABGESCHLOSSEN)
        return (abgeschlossen / len(self.schritte)) * 100

def get_default_rollback_plaene() -> list:
    """Returns 3 default RollbackPlan instances."""
    now = datetime(2026, 3, 16, 10, 0, 0)

    # Plan 1: Fully executable kontrakt rollback
    p1 = RollbackPlan("RP-001", "WI-K-001", RollbackTyp.VOLLSTAENDIG, erstellt_am=now, erstellt_von="system")
    p1.schritte = [
        RollbackSchritt("RS-001", "WS-003", RollbackTyp.SCHRITT, UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN, "Freigabe zurückziehen"),
        RollbackSchritt("RS-002", "WS-002", RollbackTyp.SCHRITT, UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.ABGESCHLOSSEN, "Prüfung rückgängig"),
        RollbackSchritt("RS-003", "WS-001", RollbackTyp.SCHRITT, UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND, "Erfassung löschen"),
    ]

    # Plan 2: Partial — has NICHT_UMKEHRBAR step
    p2 = RollbackPlan("RP-002", "WI-S-002", RollbackTyp.TEILWEISE, erstellt_am=now, erstellt_von="user-001")
    p2.schritte = [
        RollbackSchritt("RS-004", "WS-010", RollbackTyp.SCHRITT, UmkehrbarkeitsGrad.VOLLSTAENDIG, RollbackStatus.AUSSTEHEND, "Buchung stornieren"),
        RollbackSchritt("RS-005", "WS-009", RollbackTyp.SCHRITT, UmkehrbarkeitsGrad.NICHT_UMKEHRBAR, RollbackStatus.NICHT_MOEGLICH, "E-Mail bereits versendet"),
    ]

    # Plan 3: Empty
    p3 = RollbackPlan("RP-003", "WI-LEER-003", RollbackTyp.SCHRITT, erstellt_am=now)

    return [p1, p2, p3]
