"""FEED-OPT-042 (TDD-Red-Welle 2): Optimieren im Editor erzeugt eine
Candidate-Version (nie Aktivierung) mit atomarem OptimizationRun-Hook.
Vor der Implementierung geschrieben.
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
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


def test_optimize_rejects_user_without_write_role() -> None:
    from app.api.v1.endpoints import feeding_ration_editor
    app = FastAPI()
    app.include_router(feeding_ration_editor.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = role_client.post("/feeding/ration-versions/v-1/optimize",
                                    json={"expected_latest_version_no": 1})
    assert response.status_code == 403, response.text


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

REFERENCE_VALUES: list[dict[str, Any]] = [
    {"nutrient_code": "dry_matter", "value": "35", "unit_code": "percent"},
    {"nutrient_code": "metabolizable_energy", "value": "8.8", "unit_code": "MJ_per_kg"},
    {"nutrient_code": "crude_protein", "value": "150", "unit_code": "g_per_kg"},
    {"nutrient_code": "sidp", "value": "95", "unit_code": "g_per_kg"},
    {"nutrient_code": "ndf", "value": "400", "unit_code": "g_per_kg"},
    {"nutrient_code": "starch", "value": "30", "unit_code": "g_per_kg"},
    {"nutrient_code": "sugar", "value": "40", "unit_code": "g_per_kg"},
    {"nutrient_code": "crude_fat", "value": "30", "unit_code": "g_per_kg"},
    {"nutrient_code": "calcium", "value": "6.0", "unit_code": "g_per_kg"},
    {"nutrient_code": "phosphorus", "value": "3.5", "unit_code": "g_per_kg"},
    {"nutrient_code": "sodium", "value": "2.0", "unit_code": "g_per_kg"},
    {"nutrient_code": "magnesium", "value": "2.5", "unit_code": "g_per_kg"},
    {"nutrient_code": "potassium", "value": "20", "unit_code": "g_per_kg"},
]


def _feed(suffix: str) -> str:
    feed = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"OPT-{suffix}", "name": f"Optimiergras {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved",
        "preis_pro_t": 60.0})
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    for item in REFERENCE_VALUES:
        response = client.post(f"{ROOT}/feed-catalog/feeds/{feed_id}/reference-values",
                               headers=HEADERS, json={
                                   **item, "basis": "dry_matter",
                                   "source_type": "analysis",
                                   "source_ref": f"OPT golden {suffix}"})
        assert response.status_code == 201, response.text
    return feed_id


def _ration_with_profile(suffix: str, *, min_kg_fm: float | None = None) -> dict[str, Any]:
    feed_id = _feed(suffix)
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Opt {suffix}", "animal_count": 20, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS,
                          json={"group_id": group_id,
                                "inputs": {"body_weight_kg": 650, "milk_kg_day": 15}})
    assert profile.status_code == 201, profile.text
    component: dict[str, Any] = {"feed_id": feed_id, "name": f"Optimiergras {suffix}",
                                 "kg_fm": 50.0}
    if min_kg_fm is not None:
        component["min_kg_fm"] = min_kg_fm
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"OptRation {suffix}",
        "snapshot": {"components": [component]}})
    assert ration.status_code == 201, ration.text
    return {"ration_id": ration.json()["id"],
            "version_id": ration.json()["latest_version_id"],
            "feed_id": feed_id, "group_id": group_id}


def test_optimize_creates_candidate_version_with_atomic_run() -> None:
    setup = _ration_with_profile(uuid4().hex[:8])

    optimized = client.post(
        f"{ROOT}/feeding/ration-versions/{setup['version_id']}/optimize",
        headers=HEADERS, json={"expected_latest_version_no": 1})
    assert optimized.status_code == 200, optimized.text
    payload = optimized.json()
    assert payload["status"] == "optimal", payload
    candidate = payload["candidate_version"]
    assert candidate["version_no"] == 2
    assert candidate["source"] == "optimizer"
    run = payload["optimization_run"]
    assert run["status"] == "optimal"
    assert run["ration_version_id"] == candidate["id"], \
        "Run gehoert atomar zur erzeugten Candidate-Version"

    # Nie Aktivierung: Candidate bleibt draft; Kandidat traegt Komponenten
    detail = client.get(f"{ROOT}/lifecycle/rations/{setup['ration_id']}", headers=HEADERS)
    assert detail.status_code == 200, detail.text
    assert detail.json()["latest_version_no"] == 2
    assert detail.json()["latest_status"] == "draft"
    latest = next(v for v in detail.json()["versions"] if v["version_no"] == 2)
    components = latest["snapshot"]["components"]
    assert components and components[0]["feed_id"] == setup["feed_id"]
    assert float(components[0]["kg_fm"]) > 0

    # Kein Ergebnis ohne persistierten Run (FEED-OPT-005)
    runs = client.get(f"{ROOT}/feeding/optimization-runs?ration_id={setup['ration_id']}",
                      headers=HEADERS)
    assert runs.status_code == 200
    assert any(item["id"] == run["id"] for item in runs.json())

    # Optimistische Revision: veraltete Erwartung -> 409, keine weitere Version
    conflict = client.post(
        f"{ROOT}/feeding/ration-versions/{setup['version_id']}/optimize",
        headers=HEADERS, json={"expected_latest_version_no": 1})
    assert conflict.status_code == 409, conflict.text


def test_infeasible_optimization_documents_run_and_explains() -> None:
    # Mindestmenge 200 kg FM (= 70 kg TM) sprengt jedes TM-Band -> unloesbar
    setup = _ration_with_profile(uuid4().hex[:8], min_kg_fm=200.0)

    optimized = client.post(
        f"{ROOT}/feeding/ration-versions/{setup['version_id']}/optimize",
        headers=HEADERS, json={"expected_latest_version_no": 1})
    assert optimized.status_code == 200, optimized.text
    payload = optimized.json()
    assert payload["status"] == "infeasible", payload
    assert payload["candidate_version"] is None
    assert payload["explanation"], "Erklaerschicht benennt die Konfliktgrenzen"
    run = payload["optimization_run"]
    assert run["status"] == "infeasible"
    assert run["ration_version_id"] == setup["version_id"], \
        "ohne Kandidat dokumentiert der Run die Quellversion"

    # keine neue Version entstanden
    detail = client.get(f"{ROOT}/lifecycle/rations/{setup['ration_id']}", headers=HEADERS)
    assert detail.json()["latest_version_no"] == 1


def test_optimize_without_requirement_profile_fails_actionable() -> None:
    suffix = uuid4().hex[:8]
    feed_id = _feed(suffix)
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"OhneProfil {suffix}", "animal_count": 10, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"OhneProfil {suffix}",
        "snapshot": {"components": [{"feed_id": feed_id, "kg_fm": 30.0}]}})
    assert ration.status_code == 201, ration.text

    response = client.post(
        f"{ROOT}/feeding/ration-versions/{ration.json()['latest_version_id']}/optimize",
        headers=HEADERS, json={"expected_latest_version_no": 1})
    assert response.status_code == 404, response.text
    assert "Bedarf" in response.json().get("detail", ""), \
        "handlungsorientierte Meldung: zuerst Bedarf berechnen"
