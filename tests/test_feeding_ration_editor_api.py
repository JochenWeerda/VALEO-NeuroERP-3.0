"""FEED-EDITOR-021: API-Vertrag der Draft-Bewertung (RBAC + Journey).

TDD-Red-Welle 1: vor der Implementierung geschrieben (ImportError auf
app.api.v1.endpoints.feeding_ration_editor).
"""
from __future__ import annotations

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
    from app.api.v1.endpoints import feeding_ration_editor
    app = FastAPI()
    app.include_router(feeding_ration_editor.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


def test_draft_evaluate_rejects_user_without_domain_role() -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as client:
        response = client.post("/feeding/ration-drafts/evaluate", json={
            "group_id": "g-1", "components": [{"feed_id": "f-1", "kg_fm": 5.0}]})
    assert response.status_code == 403


# ── Journey (Dev-DB): Katalogfutter -> Profil -> Draft-Bewertung ────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _create_feed(suffix: str) -> str:
    response = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"ED-{suffix}", "name": f"Editor-Gras {suffix}",
        "art": "Grundfutter", "feed_kind": "forage",
        "trockensubstanz": 35.0, "protein": 16.0, "energie": 10.5,
        "preis_pro_t": 70.0,
    })
    assert response.status_code in (200, 201), response.text
    return response.json()["id"]


def test_editor_journey_evaluate_draft_against_profile() -> None:
    suffix = uuid4().hex[:8]
    feed_id = _create_feed(suffix)

    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Editor {suffix}", "animal_count": 12, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS, json={
        "group_id": group_id,
        "inputs": {"breed": "Holstein", "feeding_type": "TMR", "body_weight_kg": 650,
                   "milk_kg_day": 30, "milk_fat_pct": 4.0, "milk_protein_pct": 3.4,
                   "lactation_stage_days": 100, "parity": 2}})
    assert profile.status_code == 201, profile.text
    profile_id = profile.json()["id"]

    evaluation = client.post(f"{ROOT}/feeding/ration-drafts/evaluate", headers=HEADERS, json={
        "group_id": group_id, "requirement_profile_id": profile_id,
        "components": [{"feed_id": feed_id, "kg_fm": 30.0}]})
    assert evaluation.status_code == 200, evaluation.text
    payload = evaluation.json()

    assert payload["totals"]["dm_kg"] == pytest.approx(30.0 * 0.35, rel=1e-3)
    assert payload["positions"][0]["feed_id"] == feed_id
    assert payload["requirement_profile_id"] == profile_id
    assert isinstance(payload["findings"], list)
    metrics = {d["metric"] for d in payload["deltas"]}
    assert {"me_mj", "dm_kg"} <= metrics

    # Unbekanntes Futter -> 404 statt stiller Nullposition
    missing = client.post(f"{ROOT}/feeding/ration-drafts/evaluate", headers=HEADERS, json={
        "group_id": group_id, "requirement_profile_id": profile_id,
        "components": [{"feed_id": str(uuid4()), "kg_fm": 5.0}]})
    assert missing.status_code == 404

    # Fremdes Profil (anderer Tenant) ist nicht verwendbar
    foreign = client.post(f"{ROOT}/feeding/ration-drafts/evaluate",
                          headers={**HEADERS, "X-Tenant-Id": str(uuid4())},
                          json={"group_id": group_id, "requirement_profile_id": profile_id,
                                "components": [{"feed_id": feed_id, "kg_fm": 5.0}]})
    assert foreign.status_code == 404
