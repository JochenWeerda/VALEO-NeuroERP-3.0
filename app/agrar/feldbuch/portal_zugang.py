"""Portal-Feldbuch: welche Portalrolle welchen Weg nutzt (PORTAL-CONTEXT-001).

Aus ``app/api/v1/endpoints/portal_feldbuch.py`` ausgelagert, damit die Rechtepruefung an einer Stelle steht.
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Request

from app.auth.deps import get_current_user
from app.auth.portal_kunde import (
    AUSWERTUNGEN,
    FELDBUCH_LESEN,
    FELDBUCH_SCHREIBEN,
    FELDBUCH_VERWALTEN,
    PortalKunde,
    portal_kunde,
)


# Bis 14.10.2026 nahm dieses Feldbuch den Kunden aus dem Parameter ``customer_id``, der Anmeldekennung oder dem
# Rueckfall ``dev-customer`` — wer eine fremde Kunden-ID in die URL schrieb, las und aenderte deren Schlaege.
# Welche Wege eine Portalrolle nutzt, bestimmt ``PORTAL_RECHTE`` (PORTAL-CONTEXT-001): lesen, Massnahmen erfassen,
# Schlaege und Betrieb verwalten, Auswertungen. Ein Mitarbeiter sieht nur seine zugewiesenen Schlaege. Interne
# Betreuung liest das Feldbuch des gewaehlten Kunden; aendern darf sie es nur mit einer Agrar-Bearbeiterrolle.
_AGRAR_WRITE_ROLES = frozenset({"AGRAR_BEARBEITEN", "AGRAR_ADMIN", "admin"})

# Wege (relativ zu ``/feldbuch``) mit eigenem Recht; alle anderen: GET lesen, sonst Massnahmen erfassen.
_AUSWERTUNG_WEGE = frozenset({
    "/duengebilanz", "/anbauplan-uebersicht", "/stoffstrombilanz", "/ernte-auswertung", "/duengebedarf",
    "/pflanzenschutz-uebersicht", "/export",
})
_VERWALTEN_WEGE = frozenset({
    ("POST", "/schlaege"), ("PUT", "/schlaege/{schlag_id}"), ("DELETE", "/schlaege/{schlag_id}"),
    ("POST", "/import"), ("POST", "/andi-import"), ("POST", "/jahreswechsel"),
})


def benoetigtes_recht(request: Request) -> str:
    route = request.scope.get("route")
    pfad = getattr(route, "path", request.url.path)
    weg = pfad[pfad.index("/feldbuch") + len("/feldbuch"):] if "/feldbuch" in pfad else pfad
    if weg in _AUSWERTUNG_WEGE:
        return AUSWERTUNGEN
    if (request.method, weg) in _VERWALTEN_WEGE:
        return FELDBUCH_VERWALTEN
    return FELDBUCH_LESEN if request.method in ("GET", "HEAD") else FELDBUCH_SCHREIBEN


def feldbuch_kunde(
    request: Request,
    kunde: PortalKunde = Depends(portal_kunde),
    nutzer: dict = Depends(get_current_user),
) -> str:
    recht = benoetigtes_recht(request)
    if not kunde.darf(recht):
        raise HTTPException(status_code=403, detail=f"Keine Berechtigung im Portal: {recht}")
    if kunde.intern and request.method not in ("GET", "HEAD") and not (
        set((nutzer or {}).get("roles") or []) & _AGRAR_WRITE_ROLES
    ):
        raise HTTPException(status_code=403, detail="Keine Berechtigung: Feldbuch des Kunden bearbeiten.")
    return kunde.customer_id


def schlag_bereich(kunde: PortalKunde = Depends(portal_kunde)) -> Optional[tuple[str, ...]]:
    """Zugewiesene Schlaege eines Mitarbeiters; None = alle Schlaege des Kontos."""
    return kunde.schlag_ids


def im_bereich(bereich: Optional[tuple[str, ...]], schlag_id: Optional[str], was: str = "Schlag") -> None:
    if bereich is not None and (schlag_id is None or str(schlag_id) not in bereich):
        raise HTTPException(status_code=404, detail=f"{was} nicht gefunden")
