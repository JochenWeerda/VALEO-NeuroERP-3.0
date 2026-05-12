"""
Tenant-Prozessvarianten — Wave 24 AP1/AP5

Mandantenspezifische Prozess-Schritt-Konfiguration (Gap 009).
Ermoeglicht es, pro Tenant einzelne Prozessschritte zu aktivieren,
zu deaktivieren oder in ihrer Reihenfolge zu verschieben —
ohne Code-Aenderungen, rein konfigurativ.

Ziel: 0 globale Hardcoded Prozessschritte.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


VARIANTE_SCHEMA_VERSION = 1


class SchrittStatus(str, Enum):
    AKTIV = "AKTIV"
    DEAKTIVIERT = "DEAKTIVIERT"
    OPTIONAL = "OPTIONAL"


class VarianteValidierungsFehler(str, Enum):
    PFLICHTSCHRITT_DEAKTIVIERT = "PFLICHTSCHRITT_DEAKTIVIERT"
    SCHRITT_DOPPELT = "SCHRITT_DOPPELT"
    UNBEKANNTER_SCHRITT = "UNBEKANNTER_SCHRITT"
    REIHENFOLGE_KONFLIKT = "REIHENFOLGE_KONFLIKT"


# ---------------------------------------------------------------------------
# Datenstuktur: Prozessschritt-Definition
# ---------------------------------------------------------------------------

@dataclass
class ProzessSchrittDefinition:
    """Definition eines einzelnen Prozessschritts im Default-Prozess."""

    schritt_id: str
    bezeichnung: str
    pflicht: bool = True            # Pflichtschritte koennen nicht deaktiviert werden
    reihenfolge: int = 0            # Standardreihenfolge (aufsteigend)
    rolle: str = ""                 # Rolle, die diesen Schritt ausfuehrt
    sla_stunden: Optional[int] = None  # Maximale Bearbeitungszeit in Stunden

    def as_dict(self) -> dict:
        return {
            "schritt_id": self.schritt_id,
            "bezeichnung": self.bezeichnung,
            "pflicht": self.pflicht,
            "reihenfolge": self.reihenfolge,
            "rolle": self.rolle,
            "sla_stunden": self.sla_stunden,
        }


@dataclass
class SchrittOverride:
    """Mandantenspezifische Ueberschreibung eines Prozessschritts."""

    schritt_id: str
    status: SchrittStatus = SchrittStatus.AKTIV
    reihenfolge_override: Optional[int] = None   # None = Standard beibehalten
    sla_stunden_override: Optional[int] = None   # None = Standard beibehalten
    bemerkung: str = ""

    def as_dict(self) -> dict:
        return {
            "schritt_id": self.schritt_id,
            "status": self.status.value,
            "reihenfolge_override": self.reihenfolge_override,
            "sla_stunden_override": self.sla_stunden_override,
            "bemerkung": self.bemerkung,
        }


# ---------------------------------------------------------------------------
# Hauptstruktur: TenantProzessVariante
# ---------------------------------------------------------------------------

@dataclass
class TenantProzessVariante:
    """
    Mandantenspezifische Prozessvariante fuer einen definierten Workflow.

    Kombiniert den Default-Prozess mit Tenant-spezifischen Overrides.
    Pflichtschritte koennen nicht deaktiviert werden.
    """

    variante_id: str
    tenant_id: str
    prozess_key: str                    # z.B. "agrar_settlement", "wareneingang"
    bezeichnung: str
    default_schritte: list[ProzessSchrittDefinition] = field(default_factory=list)
    overrides: list[SchrittOverride] = field(default_factory=list)
    schema_version: int = VARIANTE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "variante_id": self.variante_id,
            "tenant_id": self.tenant_id,
            "prozess_key": self.prozess_key,
            "bezeichnung": self.bezeichnung,
            "default_schritt_count": len(self.default_schritte),
            "override_count": len(self.overrides),
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP1: resolve_process_steps()
# ---------------------------------------------------------------------------

@dataclass
class AufgeloesterProzessSchritt:
    """Schritt nach Anwendung aller Tenant-Overrides."""

    schritt_id: str
    bezeichnung: str
    pflicht: bool
    reihenfolge: int
    rolle: str
    sla_stunden: Optional[int]
    status: SchrittStatus
    override_aktiv: bool

    def as_dict(self) -> dict:
        return {
            "schritt_id": self.schritt_id,
            "bezeichnung": self.bezeichnung,
            "pflicht": self.pflicht,
            "reihenfolge": self.reihenfolge,
            "rolle": self.rolle,
            "sla_stunden": self.sla_stunden,
            "status": self.status.value,
            "override_aktiv": self.override_aktiv,
        }


def resolve_process_steps(variante: TenantProzessVariante) -> list[AufgeloesterProzessSchritt]:
    """
    Wendet alle Tenant-Overrides auf den Default-Prozess an.

    Regeln:
    - Pflichtschritte werden niemals deaktiviert (Override wird ignoriert)
    - Reihenfolge-Override ersetzt Default-Reihenfolge
    - SLA-Override ersetzt Default-SLA
    - Deaktivierte Nicht-Pflichtschritte werden gefiltert
    - Ergebnis ist nach Reihenfolge aufsteigend sortiert
    """
    override_map: dict[str, SchrittOverride] = {
        o.schritt_id: o for o in variante.overrides
    }

    aufgeloest: list[AufgeloesterProzessSchritt] = []
    for schritt in variante.default_schritte:
        override = override_map.get(schritt.schritt_id)
        override_aktiv = override is not None

        # Status bestimmen
        if override and not schritt.pflicht:
            status = override.status
        else:
            status = SchrittStatus.AKTIV  # Pflichtschritte immer AKTIV

        # Deaktivierte optionale Schritte weglassen
        if status == SchrittStatus.DEAKTIVIERT:
            continue

        # Reihenfolge
        reihenfolge = (
            override.reihenfolge_override
            if override and override.reihenfolge_override is not None
            else schritt.reihenfolge
        )

        # SLA
        sla = (
            override.sla_stunden_override
            if override and override.sla_stunden_override is not None
            else schritt.sla_stunden
        )

        aufgeloest.append(AufgeloesterProzessSchritt(
            schritt_id=schritt.schritt_id,
            bezeichnung=schritt.bezeichnung,
            pflicht=schritt.pflicht,
            reihenfolge=reihenfolge,
            rolle=schritt.rolle,
            sla_stunden=sla,
            status=status,
            override_aktiv=override_aktiv,
        ))

    aufgeloest.sort(key=lambda s: s.reihenfolge)
    return aufgeloest


# ---------------------------------------------------------------------------
# AP5: validate_prozess_variante()
# ---------------------------------------------------------------------------

@dataclass
class VarianteViolation:
    code: VarianteValidierungsFehler
    schritt_id: str
    message: str

    def as_dict(self) -> dict:
        return {
            "code": self.code.value,
            "schritt_id": self.schritt_id,
            "message": self.message,
        }


@dataclass
class VarianteValidierungsResult:
    variante_id: str
    valid: bool
    violations: list[VarianteViolation] = field(default_factory=list)
    schema_version: int = VARIANTE_SCHEMA_VERSION

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def as_dict(self) -> dict:
        return {
            "variante_id": self.variante_id,
            "valid": self.valid,
            "violation_count": self.violation_count,
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_prozess_variante(variante: TenantProzessVariante) -> VarianteValidierungsResult:
    """
    Prueft Konsistenz einer TenantProzessVariante.

    Erkannte Probleme:
    - Pflichtschritt deaktiviert
    - Override referenziert unbekannten Schritt
    - Schritt-ID doppelt im Default-Prozess
    - Reihenfolge-Konflikte (gleiche Reihenfolge fuer verschiedene Schritte)
    """
    violations: list[VarianteViolation] = []
    bekannte_ids = {s.schritt_id for s in variante.default_schritte}
    override_map: dict[str, SchrittOverride] = {  # noqa: F841
        o.schritt_id: o for o in variante.overrides
    }

    # Doppelte Schritt-IDs im Default
    gesehene: set[str] = set()
    for schritt in variante.default_schritte:
        if schritt.schritt_id in gesehene:
            violations.append(VarianteViolation(
                code=VarianteValidierungsFehler.SCHRITT_DOPPELT,
                schritt_id=schritt.schritt_id,
                message=f"Schritt '{schritt.schritt_id}' erscheint mehrfach im Default-Prozess",
            ))
        gesehene.add(schritt.schritt_id)

    # Overrides auf Pflichtschritte / unbekannte Schritte
    for override in variante.overrides:
        if override.schritt_id not in bekannte_ids:
            violations.append(VarianteViolation(
                code=VarianteValidierungsFehler.UNBEKANNTER_SCHRITT,
                schritt_id=override.schritt_id,
                message=f"Override referenziert unbekannten Schritt '{override.schritt_id}'",
            ))
            continue

        # Pflichtschritt deaktiviert?
        schritt_def = next(s for s in variante.default_schritte if s.schritt_id == override.schritt_id)
        if schritt_def.pflicht and override.status == SchrittStatus.DEAKTIVIERT:
            violations.append(VarianteViolation(
                code=VarianteValidierungsFehler.PFLICHTSCHRITT_DEAKTIVIERT,
                schritt_id=override.schritt_id,
                message=f"Pflichtschritt '{override.schritt_id}' kann nicht deaktiviert werden",
            ))

    # Reihenfolge-Konflikte in aufgeloestem Prozess
    if not violations:  # nur wenn Basis valide
        aufgeloest = resolve_process_steps(variante)
        reihenfolge_counter: dict[int, list[str]] = {}
        for s in aufgeloest:
            reihenfolge_counter.setdefault(s.reihenfolge, []).append(s.schritt_id)
        for pos, ids in reihenfolge_counter.items():
            if len(ids) > 1:
                violations.append(VarianteViolation(
                    code=VarianteValidierungsFehler.REIHENFOLGE_KONFLIKT,
                    schritt_id=ids[0],
                    message=f"Reihenfolge {pos} belegt von mehreren Schritten: {ids}",
                ))

    return VarianteValidierungsResult(
        variante_id=variante.variante_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# Default-Prozessvariante: agrar_settlement
# ---------------------------------------------------------------------------

def get_default_agrar_settlement_schritte() -> list[ProzessSchrittDefinition]:
    """Standard-Schritte fuer den agrar_settlement-Prozess."""
    return [
        ProzessSchrittDefinition("AS-01-ANNAHME",     "Wareneingang / Annahme erfassen",      pflicht=True,  reihenfolge=10, rolle="annahme_mitarbeiter", sla_stunden=2),
        ProzessSchrittDefinition("AS-02-QUALITAET",   "Qualitaetspruefung durchfuehren",       pflicht=True,  reihenfolge=20, rolle="labor_mitarbeiter",   sla_stunden=4),
        ProzessSchrittDefinition("AS-03-NEBENKOSTEN", "Nebenkosten berechnen",                 pflicht=False, reihenfolge=25, rolle="sachbearbeiter",       sla_stunden=None),
        ProzessSchrittDefinition("AS-04-SETTLEMENT",  "Settlement-Entwurf erstellen",          pflicht=True,  reihenfolge=30, rolle="sachbearbeiter",       sla_stunden=8),
        ProzessSchrittDefinition("AS-05-FREIGABE",    "Settlement freigeben (4-Augen)",        pflicht=True,  reihenfolge=40, rolle="teamleiter",           sla_stunden=24),
        ProzessSchrittDefinition("AS-06-VERBUCHUNG",  "GoBD-Verbuchung in FiBu",               pflicht=True,  reihenfolge=50, rolle="buchhalter",           sla_stunden=4),
        ProzessSchrittDefinition("AS-07-INTRASTAT",   "Intrastat-Meldung pruefen/einreichen",  pflicht=False, reihenfolge=60, rolle="compliance_beauftragter", sla_stunden=48),
    ]


def build_default_tenant_variante(tenant_id: str, prozess_key: str = "agrar_settlement") -> TenantProzessVariante:
    """Erzeugt eine Default-Variante ohne Overrides (Ausgangsbasis fuer Tenants)."""
    return TenantProzessVariante(
        variante_id=f"{tenant_id}_{prozess_key}_default",
        tenant_id=tenant_id,
        prozess_key=prozess_key,
        bezeichnung=f"Standard-Variante {prozess_key} fuer {tenant_id}",
        default_schritte=get_default_agrar_settlement_schritte(),
        overrides=[],
    )
