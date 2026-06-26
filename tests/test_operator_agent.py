"""Tests fuer OPERATOR-AGENT-001 Proposal + LOW-Risiko-Execute."""

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
EXECUTE_ROLES = {"agent:read", "agent:propose", "agent:approve", "agent:execute"}


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


# ── Execute LOW-Risiko-Aktionen ────────────────────────────────────────────────

def _approved_low_risk_proposal(svc: OperatorAgentService, action: AgentActionType):
    p = svc.create_proposal(
        tenant_id=TENANT, action_type=action, roles=PROPOSE_ROLES,
        context_summary="test", proposed_action="ausfuehren", rationale="low risk",
    )
    svc.approve_proposal(tenant_id=TENANT, proposal_id=p.proposal_id,
                         approved_by="manager", roles=APPROVE_ROLES)
    return p


def test_execute_requires_agent_execute_role(svc: OperatorAgentService) -> None:
    p = _approved_low_risk_proposal(svc, AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE)
    with pytest.raises(OperatorAgentPermissionError):
        svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                    executed_by="bot", roles=APPROVE_ROLES)


def test_execute_angebot_nachfassen(svc: OperatorAgentService) -> None:
    p = _approved_low_risk_proposal(svc, AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE)
    result = svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                         executed_by="bot", roles=EXECUTE_ROLES)
    assert result["action_type"] == AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE.value
    assert "crm.angebot.nachgefasst" in result["result"]["outbox_event"]
    assert result["result"]["simulated"] is True


def test_execute_dms_paket_senden(svc: OperatorAgentService) -> None:
    p = _approved_low_risk_proposal(svc, AgentActionType.DMS_PAKET_SENDEN_EXECUTE)
    result = svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                         executed_by="bot", roles=EXECUTE_ROLES)
    assert "dms.paket.gesendet" in result["result"]["outbox_event"]


def test_execute_gate_status_aktualisieren(svc: OperatorAgentService) -> None:
    p = _approved_low_risk_proposal(svc, AgentActionType.GATE_STATUS_AKTUALISIEREN_EXECUTE)
    result = svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                         executed_by="bot", roles=EXECUTE_ROLES)
    assert "gate.status.aktualisiert" in result["result"]["outbox_event"]


def test_execute_fails_for_non_approved_proposal(svc: OperatorAgentService) -> None:
    p = svc.create_proposal(
        tenant_id=TENANT, action_type=AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE,
        roles=PROPOSE_ROLES, context_summary="x", proposed_action="y", rationale="z",
    )
    with pytest.raises(ValueError, match="APPROVED"):
        svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                    executed_by="bot", roles=EXECUTE_ROLES)


def test_execute_fails_for_high_risk_action(svc: OperatorAgentService) -> None:
    p = svc.create_proposal(
        tenant_id=TENANT, action_type=AgentActionType.MAHNUNG_VORSCHLAG,
        roles=PROPOSE_ROLES, context_summary="x", proposed_action="y", rationale="z",
    )
    svc.approve_proposal(tenant_id=TENANT, proposal_id=p.proposal_id,
                         approved_by="manager", roles=APPROVE_ROLES)
    with pytest.raises(PermissionError):
        svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                    executed_by="bot", roles=EXECUTE_ROLES)


def test_execute_writes_audit_event(svc: OperatorAgentService) -> None:
    p = _approved_low_risk_proposal(svc, AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE)
    svc.execute_approved_action(tenant_id=TENANT, proposal_id=p.proposal_id,
                                executed_by="bot", roles=EXECUTE_ROLES)
    events = [e["event"] for e in p.audit_events]
    assert "action_executed" in events


def test_new_low_risk_action_types_have_correct_risk() -> None:
    from app.services.operator_agent_service import _RISK_BY_ACTION, AgentRiskLevel
    assert _RISK_BY_ACTION[AgentActionType.ANGEBOT_NACHFASSEN_EXECUTE] == AgentRiskLevel.LOW
    assert _RISK_BY_ACTION[AgentActionType.DMS_PAKET_SENDEN_EXECUTE] == AgentRiskLevel.LOW
    assert _RISK_BY_ACTION[AgentActionType.GATE_STATUS_AKTUALISIEREN_EXECUTE] == AgentRiskLevel.LOW
