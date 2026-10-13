"""Rechte an Belegen — einmal definiert, fuer Belegweg, DocFlow-Kommandos und MCP-Werkzeuge.

Bis zum 13.10.2026 konnte jeder angemeldete Benutzer eines Mandanten jeden DocFlow-Beleg mit Preisen lesen,
buchen und stornieren. Jetzt entscheidet die Rolle der Anmeldung, je Recht und Belegart. Die Rollen sind die
vorhandenen der Bereiche (``app/auth/finance_roles.py``); es gibt kein zweites Rechtesystem.

Sechs Rechte:

* ``lesen``       — den Beleg sehen (Mengen, Stand, Kette)
* ``preise``      — dazu Preise, Rabatte, Steuer und Summen
* ``bearbeiten``  — anlegen, aendern, Entwurf loeschen, Folgebeleg erstellen, Druck und Export vermerken
* ``ausstellen``  — freigeben (endgueltige Belegnummer)
* ``buchen``      — an Finance uebergeben
* ``stornieren``  — zuruecknehmen

Auslegung (die einfachste, die zu den vorhandenen Rollen passt):

* Der Beleg gehoert seinem Bereich: Verkaufsbelege dem Verkauf, Einkaufsbelege dem Einkauf. Die Sachbearbeitung
  des Bereichs bearbeitet und stellt aus.
* Lieferschein und Wareneingang bearbeitet auch das Lager. Das Lager liest alle Belege, aber ohne Preise.
* Buchen darf die Sachbearbeitung des Bereichs und die Buchhaltung — die Buchung selbst macht Finance.
* Einen gebuchten Beleg stornieren (Risikoklasse R4) darf die Buchhaltung und die Leitung des Bereichs, nicht die
  Sachbearbeitung. Einen Beleg, den Finance nicht bucht (Angebot, Auftrag, Lieferschein, Bestellung,
  Wareneingang), nimmt zurueck, wer ihn bearbeiten darf.

Freigabe im Sinn des Standards MCP-WRITE (ab R3) ist hier das aktionsgebundene Recht einer angemeldeten Person.
Eine eigene Freigabe mit Bindung an Belegversion und Frist, oder ein Vier-Augen-Schritt, ist das nicht.
"""
from __future__ import annotations

from typing import Any, Iterable

from fastapi import HTTPException, status

from app.core.belegvertrag import BELEGARTEN

RECHTE: tuple[str, ...] = ("lesen", "preise", "bearbeiten", "ausstellen", "buchen", "stornieren")

_IMMER = frozenset({"admin"})
_FINANZ_LESEN = frozenset({"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN"})
_FINANZ_BUCHEN = frozenset({"FINANCE_BEARBEITEN", "FINANCE_ADMIN"})
_LAGER_LESEN = frozenset({"LAGER_LESEN", "LAGER_BEARBEITEN", "LAGER_ADMIN"})
_LAGER_BEARBEITEN = frozenset({"LAGER_BEARBEITEN", "LAGER_ADMIN"})
_LAGERBELEGE = frozenset({"sales_delivery", "goods_receipt"})

_BEREICH: dict[str, dict[str, frozenset[str]]] = {
    "verkauf": {
        "lesen": frozenset({"SALES_LESEN", "SALES_BEARBEITEN", "SALES_ADMIN", "CRM_LESEN", "CRM_BEARBEITEN", "CRM_ADMIN"}),
        "bearbeiten": frozenset({"SALES_BEARBEITEN", "SALES_ADMIN"}),
        "leitung": frozenset({"SALES_ADMIN"}),
    },
    "einkauf": {
        "lesen": frozenset({"EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN"}),
        "bearbeiten": frozenset({"EINKAUF_BEARBEITEN", "EINKAUF_ADMIN"}),
        "leitung": frozenset({"EINKAUF_ADMIN"}),
    },
}


def rollen_fuer(recht: str, belegart: str) -> frozenset[str]:
    """Die Rollen, die dieses Recht an dieser Belegart haben."""
    variante = BELEGARTEN[belegart]
    bereich = _BEREICH[variante.richtung]
    manager = frozenset({"manager"})
    if recht == "preise":
        return _IMMER | manager | bereich["lesen"] | _FINANZ_LESEN
    if recht == "lesen":
        return rollen_fuer("preise", belegart) | _LAGER_LESEN
    bearbeiten = _IMMER | manager | bereich["bearbeiten"] | (_LAGER_BEARBEITEN if belegart in _LAGERBELEGE else frozenset())
    if recht in ("bearbeiten", "ausstellen"):
        return bearbeiten
    if recht == "buchen":
        return _IMMER | manager | bereich["bearbeiten"] | _FINANZ_BUCHEN
    if recht == "stornieren":
        return (_IMMER | bereich["leitung"] | _FINANZ_BUCHEN) if variante.bucht else bearbeiten
    raise KeyError(recht)


def rollen_von(nutzer: Any) -> set[str]:
    """Die Rollen der geprueften Anmeldung — aus dem Benutzerobjekt, sonst aus seinen Claims."""
    if not isinstance(nutzer, dict):
        return set(getattr(nutzer, "roles", None) or [])
    rollen: Iterable[str] | None = nutzer.get("roles")
    if rollen is None and isinstance(nutzer.get("raw"), dict):
        from app.auth.oidc import extract_roles
        rollen = extract_roles(nutzer["raw"])
    return {str(r) for r in rollen or []}


def darf(nutzer: Any, recht: str, belegart: str) -> bool:
    return belegart in BELEGARTEN and bool(rollen_von(nutzer) & rollen_fuer(recht, belegart))


def verlange(nutzer: Any, recht: str, belegart: str) -> None:
    """403, wenn das Recht fehlt. Belegarten ausserhalb des Belegvertrags (Kasse) prueft diese Stelle nicht."""
    if belegart in BELEGARTEN and not darf(nutzer, recht, belegart):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Keine Berechtigung: {BELEGARTEN[belegart].bezeichnung} {recht}.",
        )
