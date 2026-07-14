"""Pure calculations for daily feeding controlling."""
from __future__ import annotations

def energy_corrected_milk(milk_kg: float | None, fat_pct: float | None, protein_pct: float | None) -> float | None:
    if milk_kg is None or fat_pct is None or protein_pct is None: return None
    return round(milk_kg * (0.38 * fat_pct + 0.21 * protein_pct + 1.05) / 3.28, 3)

def nitrogen_efficiency(milk_kg: float | None, protein_pct: float | None, feed_n_kg: float | None) -> float | None:
    if milk_kg is None or protein_pct is None or not feed_n_kg or feed_n_kg <= 0: return None
    milk_n_kg = (milk_kg * protein_pct / 100.0) / 6.38
    return round(milk_n_kg / feed_n_kg * 100.0, 2)

def deviation(actual: float | None, target: float | None) -> float | None:
    return None if actual is None or target is None else round(actual - target, 3)
