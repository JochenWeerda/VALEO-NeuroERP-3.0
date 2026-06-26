"""OPERATOR-AGENT-002b — DB-Persistenz für Agent-Proposals."""

from __future__ import annotations

import pytest

from app.core.database import SessionLocal, engine
from app.infrastructure.models.agent_proposal_model import AgentProposalRecord
from app.repositories.agent_proposal_repository import AgentProposalRepository
from app.services.operator_agent_service import (
    AgentActionType,
    ApprovalStatus,
    OperatorAgentService,
    ProposalNotFoundError,
)

TENANT = "tenant-agent-persist"
PROPOSE_ROLES = {"agent:read", "agent:propose"}
APPROVE_ROLES = {"agent:read", "agent:propose", "agent:approve"}


@pytest.fixture()
def persist_svc(require_db):
    AgentProposalRecord.__table__.create(bind=engine, checkfirst=True)
    db = SessionLocal()
    try:
        yield OperatorAgentService(AgentProposalRepository(db)), db
    finally:
        db.close()


def test_proposal_survives_service_restart(persist_svc) -> None:
    svc, db = persist_svc
    created = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.MAHNUNG_VORSCHLAG,
        roles=PROPOSE_ROLES,
        context_summary="Offener Betrag",
        proposed_action="Mahnstufe 1",
        rationale="30 Tage ueberfaellig",
    )
    reloaded = OperatorAgentService(AgentProposalRepository(db)).get_proposal(
        tenant_id=TENANT,
        proposal_id=created.proposal_id,
    )
    assert reloaded.context_summary == "Offener Betrag"
    assert reloaded.approval_status == ApprovalStatus.PENDING


def test_idempotency_key_returns_existing_proposal(persist_svc) -> None:
    svc, _db = persist_svc
    key = "idem-agent-001"
    first = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
        roles=PROPOSE_ROLES,
        context_summary="ctx",
        proposed_action="act",
        rationale="why",
        idempotency_key=key,
    )
    second = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
        roles=PROPOSE_ROLES,
        context_summary="ctx",
        proposed_action="act",
        rationale="why",
        idempotency_key=key,
    )
    assert first.proposal_id == second.proposal_id


def test_approve_persists_to_db(persist_svc) -> None:
    svc, db = persist_svc
    proposal = svc.create_proposal(
        tenant_id=TENANT,
        action_type=AgentActionType.RECHNUNG_VORSCHLAG,
        roles=PROPOSE_ROLES,
        context_summary="LS offen",
        proposed_action="Rechnung erstellen",
        rationale="Lieferung abgeschlossen",
    )
    svc.approve_proposal(
        tenant_id=TENANT,
        proposal_id=proposal.proposal_id,
        approved_by="max.mustermann",
        roles=APPROVE_ROLES,
    )
    reloaded = OperatorAgentService(AgentProposalRepository(db)).get_proposal(
        tenant_id=TENANT,
        proposal_id=proposal.proposal_id,
    )
    assert reloaded.approval_status == ApprovalStatus.APPROVED
    assert reloaded.approved_by == "max.mustermann"


def test_tenant_isolation_from_db(persist_svc) -> None:
    svc, db = persist_svc
    proposal = svc.create_proposal(
        tenant_id="tenant-a-persist",
        action_type=AgentActionType.OFFENE_GATES_ABFRAGE,
        roles=PROPOSE_ROLES,
        context_summary="x",
        proposed_action="y",
        rationale="z",
    )
    fresh = OperatorAgentService(AgentProposalRepository(db))
    with pytest.raises(ProposalNotFoundError):
        fresh.get_proposal(tenant_id="tenant-b-persist", proposal_id=proposal.proposal_id)
