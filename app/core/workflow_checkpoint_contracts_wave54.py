from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class CheckpointTyp(str, Enum):
    AUTOMATISCH = "AUTOMATISCH"                   # System-triggered after each step
    MANUELL = "MANUELL"                           # User-triggered
    VOR_KRITISCHEM_SCHRITT = "VOR_KRITISCHEM_SCHRITT"
    NACH_FEHLER = "NACH_FEHLER"


class CheckpointStatus(str, Enum):
    AKTUELL = "AKTUELL"                           # Latest valid checkpoint
    VERALTET = "VERALTET"                         # Superseded by newer checkpoint
    WIEDERHERGESTELLT = "WIEDERHERGESTELLT"       # Used for recovery
    KORRUPT = "KORRUPT"                           # Data integrity failed


@dataclass
class WorkflowCheckpoint:
    checkpoint_id: str
    workflow_instanz_id: str
    checkpoint_typ: CheckpointTyp
    zustand_snapshot: dict                        # serialized workflow state at this point
    schritt_nummer: int                           # which step was completed
    status: CheckpointStatus = CheckpointStatus.AKTUELL
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    erstellt_von: str = ""

    def ist_verwendbar(self) -> bool:
        """True if status is AKTUELL or WIEDERHERGESTELLT."""
        return self.status in (CheckpointStatus.AKTUELL, CheckpointStatus.WIEDERHERGESTELLT)


@dataclass
class CheckpointSequenz:
    instanz_id: str
    checkpoints: list = field(default_factory=list)  # list[WorkflowCheckpoint]

    def aktuellster_checkpoint(self) -> Optional[object]:
        """Returns the checkpoint with highest schritt_nummer that ist_verwendbar(), or None."""
        verwendbare = [c for c in self.checkpoints if c.ist_verwendbar()]
        if not verwendbare:
            return None
        return max(verwendbare, key=lambda c: c.schritt_nummer)

    def wiederherstellungs_punkt(self, ab_schritt: int) -> Optional[object]:
        """
        Returns the most recent usable checkpoint where schritt_nummer <= ab_schritt.
        None if no such checkpoint exists.
        """
        kandidaten = [c for c in self.checkpoints if c.ist_verwendbar() and c.schritt_nummer <= ab_schritt]
        if not kandidaten:
            return None
        return max(kandidaten, key=lambda c: c.schritt_nummer)


def get_default_checkpoint_sequenzen() -> list:
    """Returns 3 default CheckpointSequenz instances."""
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    # Seq 1: kontrakt workflow — 3 checkpoints, last is AKTUELL
    s1 = CheckpointSequenz("WI-K-001")
    s1.checkpoints = [
        WorkflowCheckpoint("CP-001", "WI-K-001", CheckpointTyp.AUTOMATISCH, {"schritt": "erfasst"}, 1, CheckpointStatus.VERALTET, now),
        WorkflowCheckpoint("CP-002", "WI-K-001", CheckpointTyp.VOR_KRITISCHEM_SCHRITT, {"schritt": "geprueft"}, 2, CheckpointStatus.VERALTET, now + timedelta(minutes=5)),
        WorkflowCheckpoint("CP-003", "WI-K-001", CheckpointTyp.AUTOMATISCH, {"schritt": "freigegeben"}, 3, CheckpointStatus.AKTUELL, now + timedelta(minutes=10)),
    ]

    # Seq 2: settlement — 2 checkpoints, one KORRUPT
    s2 = CheckpointSequenz("WI-S-002")
    s2.checkpoints = [
        WorkflowCheckpoint("CP-004", "WI-S-002", CheckpointTyp.AUTOMATISCH, {"schritt": "berechnet"}, 1, CheckpointStatus.AKTUELL, now),
        WorkflowCheckpoint("CP-005", "WI-S-002", CheckpointTyp.NACH_FEHLER, {"schritt": "fehler"}, 2, CheckpointStatus.KORRUPT, now + timedelta(minutes=3)),
    ]

    # Seq 3: empty
    s3 = CheckpointSequenz("WI-LEER-003")

    return [s1, s2, s3]
