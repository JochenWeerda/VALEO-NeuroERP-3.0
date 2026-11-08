import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.schemas.advisory_input import PolicyEvaluationIn, ApprovalEvaluationIn
from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools
from app.core.mcp_rest_binding import check_request_binding
from app.services.neuro_tool_execution import NeuroToolExecutionService


@pytest.fixture(autouse=True)
def _enable_dev_token(): yield


@pytest.mark.parametrize("name,model,payload", [
 ("valeo_compliance_policy_evaluate", PolicyEvaluationIn, {"prozess_key": "probe", "kontext": {"amount": 10}}),
 ("valeo_workflow_approval_evaluate", ApprovalEvaluationIn, {"aktions_typ": "probe", "kontext": {"amount": 10}}),
])
def test_shared_canonical_context_and_negative_transport(name, model, payload, monkeypatch):
    contract = get_process_kernel_mcp_tools().by_tool_name(name)
    assert contract.schema_version == 2
    assert contract.as_mcp_tool()["inputSchema"] == model.model_json_schema()
    class ForbiddenClient:
        def request(self, **kwargs): pytest.fail("Missing context reached HTTP")
    service = NeuroToolExecutionService(ForbiddenClient())
    assert service._build_body(contract, {}, payload, {}, "own") == model.model_validate(payload).model_dump(mode="json")
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    missing = dict(payload); missing.pop("kontext")
    result = service.execute_contract(contract, parameters=missing, tenant_id="own", context={"auth_token": "synthetic-only"})
    assert result["http_status"] == 422


def test_advisory_rest_schemas_match_registry():
    from app.api.v1.endpoints.process_kernel_api import evaluate_policy_rules, evaluate_agent_approval
    app = FastAPI()
    app.post("/api/v1/process/policy-rules/evaluate")(evaluate_policy_rules)
    app.post("/api/v1/process/agent/approval-evaluate")(evaluate_agent_approval)
    for name in ("valeo_compliance_policy_evaluate", "valeo_workflow_approval_evaluate"):
        assert check_request_binding(app.openapi(), get_process_kernel_mcp_tools().by_tool_name(name)) == []
