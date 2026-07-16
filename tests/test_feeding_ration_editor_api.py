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

    bounded = client.post(f"{ROOT}/feeding/ration-drafts/evaluate", headers=HEADERS, json={
        "group_id": group_id, "requirement_profile_id": profile_id,
        "components": [{"feed_id": feed_id, "kg_fm": 30.0,
                        "min_kg_fm": 31.0, "max_kg_fm": 40.0}]})
    assert bounded.status_code == 200, bounded.text
    bounded_payload = bounded.json()
    assert bounded_payload["positions"][0]["min_kg_fm"] == 31.0
    finding = next(item for item in bounded_payload["findings"]
                   if item["code"] == "amount_outside_bounds")
    assert finding["feed_id"] == feed_id

    negative = client.post(f"{ROOT}/feeding/ration-drafts/evaluate", headers=HEADERS, json={
        "group_id": group_id, "requirement_profile_id": profile_id,
        "components": [{"feed_id": feed_id, "kg_fm": 30.0, "min_kg_fm": -1.0}]})
    assert negative.status_code == 422

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


def test_version_evaluation_is_persisted_from_snapshot_and_retrievable() -> None:
    """FEED-EDITOR-022: Bewertung einer Version wird serverseitig aus dem
    unveraenderlichen Snapshot abgeleitet, append-only persistiert und ist
    als juengste Bewertung abrufbar (TDD-Red-Welle 2)."""
    suffix = uuid4().hex[:8]
    feed_id = _create_feed(suffix)

    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"EvalPersist {suffix}", "animal_count": 8, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS, json={
        "group_id": group_id, "inputs": {"milk_kg_day": 30}})
    assert profile.status_code == 201, profile.text

    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"EvalRation {suffix}",
        "snapshot": {"components": [{"feed_id": feed_id, "kg_fm": 28.0,
                                      "min_kg_fm": 31.0, "max_kg_fm": 20.0}]}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]

    # Persistieren: keine Client-Komponenten - Server liest den Snapshot
    evaluated = client.post(f"{ROOT}/feeding/ration-versions/{version_id}/evaluate",
                            headers=HEADERS, json={})
    assert evaluated.status_code == 201, evaluated.text
    payload = evaluated.json()
    assert payload["ration_version_id"] == version_id
    assert payload["totals"]["dm_kg"] > 0
    assert payload["requirement_profile_id"]
    assert any(item["code"] == "bounds_conflict" and item["feed_id"] == feed_id
               for item in payload["findings"])

    latest = client.get(f"{ROOT}/feeding/ration-versions/{version_id}/evaluation",
                        headers=HEADERS)
    assert latest.status_code == 200, latest.text
    assert latest.json()["id"] == payload["id"]

    # Version ohne Komponenten-Snapshot -> 422 statt leerer Schein-Bewertung
    empty_ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"Leer {suffix}", "snapshot": {"components": []}})
    assert empty_ration.status_code == 201
    empty_eval = client.post(
        f"{ROOT}/feeding/ration-versions/{empty_ration.json()['latest_version_id']}/evaluate",
        headers=HEADERS, json={})
    assert empty_eval.status_code == 422

    # Unbekannte Version -> 404; fehlende Rolle -> 403 (isolierte App unten)
    missing = client.post(f"{ROOT}/feeding/ration-versions/{uuid4()}/evaluate",
                          headers=HEADERS, json={})
    assert missing.status_code == 404


def test_version_evaluation_endpoints_reject_user_without_role() -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as role_client:
        post = role_client.post("/feeding/ration-versions/v-1/evaluate", json={})
        get = role_client.get("/feeding/ration-versions/v-1/evaluation")
    assert post.status_code == 403
    assert get.status_code == 403


def test_compare_endpoint_journey_and_guards() -> None:
    """FEED-EDITOR-023 (TDD-Red-Welle 3): Vergleich zweier Versionen derselben
    Gruppe; ungleiche Gruppen -> 409; unbekannte Version -> 404; RBAC 403."""
    suffix = uuid4().hex[:8]
    feed_id = _create_feed(suffix)

    def make_group(name: str) -> str:
        response = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
            "name": name, "animal_count": 8, "feeding_system": "TMR",
            "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
        assert response.status_code == 201, response.text
        return response.json()["id"]

    group_id = make_group(f"Vergleich {suffix}")
    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS,
                          json={"group_id": group_id, "inputs": {"milk_kg_day": 30}})
    assert profile.status_code == 201, profile.text

    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"VglRation {suffix}",
        "snapshot": {"components": [{"feed_id": feed_id, "kg_fm": 30.0}]}})
    assert ration.status_code == 201, ration.text
    base_version = ration.json()["latest_version_id"]

    second = client.post(f"{ROOT}/lifecycle/rations/{ration.json()['id']}/versions",
                         headers=HEADERS, json={
                             "snapshot": {"components": [{"feed_id": feed_id, "kg_fm": 26.0}]},
                             "expected_latest_version_no": 1, "source": "editor"})
    assert second.status_code == 201, second.text
    variant_version = second.json()["id"]

    comparison = client.post(f"{ROOT}/feeding/ration-versions/compare", headers=HEADERS,
                             json={"base_version_id": base_version,
                                   "variant_version_id": variant_version})
    assert comparison.status_code == 200, comparison.text
    payload = comparison.json()
    row = payload["component_diff"][0]
    assert row["base_kg_fm"] == 30.0 and row["variant_kg_fm"] == 26.0
    assert payload["base"]["version_id"] == base_version
    assert payload["variant"]["version_id"] == variant_version
    metrics = {m["metric"] for m in payload["metric_diff"]}
    assert {"dm_kg", "cost_eur", "me_mj"} <= metrics

    # Ungleiche Gruppen -> 409
    other_group = make_group(f"Andere {suffix}")
    other_profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS,
                                json={"group_id": other_group, "inputs": {"milk_kg_day": 25}})
    assert other_profile.status_code == 201
    other_ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": other_group, "name": f"Fremd {suffix}",
        "snapshot": {"components": [{"feed_id": feed_id, "kg_fm": 10.0}]}})
    assert other_ration.status_code == 201
    mismatch = client.post(f"{ROOT}/feeding/ration-versions/compare", headers=HEADERS,
                           json={"base_version_id": base_version,
                                 "variant_version_id": other_ration.json()["latest_version_id"]})
    assert mismatch.status_code == 409

    missing = client.post(f"{ROOT}/feeding/ration-versions/compare", headers=HEADERS,
                          json={"base_version_id": base_version,
                                "variant_version_id": str(uuid4())})
    assert missing.status_code == 404

    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as role_client:
        forbidden = role_client.post("/feeding/ration-versions/compare", json={
            "base_version_id": "a", "variant_version_id": "b"})
    assert forbidden.status_code == 403
