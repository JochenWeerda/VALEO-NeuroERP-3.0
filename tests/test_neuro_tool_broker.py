"""Tests for Neuro Tool Broker (NC-A6)."""

from app.agents.neuro_intent_engine import IntentCategory, IntentResult, RiskClass
from app.agents.neuro_planner import ExecutionPlan, PlanStep, StepType, generate_plan
from app.services.neuro_tool_broker import NeuroToolBroker


def _make_intent(intent: str, capability: str | None = None, risk: RiskClass = RiskClass.LOW) -> IntentResult:
    return IntentResult(
        intent=intent,
        category=IntentCategory.COMMAND,
        confidence_score=0.8,
        risk_class=risk,
        explanation="test",
        matched_capability=capability,
    )


def test_inventory_query_uses_mcp_tool_contract():
    broker = NeuroToolBroker()
    plan = generate_plan(_make_intent("lagerbestand_abfragen"))

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "executed"
    assert result["tool_trace"][0]["binding_kind"] == "mcp_tool"
    assert result["tool_trace"][0]["binding_target"] == "valeo_inventory_bestand_get"
    assert result["tool_trace"][0]["status"] == "executed"


def test_purchase_order_plan_stops_at_approval_step():
    broker = NeuroToolBroker()
    plan = generate_plan(_make_intent("bestellung_anlegen", "bestellvorschlag_assistant", RiskClass.MEDIUM))

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "awaiting_approval"
    assert result["executed_steps"][0]["status"] == "executed"
    assert result["executed_steps"][1]["status"] == "executed"
    assert result["executed_steps"][2]["status"] == "pending_approval"
    assert result["tool_trace"][2]["approval_required"] is True


def test_command_binding_uses_action_execution_service():
    broker = NeuroToolBroker()
    plan = ExecutionPlan(
        intent="bestellung_anlegen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.COMMAND,
                action="create_purchase_order",
                description="Bestellung anlegen",
                entity_type="purchase_order",
                parameters={"aggregate_id": "PO-1", "approval_status": "approved"},
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "executed"
    assert result["tool_trace"][0]["binding_kind"] == "command"
    assert result["tool_trace"][0]["result"]["status"] == "accepted"


def test_state_transition_summary_is_built_from_context():
    broker = NeuroToolBroker()
    plan = ExecutionPlan(
        intent="rechnung_erstellen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.COMMAND,
                action="create_invoice",
                description="Rechnung erstellen",
                entity_type="invoice",
            )
        ],
    )

    result = broker.execute_plan(
        plan,
        tenant_id="t1",
        context={
            "channel": "api",
            "state_graph_node": {
                "node_id": "invoice-1",
                "node_type": "rechnung",
                "current_phase": "entwurf",
                "aggregate_id": "INV-1",
                "aggregate_type": "invoice",
                "label": "Rechnung INV-1",
            },
        },
    )

    assert result["state_summary"]["transition_count"] == 1
    transition = result["state_summary"]["transitions"][0]
    assert transition["from_phase"] == "entwurf"
    assert transition["to_phase"] == "offen"
