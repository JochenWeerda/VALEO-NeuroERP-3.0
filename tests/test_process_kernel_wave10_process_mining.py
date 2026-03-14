from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import benchmark_api, process_mining_api, reporting_api
from app.core.database import get_db
import app.core.endpoint_gateways as _gw
from app.core.endpoint_gateways import (
    register_projection_status_loader,
    register_runtime_report_loader,
    register_telemetry_stores,
)
from app.core.finance_projection_status import ProjectionStatusEntry, ProjectionStatusReadModel
from app.core.iot_telemetry import DeviceManifest, DeviceStatus, DeviceType, TelemetryReading
from app.core.process_mining import build_process_mining_report
from app.core.runtime_operations import ComponentHealth, RuntimeComponent, RuntimeHealthReport


def make_projection_status(*entries: ProjectionStatusEntry) -> ProjectionStatusReadModel:
    return ProjectionStatusReadModel(
        tenant_id="tenant-a",
        projection_count=len(entries),
        persisted_snapshot_count=3,
        persisted_cursor_count=2,
        cache_hits=4,
        cache_misses=1,
        projections=list(entries),
        schema_version=1,
    )


def make_runtime_report(*components: RuntimeComponent) -> RuntimeHealthReport:
    return RuntimeHealthReport(
        tenant_id="tenant-a",
        overall_health=ComponentHealth.HEALTHY,
        components=list(components),
        schema_version=1,
    )


def test_build_process_mining_report_marks_ready_projection():
    report = build_process_mining_report(
        projection_status=make_projection_status(
            ProjectionStatusEntry(
                projection_key="ap-invoice-cockpit",
                item_count=7,
                cached=True,
                cursor_status="ready",
                cursor_source="outbox",
                last_processed_event_id="42",
            )
        ),
        runtime_report=make_runtime_report(),
    )

    assert report.ready_count == 1
    assert report.traces[0].state == "ready"
    assert report.traces[0].last_event_processed == "42"


def test_build_process_mining_report_marks_cache_only_projection():
    report = build_process_mining_report(
        projection_status=make_projection_status(
            ProjectionStatusEntry(
                projection_key="cash-closings/reporting",
                item_count=2,
                cached=True,
            )
        ),
        runtime_report=make_runtime_report(),
    )

    assert report.cache_only_count == 1
    assert report.traces[0].state == "cache-only"


def test_build_process_mining_report_flags_pending_replay_as_bottleneck():
    report = build_process_mining_report(
        projection_status=make_projection_status(
            ProjectionStatusEntry(
                projection_key="payment-run-cockpit",
                item_count=1,
                cached=True,
                cursor_status="pending-replay",
                cursor_source="outbox",
            )
        ),
        runtime_report=make_runtime_report(),
    )

    assert report.lagging_count == 1
    assert report.traces[0].state == "lagging"
    assert report.bottlenecks[0].source_key == "payment-run-cockpit"


def test_build_process_mining_report_includes_runtime_component_bottleneck():
    report = build_process_mining_report(
        projection_status=make_projection_status(),
        runtime_report=make_runtime_report(
            RuntimeComponent(
                component_id="finance-projections-01",
                component_type="projection_consumer",
                health=ComponentHealth.DEGRADED,
            )
        ),
    )

    assert len(report.bottlenecks) == 1
    assert report.bottlenecks[0].source_type == "runtime_component"
    assert report.bottlenecks[0].severity == "medium"


def test_build_process_mining_report_counts_unknown_projection():
    report = build_process_mining_report(
        projection_status=make_projection_status(
            ProjectionStatusEntry(
                projection_key="process-observation",
                item_count=0,
                cached=False,
            )
        ),
        runtime_report=make_runtime_report(),
    )

    assert report.unknown_count == 1
    assert report.traces[0].state == "unknown"


def test_build_process_mining_report_includes_offline_device_signal():
    report = build_process_mining_report(
        projection_status=make_projection_status(),
        runtime_report=make_runtime_report(),
        device_manifests=[
            DeviceManifest(
                device_id="device-1",
                device_type=DeviceType.silo_sensor,
                tenant_id="tenant-a",
                location="Silo Nord",
                status=DeviceStatus.offline,
                process_context="silo_management",
            )
        ],
    )

    assert report.warning_signal_count == 1
    assert report.observability_signals[0].source_key == "device-1"
    assert report.bottlenecks[0].source_type == "observability"


def test_build_process_mining_report_escalates_bad_reading_to_critical():
    report = build_process_mining_report(
        projection_status=make_projection_status(),
        runtime_report=make_runtime_report(),
        device_manifests=[
            DeviceManifest(
                device_id="device-2",
                device_type=DeviceType.moisture_sensor,
                tenant_id="tenant-a",
                location="Lager A",
                status=DeviceStatus.online,
            )
        ],
        latest_readings=[
            TelemetryReading(
                device_id="device-2",
                device_type=DeviceType.moisture_sensor,
                tenant_id="tenant-a",
                timestamp="2026-03-12T08:00:00Z",
                value=17.5,
                unit="%",
                quality="bad",
            )
        ],
    )

    assert report.critical_signal_count == 1
    assert report.observability_signals[0].severity == "critical"


def test_api_finance_report_returns_projection_trace(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    monkeypatch.setattr(
        process_mining_api,
        "get_finance_process_mining_report",
        process_mining_api.get_finance_process_mining_report,
    )
    monkeypatch.setattr(_gw, "_projection_status_loader",
        lambda tenant_id, db=None: make_projection_status(
            ProjectionStatusEntry(
                projection_key="ap-invoice-cockpit",
                item_count=3,
                cached=True,
                cursor_status="ready",
                cursor_source="outbox",
                last_processed_event_id="100",
            )
        )
    )
    monkeypatch.setattr(_gw, "_runtime_report_loader", lambda tenant_id, db=None: make_runtime_report())
    device_store = {
        "device-3": DeviceManifest(
            device_id="device-3",
            device_type=DeviceType.weighbridge,
            tenant_id="tenant-a",
            location="Waage 1",
            status=DeviceStatus.online,
        ).model_dump()
    }
    monkeypatch.setattr(_gw, "_telemetry_device_store", {"tenant-a": device_store})
    monkeypatch.setattr(_gw, "_telemetry_reading_store", {"tenant-a": {}})

    app = FastAPI()
    app.include_router(process_mining_api.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.get(
            "/api/v1/process-mining/finance/report",
            headers={"X-Tenant-ID": "tenant-a"},
        )

    session.close()
    engine.dispose()
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["ready_count"] == 1
    assert data["traces"][0]["projection_key"] == "ap-invoice-cockpit"
    assert data["traces"][0]["last_event_processed"] == "100"
    assert data["observability_signals"][0]["source_key"] == "device-3"


def test_api_finance_bottlenecks_returns_lagging_entries(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    monkeypatch.setattr(_gw, "_projection_status_loader",
        lambda tenant_id, db=None: make_projection_status(
            ProjectionStatusEntry(
                projection_key="payment-run-cockpit",
                item_count=1,
                cached=True,
                cursor_status="pending-replay",
                cursor_source="outbox",
            )
        )
    )
    monkeypatch.setattr(_gw, "_runtime_report_loader", lambda tenant_id, db=None: make_runtime_report())
    monkeypatch.setattr(_gw, "_telemetry_device_store", {"tenant-a": {}})
    monkeypatch.setattr(_gw, "_telemetry_reading_store", {"tenant-a": {}})

    app = FastAPI()
    app.include_router(process_mining_api.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.get(
            "/api/v1/process-mining/finance/bottlenecks",
            headers={"X-Tenant-ID": "tenant-a"},
        )

    session.close()
    engine.dispose()
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["source_key"] == "payment-run-cockpit"


def test_reporting_process_mining_report_endpoint(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    monkeypatch.setattr(_gw, "_projection_status_loader",
        lambda tenant_id, db=None: make_projection_status(
            ProjectionStatusEntry(
                projection_key="process-observation",
                item_count=2,
                cached=True,
                cursor_status="ready",
                cursor_source="workflow_audit",
                last_processed_event_id="21",
            )
        )
    )
    monkeypatch.setattr(_gw, "_runtime_report_loader", lambda tenant_id, db=None: make_runtime_report())
    monkeypatch.setattr(_gw, "_telemetry_device_store", {"tenant-a": {}})
    monkeypatch.setattr(_gw, "_telemetry_reading_store", {"tenant-a": {}})

    app = FastAPI()
    app.include_router(reporting_api.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.post(
            "/api/v1/reporting/process-mining/report",
            json={"requesting_tenant": "tenant-a", "tenant_id": "tenant-a"},
        )

    session.close()
    engine.dispose()
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["traces"][0]["projection_key"] == "process-observation"


def test_benchmark_process_mining_endpoint(monkeypatch):
    monkeypatch.setattr(_gw, "_projection_status_loader",
        lambda tenant_id, db=None: make_projection_status(
            ProjectionStatusEntry(
                projection_key="ap-invoice-cockpit",
                item_count=3,
                cached=True,
                cursor_status="ready" if tenant_id == "tenant-a" else "pending-replay",
                cursor_source="outbox",
            )
        )
    )
    monkeypatch.setattr(_gw, "_runtime_report_loader", lambda tenant_id, db=None: make_runtime_report())
    monkeypatch.setattr(_gw, "_telemetry_device_store", {"tenant-a": {}, "tenant-b": {}})
    monkeypatch.setattr(_gw, "_telemetry_reading_store", {"tenant-a": {}, "tenant-b": {}})

    app = FastAPI()
    app.include_router(benchmark_api.router, prefix="/api/v1")

    with TestClient(app, raise_server_exceptions=True) as client:
        response = client.get(
            "/api/v1/benchmark/process-mining/verbund-1",
            params=[("periode", "2026-03"), ("tenant_ids", "tenant-a"), ("tenant_ids", "tenant-b")],
        )

    assert response.status_code == 200
    data = response.json()
    kennzahlen = {entry["kz_name"] for entry in data["gruppen"][0]["kennzahlen"]}
    assert "process_ready_count" in kennzahlen
    assert "process_lagging_count" in kennzahlen
