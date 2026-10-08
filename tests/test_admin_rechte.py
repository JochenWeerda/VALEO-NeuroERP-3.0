"""Verwaltungswege unter /api/v1/admin verlangen eine Rolle.

Bis zum 08.10.2026 prueften Benutzer-, Rollen- und API-Schluessel-Wege keine Rolle:
Jeder angemeldete Nutzer konnte Benutzer anlegen, sich selbst Rollen geben und
API-Schluessel erzeugen — eine Rechteausweitung bis zur Verwaltung.

Diese Vertraege pruefen die Abhaengigkeit, bevor irgendetwas geschrieben wird
(abgelehnte Aufrufe erreichen die Datenbank nicht).
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("API_DEV_TOKEN", "dev-token")

SACHBEARBEITER = {"sub": "lagerist", "roles": ["LAGER_BEARBEITEN"]}
MANAGER = {"sub": "leitung", "roles": ["manager"]}
KOPF = {"X-Tenant-ID": "default", "Authorization": "Bearer dev-token"}

SCHREIBEN = [
    ("post", "/api/v1/admin/benutzer", {"email": "x@y.example", "name": "X", "roles": ["admin"]}),
    ("put", "/api/v1/admin/benutzer/u-1", {"roles": ["admin"]}),
    ("delete", "/api/v1/admin/benutzer/u-1", None),
    ("post", "/api/v1/admin/rollen", {"name": "Superrolle"}),
    ("put", "/api/v1/admin/rollen/admin", {"name": "x"}),
    ("delete", "/api/v1/admin/rollen/admin", None),
    ("post", "/api/v1/admin/api-keys", {"name": "hintertuer"}),
    ("post", "/api/v1/admin/api-keys/k-1/rotate", None),
    ("post", "/api/v1/admin/api-keys/k-1/revoke", None),
    ("put", "/api/v1/admin/process-variants", {}),
    ("put", "/api/v1/admin/policy-overrides", {}),
]
LESEN = ["/api/v1/admin/benutzer", "/api/v1/admin/rollen", "/api/v1/admin/audit-log", "/api/v1/admin/api-keys"]


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def als(client):
    from app.auth.deps import get_current_user
    from app.main import app

    def setzen(nutzer):
        app.dependency_overrides[get_current_user] = lambda: nutzer

    yield setzen
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize("methode,weg,rumpf", SCHREIBEN)
def test_schreiben_nur_fuer_admin(client, als, methode, weg, rumpf):
    for nutzer in (SACHBEARBEITER, MANAGER):
        als(nutzer)
        antwort = getattr(client, methode)(weg, headers=KOPF, **({"json": rumpf} if rumpf is not None else {}))
        assert antwort.status_code == 403, (nutzer["sub"], weg, antwort.status_code)


@pytest.mark.parametrize("weg", LESEN)
def test_lesen_nur_fuer_leitung(client, als, weg):
    als(SACHBEARBEITER)
    assert client.get(weg, headers=KOPF).status_code == 403
    als(MANAGER)
    assert client.get(weg, headers=KOPF).status_code != 403


def test_jeder_schreibweg_traegt_eine_rolle():
    """Kein neuer Schreibweg unter /admin ohne Rollenpruefung."""
    from app.api.v1.endpoints.admin_core import router

    offen = [
        f"{','.join(sorted(r.methods))} {r.path}"
        for r in router.routes
        if (r.methods or set()) & {"POST", "PUT", "PATCH", "DELETE"}
        and not r.dependencies
        and r.path != "/workflow-sandbox/preview"  # Vorschau, schreibt nichts
    ]
    assert offen == []
