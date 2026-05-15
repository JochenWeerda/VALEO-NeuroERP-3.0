"""Unit tests for AgrarSettlementService (no DB required)."""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import ConflictError, ValidationFailedError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(db=None, tenant_id="t1"):
    from app.services.agrar_settlement_service import AgrarSettlementService
    db = db or MagicMock()
    svc = AgrarSettlementService(db, tenant_id)
    return svc, db


# ---------------------------------------------------------------------------
# compute_amounts
# ---------------------------------------------------------------------------

def test_compute_amounts_basic():
    from app.services.agrar_settlement_service import AgrarSettlementService

    class FakeDeduction:
        deduction_type = "freight"
        mode = "fixed"
        rate_per_ton_eur = None
        fixed_amount_eur = Decimal("50")
        basis_quantity_tons = None

    result = AgrarSettlementService.compute_amounts(
        billing_quantity_kg=Decimal("10000"),
        unit_price_eur_per_ton=Decimal("200"),
        deductions=[FakeDeduction()],
    )
    assert result["gross_amount"] == Decimal("2000.00")
    assert result["total_deductions"] == Decimal("50.00")
    assert result["net_amount"] == Decimal("1950.00")


def test_compute_amounts_raises_if_deductions_exceed_gross():
    from app.services.agrar_settlement_service import AgrarSettlementService

    class FakeDeduction:
        deduction_type = "freight"
        mode = "fixed"
        rate_per_ton_eur = None
        fixed_amount_eur = Decimal("9999")
        basis_quantity_tons = None

    with pytest.raises(ValidationFailedError):
        AgrarSettlementService.compute_amounts(
            billing_quantity_kg=Decimal("1000"),
            unit_price_eur_per_ton=Decimal("10"),
            deductions=[FakeDeduction()],
        )


# ---------------------------------------------------------------------------
# get_approval_status
# ---------------------------------------------------------------------------

def test_get_approval_status_from_drying_result():
    from app.services.agrar_settlement_service import AgrarSettlementService

    s = MagicMock()
    s.drying_result = {"approval_status": "FREIGEGEBEN"}
    s.approval_metadata = {}
    assert AgrarSettlementService.get_approval_status(s) == "FREIGEGEBEN"


def test_get_approval_status_fallback_to_metadata():
    from app.services.agrar_settlement_service import AgrarSettlementService

    s = MagicMock()
    s.drying_result = {}
    s.approval_metadata = {"status": "OFFEN"}
    assert AgrarSettlementService.get_approval_status(s) == "OFFEN"


def test_get_approval_status_default():
    from app.services.agrar_settlement_service import AgrarSettlementService

    s = MagicMock()
    s.drying_result = {}
    s.approval_metadata = {}
    assert AgrarSettlementService.get_approval_status(s) == "ENTWURF"


# ---------------------------------------------------------------------------
# get_allowed_transitions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status,expected", [
    ("OFFEN", ["FREIGEGEBEN", "ABGELEHNT"]),
    ("FREIGEGEBEN", ["VERBUCHT"]),
    ("ABGELEHNT", ["OFFEN"]),
    ("VERBUCHT", []),
    ("UNKNOWN", []),
])
def test_get_allowed_transitions(status, expected):
    from app.services.agrar_settlement_service import AgrarSettlementService
    assert AgrarSettlementService.get_allowed_transitions(status) == expected


# ---------------------------------------------------------------------------
# check_row_version
# ---------------------------------------------------------------------------

def test_check_row_version_passes_when_none():
    svc, _ = _make_service()
    s = MagicMock()
    s.row_version = 3
    svc.check_row_version(s, None)  # no raise


def test_check_row_version_passes_when_matching():
    svc, _ = _make_service()
    s = MagicMock()
    s.row_version = 3
    svc.check_row_version(s, 3)  # no raise


def test_check_row_version_raises_on_mismatch():
    svc, _ = _make_service()
    s = MagicMock()
    s.row_version = 5
    with pytest.raises(ConflictError):
        svc.check_row_version(s, 3)


# ---------------------------------------------------------------------------
# cancel_settlement
# ---------------------------------------------------------------------------

def test_cancel_settlement_already_cancelled():
    svc, _ = _make_service()
    s = MagicMock()
    s.status = "cancelled"
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    with pytest.raises(ConflictError):
        svc.cancel_settlement("s1")


def test_cancel_settlement_posted_raises():
    svc, _ = _make_service()
    s = MagicMock()
    s.status = "posted"
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    with pytest.raises(ValidationFailedError):
        svc.cancel_settlement("s1")


def test_cancel_settlement_success():
    svc, db = _make_service()
    s = MagicMock()
    s.status = "draft"
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    result = svc.cancel_settlement("s1", reason="test reason")
    assert s.status == "cancelled"
    assert "[STORNO]" in s.note
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# post_to_fibu
# ---------------------------------------------------------------------------

def test_post_to_fibu_rejects_non_draft():
    svc, _ = _make_service()
    s = MagicMock()
    s.status = "posted"
    s.drying_result = {"approval_status": "FREIGEGEBEN"}
    s.approval_metadata = {}
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    with pytest.raises(ValidationFailedError):
        svc.post_to_fibu("s1", journal_ref="J-001")


def test_post_to_fibu_rejects_unapproved():
    svc, _ = _make_service()
    s = MagicMock()
    s.status = "draft"
    s.drying_result = {"approval_status": "OFFEN"}
    s.approval_metadata = {}
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    with pytest.raises(ValidationFailedError):
        svc.post_to_fibu("s1", journal_ref="J-001")


def test_post_to_fibu_success():
    svc, db = _make_service()
    s = MagicMock()
    s.status = "draft"
    s.drying_result = {"approval_status": "FREIGEGEBEN"}
    s.approval_metadata = {}
    s.id = "s1"
    svc.repo = MagicMock()
    svc.repo.get_by_id.return_value = s
    result = svc.post_to_fibu("s1", journal_ref="J-001")
    assert s.status == "posted"
    assert s.posted_journal_ref == "J-001"
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# build_correction_options
# ---------------------------------------------------------------------------

def test_build_correction_options_only_for_posted():
    from app.services.agrar_settlement_service import AgrarSettlementService
    s = MagicMock()
    s.status = "draft"
    assert AgrarSettlementService.build_correction_options(s, "VERBUCHT") == []


def test_build_correction_options_posted():
    from app.services.agrar_settlement_service import AgrarSettlementService
    s = MagicMock()
    s.status = "posted"
    s.settlement_number = "SET-001"
    s.posted_journal_ref = "J-001"
    options = AgrarSettlementService.build_correction_options(s, "VERBUCHT")
    assert len(options) == 3
    types = {o["memo_type"] for o in options}
    assert types == {"credit", "debit", "rework"}
