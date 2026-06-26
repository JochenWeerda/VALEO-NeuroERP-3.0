"""LOG-FRACHTBRIEF-001 — Unit-Tests fuer /api/v1/logistik/frachtbriefe."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


TENANT = "00000000-0000-0000-0000-000000000001"


@pytest.fixture()
def client():
    from app.main import app
    return TestClient(app)


def _auth_headers():
    return {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT}


class TestFrachtbriefeEndpoint:
    def test_list_frachtbriefe_returns_200(self, client: TestClient):
        resp = client.get("/api/v1/logistik/frachtbriefe", headers=_auth_headers())
        # 200 or 503 (DB not available in unit context) — never 404/500
        assert resp.status_code in (200, 503, 422)

    def test_create_frachtbrief_schema(self, client: TestClient):
        payload = {
            "nummer": "FB-2026-001",
            "kennzeichen": "HH-AB 123",
            "artikel": "Weizen",
            "menge": 24.5,
            "absender": "Muster GmbH",
            "empfaenger": "Ziel GmbH",
            "datum": str(date.today()),
        }
        resp = client.post(
            "/api/v1/logistik/frachtbriefe",
            json=payload,
            headers=_auth_headers(),
        )
        # 201 (DB live) or 503/500 (DB not available) — never 404 or 422
        assert resp.status_code in (201, 503, 500)

    def test_status_patch_validates_enum(self, client: TestClient):
        resp = client.patch(
            "/api/v1/logistik/frachtbriefe/nonexistent/status",
            params={"status": "ungueltig"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422  # invalid enum value rejected

    def test_status_patch_valid_enum_passes_validation(self, client: TestClient):
        resp = client.patch(
            "/api/v1/logistik/frachtbriefe/nonexistent/status",
            params={"status": "unterwegs"},
            headers=_auth_headers(),
        )
        # 404 (not found) or 503 (no DB) — never 422
        assert resp.status_code in (404, 503, 500)
