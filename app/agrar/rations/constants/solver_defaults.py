"""Solver-Default-Konstanten (Relaxations-Stufen, Penalty-Gewichte,
Objective-Strategien). Keine fachliche DLG-/GfE-Quelle — reine
Implementierungsentscheidungen, begründet in der Projekt-Doku
(docs/architecture/process-kernel/...).
"""

from __future__ import annotations

# --- Relaxations-Policy ---------------------------------------------------
RELAXATION_POLICIES: tuple[str, ...] = ("strict", "standard", "soft")
RELAXATION_DEFAULT: str = "standard"
RELAXATION_FACTORS: dict[str, float] = {
    "strict": 3.0,
    "standard": 1.0,
    "soft": 0.3,
}

# --- Penalty-Gewichte (Klassen A/B/C) -------------------------------------
PENALTY_BASE_COST: float = 1.0
PENALTY_CLASS_WEIGHTS: dict[str, float] = {"A": 10.0, "B": 3.0, "C": 1.0}

# --- Objective-Strategien -------------------------------------------------
OBJECTIVE_STRATEGIES: tuple[str, ...] = (
    "balance_then_cost",  # nach Milch-Welfare-Kette: Stage letztlich EUR/kg TM (+Baseline-Slack)
    "balance_only",       # gleiche Kette; letzte Stage EUR/kg TM + Welfare-Zuschlag
    "cost_only",          # Milch max -> direkt Kosten (Welfare-Stufe entfaellt)
)
# Stage 2: Zusatzterm zu den Futterpreisen bei balance_only:
#   min sum x_i * (price_i + STAGE2_WELFARE_WEIGHT * welfare_i).
# Vorher war Stufe 2 rein euro — praktisch zu stark zur Preisecke gezogen,
# sobald mehrere LP-Punkte zulaessig sind. Kalibrierung: ~1,0–1,5 im
# Verhaeltnis zu typischen Welfare-Koeffizienten (~0,7–1,1) und €/kg (~0,2–0,6).
STAGE2_WELFARE_WEIGHT_BALANCE_ONLY: float = 1.28

# --- Milch-Lexikografie (mehrstufiges LP, ab 2026-04) ---------------------
# Obergrenze fuer die Hilfsvariable „limitierende Milch“ [kg/d]: Ist-Leistung
# aus dem Profil plus diesem relativen Aufschlag (Planungskorridor).
MILK_TARGET_HEADROOM_FRAC: float = 0.05
# Maximal erlaubte relative Einbusse der limitierenden Milch zwischen zwei
# Solver-Stufen (Milch optimum -> Welfare -> Kosten je kg TM),
# falls nicht durch disable_milk_tradeoff_between_stages abgeschaltet.
MILK_TRADEOFF_MAX_PCT_PER_STAGE_DEFAULT: float = 2.5
