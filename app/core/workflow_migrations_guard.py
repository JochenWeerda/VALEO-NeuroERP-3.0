"""
Workflow-Migrations-Guard — Wave 26 AP2

Prueft vor jedem Release, ob eine Aenderung an einer Workflow-Definition
Breaking Changes einfuehrt (Gap 011: 0 ungeplante Workflow-Brueche bei Releases).

Klassifizierung:
  SAFE    — keine Inkompatibilitaeten, Migration kann automatisch erfolgen
  WARNUNG — rueckwaertskompatible Aenderungen, manuelle Pruefung empfohlen
  BREAKING — Inkompatibel, Migration blockiert bis manueller Freigabe

Erkannte Breaking Changes:
  - Pflichtschritt entfernt
  - Terminalzustand geaendert (VERBUCHT/ABGELEHNT umbenannt/entfernt)
  - Schritt-Rolle entfernt (RBAC-Verletzung moeglich)
  - Schema-Version zurueckgesetzt (Downgrade)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


MIGRATIONS_GUARD_SCHEMA_VERSION = 1


class MigrationRisikoKlasse(str, Enum):
    SAFE = "SAFE"
    WARNUNG = "WARNUNG"
    BREAKING = "BREAKING"


class MigrationViolationCode(str, Enum):
    PFLICHTSCHRITT_ENTFERNT = "PFLICHTSCHRITT_ENTFERNT"
    TERMINALZUSTAND_GEAENDERT = "TERMINALZUSTAND_GEAENDERT"
    SCHRITT_ROLLE_ENTFERNT = "SCHRITT_ROLLE_ENTFERNT"
    SCHEMA_VERSION_DOWNGRADE = "SCHEMA_VERSION_DOWNGRADE"
    SCHRITT_REIHENFOLGE_UMGEKEHRT = "SCHRITT_REIHENFOLGE_UMGEKEHRT"
    NEUER_PFLICHTSCHRITT_OHNE_MIGRATION = "NEUER_PFLICHTSCHRITT_OHNE_MIGRATION"


# ---------------------------------------------------------------------------
# Snapshot-Struktur
# ---------------------------------------------------------------------------

@dataclass
class WorkflowSchrittSnapshot:
    """Snapshot eines einzelnen Workflow-Schritts fuer Migrationsvergleich."""

    schritt_id: str
    pflicht: bool
    reihenfolge: int
    terminal: bool = False          # Endzustand (kein Folgeschritt)
    rolle: str = ""                 # Ausfuehrender Rolle-Code
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "schritt_id": self.schritt_id,
            "pflicht": self.pflicht,
            "reihenfolge": self.reihenfolge,
            "terminal": self.terminal,
            "rolle": self.rolle,
            "schema_version": self.schema_version,
        }


@dataclass
class WorkflowDefinitionSnapshot:
    """
    Vollstaendiger Snapshot einer Workflow-Definition zu einem Versions-Zeitpunkt.
    Wird als Basis fuer den Migrationsvergleich verwendet.
    """

    prozess_key: str
    version: str                    # Semver: "1.0", "1.1", "2.0"
    schema_version: int
    schritte: list[WorkflowSchrittSnapshot] = field(default_factory=list)

    @property
    def terminal_schritte(self) -> list[str]:
        return [s.schritt_id for s in self.schritte if s.terminal]

    @property
    def pflicht_schritte(self) -> set[str]:
        return {s.schritt_id for s in self.schritte if s.pflicht}

    @property
    def rollen_mapping(self) -> dict[str, str]:
        return {s.schritt_id: s.rolle for s in self.schritte if s.rolle}

    def as_dict(self) -> dict:
        return {
            "prozess_key": self.prozess_key,
            "version": self.version,
            "schema_version": self.schema_version,
            "schritt_count": len(self.schritte),
            "pflicht_schritt_count": len(self.pflicht_schritte),
            "terminal_schritte": self.terminal_schritte,
        }


# ---------------------------------------------------------------------------
# Violations
# ---------------------------------------------------------------------------

@dataclass
class MigrationViolation:
    code: MigrationViolationCode
    risiko: MigrationRisikoKlasse
    schritt_id: Optional[str]
    message: str

    def as_dict(self) -> dict:
        return {
            "code": self.code.value,
            "risiko": self.risiko.value,
            "schritt_id": self.schritt_id,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Migrations-Check-Ergebnis
# ---------------------------------------------------------------------------

@dataclass
class MigrationCompatibilityResult:
    prozess_key: str
    von_version: str
    zu_version: str
    risiko_klasse: MigrationRisikoKlasse
    violations: list[MigrationViolation] = field(default_factory=list)
    schema_version: int = MIGRATIONS_GUARD_SCHEMA_VERSION

    @property
    def migration_erlaubt(self) -> bool:
        return self.risiko_klasse != MigrationRisikoKlasse.BREAKING

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def as_dict(self) -> dict:
        return {
            "prozess_key": self.prozess_key,
            "von_version": self.von_version,
            "zu_version": self.zu_version,
            "risiko_klasse": self.risiko_klasse.value,
            "migration_erlaubt": self.migration_erlaubt,
            "violation_count": self.violation_count,
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP2: validate_workflow_migration()
# ---------------------------------------------------------------------------

def validate_workflow_migration(
    alt: WorkflowDefinitionSnapshot,
    neu: WorkflowDefinitionSnapshot,
) -> MigrationCompatibilityResult:
    """
    Prueft ob Migration von alt → neu sicher, mit Warnung oder BREAKING ist.

    Prueft:
    1. Pflichtschritte: entfernte = BREAKING
    2. Neue Pflichtschritte ohne Default-Wert = BREAKING
    3. Terminalzustaende veraendert = BREAKING
    4. Rollen entfernt = WARNUNG
    5. Reihenfolge umgekehrt (relative Ordnung) = WARNUNG
    6. Schema-Version Downgrade = BREAKING
    """
    violations: list[MigrationViolation] = []

    # 1. Schema-Version Downgrade
    if neu.schema_version < alt.schema_version:
        violations.append(MigrationViolation(
            code=MigrationViolationCode.SCHEMA_VERSION_DOWNGRADE,
            risiko=MigrationRisikoKlasse.BREAKING,
            schritt_id=None,
            message=f"Schema-Version Downgrade: {alt.schema_version} → {neu.schema_version}",
        ))

    neu_ids = {s.schritt_id for s in neu.schritte}
    alt_ids = {s.schritt_id for s in alt.schritte}

    # 2. Pflichtschritte entfernt
    entfernte_pflicht = alt.pflicht_schritte - neu_ids
    for sid in sorted(entfernte_pflicht):
        violations.append(MigrationViolation(
            code=MigrationViolationCode.PFLICHTSCHRITT_ENTFERNT,
            risiko=MigrationRisikoKlasse.BREAKING,
            schritt_id=sid,
            message=f"Pflichtschritt '{sid}' wurde entfernt — laufende Instanzen werden blockiert",
        ))

    # 3. Neue Pflichtschritte die in alten Instanzen nicht existieren
    neue_pflicht = neu.pflicht_schritte - alt_ids
    for sid in sorted(neue_pflicht):
        violations.append(MigrationViolation(
            code=MigrationViolationCode.NEUER_PFLICHTSCHRITT_OHNE_MIGRATION,
            risiko=MigrationRisikoKlasse.BREAKING,
            schritt_id=sid,
            message=f"Neuer Pflichtschritt '{sid}' — Altinstanzen haben keinen Zustand fuer diesen Schritt",
        ))

    # 4. Terminalzustaende veraendert
    alt_terminal = set(alt.terminal_schritte)
    neu_terminal = set(neu.terminal_schritte)
    entfernte_terminal = alt_terminal - neu_terminal
    for sid in sorted(entfernte_terminal):
        violations.append(MigrationViolation(
            code=MigrationViolationCode.TERMINALZUSTAND_GEAENDERT,
            risiko=MigrationRisikoKlasse.BREAKING,
            schritt_id=sid,
            message=f"Terminalzustand '{sid}' entfernt — abgeschlossene Instanzen in inkonsistentem Zustand",
        ))

    # 5. Rollen entfernt (WARNUNG)
    alt_rollen = alt.rollen_mapping
    neu_rollen = neu.rollen_mapping
    for sid in alt_rollen:
        if sid in neu_rollen and not neu_rollen[sid] and alt_rollen[sid]:
            violations.append(MigrationViolation(
                code=MigrationViolationCode.SCHRITT_ROLLE_ENTFERNT,
                risiko=MigrationRisikoKlasse.WARNUNG,
                schritt_id=sid,
                message=f"Rolle fuer Schritt '{sid}' entfernt — RBAC-Pruefung koennte fehlschlagen",
            ))

    # 6. Relative Reihenfolge umgekehrt (WARNUNG, nur fuer gemeinsame Schritte)
    gemeinsame = [s for s in alt.schritte if s.schritt_id in neu_ids]
    if len(gemeinsame) >= 2:
        neu_map = {s.schritt_id: s.reihenfolge for s in neu.schritte}
        for i, a in enumerate(gemeinsame):
            for b in gemeinsame[i + 1:]:
                alt_ord = a.reihenfolge < b.reihenfolge
                neu_a = neu_map.get(a.schritt_id)
                neu_b = neu_map.get(b.schritt_id)
                if neu_a is not None and neu_b is not None:
                    neu_ord = neu_a < neu_b
                    if alt_ord != neu_ord:
                        violations.append(MigrationViolation(
                            code=MigrationViolationCode.SCHRITT_REIHENFOLGE_UMGEKEHRT,
                            risiko=MigrationRisikoKlasse.WARNUNG,
                            schritt_id=a.schritt_id,
                            message=f"Relative Reihenfolge '{a.schritt_id}' ↔ '{b.schritt_id}' wurde umgekehrt",
                        ))
                        break  # Nur erste Verletzung pro Paar

    # Gesamtrisiko: hoechste Einzelklasse
    if any(v.risiko == MigrationRisikoKlasse.BREAKING for v in violations):
        gesamt = MigrationRisikoKlasse.BREAKING
    elif any(v.risiko == MigrationRisikoKlasse.WARNUNG for v in violations):
        gesamt = MigrationRisikoKlasse.WARNUNG
    else:
        gesamt = MigrationRisikoKlasse.SAFE

    return MigrationCompatibilityResult(
        prozess_key=alt.prozess_key,
        von_version=alt.version,
        zu_version=neu.version,
        risiko_klasse=gesamt,
        violations=violations,
    )
