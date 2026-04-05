"""
Wave-18 Contract Tests: Action Execution Process Contracts

AP5: Action- und Business-Commands tragen process_definition_key und Workflow-Metadaten
"""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api
from app.core.database import get_db
from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionService,
    ActionExecutionStatus,
)
from app.core.action_idempotency import get_action_idempotency_store


def _make_client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    mock_session = MagicMock()

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_action_execution_request_to_business_command_carries_wave18_process_metadata():
    request = ActionExecutionRequest(
        command_name="ApproveAPInvoice",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        tenant_id="t1",
        issuer_role="ap_approver",
        issuer_type="human",
        idempotency_key="idem-wave18-1",
        process_definition_key="settlement_to_finance",
        workflow_key="ap_invoice_approval",
        workflow_version_number=1,
    )
    command = request.to_business_command()
    assert command.process_definition_key == "settlement_to_finance"
    assert command.workflow_key == "ap_invoice_approval"
    assert command.workflow_version_number == 1


def test_action_execution_service_enriches_active_workflow_metadata_when_only_process_definition_is_given():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="ApproveAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "ZUR_FREIGABE"},
            tenant_id="t1",
            issuer_role="ap_approver",
            issuer_type="human",
            idempotency_key="idem-wave18-2",
            process_definition_key="settlement_to_finance",
        )
    )
    assert result.status == ActionExecutionStatus.ACCEPTED
    assert result.process_definition_key == "settlement_to_finance"
    assert result.workflow_key == "ap_invoice_approval"
    assert result.workflow_version_number == 1


def test_action_execution_service_rejects_command_not_registered_for_process_definition():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="ApproveAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "ZUR_FREIGABE"},
            tenant_id="t1",
            issuer_role="ap_approver",
            issuer_type="human",
            idempotency_key="idem-wave18-3",
            process_definition_key="quality_to_settlement",
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "PROCESS_CONTRACT_INVALID"


def test_action_execution_service_rejects_non_active_workflow_version():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="ApproveAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "ZUR_FREIGABE"},
            tenant_id="t1",
            issuer_role="ap_approver",
            issuer_type="human",
            idempotency_key="idem-wave18-4",
            process_definition_key="settlement_to_finance",
            workflow_version_number=2,
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "PROCESS_CONTRACT_INVALID"


def test_action_execute_api_returns_wave18_process_metadata_in_snapshot():
    store = get_action_idempotency_store()
    store.clear()
    with _make_client() as client:
        response = client.post(
            "/process/actions/execute",
            json={
                "command_name": "ReleaseQualityProtocol",
                "aggregate_type": "quality_protocol",
                "aggregate_id": "QP-1",
                "payload": {"approved_by": "lab-user"},
                "tenant_id": "t1",
                "issuer_role": "quality_manager",
                "issuer_type": "human",
                "idempotency_key": "idem-wave18-5",
                "process_definition_key": "intake_to_quality",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["process_definition_key"] == "intake_to_quality"
    assert data["workflow_key"] == "annahme"
    assert data["workflow_version_number"] == 1


def test_action_execute_api_replays_same_process_metadata_on_idempotent_lookup():
    store = get_action_idempotency_store()
    store.clear()
    body = {
        "command_name": "ApproveAPInvoice",
        "aggregate_type": "ap_invoice",
        "aggregate_id": "INV-1",
        "payload": {"status": "ZUR_FREIGABE"},
        "tenant_id": "t1",
        "issuer_role": "ap_approver",
        "issuer_type": "human",
        "idempotency_key": "idem-wave18-6",
        "process_definition_key": "settlement_to_finance",
    }
    with _make_client() as client:
        first = client.post("/process/actions/execute", json=body)
        second = client.post("/process/actions/execute", json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"
    assert second.json()["process_definition_key"] == "settlement_to_finance"
    assert second.json()["workflow_key"] == "ap_invoice_approval"
    assert second.json()["workflow_version_number"] == 1
