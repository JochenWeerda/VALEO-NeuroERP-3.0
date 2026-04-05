"""
Wave-17 Contract Tests: Action Execution Layer und Agent Contracts
"""
from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints import process_kernel_api
from app.core.database import get_db
from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ActionExecutionService,
    ActionExecutionStatus,
    ActionResultSource,
)
from app.core.action_idempotency import get_action_idempotency_store


@pytest.fixture(autouse=True)
def clear_action_store():
    store = get_action_idempotency_store()
    store.clear()
    yield
    store.clear()


@pytest.fixture(autouse=True)
def register_procurement_command_mutations():
    """Gleicher Registry-Stand wie Produktion (api.py ruft register_command_mutations)."""
    from app.services.command_handlers_procurement import register_command_mutations

    register_command_mutations()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    mock_session = MagicMock()

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_action_execution_request_accepts_wave11_reference_context():
    request = ActionExecutionRequest(
        command_name="ApproveAPInvoice",
        aggregate_type="ap_invoice",
        aggregate_id="INV-1",
        payload={"status": "ZUR_FREIGABE"},
        tenant_id="t1",
        issuer_role="ap_approver",
        issuer_type="human",
        idempotency_key="idem-1",
        reference_context={
            "process_key": "settlement",
            "anchor_entity": "settlement",
            "anchor_id": "SET-1",
            "chain": {"contract_id": "KON-1", "settlement_id": "SET-1"},
        },
    )
    ctx = request.normalized_reference_context()
    assert ctx is not None
    assert ctx.process_key == "settlement"
    assert ctx.chain.contract_id == "KON-1"


def test_action_execution_service_accepts_valid_human_command():
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
            idempotency_key="idem-2",
        )
    )
    assert result.status == ActionExecutionStatus.ACCEPTED
    assert result.aggregate_owner == "finance"
    assert result.result_source == ActionResultSource.FRESH


def test_action_execution_service_calls_db_when_accepted():
    """Mit Session: Audit-Pfad (execute/commit) wird ausgeloest — Domain-Handler optional."""
    mock_db = MagicMock()
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
            idempotency_key="idem-db-mutation",
        ),
        db=mock_db,
    )
    assert result.status == ActionExecutionStatus.ACCEPTED
    mock_db.execute.assert_called()
    mock_db.commit.assert_called()


def test_create_purchase_order_runs_domain_mutation_with_db():
    """CreatePurchaseOrder: Dispatch ACCEPTED + registrierter Handler → mehrere executes (Audit + Bestellung)."""
    mock_db = MagicMock()
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="CreatePurchaseOrder",
            aggregate_type="purchase_order",
            aggregate_id="PO-UNIT-1",
            payload={
                "approval_status": "approved",
                "lieferant_id": 1,
                "bestellnummer": "UNIT-AE-PO-1",
            },
            tenant_id="t-procurement",
            issuer_role="buyer",
            issuer_type="human",
            idempotency_key="idem-create-po-domain-1",
        ),
        aggregate_state={
            "approval_status": "approved",
            "lieferant_id": 1,
            "bestellnummer": "UNIT-AE-PO-1",
        },
        db=mock_db,
    )
    assert result.status == ActionExecutionStatus.ACCEPTED
    assert mock_db.execute.call_count >= 2
    mock_db.commit.assert_called()


def test_action_execution_service_rejects_unknown_command_name():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="DeleteEverything",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={},
            tenant_id="t1",
            issuer_role="admin",
            issuer_type="human",
            idempotency_key="idem-3",
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "AGGREGATE_COMMAND_MISMATCH"


def test_action_execution_service_rejects_wrong_role():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="PostAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "FREIGEGEBEN"},
            tenant_id="t1",
            issuer_role="warehouse_manager",
            issuer_type="human",
            idempotency_key="idem-4",
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "ROLE_DENIED"


def test_action_execution_service_returns_pending_approval_when_human_confirmation_missing():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="PostAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "FREIGEGEBEN"},
            tenant_id="t1",
            issuer_role="finance_manager",
            issuer_type="human",
            idempotency_key="idem-5",
            human_confirmation=False,
        )
    )
    assert result.status == ActionExecutionStatus.PENDING_APPROVAL
    assert result.requires_human_confirmation is True
    assert result.error is not None
    assert result.error.code == "HUMAN_CONFIRMATION_REQUIRED"


def test_action_execution_service_blocks_fully_blocked_agent_command():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="RejectAPInvoice",
            aggregate_type="ap_invoice",
            aggregate_id="INV-1",
            payload={"status": "ZUR_FREIGABE"},
            tenant_id="t1",
            issuer_role="audit_agent",
            issuer_type="ai_agent",
            idempotency_key="idem-6",
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "AGENT_COMMAND_BLOCKED"


def test_action_execution_service_blocks_agent_type_not_allowed():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="FinalizeHarvestAcceptance",
            aggregate_type="harvest_acceptance",
            aggregate_id="HA-1",
            payload={"release_status": "final"},
            tenant_id="t1",
            issuer_role="audit_agent",
            issuer_type="ai_agent",
            idempotency_key="idem-7",
        )
    )
    assert result.status == ActionExecutionStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "AGENT_TYPE_NOT_ALLOWED"


def test_action_execution_service_accepts_allowed_agent_type():
    service = ActionExecutionService()
    result = service.execute(
        ActionExecutionRequest(
            command_name="FinalizeHarvestAcceptance",
            aggregate_type="harvest_acceptance",
            aggregate_id="HA-1",
            payload={"release_status": "final"},
            tenant_id="t1",
            issuer_role="acceptance_agent",
            issuer_type="ai_agent",
            idempotency_key="idem-8",
        )
    )
    assert result.status == ActionExecutionStatus.ACCEPTED
    assert result.aggregate_owner == "agrar"


def test_action_execute_api_returns_404_for_unknown_aggregate(client: TestClient):
    response = client.post(
        "/process/actions/execute",
        json={
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "shadow_model",
            "aggregate_id": "INV-1",
            "payload": {"status": "ZUR_FREIGABE"},
            "tenant_id": "t1",
            "issuer_role": "ap_approver",
            "issuer_type": "human",
            "idempotency_key": "idem-9",
        },
    )
    assert response.status_code == 404
    assert "nicht im Register" in response.json()["detail"]


def test_action_execute_api_returns_422_for_missing_required_fields(client: TestClient):
    response = client.post(
        "/process/actions/execute",
        json={
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-1",
            "tenant_id": "t1",
            "issuer_type": "human",
            "idempotency_key": "idem-10",
        },
    )
    assert response.status_code == 422


def test_action_execute_api_replays_same_execution_id_for_same_request(client: TestClient):
    body = {
        "command_name": "ApproveAPInvoice",
        "aggregate_type": "ap_invoice",
        "aggregate_id": "INV-1",
        "payload": {"status": "ZUR_FREIGABE"},
        "tenant_id": "t1",
        "issuer_role": "ap_approver",
        "issuer_type": "human",
        "idempotency_key": "idem-11",
    }
    first = client.post("/process/actions/execute", json=body)
    second = client.post("/process/actions/execute", json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    first_data = first.json()
    second_data = second.json()
    assert first_data["execution_id"] == second_data["execution_id"]
    assert first_data["status"] == "accepted"
    assert second_data["status"] == "duplicate"
    assert second_data["result_source"] == "idempotent_replay"


def test_action_execute_api_returns_409_on_idempotency_key_reuse_with_other_payload(
    client: TestClient,
):
    first = {
        "command_name": "ApproveAPInvoice",
        "aggregate_type": "ap_invoice",
        "aggregate_id": "INV-1",
        "payload": {"status": "ZUR_FREIGABE"},
        "tenant_id": "t1",
        "issuer_role": "ap_approver",
        "issuer_type": "human",
        "idempotency_key": "idem-12",
    }
    second = {
        **first,
        "payload": {"status": "TEILWEISE_FREIGEGEBEN"},
    }
    assert client.post("/process/actions/execute", json=first).status_code == 200
    conflict = client.post("/process/actions/execute", json=second)
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_get_action_by_execution_id_returns_canonical_snapshot(client: TestClient):
    response = client.post(
        "/process/actions/execute",
        json={
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-1",
            "payload": {"status": "ZUR_FREIGABE"},
            "tenant_id": "t1",
            "issuer_role": "ap_approver",
            "issuer_type": "human",
            "idempotency_key": "idem-13",
        },
    )
    execution_id = response.json()["execution_id"]
    fetched = client.get(f"/process/actions/{execution_id}")
    assert fetched.status_code == 200
    assert fetched.json()["execution_id"] == execution_id
    assert fetched.json()["result_source"] == "fresh"


def test_get_action_by_idempotency_returns_same_snapshot_as_execution_lookup(client: TestClient):
    response = client.post(
        "/process/actions/execute",
        json={
            "command_name": "FinalizeHarvestAcceptance",
            "aggregate_type": "harvest_acceptance",
            "aggregate_id": "HA-2",
            "payload": {"release_status": "final"},
            "tenant_id": "t1",
            "issuer_role": "warehouse_manager",
            "issuer_type": "human",
            "idempotency_key": "idem-14",
        },
    )
    execution_id = response.json()["execution_id"]
    by_execution = client.get(f"/process/actions/{execution_id}")
    by_key = client.get("/process/actions/idempotency/t1/idem-14")
    assert by_execution.status_code == 200
    assert by_key.status_code == 200
    assert by_execution.json() == by_key.json()


def test_get_action_endpoints_return_404_for_unknown_records(client: TestClient):
    by_execution = client.get("/process/actions/not-found")
    by_key = client.get("/process/actions/idempotency/t1/not-found")
    assert by_execution.status_code == 404
    assert by_key.status_code == 404


def test_action_execution_result_schema_version_contract(client: TestClient):
    response = client.post(
        "/process/actions/execute",
        json={
            "command_name": "ExecutePaymentRun",
            "aggregate_type": "payment_run",
            "aggregate_id": "PR-1",
            "payload": {"status": "FREIGEGEBEN"},
            "tenant_id": "t1",
            "issuer_role": "treasury_manager",
            "issuer_type": "human",
            "idempotency_key": "idem-15",
            "human_confirmation": True,
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["schema_version"] == 1
    assert data["aggregate_owner"] == "finance"
    assert data["command_name"] == "ExecutePaymentRun"


def test_get_action_snapshot_parses_to_result_model(client: TestClient):
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
            "idempotency_key": "idem-16",
        },
    )
    execution_id = response.json()["execution_id"]
    snapshot = client.get(f"/process/actions/{execution_id}")
    parsed = ActionExecutionResult(**snapshot.json())
    assert parsed.status == ActionExecutionStatus.ACCEPTED
    assert parsed.aggregate_owner == "agrar"
