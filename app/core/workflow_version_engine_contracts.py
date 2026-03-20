"""
workflow_version_engine_contracts.py — Workflow-Versionierung (Wave 86, Gap 011)

Semantic Versioning für Workflow-Definitionen mit Migrationsplanung.

KPI: Alle Breaking Changes werden durch genehmigte MAJOR-Versionen abgesichert.
     HARD_CUTOVER darf nicht mit aktiven Instanzen durchgeführt werden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AenderungsTyp(str, Enum):
    """Klassifikation einer Workflow-Versionsänderung (SemVer-Analogie)."""
    PATCH = "PATCH"    # Nur Dokumentation, Texte, keine Prozessänderung
    MINOR = "MINOR"    # Neue optionale Schritte, abwärtskompatibel
    MAJOR = "MAJOR"    # Breaking Change — neue Pflichtschritte, gelöschte Übergänge


class MigrationsStrategie(str, Enum):
    """Strategie für laufende Instanzen bei einer Workflow-Version."""
    SOFT_UPGRADE  = "SOFT_UPGRADE"   # Instanzen können auf neue Version wechseln
    HARD_CUTOVER  = "HARD_CUTOVER"   # Alle Instanzen müssen sofort migrieren
    PARALLEL_RUN  = "PARALLEL_RUN"   # Alte + neue Version laufen gleichzeitig
    DRAIN         = "DRAIN"          # Keine neuen Instanzen; laufende beenden


class WorkflowStatus(str, Enum):
    """Veröffentlichungsstatus einer Workflow-Version."""
    ENTWURF       = "ENTWURF"
    REVIEW        = "REVIEW"
    FREIGEGEBEN   = "FREIGEGEBEN"
    VERALTET      = "VERALTET"
    ARCHIVIERT    = "ARCHIVIERT"


class RisikoStufe(str, Enum):
    """Bewertetes Migrationsrisiko."""
    NIEDRIG  = "NIEDRIG"
    MITTEL   = "MITTEL"
    HOCH     = "HOCH"
    KRITISCH = "KRITISCH"


# ---------------------------------------------------------------------------
# Versionsmodell
# ---------------------------------------------------------------------------

@dataclass
class WorkflowVersion:
    """Semantische Versionsnummer eines Workflows."""
    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        for name, val in [("major", self.major), ("minor", self.minor), ("patch", self.patch)]:
            if val < 0:
                raise ValueError(f"{name} darf nicht negativ sein")

    def als_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def aenderungs_typ(self, neue: "WorkflowVersion") -> AenderungsTyp:
        """Klassifiziert den Änderungstyp zwischen zwei Versionen."""
        if neue.major != self.major:
            return AenderungsTyp.MAJOR
        if neue.minor != self.minor:
            return AenderungsTyp.MINOR
        return AenderungsTyp.PATCH

    def ist_neuer_als(self, andere: "WorkflowVersion") -> bool:
        return (self.major, self.minor, self.patch) > (andere.major, andere.minor, andere.patch)

    def as_dict(self) -> dict:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "als_string": self.als_string(),
        }


# ---------------------------------------------------------------------------
# Workflow-Versionsdefinition
# ---------------------------------------------------------------------------

@dataclass
class WorkflowVersionDefinition:
    """Vollständige Definition einer Workflow-Version."""
    workflow_id: str
    name: str
    version: WorkflowVersion
    status: WorkflowStatus
    beschreibung: str
    aenderungsprotokoll: str        # Changelog für diese Version
    genehmigungs_pflicht: bool      # Muss explizit genehmigt werden (MAJOR)
    erstellt_von: str
    erstellt_am: str                # ISO-8601
    freigegeben_von: str = ""
    freigegeben_am: str = ""
    metadaten: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "version": self.version.als_string(),
            "status": self.status.value,
            "beschreibung": self.beschreibung,
            "genehmigungs_pflicht": self.genehmigungs_pflicht,
            "erstellt_von": self.erstellt_von,
            "erstellt_am": self.erstellt_am,
            "freigegeben_von": self.freigegeben_von,
        }


# ---------------------------------------------------------------------------
# Migrationsplan
# ---------------------------------------------------------------------------

@dataclass
class WorkflowMigrationsplan:
    """Plan für den Übergang von einer Workflow-Version auf eine andere."""
    plan_id: str
    workflow_id: str
    von_version: WorkflowVersion
    zu_version: WorkflowVersion
    strategie: MigrationsStrategie
    risiko: RisikoStufe
    reversibel: bool
    genehmigungs_pflicht: bool
    beschreibung: str
    validiert_am: str = ""    # ISO-8601; leer = noch nicht validiert
    genehmigt_von: str = ""

    @property
    def aenderungs_typ(self) -> AenderungsTyp:
        return self.von_version.aenderungs_typ(self.zu_version)

    def as_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "workflow_id": self.workflow_id,
            "von_version": self.von_version.als_string(),
            "zu_version": self.zu_version.als_string(),
            "aenderungs_typ": self.aenderungs_typ.value,
            "strategie": self.strategie.value,
            "risiko": self.risiko.value,
            "reversibel": self.reversibel,
            "genehmigungs_pflicht": self.genehmigungs_pflicht,
            "genehmigt_von": self.genehmigt_von,
        }


# ---------------------------------------------------------------------------
# Migrations-Sicherheitsprüfung
# ---------------------------------------------------------------------------

@dataclass
class MigrationsSicherheitsResult:
    """Ergebnis der Sicherheitsprüfung vor einer Workflow-Migration."""
    plan_id: str
    erlaubt: bool
    blockierende_regeln: list[str] = field(default_factory=list)
    warnungen: list[str] = field(default_factory=list)
    hinweise: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "erlaubt": self.erlaubt,
            "blockierende_regeln": self.blockierende_regeln,
            "warnungen": self.warnungen,
            "hinweise": self.hinweise,
        }


def validate_migrations_sicherheit(
    plan: WorkflowMigrationsplan,
    aktive_instanzen: int = 0,
) -> MigrationsSicherheitsResult:
    """
    Prüft ob eine Workflow-Migration sicher durchgeführt werden kann.

    Blockierende Regeln (Gap 011):
    - MAJOR-Änderung ohne genehmigungs_pflicht=True → blockiert
    - HARD_CUTOVER mit aktiven Instanzen > 0 → blockiert

    Warnungen (nicht blockierend):
    - HARD_CUTOVER mit > 0 Instanzen wird gewarnt
    - PARALLEL_RUN mit KRITISCHEM Risiko

    Hinweise:
    - Irreversible HOCH-Risiko-Migrationen
    """
    blockierend: list[str] = []
    warnungen: list[str] = []
    hinweise: list[str] = []

    # MAJOR ohne Genehmigungspflicht → blockiert
    if plan.aenderungs_typ == AenderungsTyp.MAJOR and not plan.genehmigungs_pflicht:
        blockierend.append(
            f"MAJOR-Änderung ({plan.von_version.als_string()} → {plan.zu_version.als_string()}) "
            f"erfordert genehmigungs_pflicht=True"
        )

    # HARD_CUTOVER mit aktiven Instanzen → blockiert
    if plan.strategie == MigrationsStrategie.HARD_CUTOVER and aktive_instanzen > 0:
        blockierend.append(
            f"HARD_CUTOVER nicht möglich: {aktive_instanzen} aktive Instanzen laufen noch. "
            f"Strategie DRAIN oder PARALLEL_RUN verwenden."
        )

    # Nicht-reversibel + hohes Risiko → Hinweis
    if not plan.reversibel and plan.risiko in (RisikoStufe.HOCH, RisikoStufe.KRITISCH):
        hinweise.append(
            f"Irreversible Migration mit Risiko {plan.risiko.value} — "
            f"Datenbankbackup vor Durchführung empfohlen"
        )

    # PARALLEL_RUN mit KRITISCH → Warnung
    if plan.strategie == MigrationsStrategie.PARALLEL_RUN and plan.risiko == RisikoStufe.KRITISCH:
        warnungen.append(
            "PARALLEL_RUN mit KRITISCHEM Risiko erfordert erhöhte Beobachtung"
        )

    return MigrationsSicherheitsResult(
        plan_id=plan.plan_id,
        erlaubt=len(blockierend) == 0,
        blockierende_regeln=blockierend,
        warnungen=warnungen,
        hinweise=hinweise,
    )


# ---------------------------------------------------------------------------
# Versionshistorie
# ---------------------------------------------------------------------------

@dataclass
class WorkflowVersionsHistorie:
    """Historische Versionsliste eines Workflows."""
    workflow_id: str
    versionen: list[WorkflowVersionDefinition] = field(default_factory=list)

    @property
    def aktuelle_version(self) -> WorkflowVersionDefinition | None:
        freigegebene = [
            v for v in self.versionen
            if v.status == WorkflowStatus.FREIGEGEBEN
        ]
        if not freigegebene:
            return None
        return max(freigegebene, key=lambda v: (v.version.major, v.version.minor, v.version.patch))

    @property
    def anzahl_major_releases(self) -> int:
        seen: set[int] = set()
        for v in self.versionen:
            seen.add(v.version.major)
        return len(seen)

    def get_version(self, major: int, minor: int, patch: int) -> WorkflowVersionDefinition | None:
        return next(
            (v for v in self.versionen
             if v.version.major == major and v.version.minor == minor and v.version.patch == patch),
            None,
        )

    def as_dict(self) -> dict:
        aktuelle = self.aktuelle_version
        return {
            "workflow_id": self.workflow_id,
            "anzahl_versionen": len(self.versionen),
            "anzahl_major_releases": self.anzahl_major_releases,
            "aktuelle_version": aktuelle.version.als_string() if aktuelle else None,
        }
