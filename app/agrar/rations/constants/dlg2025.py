"""Fachliche Konstanten aus DLG-Information 01|2025 ("Energie- und
Nährstoffbedarf der Milchkuh aus Sicht der Praxis").

Kapitel 8.2 regelt die binäre Kaskade für aNDFomGF+CoP in Abhängigkeit
von der pabKH-Dichte. Die Werte sind 1:1 aus dem Merkblatt übernommen
und dürfen nur geändert werden, wenn ein neues DLG-Merkblatt dies
explizit vorsieht.

Historischer Fallback (DLG 01|2023, stärkeadaptives Modell) steht im
gleichen Modul unter dem Präfix ``ANDFOM_GF_*``.
"""

from __future__ import annotations

# --- DLG 01|2023 stärkeadaptives Fallback-Modell für aNDFomGF -------------
ANDFOM_GF_BASE_NON_PASTURE: float = 200.0
ANDFOM_GF_BASE_PASTURE: float = 180.0
ANDFOM_GF_STARCH_THRESHOLD: float = 180.0
ANDFOM_GF_STARCH_STEP: float = 20.0
ANDFOM_GF_STARCH_ADD_PER_STEP: float = 10.0
ANDFOM_GF_STARCH_ADD_CAP: float = 40.0

# --- DLG 01|2025 Kap. 8.2: binäre Kaskade für aNDFomGF+CoP ----------------
PABKH_THRESHOLD_LOW: float = 210.0   # pabKH-Grenzwert g/kg TM
PABKH_WARNING_HIGH: float = 260.0    # warnende pabKH-Obergrenze
ANDFOMGF_COP_LOW: float = 200.0      # aNDFomGF+CoP bei pabKH ≤ 210
ANDFOMGF_COP_HIGH: float = 280.0     # aNDFomGF+CoP bei pabKH > 210
ANDFOMGF_COP_LOW_PASTURE: float = 180.0  # weichere Schwelle PMR+Weide (DLG 01|2025)
