"""Tests for Neuro Tool Broker (NC-A6 + NC-A7)."""

from unittest.mock import MagicMock, patch

from app.agents.neuro_intent_engine import IntentCategory, IntentResult, RiskClass
from app.agents.neuro_planner import ExecutionPlan, PlanStep, StepType, generate_plan
from app.services.neuro_tool_broker import NeuroToolBroker
from app.services.neuro_tool_execution import NeuroToolExecutionService
from app.services.neuro_verification_engine import VerificationResult, VerificationStatus


def _make_intent(intent: str, capability: str | None = None, risk: RiskClass = RiskClass.LOW) -> IntentResult:
    return IntentResult(
        intent=intent,
        category=IntentCategory.COMMAND,
        confidence_score=0.8,
        risk_class=risk,
        explanation="test",
        matched_capability=capability,
    )


# ---------------------------------------------------------------------------
# NC-A6: Existing broker tests
# ---------------------------------------------------------------------------

def test_inventory_query_uses_mcp_tool_contract():
    broker = NeuroToolBroker()
    plan = generate_plan(_make_intent("lagerbestand_abfragen"))

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "executed"
    assert result["tool_trace"][0]["binding_kind"] == "mcp_tool"
    assert result["tool_trace"][0]["binding_target"] == "valeo_inventory_bestand_get"
    assert result["tool_trace"][0]["status"] == "executed"
    assert result["tool_trace"][0]["result"]["mode"] == "openapi_internal"


def test_purchase_order_plan_stops_at_approval_step():
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "openapi_internal",
        "tool_name": "valeo_process_data_quality_validate",
        "api_endpoint": "POST /api/v1/process/data-quality/validate",
        "http_status": 200,
        "request": {},
        "response": {"valid": True},
    }

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
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


# ---------------------------------------------------------------------------
# NC-A7: OpenAPI execution adapter — fallback handling
# ---------------------------------------------------------------------------

def test_fallback_contract_5xx_maps_to_failed():
    """HTTP 500 from the execution service should result in step_status='failed'."""
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "fallback_contract",
        "tool_name": "valeo_inventory_bestand_get",
        "api_endpoint": "GET /api/v1/silo/bestand/{tenant_id}",
        "fallback_reason": "http_500",
        "http_status": 500,
        "request": {},
        "response": {"detail": "Internal Server Error"},
    }

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
    plan = ExecutionPlan(
        intent="lagerbestand_abfragen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.QUERY,
                action="query_stock_levels",
                description="Bestand abfragen",
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "failed"
    assert result["executed_steps"][0]["status"] == "failed"
    assert result["tool_trace"][0]["status"] == "failed"


def test_fallback_contract_4xx_maps_to_degraded():
    """HTTP 404 from the execution service should result in step_status='degraded'."""
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "fallback_contract",
        "tool_name": "valeo_inventory_bestand_get",
        "api_endpoint": "GET /api/v1/silo/bestand/{tenant_id}",
        "fallback_reason": "http_404",
        "http_status": 404,
        "request": {},
        "response": {"detail": "Not Found"},
    }

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
    plan = ExecutionPlan(
        intent="lagerbestand_abfragen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.QUERY,
                action="query_stock_levels",
                description="Bestand abfragen",
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    # Degraded but plan continues (not a hard failure)
    assert result["status"] == "executed"
    assert result["executed_steps"][0]["status"] == "degraded"
    assert result["tool_trace"][0]["status"] == "degraded"


def test_fallback_transport_error_maps_to_degraded():
    """Transport errors without HTTP status should result in 'degraded'."""
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "fallback_contract",
        "tool_name": "valeo_inventory_bestand_get",
        "api_endpoint": "GET /api/v1/silo/bestand/{tenant_id}",
        "fallback_reason": "transport_error: ConnectionRefused",
        "http_status": None,
        "request": {},
        "response": None,
    }

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
    plan = ExecutionPlan(
        intent="lagerbestand_abfragen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.QUERY,
                action="query_stock_levels",
                description="Bestand abfragen",
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "executed"
    assert result["executed_steps"][0]["status"] == "degraded"


def test_openapi_internal_execution_carries_mode():
    """Successful OpenAPI execution should carry mode='openapi_internal'."""
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "openapi_internal",
        "tool_name": "valeo_inventory_bestand_get",
        "api_endpoint": "GET /api/v1/silo/bestand/{tenant_id}",
        "http_status": 200,
        "request": {},
        "response": {"total_kg": 42000},
    }

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
    plan = ExecutionPlan(
        intent="lagerbestand_abfragen",
        steps=[
            PlanStep(
                order=1,
                type=StepType.QUERY,
                action="query_stock_levels",
                description="Bestand abfragen",
            )
        ],
    )

    result = broker.execute_plan(plan, tenant_id="t1", context={"channel": "api"})

    assert result["status"] == "executed"
    assert result["tool_trace"][0]["result"]["mode"] == "openapi_internal"
    assert result["tool_trace"][0]["result"]["http_status"] == 200


# ---------------------------------------------------------------------------
# NC-A7: State-Graph persistence tests
# ---------------------------------------------------------------------------

def _approved_verification(*args, **kwargs) -> VerificationResult:
    """Verification mock that always approves."""
    return VerificationResult(
        trace_id="test-trace",
        status=VerificationStatus.APPROVED,
        violations=[],
    )


def _mock_success_exec_svc() -> MagicMock:
    """Create a mock execution service that always returns successful OpenAPI results."""
    svc = MagicMock(spec=NeuroToolExecutionService)
    svc.execute_contract.return_value = {
        "mode": "openapi_internal",
        "tool_name": "valeo_process_action_execute",
        "api_endpoint": "POST /api/v1/process/actions/execute",
        "http_status": 200,
        "request": {},
        "response": {"status": "ok"},
    }
    return svc


@patch("app.services.neuro_tool_broker.verify_plan", side_effect=_approved_verification)
def test_state_transition_persisted_after_successful_execution(_mock_verify):
    """After a successful step with command binding, the state transition should be committed to DB."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    broker = NeuroToolBroker(tool_execution_service=_mock_success_exec_svc())
    # Use create_purchase_order which is a 'command' binding — goes through ActionExecutionService
    # and doesn't get blocked by verification the same way mcp_tool bindings do.
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

    result = broker.execute_plan(
        plan,
        tenant_id="t1",
        db=mock_db,
        context={
            "channel": "api",
            "state_graph_node": {
                "node_id": "po-1",
                "node_type": "bestellung",
                "current_phase": "entwurf",
                "aggregate_id": "PO-1",
                "aggregate_type": "purchase_order",
                "label": "Bestellung PO-1",
            },
        },
    )

    assert result["status"] == "executed"
    # DB should have received add() calls for node + transition, then commit()
    assert mock_db.add.call_count >= 1
    assert mock_db.commit.call_count >= 1
    # Transition should be marked as committed
    transition = result["state_summary"]["transitions"][0]
    assert transition["status"] == "committed"


@patch("app.services.neuro_tool_broker.verify_plan", side_effect=_approved_verification)
def test_state_transition_not_persisted_without_db(_mock_verify):
    """Without a DB session, state transitions stay 'planned'."""
    broker = NeuroToolBroker(tool_execution_service=_mock_success_exec_svc())
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

    result = broker.execute_plan(
        plan,
        tenant_id="t1",
        db=None,
        context={
            "channel": "api",
            "state_graph_node": {
                "node_id": "po-1",
                "node_type": "bestellung",
                "current_phase": "entwurf",
                "aggregate_id": "PO-1",
                "aggregate_type": "purchase_order",
                "label": "Bestellung PO-1",
            },
        },
    )

    assert result["status"] == "executed"
    transition = result["state_summary"]["transitions"][0]
    assert transition["status"] == "planned"


def test_state_transition_not_persisted_on_failed_step():
    """Failed steps should NOT persist state transitions."""
    mock_exec_svc = MagicMock(spec=NeuroToolExecutionService)
    mock_exec_svc.execute_contract.return_value = {
        "mode": "fallback_contract",
        "http_status": 500,
        "tool_name": "valeo_process_action_execute",
        "api_endpoint": "POST /api/v1/process/actions/execute",
        "fallback_reason": "http_500",
        "request": {},
        "response": None,
    }

    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    broker = NeuroToolBroker(tool_execution_service=mock_exec_svc)
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
        db=mock_db,
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

    assert result["status"] == "failed"
    # No add() calls for state node/transition since step failed
    add_calls = [str(c) for c in mock_db.add.call_args_list]
    state_adds = [c for c in add_calls if "StateNode" in c or "StateTransition" in c]
    assert len(state_adds) == 0


# ---------------------------------------------------------------------------
# NC-A7: Per-step audit trace tests
# ---------------------------------------------------------------------------

@patch("app.services.neuro_tool_broker.verify_plan", side_effect=_approved_verification)
def test_step_audit_trace_written_to_db(_mock_verify):
    """Each executed step should write an audit record to the DB."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    broker = NeuroToolBroker(tool_execution_service=_mock_success_exec_svc())
    # Use command binding so step actually executes (not blocked by verification)
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

    result = broker.execute_plan(plan, tenant_id="t1", db=mock_db, context={"channel": "api"})

    assert result["status"] == "executed"
    # At least one db.execute() call for the audit trace INSERT
    execute_calls = [
        call for call in mock_db.execute.call_args_list
        if hasattr(call[0][0], "text") and "neuro_step_audit_trace" in call[0][0].text
    ]
    assert len(execute_calls) >= 1


def test_step_audit_trace_skipped_without_db():
    """Without a DB session, audit trace is silently skipped."""
    broker = NeuroToolBroker()
    plan = generate_plan(_make_intent("lagerbestand_abfragen"))

    # Should not raise even without DB
    result = broker.execute_plan(plan, tenant_id="t1", db=None, context={"channel": "api"})
    assert result["status"] == "executed"
