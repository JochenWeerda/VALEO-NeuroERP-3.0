"""Report-Berechtigungen als Studio-Liste mit Kommandowegen (09.11.2026): je Rolle und Auswertung eine, nur Admin."""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)

_PFAD = "/api/v1/admin/report-permissions"


@pytest.fixture(scope="module")
def mandant():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    tid = f"rp-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id) ON CONFLICT (id) DO NOTHING"),
                  {"id": tid})
    yield tid
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.admin_report_permissions WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = :t"), {"t": tid})


def _client(rollen):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {"sub": "admin-rp", "roles": rollen}
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def admin():
    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    yield _client(["admin"])
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def test_anlegen_aendern_entfernen(admin, mandant):
    kopf = {"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"}
    erst = admin.post(f"{_PFAD}/actions/anlegen", headers=kopf, json={
        "role_id": "controller", "report_key": "finance.bwa", "can_export": True,
        "allowed_scopes": "filiale-1, filiale-2"}).json()
    assert erst["success"] is True, erst
    doppelt = admin.post(f"{_PFAD}/actions/anlegen", headers=kopf,
                         json={"role_id": "controller", "report_key": "finance.bwa"}).json()
    assert doppelt["success"] is False and "schon" in doppelt["error"]
    [zeile] = admin.get(f"{_PFAD}?active_only=false", headers=kopf).json()
    assert (zeile["can_view"], zeile["can_export"], zeile["allowed_scopes"]) == (True, True, ["filiale-1", "filiale-2"])
    geaendert = admin.post(f"{_PFAD}/{zeile['id']}/actions/aendern", headers=kopf, json={
        "role_id": "controller", "report_key": "finance.bwa", "can_view": True, "can_export": False}).json()
    assert geaendert["success"] is True, geaendert
    assert admin.get(f"{_PFAD}?active_only=false", headers=kopf).json()[0]["can_export"] is False
    ohne_grund = admin.post(f"{_PFAD}/{zeile['id']}/actions/entfernen", headers=kopf, json={}).json()
    assert ohne_grund["success"] is False
    weg = admin.post(f"{_PFAD}/{zeile['id']}/actions/entfernen", headers=kopf,
                     json={"_auditReason": "Rolle aufgeloest"}).json()
    assert weg["success"] is True, weg
    assert admin.get(f"{_PFAD}?active_only=false", headers=kopf).json() == []


def test_ohne_adminrolle_kein_schreibweg(mandant):
    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    try:
        antwort = _client(["CRM_BEARBEITEN"]).post(
            f"{_PFAD}/actions/anlegen", headers={"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"},
            json={"role_id": "vertrieb", "report_key": "sales.umsatz"})
        assert antwort.status_code == 403
    finally:
        if vorher is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = vorher
