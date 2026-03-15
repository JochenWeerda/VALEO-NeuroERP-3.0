"""
Workflow-Versionierungs-Contracts — Wave 40, PKP-02
Versionierte Workflow-Definitionen, Instanzreferenzen auf Versionen,
Migrationsmodell und Sandbox-Versionsregeln.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class WorkflowDefinitionsStatus(str, Enum):
    ENTWURF = "ENTWURF"
    AKTIV = "AKTIV"
    VERALTET = "VERALTET"
    ARCHIVIERT = "ARCHIVIERT"


class WorkflowInstanzStatus(str, Enum):
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    ABGEBROCHEN = "ABGEBROCHEN"
    MIGRIERT = "MIGRIERT"
    PAUSIERT = "PAUSIERT"


class MigrationsTyp(str, Enum):
    KOMPATIBEL = "KOMPATIBEL"          # Automatisch, keine Datenverluste
    INKOMPATIBEL = "INKOMPATIBEL"      # Manueller Eingriff erforderlich
    BREAKING = "BREAKING"              # Bricht laufende Instanzen — verboten
    DEPRECATION = "DEPRECATION"        # Sanfte Abkündigung mit Frist


class MigrationsStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    UEBERSPRUNGEN = "UEBERSPRUNGEN"


class SandboxModus(str, Enum):
    EXAKTE_VERSION = "EXAKTE_VERSION"      # Sandbox läuft gegen genaue Version
    AKTUELLE_AKTIV = "AKTUELLE_AKTIV"     # Sandbox nimmt immer die aktive Version
    VORSCHAU = "VORSCHAU"                  # Sandbox läuft gegen ENTWURF-Version


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WorkflowDefinition:
    """Eine versionierte Workflow-Definition."""
    definition_id: str
    workflow_typ: str          # z.B. "kontrakt_annahme", "ap_approval"
    version: str               # Semver: "1.0.0", "2.1.3"
    status: WorkflowDefinitionsStatus
    erstellt_am: datetime
    tenant_id: str = ""        # "" = global (alle Tenants)
    beschreibung: str = ""
    schritte: list[str] = field(default_factory=list)   # Schritt-IDs
    metadaten: dict[str, str] = field(default_factory=dict)

    @property
    def versions_hash(self) -> str:
        """SHA256 über Definition-ID + Version + Schritte für Integritätsprüfung."""
        payload = json.dumps({
            "definition_id": self.definition_id,
            "version": self.version,
            "workflow_typ": self.workflow_typ,
            "schritte": sorted(self.schritte),
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    @property
    def ist_aktiv(self) -> bool:
        return self.status == WorkflowDefinitionsStatus.AKTIV

    def as_dict(self) -> dict[str, Any]:
        return {
            "definition_id": self.definition_id,
            "workflow_typ": self.workflow_typ,
            "version": self.version,
            "status": self.status.value,
            "erstellt_am": self.erstellt_am.isoformat(),
            "tenant_id": self.tenant_id,
            "beschreibung": self.beschreibung,
            "schritte": self.schritte,
            "schritte_anzahl": len(self.schritte),
            "versions_hash": self.versions_hash,
        }


@dataclass
class WorkflowInstanzReferenz:
    """Instanz-Referenz: bindet eine laufende Instanz an ihre Definition-Version."""
    instanz_id: str
    definition_id: str
    versions_snapshot: str    # gespeicherter versions_hash zum Startzeitpunkt
    gestartet_am: datetime
    instanz_status: WorkflowInstanzStatus
    aktueller_schritt: str = ""
    tenant_id: str = ""
    migrationspfad: list[str] = field(default_factory=list)  # bisherige Definition-IDs

    @property
    def wurde_migriert(self) -> bool:
        return len(self.migrationspfad) > 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "instanz_id": self.instanz_id,
            "definition_id": self.definition_id,
            "versions_snapshot": self.versions_snapshot,
            "gestartet_am": self.gestartet_am.isoformat(),
            "instanz_status": self.instanz_status.value,
            "aktueller_schritt": self.aktueller_schritt,
            "tenant_id": self.tenant_id,
            "wurde_migriert": self.wurde_migriert,
            "migrationspfad": self.migrationspfad,
        }


@dataclass
class MigrationsRegel:
    """Beschreibt eine erlaubte oder verbotene Migration zwischen Versionen."""
    regel_id: str
    von_version: str
    zu_version: str
    workflow_typ: str
    migrations_typ: MigrationsTyp
    beschreibung: str = ""
    automatisch_ausfuehrbar: bool = True
    migrationsskript: str = ""    # z.B. Skript-ID oder "" wenn manuell

    @property
    def ist_zulaessig(self) -> bool:
        """BREAKING-Migrationen sind grundsätzlich unzulässig."""
        return self.migrations_typ != MigrationsTyp.BREAKING

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "von_version": self.von_version,
            "zu_version": self.zu_version,
            "workflow_typ": self.workflow_typ,
            "migrations_typ": self.migrations_typ.value,
            "beschreibung": self.beschreibung,
            "automatisch_ausfuehrbar": self.automatisch_ausfuehrbar,
            "ist_zulaessig": self.ist_zulaessig,
        }


@dataclass
class MigrationsErgebnis:
    """Ergebnis einer Migrations-Prüfung oder -Ausführung."""
    instanz_id: str
    von_definition_id: str
    zu_definition_id: str
    status: MigrationsStatus
    migrations_typ: MigrationsTyp
    nachrichten: list[str] = field(default_factory=list)
    automatisch: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "instanz_id": self.instanz_id,
            "von_definition_id": self.von_definition_id,
            "zu_definition_id": self.zu_definition_id,
            "status": self.status.value,
            "migrations_typ": self.migrations_typ.value,
            "nachrichten": self.nachrichten,
            "automatisch": self.automatisch,
            "erfolgreich": self.status == MigrationsStatus.ABGESCHLOSSEN,
        }


@dataclass
class SandboxVersionsRegel:
    """Regelt welche Workflow-Version die Sandbox für einen Typ verwendet."""
    workflow_typ: str
    sandbox_modus: SandboxModus
    fixierte_version: str = ""   # Nur bei EXAKTE_VERSION
    tenant_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "workflow_typ": self.workflow_typ,
            "sandbox_modus": self.sandbox_modus.value,
            "fixierte_version": self.fixierte_version,
            "tenant_id": self.tenant_id,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def pruefe_migration(
    instanz: WorkflowInstanzReferenz,
    ziel_definition: WorkflowDefinition,
    regeln: list[MigrationsRegel] | None = None,
) -> MigrationsErgebnis:
    """
    Prüft ob eine Instanz auf eine neue Definition migriert werden kann.

    Logik:
    1. Passende Migrationsregel suchen (workflow_typ + von_version-Fragment)
    2. Keine Regel → KOMPATIBEL (unbekannte Versionssprünge werden optimistisch toleriert)
    3. BREAKING → FEHLGESCHLAGEN
    4. INKOMPATIBEL → AUSSTEHEND (manuell)
    5. KOMPATIBEL / DEPRECATION → ABGESCHLOSSEN (automatisch)
    """
    if regeln is None:
        regeln = get_default_migrationsregeln()

    passende = [
        r for r in regeln
        if r.workflow_typ == ziel_definition.workflow_typ
        and r.zu_version == ziel_definition.version
        and r.ist_zulaessig
    ]

    if not passende:
        # Kein Eintrag → optimistisch kompatibel
        return MigrationsErgebnis(
            instanz_id=instanz.instanz_id,
            von_definition_id=instanz.definition_id,
            zu_definition_id=ziel_definition.definition_id,
            status=MigrationsStatus.ABGESCHLOSSEN,
            migrations_typ=MigrationsTyp.KOMPATIBEL,
            nachrichten=["Keine explizite Migrationsregel gefunden — optimistisch kompatibel"],
            automatisch=True,
        )

    regel = passende[0]

    if regel.migrations_typ == MigrationsTyp.BREAKING:
        return MigrationsErgebnis(
            instanz_id=instanz.instanz_id,
            von_definition_id=instanz.definition_id,
            zu_definition_id=ziel_definition.definition_id,
            status=MigrationsStatus.FEHLGESCHLAGEN,
            migrations_typ=MigrationsTyp.BREAKING,
            nachrichten=[f"BREAKING-Migration von {regel.von_version} auf {regel.zu_version} ist unzulässig"],
            automatisch=False,
        )

    if regel.migrations_typ == MigrationsTyp.INKOMPATIBEL:
        return MigrationsErgebnis(
            instanz_id=instanz.instanz_id,
            von_definition_id=instanz.definition_id,
            zu_definition_id=ziel_definition.definition_id,
            status=MigrationsStatus.AUSSTEHEND,
            migrations_typ=MigrationsTyp.INKOMPATIBEL,
            nachrichten=[regel.beschreibung or "Manuelle Migration erforderlich"],
            automatisch=False,
        )

    return MigrationsErgebnis(
        instanz_id=instanz.instanz_id,
        von_definition_id=instanz.definition_id,
        zu_definition_id=ziel_definition.definition_id,
        status=MigrationsStatus.ABGESCHLOSSEN,
        migrations_typ=regel.migrations_typ,
        nachrichten=[regel.beschreibung or "Automatische Migration erfolgreich"],
        automatisch=regel.automatisch_ausfuehrbar,
    )


def ermittle_aktive_definition(
    workflow_typ: str,
    definitionen: list[WorkflowDefinition],
    tenant_id: str = "",
) -> WorkflowDefinition | None:
    """
    Gibt die aktive Definition für einen Workflow-Typ zurück.

    Tenant-spezifische Definition hat Vorrang vor globaler.
    """
    # Tenant-spezifisch zuerst
    if tenant_id:
        tenant_aktiv = [
            d for d in definitionen
            if d.workflow_typ == workflow_typ
            and d.status == WorkflowDefinitionsStatus.AKTIV
            and d.tenant_id == tenant_id
        ]
        if tenant_aktiv:
            return max(tenant_aktiv, key=lambda d: d.version)

    # Global
    global_aktiv = [
        d for d in definitionen
        if d.workflow_typ == workflow_typ
        and d.status == WorkflowDefinitionsStatus.AKTIV
        and d.tenant_id == ""
    ]
    if global_aktiv:
        return max(global_aktiv, key=lambda d: d.version)

    return None


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_workflow_definitionen() -> list[WorkflowDefinition]:
    """Gibt 6 Standard-Workflow-Definitionen zurück."""
    basis = datetime(2026, 1, 1)
    return [
        WorkflowDefinition(
            "WD-001", "kontrakt_annahme", "1.0.0", WorkflowDefinitionsStatus.VERALTET,
            basis, beschreibung="Kontrakt-Annahme v1 (Basis)",
            schritte=["WS-erfassen", "WS-qualitaet", "WS-freigabe"],
        ),
        WorkflowDefinition(
            "WD-002", "kontrakt_annahme", "2.0.0", WorkflowDefinitionsStatus.AKTIV,
            datetime(2026, 2, 1), beschreibung="Kontrakt-Annahme v2 mit Dual-Control",
            schritte=["WS-erfassen", "WS-qualitaet", "WS-dual-control", "WS-freigabe", "WS-settlement"],
        ),
        WorkflowDefinition(
            "WD-003", "ap_approval", "1.0.0", WorkflowDefinitionsStatus.AKTIV,
            datetime(2026, 1, 15), beschreibung="AP-Rechnungsfreigabe v1",
            schritte=["AP-erfassen", "AP-pruefen", "AP-freigeben", "AP-buchen"],
        ),
        WorkflowDefinition(
            "WD-004", "ap_approval", "1.1.0", WorkflowDefinitionsStatus.ENTWURF,
            datetime(2026, 3, 1), beschreibung="AP-Rechnungsfreigabe v1.1 — ESG-Klassifikation",
            schritte=["AP-erfassen", "AP-esg-check", "AP-pruefen", "AP-freigeben", "AP-buchen"],
        ),
        WorkflowDefinition(
            "WD-005", "zahlungslauf_freigabe", "1.0.0", WorkflowDefinitionsStatus.AKTIV,
            datetime(2026, 1, 1), beschreibung="Zahlungslauf-Freigabe 4-Augen",
            schritte=["ZL-erstellen", "ZL-pruefen", "ZL-freigeben", "ZL-ausfuehren"],
        ),
        WorkflowDefinition(
            "WD-006", "compliance_pruefung", "1.0.0", WorkflowDefinitionsStatus.AKTIV,
            datetime(2026, 2, 15), beschreibung="Compliance-Prüfung Standard",
            schritte=["CO-initiieren", "CO-dokumente", "CO-pruefen", "CO-zertifizieren"],
        ),
    ]


def get_default_migrationsregeln() -> list[MigrationsRegel]:
    """Gibt 5 Standard-Migrationsregeln zurück."""
    return [
        MigrationsRegel(
            "MR-001", "1.0.0", "2.0.0", "kontrakt_annahme",
            MigrationsTyp.INKOMPATIBEL,
            beschreibung="v1→v2: Dual-Control-Schritt manuell konfigurieren",
            automatisch_ausfuehrbar=False,
        ),
        MigrationsRegel(
            "MR-002", "1.0.0", "1.1.0", "ap_approval",
            MigrationsTyp.KOMPATIBEL,
            beschreibung="v1→v1.1: ESG-Check ist optional — abwärtskompatibel",
            automatisch_ausfuehrbar=True,
        ),
        MigrationsRegel(
            "MR-003", "1.1.0", "2.0.0", "ap_approval",
            MigrationsTyp.BREAKING,
            beschreibung="v1.1→v2: Schritt-IDs inkompatibel geändert — Migration gesperrt",
            automatisch_ausfuehrbar=False,
        ),
        MigrationsRegel(
            "MR-004", "1.0.0", "1.1.0", "zahlungslauf_freigabe",
            MigrationsTyp.DEPRECATION,
            beschreibung="v1→v1.1: v1.0 läuft bis 2026-12-31 weiter",
            automatisch_ausfuehrbar=True,
        ),
        MigrationsRegel(
            "MR-005", "1.0.0", "2.0.0", "compliance_pruefung",
            MigrationsTyp.KOMPATIBEL,
            beschreibung="v1→v2: Zusätzliche Dokument-Kategorie — rückwärtskompatibel",
            automatisch_ausfuehrbar=True,
        ),
    ]


def get_default_sandbox_regeln() -> list[SandboxVersionsRegel]:
    """Gibt 4 Standard-Sandbox-Versionsregeln zurück."""
    return [
        SandboxVersionsRegel("kontrakt_annahme", SandboxModus.AKTUELLE_AKTIV),
        SandboxVersionsRegel("ap_approval", SandboxModus.VORSCHAU),
        SandboxVersionsRegel("zahlungslauf_freigabe", SandboxModus.EXAKTE_VERSION, "1.0.0"),
        SandboxVersionsRegel("compliance_pruefung", SandboxModus.AKTUELLE_AKTIV),
    ]
