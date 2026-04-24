"""Feeding-System-Konstanten: Konzentrat-Abruf-Staffel, TMR-Mischprotokoll.

Quellen: Praxis-Richtwerte (Holsteins großrahmig, PMR/TMR/Weide),
siehe Slice-2/3-Dokumentation im Workboard
(docs/agent-ops/active-workboard.md, Eintrag
FEEDING-SYSTEM-ARCHITECTURE Slices 1-3).
"""

from __future__ import annotations

# --- Konzentrat-Abruf-Staffel (Slice 2) ------------------------------------
# kg Konzentrat (FM) pro kg Zusatzmilch oberhalb der Basisleistung
# aus Grobfutter/Weide:
#   0.45 = Hochleistungs-Kraftfutter, hohe Energiedichte
#   0.50 = Standard-Kraftfutter (Energiestufe 3 nach alter DLG)
CONC_PER_ADDITIONAL_MILK_LOW: float = 0.45
CONC_PER_ADDITIONAL_MILK_HIGH: float = 0.50

# Annahme TM-Gehalt Praxis-Konzentrat ~88 % FM (Pellets, Schrot).
CONC_DEFAULT_DM_FRAC: float = 0.88

# Physiologisches Sicherheitsnetz: 1.5x des empfohlenen Tagesmaximums
# als absolute Obergrenze (hart im LP, Warnschwelle in der Staffel).
CONC_HARD_SAFETY_FACTOR: float = 1.5

# --- TMR-Mischprotokoll (Slice 3) ------------------------------------------
MIX_TARGET_DM_FRAC_DEFAULT: float = 0.40  # Zielfeuchte ~40 % TM im Mischwagen
MIX_OVERFILL_PCT_DEFAULT: float = 5.0     # Praxisaufschlag für Mischverluste

MIX_GROUP_LABELS: dict[int, str] = {
    1: "Strukturfutter",
    2: "Silagen",
    3: "Saftfutter / Co-Produkte",
    4: "Sonstiges",
    5: "Kraftfutter + Mineralien",
}
