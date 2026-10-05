"""QS-/GLOBALG.A.P.-Checkliste (ASK-QS-001)."""
from __future__ import annotations

from typing import Any

PFLICHTFELDER = (
    "schlagdokumentation_vollstaendig",
    "wartezeiten_eingehalten",
    "sachkunde_nachgewiesen",
    "geraetepruefung_gueltig",
    "risikobewertung_boden",
)


def evaluate_qs_checkliste(checks: dict[str, Any]) -> dict[str, Any]:
    offene = [k for k in PFLICHTFELDER if not bool(checks.get(k))]
    erfuellt = len(PFLICHTFELDER) - len(offene)
    return {
        "bestanden": len(offene) == 0,
        "erfuellt": erfuellt,
        "gesamt": len(PFLICHTFELDER),
        "offene": offene,
        "checks": {k: bool(checks.get(k)) for k in PFLICHTFELDER},
    }
