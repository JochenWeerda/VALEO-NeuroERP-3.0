"""FEED-REP-039: Report-Entitaet mit reproduzierbaren, profilierten Ausgaben
(TDD-Red-Welle 1). Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from datetime import date
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
    from app.api.v1.endpoints import feeding_reports
    app = FastAPI()
    app.include_router(feeding_reports.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


@pytest.mark.parametrize(("method", "path", "body"), [
    ("post", "/feeding/reports", {"report_type": "feeding_plan", "profile": "feeder",
                                  "source_ref": "pv-1"}),
    ("get", "/feeding/reports?source_ref=pv-1", None),
    ("get", "/feeding/reports/r-1", None),
    ("get", "/feeding/reports/r-1/csv", None),
])
def test_report_endpoints_reject_user_without_domain_role(method: str, path: str, body: dict | None) -> None:
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


def _published_plan(suffix: str) -> str:
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Report {suffix}", "animal_count": 40, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"ReportRation {suffix}",
        "snapshot": {"components": [
            {"feed_id": f"gras-{suffix}", "name": "Grassilage", "kg_fm": 24.0},
            {"feed_id": f"mais-{suffix}", "name": "Maissilage", "kg_fm": 16.0},
        ]}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]
    for target, expected in (("in_review", "draft"), ("approved", "in_review")):
        transition = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                                 headers=HEADERS,
                                 json={"target_status": target, "expected_status": expected})
        assert transition.status_code == 200, transition.text
    plan = client.post(f"{ROOT}/feeding/plans/publish", headers=HEADERS, json={
        "source_ration_version_id": version_id, "animal_count": 38,
        "dosing_step_kg": 5, "rounding_mode": "nearest",
        "valid_from": str(date.today()), "reason": "Berichtstestplan veroeffentlichen",
        "idempotency_key": f"rep-{suffix}"})
    assert plan.status_code == 201, plan.text
    return plan.json()["id"]


def test_report_is_reproducible_profiled_and_append_only() -> None:
    suffix = uuid4().hex[:8]
    plan_version_id = _published_plan(suffix)

    def create(profile: str) -> dict[str, Any]:
        response = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
            "report_type": "feeding_plan", "profile": profile,
            "source_ref": plan_version_id})
        assert response.status_code == 201, response.text
        return response.json()

    feeder_a = create("feeder")
    feeder_b = create("feeder")
    assert feeder_a["content_hash"] == feeder_b["content_hash"], \
        "gleiche Quellversion+Profil => identischer Inhalt"
    assert feeder_b["id"] == feeder_a["id"], "idempotente Wiedererzeugung statt Dublette"

    advisor = create("advisor")
    assert advisor["content_hash"] != feeder_a["content_hash"], \
        "Profile unterscheiden sich inhaltlich"

    # Profilierung: feeder ohne Preise/Quellen, advisor mit Quellhinweis
    assert "loads" in feeder_a["content"]
    assert feeder_a["content"]["loads"][0]["feed_name"] == "Grassilage"
    assert "source" not in feeder_a["content"], "feeder-Profil traegt keine Quellendetails"
    assert advisor["content"]["source"]["plan_version_id"] == plan_version_id

    listed = client.get(f"{ROOT}/feeding/reports?source_ref={plan_version_id}", headers=HEADERS)
    assert listed.status_code == 200
    assert {item["profile"] for item in listed.json()} == {"feeder", "advisor"}

    # CSV-Export strukturierter Daten
    csv = client.get(f"{ROOT}/feeding/reports/{feeder_a['id']}/csv", headers=HEADERS)
    assert csv.status_code == 200, csv.text
    assert csv.headers["content-type"].startswith("text/csv")
    assert "Grassilage" in csv.text
    assert csv.text.splitlines()[0].startswith("sequence;feed_name"), "CSV mit Kopfzeile"

    # Unbekannte Quelle -> 404; Tenant-Isolation
    missing = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
        "report_type": "feeding_plan", "profile": "feeder", "source_ref": str(uuid4())})
    assert missing.status_code == 404
    foreign = client.get(f"{ROOT}/feeding/reports/{feeder_a['id']}",
                         headers={**HEADERS, "X-Tenant-Id": str(uuid4())})
    assert foreign.status_code == 404
