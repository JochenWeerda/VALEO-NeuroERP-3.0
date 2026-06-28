"""Wave 98 — Unit-Tests fuer scheduler_service, sales_storno_service, vies_service,
neuro_simulation_engine, neuro_verification_engine (pure domain functions)."""

from __future__ import annotations

import asyncio
import pytest


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# scheduler_service — get_scheduler_status, execute_job_immediately
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_scheduler_status_returns_dict() -> None:
    from app.services.scheduler_service import get_scheduler_status
    result = get_scheduler_status()
    assert isinstance(result, dict)


@pytest.mark.unit
def test_get_scheduler_status_has_required_keys() -> None:
    from app.services.scheduler_service import get_scheduler_status
    result = get_scheduler_status()
    for key in ("running", "scheduler_id", "jobs", "total_jobs"):
        assert key in result


@pytest.mark.unit
def test_get_scheduler_status_total_jobs_int() -> None:
    from app.services.scheduler_service import get_scheduler_status
    result = get_scheduler_status()
    assert isinstance(result["total_jobs"], int)


@pytest.mark.unit
def test_execute_job_immediately_unknown_tag_returns_error() -> None:
    from app.services.scheduler_service import execute_job_immediately
    result = execute_job_immediately("nonexistent_job_tag_wave98")
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "error" in result


# ---------------------------------------------------------------------------
# sales_storno_service — can_storno
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_can_storno_open_status_returns_false() -> None:
    from app.services.sales_storno_service import can_storno
    ok, reason = can_storno("offen", "INV-001")
    assert isinstance(ok, bool)
    assert isinstance(reason, str)
    assert len(reason) > 0


@pytest.mark.unit
def test_can_storno_storniert_returns_false() -> None:
    from app.services.sales_storno_service import can_storno
    ok, _ = can_storno("storniert", "INV-001")
    assert ok is False


@pytest.mark.unit
def test_can_storno_none_status() -> None:
    from app.services.sales_storno_service import can_storno
    ok, reason = can_storno(None, None)
    assert isinstance(ok, bool)
    assert isinstance(reason, str)


# ---------------------------------------------------------------------------
# vies_service — validate_eu_vat  (async, graceful on network failure)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_eu_vat_returns_vies_result() -> None:
    from app.services.vies_service import validate_eu_vat, ViesResult
    result = _run(validate_eu_vat("DE123456789"))
    assert isinstance(result, ViesResult)


@pytest.mark.unit
def test_validate_eu_vat_has_required_fields() -> None:
    from app.services.vies_service import validate_eu_vat
    result = _run(validate_eu_vat("DE123456789"))
    assert hasattr(result, "valid")
    assert hasattr(result, "vat_number")
    assert hasattr(result, "country_code")


@pytest.mark.unit
def test_validate_eu_vat_preserves_vat_number() -> None:
    from app.services.vies_service import validate_eu_vat
    result = _run(validate_eu_vat("DE123456789"))
    assert result.vat_number == "DE123456789"


@pytest.mark.unit
def test_validate_eu_vat_country_code_extracted() -> None:
    from app.services.vies_service import validate_eu_vat
    result = _run(validate_eu_vat("DE123456789"))
    assert result.country_code == "DE"


# ---------------------------------------------------------------------------
# neuro_simulation_engine — simulate_dry_run, simulate_what_if, get_simulation_result
# ---------------------------------------------------------------------------

def _valid_plan():
    return {"action": "update", "entity_type": "invoice", "entity_id": "INV-WAVE98", "betrag": 1000}


@pytest.mark.unit
def test_simulate_dry_run_returns_result() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run(_valid_plan())
    assert result is not None


@pytest.mark.unit
def test_simulate_dry_run_has_run_id() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run(_valid_plan())
    assert result.run_id is not None
    assert len(result.run_id) > 0


@pytest.mark.unit
def test_simulate_dry_run_valid_plan_approved() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run(_valid_plan())
    assert result.verification_status == "approved"


@pytest.mark.unit
def test_simulate_dry_run_invalid_plan_rejected() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run
    result = simulate_dry_run({})
    assert result.verification_status == "rejected"
    assert len(result.violations) > 0


@pytest.mark.unit
def test_get_simulation_result_returns_stored_result() -> None:
    from app.services.neuro_simulation_engine import simulate_dry_run, get_simulation_result
    result = simulate_dry_run(_valid_plan())
    fetched = get_simulation_result(result.run_id)
    assert fetched is not None
    assert fetched.run_id == result.run_id


@pytest.mark.unit
def test_get_simulation_result_unknown_id_returns_none() -> None:
    from app.services.neuro_simulation_engine import get_simulation_result
    result = get_simulation_result("nonexistent-run-id-wave98")
    assert result is None


@pytest.mark.unit
def test_simulate_what_if_returns_result() -> None:
    from app.services.neuro_simulation_engine import simulate_what_if
    result = simulate_what_if(_valid_plan(), {"status": "offen", "betrag": 800})
    assert result is not None
    assert result.mode == "what_if"


@pytest.mark.unit
def test_simulate_what_if_has_side_effects_list() -> None:
    from app.services.neuro_simulation_engine import simulate_what_if
    result = simulate_what_if(_valid_plan(), {})
    assert isinstance(result.side_effects, list)


# ---------------------------------------------------------------------------
# neuro_verification_engine — check_* functions  (pure plan validators)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_check_data_integrity_empty_plan_no_violations() -> None:
    from app.services.neuro_verification_engine import check_data_integrity
    violations = check_data_integrity({})
    assert isinstance(violations, list)


@pytest.mark.unit
def test_check_preconditions_valid_plan_no_violations() -> None:
    from app.services.neuro_verification_engine import check_preconditions
    violations = check_preconditions(_valid_plan())
    assert violations == []


@pytest.mark.unit
def test_check_preconditions_missing_entity_type_has_violation() -> None:
    from app.services.neuro_verification_engine import check_preconditions
    violations = check_preconditions({"action": "update", "entity_id": "X"})
    assert len(violations) > 0


@pytest.mark.unit
def test_check_state_transition_returns_list() -> None:
    from app.services.neuro_verification_engine import check_state_transition
    violations = check_state_transition(_valid_plan())
    assert isinstance(violations, list)


@pytest.mark.unit
def test_check_cross_entity_integrity_returns_list() -> None:
    from app.services.neuro_verification_engine import check_cross_entity_integrity
    violations = check_cross_entity_integrity(_valid_plan())
    assert isinstance(violations, list)
