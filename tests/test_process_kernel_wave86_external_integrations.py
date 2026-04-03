from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.core.endpoint_gateways as _gw
from app.api.v1.endpoints import (
    external_agent_integrations,
    job_runner,
    process_mining_api,
    reklamation_api,
    tenant_governance,
    workflow_simulation,
)
from app.core.finance_projection_status import ProjectionStatusEntry, ProjectionStatusReadModel
from app.core.iot_telemetry import DeviceManifest, DeviceStatus, DeviceType
from app.core.process_mining import build_process_mining_report
from app.core.runtime_operations import ComponentHealth, RuntimeComponent, RuntimeHealthReport
from app.core.tenant import get_tenant_id


def test_external_agent_integration_catalog_surfaces_eleven_use_cases():
    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    client = TestClient(app)

    response = client.get("/agent/integrations")

    assert response.status_code == 200
    body = response.json()
    assert body["manifest_kind"] == "EXTERNAL_AGENT_INTEGRATION_CATALOG"
    assert body["provider_count"] >= 7
    assert body["use_case_count"] >= 13
    assert "knowledge_lookup" in {item["use_case_id"] for item in body["use_cases"]}
    assert "slack_app" in {provider["provider_key"] for provider in body["providers"]}
    assert "superglue" in {provider["provider_key"] for provider in body["providers"]}


def test_external_agent_install_pack_exposes_entrypoints_and_headers():
    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    client = TestClient(app)

    response = client.get("/agent/integrations/use-cases/document_extraction/install-pack")

    assert response.status_code == 200
    body = response.json()
    assert body["use_case_id"] == "document_extraction"
    assert "/api/v1/process/dms/extract" in body["entrypoints"]
    assert "Authorization" in body["required_headers"]


def test_workflow_sandbox_preview_alias_returns_preview_result():
    app = FastAPI()
    app.include_router(workflow_simulation.router)
    client = TestClient(app)

    response = client.post(
        "/workflow/simulation/sandbox/preview",
        json={
            "tenant_id": "tenant-a",
            "process_key": "ap_invoice_approval",
            "scenario": "standard_approval",
            "workflow_definition_version": "1.0.0",
            "context": {"workflow_definition_status": "ACTIVE"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sandbox_mode"] == "preview"
    assert body["simulation"]["final_status"] == "completed"


def test_process_mining_top_processes_and_drilldown(monkeypatch):
    monkeypatch.setattr(
        _gw,
        "_projection_status_loader",
        lambda tenant_id, db=None: ProjectionStatusReadModel(
            tenant_id=tenant_id,
            projection_count=2,
            persisted_snapshot_count=1,
            persisted_cursor_count=1,
            cache_hits=2,
            cache_misses=1,
            projections=[
                ProjectionStatusEntry(
                    projection_key="ap-invoice-cockpit",
                    item_count=7,
                    cached=True,
                    cursor_status="ready",
                    cursor_source="outbox",
                    last_processed_event_id="100",
                ),
                ProjectionStatusEntry(
                    projection_key="payment-run-cockpit",
                    item_count=3,
                    cached=True,
                    cursor_status="pending-replay",
                    cursor_source="outbox",
                ),
            ],
        ),
    )
    monkeypatch.setattr(
        _gw,
        "_runtime_report_loader",
        lambda tenant_id, db=None: RuntimeHealthReport(
            tenant_id=tenant_id,
            overall_health=ComponentHealth.HEALTHY,
            components=[RuntimeComponent(component_id="finance", component_type="projection_consumer", health=ComponentHealth.HEALTHY)],
        ),
    )
    monkeypatch.setattr(_gw, "_telemetry_device_store", {"tenant-a": {}})
    monkeypatch.setattr(_gw, "_telemetry_reading_store", {"tenant-a": {}})

    app = FastAPI()
    app.include_router(process_mining_api.router)
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    client = TestClient(app)

    top_response = client.get("/process-mining/finance/top-processes?limit=1")
    assert top_response.status_code == 200
    top_body = top_response.json()
    assert top_body[0]["projection_key"] == "payment-run-cockpit"
    assert top_body[0]["bottleneck_count"] >= 1

    drilldown_response = client.get("/process-mining/finance/drilldown/payment-run-cockpit")
    assert drilldown_response.status_code == 200
    drilldown_body = drilldown_response.json()
    assert drilldown_body["projection_key"] == "payment-run-cockpit"
    assert drilldown_body["trace"]["state"] == "lagging"


def test_job_catalog_surfaces_queue_contracts():
    app = FastAPI()
    app.include_router(job_runner.router, prefix="/api/v1/jobs")
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    client = TestClient(app)

    response = client.get("/api/v1/jobs/catalog")

    assert response.status_code == 200
    body = response.json()
    assert body["job_count"] >= 10
    assert body["queue_summary"]["schema_version"] == 1
    assert len(body["routings"]) == body["job_count"]


def test_runtime_shield_surfaces_rate_limits_and_cache_configs():
    app = FastAPI()
    app.include_router(tenant_governance.router)
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    client = TestClient(app)

    response = client.get("/tenant/runtime-shield")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-a"
    assert len(body["rate_limit_policies"]) >= 5
    assert len(body["cache_configs"]) >= 3


def test_reklamation_e2e_overview_contains_crm_and_dms_links():
    app = FastAPI()
    app.include_router(reklamation_api.router)
    client = TestClient(app)

    created = client.post(
        "/reklamationen",
        json={
            "tenant_id": "tenant-a",
            "lieferant_id": "supplier-1",
            "typ": "qualitaet",
            "positionen": [
                {
                    "artikel_id": "article-1",
                    "beanstandete_menge": 100,
                    "anerkannte_menge": 20,
                    "beanstandeter_wert_eur": 1000,
                    "begruendung": "Falsche Lieferung",
                }
            ],
            "zustaendiger": "support",
            "frist_datum": "2026-03-25",
            "crm_referenz": {
                "crm_system": "salesforce",
                "crm_case_id": "CRM-1",
            },
            "dms_referenzen": [
                {
                    "dokument_id": "DOC-1",
                    "dokument_typ": "REKLAMATION",
                }
            ],
        },
    )
    assert created.status_code == 201
    reklamation_id = created.json()["reklamation_id"]

    response = client.get(f"/reklamationen/{reklamation_id}/e2e")

    assert response.status_code == 200
    body = response.json()
    assert body["e2e_complete"] is True
    assert body["crm_case_id"] == "CRM-1"
    assert body["dms_document_ids"] == ["DOC-1"]
    assert body["sla_status"] in {"in_frist", "bald_faellig", "ueberfaellig", "erledigt"}
