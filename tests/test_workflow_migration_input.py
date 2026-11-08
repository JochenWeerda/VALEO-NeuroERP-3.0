"""Explicit migration content, transport and endpoint safety."""
from copy import deepcopy
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.schemas.workflow_migration_input import WorkflowMigrationCheckIn
from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools
from app.services.neuro_tool_execution import NeuroToolExecutionService


@pytest.fixture(autouse=True)
def _enable_dev_token():
    # This isolated contract does not modify any production identity checks.
    yield


def payload():
    return {"prozess_key": "probe", "von_version": "1", "zu_version": "2",
            "alt_schritte": [{"schritt_id": "POST", "pflicht": True, "terminal": True}],
            "neu_schritte": []}


def client():
    from app.api.v1.endpoints.process_kernel_api import check_workflow_migration
    app = FastAPI()
    app.post("/check")(check_workflow_migration)
    return TestClient(app)


@pytest.mark.parametrize("change", ["missing_old", "missing_new", "empty_old", "duplicate", "false_string", "unknown", "blank"])
def test_invalid_snapshots_are_not_safe(change):
    value = payload()
    if change == "missing_old": value.pop("alt_schritte")
    elif change == "missing_new": value.pop("neu_schritte")
    elif change == "empty_old": value["alt_schritte"] = []
    elif change == "duplicate": value["alt_schritte"] *= 2
    elif change == "false_string": value["alt_schritte"][0]["pflicht"] = "false"
    elif change == "unknown": value["approved_by"] = "caller"
    elif change == "blank": value["alt_schritte"][0]["schritt_id"] = " "
    with pytest.raises(ValidationError):
        WorkflowMigrationCheckIn.model_validate(value)


def test_empty_http_body_no_longer_returns_demo_safe():
    response = client().post("/check", json={})
    assert response.status_code == 422


def test_empty_target_is_real_deletion():
    response = client().post("/check", json=payload())
    assert response.status_code == 200
    result = response.json()
    assert result["risiko_klasse"] == "BREAKING"
    assert result["migration_erlaubt"] is False
    assert result["comparison_revision"] == WorkflowMigrationCheckIn.model_validate(payload()).comparison_revision()


def test_fingerprint_binds_roles_and_versions():
    original = WorkflowMigrationCheckIn.model_validate(payload()).comparison_revision()
    value = payload()
    value["alt_schritte"][0]["rolle"] = "different"
    assert WorkflowMigrationCheckIn.model_validate(value).comparison_revision() != original
    value = payload()
    value["zu_version"] = "3"
    assert WorkflowMigrationCheckIn.model_validate(value).comparison_revision() != original


def test_mcp_schema_comes_from_rest_validator_and_is_not_mutable():
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_workflow_migration_check")
    schema = contract.as_mcp_tool()["inputSchema"]
    assert schema == WorkflowMigrationCheckIn.model_json_schema()
    assert contract.schema_version == 2
    schema["required"].clear()
    assert contract.as_mcp_tool()["inputSchema"]["required"]


def test_transport_retains_target_and_rejects_missing_before_http(monkeypatch):
    class ForbiddenClient:
        def request(self, **kwargs):
            pytest.fail("Invalid migration must not reach HTTP")
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_workflow_migration_check")
    service = NeuroToolExecutionService(ForbiddenClient())
    expected = WorkflowMigrationCheckIn.model_validate(payload()).model_dump(mode="json")
    body = service._build_body(contract, {}, payload(), {}, "tenant")
    assert body == expected
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    value = payload()
    value.pop("neu_schritte")
    result = service.execute_contract(contract, parameters=value, tenant_id="tenant",
                                      context={"auth_token": "synthetic-only"})
    assert result["http_status"] == 422
    assert result["rejection_reason"] == "invalid_contract_payload"


def test_rest_schema_drift_is_rejected():
    from app.core.mcp_rest_binding import check_request_binding
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_workflow_migration_check")
    spec = client().app.openapi()
    spec["paths"]["/api/v1/process/workflow-migration/check"] = spec["paths"].pop("/check")
    assert check_request_binding(spec, contract) == []
    spec["components"]["schemas"]["WorkflowMigrationStepIn"]["properties"]["pflicht"]["type"] = "string"
    assert check_request_binding(spec, contract)


def test_schema_annotations_do_not_hide_a_field_named_title():
    from app.core.mcp_rest_binding import check_request_binding
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_workflow_migration_check")
    contract.input_schema = {"type": "object", "properties": {"title": {"type": "string"}}}
    spec = {"paths": {"/api/v1/process/workflow-migration/check": {"post": {
        "requestBody": {"content": {"application/json": {"schema": {
            "type": "object", "properties": {"title": {"type": "number"}}
        }}}}}}}}
    assert check_request_binding(spec, contract)
