"""
Wave-18 Contract Tests: Process Kernel API Surfacing

AP6: Lesende Surfacing-Endpoints fuer Process Definitions und Workflow-Versionen
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api


def _make_client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    return TestClient(app)


def test_list_process_definitions_returns_wave18_registry():
    with _make_client() as client:
        response = client.get("/process/definitions")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 4
    keys = {item["process_definition_key"] for item in data["definitions"]}
    assert "contract_to_intake" in keys
    assert "settlement_to_finance" in keys
    assert data["schema_version"] == 1


def test_list_process_definitions_filters_by_domain():
    with _make_client() as client:
        response = client.get("/process/definitions", params={"domain": "finance"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["definitions"][0]["process_definition_key"] == "settlement_to_finance"


def test_get_process_definition_includes_active_workflow_version():
    with _make_client() as client:
        response = client.get("/process/definitions/quality_to_settlement")
    assert response.status_code == 200
    data = response.json()
    assert data["process_definition_key"] == "quality_to_settlement"
    assert data["active_workflow_version"]["definition_ref"]["workflow_key"] == "settlement"
    assert data["active_workflow_version"]["definition_ref"]["version_number"] == 1


def test_get_process_definition_returns_404_for_unknown_key():
    with _make_client() as client:
        response = client.get("/process/definitions/unknown-process")
    assert response.status_code == 404
    assert "nicht im Register" in response.json()["detail"]


def test_list_process_workflows_returns_version_registry():
    with _make_client() as client:
        response = client.get("/process/workflows")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 4
    process_keys = {
        item["definition_ref"]["process_definition_key"] for item in data["workflows"]
    }
    assert "contract_to_intake" in process_keys
    assert "settlement_to_finance" in process_keys


def test_list_process_workflows_filters_by_process_definition_and_active_only():
    with _make_client() as client:
        response = client.get(
            "/process/workflows",
            params={
                "process_definition_key": "settlement_to_finance",
                "active_only": "true",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    workflow = data["workflows"][0]
    assert workflow["status"] == "active"
    assert workflow["definition_ref"]["process_definition_key"] == "settlement_to_finance"
