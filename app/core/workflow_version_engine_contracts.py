"""
workflow_version_engine_contracts.py — Versionierte Workflow Engine (Wave 86, Gap 011)

Versionierte Workflow-Definitionen mit automatischen Migrationsplänen.
Kein ungeplanter Workflow-Bruch bei Releases.

Gap 011: 0 ungeplante Workflow-Brüche bei Releases
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MigrationStrategie(str, Enum):
    """Strategie für die Workflow-Migration."""
    IN_PLACE      = "IN_PLACE"       # Laufende Instanzen direkt migrieren
    DUAL_RUN      = "DUAL_RUN"       # Alt + Neu parallel bis alle Instanzen beendet
    HARD_CUTOVER  = "HARD_CUTOVER"   # Sofortiger Schnitt — nur bei Breaking Changes mit Genehmigung
    ROLLBACK      = "ROLLBACK"       # Zurück auf Vorgängerversion


class AenderungsTyp(str, Enum):
    """Typ einer Workflow-Änderung (Semantic Versioning)."""
    PATCH = "PATCH"   # Fehlerbehebung, keine Schemaänderung — minor bump
    MINOR = "MINOR"   # Neue optionale Schritte, abwärtskompatibel
    MAJOR = "MAJOR"   # Breaking Change — Instanzen müssen migriert werden


class MigrationStatus(str, Enum):
    """Status eines Migrationsplans."""
    GEPLANT     = "GEPLANT"
    AKTIV       = "AKTIV"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    ZURUECKGEROLLT = "ZURUECKGEROLLT"


class BreakingChangeRisiko(str, Enum):
    """Risikobewertung einer Workflow-Änderung."""
    KEIN   = "KEIN"    # Patch — kein Risiko
    NIEDRIG = "NIEDRIG"  # Minor — kompatibel, aber prüfen
    HOCH   = "HOCH"    # Major — Breaking Change, Genehmigung nötig


# ---------------------------------------------------------------------------
# Workflow-Version
# ---------------------------------------------------------------------------

@dataclass
class WorkflowVersion:
    """
    Semantic-Version einer Workflow-Definition.

    Format: major.minor.patch
    - MAJOR: Breaking Change (Instanz-Migration nötig)
    - MINOR: Neue optionale Schritte (rückwärtskompatibel)
    - PATCH: Fehlerbehebung (kein Schema-Impact)
    """
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "WorkflowVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: "WorkflowVersion") -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkflowVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def ist_kompatibel_mit(self, andere: "WorkflowVersion") -> bool:
        """True wenn dieselbe Major-Version → kein Breaking Change."""
        return self.major == andere.major

    def aenderungs_typ(self, neue: "WorkflowVersion") -> AenderungsTyp:
        """Ermittelt den Änderungstyp zwischen dieser und einer neuen Version."""
        if neue.major != self.major:
            return AenderungsTyp.MAJOR
        if neue.minor != self.minor:
            return AenderungsTyp.MINOR
        return AenderungsTyp.PATCH

    def as_dict(self) -> dict:
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "version_str": str(self),
        }


# ---------------------------------------------------------------------------
# Workflow-Definition (versioniert)
# ---------------------------------------------------------------------------

@dataclass
class WorkflowDefinition:
    """
    Versionierte Workflow-Definition.

    name + version identifizieren die Definition eindeutig.
    schema_hash stellt sicher dass Schema-Änderungen erkannt werden.
    """
    name: str
    version: WorkflowVersion
    schritte: list[str]           # Geordnete Schritt-IDs
    schema_hash: str              # SHA-256 über Schritte + Config
    beschreibung: str = ""
    pflicht_felder: list[str] = field(default_factory=list)
    metadaten: dict[str, Any] = field(default_factory=dict)

    @property
    def version_key(self) -> str:
        return f"{self.name}@{self.version}"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version.as_dict(),
            "version_key": self.version_key,
            "schritte": self.schritte,
            "schema_hash": self.schema_hash,
            "beschreibung": self.beschreibung,
            "pflicht_felder": self.pflicht_felder,
        }


# ---------------------------------------------------------------------------
# Migrations-Schritt
# ---------------------------------------------------------------------------

@dataclass
class MigrationsSchritt:
    """
    Einzelner Schritt eines Migrationsplans.

    Transformiert laufende Instanzen von von_version auf bis_version.
    """
    schritt_id: str
    von_version: WorkflowVersion
    bis_version: WorkflowVersion
    strategie: MigrationStrategie
    transformation_beschreibung: str
    ist_umkehrbar: bool = True
    risiko: BreakingChangeRisiko = BreakingChangeRisiko.KEIN

    def as_dict(self) -> dict:
        return {
            "schritt_id": self.schritt_id,
            "von_version": str(self.von_version),
            "bis_version": str(self.bis_version),
            "strategie": self.strategie.value,
            "transformation_beschreibung": self.transformation_beschreibung,
            "ist_umkehrbar": self.ist_umkehrbar,
            "risiko": self.risiko.value,
        }


# ---------------------------------------------------------------------------
# Migrations-Plan
# ---------------------------------------------------------------------------

@dataclass
class MigrationsPlan:
    """
    Geordneter Plan zur Migration von Workflow-Instanzen.

    Ein Plan besteht aus einer oder mehreren MigrationsSchritten
    und definiert die Strategie für den Übergang.
    """
    plan_id: str
    workflow_name: str
    von_version: WorkflowVersion
    bis_version: WorkflowVersion
    schritte: list[MigrationsSchritt] = field(default_factory=list)
    status: MigrationStatus = MigrationStatus.GEPLANT
    genehmigungs_pflicht: bool = False

    @property
    def ist_breaking(self) -> bool:
        return self.von_version.aenderungs_typ(self.bis_version) == AenderungsTyp.MAJOR

    @property
    def anzahl_schritte(self) -> int:
        return len(self.schritte)

    @property
    def hoechstes_risiko(self) -> BreakingChangeRisiko:
        if not self.schritte:
            return BreakingChangeRisiko.KEIN
        risikoreihenfolge = [
            BreakingChangeRisiko.KEIN,
            BreakingChangeRisiko.NIEDRIG,
            BreakingChangeRisiko.HOCH,
        ]
        max_index = max(risikoreihenfolge.index(s.risiko) for s in self.schritte)
        return risikoreihenfolge[max_index]

    def as_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "workflow_name": self.workflow_name,
            "von_version": str(self.von_version),
            "bis_version": str(self.bis_version),
            "ist_breaking": self.ist_breaking,
            "anzahl_schritte": self.anzahl_schritte,
            "status": self.status.value,
            "genehmigungs_pflicht": self.genehmigungs_pflicht,
            "hoechstes_risiko": self.hoechstes_risiko.value,
            "schritte": [s.as_dict() for s in self.schritte],
        }


# ---------------------------------------------------------------------------
# Workflow Version Registry
# ---------------------------------------------------------------------------

@dataclass
class WorkflowVersionRegistry:
    """
    Zentrales Register aller versionierten Workflow-Definitionen.

    Speichert alle Versionen pro Workflow-Name und liefert
    automatisch Migrationspfade zwischen Versionen.
    """
    _definitionen: dict[str, list[WorkflowDefinition]] = field(default_factory=dict)

    def register(self, definition: WorkflowDefinition) -> None:
        """Registriert eine Workflow-Definition."""
        name = definition.name
        if name not in self._definitionen:
            self._definitionen[name] = []
        # Duplikat-Check
        for existing in self._definitionen[name]:
            if existing.version == definition.version:
                raise ValueError(
                    f"Version {definition.version} für '{name}' bereits registriert"
                )
        self._definitionen[name].append(definition)
        self._definitionen[name].sort(key=lambda d: d.version)

    def get_latest(self, name: str) -> WorkflowDefinition | None:
        """Gibt die neueste Version eines Workflows zurück."""
        versionen = self._definitionen.get(name, [])
        return versionen[-1] if versionen else None

    def get_version(self, name: str, version: WorkflowVersion) -> WorkflowDefinition | None:
        """Gibt eine spezifische Version zurück."""
        for d in self._definitionen.get(name, []):
            if d.version == version:
                return d
        return None

    def alle_versionen(self, name: str) -> list[WorkflowVersion]:
        """Alle bekannten Versionen eines Workflows (sortiert)."""
        return [d.version for d in self._definitionen.get(name, [])]

    def registrierte_workflows(self) -> list[str]:
        return list(self._definitionen.keys())

    @property
    def anzahl_workflows(self) -> int:
        return len(self._definitionen)

    @property
    def anzahl_definitionen_gesamt(self) -> int:
        return sum(len(v) for v in self._definitionen.values())


# ---------------------------------------------------------------------------
# Migrations-Sicherheitscheck
# ---------------------------------------------------------------------------

@dataclass
class MigrationsSicherheitsResult:
    """Ergebnis des Sicherheitschecks für einen Migrationsplan."""
    plan_id: str
    ist_sicher: bool
    risiko: BreakingChangeRisiko
    hinweise: list[str] = field(default_factory=list)
    blockierende_fehler: list[str] = field(default_factory=list)
    kpi_erfuellt: bool = True   # Kein ungeplanter Workflow-Bruch

    def as_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "ist_sicher": self.ist_sicher,
            "risiko": self.risiko.value,
            "hinweise": self.hinweise,
            "blockierende_fehler": self.blockierende_fehler,
            "kpi_erfuellt": self.kpi_erfuellt,
        }


def validate_migrations_sicherheit(
    plan: MigrationsPlan,
    aktive_instanzen: int = 0,
) -> MigrationsSicherheitsResult:
    """
    Prüft ob ein Migrationsplan sicher ausgeführt werden kann.

    KPI: 0 ungeplante Workflow-Brüche bei Releases.
    Ein Bruch tritt auf wenn:
    - MAJOR-Änderung ohne Genehmigung
    - HARD_CUTOVER mit aktiven Instanzen
    - Nicht-umkehrbarer Schritt bei HOCH-Risiko
    """
    fehler: list[str] = []
    hinweise: list[str] = []

    # Breaking Changes brauchen Genehmigung
    if plan.ist_breaking and not plan.genehmigungs_pflicht:
        fehler.append(
            "MAJOR-Änderung ohne genehmigungs_pflicht=True — "
            "Breaking Change muss explizit genehmigt werden"
        )

    # HARD_CUTOVER mit aktiven Instanzen
    for schritt in plan.schritte:
        if schritt.strategie == MigrationStrategie.HARD_CUTOVER and aktive_instanzen > 0:
            fehler.append(
                f"Schritt '{schritt.schritt_id}': HARD_CUTOVER mit {aktive_instanzen} "
                f"aktiven Instanzen — Datenverlust möglich"
            )

        if not schritt.ist_umkehrbar and schritt.risiko == BreakingChangeRisiko.HOCH:
            hinweise.append(
                f"Schritt '{schritt.schritt_id}': Nicht umkehrbar + HOCH-Risiko — "
                f"Backup vor Migration empfohlen"
            )

    if not plan.schritte:
        hinweise.append("Migrationsplan hat keine Schritte — NOOP")

    return MigrationsSicherheitsResult(
        plan_id=plan.plan_id,
        ist_sicher=len(fehler) == 0,
        risiko=plan.hoechstes_risiko,
        hinweise=hinweise,
        blockierende_fehler=fehler,
        kpi_erfuellt=len(fehler) == 0,
    )
