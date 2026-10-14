from dataclasses import replace
from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from app.core.database import engine
from app.repositories.agent_proposal_repository import AgentProposalRepository
from app.infrastructure.models.agent_proposal_model import AgentProposalRecord
from app.services.operator_agent_service import AgentProposal, AgentActionType, AgentRiskLevel


@pytest.fixture
def repository(require_db):
    assert engine.url.database == 'valeo_probe' or 'test' in engine.url.database.lower()
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode='create_savepoint') as session:
            yield AgentProposalRepository(session), session
        transaction.rollback()


def proposal():
    return AgentProposal(str(uuid4()), 'tenant-a', AgentActionType.MAHNUNG_VORSCHLAG,
                         AgentRiskLevel.MEDIUM, True, 'Original', 'Vorschlag', 'Grund')


def test_foreign_save_cannot_change_existing_proposal(repository):
    repo, session = repository
    original = proposal()
    repo.save('tenant-a', original)
    attack = replace(original, tenant_id='tenant-b', context_summary='Fremde Aenderung')
    with pytest.raises(ValueError, match='proposal_nicht_gefunden'):
        repo.save('tenant-b', attack)
    session.expire_all()
    row = session.get(AgentProposalRecord, original.proposal_id)
    assert row.tenant_id == 'tenant-a'
    assert row.context_snapshot['context_summary'] == 'Original'
    assert row.reviewed_by is None


def test_proposal_tenant_must_match_call_before_insert(repository):
    repo, session = repository
    original = proposal()
    with pytest.raises(ValueError, match='proposal_mandant_abweichend'):
        repo.save('tenant-b', original)
    assert session.get(AgentProposalRecord, original.proposal_id) is None


def test_own_save_still_updates(repository):
    repo, session = repository
    original = proposal()
    repo.save('tenant-a', original)
    repo.save('tenant-a', replace(original, context_summary='Eigene Aenderung'))
    session.expire_all()
    assert repo.get('tenant-a', original.proposal_id).context_snapshot['context_summary'] == 'Eigene Aenderung'
    assert repo.get('tenant-b', original.proposal_id) is None
