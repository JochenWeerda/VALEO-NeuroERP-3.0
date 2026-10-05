"""FEED-REL-047 (TDD-Red-Welle 1): Modul-Flag `feeding_advisory` gate't die
Feeding-Router mandantenweise. Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


def test_module_is_registered_and_enabled_by_default() -> None:
    from modules.bootstrap import initialize_module_registry
    from app.core.module_registry import registry

    initialize_module_registry()
    module = registry.get("feeding_advisory")
    assert module is not None, "feeding_advisory ist als Modul registriert"
    assert "agrar" in module.required_modules
    assert registry.is_enabled("feeding_advisory", tenant_id=TENANT), \
        "Default = aktiviert (heutiges Verhalten)"


def test_feeding_routes_reject_tenant_without_module(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(settings.TENANT_MODULE_FLAGS, TENANT, ["core", "agrar"])

    response = client.get(f"{ROOT}/feeding/plans/current", headers=HEADERS)
    assert response.status_code == 404, response.text
    assert "feeding_advisory" in response.json()["detail"], \
        "Meldung benennt das deaktivierte Modul"

    reports = client.get(f"{ROOT}/feeding/reports", headers=HEADERS)
    assert reports.status_code == 404

    # Nicht-Feeding-Routen des Agrar-Moduls bleiben nutzbar
    feeds = client.get(f"{ROOT}/feed-catalog/feeds", headers=HEADERS)
    assert feeds.status_code == 200, feeds.text


def test_feeding_routes_work_with_module_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(settings.TENANT_MODULE_FLAGS, TENANT,
                        ["core", "agrar", "feeding_advisory"])
    response = client.get(f"{ROOT}/feeding/plans/current", headers=HEADERS)
    assert response.status_code == 200, response.text
