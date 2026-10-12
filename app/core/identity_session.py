"""Shared server-side sessions: no process-local or availability fallback."""
from __future__ import annotations
import hashlib
import time
import math
from functools import lru_cache
import redis
from fastapi import HTTPException
from app.core.config import settings

PREFIX='valeo:identity:v1:'
_CHECK = '''
local revoked = tonumber(redis.call('GET', KEYS[2]) or '0')
local now, issued, idle, maximum, touch = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3]), tonumber(ARGV[4]), tonumber(ARGV[5])
if issued <= revoked then return 'revoked' end
local start = tonumber(redis.call('HGET', KEYS[1], 'started') or ARGV[2])
local last = tonumber(redis.call('HGET', KEYS[1], 'active') or ARGV[1])
if redis.call('HGET', KEYS[1], 'revoked') == '1' then return 'revoked' end
if now >= start + maximum then return 'absolute_expired' end
if now >= last + idle then return 'idle_expired' end
local new = redis.call('HSETNX', KEYS[1], 'started', start)
redis.call('HSETNX', KEYS[1], 'active', last)
if touch == 1 then redis.call('HSET', KEYS[1], 'active', now) end
if new == 1 then redis.call('EXPIRE', KEYS[1], math.ceil(start + maximum - now) + 60) end
return 'active'
'''


def store():
    return _client(settings.REDIS_URL)


@lru_cache(maxsize=4)
def _client(url: str):
    return redis.Redis.from_url(url, decode_responses=True,
                                socket_connect_timeout=0.5, socket_timeout=0.5)


def keys(claims: dict, token: str) -> tuple[str,str]:
    identity='|'.join((claims['iss'], claims['tenant_id'], claims['sub']))
    # Keycloak 22 uses session_state; refreshed JWTs have a new jti but the same session.
    session=claims.get('sid') or claims.get('session_state') or claims.get('jti') or hashlib.sha256(token.encode()).hexdigest()
    if not isinstance(session,str) or not session:
        raise HTTPException(401,'Invalid session identity')
    digest=lambda v:hashlib.sha256(v.encode()).hexdigest()
    return PREFIX+'session:'+digest(identity+'|'+session), PREFIX+'subject:'+digest(identity)


def validate(claims: dict, token: str, *, touch: bool = True) -> None:
    now=time.time()
    issued=claims.get('auth_time', claims.get('iat'))
    if isinstance(issued,bool) or not isinstance(issued,(int,float)) or not math.isfinite(issued) or issued <= 0 or issued > now+30:
        raise HTTPException(401,'Invalid authentication time')
    normalized={**claims,'tenant_id': claims.get('tenant_id') or claims.get('mandanten_id')}
    session, subject=keys(normalized,token)
    try:
        result=store().eval(_CHECK,2,session,subject,now,issued,
                            settings.IDENTITY_SESSION_IDLE_SECONDS,settings.IDENTITY_SESSION_MAX_SECONDS,int(touch))
    except redis.RedisError as exc:
        raise HTTPException(503,'Identity session store unavailable') from exc
    if result != 'active':
        raise HTTPException(401,'Session expired or revoked')


def revoke_session(claims: dict, token: str) -> None:
    tenant=claims.get('tenant_id') or claims.get('mandanten_id')
    session,_=keys({**claims,'tenant_id':tenant},token)
    try:
        client=store()
        with client.pipeline(transaction=True) as tx:
            tx.hset(session,'revoked','1')
            tx.expire(session,settings.IDENTITY_SESSION_MAX_SECONDS+60)
            tx.xadd(PREFIX+'audit:'+tenant,
                    {'event':'session_revoked','actor':claims['sub'],'subject':claims['sub'],
                     'tenant_id':tenant, 'at':str(time.time())})
            tx.execute()
    except redis.RedisError as exc:
        raise HTTPException(503,'Identity session store unavailable') from exc


def revoke_subject(issuer: str, tenant: str, subject: str, *, actor: str) -> None:
    _, key=keys({'iss':issuer,'tenant_id':tenant,'sub':subject,'sid':'revocation'},'')
    try:
        # Kept beyond session lifetimes; never fail open on a cache miss/worker restart.
        with store().pipeline(transaction=True) as tx:
            tx.set(key,time.time())
            tx.xadd(PREFIX+'audit:'+tenant, {'event':'subject_sessions_revoked',
                    'actor':actor,'subject':subject,'tenant_id':tenant,'at':str(time.time())})
            tx.execute()
    except redis.RedisError as exc:
        raise HTTPException(503,'Identity session store unavailable') from exc
