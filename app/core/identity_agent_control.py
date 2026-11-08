"""Tenant-bound agent mandates, four-eyes content approval and atomic job budgets."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
import time
from uuid import uuid4

from fastapi import HTTPException
from app.core import identity_session
from app.core.config import settings
from app.core.identity_context import current_identity

PREFIX = 'valeo:identity:agents:v1:'


def fingerprint(payload: dict) -> str:
    try:
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                         allow_nan=False).encode()).hexdigest()
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, 'Mandate payload must be finite JSON') from exc


def key(tenant: str, kind: str, identifier: str = '') -> str:
    return PREFIX + tenant + ':' + kind + ':' + hashlib.sha256(identifier.encode()).hexdigest()


from app.core.identity_control_store import storage_boundary, human, read_record


@storage_boundary
def register_agent(subject: str, purpose: str, actions: list[str]) -> dict:
    principal = human(administrative=True)
    record = {'subject': subject, 'tenant_id': principal.tenant_id, 'issuer': principal.issuer,
              'owner': principal.subject, 'purpose': purpose, 'actions': sorted(set(actions)),
              'enabled': True, 'updated_at': time.time()}
    client = identity_session.store()
    with client.pipeline(transaction=True) as tx:
        tx.set(key(principal.tenant_id, 'agent', subject), json.dumps(record))
        tx.sadd(key(principal.tenant_id, 'registry'), subject)
        tx.xadd(key(principal.tenant_id, 'audit'), {'event': 'agent_registered',
                'actor': principal.subject, 'subject': subject, 'at': str(time.time())})
        tx.execute()
    return record


@storage_boundary
def disable_agent(subject: str) -> None:
    principal = human(administrative=True)
    client = identity_session.store()
    location = key(principal.tenant_id, 'agent', subject)
    # A separate revocation key cannot be overwritten by a stale registry update.
    read_record(client, location)
    with client.pipeline(transaction=True) as tx:
        tx.set(key(principal.tenant_id, 'agent_disabled', subject), '1')
        tx.xadd(key(principal.tenant_id, 'audit'), {'event': 'agent_disabled',
                'actor': principal.subject, 'subject': subject, 'at': str(time.time())})
        tx.execute()


@storage_boundary
def create_mandate(agent: str, task: str, actions: list[str], payload: dict,
                   seconds: int, autonomy: int) -> dict:
    principal = human()
    client = identity_session.store()
    registered = read_record(client, key(principal.tenant_id, 'agent', agent))
    permitted = principal.scopes
    if (registered['issuer'] != principal.issuer or client.exists(key(principal.tenant_id, 'agent_disabled', agent))
            or not set(actions) <= set(registered['actions'])
            or ('admin:all' not in permitted and not set(actions) <= permitted)):
        raise HTTPException(403, 'Mandate exceeds registered or delegator permissions')
    identifier = str(uuid4())
    expires = min(time.time() + seconds, principal.claims['exp'])
    record = {'id': identifier, 'tenant_id': principal.tenant_id, 'issuer': principal.issuer,
        'agent': agent, 'delegator': principal.subject, 'task': task,
        'actions': sorted(set(actions)), 'payload_hash': fingerprint(payload),
        'autonomy': autonomy, 'expires_at': expires, 'approved_by': None,
        # Only authentication metadata, never the JWT or personal profile.
        'delegator_session': {name: principal.claims[name] for name in
            ('iss', 'sub', 'sid', 'session_state', 'jti', 'iat', 'auth_time', 'exp') if name in principal.claims}}
    record['delegator_session']['tenant_id'] = principal.tenant_id
    if not (record['delegator_session'].get('sid') or record['delegator_session'].get('session_state')):
        raise HTTPException(403, 'A provider session is required for delegation')
    with client.pipeline(transaction=True) as tx:
        tx.set(key(principal.tenant_id, 'mandate', identifier), json.dumps(record), ex=max(1, int(expires-time.time())+60))
        tx.xadd(key(principal.tenant_id, 'audit'), {'event': 'mandate_created', 'actor': principal.subject,
                'subject': agent, 'mandate': identifier, 'payload_hash': record['payload_hash'], 'at': str(time.time())})
        tx.execute()
    return record


@storage_boundary
def approve_mandate(identifier: str, payload_hash: str) -> dict:
    principal = human()
    client = identity_session.store()
    location = key(principal.tenant_id, 'mandate', identifier)
    record = read_record(client, location)
    if record['delegator'] == principal.subject or record['agent'] == principal.subject:
        raise HTTPException(403, 'Self approval is prohibited')
    if record['payload_hash'] != payload_hash or record['expires_at'] <= time.time():
        raise HTTPException(409, 'Mandate content changed or expired')
    if 'admin:all' not in principal.scopes and not set(record['actions']) <= principal.scopes:
        raise HTTPException(403, 'Approval exceeds current permissions')
    # Approval is a separate immutable binding, not a rewrite of the mandate.
    approval = {'approved_by': principal.subject, 'payload_hash': payload_hash, 'at': time.time()}
    if not client.set(key(principal.tenant_id, 'approval', identifier), json.dumps(approval),
                      nx=True, ex=max(1, int(record['expires_at']-time.time())+60)):
        raise HTTPException(409, 'Mandate already reviewed')
    return approval


@storage_boundary
def revoke_mandate(identifier: str) -> None:
    principal = human()
    client = identity_session.store()
    record = read_record(client, key(principal.tenant_id, 'mandate', identifier))
    if principal.subject != record['delegator'] and 'admin' not in principal.roles:
        raise HTTPException(403, 'Only the delegator or tenant administration may revoke')
    client.set(key(principal.tenant_id, 'mandate_revoked', identifier), '1',
               ex=max(1, int(record['expires_at']-time.time())+60))


@storage_boundary
def authorize(identifier: str, payload: dict, action: str, *, write: bool = False) -> dict:
    principal = current_identity()
    if principal.claims.get('identity_type') != 'service':
        raise HTTPException(403, 'An independent service identity is required')
    client = identity_session.store()
    record = read_record(client, key(principal.tenant_id, 'mandate', identifier))
    agent = read_record(client, key(principal.tenant_id, 'agent', principal.subject))
    if (record['agent'] != principal.subject or record['issuer'] != principal.issuer
            or agent['issuer'] != principal.issuer
            or record['expires_at'] <= time.time() or record['payload_hash'] != fingerprint(payload)
            or client.exists(key(principal.tenant_id, 'agent_disabled', principal.subject))
            or client.exists(key(principal.tenant_id, 'mandate_revoked', identifier))
            or action not in record['actions'] or action not in agent['actions']
            or ('admin:all' not in principal.scopes and action not in principal.scopes)):
        raise HTTPException(403, 'Agent mandate does not authorize this execution')
    identity_session.validate(record['delegator_session'], '', touch=False)
    if write:
        if record['autonomy'] < 2:
            raise HTTPException(403, 'Observation or draft mandate cannot execute writes')
        approval = read_record(client, key(principal.tenant_id, 'approval', identifier))
        if approval['payload_hash'] != record['payload_hash']:
            raise HTTPException(409, 'Approval is not bound to this content')
    return record


_ACQUIRE = '''
if redis.call('EXISTS', KEYS[1]) == 1 then return 'replay' end
redis.call('ZREMRANGEBYSCORE', KEYS[2], '-inf', ARGV[1])
if redis.call('ZCARD', KEYS[2]) >= tonumber(ARGV[3]) then return 'parallel_limit' end
redis.call('HSET', KEYS[1], 'status', 'running', 'deadline', ARGV[2], 'calls', 0, 'units', 0)
redis.call('EXPIRE', KEYS[1], 604800)
redis.call('ZADD', KEYS[2], ARGV[2], KEYS[1])
return 'acquired'
'''
_CONSUME = '''
if redis.call('HGET', KEYS[1], 'status') ~= 'running' then return 'not_running' end
if tonumber(ARGV[1]) >= tonumber(redis.call('HGET', KEYS[1], 'deadline')) then return 'deadline' end
local calls = tonumber(redis.call('HGET', KEYS[1], 'calls') or '0') + 1
local units = tonumber(redis.call('HGET', KEYS[1], 'units') or '0') + tonumber(ARGV[2])
if calls > tonumber(ARGV[3]) or units > tonumber(ARGV[4]) then return 'budget' end
redis.call('HSET', KEYS[1], 'calls', calls, 'units', units)
return 'allowed'
'''
_job: ContextVar[tuple[str, str] | None] = ContextVar('agent_execution_budget', default=None)


@contextmanager
@storage_boundary
def job(identifier: str, payload: dict):
    principal = current_identity()
    client = identity_session.store()
    location = key(principal.tenant_id, 'job', identifier)
    pool = key(principal.tenant_id, 'active_jobs')
    deadline = min(time.time()+settings.IDENTITY_MAX_JOB_SECONDS, principal.claims['exp'])
    result = client.eval(_ACQUIRE, 2, location, pool, time.time(), deadline, settings.IDENTITY_MAX_PARALLEL_JOBS)
    if result != 'acquired':
        raise HTTPException(409 if result == 'replay' else 429, 'Job already started or concurrency limit reached')
    token = _job.set((principal.tenant_id, location))
    try:
        yield
        client.hset(location, 'status', 'completed')
    except BaseException:
        # Ambiguous external effects are never silently retried.
        client.hset(location, 'status', 'stopped')
        raise
    finally:
        _job.reset(token)
        client.zrem(pool, location)


@storage_boundary
def consume(units: int = 0) -> None:
    principal = current_identity()
    active = _job.get()
    if active is None or active[0] != principal.tenant_id:
        raise HTTPException(403, 'Execution requires a bounded job')
    if isinstance(units, bool) or not isinstance(units, int) or units < 0:
        raise HTTPException(400, 'Invalid resource reservation')
    result = identity_session.store().eval(_CONSUME, 1, active[1], time.time(), units,
        settings.IDENTITY_MAX_JOB_CALLS, settings.IDENTITY_MAX_JOB_TOKEN_UNITS)
    if result != 'allowed':
        raise HTTPException(429, 'Execution budget or deadline exhausted')
