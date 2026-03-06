"""
B5: Qualitätsregeln für den Agrar-Bereich

Maschinenlesbare Regeldefinitionen für:
- PSM-Compliance (§11 PflSchG)
- Dünger-Compliance (DüV)
- Ernte-Annahme-Qualität
- Wasserschutz-Zonen-Regeln
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class QualityRule:
    id: str
    domain: str  # psm | duengung | ernte | wasserschutz
    severity: str  # error | warning | info
    description: str
    legal_reference: Optional[str] = None
    check_field: Optional[str] = None
    condition: Optional[str] = None  # human-readable condition
    auto_enforceable: bool = True


# ── PSM-Compliance (§11 PflSchG) ─────────────────────────────────────────

PSM_RULES: list[QualityRule] = [
    QualityRule(
        id="PSM-001",
        domain="psm",
        severity="error",
        description="Datum der Anwendung muss dokumentiert werden",
        legal_reference="§11 Abs. 1 Nr. 1 PflSchG",
        check_field="datum",
        condition="NOT NULL",
    ),
    QualityRule(
        id="PSM-002",
        domain="psm",
        severity="error",
        description="Bezeichnung des Pflanzenschutzmittels muss dokumentiert werden",
        legal_reference="§11 Abs. 1 Nr. 2 PflSchG",
        check_field="mittel",
        condition="NOT NULL AND NOT EMPTY",
    ),
    QualityRule(
        id="PSM-003",
        domain="psm",
        severity="error",
        description="Aufwandmenge muss dokumentiert werden",
        legal_reference="§11 Abs. 1 Nr. 3 PflSchG",
        check_field="menge",
        condition="> 0",
    ),
    QualityRule(
        id="PSM-004",
        domain="psm",
        severity="error",
        description="Einheit der Aufwandmenge muss dokumentiert werden",
        legal_reference="§11 Abs. 1 PflSchG",
        check_field="einheit",
        condition="NOT NULL AND NOT EMPTY",
    ),
    QualityRule(
        id="PSM-005",
        domain="psm",
        severity="error",
        description="Behandelte Fläche muss dokumentiert werden",
        legal_reference="§11 Abs. 1 Nr. 4 PflSchG",
        check_field="flaeche",
        condition="> 0",
    ),
    QualityRule(
        id="PSM-006",
        domain="psm",
        severity="error",
        description="Name des Anwenders muss dokumentiert werden",
        legal_reference="§11 Abs. 1 Nr. 5 PflSchG",
        check_field="anwender",
        condition="NOT NULL AND NOT EMPTY",
    ),
    QualityRule(
        id="PSM-007",
        domain="psm",
        severity="warning",
        description="Windgeschwindigkeit > 25 km/h — Abdriftgefahr bei PSM-Anwendung",
        legal_reference="Gute fachliche Praxis (GfP)",
        check_field="windgeschwindigkeit",
        condition="<= 25",
    ),
    QualityRule(
        id="PSM-008",
        domain="psm",
        severity="warning",
        description="Temperatur > 35°C — Verdunstungsgefahr, reduzierte Wirksamkeit",
        legal_reference="Gute fachliche Praxis (GfP)",
        check_field="temperatur",
        condition="<= 35",
    ),
    QualityRule(
        id="PSM-009",
        domain="psm",
        severity="warning",
        description="Temperatur < 5°C — eingeschränkte PSM-Wirksamkeit",
        legal_reference="Gute fachliche Praxis (GfP)",
        check_field="temperatur",
        condition=">= 5",
    ),
    QualityRule(
        id="PSM-010",
        domain="psm",
        severity="warning",
        description="Wartezeit bis zur Ernte muss ≥ 0 sein",
        legal_reference="PflSchG",
        check_field="wartezeit_tage",
        condition=">= 0",
    ),
]


# ── Dünger-Compliance (DüV) ─────────────────────────────────────────────

DUENGER_RULES: list[QualityRule] = [
    QualityRule(
        id="DUE-001",
        domain="duengung",
        severity="error",
        description="Ausbringungsdatum muss dokumentiert werden",
        legal_reference="§10 Abs. 2 DüV",
        check_field="datum",
        condition="NOT NULL",
    ),
    QualityRule(
        id="DUE-002",
        domain="duengung",
        severity="error",
        description="Düngemittel-Bezeichnung muss dokumentiert werden",
        legal_reference="§10 Abs. 2 DüV",
        check_field="mittel",
        condition="NOT NULL",
    ),
    QualityRule(
        id="DUE-003",
        domain="duengung",
        severity="error",
        description="Aufwandmenge und Fläche müssen dokumentiert werden",
        legal_reference="§10 Abs. 2 DüV",
        check_field="menge",
        condition="> 0",
    ),
    QualityRule(
        id="DUE-004",
        domain="duengung",
        severity="warning",
        description="N-Ausbringung in Wasserschutzgebieten beachten (≤ 170 kg N/ha)",
        legal_reference="§13a DüV / Wasserschutzgebietsverordnungen",
        check_field="menge",
        condition="Context-abhängig",
        auto_enforceable=False,
    ),
]


# ── Ernte-Annahme ───────────────────────────────────────────────────────

ERNTE_RULES: list[QualityRule] = [
    QualityRule(
        id="ERN-001",
        domain="ernte",
        severity="error",
        description="Feuchte muss bei Getreide-Annahme gemessen werden",
        legal_reference="Handelsbrauch / GMP+",
        check_field="feuchte_prozent",
        condition="NOT NULL",
    ),
    QualityRule(
        id="ERN-002",
        domain="ernte",
        severity="warning",
        description="Feuchte > 14.5% bei Weizen — Trocknungsabzug erforderlich",
        legal_reference="Handelsbrauch",
        check_field="feuchte_prozent",
        condition="<= 14.5 (für Weizen)",
        auto_enforceable=False,
    ),
    QualityRule(
        id="ERN-003",
        domain="ernte",
        severity="error",
        description="Besatz muss bei Getreide-Annahme gemessen werden",
        legal_reference="Handelsbrauch / GMP+",
        check_field="besatz_prozent",
        condition="NOT NULL",
    ),
]


# ── Wasserschutz-Zonen ──────────────────────────────────────────────────

WASSERSCHUTZ_RULES: list[QualityRule] = [
    QualityRule(
        id="WSG-001",
        domain="wasserschutz",
        severity="error",
        description="In Schutzzone I ist keine PSM-Ausbringung erlaubt",
        legal_reference="WHG §52, Schutzgebietsverordnungen",
        check_field="zone",
        condition="!= 'I'",
    ),
    QualityRule(
        id="WSG-002",
        domain="wasserschutz",
        severity="warning",
        description="In Schutzzone II gelten erhöhte Auflagen für PSM-Einsatz",
        legal_reference="WHG §52",
        check_field="zone",
        condition="!= 'II' OR auflagen_eingehalten",
    ),
    QualityRule(
        id="WSG-003",
        domain="wasserschutz",
        severity="info",
        description="Koordinaten müssen innerhalb der Deutschland-BBox liegen",
        check_field="koordinaten",
        condition="lat ∈ [47.27, 55.06], lng ∈ [5.87, 15.04]",
    ),
]


ALL_RULES = PSM_RULES + DUENGER_RULES + ERNTE_RULES + WASSERSCHUTZ_RULES


def get_rules_by_domain(domain: str) -> list[QualityRule]:
    return [r for r in ALL_RULES if r.domain == domain]


def get_rules_by_severity(severity: str) -> list[QualityRule]:
    return [r for r in ALL_RULES if r.severity == severity]
