"""Deep-Link-Parameter aus Voice-Text fuer bestehende Nav-Action-IDs.

Spiegel der Extraktoren in services/ki-usability (ohne neuen Backend-Vertrag).
Nur relative Kennungen; Open-Redirect-Guard bleibt im Frontend-Dispatch.
"""

from __future__ import annotations

import re
from typing import Dict


def _first_id(*patterns: str, text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return None


def extract_deep_link_params(action_id: str, text: str) -> Dict[str, str]:
    """Liefert optionale Kennungen fuer Deep-Link-Nav-Actions."""
    if action_id == "nav-orders":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+auftrag\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"auftrag\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"auftrag_nr": value} if value else {}

    if action_id == "nav-lot":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+(?:lot|charge|partie)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"(?:lot|charge|partie)\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"lot_id": value} if value else {}

    if action_id == "nav-silo-cell":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+(?:silo)?zelle\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"(?:silo)?zelle\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"cell_code": value} if value else {}

    if action_id == "nav-einkauf":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+bestellung\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"bestellung\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"bestellung_id": value} if value else {}

    if action_id == "nav-lager":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+(?:bestand|artikel|lagerartikel)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"(?:bestand|artikel|lagerartikel)\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"artikel_id": value} if value else {}

    if action_id == "nav-nachweisraum":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+(?:dokument|nachweis)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"(?:dokument|nachweis)\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"dokument_id": value} if value else {}

    if action_id == "nav-agrar-vertraege":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+(?:kontrakt|vertrag)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"(?:kontrakt|vertrag)\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"kontrakt_id": value} if value else {}

    if action_id == "nav-wiegeschein":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+wiegeschein\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"wiegeschein\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"ticket_id": value} if value else {}

    if action_id == "nav-customers":
        value = _first_id(
            r"(?:oeffne|öffne|zeige|gehe\s+zu)\s+kunde(?:n)?\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            r"kunde(?:n)?\s+(?:oeffnen|öffnen)\s+([A-Za-z0-9][A-Za-z0-9._-]{0,63})\b",
            text=text,
        )
        return {"kunden_nr": value} if value else {}

    return {}
