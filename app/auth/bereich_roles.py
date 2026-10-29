"""Schreibrechte je Bereich — aus dem bestehenden Rollenmodell, einmal definiert (WRITE-ROLES-20261019).

Nutzerentscheid 19.10.2026: Schreibwege brauchen eine ausdrueckliche serverseitige Berechtigung aus dem bestehenden
Rollenmodell; Fachaktionen behalten ihre Bereichsrollen und Freigaben. Die Rollen sind die Fachrollen aus
``config/keycloak/fachrollen.json`` (``*_BEARBEITEN``/``*_ADMIN``) und ``admin`` wie in ``app/auth/beleg_roles.py``
und ``app/auth/finance_roles.py``. Es gibt kein zweites Rechtesystem.

Je Weg haengt eine dieser Listen als ``dependencies=`` am Decorator. Wege mit eigener, strengerer Pruefung
(z. B. Finanzleitung, Vier-Augen) behalten sie zusaetzlich; die Liste hier ist die Untergrenze.
"""
from __future__ import annotations

from typing import Any

from fastapi import Depends

from app.auth.deps import get_current_user, require_roles

#: Technische Leitung. Die historische Rolle ``manager`` ist abgeloest (MANAGER-ROLE-ENFORCEMENT-20261019,
#: docs/architecture/security/role-description-contract.md) und erteilt keine Bereichsrechte.
_LEITUNG = ("admin",)


def _bearbeiten(*bereiche: str) -> tuple[str, ...]:
    return tuple(f"{b}_{stufe}" for b in bereiche for stufe in ("BEARBEITEN", "ADMIN")) + _LEITUNG


VERKAUF = _bearbeiten("SALES")
CRM = _bearbeiten("CRM", "SALES")
EINKAUF = _bearbeiten("EINKAUF")
LAGER = _bearbeiten("LAGER")
#: Stammdaten (Artikel, Partner) pflegen Einkauf, Verkauf und Lager.
STAMMDATEN = _bearbeiten("EINKAUF", "SALES", "LAGER")
#: Logistik, Touren, Fuhrpark und Zoll fuehren Lager, Verkauf und Einkauf (keine eigene Logistikrolle).
LOGISTIK = _bearbeiten("LAGER", "SALES", "EINKAUF")
AGRAR = _bearbeiten("AGRAR", "HARVEST", "KONTRAKT", "FUTTERMITTEL")
ERNTE = _bearbeiten("HARVEST", "AGRAR", "LAGER")
KONTRAKT = _bearbeiten("KONTRAKT", "AGRAR")
FUTTERMITTEL = _bearbeiten("FUTTERMITTEL", "AGRAR")
PRODUKTION = _bearbeiten("LAGER", "AGRAR", "FUTTERMITTEL")
FINANZ = _bearbeiten("FINANCE")
CONTROLLING = (*_bearbeiten("FINANCE"), "controller", "CONTROLLING")
PERSONAL = _bearbeiten("PERSONAL")
#: Belege, an denen mehrere Bereiche arbeiten (wie ``finance_roles.BELEG_WRITE_ROLES``).
BELEGE = _bearbeiten("FINANCE", "SALES", "EINKAUF", "LAGER")
#: Freigabe als zweite Person (APPROVAL-001, ``beleg_roles.rollen_fuer("freigeben")``): die Bereiche des Belegs, die
#: Buchhaltung und das Controlling. Die Funktionstrennung prueft die Approval Engine.
FREIGABE = (*BELEGE, "controller", "CONTROLLING")
#: Qualitaet, Reklamation, Nachweise: die Bereiche, deren Ware oder Beleg es betrifft.
QUALITAET = _bearbeiten("LAGER", "EINKAUF", "SALES", "AGRAR", "FUTTERMITTEL")
#: Bereichsuebergreifende Fachwege (Prozesskern, Agenten, Workflow, Berichte): eine Bearbeitungsrolle irgendeines
#: Bereichs. Reine Leser und Konten ohne Fachrolle schreiben nicht.
FACHLICH = _bearbeiten("SALES", "CRM", "EINKAUF", "LAGER", "AGRAR", "HARVEST", "KONTRAKT", "FUTTERMITTEL",
                       "FINANCE", "PERSONAL")
#: Bereichsuebergreifende Berechnungen ohne Schreibwirkung (Prozesskern: Policy aufloesen, pruefen, erklaeren):
#: eine Lese- oder Bearbeitungsrolle irgendeines Bereichs. Konten ohne Fachrolle rechnen nicht.
BERECHNEN = (*FACHLICH, *(f"{b}_LESEN" for b in ("SALES", "CRM", "EINKAUF", "LAGER", "AGRAR", "HARVEST",
                                                        "KONTRAKT", "FUTTERMITTEL", "FINANCE", "PERSONAL",
                                                        "QUALITAET", "SETTLEMENT")),
                  "controller", "CONTROLLING")
#: Plattformverwaltung (Mandanten, Nutzer, Identitaet, Konfiguration, Governance, Entwicklung/Abnahme).
PLATTFORM = ("admin",)


def _liste(rollen: tuple[str, ...]) -> list[Any]:
    return [Depends(require_roles(*rollen))]


SCHREIBEN = {name: _liste(rollen) for name, rollen in {
    "VERKAUF": VERKAUF, "CRM": CRM, "EINKAUF": EINKAUF, "LAGER": LAGER, "STAMMDATEN": STAMMDATEN,
    "LOGISTIK": LOGISTIK, "AGRAR": AGRAR, "ERNTE": ERNTE, "KONTRAKT": KONTRAKT, "FUTTERMITTEL": FUTTERMITTEL,
    "PRODUKTION": PRODUKTION, "FINANZ": FINANZ, "CONTROLLING": CONTROLLING, "PERSONAL": PERSONAL,
    "BELEGE": BELEGE, "FREIGABE": FREIGABE, "QUALITAET": QUALITAET, "FACHLICH": FACHLICH,
    "BERECHNEN": BERECHNEN, "PLATTFORM": PLATTFORM,
}.items()}


def eigene_daten_schreibrecht(user: dict = Depends(get_current_user)) -> dict:
    """Ausdrueckliche Berechtigung fuer persoenliche Daten (eigene Ansicht, Telemetrie, zuletzt geoeffnet):
    jede gepruefte Person, zugeordnet ueber ihre Kennung aus dem Token — nie fuer Daten anderer."""
    return user


def geraete_schreibrecht(user: dict = Depends(get_current_user)) -> dict:
    """Ausdrueckliche Berechtigung fuer Geraete- und Eingangswege (SPS, MDE, EPCIS, Webhooks, Rueckmeldungen):
    ein gepruefter, auch technischer Zugang des Mandanten; der Mandant kommt aus dem Token, der Inhalt wird
    fachlich geprueft. Eine Fachrolle wird hier bewusst nicht verlangt (sonst waeren Geraete ausgesperrt)."""
    return user


SCHREIBEN["EIGENE_DATEN"] = [Depends(eigene_daten_schreibrecht)]
SCHREIBEN["GERAET"] = [Depends(geraete_schreibrecht)]
