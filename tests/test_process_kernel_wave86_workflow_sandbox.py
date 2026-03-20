from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import workflow_simulation
from app.core.workflow_simulation import SimulationScenario, preview_workflow_sandbox


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(workflow_simulation.router)
    return TestClient(app)


def test_preview_workflow_sandbox_builds_warnings_for_draft_context():
    preview = preview_workflow_sandbox(
        workflow_simulation.WorkflowSandboxPreviewInput(
            tenant_id="tenant-1",
            process_key="ap_invoice_approval",
            scenario=SimulationScenario.STANDARD_APPROVAL,
            workflow_definition_version="2.1.0",
            context={
                "workflow_definition_status": "ENTWURF",
                "requires_migration": True,
                "draft_only": True,
            },
        )
    )

    assert preview.process_key == "ap_invoice_approval"
    assert preview.simulation.final_status == "completed"
    assert len(preview.warnings) >= 2
    assert preview.recommended_next_action.startswith("Workflow kann")


def test_workflow_simulation_preview_endpoint_returns_nested_simulation():
    client = _client()

    response = client.post(
        "/workflow/simulation/preview",
        json={
            "tenant_id": "tenant-1",
            "process_key": "ap_invoice_approval",
            "scenario": "rejection",
            "workflow_definition_version": "2.1.0",
            "simulation_date": "2026-03-20",
            "context": {"workflow_definition_status": "AKTIV"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["process_key"] == "ap_invoice_approval"
    assert body["simulation"]["scenario"] == "rejection"
    assert body["simulation"]["final_status"] == "rejected"
    assert body["warnings"]
    assert body["recommended_next_action"].startswith("Regeln")


def test_workflow_simulation_run_endpoint_remains_available():
    client = _client()

    response = client.post(
        "/workflow/simulation/run",
        json={
            "tenant_id": "tenant-1",
            "process_key": "ap_invoice_approval",
            "scenario": "standard_approval",
            "workflow_definition_version": "2.1.0",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "standard_approval"
    assert body["final_status"] == "completed"
