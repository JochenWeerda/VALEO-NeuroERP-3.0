"""Transaction ownership and identity binding of shared command replay."""
import json
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.command_idempotency import lock_and_replay, store_execution

FINGERPRINT = 'a' * 64
BASE = {'tenant': 'tenant-a', 'command': 'inventory.count_sheet.create.v1',
        'key': 'key-a', 'actor': 'actor-a', 'fingerprint': FINGERPRINT}


def database(row):
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = row
    return db


def test_first_execution_locks_and_does_not_manage_transaction():
    db = database(None)
    assert lock_and_replay(db, **BASE) is None
    assert len(db.execute.call_args_list) == 2
    assert 'pg_advisory_xact_lock' in str(db.execute.call_args_list[0].args[0])
    assert db.execute.call_args_list[1].args[1] == {'tenant': 'tenant-a',
                                                   'command': 'inventory.count_sheet.create.v1', 'key': 'key-a'}
    db.commit.assert_not_called(); db.rollback.assert_not_called()


@pytest.mark.parametrize('result', [{'success': True, 'id': 'one'}, '{"success":true,"id":"one"}'])
def test_replay_preserves_result_without_transaction_side_effect(result):
    db = database({'actor_id': 'actor-a', 'payload_hash': FINGERPRINT, 'result': result})
    assert lock_and_replay(db, **BASE) == {'success': True, 'id': 'one', 'replayed': True}
    db.commit.assert_not_called(); db.rollback.assert_not_called()


@pytest.mark.parametrize('actor,digest', [('actor-b', FINGERPRINT), ('actor-a', 'b' * 64), ('actor-a', None), ('actor-a', 'ä' * 64)])
def test_reusing_key_for_other_identity_or_payload_is_conflict(actor, digest):
    db = database({'actor_id': actor, 'payload_hash': digest, 'result': {'success': True}})
    with pytest.raises(HTTPException) as exc:
        lock_and_replay(db, **BASE)
    assert exc.value.status_code == 409
    db.commit.assert_not_called(); db.rollback.assert_not_called()


@pytest.mark.parametrize('result', [None, [], 'not-json'])
def test_corrupt_stored_result_is_never_replayed(result):
    db = database({'actor_id': 'actor-a', 'payload_hash': FINGERPRINT, 'result': result})
    with pytest.raises(HTTPException) as exc:
        lock_and_replay(db, **BASE)
    assert exc.value.status_code == 503
    db.commit.assert_not_called(); db.rollback.assert_not_called()


@pytest.mark.parametrize('override', [{'tenant': ''}, {'actor': ''}, {'command': ''}, {'key': '  '},
                                      {'key': 'x' * 201}, {'fingerprint': 'bad'}])
def test_invalid_contract_is_rejected_before_sql(override):
    db = database(None)
    with pytest.raises(HTTPException) as exc:
        lock_and_replay(db, **(BASE | override))
    assert exc.value.status_code == 422
    db.execute.assert_not_called()


def test_store_binds_every_field_and_leaves_transaction_with_caller():
    db = database(None)
    result = {'success': True, 'label': 'Zählliste'}
    store_execution(db, **BASE, result=result)
    params = db.execute.call_args.args[1]
    assert params == BASE | {'result': json.dumps(result, ensure_ascii=False)}
    assert 'INSERT INTO public.mcp_tool_executions' in str(db.execute.call_args.args[0])
    db.commit.assert_not_called(); db.rollback.assert_not_called()
