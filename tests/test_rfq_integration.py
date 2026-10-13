"""Real RFQ business persistence with explicit isolated provider dependencies."""

from __future__ import annotations

from uuid import uuid4
from procurement_identity_fixture import keys, probe, procurement_context

import pytest
from fastapi.testclient import TestClient

from main import app

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

HEADERS = {}
client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


@pytest.fixture
def rfq_context(procurement_context, monkeypatch):
    monkeypatch.setitem(globals(), 'HEADERS', procurement_context.headers)
    created = client.post('/api/v1/einkauf/rfq',
                          json={'article_id': 'WEIZEN-A', 'quantity': 100, 'notes': 'IT-RFQ-'+procurement_context.namespace},
                          headers=HEADERS)
    assert created.status_code == 201, created.text
    yield {'rfq_id': created.json()['id'], 'supplier_id': procurement_context.supplier}


class TestRfqIntegration:
    def test_rfq_lifecycle_accept_creates_po(self, rfq_context):
        rfq_id = rfq_context["rfq_id"]
        supplier_id = rfq_context["supplier_id"]

        # Ohne Lieferanten geht nichts hinaus und der Status bleibt (bis 08.10.2026: "VERSENDET"
        # ohne eine Mail). Der Mailweg selbst: tests/test_versandwege_vertrag.py.
        sent = client.post(f"/api/v1/einkauf/rfq/{rfq_id}/send", json={}, headers=HEADERS)
        assert sent.status_code == 422, sent.text

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


@pytest.mark.parametrize('credential', [None, 'dev-token'])
def test_rfq_rejects_missing_or_legacy_identity(rfq_context, credential):
    headers = {'X-Tenant-ID': HEADERS['X-Tenant-ID']}
    if credential:
        headers['Authorization'] = 'Bearer '+credential
    response = client.get('/api/v1/einkauf/rfq', headers=headers)
    assert response.status_code == 401


def test_rfq_rejects_foreign_tenant_selector(rfq_context):
    response = client.get(f"/api/v1/einkauf/rfq/{rfq_context['rfq_id']}",
                          headers={**HEADERS, 'X-Tenant-ID': str(uuid4())})
    assert response.status_code == 403
