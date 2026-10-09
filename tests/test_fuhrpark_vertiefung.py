"""Integrationstests Fuhrpark-Vertiefung: Statushistorie, Schadensfälle, Bußgeld, Wartungsvorhersage, Leasing.

Markers: integration, needs_live_db — nicht in CI-Smoke-Runs.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlalchemy import text

from app.api.v1.endpoints import fuhrpark
from app.auth.deps_oidc import get_current_user
from app.core.database import get_db
from app.domains.operations.repository import FahrzeugRepository
from test_fuhrpark_isolation_effects import db

app = FastAPI()
app.include_router(fuhrpark.router, prefix="/api/v1")

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


@pytest.fixture(autouse=True)
def isolated_client(db):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "fuhrpark-integration-test", "scopes": ["logistics:read", "logistics:write"],
        "raw": {"tenant_id": TENANT_ID},
    }
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def fahrzeug_id(db) -> str:
    """Only our own vehicle; outer probe transaction rolls back every mutation."""
    row = FahrzeugRepository(db).create(TENANT_ID, {
        "kennzeichen": "TEST-" + uuid4().hex[:8], "typ": "LKW",
        "leasinggesellschaft": None,
    }, commit=False)
    db.commit()
    return row.id


# ── Status-Historie ───────────────────────────────────────────────────────────

class TestStatusHistorie:
    def test_status_wechsel_valide(self, fahrzeug_id: str) -> None:
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/status",
            json={"zu_status": "wartung", "grund": "TÜV fällig", "km_stand": 120000},
            headers=HEADERS,
        )
        assert r.status_code in (200, 201), r.text
        data = r.json()
        assert data.get("id") == fahrzeug_id

    def test_status_wechsel_ungueltig(self, fahrzeug_id: str) -> None:
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/status",
            json={"zu_status": "UNGUELTIG_XYZ"},
            headers=HEADERS,
        )
        assert r.status_code == 422

    def test_status_historie_liste(self, fahrzeug_id: str) -> None:
        r = client.get(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/status-historie",
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_status_wechsel_zurueck_verfuegbar(self, fahrzeug_id: str) -> None:
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/status",
            json={"zu_status": "verfuegbar"},
            headers=HEADERS,
        )
        assert r.status_code in (200, 201)


# ── Schadensfälle ─────────────────────────────────────────────────────────────

class TestSchaeden:
    def _anlegen(self, fahrzeug_id: str) -> dict:
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/schaeden",
            json={
                "datum": "2026-06-16T08:00:00Z",
                "ort": "BAB 7, km 200",
                "beschreibung": "Frontschaden durch Wildunfall",
                "schadenhoehe_eur": 3500.00,
                "versicherung_gemeldet": True,
                "status": "offen",
            },
            headers=HEADERS,
        )
        assert r.status_code in (200, 201), r.text
        return r.json()

    def test_schaden_anlegen_und_abrufen(self, fahrzeug_id: str) -> None:
        schaden = self._anlegen(fahrzeug_id)
        assert schaden.get("id")
        assert schaden.get("status") == "offen"

        r = client.get(f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/schaeden", headers=HEADERS)
        assert r.status_code == 200
        ids = [s["id"] for s in r.json()]
        assert schaden["id"] in ids

    def test_schaden_abschliessen(self, fahrzeug_id: str) -> None:
        schaden = self._anlegen(fahrzeug_id)
        schaden_id = schaden["id"]

        r = client.patch(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/schaeden/{schaden_id}",
            json={"status": "abgeschlossen", "abgeschlossen_am": "2026-06-16T10:00:00Z"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json().get("status") == "abgeschlossen"

    def test_schaden_filter_status(self, fahrzeug_id: str) -> None:
        r = client.get(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/schaeden?status=offen",
            headers=HEADERS,
        )
        assert r.status_code == 200
        for s in r.json():
            assert s["status"] == "offen"


# ── Bußgeld ───────────────────────────────────────────────────────────────────

class TestBussgeld:
    def _anlegen(self, fahrzeug_id: str) -> dict:
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/bussgeld",
            json={
                "datum": "2026-06-16T09:00:00Z",
                "tatbestand": "Überladung §34 StVZO",
                "betrag_eur": 395.00,
                "ort": "Weende-Nord, BAB 7",
            },
            headers=HEADERS,
        )
        assert r.status_code in (200, 201), r.text
        return r.json()

    def test_bussgeld_anlegen(self, fahrzeug_id: str) -> None:
        bg = self._anlegen(fahrzeug_id)
        assert bg.get("id")
        assert bg.get("status") == "offen"
        assert float(bg.get("betrag_eur", 0)) == pytest.approx(395.00, rel=1e-3)

    def test_bussgeld_bezahlen(self, fahrzeug_id: str) -> None:
        bg = self._anlegen(fahrzeug_id)
        bg_id = bg["id"]

        r = client.patch(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/bussgeld/{bg_id}",
            json={"status": "bezahlt", "bezahlt_am": "2026-06-16T11:00:00Z"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json().get("status") == "bezahlt"

    def test_bussgeld_liste(self, fahrzeug_id: str) -> None:
        r = client.get(f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/bussgeld", headers=HEADERS)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ── Wartungsvorhersage ────────────────────────────────────────────────────────

class TestWartungsVorhersage:
    def test_vorhersage_struktur(self, fahrzeug_id: str) -> None:
        r = client.get(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/wartung-vorhersage",
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert "aktueller_km_stand" in data
        assert "vorhersagen_nach_km" in data
        assert isinstance(data["vorhersagen_nach_km"], list)


# ── Leasing-Rückgabe ──────────────────────────────────────────────────────────

class TestLeasingRueckgabe:
    def test_rueckgabe_ohne_leasing_schlaegt_fehl(self, fahrzeug_id: str) -> None:
        """Fahrzeuge ohne leasinggesellschaft müssen 422 liefern."""
        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/leasing-rueckgabe",
            json={"rueckgabedatum": "2026-06-16T12:00:00Z", "km_stand_bei_rueckgabe": 145000},
            headers=HEADERS,
        )
        assert r.status_code == 422
