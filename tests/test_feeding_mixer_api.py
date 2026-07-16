"""FEED-INT-035: Mischtechnik bidirektional (TDD-Red-Welle 1).

Vor der Implementierung geschrieben; scheiterte zunaechst mit ImportError auf
app.api.v1.endpoints.feeding_mixer.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

_CONTEXT: dict[str, Any] = {"roles": []}


def _build_role_app() -> FastAPI:
    from app.api.v1.endpoints import feeding_mixer
    app = FastAPI()
    app.include_router(feeding_mixer.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


@pytest.mark.parametrize(("method", "path", "body"), [
    ("get", "/feeding/plans/versions/v-1/mixer-export", None),
    ("post", "/feeding/mixer-feedback", {
        "plan_version_id": "v-1", "client_ref": "m-1",
        "loaded": [{"feed_id": "f-1", "kg_loaded": 100.0}]}),
])
def test_mixer_endpoints_reject_user_without_domain_role(method: str, path: str, body: dict | None) -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as client:
        response = getattr(client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _approved_ration_version(suffix: str, feed_id: str) -> tuple[str, str]:
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Mixer {suffix}", "animal_count": 50, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"MixerRation {suffix}",
        "snapshot": {"components": [
            {"feed_id": feed_id, "name": "Grassilage", "kg_fm": 24.0},
        ]}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]
    for target, expected in (("in_review", "draft"), ("approved", "in_review")):
        transition = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                                 headers=HEADERS,
                                 json={"target_status": target, "expected_status": expected})
        assert transition.status_code == 200, transition.text
    return group.json()["id"], version_id


def _publish_plan(version_id: str, key: str) -> dict[str, Any]:
    response = client.post(f"{ROOT}/feeding/plans/publish", headers=HEADERS, json={
        "source_ration_version_id": version_id, "animal_count": 48,
        "dosing_step_kg": 5, "rounding_mode": "nearest",
        "valid_from": str(date.today()), "reason": "Mischwagen-Testplan fuer Export",
        "idempotency_key": key})
    assert response.status_code == 201, response.text
    return response.json()


def _create_feed(suffix: str) -> str:
    response = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"MX-{suffix}", "name": f"Mixer-Gras {suffix}",
        "art": "Grundfutter", "feed_kind": "forage",
        "trockensubstanz": 35.0, "protein": 16.0, "energie": 10.4,
        "preis_pro_t": 70.0})
    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


def test_mixer_export_and_idempotent_feedback_with_conflict_quarantine() -> None:
    suffix = uuid4().hex[:8]
    feed_id = _create_feed(suffix)
    _group_id, version_id = _approved_ration_version(suffix, feed_id)
    plan_v1 = _publish_plan(version_id, f"mix-{suffix}-1")

    # Export der aktuellen Planversion: Maschinenformat mit stabiler Referenz
    export = client.get(f"{ROOT}/feeding/plans/versions/{plan_v1['id']}/mixer-export",
                        headers=HEADERS)
    assert export.status_code == 200, export.text
    doc = export.json()
    assert doc["reference"] == plan_v1["id"]
    assert doc["format"] == "agrirouter-feeding-plan-v1"
    assert doc["loads"], "Export enthaelt Mischinstruktionen"
    assert doc["loads"][0]["feed_id"] == feed_id
    assert doc["loads"][0]["target_batch_kg"] > 0

    # Rueckmeldung idempotent auf die Planversion
    feedback_body = {
        "plan_version_id": plan_v1["id"], "client_ref": f"wagen-{suffix}",
        "loaded": [{"feed_id": feed_id, "kg_loaded": float(doc["loads"][0]["target_batch_kg"]) - 12.0}],
        "residual_kg": 35.0,
    }
    first = client.post(f"{ROOT}/feeding/mixer-feedback", headers=HEADERS, json=feedback_body)
    assert first.status_code == 201, first.text
    result = first.json()
    assert result["plan_version_id"] == plan_v1["id"]
    assert result["lines"][0]["delta_kg"] == pytest.approx(-12.0)
    assert 0 < result["accuracy_pct"] < 100

    second = client.post(f"{ROOT}/feeding/mixer-feedback", headers=HEADERS, json=feedback_body)
    assert second.status_code == 201, second.text
    assert second.json()["id"] == result["id"], "client_ref muss idempotent sein"
    assert second.json()["duplicate"] is True

    # Neue Planversion macht v1 stale -> Export von v1 ist 409,
    # Rueckmeldung auf v1 geht NICHT verloren, sondern in die Quarantaene (Monitor)
    plan_v2 = _publish_plan(version_id, f"mix-{suffix}-2")
    assert plan_v2["version_no"] == plan_v1["version_no"] + 1

    stale_export = client.get(f"{ROOT}/feeding/plans/versions/{plan_v1['id']}/mixer-export",
                              headers=HEADERS)
    assert stale_export.status_code == 409

    stale_feedback = client.post(f"{ROOT}/feeding/mixer-feedback", headers=HEADERS, json={
        "plan_version_id": plan_v1["id"], "client_ref": f"spaet-{suffix}",
        "loaded": [{"feed_id": feed_id, "kg_loaded": 100.0}]})
    assert stale_feedback.status_code == 202, stale_feedback.text
    conflict = stale_feedback.json()
    assert conflict["quarantined"] is True
    assert conflict["import_job_id"]

    jobs = client.get(f"{ROOT}/feeding/imports?status=quarantined", headers=HEADERS)
    assert jobs.status_code == 200
    assert any(job["id"] == conflict["import_job_id"] for job in jobs.json())

    # Unbekannte Planversion -> 404; unbekanntes Futter in der Rueckmeldung -> 422
    missing = client.post(f"{ROOT}/feeding/mixer-feedback", headers=HEADERS, json={
        "plan_version_id": str(uuid4()), "client_ref": "x",
        "loaded": [{"feed_id": feed_id, "kg_loaded": 10.0}]})
    assert missing.status_code == 404

    wrong_feed = client.post(f"{ROOT}/feeding/mixer-feedback", headers=HEADERS, json={
        "plan_version_id": plan_v2["id"], "client_ref": f"falsch-{suffix}",
        "loaded": [{"feed_id": str(uuid4()), "kg_loaded": 10.0}]})
    assert wrong_feed.status_code == 422
