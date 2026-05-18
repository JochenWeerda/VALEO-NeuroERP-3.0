"""Unit tests for settlement service layer: drying + approval services.

Run with:
    pytest tests/test_settlement_services.py --no-cov -q
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_settlement(
    id: str = "settle-001",
    status: str = "draft",
    approval_status: str = "ENTWURF",
    approval_history: list | None = None,
    row_version: int = 1,
    gross_quantity_kg: float = 10_000.0,
    article_id: str | None = "WW",
    drying_snapshot: dict | None = None,
) -> MagicMock:
    s = MagicMock()
    s.id = id
    s.status = status
    s.row_version = row_version
    s.gross_quantity_kg = Decimal(str(gross_quantity_kg))
    s.article_id = article_id
    s.settlement_number = f"SET-{id}"
    s.posted_journal_ref = None
    base_drying: dict = {}
    if drying_snapshot:
        base_drying.update(drying_snapshot)
    base_drying["approval_status"] = approval_status
    base_drying["approval_history"] = approval_history or []
    s.drying_result = base_drying
    return s


# ---------------------------------------------------------------------------
# SettlementDryingService — stateless calculate_drying_costs
# ---------------------------------------------------------------------------

class TestCalculateDryingCosts:
    """Tests for the pure-math calculate_drying_costs method."""

    def test_no_moisture_excess_returns_zero(self):
        """When moisture == target, no drying cost should be incurred."""
        from app.services.settlement_drying_service import SettlementDryingService
        cost = SettlementDryingService.calculate_drying_costs(
            gross_kg=10_000.0,
            moisture_pct=14.0,
            target_pct=14.0,
            rate_eur_per_t=1.5,
        )
        assert cost == pytest.approx(0.0, abs=0.01)

    def test_cost_increases_with_moisture_delta(self):
        """Higher moisture excess → higher drying cost."""
        from app.services.settlement_drying_service import SettlementDryingService
        cost_low = SettlementDryingService.calculate_drying_costs(
            gross_kg=10_000.0,
            moisture_pct=15.0,
            target_pct=14.0,
            rate_eur_per_t=1.5,
        )
        cost_high = SettlementDryingService.calculate_drying_costs(
            gross_kg=10_000.0,
            moisture_pct=18.0,
            target_pct=14.0,
            rate_eur_per_t=1.5,
        )
        assert cost_high > cost_low

    def test_cost_scales_with_weight(self):
        """Double the weight → double the cost (linear scaling)."""
        from app.services.settlement_drying_service import SettlementDryingService
        cost_1t = SettlementDryingService.calculate_drying_costs(
            gross_kg=1_000.0,
            moisture_pct=17.0,
            target_pct=14.0,
            rate_eur_per_t=2.0,
        )
        cost_2t = SettlementDryingService.calculate_drying_costs(
            gross_kg=2_000.0,
            moisture_pct=17.0,
            target_pct=14.0,
            rate_eur_per_t=2.0,
        )
        assert cost_2t == pytest.approx(cost_1t * 2, rel=1e-4)


# ---------------------------------------------------------------------------
# SettlementDryingService — get_crop_defaults
# ---------------------------------------------------------------------------

class TestGetCropDefaults:
    def test_known_crop_returns_params(self):
        from app.services.settlement_drying_service import SettlementDryingService
        params = SettlementDryingService.get_crop_defaults("WW")
        assert params["crop_code"] == "WW"
        assert "start_threshold_pct" in params
        assert "trocknungskosten_eur_per_pct_per_t" in params

    def test_unknown_crop_returns_empty(self):
        from app.services.settlement_drying_service import SettlementDryingService
        params = SettlementDryingService.get_crop_defaults("UNICORN")
        assert params == {}


# ---------------------------------------------------------------------------
# SettlementDryingService — get_drying_summary
# ---------------------------------------------------------------------------

class TestGetDryingSummary:
    def test_returns_summary_when_snapshot_present(self):
        from app.services.settlement_drying_service import SettlementDryingService
        import app.repositories.agrar_settlement_repository as repo_mod

        snapshot = {
            "crop_code": "WW",
            "moisture_pct": 17.5,
            "invoice_weight_kg": 9800.0,
            "drying_fee_eur": 45.0,
            "used_rule_set_id": "rs-1",
            "used_rule_version": 2,
            "approval_status": "ENTWURF",  # should be excluded
        }
        settlement = _make_settlement(drying_snapshot=snapshot)

        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = settlement

        svc = SettlementDryingService.__new__(SettlementDryingService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"
        svc._drying_repo = MagicMock()

        with patch.object(repo_mod, "AgrarSettlementRepository", return_value=mock_repo_instance):
            result = svc.get_drying_summary("settle-001")

        assert result["settlement_id"] == "settle-001"
        assert result["has_drying_data"] is True
        assert result["crop_code"] == "WW"
        # approval_status must not leak into drying summary
        assert "approval_status" not in result

    def test_returns_empty_summary_when_no_snapshot(self):
        from app.services.settlement_drying_service import SettlementDryingService
        import app.repositories.agrar_settlement_repository as repo_mod

        settlement = _make_settlement()  # drying_result has only approval fields

        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = settlement

        svc = SettlementDryingService.__new__(SettlementDryingService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"
        svc._drying_repo = MagicMock()

        with patch.object(repo_mod, "AgrarSettlementRepository", return_value=mock_repo_instance):
            result = svc.get_drying_summary("settle-001")

        assert result["has_drying_data"] is False


# ---------------------------------------------------------------------------
# SettlementApprovalService — get_approval_status
# ---------------------------------------------------------------------------

class TestGetApprovalStatus:
    def test_returns_entwurf_for_new_settlement(self):
        from app.services.settlement_approval_service import SettlementApprovalService
        import app.repositories.agrar_settlement_repository as repo_mod

        settlement = _make_settlement(approval_status="ENTWURF")
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = settlement

        svc = SettlementApprovalService.__new__(SettlementApprovalService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"

        with patch.object(repo_mod, "AgrarSettlementRepository", return_value=mock_repo_instance):
            result = svc.get_approval_status("settle-001")

        assert result["approval_status"] == "ENTWURF"
        assert "ZUR_FREIGABE" in result["allowed_transitions"]
        assert result["is_terminal"] is False

    def test_verbucht_is_terminal(self):
        from app.services.settlement_approval_service import SettlementApprovalService
        import app.repositories.agrar_settlement_repository as repo_mod

        settlement = _make_settlement(approval_status="VERBUCHT")
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = settlement

        svc = SettlementApprovalService.__new__(SettlementApprovalService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"

        with patch.object(repo_mod, "AgrarSettlementRepository", return_value=mock_repo_instance):
            result = svc.get_approval_status("settle-001")

        assert result["is_terminal"] is True
        assert result["allowed_transitions"] == []


# ---------------------------------------------------------------------------
# SettlementApprovalService — reject_settlement validation
# ---------------------------------------------------------------------------

class TestRejectSettlement:
    def test_reject_requires_reason(self):
        from app.services.settlement_approval_service import SettlementApprovalService
        from app.core.exceptions import ValidationFailedError

        svc = SettlementApprovalService.__new__(SettlementApprovalService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"

        with pytest.raises(ValidationFailedError, match="Pflichtfeld"):
            svc.reject_settlement("settle-001", reason="")

    def test_reject_whitespace_reason_raises(self):
        from app.services.settlement_approval_service import SettlementApprovalService
        from app.core.exceptions import ValidationFailedError

        svc = SettlementApprovalService.__new__(SettlementApprovalService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"

        with pytest.raises(ValidationFailedError):
            svc.reject_settlement("settle-001", reason="   ")


# ---------------------------------------------------------------------------
# SettlementApprovalService — _apply_transition (row_version conflict)
# ---------------------------------------------------------------------------

class TestRowVersionConflict:
    def test_row_version_mismatch_raises_conflict(self):
        from app.services.settlement_approval_service import SettlementApprovalService
        from app.core.exceptions import ConflictError

        settlement = _make_settlement(row_version=3)

        svc = SettlementApprovalService.__new__(SettlementApprovalService)
        svc.db = MagicMock()
        svc.tenant_id = "t1"

        with pytest.raises(ConflictError, match="row_version_conflict"):
            svc._apply_transition(
                settlement,
                actor_id="u1",
                actor_type_str="SACHBEARBEITER",
                target_status_str="ZUR_FREIGABE",
                reason=None,
                expected_row_version=1,  # stale
            )


# ---------------------------------------------------------------------------
# Router import smoke test
# ---------------------------------------------------------------------------

def test_router_importable():
    """Smoke test: endpoint module must import cleanly."""
    from app.api.v1.endpoints.agrar_settlements import router
    assert router is not None
