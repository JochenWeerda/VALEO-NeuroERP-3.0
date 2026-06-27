"""Wave 50 — Tests fuer neuro_compensation und neuro_consent."""

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
# neuro_compensation  /api/v1/neuro/compensate
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compensate_returns_200() -> None:
    payload = {
        "error": "Order creation failed",
        "strategy": "retry_linear",
        "context": {"order_id": "ORD-001"},
    }
    resp = _client.post("/api/v1/neuro/compensate", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert len(body) > 0


@pytest.mark.unit
def test_compensate_rollback_strategy() -> None:
    payload = {
        "error": "Payment failed",
        "strategy": "rollback",
        "rollback_steps": [{"action": "cancel_reservation", "entity_id": "RES-001"}],
    }
    resp = _client.post("/api/v1/neuro/compensate", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_compensate_missing_required_field() -> None:
    resp = _client.post("/api/v1/neuro/compensate", json={"strategy": "rollback"}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_compensation_get_run_not_found() -> None:
    resp = _client.get("/api/v1/neuro/compensate/nonexistent-run-xyz", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_compensation_retry_not_found() -> None:
    resp = _client.post("/api/v1/neuro/compensate/nonexistent-run-xyz/retry", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_compensate_and_retrieve_run() -> None:
    create_payload = {"error": "Test error for retrieval", "strategy": "escalate"}
    create_resp = _client.post("/api/v1/neuro/compensate", json=create_payload, headers=_HEADERS)
    assert create_resp.status_code == 200
    body = create_resp.json()
    run_id = body.get("run_id") or body.get("id")
    if not run_id:
        pytest.skip("Response does not include run_id — cannot test retrieval")
    get_resp = _client.get(f"/api/v1/neuro/compensate/{run_id}", headers=_HEADERS)
    assert get_resp.status_code == 200


# ---------------------------------------------------------------------------
# neuro_consent  /api/v1/neuro/consent
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_consent_check_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_consent as ep_mod

    monkeypatch.setattr(ep_mod, "check_consent", lambda eid, ctype, tid, db: {"granted": False, "entity_id": eid})
    payload = {"entity_id": "ENT-001", "consent_type": "marketing"}
    resp = _client.post("/api/v1/neuro/consent/check", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_consent_grant_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_consent as ep_mod

    monkeypatch.setattr(
        ep_mod, "grant_consent",
        lambda eid, ctype, purpose, tid, db: {"granted": True, "entity_id": eid, "consent_type": ctype},
    )
    payload = {"entity_id": "ENT-001", "consent_type": "marketing", "purpose": "Direktmarketing"}
    resp = _client.post("/api/v1/neuro/consent/grant", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_consent_revoke_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_consent as ep_mod

    monkeypatch.setattr(
        ep_mod, "revoke_consent",
        lambda eid, ctype, tid, db: {"revoked": True, "entity_id": eid},
    )
    payload = {"entity_id": "ENT-001", "consent_type": "marketing"}
    resp = _client.post("/api/v1/neuro/consent/revoke", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_consent_status_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.neuro_consent as ep_mod

    monkeypatch.setattr(
        ep_mod, "get_consent_status",
        lambda eid, tid, db: {"marketing": False, "analytics": True},
    )
    resp = _client.get("/api/v1/neuro/consent/ENT-001", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["entity_id"] == "ENT-001"
    assert "consents" in body


@pytest.mark.unit
def test_consent_check_missing_fields() -> None:
    resp = _client.post("/api/v1/neuro/consent/check", json={}, headers=_HEADERS)
    assert resp.status_code == 422
