"""Tests fuer Neuro Planner (NC-A3/A4)."""
import pytest

from app.agents.neuro_intent_engine import IntentCategory, IntentResult, RiskClass
from app.agents.neuro_planner import (
    ExecutionPlan,
    PlanStep,
    StepType,
    generate_plan,
    PLAN_TEMPLATES,
)


def _make_intent(intent: str, capability: str = None, risk: RiskClass = RiskClass.LOW) -> IntentResult:
    return IntentResult(
        intent=intent,
        category=IntentCategory.COMMAND,
        confidence_score=0.8,
        risk_class=risk,
        explanation="test",
        matched_capability=capability,
    )


class TestGeneratePlan:
    def test_bestellung_plan_has_4_steps(self):
        intent = _make_intent("bestellung_anlegen", "bestellvorschlag_assistant", RiskClass.MEDIUM)
        plan = generate_plan(intent)
        assert len(plan.steps) == 4
        assert plan.intent == "bestellung_anlegen"
        assert plan.capability == "bestellvorschlag_assistant"

    def test_bestellung_step_types(self):
        intent = _make_intent("bestellung_anlegen")
        plan = generate_plan(intent)
        types = [s.type for s in plan.steps]
        assert StepType.VALIDATION in types
        assert StepType.QUERY in types
        assert StepType.COMMAND in types
        assert StepType.NOTIFICATION in types

    def test_bestellung_has_approval_step(self):
        intent = _make_intent("bestellung_anlegen")
        plan = generate_plan(intent)
        approval_steps = [s for s in plan.steps if s.requires_approval]
        assert len(approval_steps) >= 1

    def test_bestellung_has_rollback(self):
        intent = _make_intent("bestellung_anlegen")
        plan = generate_plan(intent)
        rollback_steps = [s for s in plan.steps if s.rollback_action]
        assert len(rollback_steps) >= 1

    def test_skonto_plan(self):
        intent = _make_intent("skonto_pruefen", "finance_skonto_assistant")
        plan = generate_plan(intent)
        assert len(plan.steps) == 3

    def test_compliance_plan_has_gate(self):
        intent = _make_intent("compliance_pruefen", "compliance_copilot")
        plan = generate_plan(intent)
        gates = [s for s in plan.steps if s.type == StepType.GATE]
        assert len(gates) >= 1

    def test_lagerbestand_single_query(self):
        intent = _make_intent("lagerbestand_abfragen")
        plan = generate_plan(intent)
        assert len(plan.steps) == 1
        assert plan.steps[0].type == StepType.QUERY

    def test_unknown_intent_uses_dynamic_command_plan(self):
        intent = _make_intent("something_unknown")
        plan = generate_plan(intent)
        assert len(plan.steps) == 3
        assert plan.steps[0].action == "validate_dynamic_request"
        assert plan.steps[-1].action == "execute_dynamic_command"
        assert plan.steps[-1].parameters["_dynamic_plan"] is True

    def test_navigation_without_template_uses_dynamic_navigation_plan(self):
        intent = IntentResult(
            intent="navigation",
            category=IntentCategory.NAVIGATION,
            confidence_score=0.9,
            risk_class=RiskClass.LOW,
            explanation="test",
        )
        plan = generate_plan(intent)
        assert len(plan.steps) == 2
        assert plan.steps[0].action == "resolve_navigation_target"
        assert plan.steps[1].action == "open_navigation_target"

    def test_high_risk_requires_approval(self):
        intent = _make_intent("ausnahme_behandeln", "operations_exception_assistant", RiskClass.HIGH)
        plan = generate_plan(intent)
        assert plan.requires_human_approval is True

    def test_low_risk_no_forced_approval(self):
        intent = _make_intent("lagerbestand_abfragen", risk=RiskClass.LOW)
        plan = generate_plan(intent)
        assert plan.requires_human_approval is False

    def test_parameters_propagated(self):
        intent = _make_intent("bestellung_anlegen")
        intent.parameters = {"amount": 500.0, "currency": "EUR"}
        plan = generate_plan(intent)
        for step in plan.steps:
            assert step.parameters.get("amount") == 500.0

    def test_extra_params_merged(self):
        intent = _make_intent("bestellung_anlegen")
        plan = generate_plan(intent, context={"extra_params": {"warehouse_id": "WH-01"}})
        assert plan.steps[0].parameters.get("warehouse_id") == "WH-01"


class TestPlanStepSerialization:
    def test_to_dict(self):
        step = PlanStep(order=1, type=StepType.COMMAND, action="test", description="Test Step")
        d = step.to_dict()
        assert d["order"] == 1
        assert d["type"] == "command"
        assert d["action"] == "test"


class TestExecutionPlanSerialization:
    def test_to_dict(self):
        intent = _make_intent("bestellung_anlegen")
        plan = generate_plan(intent)
        d = plan.to_dict()
        assert "plan_id" in d
        assert "steps" in d
        assert "step_count" in d
        assert d["step_count"] == len(d["steps"])
        assert d["intent"] == "bestellung_anlegen"


class TestAllTemplatesCovered:
    @pytest.mark.parametrize("intent_name", list(PLAN_TEMPLATES.keys()))
    def test_template_produces_plan(self, intent_name):
        intent = _make_intent(intent_name)
        plan = generate_plan(intent)
        assert len(plan.steps) >= 1
        for step in plan.steps:
            assert step.action
            assert step.description
