"""Sachkundenachweis-Prüfung für Pflanzenschutz (Lastenheft Kap. 10/25)."""
from __future__ import annotations

from datetime import date
from typing import Any, Optional


def pruefe_sachkunde(
    *,
    anwender: Optional[str],
    sachkunde_nummer: Optional[str],
    gueltig_bis: Optional[date],
    anwendungsdatum: Optional[date],
) -> dict[str, Any]:
    """Prüft, ob ein Anwender zum Anwendungszeitpunkt sachkundeberechtigt ist."""
    fehlende: list[str] = []
    if not (anwender or "").strip():
        fehlende.append("Anwender")
    if not (sachkunde_nummer or "").strip():
        fehlende.append("Sachkundenachweis")
    if gueltig_bis is None:
        fehlende.append("Sachkunde-Gueltigkeit")
    elif anwendungsdatum is not None and gueltig_bis < anwendungsdatum:
        fehlende.append("Sachkundenachweis abgelaufen")
    return {"erlaubt": len(fehlende) == 0, "fehlende": fehlende}
