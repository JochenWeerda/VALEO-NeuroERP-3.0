from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import benchmark_cockpit, data_quality, idempotency_monitoring, sustainability
from app.core.action_execution import ActionExecutionResult, ActionExecutionStatus, ActionResultSource
from app.core.action_idempotency import get_action_idempotency_store


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(idempotency_monitoring.router)
    app.include_router(data_quality.router)
    app.include_router(sustainability.router)
    app.include_router(benchmark_cockpit.router)
    return TestClient(app)


def setup_function() -> None:
    get_action_idempotency_store().clear()


def _seed_idempotency_record() -> None:
    store = get_action_idempotency_store()
    store.remember(
        tenant_id="tenant-a",
        idempotency_key="idem-001",
        request_fingerprint="fingerprint-001",
        result=ActionExecutionResult(
            execution_id="exec-001",
            command_id="cmd-001",
            status=ActionExecutionStatus.ACCEPTED,
            aggregate_type="agrar_settlement",
            aggregate_id="settlement-001",
            aggregate_owner="agrar",
            command_name="approve_settlement",
            idempotency_key="idem-001",
            requires_human_confirmation=True,
            result_source=ActionResultSource.FRESH,
        ),
    )


def test_idempotency_audit_feed_returns_structured_entries():
    client = _client()
    _seed_idempotency_record()

    response = client.get("/process/idempotency/audit", params={"tenant_id": "tenant-a"})

    assert response.status_code == 200
    body = response.json()
    assert body["entry_count"] == 1
    assert body["tenant_count"] == 1
    assert body["command_count"] == 1
    assert body["aggregate_count"] == 1
    assert body["entries"][0]["execution_id"] == "exec-001"
    assert body["entries"][0]["status"] == "accepted"
    assert body["entries"][0]["requires_human_confirmation"] is True


def test_idempotency_summary_surfaces_replay_and_status_counts():
    client = _client()
    _seed_idempotency_record()

    response = client.get("/process/idempotency/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 1
    assert body["status_counts"]["accepted"] == 1
    assert body["result_source_counts"]["fresh"] == 1
    assert body["replay_count"] == 0
    assert body["pending_approval_count"] == 0


def test_data_quality_catalog_and_ruleset_summary_are_consistent():
    client = _client()

    catalog = client.get("/data-quality/catalog")
    assert catalog.status_code == 200
    catalog_body = catalog.json()
    assert catalog_body["ruleset_count"] >= 10
    assert "Debitor" in catalog_body["entity_types"]
    assert catalog_body["rule_count"] >= catalog_body["ruleset_count"]

    ruleset = client.get("/data-quality/rulesets/Debitor/summary")
    assert ruleset.status_code == 200
    ruleset_body = ruleset.json()
    assert ruleset_body["entity_typ"] == "Debitor"
    assert ruleset_body["regel_count"] >= 3


def test_data_quality_ruleset_lookup_returns_404_for_unknown_entity():
    client = _client()

    response = client.get("/data-quality/rulesets/unknown-entity")

    assert response.status_code == 404


def test_sustainability_catalog_and_read_model_surface_structured_rollups():
    client = _client()

    catalog = client.get("/sustainability/catalog", params={"tenant_id": "TEN-1", "jahr": 2026})
    assert catalog.status_code == 200
    catalog_body = catalog.json()
    assert catalog_body["report_id"].startswith("ESG-TEN-1-2026")
    assert catalog_body["scope_count"] >= 2
    assert catalog_body["category_count"] >= 4
    assert catalog_body["top_scope"] in {"SCOPE_1", "SCOPE_2", "SCOPE_3"}

    read_model = client.get("/sustainability/read-model", params={"tenant_id": "TEN-1", "jahr": 2026})
    assert read_model.status_code == 200
    read_model_body = read_model.json()
    assert read_model_body["report"]["tenant_id"] == "TEN-1"
    assert read_model_body["catalog"]["top_category"]
    assert read_model_body["coverage_notes"]


def test_benchmark_catalog_and_read_model_surface_structured_rollups():
    client = _client()

    catalog = client.get("/benchmark/catalog", params={"tenant_id": "TEN-2"})
    assert catalog.status_code == 200
    catalog_body = catalog.json()
    assert catalog_body["kennzahl_count"] == 6
    assert catalog_body["category_count"] >= 4
    assert catalog_body["best_metric"]
    assert catalog_body["weakest_metric"]

    read_model = client.get("/benchmark/read-model", params={"tenant_id": "TEN-2"})
    assert read_model.status_code == 200
    read_model_body = read_model.json()
    assert read_model_body["report"]["tenant_id"] == "TEN-2"
    assert read_model_body["catalog"]["trend_series_count"] == 2
    assert read_model_body["coverage_notes"]
