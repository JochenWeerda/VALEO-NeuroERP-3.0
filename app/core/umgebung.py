"""In welcher Umgebung laeuft VALEO? (M5, Nutzerentscheid 25.11.2026)

Zielmodell: LOCAL (Entwicklung), CI (automatisierte Pruefung), STAGING (Integration, Spiegelbetrieb), PRODUCTION.
Gesetzt ausdruecklich ueber ``VALEO_UMGEBUNG``. **Fehlt der Schalter oder ist er unbekannt, gilt PRODUCTION** - eine
vergessene Einstellung darf nie mehr Rechte geben.

Agentenmatrix (Nutzer 25.11.2026): In LOCAL und CI duerfen Agenten autonom implementieren, testen und synthetische Daten
verarbeiten - alle deklarierten Kommandowege sind fuer sie offen. In STAGING und PRODUCTION gilt die Freigabe je Aktion
(``write_capabilities``, Default Deny). Fachregeln der Maske (forbiddenForAgents, humanApprovalRequired: Zahlungen,
Buchungen, irreversible Loeschungen ...) gelten in **jeder** Umgebung.
"""
from __future__ import annotations

import os
from enum import Enum


class Umgebung(str, Enum):
    LOCAL = "local"
    CI = "ci"
    STAGING = "staging"
    PRODUCTION = "production"


#: Umgebungen, in denen Agenten ohne Freigabe je Aktion schreiben duerfen (nur synthetische Daten).
AGENTEN_AUTONOM = frozenset({Umgebung.LOCAL, Umgebung.CI})


def aktuelle_umgebung() -> Umgebung:
    wert = (os.environ.get("VALEO_UMGEBUNG") or "").strip().lower()
    try:
        return Umgebung(wert)
    except ValueError:
        return Umgebung.PRODUCTION


def agenten_autonom() -> bool:
    return aktuelle_umgebung() in AGENTEN_AUTONOM
