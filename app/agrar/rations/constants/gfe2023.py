"""Fachliche Konstanten aus dem GfE-Workshop 2023 und eng verwandten
DLG-Merkblättern (pH-Modell nach Zebeli 2008, FIKH nach DLG 01|2025
Kap. 8.4, FAN-Iteration per GfE-2023).

Alle Werte sind 1:1 aus den Primärquellen übernommen.
"""

from __future__ import annotations

# --- Zebeli-2008-Formel-Validitätsbereich (DLG 01|2025, Kap. 8.3) ---------
PH_PEN_DENS_MIN_KGDM: float = 60.0
PH_PEN_DENS_MAX_KGDM: float = 250.0
PH_STARCH_MIN_KGDM: float = 50.0
PH_STARCH_MAX_KGDM: float = 350.0
PH_DMI_MIN: float = 10.0
PH_DMI_MAX: float = 25.0

# --- Fermentationsindex Kohlenhydrate (DLG 01|2025, Kap. 8.4) -------------
FIKH_TARGET_PCT: float = 50.0

# --- FAN-Iteration (GfE-Workshop 2023 / DLG-Information 01|2025) ----------
FAN_DEFAULT_MODE: str = "auto_iterative"
FAN_DEFAULT_TOLERANCE: float = 0.05       # |FAN_out − FAN_in| ≤ 0.05 als Abbruch
FAN_DEFAULT_TOLERANCE_WARN: float = 0.10  # Warnschwelle für noch nicht konvergierte Iterationen
FAN_DEFAULT_MAX_ITERATIONS: int = 5
FAN_REFERENCE_PRESETS: tuple[float, ...] = (2.5, 3.0, 3.5)
FAN_REFERENCE_MIN: float = 2.0
FAN_REFERENCE_MAX: float = 5.0
FAN_MODES: tuple[str, ...] = ("auto_iterative", "reference", "evaluation_only")
