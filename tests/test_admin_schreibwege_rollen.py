"""Administrative Schreibwege verlangen eine ausdrueckliche Rolle (ADMIN-WRITE-ROLES-20261019).

Nutzerentscheid 19.10.2026: Schreibwege brauchen eine serverseitige Berechtigung aus dem bestehenden Rollenmodell,
administrative Aenderungen zuerst. Bis dahin konnte jede angemeldete Person eines Mandanten unter ``/api/v1/admin*``
Niederlassungen loeschen, Nummernkreise, Kassen, TSE-Geraete, Monitoring-Regeln oder Vordrucke aendern.

Modell wie ``admin_core``: Konfiguration ``admin``; Massenimport und Steuerexport ``admin``/``FINANCE_ADMIN``;
der Kassiervorgang (TSE-Transaktion) ist Fachaktion des Verkaufs. Die Pruefung greift vor jedem Datenbankzugriff,
deshalb braucht dieser Vertrag keine Daten.
"""
from __future__ import annotations

import re

import pytest
from fastapi.routing import APIRoute

from app.auth.deps import get_current_user
from app.main import app

pytestmark = pytest.mark.unit

KASSE = ("/api/v1/admin/pos/tse/transaction/start", "/api/v1/admin/pos/tse/transaction/finish")
LEITUNG_FINANZ = ("/api/v1/admin/pos/uebernahme-kasse", "/api/v1/admin/pos/dsfinvk-exports", "/api/v1/admin/pos/tse/export")


def _schreibwege():
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1/admin"):
            for methode in sorted(set(route.methods or ()) & {"POST", "PUT", "PATCH", "DELETE"}):
                yield methode, route.path


def _pfad(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "x", path)


@pytest.fixture()
def als():
    from fastapi.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)

    def setzen(*rollen: str):
        app.dependency_overrides[get_current_user] = lambda: {"sub": "pruef-sub", "name": "pruef", "roles": list(rollen)}
        return client

    yield setzen
    app.dependency_overrides.pop(get_current_user, None)


def _status(client, methode: str, path: str) -> int:
    return client.request(methode, _pfad(path), json={}, headers={"Authorization": "Bearer dev-token",
                                                                   "X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}).status_code


def test_fachanwender_ohne_adminrolle_wird_abgewiesen(als) -> None:
    client = als("SALES_BEARBEITEN", "LAGER_BEARBEITEN", "FINANCE_BEARBEITEN")  # Fachrollen, keine Leitung
    offen = [f"{m} {p}" for m, p in _schreibwege()
             if p not in KASSE and _status(client, m, p) != 403]
    assert offen == []


def _erlaubte_rollen(methode: str, path: str) -> set[str]:
    """Rollen der Rollen-Abhaengigkeiten des Wegs, ohne ihn auszufuehren (Erlaubt-Faelle laufen nie gegen Handler:
    Kassenuebernahme, Steuerexport, TSE und DMS-Bootstrap haben Wirkung oder rufen externe Dienste)."""
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path and methode in (route.methods or ()):
            rollen: set[str] = set()
            for dep in route.dependant.dependencies:
                for zelle in getattr(dep.call, "__closure__", None) or ():
                    inhalt = zelle.cell_contents
                    if isinstance(inhalt, tuple) and all(isinstance(r, str) for r in inhalt):
                        rollen |= set(inhalt)
            return rollen
    raise AssertionError(f"{methode} {path} nicht gefunden")


def test_kassiervorgang_bleibt_beim_verkauf(als) -> None:
    for path in KASSE:
        assert "SALES_BEARBEITEN" in _erlaubte_rollen("POST", path), path
    client = als("LAGER_BEARBEITEN")
    for path in KASSE:
        assert _status(client, "POST", path) == 403, path


def test_finanzleitung_darf_import_und_steuerexport(als) -> None:
    for path in LEITUNG_FINANZ:
        assert "FINANCE_ADMIN" in _erlaubte_rollen("POST", path), path
    assert _status(als("FINANCE_ADMIN"), "POST", "/api/v1/admin/branches") == 403


def test_admin_wird_nicht_abgewiesen() -> None:
    """Gegenprobe: Jeder Admin-Schreibweg laesst die Rolle ``admin`` zu."""
    ohne_admin = [f"{m} {p}" for m, p in _schreibwege() if "admin" not in _erlaubte_rollen(m, p)]
    assert ohne_admin == []
