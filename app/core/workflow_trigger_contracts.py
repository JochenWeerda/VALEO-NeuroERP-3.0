from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class TriggerTyp(str, Enum):
    ZEITPLAN = "ZEITPLAN"           # Cron-like schedule
    EREIGNIS = "EREIGNIS"           # Domain event
    SCHWELLWERT = "SCHWELLWERT"     # Threshold exceeded
    MANUELL = "MANUELL"             # Manual activation
    ABHAENGIGKEIT = "ABHAENGIGKEIT" # Another workflow completed


class TriggerStatus(str, Enum):
    AKTIV = "AKTIV"
    INAKTIV = "INAKTIV"
    AUSGELOEST = "AUSGELOEST"
    FEHLER = "FEHLER"


class BedingungsOperator(str, Enum):
    GLEICH = "GLEICH"               # ==
    UNGLEICH = "UNGLEICH"           # !=
    GROESSER = "GROESSER"           # >
    KLEINER = "KLEINER"             # <
    GROESSER_GLEICH = "GROESSER_GLEICH"  # >=
    KLEINER_GLEICH = "KLEINER_GLEICH"    # <=
    ENTHAELT = "ENTHAELT"           # in


@dataclass
class TriggerBedingung:
    feld: str
    operator: BedingungsOperator
    wert: object                    # comparison value

    def pruefe(self, kontext: dict) -> bool:
        """
        Evaluates the condition against kontext[feld].
        Returns False if feld not in kontext.
        GLEICH: ==, UNGLEICH: !=, GROESSER: >, KLEINER: <,
        GROESSER_GLEICH: >=, KLEINER_GLEICH: <=,
        ENTHAELT: wert in kontext[feld] (works for strings and lists)
        Returns False on TypeError/ValueError.
        """
        if self.feld not in kontext:
            return False
        try:
            aktuell = kontext[self.feld]
            if self.operator == BedingungsOperator.GLEICH:
                return aktuell == self.wert
            elif self.operator == BedingungsOperator.UNGLEICH:
                return aktuell != self.wert
            elif self.operator == BedingungsOperator.GROESSER:
                return aktuell > self.wert
            elif self.operator == BedingungsOperator.KLEINER:
                return aktuell < self.wert
            elif self.operator == BedingungsOperator.GROESSER_GLEICH:
                return aktuell >= self.wert
            elif self.operator == BedingungsOperator.KLEINER_GLEICH:
                return aktuell <= self.wert
            else:  # ENTHAELT
                return self.wert in aktuell
        except (TypeError, ValueError):
            return False


@dataclass
class WorkflowTrigger:
    trigger_id: str
    workflow_typ: str
    trigger_typ: TriggerTyp
    bedingungen: list = field(default_factory=list)  # list[TriggerBedingung], ALL must be True
    status: TriggerStatus = TriggerStatus.AKTIV
    beschreibung: str = ""
    zuletzt_ausgeloest_am: Optional[datetime] = None

    def pruefe_bedingungen(self, kontext: dict) -> bool:
        """
        Returns True if all bedingungen.pruefe(kontext) are True.
        Returns True for empty bedingungen (no conditions = always fires).
        Returns False if status != AKTIV.
        """
        if self.status != TriggerStatus.AKTIV:
            return False
        return all(b.pruefe(kontext) for b in self.bedingungen)


def get_default_workflow_trigger() -> list:
    return [
        WorkflowTrigger(
            "WT-001", "kontrakt_freigabe", TriggerTyp.SCHWELLWERT, [
                TriggerBedingung("menge_tonnen", BedingungsOperator.GROESSER_GLEICH, 100),
                TriggerBedingung("status", BedingungsOperator.GLEICH, "GEPRUEFT"),
            ], TriggerStatus.AKTIV, "Freigabe ab 100t"
        ),
        WorkflowTrigger(
            "WT-002", "settlement_automatisch", TriggerTyp.EREIGNIS, [
                TriggerBedingung("ereignis_typ", BedingungsOperator.GLEICH, "WAAGE_ABGESCHLOSSEN"),
            ], TriggerStatus.AKTIV, "Auto-Settlement nach Waage"
        ),
        WorkflowTrigger(
            "WT-003", "mahnlauf", TriggerTyp.ZEITPLAN, [],
            TriggerStatus.AKTIV, "Täglicher Mahnlauf (keine Bedingungen)"
        ),
        WorkflowTrigger(
            "WT-004", "archivierung", TriggerTyp.ABHAENGIGKEIT, [
                TriggerBedingung("abgeschlossen_workflows", BedingungsOperator.ENTHAELT, "settlement"),
            ], TriggerStatus.INAKTIV, "Archivierung nach Settlement (inaktiv)"
        ),
        WorkflowTrigger(
            "WT-005", "qualitaets_eskalation", TriggerTyp.SCHWELLWERT, [
                TriggerBedingung("feuchte_pct", BedingungsOperator.GROESSER, 15.0),
            ], TriggerStatus.AKTIV, "Eskalation bei hoher Feuchte"
        ),
    ]
