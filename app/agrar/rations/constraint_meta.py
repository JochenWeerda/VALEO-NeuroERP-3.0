"""Constraint-Meta-Modell der Rationsoptimierung (RATION-CANON-02, Skill §5).

Die Rechenlogik im LP unterscheidet bisher nur ``kind`` ("hart"/"weich") und
eine Penalty-Klasse (A/B/C). Der Skill §5 verlangt darueber hinaus eine
**Haerteklasse** und eine **Quelle** je Grenze, damit die Invariante §11.2 –
"Safety-hard-Grenzen werden nie automatisch relaxiert" – strukturell gilt und
nicht nur implizit aus dem Solverpfad folgt.

Dieses Modul ist bewusst **standalone** (keine Abhaengigkeit zum Endpoint), damit
es kein Import-Zyklus wird. Die Konsistenz zur produktiven Klassifikation
``_CONSTRAINT_CLASSIFICATION`` (kind/penalty_class) wird per Test erzwungen
(`tests/test_rations_constraint_meta.py`): jede "hart"-Grenze ist nicht
auto-relaxierbar, jede "weich"-Grenze ist advisory/solver_working.

Haerteklassen (Skill §5.1):

* ``safety_hard``   – Recht/Physiologie/Tiergesundheit. Wird NIE automatisch
  geoeffnet.
* ``business_hard`` – betrieblich/zielsetzend. Nur nach ausdruecklicher
  Benutzeraenderung (z. B. Absenken der Wunschleistung) offen.
* ``advisory``      – Beratungs-/Praxiskorridor. Darf im Relaxationslauf
  kontrolliert und protokolliert veraendert werden.
* ``solver_working``– reine Suchraum-Eingrenzung; darf transparent
  angepasst werden.
* ``observation``   – wird berechnet/angezeigt, blockiert den Solver nicht.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional


class Hardness(str, Enum):
    SAFETY_HARD = "safety_hard"
    BUSINESS_HARD = "business_hard"
    ADVISORY = "advisory"
    SOLVER_WORKING = "solver_working"
    OBSERVATION = "observation"


class SourceType(str, Enum):
    LAW = "law"
    GFE = "gfe"
    DLG = "dlg"
    FARM_POLICY = "farm_policy"
    ADVISOR = "advisor"
    SOLVER_DEFAULT = "solver_default"
    UI_DEFAULT = "ui_default"


#: Haerteklassen, die der Solver NIEMALS automatisch relaxieren darf (Skill §11.2).
_NON_AUTO_RELAXABLE: frozenset = frozenset(
    {Hardness.SAFETY_HARD, Hardness.BUSINESS_HARD}
)

#: Prioritaet je Haerteklasse (hoeher = wichtiger; fuer lexikografische Reihung §4.1).
_PRIORITY_BY_HARDNESS: Dict[Hardness, int] = {
    Hardness.SAFETY_HARD: 100,
    Hardness.BUSINESS_HARD: 80,
    Hardness.ADVISORY: 50,
    Hardness.SOLVER_WORKING: 30,
    Hardness.OBSERVATION: 10,
}


@dataclass(slots=True, frozen=True)
class ConstraintMeta:
    """Meta-Beschreibung einer Nebenbedingung (Skill §5, pragmatischer Kern).

    ``expected_kind``/``penalty_class`` spiegeln die produktive Klassifikation
    (``_CONSTRAINT_CLASSIFICATION``) und werden per Test gegengeprueft, damit das
    Meta-Modell nicht vom realen Solververhalten abdriftet.
    """

    constraint_id: str
    metric_id: str
    hardness: Hardness
    source_type: SourceType
    source_ref: str
    #: Muss zur LP-Realitaet passen: "hart" => nicht relaxierbar.
    expected_kind: str
    penalty_class: Optional[str] = None
    max_relaxation: Optional[float] = None

    @property
    def relaxable(self) -> bool:
        """True nur fuer advisory/solver_working/observation (nie safety/business)."""
        return self.hardness not in _NON_AUTO_RELAXABLE

    @property
    def priority(self) -> int:
        return _PRIORITY_BY_HARDNESS[self.hardness]

    def to_dict(self) -> Dict[str, object]:
        return {
            "constraint_id": self.constraint_id,
            "metric_id": self.metric_id,
            "hardness": self.hardness.value,
            "source_type": self.source_type.value,
            "source_ref": self.source_ref,
            "penalty_class": self.penalty_class,
            "relaxable": self.relaxable,
            "max_relaxation": self.max_relaxation,
            "priority": self.priority,
        }


def _m(
    name: str,
    hardness: Hardness,
    source_type: SourceType,
    source_ref: str,
    expected_kind: str,
    penalty_class: Optional[str] = None,
) -> ConstraintMeta:
    return ConstraintMeta(
        constraint_id=name,
        metric_id=name,
        hardness=hardness,
        source_type=source_type,
        source_ref=source_ref,
        expected_kind=expected_kind,
        penalty_class=penalty_class,
    )


# Registry der bekannten Grenzen. Schluessel identisch zu den Namen in
# ``_CONSTRAINT_CLASSIFICATION`` (endpoint), damit der Konsistenztest greift.
CONSTRAINT_META: Dict[str, ConstraintMeta] = {
    # --- Bedarfs-Floors (zielsetzend): nur ueber Zielaenderung zu oeffnen ---
    "ME (MJ/d)": _m(
        "ME (MJ/d)", Hardness.BUSINESS_HARD, SourceType.GFE,
        "GfE 2023 Energiebedarf (ME) Milchkuh", "hart",
    ),
    "sidP (g/d)": _m(
        "sidP (g/d)", Hardness.BUSINESS_HARD, SourceType.GFE,
        "GfE 2023 Proteinbewertung (sidP)", "hart",
    ),
    # --- Physiologische Kapazitaet / Tiergesundheit: safety_hard ---
    "TM-Aufnahme (kg/d)": _m(
        "TM-Aufnahme (kg/d)", Hardness.SAFETY_HARD, SourceType.GFE,
        "GfE 2023 Futteraufnahmekapazitaet (DMI-Korridor)", "hart",
    ),
    "Magnesium (g/d)": _m(
        "Magnesium (g/d)", Hardness.SAFETY_HARD, SourceType.GFE,
        "GfE 2023 Mg-Bedarf (Weidetetanie-Prophylaxe)", "hart",
    ),
    "Calcium (g/d)": _m(
        "Calcium (g/d)", Hardness.SAFETY_HARD, SourceType.GFE,
        "GfE 2023 Ca-Bedarf", "hart",
    ),
    "Phosphor (g/d)": _m(
        "Phosphor (g/d)", Hardness.SAFETY_HARD, SourceType.GFE,
        "GfE 2023 P-Bedarf", "hart",
    ),
    # --- Struktur-/Pansen-Korridore (advisory: im LP weich mit Penalty) ---
    "aNDFom (g/d)": _m(
        "aNDFom (g/d)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Strukturversorgung (aNDFom)", "weich", "B",
    ),
    "aNDFomGF (g/kg TM)": _m(
        "aNDFomGF (g/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Grobfutter-NDF-Dichte", "weich", "B",
    ),
    "pabKH (g/kg TM)": _m(
        "pabKH (g/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 pansenabbaubare KH (SARA-nah)", "weich", "B",
    ),
    "XL Rohfett (g/kg TM)": _m(
        "XL Rohfett (g/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Rohfett-Obergrenze Pansen", "weich", "C",
    ),
    "peNDF (g/kg TM)": _m(
        "peNDF (g/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 / GfE-Workshop 2023 peNDF (PennState)", "weich", "B",
    ),
    "Grundfutteranteil (%TM)": _m(
        "Grundfutteranteil (%TM)", Hardness.ADVISORY, SourceType.FARM_POLICY,
        "Beratungsvorgabe 'Grobfutter zuerst'", "weich", "B",
    ),
    "RMD (g N/kg TM)": _m(
        "RMD (g N/kg TM)", Hardness.ADVISORY, SourceType.GFE,
        "GfE-Workshop 2023 ruminale N-Bilanz (RMD)", "weich", "A",
    ),
    "Kalium (g/d)": _m(
        "Kalium (g/d)", Hardness.ADVISORY, SourceType.GFE,
        "GfE-Workshop 2023 K-Obergrenze (K:Mg)", "weich", "A",
    ),
    "ME-Dichte (MJ/kg TM)": _m(
        "ME-Dichte (MJ/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Energiedichte-Obergrenze", "weich", "A",
    ),
    "sidP-Zielkorridor (g/d)": _m(
        "sidP-Zielkorridor (g/d)", Hardness.ADVISORY, SourceType.GFE,
        "GfE 2023 sidP-Zielkorridor", "weich", "A",
    ),
    "CP-Dichte (g/kg TM)": _m(
        "CP-Dichte (g/kg TM)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Rohprotein-Obergrenze (N-Effizienz)", "weich", "C",
    ),
    "K:Mg-Ratio": _m(
        "K:Mg-Ratio", Hardness.ADVISORY, SourceType.GFE,
        "GfE-Workshop 2023 K:Mg (Tetanie-Risiko)", "weich", "A",
    ),
    "Konzentrat-Tagesmax (kg TM/d)": _m(
        # Die physiologisch harte Einzelgaben-Deckelung (1,5x SARA-Netz) ist im
        # LP separat; das empfohlene Tagesmaximum selbst ist advisory.
        "Konzentrat-Tagesmax (kg TM/d)", Hardness.ADVISORY, SourceType.DLG,
        "FeedingSystemConfig Tagesmax (SARA-Schutz separat safety_hard im LP)",
        "weich", "B",
    ),
    "Saftfutter/nasse CoP (kg TM/d)": _m(
        "Saftfutter/nasse CoP (kg TM/d)", Hardness.ADVISORY, SourceType.DLG,
        "DLG 01|2023 Saftfutter/nasse Co-Produkte Leitplanke", "weich", "B",
    ),
}


def get_meta(name: str) -> Optional[ConstraintMeta]:
    """Meta-Beschreibung zu einem Constraint-Namen (None wenn unbekannt)."""
    return CONSTRAINT_META.get(name)


def is_auto_relaxable(name: str) -> bool:
    """Darf der Solver diese Grenze automatisch relaxieren?

    Unbekannte Namen gelten konservativ als **nicht** auto-relaxierbar (fail-safe):
    lieber eine harmlose Grenze nicht oeffnen, als versehentlich eine
    Sicherheitsgrenze zu relaxieren.
    """
    meta = CONSTRAINT_META.get(name)
    if meta is None:
        return False
    return meta.relaxable


def safety_hard_names() -> List[str]:
    return [n for n, m in CONSTRAINT_META.items() if m.hardness is Hardness.SAFETY_HARD]


def assert_safety_hard_not_relaxed(relaxed_names: Iterable[str]) -> None:
    """Invariante §11.2: keine safety_hard-Grenze in der Relaxationsmenge.

    Wirft ``AssertionError``, wenn eine safety_hard-Grenze relaxiert wurde. Als
    Guard fuer Solverpfade gedacht, die eine Relaxationsliste erzeugen.
    """
    safety = set(safety_hard_names())
    violating = sorted(safety.intersection(set(relaxed_names)))
    assert not violating, (
        f"Invariante verletzt: safety_hard-Grenzen relaxiert: {violating}"
    )


def meta_row(name: str) -> Dict[str, object]:
    """Additive Anreicherung einer Constraint-Status-Zeile (Skill §5.2).

    Liefert hardness/source_type/relaxable/priority; bei unbekanntem Namen einen
    konservativen, nicht-relaxierbaren Observation-Platzhalter (keine erfundene
    Quelle).
    """
    meta = CONSTRAINT_META.get(name)
    if meta is None:
        return {
            "hardness": None,
            "source_type": None,
            "relaxable": False,
            "priority": None,
        }
    return {
        "hardness": meta.hardness.value,
        "source_type": meta.source_type.value,
        "relaxable": meta.relaxable,
        "priority": meta.priority,
    }


__all__ = [
    "Hardness",
    "SourceType",
    "ConstraintMeta",
    "CONSTRAINT_META",
    "get_meta",
    "is_auto_relaxable",
    "safety_hard_names",
    "assert_safety_hard_not_relaxed",
    "meta_row",
]
