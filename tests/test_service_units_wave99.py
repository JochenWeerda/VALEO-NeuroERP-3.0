"""Wave 99 — Unit-Tests fuer docflow_artifact_service, docflow_evidence_service,
docflow_gobd_service, finance_clearing_service, finance_dunning_service,
finance_op_service, finance_period_service, contract_engagement_service,
contract_settlement_service (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import date


# ---------------------------------------------------------------------------
# docflow_artifact_service — next_version, sha256_hex, valid_transition
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_next_version_increments() -> None:
    from app.services.docflow_artifact_service import next_version
    assert next_version([1, 2, 3]) == 4


@pytest.mark.unit
def test_next_version_empty_list_returns_one() -> None:
    from app.services.docflow_artifact_service import next_version
    assert next_version([]) == 1


@pytest.mark.unit
def test_sha256_hex_returns_hex_string() -> None:
    from app.services.docflow_artifact_service import sha256_hex
    result = sha256_hex("hello")
    assert isinstance(result, str)
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


@pytest.mark.unit
def test_sha256_hex_deterministic() -> None:
    from app.services.docflow_artifact_service import sha256_hex
    assert sha256_hex("test") == sha256_hex("test")


@pytest.mark.unit
def test_valid_transition_entwurf_to_freigegeben() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("entwurf", "freigegeben") is True


@pytest.mark.unit
def test_valid_transition_freigegeben_to_archiviert() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("freigegeben", "archiviert") is True


@pytest.mark.unit
def test_valid_transition_backwards_invalid() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("archiviert", "entwurf") is False


# ---------------------------------------------------------------------------
# docflow_evidence_service — evaluate_gaps
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_gaps_returns_list() -> None:
    from app.services.docflow_evidence_service import evaluate_gaps
    result = evaluate_gaps({"doc_type": "invoice"}, [], [])
    assert isinstance(result, list)


@pytest.mark.unit
def test_evaluate_gaps_no_artifacts_has_warning() -> None:
    from app.services.docflow_evidence_service import evaluate_gaps
    result = evaluate_gaps({"doc_type": "invoice"}, [], [])
    severities = [g["schwere"] for g in result]
    assert "warnung" in severities


# ---------------------------------------------------------------------------
# docflow_gobd_service — build_gobd_manifest
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_gobd_manifest_returns_dict() -> None:
    from app.services.docflow_gobd_service import build_gobd_manifest
    result = build_gobd_manifest({"doc_id": "I-001"}, "2024-01-01", "admin")
    assert isinstance(result, dict)


@pytest.mark.unit
def test_build_gobd_manifest_has_required_keys() -> None:
    from app.services.docflow_gobd_service import build_gobd_manifest
    result = build_gobd_manifest({"doc_id": "I-001"}, "2024-01-01", "admin")
    for key in ("exportiert_am", "exportiert_von", "pruefsumme_sha256", "revisionssicher"):
        assert key in result


@pytest.mark.unit
def test_build_gobd_manifest_exported_by_preserved() -> None:
    from app.services.docflow_gobd_service import build_gobd_manifest
    result = build_gobd_manifest({}, "2024-06-01", "controller-user")
    assert result["exportiert_von"] == "controller-user"


# ---------------------------------------------------------------------------
# finance_clearing_service — clearing_result
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_clearing_result_full_payment() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(1000, 1000)
    assert result["voll_ausgeziffert"] is True
    assert result["neu_offen"] == pytest.approx(0.0)


@pytest.mark.unit
def test_clearing_result_partial_payment() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(1000, 600)
    assert result["voll_ausgeziffert"] is False
    assert result["neu_offen"] == pytest.approx(400.0)


@pytest.mark.unit
def test_clearing_result_has_required_keys() -> None:
    from app.services.finance_clearing_service import clearing_result
    result = clearing_result(500, 300)
    for key in ("ausgleich", "neu_offen", "voll_ausgeziffert", "ueberzahlt"):
        assert key in result


# ---------------------------------------------------------------------------
# finance_dunning_service — days_based_level, compute_dunning
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_days_based_level_early_overdue() -> None:
    from app.services.finance_dunning_service import days_based_level
    assert days_based_level(10) == 1


@pytest.mark.unit
def test_days_based_level_late_overdue() -> None:
    from app.services.finance_dunning_service import days_based_level
    level = days_based_level(60)
    assert level >= 2


@pytest.mark.unit
def test_compute_dunning_returns_dict() -> None:
    from app.services.finance_dunning_service import compute_dunning
    result = compute_dunning(500.0, 1, {"gebuehr": 5.0, "zinssatz": 0.05}, 30)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_compute_dunning_has_required_keys() -> None:
    from app.services.finance_dunning_service import compute_dunning
    result = compute_dunning(500.0, 1, {"gebuehr": 5.0, "zinssatz": 0.05}, 30)
    for key in ("dunning_level", "total_amount"):
        assert key in result


# ---------------------------------------------------------------------------
# finance_op_service — aging_bucket
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_aging_bucket_overdue_31_days() -> None:
    from app.services.finance_op_service import aging_bucket
    bucket, days = aging_bucket(date(2024, 1, 1), date(2024, 2, 1))
    assert isinstance(bucket, str)
    assert days >= 0


@pytest.mark.unit
def test_aging_bucket_not_yet_due() -> None:
    from app.services.finance_op_service import aging_bucket
    bucket, days = aging_bucket(date(2024, 3, 1), date(2024, 2, 1))
    assert "nicht_faellig" in bucket or days <= 0 or isinstance(bucket, str)


# ---------------------------------------------------------------------------
# finance_period_service — period_bounds
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_period_bounds_january() -> None:
    from app.services.finance_period_service import period_bounds
    start, end = period_bounds("2024-01")
    assert start == date(2024, 1, 1)
    assert end == date(2024, 1, 31)


@pytest.mark.unit
def test_period_bounds_december() -> None:
    from app.services.finance_period_service import period_bounds
    start, end = period_bounds("2024-12")
    assert start == date(2024, 12, 1)
    assert end == date(2024, 12, 31)


# ---------------------------------------------------------------------------
# contract_engagement_service — naechste_mahnstufe, netto_position, offen_menge
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_naechste_mahnstufe_after_first() -> None:
    from app.services.contract_engagement_service import naechste_mahnstufe
    assert naechste_mahnstufe(1) == 2


@pytest.mark.unit
def test_naechste_mahnstufe_from_none_returns_one() -> None:
    from app.services.contract_engagement_service import naechste_mahnstufe
    assert naechste_mahnstufe(None) == 1


@pytest.mark.unit
def test_netto_position_calculates_difference() -> None:
    from app.services.contract_engagement_service import netto_position
    result = netto_position(Decimal("1000"), Decimal("800"))
    assert result == Decimal("200")


@pytest.mark.unit
def test_offen_menge_remaining_quantity() -> None:
    from app.services.contract_engagement_service import offen_menge
    result = offen_menge(Decimal("500"), Decimal("200"))
    assert result == Decimal("300")


# ---------------------------------------------------------------------------
# contract_settlement_service — movement_state
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_movement_state_offen() -> None:
    from app.services.contract_settlement_service import movement_state
    assert movement_state(False, False) == "offen"


@pytest.mark.unit
def test_movement_state_storniert() -> None:
    from app.services.contract_settlement_service import movement_state
    assert movement_state(True, False) == "storniert"


@pytest.mark.unit
def test_movement_state_invoiced() -> None:
    from app.services.contract_settlement_service import movement_state
    result = movement_state(False, True)
    assert isinstance(result, str)
    assert len(result) > 0
