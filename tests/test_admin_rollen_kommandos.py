"""Rollen als Studio-Liste mit Kommandowegen (09.11.2026): Systemrollen nur lesbar, Rolle mit Benutzern bleibt."""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)

_PFAD = "/api/v1/admin/rollen"


@pytest.fixture(scope="module")
def mandant():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    tid = f"ro-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id)"), {"id": tid})
    yield tid
    with engine.begin() as v:
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": tid})


@pytest.fixture()
def admin():
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "admin-ro", "roles": ["admin"]}
    yield TestClient(app, raise_server_exceptions=False)
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def test_anlegen_aendern_entfernen(admin, mandant):
    kopf = {"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"}
    erst = admin.post(f"{_PFAD}/actions/anlegen", headers=kopf, json={
        "name": "Disposition", "beschreibung": "Touren und Verladung", "rechte_liste": "logistik.read, logistik.write"}).json()
    assert erst["success"] is True, erst
    doppelt = admin.post(f"{_PFAD}/actions/anlegen", headers=kopf, json={"name": "disposition"}).json()
    assert doppelt["success"] is False and "schon" in doppelt["error"]
    rolle = next(r for r in admin.get(_PFAD, headers=kopf).json() if r["name"] == "Disposition")
    assert (rolle["rechte"], rolle["benutzer"]) == (2, 0)
    geaendert = admin.post(f"{_PFAD}/{rolle['id']}/actions/aendern", headers=kopf,
                           json={"name": "Disposition Nord", "beschreibung": "Nur Nord"}).json()
    assert geaendert["success"] is True, geaendert
    ohne_grund = admin.post(f"{_PFAD}/{rolle['id']}/actions/entfernen", headers=kopf, json={}).json()
    assert ohne_grund["success"] is False
    weg = admin.post(f"{_PFAD}/{rolle['id']}/actions/entfernen", headers=kopf,
                     json={"_auditReason": "Rolle zusammengelegt"}).json()
    assert weg["success"] is True, weg
    assert all(r["id"] != rolle["id"] for r in admin.get(_PFAD, headers=kopf).json())


def test_systemrolle_bleibt_lesbar(admin, mandant):
    from app.auth.scopes import ROLE_SCOPES

    kopf = {"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"}
    system = next(iter(ROLE_SCOPES))
    antwort = admin.post(f"{_PFAD}/{system}/actions/aendern", headers=kopf, json={"name": "Umbenannt"}).json()
    assert antwort["success"] is False
