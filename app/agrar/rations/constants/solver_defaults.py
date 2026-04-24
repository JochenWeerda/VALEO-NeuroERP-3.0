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
    "balance_then_cost",  # Stufe 1 fachliche Balance, Stufe 2 Kosten
    "balance_only",       # nur fachliche Balance (Gutachten-Modus)
    "cost_only",          # klassische reine Kostenoptimierung
)
