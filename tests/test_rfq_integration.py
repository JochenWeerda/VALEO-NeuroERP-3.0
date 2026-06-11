"""Integrationstests RFQ (DOM-PROC-RFQ) — echte DB + API, keine Mocks."""

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
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


def _rfq_tables_ready() -> bool:
    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'domain_einkauf' "
                "AND table_name IN ('rfq_requests', 'rfq_quotes')"
            ),
        ).scalar()
        return int(n or 0) == 2
    finally:
        db.close()


def _ensure_rfq_schema() -> None:
    if _rfq_tables_ready():
        return
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "proc_rfq_20260611"],
        text=True,
        capture_output=True,
        env={**os.environ},
        timeout=180,
        check=False,
    )
    if result.returncode != 0 or not _rfq_tables_ready():
        pytest.skip(f"RFQ-Schema nicht migrierbar: {result.stderr[-400:]}")


def _ensure_tenant_and_supplier() -> str:
    db = SessionLocal()
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :name, :domain, TRUE) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": TENANT_ID, "name": "VALEO Demo", "domain": "demo.valeo.local"},
        )
        db.commit()
    finally:
        db.close()

    from scripts.seed_demo_procurement import seed

    seed()
    db = SessionLocal()
    try:
        row = db.execute(
            text(
                "SELECT lieferant_id FROM domain_einkauf.bestellungen "
                "WHERE tenant_id = :t AND bestellnummer = 'DEMO-PO-001' LIMIT 1"
            ),
            {"t": TENANT_ID},
        ).first()
        if not row:
            row = db.execute(
                text("SELECT id FROM domain_einkauf.lieferanten WHERE tenant_id = :t LIMIT 1"),
                {"t": TENANT_ID},
            ).first()
        if not row:
            pytest.skip("Kein Lieferant für Demo-Tenant — seed_demo_procurement ausführen")
        return str(row[0])
    finally:
        db.close()


def _purge_rfq(rfq_id: int) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text("DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                 "(SELECT id FROM domain_einkauf.bestellungen WHERE notiz LIKE :n)"),
            {"n": f"%RFQ #{rfq_id}%"},
        )
        db.execute(
            text("DELETE FROM domain_einkauf.bestellungen WHERE notiz LIKE :n"),
            {"n": f"%RFQ #{rfq_id}%"},
        )
        db.execute(
            text("DELETE FROM domain_einkauf.rfq_quotes WHERE rfq_id = :id AND tenant_id = :t"),
            {"id": rfq_id, "t": TENANT_ID},
        )
        db.execute(
            text("DELETE FROM domain_einkauf.rfq_requests WHERE id = :id AND tenant_id = :t"),
            {"id": rfq_id, "t": TENANT_ID},
        )
        db.commit()
    finally:
        db.close()


@pytest.fixture
def rfq_context(require_db):
    _ensure_rfq_schema()
    supplier_id = _ensure_tenant_and_supplier()
    created = client.post(
        "/api/v1/einkauf/rfq",
        json={"article_id": "WEIZEN-A", "quantity": 100, "notes": "IT-RFQ-Test"},
        headers=HEADERS,
    )
    assert created.status_code == 201, created.text
    rfq_id = created.json()["id"]
    yield {"rfq_id": rfq_id, "supplier_id": supplier_id}
    _purge_rfq(rfq_id)


class TestRfqIntegration:
    def test_rfq_lifecycle_accept_creates_po(self, rfq_context):
        rfq_id = rfq_context["rfq_id"]
        supplier_id = rfq_context["supplier_id"]

        sent = client.post(f"/api/v1/einkauf/rfq/{rfq_id}/send", json={}, headers=HEADERS)
        assert sent.status_code == 200
        assert sent.json()["status"] == "VERSENDET"

        q1 = client.post(
            f"/api/v1/einkauf/rfq/{rfq_id}/quotes",
            json={"supplier_id": supplier_id, "unit_price": 210.0, "delivery_days": 10},
            headers=HEADERS,
        )
        q2 = client.post(
            f"/api/v1/einkauf/rfq/{rfq_id}/quotes",
            json={"supplier_id": supplier_id, "unit_price": 205.5, "delivery_days": 7},
            headers=HEADERS,
        )
        assert q1.status_code == 201 and q2.status_code == 201

        cmp_res = client.get(f"/api/v1/einkauf/rfq/{rfq_id}/comparison", headers=HEADERS)
        assert cmp_res.status_code == 200
        quotes = cmp_res.json()["quotes"]
        assert quotes[0]["unit_price"] <= quotes[1]["unit_price"]
        assert quotes[0]["price_rank"] == 1

        best_id = quotes[0]["id"]
        accept = client.post(
            f"/api/v1/einkauf/rfq/{rfq_id}/accept/{best_id}",
            headers=HEADERS,
        )
        assert accept.status_code == 200
        body = accept.json()
        assert body["status"] == "ABGESCHLOSSEN"
        assert body["total_amount"] == pytest.approx(100 * 205.5)
        assert body["purchase_order_id"]

        detail = client.get(f"/api/v1/einkauf/rfq/{rfq_id}", headers=HEADERS)
        assert detail.json()["status"] == "ABGESCHLOSSEN"

    def test_rfq_list_includes_created(self, rfq_context):
        listed = client.get("/api/v1/einkauf/rfq", headers=HEADERS)
        assert listed.status_code == 200
        ids = [r["id"] for r in listed.json()]
        assert rfq_context["rfq_id"] in ids
