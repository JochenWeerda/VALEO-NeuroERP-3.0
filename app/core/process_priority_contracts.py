from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class AufgabenPrioritaet(str, Enum):
    KRITISCH = "KRITISCH"    # P0
    HOCH = "HOCH"            # P1
    MITTEL = "MITTEL"        # P2
    NIEDRIG = "NIEDRIG"      # P3
    HINTERGRUND = "HINTERGRUND"  # P4

class WarteschlangenStatus(str, Enum):
    WARTEND = "WARTEND"
    VERARBEITUNG = "VERARBEITUNG"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    ABGEBROCHEN = "ABGEBROCHEN"

PRIORITAET_GEWICHT = {
    AufgabenPrioritaet.KRITISCH: 0,
    AufgabenPrioritaet.HOCH: 1,
    AufgabenPrioritaet.MITTEL: 2,
    AufgabenPrioritaet.NIEDRIG: 3,
    AufgabenPrioritaet.HINTERGRUND: 4,
}

@dataclass
class PrioritaetsAufgabe:
    aufgabe_id: str
    aufgabe_typ: str
    prioritaet: AufgabenPrioritaet
    tenant_id: str
    nutzlast: dict = field(default_factory=dict)
    status: WarteschlangenStatus = WarteschlangenStatus.WARTEND
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    faellig_am: Optional[datetime] = None

    def sort_schluessel(self) -> tuple:
        """Returns (prioritaet_gewicht, erstellt_am) for queue ordering."""
        return (PRIORITAET_GEWICHT[self.prioritaet], self.erstellt_am)

@dataclass
class PrioritaetsWarteschlange:
    schlange_id: str
    aufgaben: list = field(default_factory=list)  # list[PrioritaetsAufgabe]

    def naechste_aufgabe(self) -> Optional[object]:
        """Returns WARTEND task with lowest sort_schluessel(), None if empty."""
        wartende = [a for a in self.aufgaben if a.status == WarteschlangenStatus.WARTEND]
        if not wartende:
            return None
        return min(wartende, key=lambda a: a.sort_schluessel())

    def aufgaben_nach_prioritaet(self) -> list:
        """Returns all WARTEND tasks sorted by sort_schluessel() ascending."""
        wartende = [a for a in self.aufgaben if a.status == WarteschlangenStatus.WARTEND]
        return sorted(wartende, key=lambda a: a.sort_schluessel())

    def warteschlangen_tiefe(self) -> dict:
        """Returns {AufgabenPrioritaet: count} for WARTEND tasks."""
        result = {p: 0 for p in AufgabenPrioritaet}
        for a in self.aufgaben:
            if a.status == WarteschlangenStatus.WARTEND:
                result[a.prioritaet] += 1
        return result

def get_default_warteschlangen() -> list:
    """Returns 2 default PrioritaetsWarteschlange instances."""
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    # Queue 1: mixed priorities
    q1 = PrioritaetsWarteschlange("WS-001")
    q1.aufgaben = [
        PrioritaetsAufgabe("AUF-001", "settlement_freigabe", AufgabenPrioritaet.KRITISCH, "TENANT-A", {}, WarteschlangenStatus.WARTEND, now + timedelta(minutes=1)),
        PrioritaetsAufgabe("AUF-002", "bericht_generieren", AufgabenPrioritaet.NIEDRIG, "TENANT-A", {}, WarteschlangenStatus.WARTEND, now + timedelta(minutes=2)),
        PrioritaetsAufgabe("AUF-003", "kontrakt_pruefung", AufgabenPrioritaet.HOCH, "TENANT-B", {}, WarteschlangenStatus.WARTEND, now),
        PrioritaetsAufgabe("AUF-004", "email_versand", AufgabenPrioritaet.HINTERGRUND, "TENANT-A", {}, WarteschlangenStatus.ABGESCHLOSSEN, now),
        PrioritaetsAufgabe("AUF-005", "daten_export", AufgabenPrioritaet.MITTEL, "TENANT-B", {}, WarteschlangenStatus.WARTEND, now + timedelta(minutes=3)),
    ]

    # Queue 2: empty
    q2 = PrioritaetsWarteschlange("WS-002")

    return [q1, q2]
