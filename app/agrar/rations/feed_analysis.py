"""Domain rules for versioned feed analyses and their provenance."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, Iterable, Mapping

from app.agrar.rations.reference_data import UnitDefinition, convert_unit


class AnalysisStatus(StrEnum):
    UPLOADED = "uploaded"
    MAPPED = "mapped"
    DRAFT = "draft"
    VALIDATED = "validated"
    RELEASED = "released"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class AnalysisValueStatus(StrEnum):
    MEASURED = "measured"
    CALCULATED = "calculated"
    ESTIMATED = "estimated"


_TRANSITIONS: dict[AnalysisStatus, frozenset[AnalysisStatus]] = {
    AnalysisStatus.UPLOADED: frozenset({AnalysisStatus.MAPPED, AnalysisStatus.REJECTED}),
    AnalysisStatus.MAPPED: frozenset({AnalysisStatus.DRAFT, AnalysisStatus.REJECTED}),
    AnalysisStatus.DRAFT: frozenset({AnalysisStatus.VALIDATED, AnalysisStatus.REJECTED}),
    AnalysisStatus.VALIDATED: frozenset({AnalysisStatus.DRAFT, AnalysisStatus.RELEASED, AnalysisStatus.REJECTED}),
    AnalysisStatus.RELEASED: frozenset({AnalysisStatus.SUPERSEDED}),
    AnalysisStatus.SUPERSEDED: frozenset(),
    AnalysisStatus.REJECTED: frozenset(),
}


def transition_analysis(
    current: AnalysisStatus | str,
    target: AnalysisStatus | str,
    findings: Iterable[Mapping[str, Any]],
) -> AnalysisStatus:
    current_status = AnalysisStatus(current)
    target_status = AnalysisStatus(target)
    if target_status not in _TRANSITIONS[current_status]:
        raise ValueError(f"Statuswechsel {current_status.value} -> {target_status.value} ist nicht zulaessig.")
    if target_status == AnalysisStatus.RELEASED and any(
        finding.get("severity") == "blocker" for finding in findings
    ):
        raise ValueError("Analyse mit Blocker-Befunden darf nicht freigegeben werden.")
    return target_status


_UNITS = {
    "percent": UnitDefinition("percent", "%", "mass_concentration", Decimal("10"), 1),
    "g_per_kg": UnitDefinition("g_per_kg", "g/kg", "mass_concentration", Decimal("1"), 1),
    "MJ_per_kg": UnitDefinition("MJ_per_kg", "MJ/kg", "energy_concentration", Decimal("1"), 3),
    "pH": UnitDefinition("pH", "pH", "ph", Decimal("1"), 2),
}


@dataclass(frozen=True, slots=True)
class NormalizedAnalysisValue:
    nutrient_code: str
    original_value: Decimal
    original_unit_code: str
    canonical_value: Decimal
    canonical_unit_code: str
    basis: str
    value_status: AnalysisValueStatus
    estimated: bool


def normalize_analysis_value(
    nutrient_code: str,
    original_value: Decimal | str | int,
    original_unit_code: str,
    canonical_unit_code: str,
    basis: str,
    value_status: AnalysisValueStatus | str,
) -> NormalizedAnalysisValue:
    try:
        status = AnalysisValueStatus(value_status)
    except ValueError as exc:
        raise ValueError("Status des Analysewerts ist ungueltig.") from exc
    if not nutrient_code.strip():
        raise ValueError("Naehrstoffcode ist erforderlich.")
    if basis not in {"fresh_matter", "dry_matter"}:
        raise ValueError("Bezugsbasis ist ungueltig.")
    try:
        source_unit = _UNITS[original_unit_code]
        target_unit = _UNITS[canonical_unit_code]
    except KeyError as exc:
        raise ValueError(f"Unbekannte Einheit: {exc.args[0]}.") from exc
    original = Decimal(str(original_value))
    if original < 0:
        raise ValueError("Analysewerte duerfen nicht negativ sein.")
    canonical = convert_unit(original, source_unit, target_unit)
    return NormalizedAnalysisValue(
        nutrient_code=nutrient_code,
        original_value=original,
        original_unit_code=original_unit_code,
        canonical_value=canonical,
        canonical_unit_code=canonical_unit_code,
        basis=basis,
        value_status=status,
        estimated=status == AnalysisValueStatus.ESTIMATED,
    )


def evaluate_analysis(values: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_code = {str(value.get("nutrient_code")): value.get("canonical_value") for value in values}
    findings: list[dict[str, Any]] = []
    dry_matter = by_code.get("dry_matter")
    if dry_matter is None:
        findings.append({
            "code": "missing-dry-matter", "severity": "blocker",
            "message": "Trockensubstanz fehlt; eine sichere FM/TM-Umrechnung ist nicht moeglich.",
        })
    elif not Decimal("0") < Decimal(str(dry_matter)) <= Decimal("1000"):
        findings.append({"code": "dry-matter-out-of-range", "severity": "blocker", "value": dry_matter})
    crude_protein = by_code.get("crude_protein")
    if crude_protein is not None and not Decimal("0") <= Decimal(str(crude_protein)) <= Decimal("1000"):
        findings.append({
            "code": "crude-protein-out-of-range", "severity": "warning", "value": crude_protein,
            "message": "Rohprotein liegt ausserhalb des plausiblen Massenanteils.",
        })
    return findings
