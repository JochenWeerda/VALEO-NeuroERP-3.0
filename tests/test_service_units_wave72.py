"""Wave 72 — Unit-Tests fuer settlement_approval_service (pure domain state machine)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# settlement_approval_service  (pure state machine — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_terminal_verbucht() -> None:
    from app.services.settlement_approval_service import is_terminal, SettlementApprovalStatus
    assert is_terminal(SettlementApprovalStatus.VERBUCHT) is True


@pytest.mark.unit
def test_is_not_terminal_abgelehnt() -> None:
    # ABGELEHNT allows transition back to ENTWURF — not a terminal state
    from app.services.settlement_approval_service import is_terminal, SettlementApprovalStatus
    assert is_terminal(SettlementApprovalStatus.ABGELEHNT) is False


@pytest.mark.unit
def test_is_not_terminal_entwurf() -> None:
    from app.services.settlement_approval_service import is_terminal, SettlementApprovalStatus
    assert is_terminal(SettlementApprovalStatus.ENTWURF) is False


@pytest.mark.unit
def test_is_not_terminal_zur_freigabe() -> None:
    from app.services.settlement_approval_service import is_terminal, SettlementApprovalStatus
    assert is_terminal(SettlementApprovalStatus.ZUR_FREIGABE) is False


@pytest.mark.unit
def test_get_allowed_transitions_entwurf() -> None:
    from app.services.settlement_approval_service import get_allowed_transitions, SettlementApprovalStatus
    transitions = get_allowed_transitions(SettlementApprovalStatus.ENTWURF)
    assert isinstance(transitions, list)
    assert len(transitions) > 0
    # ENTWURF should allow ZUR_FREIGABE
    values = [t.value for t in transitions]
    assert "ZUR_FREIGABE" in values


@pytest.mark.unit
def test_get_allowed_transitions_terminal_empty() -> None:
    from app.services.settlement_approval_service import get_allowed_transitions, SettlementApprovalStatus
    transitions = get_allowed_transitions(SettlementApprovalStatus.VERBUCHT)
    assert transitions == []


@pytest.mark.unit
def test_evaluate_settlement_approval_entwurf_to_zur_freigabe() -> None:
    from app.services.settlement_approval_service import (
        evaluate_settlement_approval, SettlementApprovalStatus,
        SettlementApprovalRequest, SettlementActorType,
    )
    req = SettlementApprovalRequest(
        settlement_id="SET-001",
        tenant_id="T001",
        actor_id="USR-001",
        actor_type=SettlementActorType.ABTEILUNGSLEITER,
        target_status=SettlementApprovalStatus.ZUR_FREIGABE,
    )
    result = evaluate_settlement_approval(req, SettlementApprovalStatus.ENTWURF)
    assert result.allowed is True
    assert result.new_status == SettlementApprovalStatus.ZUR_FREIGABE
    assert result.previous_status == SettlementApprovalStatus.ENTWURF


@pytest.mark.unit
def test_evaluate_settlement_approval_invalid_transition() -> None:
    from app.services.settlement_approval_service import (
        evaluate_settlement_approval, SettlementApprovalStatus,
        SettlementApprovalRequest, SettlementActorType,
    )
    req = SettlementApprovalRequest(
        settlement_id="SET-002",
        tenant_id="T001",
        actor_id="USR-001",
        actor_type=SettlementActorType.ABTEILUNGSLEITER,
        target_status=SettlementApprovalStatus.VERBUCHT,  # skip states
    )
    result = evaluate_settlement_approval(req, SettlementApprovalStatus.ENTWURF)
    assert result.allowed is False
    assert len(result.reason) > 0


@pytest.mark.unit
def test_evaluate_settlement_approval_result_has_actor() -> None:
    from app.services.settlement_approval_service import (
        evaluate_settlement_approval, SettlementApprovalStatus,
        SettlementApprovalRequest, SettlementActorType,
    )
    req = SettlementApprovalRequest(
        settlement_id="SET-003",
        tenant_id="T001",
        actor_id="USR-042",
        actor_type=SettlementActorType.ABTEILUNGSLEITER,
        target_status=SettlementApprovalStatus.ZUR_FREIGABE,
    )
    result = evaluate_settlement_approval(req, SettlementApprovalStatus.ENTWURF)
    assert result.actor_id == "USR-042"
    assert result.settlement_id == "SET-003"


@pytest.mark.unit
def test_evaluate_settlement_approval_has_decided_at() -> None:
    from app.services.settlement_approval_service import (
        evaluate_settlement_approval, SettlementApprovalStatus,
        SettlementApprovalRequest, SettlementActorType,
    )
    req = SettlementApprovalRequest(
        settlement_id="SET-004",
        tenant_id="T001",
        actor_id="USR-001",
        actor_type=SettlementActorType.ABTEILUNGSLEITER,
        target_status=SettlementApprovalStatus.ZUR_FREIGABE,
    )
    result = evaluate_settlement_approval(req, SettlementApprovalStatus.ENTWURF)
    assert result.decided_at is not None


@pytest.mark.unit
def test_status_enum_has_entwurf_and_verbucht() -> None:
    from app.services.settlement_approval_service import SettlementApprovalStatus
    values = [e.value for e in SettlementApprovalStatus]
    assert "ENTWURF" in values
    assert "VERBUCHT" in values
    assert "FREIGEGEBEN" in values


@pytest.mark.unit
def test_actor_type_enum_values() -> None:
    from app.services.settlement_approval_service import SettlementActorType
    values = [e.value for e in SettlementActorType]
    assert len(values) > 0
