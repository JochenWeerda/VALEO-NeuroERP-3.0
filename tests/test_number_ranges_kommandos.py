"""Nummernkreise als Studio-Liste mit Kommandowegen (09.11.2026): Regeln des NumberRangeService, nur Admin."""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)

_PFAD = "/api/v1/admin/number-ranges"


@pytest.fixture(scope="module")
def mandant():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    tid = f"nk-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id) ON CONFLICT (id) DO NOTHING"),
                  {"id": tid})
    yield tid
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.number_ranges WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = :t"), {"t": tid})


def _client(rollen):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: {"sub": "admin-nk", "roles": rollen}
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


def test_konfigurieren_aendern_stilllegen(admin, mandant):
    kopf = {"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"}
    unbekannt = admin.post(f"{_PFAD}/actions/konfigurieren", headers=kopf,
                           json={"range_type": "irgendwas", "start_number": 1, "digit_count": 5}).json()
    assert unbekannt["success"] is False
    erst = admin.post(f"{_PFAD}/actions/konfigurieren", headers=kopf, json={
        "range_type": "debtor_account", "prefix": "D", "start_number": 10000, "digit_count": 5}).json()
    assert erst["success"] is True, erst
    [kreis] = admin.get(f"{_PFAD}/", headers=kopf).json()
    assert (kreis["range_type"], kreis["prefix"], kreis["is_active"]) == ("debtor_account", "D", True)
    kleiner = admin.post(f"{_PFAD}/{kreis['id']}/actions/aendern", headers=kopf,
                         json={"start_number": 10000, "digit_count": 4}).json()
    assert kleiner["success"] is False and "verkleinert" in kleiner["error"]
    groesser = admin.post(f"{_PFAD}/{kreis['id']}/actions/aendern", headers=kopf,
                          json={"prefix": "DB", "start_number": 20000, "digit_count": 6}).json()
    assert groesser["success"] is True, groesser
    [kreis] = admin.get(f"{_PFAD}/", headers=kopf).json()
    assert (kreis["prefix"], kreis["start_number"], kreis["digit_count"]) == ("DB", 20000, 6)
    still = admin.post(f"{_PFAD}/{kreis['id']}/actions/stilllegen", headers=kopf,
                       json={"_auditReason": "Nummern jetzt aus der Fibu"}).json()
    assert still["success"] is True, still
    assert admin.get(f"{_PFAD}/", headers=kopf).json()[0]["is_active"] is False


def test_ohne_adminrolle_kein_schreibweg(mandant):
    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    try:
        antwort = _client(["CRM_BEARBEITEN"]).post(
            f"{_PFAD}/actions/konfigurieren", headers={"X-Tenant-Id": mandant, "Authorization": "Bearer dev-token"},
            json={"range_type": "partner_number", "start_number": 1, "digit_count": 5})
        assert antwort.status_code == 403
    finally:
        if vorher is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = vorher
