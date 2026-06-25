"""Tests fuer OPERATOR-AGENT-001 Read-Only/Proposal-Modus."""

import pytest
from app.services.operator_agent_service import (
    AgentActionType,
    AgentRiskLevel,
    ApprovalStatus,
    OperatorAgentPermissionError,
    OperatorAgentService,
    ProposalNotFoundError,
)

TENANT = "tenant-agent-test"
READ_ROLES = {"agent:read"}
PROPOSE_ROLES = {"agent:read", "agent:propose"}
APPROVE_ROLES = {"agent:read", "agent:propose", "agent:approve"}


@pytest.fixture()
def svc() -> OperatorAgentService:
    return OperatorAgentService()


def test_read_context_requires_agent_read(svc: OperatorAgentService) -> None:
    with pytest.raises(OperatorAgentPermissionError):
        svc.read_context(tenant_id=TENANT, action_type=AgentActionType.OFFENE_GATES_ABFRAGE, roles=set())


def test_read_context_low_risk(svc: OperatorAgentService) -> None:
    result = svc.read_context(
        tenant_id=TENANT,
        action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
        roles=READ_ROLES,
    )
    assert result["risk_level"] == AgentRiskLevel.LOW.value
    assert result["human_approval_required"] is False
    assert "hinweis" in result
    assert "context" in result


def test_read_context_high_risk_needs_approval(svc: OperatorAgentService) -> None:
    result = svc.read_context(
        tenant_id=TENANT,
        action_type=AgentActionType.MAHNUNG_VORSCHLAG,
        roles=READ_ROLES,
    )
    assert result["risk_level"] == AgentRiskLevel.HIGH.value
    assert result["human_approval_required"] is True


def test_create_proposal_requires_agent_propose(svc: OperatorAgentService) -> None:
    with pytest.raises(OperatorAgentPermissionError):
        svc.create_proposal(
            tenant_id=TENANT,
            action_type=AgentActionType.MAHNUNG_VORSCHLAG,
            roles=READ_ROLES,
            context_summary="test",
            proposed_action="Mahnung versenden",
            rationale="Faellig seit 30 Tagen",
        )


def test_create_proposal_success(svc: OperatorAgentService) -> None:
    proposal = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.MAHNUNG_VORSCHLAG,
        roles=PROPOSE_ROLES,
        context_summary="Offener Betrag 1234 EUR",
        proposed_action="Mahnstufe 1 versenden",
        rationale="30 Tage ueberfaellig",
    )
    assert proposal.approval_status == ApprovalStatus.PENDING
    assert proposal.human_approval_required is True
    assert proposal.risk_level == AgentRiskLevel.HIGH
    assert len(proposal.audit_events) == 1


def test_approve_proposal(svc: OperatorAgentService) -> None:
    proposal = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.RECHNUNG_VORSCHLAG,
        roles=PROPOSE_ROLES,
        context_summary="LS offen",
        proposed_action="Rechnung erstellen",
        rationale="Lieferung abgeschlossen",
    )
    approved = svc.approve_proposal(
        tenant_id=TENANT,
        proposal_id=proposal.proposal_id,
        approved_by="max.mustermann",
        roles=APPROVE_ROLES,
    )
    assert approved.approval_status == ApprovalStatus.APPROVED
    assert approved.approved_by == "max.mustermann"
    assert len(approved.audit_events) == 2


def test_reject_proposal(svc: OperatorAgentService) -> None:
    proposal = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.QS_FREIGABE_VORSCHLAG,
        roles=PROPOSE_ROLES,
        context_summary="Lot in Pruefung",
        proposed_action="QS freigeben",
        rationale="Laborwerte ok",
    )
    rejected = svc.reject_proposal(
        tenant_id=TENANT,
        proposal_id=proposal.proposal_id,
        rejected_by="qa.manager",
        reason="Laborwerte fehlen noch",
        roles=APPROVE_ROLES,
    )
    assert rejected.approval_status == ApprovalStatus.REJECTED
    assert rejected.rejection_reason == "Laborwerte fehlen noch"


def test_approve_already_approved_raises(svc: OperatorAgentService) -> None:
    proposal = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.ANGEBOTSNACHFASSUNG,
        roles=PROPOSE_ROLES,
        context_summary="Angebot offen",
        proposed_action="Nachfassen",
        rationale="7 Tage kein Feedback",
    )
    svc.approve_proposal(tenant_id=TENANT, proposal_id=proposal.proposal_id, approved_by="a", roles=APPROVE_ROLES)
    with pytest.raises(ValueError):
        svc.approve_proposal(tenant_id=TENANT, proposal_id=proposal.proposal_id, approved_by="b", roles=APPROVE_ROLES)


def test_get_proposal_not_found(svc: OperatorAgentService) -> None:
    with pytest.raises(ProposalNotFoundError):
        svc.get_proposal(tenant_id=TENANT, proposal_id="does-not-exist")


def test_tenant_isolation(svc: OperatorAgentService) -> None:
    proposal = svc.create_proposal(
        tenant_id="tenant-a",
        action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
        roles=PROPOSE_ROLES,
        context_summary="test",
        proposed_action="test",
        rationale="test",
    )
    with pytest.raises(ProposalNotFoundError):
        svc.get_proposal(tenant_id="tenant-b", proposal_id=proposal.proposal_id)


def test_summary_structure(svc: OperatorAgentService) -> None:
    summary = svc.summary(tenant_id=TENANT)
    assert "total_proposals" in summary
    assert "by_status" in summary
    assert "pending_high_risk" in summary


def test_list_proposals_filter_by_status(svc: OperatorAgentService) -> None:
    p1 = svc.create_proposal(tenant_id=TENANT, action_type=AgentActionType.ANGEBOTSNACHFASSUNG,
                              roles=PROPOSE_ROLES, context_summary="a", proposed_action="b", rationale="c")
    svc.approve_proposal(tenant_id=TENANT, proposal_id=p1.proposal_id, approved_by="x", roles=APPROVE_ROLES)
    svc.create_proposal(tenant_id=TENANT, action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
                        roles=PROPOSE_ROLES, context_summary="a", proposed_action="b", rationale="c")
    pending = svc.list_proposals(tenant_id=TENANT, status=ApprovalStatus.PENDING)
    assert all(p.approval_status == ApprovalStatus.PENDING for p in pending)
    approved = svc.list_proposals(tenant_id=TENANT, status=ApprovalStatus.APPROVED)
    assert all(p.approval_status == ApprovalStatus.APPROVED for p in approved)
