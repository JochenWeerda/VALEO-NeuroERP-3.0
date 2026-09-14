"""LOG-FRACHTBRIEF-001 — HTTP-Vertraege fuer /api/v1/logistik/frachtbriefe."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


TENANT = "00000000-0000-0000-0000-000000000001"


@pytest.fixture()
def client(require_db):
    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def _auth_headers():
    return {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT}


@pytest.fixture()
def frachtbrief_nummer():
    """Eindeutige Belegnummer je Lauf; der Beleg wird danach wieder entfernt."""
    nummer = f"IT-FB-{uuid.uuid4().hex[:10]}"
    yield nummer

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        db.execute(
            text(
                "DELETE FROM domain_logistics.frachtbriefe "
                "WHERE tenant_id = :t AND nummer = :n"
            ),
            {"t": TENANT, "n": nummer},
        )
        db.commit()
    finally:
        db.close()


def _payload(nummer: str) -> dict:
    return {
        "nummer": nummer,
        "kennzeichen": "HH-AB 123",
        "artikel": "Weizen",
        "menge": 24.5,
        "absender": "Muster GmbH",
        "empfaenger": "Ziel GmbH",
        "datum": str(date.today()),
    }


class TestFrachtbriefeEndpoint:
    def test_list_frachtbriefe_returns_list(self, client: TestClient):
        resp = client.get("/api/v1/logistik/frachtbriefe", headers=_auth_headers())
        assert resp.status_code == 200, resp.text
        assert isinstance(resp.json(), list)

    def test_create_frachtbrief_persists_and_is_listed(
        self, client: TestClient, frachtbrief_nummer: str
    ):
        resp = client.post(
            "/api/v1/logistik/frachtbriefe",
            json=_payload(frachtbrief_nummer),
            headers=_auth_headers(),
        )
        assert resp.status_code == 201, resp.text
        created = resp.json()
        assert created["nummer"] == frachtbrief_nummer
        assert created["status"] == "erstellt"
        assert created["id"]

        listed = client.get(
            "/api/v1/logistik/frachtbriefe",
            params={"limit": 500},
            headers=_auth_headers(),
        )
        assert listed.status_code == 200, listed.text
        assert any(r["id"] == created["id"] for r in listed.json()), (
            "angelegter Frachtbrief fehlt in der Liste — create ohne Persistenz"
        )

    def test_duplicate_nummer_is_409_not_server_error(
        self, client: TestClient, frachtbrief_nummer: str
    ):
        first = client.post(
            "/api/v1/logistik/frachtbriefe",
            json=_payload(frachtbrief_nummer),
            headers=_auth_headers(),
        )
        assert first.status_code == 201, first.text

        second = client.post(
            "/api/v1/logistik/frachtbriefe",
            json=_payload(frachtbrief_nummer),
            headers=_auth_headers(),
        )
        assert second.status_code == 409, second.text
        assert second.json()["detail"]["nummer"] == frachtbrief_nummer

    def test_status_transition_is_applied(
        self, client: TestClient, frachtbrief_nummer: str
    ):
        created = client.post(
            "/api/v1/logistik/frachtbriefe",
            json=_payload(frachtbrief_nummer),
            headers=_auth_headers(),
        )
        assert created.status_code == 201, created.text
        fb_id = created.json()["id"]

        patched = client.patch(
            f"/api/v1/logistik/frachtbriefe/{fb_id}/status",
            params={"status": "unterwegs"},
            headers=_auth_headers(),
        )
        assert patched.status_code == 200, patched.text
        assert patched.json()["status"] == "unterwegs"

    def test_status_patch_rejects_invalid_enum(self, client: TestClient):
        resp = client.patch(
            "/api/v1/logistik/frachtbriefe/nonexistent/status",
            params={"status": "ungueltig"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422, resp.text

    def test_status_patch_unknown_id_is_404(self, client: TestClient):
        resp = client.patch(
            f"/api/v1/logistik/frachtbriefe/{uuid.uuid4()}/status",
            params={"status": "unterwegs"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 404, resp.text
