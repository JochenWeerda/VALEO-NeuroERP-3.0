"""Wave 68 — Unit-Tests fuer neuro_verification_engine und neuro_simulation_engine (pure logic)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# neuro_verification_engine  (pure checks — keine DB required fuer die meisten)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_check_data_integrity_empty_plan() -> None:
    from app.services.neuro_verification_engine import check_data_integrity
    violations = check_data_integrity({"plan_steps": []})
    assert violations == []


@pytest.mark.unit
def test_check_preconditions_valid_plan() -> None:
    from app.services.neuro_verification_engine import check_preconditions
    plan = {"action": "create", "entity_type": "order", "plan_steps": []}
    violations = check_preconditions(plan)
    assert violations == []


@pytest.mark.unit
def test_check_preconditions_missing_action() -> None:
    from app.services.neuro_verification_engine import check_preconditions, ViolationType
    violations = check_preconditions({"requires_auth": True, "auth_token": None})
    types = [v.type for v in violations]
    assert ViolationType.PRECONDITION_FAILED in types


@pytest.mark.unit
def test_check_preconditions_missing_entity_type() -> None:
    from app.services.neuro_verification_engine import check_preconditions, ViolationType
    violations = check_preconditions({"action": "update"})
    types = [v.type for v in violations]
    assert ViolationType.PRECONDITION_FAILED in types


@pytest.mark.unit
def test_check_state_transition_no_constraints() -> None:
    from app.services.neuro_verification_engine import check_state_transition
    # If no allowed_transitions dict, no violations
    violations = check_state_transition({"from_state": "draft", "to_state": "submitted"})
    assert violations == []


@pytest.mark.unit
def test_check_cross_entity_integrity_empty() -> None:
    from app.services.neuro_verification_engine import check_cross_entity_integrity
    violations = check_cross_entity_integrity({"entities": []})
    assert violations == []


@pytest.mark.unit
def test_violation_dataclass_fields() -> None:
    from app.services.neuro_verification_engine import Violation, ViolationType
    v = Violation(
        type=ViolationType.PRECONDITION_FAILED,
        message="test violation",
        field="field_x",
        severity="error",
    )
    assert v.type == ViolationType.PRECONDITION_FAILED
    assert v.severity == "error"
    assert v.field == "field_x"


@pytest.mark.unit
def test_violation_type_enum_values() -> None:
    from app.services.neuro_verification_engine import ViolationType
    # Enum should contain standard violation types
    members = [e.value for e in ViolationType]
    assert "precondition_failed" in members


# ---------------------------------------------------------------------------
# neuro_simulation_engine  (pure simulation — keine DB)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_simulate_dry_run_basic() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run, SimulationResult
    plan = {"action": "create_order", "entity_type": "order"}
    result = simulate_dry_run(plan, tenant_id="T001")
    assert isinstance(result, SimulationResult)
    assert result.run_id is not None
    assert result.mode == "dry_run"


@pytest.mark.unit
def test_simulate_dry_run_verification_status() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    plan = {"action": "create_order", "entity_type": "order", "plan_steps": []}
    result = simulate_dry_run(plan)
    assert result.verification_status in ("approved", "rejected", "pending", "warnings")


@pytest.mark.unit
def test_simulate_dry_run_has_recommendation() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run({"action": "test"})
    assert isinstance(result.recommendation, str)
    assert len(result.recommendation) > 0


@pytest.mark.unit
def test_simulate_what_if_returns_result() -> None:
    from app.services.neuro_simulation_engine import simulate_what_if, SimulationResult
    plan = {"action": "approve", "entity_type": "order", "entity_id": "ORD-001"}
    current_state = {"status": "draft", "total": 5000.0}
    result = simulate_what_if(plan, current_state, tenant_id="T001")
    assert isinstance(result, SimulationResult)


@pytest.mark.unit
def test_simulation_result_has_run_id() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    r1 = simulate_dry_run({"action": "a"})
    r2 = simulate_dry_run({"action": "b"})
    # Each run gets a unique ID
    assert r1.run_id != r2.run_id


@pytest.mark.unit
def test_simulation_result_completed_at() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run({"action": "test"})
    assert result.completed_at is not None
    assert "T" in result.completed_at  # ISO timestamp
