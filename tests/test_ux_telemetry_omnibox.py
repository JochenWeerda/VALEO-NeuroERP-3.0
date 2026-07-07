"""UIX-060: Omnibox-Telemetrie — datenschutzfreundliche Intent-Signale.

Erfasst nur SHA-256-Hashes (kein Klartext), tenant-isoliert; liefert ein
Aggregat je getroffener Maske fuer das M2-Tuning.
"""
from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000abc",
}
BASE = "/api/v1/ux-telemetry/omnibox"


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_record_signal_returns_204():
    resp = client.post(
        BASE,
        headers=HEADERS,
        json={
            "intent_hash": _hash("offene posten folkerts"),
            "matched_screen_id": "finance/ar-open-item",
            "confidence": 0.82,
            "accepted": True,
        },
    )
    assert resp.status_code == 204, resp.text
    assert resp.content == b""


def test_cleartext_intent_is_rejected():
    """Klartext statt Hash → 422 (Datenschutz-Vertrag)."""
    resp = client.post(
        BASE,
        headers=HEADERS,
        json={
            "intent_hash": "offene posten folkerts",
            "matched_screen_id": "finance/ar-open-item",
            "confidence": 0.82,
            "accepted": True,
        },
    )
    assert resp.status_code == 422


def test_confidence_out_of_bounds_rejected():
    resp = client.post(
        BASE,
        headers=HEADERS,
        json={"intent_hash": _hash("x"), "confidence": 1.5, "accepted": False},
    )
    assert resp.status_code == 422


def test_aggregate_reflects_accepted_ratio_and_avg_confidence():
    tenant = {"Authorization": "Bearer dev-token", "X-Tenant-Id": "00000000-0000-0000-0000-0000000aggr1"}
    for conf, accepted in [(0.9, True), (0.7, True), (0.5, False)]:
        client.post(
            BASE,
            headers=tenant,
            json={
                "intent_hash": _hash(f"zahlungslauf {conf}"),
                "matched_screen_id": "finance/payment-run",
                "confidence": conf,
                "accepted": accepted,
            },
        )
    resp = client.get(f"{BASE}/aggregate", headers=tenant)
    assert resp.status_code == 200, resp.text
    by_screen = {e["matched_screen_id"]: e for e in resp.json()["entries"]}
    pr = by_screen["finance/payment-run"]
    assert pr["total"] == 3
    assert pr["accepted"] == 2
    assert pr["avg_confidence"] == round((0.9 + 0.7 + 0.5) / 3, 4)


def test_aggregate_is_tenant_isolated():
    ta = {"Authorization": "Bearer dev-token", "X-Tenant-Id": "00000000-0000-0000-0000-00000tenanta"}
    tb = {"Authorization": "Bearer dev-token", "X-Tenant-Id": "00000000-0000-0000-0000-00000tenantb"}
    client.post(
        BASE,
        headers=ta,
        json={"intent_hash": _hash("kunde 10233"), "matched_screen_id": "crm/customer-360", "confidence": 0.6, "accepted": True},
    )
    resp_b = client.get(f"{BASE}/aggregate", headers=tb)
    screens_b = {e["matched_screen_id"] for e in resp_b.json()["entries"]}
    assert "crm/customer-360" not in screens_b


def test_null_match_signal_is_recorded():
    tenant = {"Authorization": "Bearer dev-token", "X-Tenant-Id": "00000000-0000-0000-0000-00000nullmt1"}
    resp = client.post(
        BASE,
        headers=tenant,
        json={"intent_hash": _hash("qwertzblah"), "matched_screen_id": None, "confidence": 0.1, "accepted": False},
    )
    assert resp.status_code == 204
    agg = client.get(f"{BASE}/aggregate", headers=tenant).json()["entries"]
    assert any(e["matched_screen_id"] is None and e["total"] == 1 for e in agg)
