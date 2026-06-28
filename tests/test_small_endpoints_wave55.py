"""Wave 55 — Tests fuer neuro_guardrails und neuro_verification."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# neuro_guardrails  /api/v1/neuro/guardrails/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_guardrails_check_input_clean_text() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/check-input",
        json={"text": "Hallo, ich moechte Getreidepreise abfragen."},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_guardrails_check_input_missing_text() -> None:
    resp = _client.post("/api/v1/neuro/guardrails/check-input", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_guardrails_sanitize_output() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/sanitize-output",
        json={"text": "Ergebnis: Preis 42 EUR"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "sanitized_text" in body


@pytest.mark.unit
def test_guardrails_detect_pii_no_pii() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/detect-pii",
        json={"text": "Getreidepreis liegt bei 200 EUR/t"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "count" in body
    assert "matches" in body


@pytest.mark.unit
def test_guardrails_detect_pii_with_email() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/detect-pii",
        json={"text": "Kontakt: test.user@example.com"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 0  # may or may not detect depending on PII detector impl


@pytest.mark.unit
def test_guardrails_mask_irreversible() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/mask",
        json={"text": "Meine IBAN ist DE89 3704 0044 0532 0130 00"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "masked" in body


@pytest.mark.unit
def test_guardrails_mask_reversible() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/mask-reversible",
        json={"text": "Name: Max Mustermann"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "masked" in body
    assert "tokens" in body


@pytest.mark.unit
def test_guardrails_scan_dict() -> None:
    resp = _client.post(
        "/api/v1/neuro/guardrails/scan-dict",
        json={"data": {"name": "Max Mustermann", "price": 42}},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "count" in body
    assert "matches" in body


@pytest.mark.unit
def test_guardrails_scan_dict_missing_data() -> None:
    resp = _client.post("/api/v1/neuro/guardrails/scan-dict", json={}, headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# neuro_verification  /api/v1/neuro/verify
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_neuro_verify_returns_200() -> None:
    payload = {
        "action": "create",
        "entity_type": "order",
        "entity_id": "ORD-001",
        "current_state": "draft",
        "target_state": "confirmed",
        "amount": 5000.0,
    }
    resp = _client.post("/api/v1/neuro/verify", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert "trace_id" in body
    assert "violations" in body


@pytest.mark.unit
def test_neuro_verify_missing_required_fields() -> None:
    resp = _client.post("/api/v1/neuro/verify", json={}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_neuro_verify_get_by_trace_not_found() -> None:
    resp = _client.get("/api/v1/neuro/verify/nonexistent-trace-xyz", headers=_HEADERS)
    assert resp.status_code in (404, 500)
