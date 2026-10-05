"""Jahreswechsel: Schläge fortführen ohne Bewegungsdaten (Lastenheft Kap. 36)."""
from __future__ import annotations

from typing import Any


_COPY_FIELDS = (
    "name",
    "flik",
    "flaeche",
    "gemeinde",
    "gemarkung",
    "bodenart",
    "ackerzahl",
    "geometry_geojson",
)


def plan_jahreswechsel(
    *,
    schlaege: list[dict[str, Any]],
    von_jahr: int,
    nach_jahr: int,
) -> list[dict[str, Any]]:
    """Plant Stammdaten-Kopien von ``von_jahr`` nach ``nach_jahr``.

    Bewegungsdaten (Maßnahmen) werden bewusst nicht übernommen.
    Kultur des Vorjahres wird zur Vorkultur; Kultur bleibt leer (neu planen).
    """
    if int(nach_jahr) <= int(von_jahr):
        raise ValueError("nach_jahr muss groesser als von_jahr sein")

    geplant: list[dict[str, Any]] = []
    for s in schlaege:
        sj = s.get("wirtschaftsjahr")
        if sj is not None and int(sj) != int(von_jahr):
            continue
        if sj is None:
            # Ohne Jahresmarkierung nur übernehmen, wenn explizit alle
            # Vorjahresschläge gemeint sind — hier: nur markierte.
            continue
        neu: dict[str, Any] = {k: s.get(k) for k in _COPY_FIELDS}
        neu["vorkultur"] = s.get("kultur")
        neu["kultur"] = None
        neu["wirtschaftsjahr"] = int(nach_jahr)
        neu["status"] = "aktiv"
        neu["quelle_schlag_id"] = s.get("id")
        # DüV-Sollwerte/Nmin gehören zum neuen Jahr und werden nicht kopiert
        geplant.append(neu)
    return geplant
