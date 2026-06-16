"""Integrationstests Fuhrpark-Vertiefung: Statushistorie, Schadensfälle, Bußgeld, Wartungsvorhersage, Leasing.

Markers: integration, needs_live_db — nicht in CI-Smoke-Runs.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from main import app

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


def _vertiefung_tables_ready() -> bool:
    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'domain_ops' "
                "AND table_name IN ('ops_fahrzeug_status_historie', 'ops_fahrzeug_schaeden', 'ops_fahrzeug_bussgeld')"
            )
        ).scalar()
        return int(n or 0) == 3
    finally:
        db.close()


def _get_or_create_fahrzeug() -> str | None:
    """Liefert eine Fahrzeug-ID aus ops_fahrzeuge, oder None wenn Tabelle leer."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT id FROM domain_ops.ops_fahrzeuge LIMIT 1")
        ).fetchone()
        return str(row[0]) if row else None
    finally:
        db.close()


@pytest.fixture(scope="module")
def fahrzeug_id() -> str:
    if not _vertiefung_tables_ready():
        pytest.skip("Fuhrpark-Vertiefung-Tabellen fehlen — bitte alembic upgrade head ausführen.")
    fid = _get_or_create_fahrzeug()
    if fid is None:
        pytest.skip("Keine Fahrzeuge in domain_ops.ops_fahrzeuge — Seed erforderlich.")
    return fid


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
        db = SessionLocal()
        try:
            lsg = db.execute(
                text("SELECT leasinggesellschaft FROM domain_ops.ops_fahrzeuge WHERE id = :id"),
                {"id": fahrzeug_id},
            ).scalar()
        finally:
            db.close()

        if lsg:
            pytest.skip("Test-Fahrzeug hat bereits eine Leasinggesellschaft — skip Fehlerfall.")

        r = client.post(
            f"/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}/leasing-rueckgabe",
            json={"rueckgabedatum": "2026-06-16T12:00:00Z", "km_stand_bei_rueckgabe": 145000},
            headers=HEADERS,
        )
        assert r.status_code == 422
