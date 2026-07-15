"""FEED-CORE-020 / FEED-T053-artig + API-Happy-Path: /feeding-Requirements-Endpoints.

TDD-Red-Welle 1 (API): vor der Implementierung geschrieben; scheiterte zunaechst
mit ImportError auf app.api.v1.endpoints.feeding_requirements.
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

# ── Rollenregression (ohne DB) ──────────────────────────────────────────────

_CONTEXT: dict[str, Any] = {"roles": []}


def _build_role_app() -> FastAPI:
    from app.api.v1.endpoints import feeding_requirements
    app = FastAPI()
    app.include_router(feeding_requirements.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


@pytest.fixture(scope="module")
def role_client() -> TestClient:
    with TestClient(_build_role_app()) as value:
        yield value


REQUESTS = [
    ("get", "/feeding/evaluation-systems", None),
    ("post", "/feeding/requirement-profiles", {"group_id": "g-1", "inputs": {"milk_kg_day": 30}}),
    ("get", "/feeding/requirement-profiles?group_id=g-1", None),
    ("post", "/feeding/optimization-runs", {
        "ration_version_id": "v-1", "solver_version": "s", "objective": "min_cost",
        "status": "optimal", "parameters": {}}),
    ("get", "/feeding/optimization-runs?ration_id=r-1", None),
]


@pytest.mark.parametrize(("method", "path", "body"), REQUESTS)
def test_requirements_endpoints_reject_user_without_domain_role(
    role_client: TestClient, method: str, path: str, body: dict | None,
) -> None:
    _CONTEXT["roles"] = []
    response = getattr(role_client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Happy Path (Dev-DB) ─────────────────────────────────────────────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization/feeding"
LIFECYCLE = "/api/v1/agrar/rations-optimization/lifecycle"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def test_requirements_journey_systems_profile_and_run() -> None:
    suffix = uuid4().hex[:8]

    systems = client.get(f"{ROOT}/evaluation-systems", headers=HEADERS)
    assert systems.status_code == 200, systems.text
    slugs = {s["id"] for s in systems.json()}
    assert {"gfe2023", "dlg2025"} <= slugs

    group = client.post(f"{LIFECYCLE}/groups", headers=HEADERS,
                        json={"name": f"API-Req {suffix}", "animal_count": 12, "feeding_system": "TMR"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    profile = client.post(f"{ROOT}/requirement-profiles", headers=HEADERS, json={
        "group_id": group_id,
        "inputs": {"breed": "Holstein", "feeding_type": "TMR",
                   "body_weight_kg": 660, "milk_kg_day": 31, "milk_fat_pct": 4.0,
                   "milk_protein_pct": 3.35, "lactation_stage_days": 90, "parity": 3},
    })
    assert profile.status_code == 201, profile.text
    payload = profile.json()
    assert payload["requirements"]["me_mj"] > 0
    assert payload["system_version_id"]
    assert payload["estimated_inputs"] == []

    listed = client.get(f"{ROOT}/requirement-profiles?group_id={group_id}", headers=HEADERS)
    assert listed.status_code == 200
    assert any(p["id"] == payload["id"] for p in listed.json())

    ration = client.post(f"{LIFECYCLE}/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"Ration {suffix}", "snapshot": {"components": []}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]

    run = client.post(f"{ROOT}/optimization-runs", headers=HEADERS, json={
        "ration_version_id": version_id, "solver_version": "lp_stage2-2026.07",
        "objective": "min_cost", "status": "optimal", "duration_ms": 640,
        "parameters": {"fan_mode": "005"}})
    assert run.status_code == 201, run.text
    assert run.json()["parameters"] == {"fan_mode": "005"}

    runs = client.get(f"{ROOT}/optimization-runs?ration_id={ration.json()['id']}", headers=HEADERS)
    assert runs.status_code == 200
    assert any(r["id"] == run.json()["id"] for r in runs.json())

    orphan = client.post(f"{ROOT}/optimization-runs", headers=HEADERS, json={
        "ration_version_id": str(uuid4()), "solver_version": "x",
        "objective": "min_cost", "status": "optimal", "parameters": {}})
    assert orphan.status_code == 404

    # Tenant-Isolation
    foreign = client.get(f"{ROOT}/requirement-profiles?group_id={group_id}",
                         headers={**HEADERS, "X-Tenant-Id": str(uuid4())})
    assert foreign.status_code == 200
    assert foreign.json() == []
