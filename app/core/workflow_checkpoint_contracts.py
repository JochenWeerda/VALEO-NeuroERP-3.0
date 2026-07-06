"""
Workflow Checkpoint Contracts
Wave 43 — Checkpoints & Cross-Domain Projections
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum


class CheckpointStatus(str, Enum):
    ERSTELLT = "ERSTELLT"
    GUELTIG = "GUELTIG"
    VERALTET = "VERALTET"
    WIEDERHERGESTELLT = "WIEDERHERGESTELLT"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"


class CheckpointIntervall(str, Enum):
    NACH_JEDEM_SCHRITT = "NACH_JEDEM_SCHRITT"
    ALLE_5_SCHRITTE = "ALLE_5_SCHRITTE"
    ALLE_10_SCHRITTE = "ALLE_10_SCHRITTE"
    MANUELL = "MANUELL"


class WiederherstellungsErgebnis(str, Enum):
    ERFOLGREICH = "ERFOLGREICH"
    CHECKPOINT_VERALTET = "CHECKPOINT_VERALTET"
    CHECKPOINT_FEHLERHAFT = "CHECKPOINT_FEHLERHAFT"
    KEIN_CHECKPOINT = "KEIN_CHECKPOINT"


@dataclass
class WorkflowCheckpoint:
    checkpoint_id: str
    workflow_instanz_id: str
    schritt_id: str
    status: CheckpointStatus
    erstellt_am: datetime.datetime
    tenant_id: str
    zustand: dict = field(default_factory=dict)
    schritte_ausgefuehrt: int = 0

    @property
    def alter_minuten(self) -> float:
        delta = datetime.datetime.utcnow() - self.erstellt_am
        return round(delta.total_seconds() / 60, 2)

    def ist_veraltet(self, max_alter_minuten: float = 60.0) -> bool:
        return self.alter_minuten > max_alter_minuten

    @property
    def ist_gueltig(self) -> bool:
        return self.status == CheckpointStatus.GUELTIG

    def as_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "schritt_id": self.schritt_id,
            "status": self.status.value,
            "erstellt_am": self.erstellt_am.isoformat(),
            "tenant_id": self.tenant_id,
            "schritte_ausgefuehrt": self.schritte_ausgefuehrt,
            "zustand_groesse": len(self.zustand),
            "ist_gueltig": self.ist_gueltig,
        }


@dataclass
class CheckpointRegel:
    regel_id: str
    workflow_typ: str
    intervall: CheckpointIntervall
    max_checkpoints: int = 10
    max_alter_minuten: float = 60.0

    def pruefe_intervall(self, schritte_ausgefuehrt: int) -> bool:
        if self.intervall == CheckpointIntervall.NACH_JEDEM_SCHRITT:
            return schritte_ausgefuehrt > 0
        if self.intervall == CheckpointIntervall.ALLE_5_SCHRITTE:
            return schritte_ausgefuehrt > 0 and schritte_ausgefuehrt % 5 == 0
        if self.intervall == CheckpointIntervall.ALLE_10_SCHRITTE:
            return schritte_ausgefuehrt > 0 and schritte_ausgefuehrt % 10 == 0
        # MANUELL
        return False

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "workflow_typ": self.workflow_typ,
            "intervall": self.intervall.value,
            "max_checkpoints": self.max_checkpoints,
            "max_alter_minuten": self.max_alter_minuten,
        }


@dataclass
class CheckpointWiederherstellung:
    wiederherstellung_id: str
    workflow_instanz_id: str
    checkpoint_id: str
    ergebnis: WiederherstellungsErgebnis
    naechster_schritt: str = ""
    nachrichten: list = field(default_factory=list)

    @property
    def kann_fortgesetzt_werden(self) -> bool:
        return self.ergebnis == WiederherstellungsErgebnis.ERFOLGREICH


def erstelle_checkpoint(
    checkpoint_id: str,
    workflow_instanz_id: str,
    schritt_id: str,
    tenant_id: str,
    zustand=None,
    schritte_ausgefuehrt: int = 0,
    erstellt_am=None,
) -> WorkflowCheckpoint:
    return WorkflowCheckpoint(
        checkpoint_id=checkpoint_id,
        workflow_instanz_id=workflow_instanz_id,
        schritt_id=schritt_id,
        status=CheckpointStatus.GUELTIG,
        erstellt_am=erstellt_am if erstellt_am is not None else datetime.datetime.utcnow(),
        tenant_id=tenant_id,
        zustand=zustand if zustand is not None else {},
        schritte_ausgefuehrt=schritte_ausgefuehrt,
    )


def stelle_checkpoint_wieder_her(
    wiederherstellung_id: str,
    workflow_instanz_id: str,
    checkpoint: WorkflowCheckpoint,
    max_alter_minuten: float = 60.0,
) -> CheckpointWiederherstellung:
    if checkpoint.status == CheckpointStatus.FEHLGESCHLAGEN:
        return CheckpointWiederherstellung(
            wiederherstellung_id=wiederherstellung_id,
            workflow_instanz_id=workflow_instanz_id,
            checkpoint_id=checkpoint.checkpoint_id,
            ergebnis=WiederherstellungsErgebnis.CHECKPOINT_FEHLERHAFT,
            naechster_schritt="",
            nachrichten=["Checkpoint ist fehlgeschlagen und kann nicht wiederhergestellt werden."],
        )
    if checkpoint.ist_veraltet(max_alter_minuten):
        return CheckpointWiederherstellung(
            wiederherstellung_id=wiederherstellung_id,
            workflow_instanz_id=workflow_instanz_id,
            checkpoint_id=checkpoint.checkpoint_id,
            ergebnis=WiederherstellungsErgebnis.CHECKPOINT_VERALTET,
            naechster_schritt="",
            nachrichten=["Checkpoint ist veraltet."],
        )
    naechster_schritt = checkpoint.zustand.get("naechster_schritt", checkpoint.schritt_id)
    return CheckpointWiederherstellung(
        wiederherstellung_id=wiederherstellung_id,
        workflow_instanz_id=workflow_instanz_id,
        checkpoint_id=checkpoint.checkpoint_id,
        ergebnis=WiederherstellungsErgebnis.ERFOLGREICH,
        naechster_schritt=naechster_schritt,
        nachrichten=["Checkpoint erfolgreich wiederhergestellt."],
    )


def get_default_checkpoint_regeln() -> list:
    return [
        CheckpointRegel(
            regel_id="CR-001",
            workflow_typ="kontrakt_annahme",
            intervall=CheckpointIntervall.NACH_JEDEM_SCHRITT,
            max_checkpoints=5,
            max_alter_minuten=120.0,
        ),
        CheckpointRegel(
            regel_id="CR-002",
            workflow_typ="ap_approval",
            intervall=CheckpointIntervall.ALLE_5_SCHRITTE,
            max_checkpoints=10,
            max_alter_minuten=60.0,
        ),
        CheckpointRegel(
            regel_id="CR-003",
            workflow_typ="settlement_freigabe",
            intervall=CheckpointIntervall.ALLE_10_SCHRITTE,
            max_checkpoints=3,
            max_alter_minuten=240.0,
        ),
        CheckpointRegel(
            regel_id="CR-004",
            workflow_typ="compliance_pruefung",
            intervall=CheckpointIntervall.MANUELL,
            max_checkpoints=20,
            max_alter_minuten=1440.0,
        ),
    ]
