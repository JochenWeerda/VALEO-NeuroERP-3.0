"""Non-database count-sheet command and route guards."""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.v1.endpoints import inventory_auxiliary as endpoint
from app.services import inventory_count_sheet_command as service


REVISION = 'a' * 64


def principal(tenant='tenant-a', roles=None, claims=None, scopes=None):
    return SimpleNamespace(tenant_id=tenant, subject='actor-a', roles={'LAGER_BEARBEITEN'} if roles is None else roles,
                           scopes={'masks:write'} if scopes is None else scopes,
                           claims={'identity_type': 'human'} if claims is None else claims)


def command(**changes):
    return service.CountSheetCommand(**({'inventory_count_id': 'count-a', 'expected_revision': REVISION,
                                        'idempotency_key': 'key-a', 'reason': 'Kontrollierter Lauf'} | changes))


@pytest.fixture
def guard(monkeypatch):
    monkeypatch.setattr(service, 'current_identity', principal)


@pytest.mark.parametrize('user,tenant', [(principal(tenant='other'), 'tenant-a'),
    (principal(roles=set()), 'tenant-a'), (principal(claims={}), 'tenant-a'),
    (principal(claims={'identity_type': 'human', 'act': {'sub': 'agent'}}), 'tenant-a')])
def test_identity_guards_precede_database(monkeypatch, user, tenant):
    monkeypatch.setattr(service, 'current_identity', lambda: user)
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        service.create_count_sheet(db, tenant, command())
    assert exc.value.status_code == 403
    db.execute.assert_not_called()


@pytest.mark.parametrize('changes', [{'inventory_count_id': ' '}, {'expected_revision': 'x'},
                                     {'idempotency_key': ''}, {'reason': '  no  '}])
def test_invalid_command_rejected(changes):
    with pytest.raises(ValidationError):
        command(**changes)


def test_replay_does_not_read_or_write_inventory(monkeypatch, guard):
    monkeypatch.setattr(service, 'lock_and_replay', lambda *a, **kw: {'id': 'batch-1', 'replayed': True})
    locked = Mock(); monkeypatch.setattr(service, '_lock_sources', locked)
    db = MagicMock()
    assert service.create_count_sheet(db, 'tenant-a', command())['replayed'] is True
    locked.assert_not_called()
    db.commit.assert_not_called(); db.rollback.assert_not_called()


def test_changed_snapshot_blocks_before_batch_audit_and_outbox(monkeypatch, guard):
    monkeypatch.setattr(service, 'lock_and_replay', lambda *a, **kw: None)
    monkeypatch.setattr(service, '_lock_sources', lambda *a: None)
    monkeypatch.setattr(service, 'snapshot', lambda *a: {'revision': 'b' * 64})
    builder = Mock(); monkeypatch.setattr(service, 'InventoryAuxiliaryService', builder)
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        service.create_count_sheet(db, 'tenant-a', command())
    assert exc.value.status_code == 409
    builder.assert_not_called(); db.commit.assert_not_called(); db.rollback.assert_not_called()


def test_creation_uses_domain_service_and_caller_transaction(monkeypatch, guard):
    monkeypatch.setattr(service, 'lock_and_replay', lambda *a, **kw: None)
    monkeypatch.setattr(service, '_lock_sources', lambda *a: None)
    monkeypatch.setattr(service, 'snapshot', lambda *a: {'revision': REVISION})
    builder = Mock()
    builder.return_value.create.return_value = {'id': 'batch-1', 'status': 'generated', 'source_hash': 'h'}
    monkeypatch.setattr(service, 'InventoryAuxiliaryService', builder)
    audit, outbox, record = Mock(return_value='a'), Mock(return_value='o'), Mock()
    monkeypatch.setattr(service, '_write_audit', audit)
    monkeypatch.setattr(service, '_write_outbox', outbox)
    monkeypatch.setattr(service, 'store_execution', record)
    db = MagicMock()
    result = service.create_count_sheet(db, 'tenant-a', command())
    assert result['id'] == 'batch-1' and result['replayed'] is False
    builder.return_value.create.assert_called_once_with(count_id='count-a', batch_type='count_sheet',
        actor='actor-a', reason='Kontrollierter Lauf', commit=False)
    assert audit.call_args.kwargs['performed_by'] == 'actor-a'
    assert outbox.call_args.kwargs['payload']['audit_id'] == 'a'
    assert record.call_args.kwargs['actor'] == 'actor-a'
    db.commit.assert_not_called(); db.rollback.assert_not_called()


def test_old_unversioned_batch_entry_does_not_mutate():
    body = endpoint.BatchIn(inventory_count_id='count-a', batch_type='count_sheet', reason='Testgrund')
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        endpoint.create_batch(body, user={}, db=db, tenant_id='tenant-a')
    assert exc.value.status_code == 422
    db.commit.assert_not_called()


def test_mask_unknown_parameter_fails_before_database():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(endpoint.run_create_action(action_key='create_count_sheet', body={'tenant_id': 'other'},
                                                user={}, db=db, tenant_id='tenant-a'))
    assert exc.value.status_code == 422
    db.execute.assert_not_called()
