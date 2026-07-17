"""FEED-RBAC-048 (TDD-Red-Welle 1): vereinheitlichtes Stammdaten-Audit und
mandantenkonfigurierbares Vier-Augen-Prinzip. Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.tenant import get_tenant_id
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


@pytest.mark.parametrize(("method", "path", "body"), [
    ("get", "/feeding/audit/master-data", None),
    ("get", "/feeding/policies", None),
    ("put", "/feeding/policies", {"four_eyes_approval": True}),
])
def test_governance_endpoints_reject_user_without_role(method: str, path: str, body: dict | None) -> None:
    from app.api.v1.endpoints import feeding_governance
    app = FastAPI()
    app.include_router(feeding_governance.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = getattr(role_client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

def test_master_data_mutations_emit_readable_audit_events() -> None:
    suffix = uuid4().hex[:8]

    business = client.post(f"{ROOT}/feeding/businesses", headers=HEADERS,
                           json={"name": f"Auditbetrieb {suffix}"})
    assert business.status_code == 201, business.text
    business_id = business.json()["id"]

    grant = client.post(f"{ROOT}/feeding/businesses/{business_id}/grants", headers=HEADERS,
                        json={"subject": f"berater-{suffix}", "scope": "read"})
    assert grant.status_code == 201, grant.text

    feed = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"GOV-{suffix}", "name": f"Auditfutter {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved"})
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    reference = client.post(f"{ROOT}/feed-catalog/feeds/{feed_id}/reference-values",
                            headers=HEADERS, json={
                                "nutrient_code": "dry_matter", "value": "35",
                                "unit_code": "percent", "basis": "dry_matter",
                                "source_type": "analysis", "source_ref": f"gov {suffix}"})
    assert reference.status_code == 201, reference.text

    audit = client.get(f"{ROOT}/feeding/audit/master-data?entity_id={business_id}",
                       headers=HEADERS)
    assert audit.status_code == 200, audit.text
    business_events = audit.json()
    assert any(item["entity_type"] == "business" and item["event_type"] == "created"
               for item in business_events), business_events
    grant_events = client.get(
        f"{ROOT}/feeding/audit/master-data?entity_type=grant", headers=HEADERS).json()
    my_grant = next(item for item in grant_events
                    if item["delta"].get("subject") == f"berater-{suffix}")
    assert my_grant["event_type"] == "granted"
    assert my_grant["actor"], "Actor ist Teil des fachlich lesbaren Events"

    feed_events = client.get(
        f"{ROOT}/feeding/audit/master-data?entity_id={feed_id}", headers=HEADERS).json()
    types = {(item["entity_type"], item["event_type"]) for item in feed_events}
    assert ("feed", "created") in types
    assert ("analysis", "reference_value_added") in types
    named = next(item for item in feed_events if item["event_type"] == "created")
    assert named["delta"].get("name") == f"Auditfutter {suffix}", \
        "Delta traegt den fachlichen Namen, nicht nur IDs"


def _approver_client() -> TestClient:
    """Zweiter Akteur mit Freigaberecht gegen die echte Dev-DB."""
    from app.api.v1.endpoints import rations_lifecycle

    def _db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(rations_lifecycle.router)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "vier-augen-freigeber", "roles": ["FUTTERMITTEL_ADMIN"]}
    app.dependency_overrides[get_tenant_id] = lambda: TENANT
    app.dependency_overrides[get_db] = _db
    return TestClient(app, raise_server_exceptions=False)


def test_four_eyes_policy_blocks_self_approval_when_enabled() -> None:
    suffix = uuid4().hex[:8]

    enabled = client.put(f"{ROOT}/feeding/policies", headers=HEADERS,
                         json={"four_eyes_approval": True})
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["four_eyes_approval"] is True

    try:
        group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
            "name": f"VierAugen {suffix}", "animal_count": 12, "feeding_system": "TMR",
            "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
        assert group.status_code == 201, group.text
        ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
            "group_id": group.json()["id"], "name": f"VierAugen {suffix}",
            "snapshot": {"components": [{"feed_id": f"va-{suffix}", "name": "VA", "kg_fm": 10.0}]}})
        assert ration.status_code == 201, ration.text
        version_id = ration.json()["latest_version_id"]

        submit = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                             headers=HEADERS, json={"target_status": "in_review",
                                                    "expected_status": "draft"})
        assert submit.status_code == 200, submit.text

        # Einreicher versucht selbst freizugeben -> 409 mit klarer Meldung
        self_approve = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                                   headers=HEADERS, json={"target_status": "approved",
                                                          "expected_status": "in_review",
                                                          "reason": "Selbstfreigabe"})
        assert self_approve.status_code == 409, self_approve.text
        assert "Vier-Augen" in self_approve.json()["detail"]

        # anderer Freigeber darf
        with _approver_client() as approver:
            approved = approver.post(f"/lifecycle/versions/{version_id}/transitions",
                                     json={"target_status": "approved",
                                           "expected_status": "in_review",
                                           "reason": "Fachlich geprueft"})
            assert approved.status_code == 200, approved.text
    finally:
        disabled = client.put(f"{ROOT}/feeding/policies", headers=HEADERS,
                              json={"four_eyes_approval": False})
        assert disabled.status_code == 200


def test_without_policy_self_approval_stays_allowed() -> None:
    suffix = uuid4().hex[:8]
    policy = client.get(f"{ROOT}/feeding/policies", headers=HEADERS)
    assert policy.status_code == 200
    assert policy.json()["four_eyes_approval"] is False, "Default = heutiges Verhalten"

    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"OhnePolicy {suffix}", "animal_count": 12, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"OhnePolicy {suffix}",
        "snapshot": {"components": [{"feed_id": f"op-{suffix}", "name": "OP", "kg_fm": 10.0}]}})
    version_id = ration.json()["latest_version_id"]
    for target, expected in (("in_review", "draft"), ("approved", "in_review")):
        response = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                               headers=HEADERS, json={"target_status": target,
                                                      "expected_status": expected})
        assert response.status_code == 200, response.text
