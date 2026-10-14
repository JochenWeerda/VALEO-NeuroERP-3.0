from copy import deepcopy

import pytest
from app.core.mcp_rest_binding import check_read_binding
from app.core.mcp_tool_contracts import (
    MCPToolContract, MCPToolKategorie, MCPToolParameter, MCPParameterTyp,
    get_process_kernel_mcp_tools,
)
from app.services.neuro_tool_execution import NeuroToolExecutionService


@pytest.fixture(autouse=True)
def _enable_dev_token():
    # Pure schema checks and execution rejection: no compatibility app/auth double.
    yield


def sample():
    contract = MCPToolContract(
        "valeo_process_probe", "process", "probe", "probe", MCPToolKategorie.LESEN,
        parameter=[MCPToolParameter("id", MCPParameterTyp.STRING, "id", True),
                   MCPToolParameter("limit", MCPParameterTyp.INTEGER, "limit", False, minimum=1, maximum=50)],
        api_endpoint="GET /probe/{id}",
    )
    spec = {"paths": {"/probe/{id}": {"get": {"operationId": "read_probe", "parameters": [
        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
        {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 50}},
    ]}}}}
    return spec, contract


def test_valid_read_binding():
    spec, contract = sample()
    assert check_read_binding(spec, contract) == []


@pytest.mark.parametrize("fault,expected", [
    ("path", "missing REST operation"), ("operation", "missing REST operationId"),
    ("unknown", "unknown REST parameter"), ("required", "missing required REST parameter"),
    ("type", "incompatible type"), ("bound", "weaker maximum"),
    ("enum", "incompatible enum"), ("duplicate", "duplicate tool parameter"),
])
def test_drift_is_rejected(fault, expected):
    spec, contract = sample()
    op = spec["paths"]["/probe/{id}"]["get"]
    if fault == "path": spec["paths"] = {}
    elif fault == "operation": op.pop("operationId")
    elif fault == "unknown": contract.parameter[1].name = "ignored_filter"
    elif fault == "required": contract.parameter[0].pflicht = False
    elif fault == "type": op["parameters"][1]["schema"]["type"] = "number"
    elif fault == "bound": op["parameters"][1]["schema"]["maximum"] = 10
    elif fault == "enum": op["parameters"][0]["schema"]["enum"] = ["a", "b"]
    elif fault == "duplicate": contract.parameter.append(deepcopy(contract.parameter[0]))
    assert any(expected in error for error in check_read_binding(spec, contract))


def test_nullable_referenced_schema_is_checked():
    spec, contract = sample()
    spec["components"] = {"schemas": {"Limit": {"type": "integer", "minimum": 1, "maximum": 50}}}
    spec["paths"]["/probe/{id}"]["get"]["parameters"][1]["schema"] = {
        "anyOf": [{"$ref": "#/components/schemas/Limit"}, {"type": "null"}]}
    assert check_read_binding(spec, contract) == []


@pytest.mark.parametrize("name", ["valeo_agrar_quality_protocol_approve", "valeo_finance_dunning_run"])
def test_business_mutations_cannot_use_read_execution(name):
    contract = get_process_kernel_mcp_tools().by_tool_name(name)
    assert contract.kategorie == MCPToolKategorie.SCHREIBEN
    assert contract.requires_approval
    result = NeuroToolExecutionService._execution_rejection(
        contract, "tenant", {"auth_token": "synthetic-not-used", "execution_headers": {}})
    assert result["rejection_reason"] == "write_capability_not_approved"


def test_definition_list_cannot_masquerade_as_instance_verification():
    class ForbiddenTransport:
        def request(self, **kwargs):
            pytest.fail("Unsupported instance contract must not call REST")

    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_workflow_instance_status")
    result = NeuroToolExecutionService(ForbiddenTransport()).execute_contract(
        contract, parameters={"instance_id": "probe"}, tenant_id="tenant",
        context={"auth_token": "synthetic-not-used"},
    )
    assert result["mode"] == "execution_rejected"
    assert result["rejection_reason"] == "workflow_instance_contract_not_implemented"


def test_changed_contracts_have_explicit_new_versions():
    names = {"valeo_agrar_settlement_list", "valeo_agrar_kampagne_list",
             "valeo_agrar_quality_protocol_approve", "valeo_finance_ap_invoice_list",
             "valeo_finance_open_items_get", "valeo_finance_dunning_run",
             "valeo_workflow_instance_status"}
    registry = get_process_kernel_mcp_tools()
    assert registry.schema_version == 1
    for name in names:
        contract = registry.by_tool_name(name)
        assert contract.schema_version == 2
        assert contract.as_mcp_tool()["_meta"]["valeo/schemaVersion"] == 2
