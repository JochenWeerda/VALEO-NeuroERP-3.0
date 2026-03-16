"""
Workflow Schema Versioning and Migration Guards — Wave 57
Versionierte Workflow-Schemata, Migrationspfade und Breaking-Change-Detection.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class VersionsStatus(str, Enum):
    ENTWURF = "ENTWURF"
    AKTIV = "AKTIV"
    VERALTET = "VERALTET"
    ZURUECKGEZOGEN = "ZURUECKGEZOGEN"


class MigrationsTyp(str, Enum):
    VORWAERTS = "VORWAERTS"          # Upgrade
    RUECKWAERTS = "RUECKWAERTS"      # Downgrade
    DATENMIGRATION = "DATENMIGRATION"


class KompatibilitaetsTyp(str, Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"    # Backward + forward compatible
    RUECKWAERTS = "RUECKWAERTS"      # Only backward compatible
    BRECHEND = "BRECHEND"            # Breaking change


@dataclass
class WorkflowSchemaVersion:
    schema_id: str
    workflow_typ: str
    version: str                     # semver e.g. "1.0.0"
    status: VersionsStatus = VersionsStatus.ENTWURF
    kompatibilitaet: KompatibilitaetsTyp = KompatibilitaetsTyp.VOLLSTAENDIG
    aenderungsbeschreibung: str = ""
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    aktiviert_am: Optional[datetime] = None

    def ist_produktiv(self) -> bool:
        return self.status == VersionsStatus.AKTIV

    def version_tuple(self) -> tuple:
        """Parses 'major.minor.patch' into (int, int, int). Returns (0,0,0) on error."""
        try:
            parts = self.version.split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            return (0, 0, 0)


@dataclass
class MigrationsSchritt:
    schritt_id: str
    migrations_typ: MigrationsTyp
    von_version: str
    zu_version: str
    beschreibung: str = ""
    ist_rueckwaerts_kompatibel: bool = True


@dataclass
class MigrationsGuard:
    guard_id: str
    workflow_typ: str
    versionen: list = field(default_factory=list)   # list[WorkflowSchemaVersion]
    migrationen: list = field(default_factory=list)  # list[MigrationsSchritt]

    def aktive_version(self) -> Optional[object]:
        """Returns the AKTIV version, or None."""
        aktive = [v for v in self.versionen if v.status == VersionsStatus.AKTIV]
        return aktive[0] if aktive else None

    def neueste_version(self) -> Optional[object]:
        """Returns version with highest version_tuple(), regardless of status."""
        if not self.versionen:
            return None
        return max(self.versionen, key=lambda v: v.version_tuple())

    def hat_brechende_aenderung(self, von: str, zu: str) -> bool:
        """
        Returns True if any MigrationsSchritt between von_version and zu_version
        has ist_rueckwaerts_kompatibel=False, or if the target WorkflowSchemaVersion
        has kompatibilitaet=BRECHEND.
        Also returns True if target version has kompatibilitaet==BRECHEND.
        """
        for m in self.migrationen:
            if m.von_version == von and m.zu_version == zu:
                if not m.ist_rueckwaerts_kompatibel:
                    return True
        ziel = next((v for v in self.versionen if v.version == zu), None)
        if ziel and ziel.kompatibilitaet == KompatibilitaetsTyp.BRECHEND:
            return True
        return False


def get_default_migrations_guards() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    # Guard 1: kontrakt workflow versions 1.0.0 → 1.1.0 → 2.0.0
    g1 = MigrationsGuard("MG-001", "kontrakt_freigabe")
    g1.versionen = [
        WorkflowSchemaVersion("WSV-001", "kontrakt_freigabe", "1.0.0", VersionsStatus.VERALTET,
                              KompatibilitaetsTyp.VOLLSTAENDIG, "Initialversion",
                              now - timedelta(days=90), now - timedelta(days=90)),
        WorkflowSchemaVersion("WSV-002", "kontrakt_freigabe", "1.1.0", VersionsStatus.VERALTET,
                              KompatibilitaetsTyp.RUECKWAERTS, "Neues Pflichtfeld",
                              now - timedelta(days=30), now - timedelta(days=30)),
        WorkflowSchemaVersion("WSV-003", "kontrakt_freigabe", "2.0.0", VersionsStatus.AKTIV,
                              KompatibilitaetsTyp.BRECHEND, "Architekturwechsel", now, now),
    ]
    g1.migrationen = [
        MigrationsSchritt("MS-001", MigrationsTyp.VORWAERTS, "1.0.0", "1.1.0",
                          "Pflichtfeld ergänzen", True),
        MigrationsSchritt("MS-002", MigrationsTyp.VORWAERTS, "1.1.0", "2.0.0",
                          "Schema-Umbau", False),
    ]

    # Guard 2: ap_rechnung simple
    g2 = MigrationsGuard("MG-002", "ap_rechnung")
    g2.versionen = [
        WorkflowSchemaVersion("WSV-004", "ap_rechnung", "1.0.0", VersionsStatus.AKTIV,
                              KompatibilitaetsTyp.VOLLSTAENDIG, "Einzige Version", now),
    ]

    return [g1, g2]
