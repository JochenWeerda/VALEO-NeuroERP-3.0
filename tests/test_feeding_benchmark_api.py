"""FEED-PERF-044 (TDD-Red-Welle 1): Zeitraumvergleich, tenant-interner
Gruppen-Benchmark und Benchmark-Bericht. Vor der Implementierung geschrieben.

Bewusst NICHT enthalten: anonymisierter betriebsuebergreifender Vergleich —
wartet auf die Auftraggeber-/Datenschutzentscheidung (Opt-in-Modell).
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
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


@pytest.mark.parametrize("path", [
    "/feeding/performance/period-comparison?group_id=g-1",
    "/feeding/performance/group-benchmark?group_id=g-1",
])
def test_benchmark_endpoints_reject_user_without_role(path: str) -> None:
    from app.api.v1.endpoints import feeding_performance
    app = FastAPI()
    app.include_router(feeding_performance.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = role_client.get(path)
    assert response.status_code == 403, (path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

def _group(suffix: str, milk_base: float, days: int = 8,
           offset_days: int = 0) -> str:
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Bench {suffix}", "animal_count": 60, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    for day_index in range(days):
        observation_date = date.today() - timedelta(days=offset_days + day_index)
        response = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json={
            "group_id": group_id, "observation_date": str(observation_date),
            "source": "manual", "source_ref": f"bench-{suffix}-{observation_date}",
            "cow_count": 60, "actual_milk_kg_cow": milk_base + day_index * 0.1,
            "actual_dmi_kg_cow": 22.0, "actual_fat_pct": 4.0,
            "actual_protein_pct": 3.4})
        assert response.status_code == 201, response.text
    return group_id


def test_period_comparison_with_honest_uncertainty() -> None:
    suffix = uuid4().hex[:8]
    # aktueller Zeitraum (Tage 0..7) + Vorzeitraum (Tage 10..17) mit weniger Milch
    group_id = _group(suffix, 32.0, days=8, offset_days=0)
    for day_index in range(8):
        observation_date = date.today() - timedelta(days=10 + day_index)
        response = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json={
            "group_id": group_id, "observation_date": str(observation_date),
            "source": "manual", "source_ref": f"bench-prev-{suffix}-{observation_date}",
            "cow_count": 60, "actual_milk_kg_cow": 29.0,
            "actual_dmi_kg_cow": 21.5, "actual_fat_pct": 4.0,
            "actual_protein_pct": 3.4})
        assert response.status_code == 201, response.text

    comparison = client.get(
        f"{ROOT}/feeding/performance/period-comparison?group_id={group_id}&period_days=9",
        headers=HEADERS)
    assert comparison.status_code == 200, comparison.text
    payload = comparison.json()
    assert payload["group_id"] == group_id
    assert payload["current"]["n"] >= 7
    assert payload["previous"]["n"] >= 7
    assert payload["confidence"] == "sufficient"
    assert payload["current"]["metrics"]["actual_milk_kg_cow"] > \
        payload["previous"]["metrics"]["actual_milk_kg_cow"]
    delta = payload["delta"]["actual_milk_kg_cow"]
    assert delta is not None and delta > 2.0

    # Kleine Stichprobe wird ehrlich benannt statt als Trend verkauft
    sparse = _group(f"sparse-{suffix}", 30.0, days=2)
    sparse_payload = client.get(
        f"{ROOT}/feeding/performance/period-comparison?group_id={sparse}&period_days=9",
        headers=HEADERS).json()
    assert sparse_payload["confidence"] == "insufficient_data"

    missing = client.get(
        f"{ROOT}/feeding/performance/period-comparison?group_id={uuid4()}",
        headers=HEADERS)
    assert missing.status_code == 404


def test_group_benchmark_is_tenant_internal_with_peer_context() -> None:
    suffix = uuid4().hex[:8]
    strong = _group(f"strong-{suffix}", 34.0)
    _group(f"peer1-{suffix}", 28.0)
    _group(f"peer2-{suffix}", 30.0)

    benchmark = client.get(
        f"{ROOT}/feeding/performance/group-benchmark?group_id={strong}&window_days=14",
        headers=HEADERS)
    assert benchmark.status_code == 200, benchmark.text
    payload = benchmark.json()
    assert payload["group_id"] == strong
    assert payload["peer_group_count"] >= 2, "Vergleich gegen uebrige Tenant-Gruppen"
    milk = payload["metrics"]["actual_milk_kg_cow"]
    assert milk["group_avg"] is not None and milk["peer_median"] is not None
    assert milk["group_avg"] > milk["peer_median"], "starke Gruppe liegt ueber dem Peer-Median"
    assert "scope" in payload and payload["scope"] == "tenant_internal", \
        "kein betriebsuebergreifender Vergleich ohne Opt-in-Entscheidung"


def test_benchmark_report_uses_report_entity_with_csv() -> None:
    suffix = uuid4().hex[:8]
    group_id = _group(f"rep-{suffix}", 33.0)
    _group(f"repperf-{suffix}", 29.0)

    created = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
        "report_type": "benchmark", "profile": "farmer", "source_ref": group_id})
    assert created.status_code == 201, created.text
    report = created.json()
    assert report["content"]["group_id"] == group_id
    assert report["content"]["benchmark"]["scope"] == "tenant_internal"
    assert "period_comparison" in report["content"]

    again = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
        "report_type": "benchmark", "profile": "farmer", "source_ref": group_id})
    assert again.status_code == 201
    assert again.json()["id"] == report["id"], "gleicher Datenstand => derselbe Bericht"

    csv = client.get(f"{ROOT}/feeding/reports/{report['id']}/csv", headers=HEADERS)
    assert csv.status_code == 200, csv.text
    assert csv.text.splitlines()[0].startswith("metric;")

    feeder = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
        "report_type": "benchmark", "profile": "feeder", "source_ref": group_id})
    assert feeder.status_code == 422
