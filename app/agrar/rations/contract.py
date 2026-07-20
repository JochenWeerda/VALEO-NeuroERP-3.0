"""Kanonischer Ergebnisvertrag der Rationsoptimierung (RATION-CANON-01).

Dieses Modul definiert die **fachliche** Ergebnissprache des Solvers,
unabhaengig vom technischen SciPy/HiGHS-Status:

* :class:`RationResultStatus` – die neun fachlichen Ergebnisstatus aus
  Skill §4.4 (``FEASIBLE_OPTIMAL`` … ``SOLVER_ERROR``).
* :class:`AttainabilityReport` – der Erreichbarkeits-Fuenfling aus
  Skill §3 (Phase 2): ``baseline_supported`` / ``safe_attainable`` /
  ``technical_max`` / ``target`` / ``target_gap`` plus limitierende Achse.

Bewusst als **reine** Bausteine (keine SciPy-, keine FastAPI-Abhaengigkeit),
damit der Vertrag deterministisch testbar bleibt und in ``_build_response``
nur noch verdrahtet werden muss.

Fachliche Leitplanken (Skill §2.3, §10.3):

* Die Wunschleistung (``target``) ist ein Planungsziel, keine Wahrheit. Der
  Vertrag gibt sie niemals als "erreicht" aus, wenn ``safe_attainable`` sie
  nicht deckt.
* Fehlende Kennwerte werden als ``None`` gefuehrt, nicht als ``0`` oder
  erfundener Durchschnitt. ``technical_max`` bleibt ``None``, solange kein
  dedizierter Maximalleistungslauf vorliegt (folgt in einem spaeteren Slice);
  der Status haengt nicht von ``technical_max`` ab.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class RationResultStatus(str, Enum):
    """Fachlicher Ergebnisstatus eines Solverlaufs (Skill §4.4).

    ``str``-Enum, damit der Wert direkt JSON-serialisierbar ist und in der
    API als stabiler String (z. B. ``"FEASIBLE_OPTIMAL"``) erscheint.
    """

    #: Loesung gefunden, Ziel gedeckt, ohne Relaxation.
    FEASIBLE_OPTIMAL = "FEASIBLE_OPTIMAL"
    #: Loesung gefunden und zulaessig, aber nicht nachweislich kostenoptimal.
    FEASIBLE_NON_OPTIMAL = "FEASIBLE_NON_OPTIMAL"
    #: Ziel unter harten Grenzen nicht voll deckbar – beste erreichbare Loesung.
    BEST_ATTAINABLE = "BEST_ATTAINABLE"
    #: Ziel erst nach kontrollierter Relaxation weicher Grenzen gedeckt.
    RELAXED_ACCEPTABLE = "RELAXED_ACCEPTABLE"
    #: Ziel mit den zugelassenen Futtermitteln/Grenzen nicht erreichbar.
    TARGET_NOT_ATTAINABLE = "TARGET_NOT_ATTAINABLE"
    #: Harte Grenzen widersprechen sich – keine zulaessige Loesung moeglich.
    CONSTRAINT_CONFLICT = "CONSTRAINT_CONFLICT"
    #: Eingabe-/Analysedaten unvollstaendig – Bewertung nicht belastbar.
    DATA_INCOMPLETE = "DATA_INCOMPLETE"
    #: Loesung waere nur unter Verletzung einer Sicherheitsgrenze moeglich.
    UNSAFE_REJECTED = "UNSAFE_REJECTED"
    #: Technischer Solverfehler (Exception, numerischer Abbruch).
    SOLVER_ERROR = "SOLVER_ERROR"


#: Einheit des Erreichbarkeits-Fuenflings. Heute ausschliesslich kg Milch/Tag;
#: als Feld gefuehrt, damit ein spaeterer ECM-Bezug nicht stillschweigend die
#: Bedeutung aendert.
OUTPUT_UNIT_MILK_KG = "kg_milk_day"

#: Standard-Toleranz (kg Milch/Tag), innerhalb derer eine Zielverfehlung noch
#: als "Ziel erreicht" gilt. UI-/Solver-Default (Skill §5: source_type ui_default),
#: KEINE GfE-Norm.
DEFAULT_TARGET_TOLERANCE_KG = 0.5


@dataclass(slots=True)
class AttainabilityReport:
    """Erreichbarkeitsanalyse (Skill §3, Phase 2).

    Alle Leistungsgroessen in kg Milch/Tag (siehe :data:`OUTPUT_UNIT_MILK_KG`).
    ``None`` bedeutet "nicht bestimmt", niemals "null Leistung".
    """

    #: Mit der Ausgangs-/Eingaberation versorgte Leistung. Im reinen
    #: Optimierlauf nicht bestimmbar (die Ration wird ja veraendert) -> None.
    baseline_supported: Optional[float] = None
    #: Unter Einhaltung ALLER harten Grenzen sicher erreichbare Leistung.
    safe_attainable: Optional[float] = None
    #: Technisch maximal erreichbare Leistung. None, solange kein dedizierter
    #: Maximalleistungslauf vorliegt (spaeterer Slice) – nicht schaetzen.
    technical_max: Optional[float] = None
    #: Gewuenschte Herdenleistung (Planungsziel).
    target: Optional[float] = None
    #: Ziellücke = target - safe_attainable (positiv = unterversorgt). None,
    #: wenn eine der beiden Groessen fehlt.
    target_gap: Optional[float] = None
    #: Limitierende Naehrstoffachse der erreichbaren Leistung
    #: ("energy" | "protein" | None).
    limiting_axis: Optional[str] = None
    #: True, wenn safe_attainable das Ziel innerhalb der Toleranz deckt.
    meets_target: bool = False
    #: Angewandte Zieltoleranz (kg), zur Nachvollziehbarkeit mitgefuehrt.
    tolerance_kg: float = DEFAULT_TARGET_TOLERANCE_KG
    unit: str = OUTPUT_UNIT_MILK_KG

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_supported": _round1(self.baseline_supported),
            "safe_attainable": _round1(self.safe_attainable),
            "technical_max": _round1(self.technical_max),
            "target": _round1(self.target),
            "target_gap": _round1(self.target_gap),
            "limiting_axis": self.limiting_axis,
            "meets_target": self.meets_target,
            "tolerance_kg": self.tolerance_kg,
            "unit": self.unit,
        }


def _round1(v: Optional[float]) -> Optional[float]:
    return None if v is None else round(float(v), 1)


def limiting_axis_from_milk(
    milk_from_energy: Optional[float],
    milk_from_protein: Optional[float],
) -> Optional[str]:
    """Bestimme die limitierende Achse aus den beiden Teil-Leistungen.

    Kleinerer Wert limitiert. Bei Gleichstand oder fehlenden Werten -> None.
    """
    if milk_from_energy is None or milk_from_protein is None:
        return None
    if abs(milk_from_energy - milk_from_protein) < 1e-6:
        return None
    return "energy" if milk_from_energy < milk_from_protein else "protein"


def build_attainability(
    *,
    target: Optional[float],
    safe_attainable: Optional[float],
    baseline_supported: Optional[float] = None,
    technical_max: Optional[float] = None,
    limiting_axis: Optional[str] = None,
    tolerance_kg: float = DEFAULT_TARGET_TOLERANCE_KG,
) -> AttainabilityReport:
    """Baue den Erreichbarkeitsbericht.

    ``target_gap`` = ``target - safe_attainable`` (positiv = Unterversorgung).
    ``meets_target`` ist True, wenn kein positives Ziel gesetzt ist oder die
    sichere Leistung das Ziel bis auf ``tolerance_kg`` deckt.
    """
    gap: Optional[float] = None
    if target is not None and target > 0 and safe_attainable is not None:
        gap = float(target) - float(safe_attainable)

    if target is None or target <= 0:
        # Kein positives Leistungsziel -> es gibt nichts zu verfehlen.
        meets = True
    elif safe_attainable is None:
        meets = False
    else:
        meets = float(safe_attainable) >= float(target) - float(tolerance_kg)

    return AttainabilityReport(
        baseline_supported=baseline_supported,
        safe_attainable=safe_attainable,
        technical_max=technical_max,
        target=target,
        target_gap=gap,
        limiting_axis=limiting_axis,
        meets_target=meets,
        tolerance_kg=tolerance_kg,
    )


def derive_result_status(
    *,
    solver_ok: bool,
    attainability: AttainabilityReport,
    relaxation_applied: bool = False,
    data_incomplete: bool = False,
    constraint_conflict: bool = False,
    unsafe_rejected: bool = False,
    optimal: bool = True,
) -> RationResultStatus:
    """Leite den fachlichen Ergebnisstatus ab (Skill §4.4).

    Prioritaet der Sonderfaelle (hart vor weich):

    1. ``unsafe_rejected`` -> ``UNSAFE_REJECTED`` (eine Sicherheitsgrenze
       muesste verletzt werden; Skill-Invariante §11.2).
    2. Kein Solverlauf-Erfolg (``solver_ok`` False):

       * ``constraint_conflict`` -> ``CONSTRAINT_CONFLICT``
       * ``data_incomplete``     -> ``DATA_INCOMPLETE``
       * sonst                   -> ``TARGET_NOT_ATTAINABLE``

    3. Solverlauf erfolgreich – anhand Zieldeckung und Relaxation:

       * Ziel gedeckt, keine Relaxation, optimal -> ``FEASIBLE_OPTIMAL``
       * Ziel gedeckt, keine Relaxation, nicht optimal -> ``FEASIBLE_NON_OPTIMAL``
       * Ziel gedeckt, mit Relaxation -> ``RELAXED_ACCEPTABLE``
       * Ziel verfehlt, mit Relaxation -> ``BEST_ATTAINABLE``
       * Ziel verfehlt, ohne Relaxation -> ``TARGET_NOT_ATTAINABLE``
    """
    if unsafe_rejected:
        return RationResultStatus.UNSAFE_REJECTED

    if not solver_ok:
        if constraint_conflict:
            return RationResultStatus.CONSTRAINT_CONFLICT
        if data_incomplete:
            return RationResultStatus.DATA_INCOMPLETE
        return RationResultStatus.TARGET_NOT_ATTAINABLE

    # Solverlauf erfolgreich.
    if data_incomplete:
        # Loesung technisch vorhanden, aber fachlich nicht belastbar.
        return RationResultStatus.DATA_INCOMPLETE

    if attainability.meets_target:
        if relaxation_applied:
            return RationResultStatus.RELAXED_ACCEPTABLE
        return (
            RationResultStatus.FEASIBLE_OPTIMAL
            if optimal
            else RationResultStatus.FEASIBLE_NON_OPTIMAL
        )

    # Ziel nicht gedeckt.
    if relaxation_applied:
        return RationResultStatus.BEST_ATTAINABLE
    return RationResultStatus.TARGET_NOT_ATTAINABLE


def build_result_contract(
    *,
    solver_ok: bool,
    target: Optional[float],
    safe_attainable: Optional[float],
    baseline_supported: Optional[float] = None,
    technical_max: Optional[float] = None,
    milk_from_energy: Optional[float] = None,
    milk_from_protein: Optional[float] = None,
    relaxation_applied: bool = False,
    data_incomplete: bool = False,
    constraint_conflict: bool = False,
    unsafe_rejected: bool = False,
    optimal: bool = True,
    tolerance_kg: float = DEFAULT_TARGET_TOLERANCE_KG,
) -> Dict[str, Any]:
    """Ein-Aufruf-Fassade fuer ``_build_response``.

    Liefert ``{"result_status": <str>, "attainability": {...}}`` – additiv zum
    bestehenden ``status``-Feld, das aus Rueckwaertskompatibilitaet unveraendert
    bleibt.
    """
    axis = limiting_axis_from_milk(milk_from_energy, milk_from_protein)
    report = build_attainability(
        target=target,
        safe_attainable=safe_attainable,
        baseline_supported=baseline_supported,
        technical_max=technical_max,
        limiting_axis=axis,
        tolerance_kg=tolerance_kg,
    )
    status = derive_result_status(
        solver_ok=solver_ok,
        attainability=report,
        relaxation_applied=relaxation_applied,
        data_incomplete=data_incomplete,
        constraint_conflict=constraint_conflict,
        unsafe_rejected=unsafe_rejected,
        optimal=optimal,
    )
    return {
        "result_status": status.value,
        "attainability": report.to_dict(),
    }


__all__ = [
    "RationResultStatus",
    "AttainabilityReport",
    "OUTPUT_UNIT_MILK_KG",
    "DEFAULT_TARGET_TOLERANCE_KG",
    "limiting_axis_from_milk",
    "build_attainability",
    "derive_result_status",
    "build_result_contract",
]
