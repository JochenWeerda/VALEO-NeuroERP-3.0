"""Financial Reports API — echte HTTP-Vertraege (SPEC-P0-05).

Erfordert PostgreSQL (`require_db`). Keine Mock-DB, keine weichen Status-Mengen.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/finance/financial-reports"
PERIOD = "2026-03"

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("path", ["/balance-sheet", "/profit-loss", "/bwa"])
def test_reports_return_200_with_period(require_db, path):
    resp = client.get(
        f"{BASE}{path}",
        params={"period": PERIOD, "tenant_id": "system"},
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), dict)


def test_balance_sheet_with_explicit_as_of_date(require_db):
    resp = client.get(
        f"{BASE}/balance-sheet",
        params={"period": PERIOD, "as_of_date": "2026-03-31", "tenant_id": "system"},
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["period"] == PERIOD
    assert "assets" in body
    assert "is_balanced" in body


@pytest.mark.parametrize("path", ["/balance-sheet", "/profit-loss", "/bwa"])
def test_reports_invalid_period_returns_400(require_db, path):
    resp = client.get(f"{BASE}{path}", params={"period": "2026"}, headers=HEADERS)
    assert resp.status_code == 400, resp.text
    assert "YYYY-MM" in resp.text


def test_drilldown_returns_list(require_db):
    resp = client.get(
        f"{BASE}/drilldown",
        params={"account_number": "1200", "period": PERIOD, "limit": 50, "tenant_id": "system"},
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_export_json_known_and_unknown(require_db):
    for rt in ("balance-sheet", "profit-loss", "bwa"):
        resp = client.get(
            f"{BASE}/export/{rt}",
            params={"period": PERIOD, "format": "json", "tenant_id": "system"},
            headers=HEADERS,
        )
        assert resp.status_code == 200, (rt, resp.text)
        assert resp.json()["report_type"] == rt

    bad = client.get(
        f"{BASE}/export/nonexistent-report",
        params={"period": PERIOD, "format": "json"},
        headers=HEADERS,
    )
    assert bad.status_code == 400, bad.text


def test_periodenvergleich_structure(require_db):
    resp = client.get(
        f"{BASE}/periodenvergleich",
        params={
            "periode_aktuell": PERIOD,
            "periode_vergleich": "2026-02",
            "konto_klasse": "4",
            "tenant_id": "system",
        },
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "zeilen" in body and "count" in body


def test_beleg_drilldown_unknown_is_404(require_db):
    resp = client.get(f"{BASE}/beleg-drilldown/{uuid.uuid4()}", headers=HEADERS)
    assert resp.status_code == 404, resp.text
