"""FEED-PERF-033: MLP-/Milchguete-Kennzahlen und Vorher/Nachher-Auswertung
(TDD-Red-Welle 1). Vor der Implementierung geschrieben.
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


def test_fat_protein_quotient_is_none_safe_and_deterministic() -> None:
    from app.agrar.rations.controlling import fat_protein_quotient

    assert fat_protein_quotient(4.2, 3.5) == pytest.approx(1.2)
    assert fat_protein_quotient(None, 3.5) is None
    assert fat_protein_quotient(4.2, None) is None
    assert fat_protein_quotient(4.2, 0) is None, "Division durch 0 -> unbekannt, nie 0-fabriziert"


_CONTEXT: dict[str, Any] = {"roles": []}


def _build_role_app() -> FastAPI:
    from app.api.v1.endpoints import feeding_performance
    app = FastAPI()
    app.include_router(feeding_performance.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


def test_version_impact_rejects_user_without_domain_role() -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as client:
        response = client.get("/feeding/performance/version-impact?group_id=g-1")
    assert response.status_code == 403


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _record(group_id: str, day: date, **values: Any) -> None:
    body = {"group_id": group_id, "observation_date": str(day), "source": "manual",
            "source_ref": f"mlp-{day}", **values}
    response = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json=body)
    assert response.status_code == 201, response.text


def test_mlp_metrics_are_recorded_with_provenance_and_fpq_derived() -> None:
    suffix = uuid4().hex[:8]
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"MLP {suffix}", "animal_count": 30, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    _record(group_id, date.today(), actual_milk_kg_cow=31.0, actual_fat_pct=4.2,
            actual_protein_pct=3.5, milk_urea_mg_dl=24.0, somatic_cell_count_k=180.0)

    series = client.get(f"{ROOT}/controlling/series?group_id={group_id}", headers=HEADERS)
    assert series.status_code == 200, series.text
    point = series.json()[0]
    assert point["milk_urea_mg_dl"] == pytest.approx(24.0)
    assert point["somatic_cell_count_k"] == pytest.approx(180.0)
    assert point["fat_protein_quotient"] == pytest.approx(1.2)
    assert point["source"] == "manual", "Provenienz je Beobachtung bleibt sichtbar"

    # Ohne Eiweiss bleibt FEQ unbekannt (nie 0)
    _record(group_id, date.today() - timedelta(days=1), actual_milk_kg_cow=30.0,
            actual_fat_pct=4.0)
    series = client.get(f"{ROOT}/controlling/series?group_id={group_id}", headers=HEADERS)
    older = [p for p in series.json()
             if p["observation_date"] == str(date.today() - timedelta(days=1))][0]
    assert older["fat_protein_quotient"] is None


def test_version_impact_reports_honest_uncertainty() -> None:
    suffix = uuid4().hex[:8]
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Impact {suffix}", "animal_count": 30, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group_id, "name": f"ImpactRation {suffix}",
        "snapshot": {"components": [{"feed_id": f"f-{suffix}", "kg_fm": 20.0}]}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]

    # 3 Tage Vorher-Daten
    for offset in (3, 2, 1):
        _record(group_id, date.today() - timedelta(days=offset),
                actual_milk_kg_cow=28.0, actual_dmi_kg_cow=21.0)

    for target, expected in (("in_review", "draft"), ("approved", "in_review"),
                             ("active", "approved")):
        transition = client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                                 headers=HEADERS,
                                 json={"target_status": target, "expected_status": expected})
        assert transition.status_code == 200, transition.text

    # 2 Tage Nachher-Daten (heute zaehlt zur Nachher-Seite)
    _record(group_id, date.today(), actual_milk_kg_cow=30.5, actual_dmi_kg_cow=21.8)

    impact = client.get(f"{ROOT}/feeding/performance/version-impact?group_id={group_id}",
                        headers=HEADERS)
    assert impact.status_code == 200, impact.text
    payload = impact.json()
    assert payload, "mindestens die aktivierte Version wird ausgewertet"
    entry = payload[0]
    assert entry["ration_version_id"] == version_id
    assert entry["before"]["n"] == 3
    assert entry["after"]["n"] >= 1
    assert entry["before"]["metrics"]["actual_milk_kg_cow"] == pytest.approx(28.0)
    assert entry["after"]["metrics"]["actual_milk_kg_cow"] >= 30.0
    # Ehrliche Unsicherheit: kleine Stichprobe wird benannt, keine Scheinsignifikanz
    assert entry["confidence"] == "insufficient_data"
    assert "window_days" in entry

    # Gruppe ohne Aktivierung -> leere Liste, kein Fehler
    empty_group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Leer {suffix}", "animal_count": 5, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert empty_group.status_code == 201
    none_yet = client.get(
        f"{ROOT}/feeding/performance/version-impact?group_id={empty_group.json()['id']}",
        headers=HEADERS)
    assert none_yet.status_code == 200
    assert none_yet.json() == []
