"""Actual shared Redis session state; no new server/container/database."""
import time
import uuid
import pytest
import redis
from fastapi import HTTPException
from app.core import identity_session as sessions
from test_system_tenant_binding import keys, probe

ORIGINAL_VALIDATE=sessions.validate


@pytest.fixture
def session(monkeypatch):
    client=redis.Redis.from_url('redis://127.0.0.1:6379/0',decode_responses=True,socket_connect_timeout=1,socket_timeout=2)
    try:
        client.ping()
    except redis.RedisError:
        pytest.skip('Existing shared Redis unavailable')
    prefix='valeo:identity:contract:'+uuid.uuid4().hex+':'
    monkeypatch.setattr(sessions,'PREFIX',prefix)
    monkeypatch.setattr(sessions,'store',lambda:client)
    now=time.time()
    claims={'iss':'https://example.invalid','tenant_id':'tenant-a','sub':'test-person','sid':'test-device','iat':now,'exp':now+300}
    yield client, claims
    own=list(client.scan_iter(prefix+'*'))
    if own:
        client.delete(*own)


def test_session_revocation_is_shared_and_does_not_affect_other_devices(session):
    _, claims=session
    sessions.validate(claims,'own-token')
    sessions.revoke_session(claims,'own-token')
    with pytest.raises(HTTPException) as error:
        sessions.validate(claims,'own-token')
    assert error.value.status_code == 401
    sessions.validate({**claims,'sid':'other-device'},'other-token')


def test_keycloak_refresh_does_not_evade_session_revocation(session):
    _,claims=session
    claims.pop('sid')
    claims.update(session_state='provider-browser-session',jti='first-token')
    sessions.validate(claims,'first-token')
    sessions.revoke_session(claims,'first-token')
    with pytest.raises(HTTPException) as error:
        sessions.validate({**claims,'jti':'refreshed-token'},'refreshed-token')
    assert error.value.status_code==401


def test_subject_revocation_rejects_existing_sessions_and_old_authentication(session):
    _, claims=session
    sessions.validate(claims,'own-token')
    sessions.revoke_subject(claims['iss'],claims['tenant_id'],claims['sub'],actor='synthetic-reviewer')
    with pytest.raises(HTTPException):
        sessions.validate({**claims,'sid':'new-device'},'new-token')
    sessions.validate({**claims,'tenant_id':'tenant-b'},'other-tenant')


def test_idle_session_cannot_be_revived_by_touch(session):
    client, claims=session
    sessions.validate(claims,'own-token')
    key,_=sessions.keys(claims,'own-token')
    client.hset(key,'active',time.time()-sessions.settings.IDENTITY_SESSION_IDLE_SECONDS-1)
    with pytest.raises(HTTPException):
        sessions.validate(claims,'own-token',touch=True)


def test_absolute_limit_uses_authentication_time_even_on_first_request(session):
    _, claims=session
    claims['auth_time']=time.time()-sessions.settings.IDENTITY_SESSION_MAX_SECONDS-1
    with pytest.raises(HTTPException):
        sessions.validate(claims,'own-token')


def test_session_store_failure_never_falls_back_to_memory(session,monkeypatch):
    _,claims=session
    def unavailable():
        raise redis.ConnectionError('Unavailable')
    monkeypatch.setattr(sessions,'store',unavailable)
    with pytest.raises(HTTPException) as error:
        sessions.validate(claims,'own-token')
    assert error.value.status_code == 503


def test_actual_signed_http_logout_denies_reuse(probe,session,monkeypatch):
    from main import app
    from fastapi.testclient import TestClient
    monkeypatch.setattr(sessions,'validate',ORIGINAL_VALIDATE)
    client=TestClient(app)
    headers=probe.headers()
    assert client.get('/api/v1/identity/session',headers=headers).status_code==200
    assert client.post('/api/v1/identity/session/logout',headers=headers).status_code==204
    assert client.get('/api/v1/identity/session',headers=headers).status_code==401
    entries=session[0].xrange(sessions.PREFIX+'audit:tenant-a')
    assert len(entries)==1
    assert entries[0][1]['actor']=='human-a'
    assert entries[0][1]['event']=='session_revoked'
    assert headers['Authorization'] not in str(entries)


def test_idle_websocket_closes_after_shared_revocation(probe,session,monkeypatch):
    from main import app
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect
    from app.api.v1.endpoints.websocket import active_terminals
    import jwt
    monkeypatch.setattr(sessions,'validate',ORIGINAL_VALIDATE)
    monkeypatch.setattr(sessions.settings,'IDENTITY_REVOCATION_POLL_SECONDS',0.02)
    token=probe.token()
    claims=jwt.decode(token,options={'verify_signature':False})
    with TestClient(app).websocket_connect('/api/v1/ws/pos/session-proof?token='+token) as ws:
        sessions.revoke_session(claims,token)
        with pytest.raises(WebSocketDisconnect) as error:
            ws.receive_json()
        assert error.value.code==1008
    assert 'tenant-a:session-proof' not in active_terminals


@pytest.mark.parametrize('issued',[float('nan'),float('inf'),True,-1])
def test_invalid_authentication_time_is_rejected_before_session_storage(session,issued):
    _,claims=session
    with pytest.raises(HTTPException) as error:
        sessions.validate({**claims,'iat':issued},'own-token')
    assert error.value.status_code==401


def test_subject_revoke_requires_admin_and_rejects_old_token(probe,session,monkeypatch):
    from main import app
    from fastapi.testclient import TestClient
    monkeypatch.setattr(sessions,'validate',ORIGINAL_VALIDATE)
    client=TestClient(app)
    headers=probe.headers()
    assert client.post('/api/v1/identity/subjects/revoke',headers=headers,json={'subject':'human-a'}).status_code==403
    admin={'Authorization':'Bearer '+probe.token(changes={'sub':'test-admin','sid':'admin-session','roles':['admin']})}
    assert client.post('/api/v1/identity/subjects/revoke',headers=admin,json={'subject':'human-a'}).status_code==204
    assert client.get('/api/v1/identity/session',headers=headers).status_code==401


def test_tenant_block_revokes_every_subject_but_preserves_other_tenants(session):
    _,claims=session
    sessions.validate(claims,'own-token')
    sessions.block_tenant(claims['tenant_id'],actor='fixture-platform')
    for subject in (claims['sub'],'other-person','service-worker'):
        with pytest.raises(HTTPException) as error:
            sessions.validate({**claims,'sub':subject,'sid':'fresh-session'},'other-token')
        assert error.value.status_code==403
    sessions.validate({**claims,'tenant_id':'tenant-b'},'other-tenant')
