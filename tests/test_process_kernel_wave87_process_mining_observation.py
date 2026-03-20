from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_mining_observation
from app.core.process_mining import (
    ProcessMiningBottleneck,
    ProcessMiningReport,
    ProcessMiningTrace,
)
from app.core.process_mining_observation import build_process_mining_observation_read_model
from app.core.runtime_operations import ComponentHealth, RuntimeComponent, RuntimeHealthReport


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(process_mining_observation.router)
    app.dependency_overrides[process_mining_observation.get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[process_mining_observation.get_db] = lambda: object()
    return TestClient(app)


def _report() -> ProcessMiningReport:
    return ProcessMiningReport(
        tenant_id="tenant-a",
        traces=[
            ProcessMiningTrace(
                projection_key="ap-invoice-cockpit",
                item_count=7,
                cached=True,
                cursor_status="ready",
                cursor_source="outbox",
                last_event_processed="42",
                state="ready",
            ),
            ProcessMiningTrace(
                projection_key="payment-run-cockpit",
                item_count=3,
                cached=True,
                cursor_status="pending-replay",
                cursor_source="outbox",
                state="lagging",
            ),
            ProcessMiningTrace(
                projection_key="cash-closings/reporting",
                item_count=1,
                cached=True,
                state="cache-only",
            ),
        ],
        bottlenecks=[
            ProcessMiningBottleneck(
                bottleneck_id="projection:payment-run-cockpit",
                source_type="projection",
                source_key="payment-run-cockpit",
                severity="high",
                detail="Cursor status pending-replay blocks clean replay progress",
            )
        ],
        ready_count=1,
        lagging_count=1,
        cache_only_count=1,
        unknown_count=0,
        warning_signal_count=0,
        critical_signal_count=0,
    )


def test_build_process_mining_observation_ranks_lagging_process_first():
    observation = build_process_mining_observation_read_model(_report(), top_n=2)

    assert observation.top_n == 2
    assert observation.top_processes[0].projection_key == "payment-run-cockpit"
    assert observation.top_processes[0].risk_score > observation.top_processes[1].risk_score
    assert observation.top_processes[0].recommended_action.startswith("Replay- oder Cursor-Rueckstand")


def test_process_mining_observation_endpoint_returns_top_processes(monkeypatch):
    client = _client()

    def _projection_loader(_tenant_id, _db=None):
        from app.core.finance_projection_status import ProjectionStatusEntry, ProjectionStatusReadModel

        return ProjectionStatusReadModel(
            tenant_id="tenant-a",
            projection_count=3,
            persisted_snapshot_count=3,
            persisted_cursor_count=2,
            cache_hits=4,
            cache_misses=1,
            projections=[
                ProjectionStatusEntry(
                    projection_key="ap-invoice-cockpit",
                    item_count=7,
                    cached=True,
                    cursor_status="ready",
                    cursor_source="outbox",
                    last_processed_event_id="42",
                ),
                ProjectionStatusEntry(
                    projection_key="payment-run-cockpit",
                    item_count=3,
                    cached=True,
                    cursor_status="pending-replay",
                    cursor_source="outbox",
                ),
                ProjectionStatusEntry(
                    projection_key="cash-closings/reporting",
                    item_count=1,
                    cached=True,
                ),
            ],
            schema_version=1,
        )

    def _runtime_loader(_tenant_id, _db=None):
        return RuntimeHealthReport(
            tenant_id="tenant-a",
            overall_health=ComponentHealth.HEALTHY,
            components=[
                RuntimeComponent(
                    component_id="projection-consumer-1",
                    component_type="projection_consumer",
                    health=ComponentHealth.DEGRADED,
                )
            ],
            schema_version=1,
        )

    monkeypatch.setattr(process_mining_observation, "get_projection_status_loader", lambda: _projection_loader)
    monkeypatch.setattr(process_mining_observation, "get_runtime_report_loader", lambda: _runtime_loader)
    monkeypatch.setattr(process_mining_observation, "get_telemetry_device_store", lambda: {"tenant-a": {}})
    monkeypatch.setattr(process_mining_observation, "get_telemetry_reading_store", lambda: {"tenant-a": {}})

    response = client.get("/process-mining/finance/observation", params={"top_n": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-a"
    assert body["top_n"] == 2
    assert body["top_processes"][0]["projection_key"] == "payment-run-cockpit"
    assert body["top_processes"][0]["bottleneck_count"] == 1


def test_process_mining_observation_drilldown_returns_selected_process(monkeypatch):
    client = _client()

    def _projection_loader(_tenant_id, _db=None):
        from app.core.finance_projection_status import ProjectionStatusEntry, ProjectionStatusReadModel

        return ProjectionStatusReadModel(
            tenant_id="tenant-a",
            projection_count=1,
            persisted_snapshot_count=1,
            persisted_cursor_count=1,
            cache_hits=1,
            cache_misses=0,
            projections=[
                ProjectionStatusEntry(
                    projection_key="payment-run-cockpit",
                    item_count=3,
                    cached=True,
                    cursor_status="pending-replay",
                    cursor_source="outbox",
                )
            ],
            schema_version=1,
        )

    monkeypatch.setattr(process_mining_observation, "get_projection_status_loader", lambda: _projection_loader)
    monkeypatch.setattr(
        process_mining_observation,
        "get_runtime_report_loader",
        lambda: (
            lambda _tenant_id, _db=None: RuntimeHealthReport(
                tenant_id="tenant-a",
                overall_health=ComponentHealth.HEALTHY,
                components=[],
                schema_version=1,
            )
        ),
    )
    monkeypatch.setattr(process_mining_observation, "get_telemetry_device_store", lambda: {"tenant-a": {}})
    monkeypatch.setattr(process_mining_observation, "get_telemetry_reading_store", lambda: {"tenant-a": {}})

    response = client.get("/process-mining/finance/observation/payment-run-cockpit")

    assert response.status_code == 200
    body = response.json()
    assert body["selected_projection_key"] == "payment-run-cockpit"
    assert body["selected_process"]["projection_key"] == "payment-run-cockpit"
    assert body["selected_process"]["risk_score"] >= body["selected_process"]["item_count"]
