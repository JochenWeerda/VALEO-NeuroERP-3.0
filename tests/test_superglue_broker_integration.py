import httpx

from app.agents.neuro_planner import ExecutionPlan, PlanStep, RiskClass, StepType
from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.services.superglue_capability_service import SuperglueCapabilityService
from app.integrations.services.superglue_execution_service import SuperglueExecutionService
from app.services.neuro_tool_broker import NeuroToolBroker


def test_neuro_tool_broker_executes_superglue_step():
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "runId": "run-1",
                    "status": "completed",
                    "data": {"ok": True, "tool": "sg.document.search"},
                },
            )
        ),
    )
    broker = NeuroToolBroker(
        superglue_capability_service=SuperglueCapabilityService(
            execution_service=SuperglueExecutionService(client=client)
        )
    )
    plan = ExecutionPlan(
        plan_id="plan-1",
        capability="superglue.document.search",
        intent="lookup",
        risk_class=RiskClass.LOW,
        steps=[
            PlanStep(
                step_id="step-1",
                order=1,
                type=StepType.QUERY,
                action="superglue_search",
                description="Lookup document",
                parameters={
                    "provider_key": "superglue",
                    "superglue_tool_id": "sg.document.search",
                    "superglue_target_kind": "document",
                    "superglue_execution_mode": "read",
                    "query": "contract 4711",
                },
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="tenant-a")

    assert result["status"] == "executed"
    assert result["tool_trace"][0]["binding_kind"] == "superglue"
    assert result["tool_trace"][0]["result"]["provider_key"] == "superglue"
