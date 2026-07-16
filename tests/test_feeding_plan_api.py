from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.tenant import get_tenant_id
from app.main import app

BASE = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def _business_group_ration() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    suffix = uuid4().hex[:8]
    business = client.post(f"{BASE}/feeding/businesses", headers=HEADERS, json={"name": f"Planbetrieb {suffix}"})
    assert business.status_code == 201, business.text
    group = client.post(f"{BASE}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Plan-Gruppe {suffix}", "external_ref": f"plan-{suffix}",
        "animal_count": 42, "business_id": business.json()["id"],
    })
    assert group.status_code == 201, group.text
    ration = client.post(f"{BASE}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"Planration {suffix}", "source": "editor",
        "snapshot": {"ration": [
            {"feed_id": "mineral", "feed_name": "Mineralfutter", "kg_fm": 0.157, "mixing_sequence": 1},
            {"feed_id": "grass", "feed_name": "Grassilage", "kg_fm": 12.345, "mixing_sequence": 2},
        ]},
    })
    assert ration.status_code == 201, ration.text
    return business.json(), group.json(), ration.json()


def _approve(version_id: str) -> None:
    for current, target, reason in (("draft", "in_review", None), ("in_review", "approved", "Fachlich geprueft")):
        response = client.post(f"{BASE}/lifecycle/versions/{version_id}/transitions", headers=HEADERS, json={
            "expected_status": current, "target_status": target, "reason": reason,
        })
        assert response.status_code == 200, response.text


def _publish(version_id: str, key: str, **patch: Any):
    payload = {
        "source_ration_version_id": version_id, "animal_count": 42,
        "dosing_step_kg": "0.5", "rounding_mode": "nearest",
        "valid_from": "2026-07-17", "valid_until": "2026-07-31",
        "reason": "Freigabe fuer die naechste Fuetterungsperiode", "idempotency_key": key,
    }
    payload.update(patch)
    return client.post(f"{BASE}/feeding/plans/publish", headers=HEADERS, json=payload)


def test_publish_plan_scales_instructions_and_writes_one_outbox_event() -> None:
    _, group, ration = _business_group_ration()
    version_id = ration["versions"][0]["id"]
    rejected = _publish(version_id, f"draft-{uuid4()}")
    assert rejected.status_code == 409
    assert "approved oder active" in rejected.json()["detail"]
    _approve(version_id)

    key = f"publish-{uuid4()}"
    published = _publish(version_id, key)
    assert published.status_code == 201, published.text
    plan = published.json()
    assert plan["group_id"] == group["id"]
    assert plan["version_no"] == 1
    assert [row["feed_id"] for row in plan["instructions"]] == ["mineral", "grass"]
    assert float(plan["instructions"][0]["raw_batch_kg"]) == pytest.approx(6.594)
    assert float(plan["instructions"][0]["target_batch_kg"]) == pytest.approx(6.5)

    repeated = _publish(version_id, key)
    assert repeated.status_code == 201
    assert repeated.json()["id"] == plan["id"]

    db = SessionLocal()
    try:
        events = db.execute(text("""SELECT payload FROM public.outbox_events
          WHERE tenant_id=:tenant_id AND event_type='feeding.plan.published'
            AND payload LIKE :needle"""), {"tenant_id": TENANT, "needle": f'%"plan_version_id": "{plan["id"]}"%'}).scalars().all()
        assert len(events) == 1
        event = json.loads(events[0])
        assert event["schema_version"] == "1.0"
        assert event["event_type"] == "feeding.plan.published"
        assert event["payload"]["source_ration_version_id"] == version_id
    finally:
        db.close()

    detail = client.get(f"{BASE}/feeding/plans/{plan['id']}", headers=HEADERS)
    assert detail.status_code == 200
    listed = client.get(f"{BASE}/feeding/plans?group_id={group['id']}", headers=HEADERS)
    assert listed.status_code == 200
    assert any(row["id"] == plan["id"] for row in listed.json())


def test_idempotency_payload_conflict_and_tenant_isolation() -> None:
    _, _, ration = _business_group_ration()
    version_id = ration["versions"][0]["id"]
    _approve(version_id)
    key = f"publish-{uuid4()}"
    assert _publish(version_id, key).status_code == 201
    conflict = _publish(version_id, key, animal_count=43)
    assert conflict.status_code == 409
    assert "anderem Inhalt" in conflict.json()["detail"]
    foreign = client.get(f"{BASE}/feeding/plans", headers={
        "Authorization": "Bearer dev-token", "X-Tenant-Id": str(uuid4()),
    })
    assert foreign.status_code == 200
    assert all(row["source_ration_version_id"] != version_id for row in foreign.json())

    invalid_dates = _publish(
        version_id, f"publish-{uuid4()}", valid_from="2026-08-01", valid_until="2026-07-31",
    )
    assert invalid_dates.status_code == 409
    assert "Gueltig-bis" in invalid_dates.json()["detail"]


def test_plan_version_and_instruction_are_database_immutable() -> None:
    _, _, ration = _business_group_ration()
    version_id = ration["versions"][0]["id"]
    _approve(version_id)
    plan = _publish(version_id, f"publish-{uuid4()}").json()
    db = SessionLocal()
    try:
        with pytest.raises(DBAPIError):
            db.execute(text("UPDATE domain_agrar.feeding_plan_versions SET animal_count=99 WHERE id=:id"), {"id": plan["id"]})
            db.commit()
        db.rollback()
        with pytest.raises(DBAPIError):
            db.execute(text("DELETE FROM domain_agrar.feeding_mixing_instructions WHERE plan_version_id=:id"), {"id": plan["id"]})
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_feeding_plan_endpoints_require_feed_roles() -> None:
    from app.api.v1.endpoints.feeding_plans import router
    local = FastAPI()
    local.include_router(router)
    local.dependency_overrides[get_current_user] = lambda: {"sub": "no-role", "roles": []}
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    local.dependency_overrides[get_db] = lambda: object()
    with TestClient(local) as role_client:
        assert role_client.get("/feeding/plans").status_code == 403
        assert role_client.post("/feeding/plans/publish", json={
            "source_ration_version_id": "version-1", "animal_count": 1,
            "dosing_step_kg": "1", "rounding_mode": "nearest",
            "valid_from": "2026-07-17", "reason": "Ausreichender Testgrund",
            "idempotency_key": "role-test-key",
        }).status_code == 403


def test_reader_without_business_grant_cannot_discover_plans() -> None:
    _, group, ration = _business_group_ration()
    version_id = ration["versions"][0]["id"]
    _approve(version_id)
    plan = _publish(version_id, f"publish-{uuid4()}").json()

    from app.api.v1.endpoints.feeding_plans import router
    local = FastAPI()
    local.include_router(router)
    local.dependency_overrides[get_current_user] = lambda: {
        "sub": f"external-reader-{uuid4()}", "roles": ["FUTTERMITTEL_LESEN"],
    }
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(local, raise_server_exceptions=False) as reader:
        listed = reader.get(f"/feeding/plans?group_id={group['id']}")
        assert listed.status_code == 404
        detail = reader.get(f"/feeding/plans/{plan['id']}")
        assert detail.status_code == 404

    editor_app = FastAPI()
    editor_app.include_router(router)
    editor_app.dependency_overrides[get_current_user] = lambda: {
        "sub": f"external-editor-{uuid4()}", "roles": ["FUTTERMITTEL_BEARBEITEN"],
    }
    editor_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(editor_app, raise_server_exceptions=False) as editor:
        denied = editor.post("/feeding/plans/publish", json={
            "source_ration_version_id": version_id, "animal_count": 42,
            "dosing_step_kg": "0.5", "rounding_mode": "nearest",
            "valid_from": "2026-07-17", "reason": "Nicht autorisierte Publikation",
            "idempotency_key": f"denied-{uuid4()}",
        })
        assert denied.status_code == 404
