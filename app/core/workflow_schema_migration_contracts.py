"""
Workflow Schema Migration Contracts — Wave 67
Pure Python, no app/api imports.
"""
from enum import Enum
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional, List, Dict, Any


class SchemaKompatibilitaet(Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"  # Fully backward compatible
    RUECKWAERTS = "RUECKWAERTS"    # Backward compatible (old readers can read new)
    VORWAERTS = "VORWAERTS"        # Forward compatible (new readers can read old)
    KEINE = "KEINE"                 # Breaking change, no compatibility


class MigrationsStatus(Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    ZURUECKGEROLLT = "ZURUECKGEROLLT"


class FeldAenderungsTyp(Enum):
    HINZUGEFUEGT = "HINZUGEFUEGT"
    ENTFERNT = "ENTFERNT"
    UMBENANNT = "UMBENANNT"
    TYP_GEAENDERT = "TYP_GEAENDERT"
    OPTIONAL_GEMACHT = "OPTIONAL_GEMACHT"
    PFLICHT_GEMACHT = "PFLICHT_GEMACHT"


@dataclass
class FeldAenderung:
    feld_name: str
    aenderungs_typ: FeldAenderungsTyp
    alter_wert: Optional[str] = None   # old type or value
    neuer_wert: Optional[str] = None   # new type or value
    migrations_ausdruck: Optional[str] = None  # transformation expression

    def ist_brechend(self) -> bool:
        """Breaking changes: removing required fields, making optional→required, type changes."""
        return self.aenderungs_typ in (
            FeldAenderungsTyp.ENTFERNT,
            FeldAenderungsTyp.TYP_GEAENDERT,
            FeldAenderungsTyp.PFLICHT_GEMACHT,
        )


@dataclass
class SchemaVersion:
    schema_id: str
    version: str  # semver e.g. "2.1.0"
    felder: List[str]
    erstellt_am: datetime
    aenderungen: List[FeldAenderung] = field(default_factory=list)

    def version_tuple(self) -> tuple:
        teile = self.version.split(".")
        return tuple(int(t) for t in teile)

    def berechne_kompatibilitaet(self) -> SchemaKompatibilitaet:
        if not self.aenderungen:
            return SchemaKompatibilitaet.VOLLSTAENDIG
        hat_brechend = any(a.ist_brechend() for a in self.aenderungen)
        _hat_harmlos = any(not a.ist_brechend() for a in self.aenderungen)  # noqa: F841
        if hat_brechend:
            return SchemaKompatibilitaet.KEINE
        # Only non-breaking (added optional fields → backward compat)
        return SchemaKompatibilitaet.RUECKWAERTS


@dataclass
class MigrationsSchritt:
    schritt_nr: int
    beschreibung: str
    sql_ausdruck: Optional[str] = None
    rueckgaengig_ausdruck: Optional[str] = None  # rollback SQL
    ist_optional: bool = False


@dataclass
class SchemaMigration:
    migrations_id: str
    von_version: str
    zu_version: str
    schritte: List[MigrationsSchritt]
    status: MigrationsStatus = MigrationsStatus.AUSSTEHEND
    begonnen_am: Optional[datetime] = None
    abgeschlossen_am: Optional[datetime] = None
    fehler_meldung: Optional[str] = None

    def fortschritt_pct(self, abgeschlossene_schritte: int) -> float:
        if not self.schritte:
            return 100.0
        return round(abgeschlossene_schritte / len(self.schritte) * 100, 2)

    def hat_rueckgaengig_pfad(self) -> bool:
        """True if all mandatory steps have rollback expressions."""
        pflicht_schritte = [s for s in self.schritte if not s.ist_optional]
        return all(s.rueckgaengig_ausdruck is not None for s in pflicht_schritte)


@dataclass
class SchemaRegistry:
    registry_id: str
    versionen: List[SchemaVersion] = field(default_factory=list)
    migrationen: List[SchemaMigration] = field(default_factory=list)

    def aktuellste_version(self) -> Optional[SchemaVersion]:
        if not self.versionen:
            return None
        return max(self.versionen, key=lambda v: v.version_tuple())

    def finde_migration(self, von: str, zu: str) -> Optional[SchemaMigration]:
        for m in self.migrationen:
            if m.von_version == von and m.zu_version == zu:
                return m
        return None


# 5 default schema versions
SCHEMA_VERSIONEN = [
    SchemaVersion(
        "SV-001",
        version="1.0.0",
        felder=["id", "name", "status"],
        erstellt_am=datetime(2026, 1, 1),
    ),
    SchemaVersion(
        "SV-002",
        version="1.1.0",
        felder=["id", "name", "status", "beschreibung"],
        erstellt_am=datetime(2026, 1, 15),
        aenderungen=[
            FeldAenderung("beschreibung", FeldAenderungsTyp.HINZUGEFUEGT, neuer_wert="str"),
        ],
    ),
    SchemaVersion(
        "SV-003",
        version="2.0.0",
        felder=["id", "name", "status", "beschreibung", "pflicht_feld"],
        erstellt_am=datetime(2026, 2, 1),
        aenderungen=[
            FeldAenderung("pflicht_feld", FeldAenderungsTyp.PFLICHT_GEMACHT),
        ],
    ),
    SchemaVersion(
        "SV-004",
        version="2.1.0",
        felder=["id", "name", "status", "beschreibung", "pflicht_feld"],
        erstellt_am=datetime(2026, 2, 15),
        aenderungen=[
            FeldAenderung("status", FeldAenderungsTyp.OPTIONAL_GEMACHT),
        ],
    ),
    SchemaVersion(
        "SV-005",
        version="3.0.0",
        felder=["id", "bezeichnung", "status", "beschreibung", "pflicht_feld"],
        erstellt_am=datetime(2026, 3, 1),
        aenderungen=[
            FeldAenderung("name", FeldAenderungsTyp.ENTFERNT),
            FeldAenderung("bezeichnung", FeldAenderungsTyp.HINZUGEFUEGT, neuer_wert="str"),
        ],
    ),
]
