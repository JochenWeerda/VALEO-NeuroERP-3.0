"""Rollen der Betriebswege (Lager, Produktion, Schnittstellen) — einmal definiert.

Bis zum 19.10.2026 hatten mehrere Schreibwege dieser Bereiche keine Rollenpruefung: Jede angemeldete Person
des Mandanten konnte Produktionsvorgaenge weiterschalten, Fremdware umlagern oder Inventur-Nebenlaeufe
anwenden. Lesen bleibt unveraendert; geschrieben wird nur mit Bearbeitungsrolle des Bereichs.
"""
from __future__ import annotations

from app.auth.deps import require_roles

_LEITUNG = ("admin",)  # ``manager`` ist abgeloest (MANAGER-ROLE-ENFORCEMENT-20261019)

LAGER_SCHREIBEN = ("LAGER_BEARBEITEN", "LAGER_ADMIN", *_LEITUNG)
#: Produktion (Mischen, Mahlen, Umbuchen) fuehrt das Lager mit der Agrar- bzw. Futtermittelsparte.
PRODUKTION_SCHREIBEN = ("LAGER_BEARBEITEN", "LAGER_ADMIN", "AGRAR_BEARBEITEN", "AGRAR_ADMIN",
                        "FUTTERMITTEL_BEARBEITEN", "FUTTERMITTEL_ADMIN", *_LEITUNG)
#: Freigeben und Anwenden einer Inventurbewertung veraendert Bestandswerte: Lagerleitung.
LAGER_LEITUNG = ("LAGER_ADMIN", *_LEITUNG)

lager_write = require_roles(*LAGER_SCHREIBEN)
lager_admin = require_roles(*LAGER_LEITUNG)
produktion_write = require_roles(*PRODUKTION_SCHREIBEN)

#: Tankanlage: Lieferungen der Zapfsaeulen pruefen und verarbeiten (Lager bzw. Verkauf an der Tankstelle).
TANK_SCHREIBEN = (*LAGER_SCHREIBEN, "SALES_BEARBEITEN", "SALES_ADMIN")
tank_write = require_roles(*TANK_SCHREIBEN)
