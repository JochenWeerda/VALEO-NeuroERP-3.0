"""Integrationstests Beschaffungs-Match (DOM-PROC-004) — echte DB + API, keine Mocks.

Voraussetzungen: PostgreSQL erreichbar, `alembic upgrade head`, Seed via
`scripts/seed_demo_procurement.py` (wird im Fixture nachgezogen).
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from main import app

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

TENANT_ID = "00000000-0000-0000-0000-000000000001"
PO_OK = "DEMO-PO-001"
PO_OVER = "DEMO-PO-002"
AUTH_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": TENANT_ID,
}

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


def _skip_if_db_unavailable(response) -> None:
    if response.status_code == 500:
        body = response.text
        if "OperationalError" in body or "Connection refused" in body:
            pytest.skip("PostgreSQL nicht erreichbar — docker compose up erforderlich")


def _skip_if_schema_missing(response) -> None:
    _skip_if_db_unavailable(response)
    if response.status_code == 500:
        body = response.text
        if "UndefinedTable" in body or "does not exist" in body or "relation" in body.lower():
            pytest.skip("Procurement-Schema fehlt — alembic upgrade head ausführen")


def _proc_tables_ready() -> bool:
    db = SessionLocal()
    try:
        ready = db.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'domain_einkauf' "
                "AND table_name IN ('procurement_follow_up', 'procurement_ers_credits')"
            ),
        ).scalar()
        finance = db.execute(
            text("SELECT to_regclass('public.finance_erechnungen')"),
        ).scalar()
        return int(ready or 0) == 2 and finance is not None
    finally:
        db.close()


def _ensure_proc_schema() -> None:
    if _proc_tables_ready():
        return
    env = {**os.environ}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "proc_ers_credit_20260611"],
        text=True,
        capture_output=True,
        env=env,
        timeout=180,
        check=False,
    )
    if result.returncode != 0 or not _proc_tables_ready():
        pytest.skip(
            "Procurement-Schema nicht migrierbar — alembic upgrade head manuell ausführen. "
            f"stderr={result.stderr[-500:]}"
        )


def _ensure_demo_tenant() -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.tenants (id, name, domain, is_active)
                VALUES (:id, :name, :domain, TRUE)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": TENANT_ID,
                "name": "VALEO Demo Tenant",
                "domain": "demo.valeo.local",
            },
        )
        db.commit()
    finally:
        db.close()


def _ensure_demo_seed() -> None:
    from scripts.seed_demo_procurement import seed

    _ensure_demo_tenant()
    seed()


def _purge_test_rows(po: str) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
                "DELETE FROM domain_einkauf.procurement_follow_up "
                "WHERE tenant_id = :t AND bestellnummer = :po AND grund LIKE 'IT-%'"
            ),
            {"t": TENANT_ID, "po": po},
        )
        db.execute(
            text(
                "DELETE FROM domain_einkauf.procurement_ers_credits "
                "WHERE tenant_id = :t AND bestellnummer = :po AND grund LIKE 'IT-%'"
            ),
            {"t": TENANT_ID, "po": po},
        )
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _procurement_match_fixture(require_db):
    _ensure_proc_schema()
    _ensure_demo_seed()
    _purge_test_rows(PO_OVER)
    yield
    _purge_test_rows(PO_OVER)


class TestProcurementMatchIntegration:
    def test_three_way_demo_po_001_abgeglichen(self):
        r = client.get(
            "/api/v1/procurement/match/three-way",
            params={"bestellung": PO_OK},
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(r)
        assert r.status_code == 200
        data = r.json()
        assert data["found"] is True
        assert data["summary"]["drei_wege_abgeglichen"] is True
        assert data["three_way"]["geliefert_wert"] == 27700.0
        assert data["three_way"]["fakturiert_netto"] == 27700.0

    def test_three_way_demo_po_002_ers_preview_960(self):
        r = client.get(
            "/api/v1/procurement/match/three-way",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(r)
        assert r.status_code == 200
        data = r.json()
        assert data["found"] is True
        assert data["summary"]["hat_abweichung"] is True
        preview = data["ers_preview"]
        assert preview["berechtigt"] is True
        assert preview["betrag_netto"] == 960.0

    def test_follow_up_append_only_and_eskalation_stufe(self):
        r1 = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "eskalation",
                "grund": "IT-Eskalation Stufe 1",
            },
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(r1)
        assert r1.status_code == 201
        assert r1.json()["eskalationsstufe"] == 1

        r2 = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "eskalation",
                "grund": "IT-Eskalation Stufe 2",
            },
            headers=AUTH_HEADERS,
        )
        assert r2.status_code == 201
        assert r2.json()["eskalationsstufe"] == 2

        listed = client.get(
            "/api/v1/procurement/match/follow-up",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert listed.status_code == 200
        items = listed.json()["items"]
        assert len(items) >= 2
        assert items[0]["eskalationsstufe"] >= items[1]["eskalationsstufe"]

    def test_ers_credit_create_and_list(self):
        preview = client.get(
            "/api/v1/procurement/match/ers/preview",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(preview)
        assert preview.status_code == 200
        assert preview.json()["ers_preview"]["betrag_netto"] == 960.0

        created = client.post(
            "/api/v1/procurement/match/ers",
            json={"bestellnummer": PO_OVER, "grund": "IT-ERS Überlieferung"},
            headers=AUTH_HEADERS,
        )
        assert created.status_code == 201
        body = created.json()
        assert body["betrag_netto"] == 960.0
        assert body["status"] == "entwurf"
        assert body["gutschrift_nummer"].startswith(f"ERS-{PO_OVER}-")

        listed = client.get(
            "/api/v1/procurement/match/ers",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert listed.status_code == 200
        assert any(x["id"] == body["id"] for x in listed.json()["items"])

    def test_follow_up_invalid_action_422(self):
        r = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "storno",
                "grund": "IT-invalid",
            },
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(r)
        assert r.status_code == 422

    def test_ers_not_eligible_422(self):
        r = client.post(
            "/api/v1/procurement/match/ers",
            json={"bestellnummer": PO_OK, "grund": "IT-sollte scheitern"},
            headers=AUTH_HEADERS,
        )
        _skip_if_schema_missing(r)
        assert r.status_code == 422
