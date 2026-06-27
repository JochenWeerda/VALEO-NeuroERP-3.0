"""Wave 80 — Unit-Tests fuer case_management (in-memory ApprovalCase lifecycle)."""

from __future__ import annotations

import pytest


def _make_requirement():
    from app.core.human_approval_gate import ApprovalAusloserTyp
    from app.services.case_management import HumanApprovalRequirement, ApprovalRisikostufe
    return HumanApprovalRequirement(
        aktions_typ="freigabe",
        risiko_stufe=ApprovalRisikostufe.MITTEL,
        requires_human_approval=True,
        ausgeloeste_regel_id="RULE-001",
        ausloser_typ=ApprovalAusloserTyp.BETRAG_SCHWELLE,
        begruendung="Betrag > 10000 EUR",
        freigabe_rolle="controller",
    )


# ---------------------------------------------------------------------------
# case_management  (pure in-memory lifecycle — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_case_returns_case() -> None:
    from app.services.case_management import create_case, ApprovalCase
    case = create_case(_make_requirement(), "INST-001", "AGENT-001", {"doc": "INV-001"})
    assert isinstance(case, ApprovalCase)
    assert case.case_id is not None


@pytest.mark.unit
def test_create_case_initial_status_open() -> None:
    from app.services.case_management import create_case, CaseStatus
    case = create_case(_make_requirement(), "INST-002", "AGENT-001", {})
    assert case.status == CaseStatus.OPEN


@pytest.mark.unit
def test_get_case_returns_created_case() -> None:
    from app.services.case_management import create_case, get_case
    case = create_case(_make_requirement(), "INST-003", "AGENT-001", {})
    fetched = get_case(case.case_id)
    assert fetched is not None
    assert fetched.case_id == case.case_id


@pytest.mark.unit
def test_get_case_unknown_id_returns_none() -> None:
    from app.services.case_management import get_case
    result = get_case("00000000-0000-0000-0000-nonexistent")
    assert result is None


@pytest.mark.unit
def test_list_cases_contains_created_case() -> None:
    from app.services.case_management import create_case, list_cases
    case = create_case(_make_requirement(), "INST-004", "AGENT-001", {})
    all_cases = list_cases()
    ids = [c.case_id for c in all_cases]
    assert case.case_id in ids


@pytest.mark.unit
def test_assign_case_updates_assignee() -> None:
    from app.services.case_management import create_case, assign_case
    case = create_case(_make_requirement(), "INST-005", "AGENT-001", {})
    updated = assign_case(case.case_id, "USR-CONTROLLER")
    assert updated is not None
    assert updated.assigned_to == "USR-CONTROLLER"


@pytest.mark.unit
def test_decide_case_approve() -> None:
    from app.services.case_management import create_case, decide_case, ApprovalDecision, CaseStatus
    case = create_case(_make_requirement(), "INST-006", "AGENT-001", {})
    result = decide_case(case.case_id, ApprovalDecision.GENEHMIGT, "USR-001", "Freigegeben nach Prüfung")
    assert result is not None
    assert result.status in (CaseStatus.CLOSED, CaseStatus.DECIDED)


@pytest.mark.unit
def test_decide_case_reject() -> None:
    from app.services.case_management import create_case, decide_case, ApprovalDecision, CaseStatus
    case = create_case(_make_requirement(), "INST-007", "AGENT-001", {})
    result = decide_case(case.case_id, ApprovalDecision.ABGELEHNT, "USR-001", "Betrag zu hoch")
    assert result is not None
    assert result.status in (CaseStatus.CLOSED, CaseStatus.DECIDED)


@pytest.mark.unit
def test_close_case_changes_status() -> None:
    from app.services.case_management import create_case, close_case, CaseStatus
    case = create_case(_make_requirement(), "INST-008", "AGENT-001", {})
    closed = close_case(case.case_id)
    assert closed is not None
    assert closed.status == CaseStatus.CLOSED


@pytest.mark.unit
def test_get_dashboard_stats_structure() -> None:
    from app.services.case_management import get_dashboard_stats
    stats = get_dashboard_stats()
    assert "total" in stats
    assert "open" in stats
    assert isinstance(stats["total"], int)


@pytest.mark.unit
def test_get_dashboard_stats_tenant_filter() -> None:
    from app.services.case_management import get_dashboard_stats
    stats = get_dashboard_stats(tenant_id="T-UNKNOWN-TENANT")
    assert isinstance(stats, dict)
    assert "total" in stats
