"""Real signed HTTP identities and shared Redis at the agent-control boundary."""
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import Body
from app.core import identity_agent_control as control
from app.core import identity_session as sessions
from test_identity_sessions import session, ORIGINAL_VALIDATE
from test_system_tenant_binding import keys, probe


@pytest.fixture
def controller(probe, session, monkeypatch):
    prefix='valeo:identity:agent-contract:'+uuid.uuid4().hex+':'
    monkeypatch.setattr(control,'PREFIX',prefix)
    monkeypatch.setattr(sessions,'validate',ORIGINAL_VALIDATE)
    effects=[]

    @probe.app.post('/api/control-contract')
    def endpoint(body: dict = Body(...)):
        operation=body.pop('operation')
        if operation=='job':
            with control.job(body['id'], {}):
                for _ in range(body.get('calls',1)):
                    control.consume(body.get('units',0))
                    effects.append(body['id'])
                if body.get('pause'): time.sleep(body['pause'])
            return {'ok':True}
        if operation=='authorize':
            return control.authorize(**body)
        return {'result': getattr(control,operation)(**body)}

    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    install_tenant_bindings(probe.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)

    def request(operation, actor='owner-fixture', tenant='tenant-a', kind='human',
                scopes=('admin:all',), roles=('admin',), **body):
        token=probe.token(tenant,changes={'sub':actor,'identity_type':kind,
            'erp_scopes':list(scopes),'roles':list(roles)})
        return probe.client.post('/api/control-contract',json={'operation':operation,**body},
                                 headers={'Authorization':'Bearer '+token})

    yield request, effects, session[0]
    own=list(session[0].scan_iter(prefix+'*'))
    if own: session[0].delete(*own)


def mandate(request, *, autonomy=2):
    action='tool:fixture-write'
    assert request('register_agent',subject='worker-fixture',purpose='contract only',actions=[action]).status_code==200
    response=request('create_mandate',agent='worker-fixture',task='fixture-task',actions=[action],
        payload={'amount':3},seconds=120,autonomy=autonomy)
    assert response.status_code==200
    return response.json()['result']


def test_four_eyes_content_and_tenant_are_checked_with_signed_identities(controller):
    request,_,_=controller
    record=mandate(request)
    assert request('approve_mandate',identifier=record['id'],payload_hash=record['payload_hash']).status_code==403
    assert request('approve_mandate',actor='reviewer-fixture',identifier=record['id'],payload_hash='changed').status_code==409
    assert request('approve_mandate',actor='reviewer-fixture',identifier=record['id'],payload_hash=record['payload_hash']).status_code==200
    assert request('authorize',actor='worker-fixture',kind='service',identifier=record['id'],
        payload={'amount':3},action='tool:fixture-write',write=True).status_code==200
    assert request('authorize',actor='worker-fixture',kind='service',identifier=record['id'],
        payload={'amount':4},action='tool:fixture-write',write=True).status_code==403
    assert request('authorize',actor='worker-fixture',kind='service',tenant='tenant-b',identifier=record['id'],
        payload={'amount':3},action='tool:fixture-write',write=True).status_code==404


def test_current_service_rights_and_read_only_autonomy_cannot_be_widened(controller):
    request,_,_=controller
    record=mandate(request,autonomy=0)
    assert request('approve_mandate',actor='reviewer-fixture',identifier=record['id'],payload_hash=record['payload_hash']).status_code==200
    assert request('authorize',actor='worker-fixture',kind='service',identifier=record['id'],
        payload={'amount':3},action='tool:fixture-write',write=True).status_code==403
    assert request('authorize',actor='worker-fixture',kind='service',scopes=(),identifier=record['id'],
        payload={'amount':3},action='tool:fixture-write').status_code==403
    assert request('create_mandate',scopes=('tool:other',),agent='worker-fixture',task='fixture',
        actions=['tool:fixture-write'],payload={},seconds=120,autonomy=2).status_code==403


def test_disabled_agent_and_revoked_mandate_stop_existing_authorization(controller):
    request,_,_=controller
    record=mandate(request)
    arguments={'actor':'worker-fixture','kind':'service','identifier':record['id'],
               'payload':{'amount':3},'action':'tool:fixture-write'}
    assert request('authorize',**arguments).status_code==200
    assert request('revoke_mandate',identifier=record['id']).status_code==200
    assert request('authorize',**arguments).status_code==403
    other=mandate(request)
    assert request('disable_agent',subject='worker-fixture').status_code==200
    assert request('authorize',**{**arguments,'identifier':other['id']}).status_code==403


def test_logout_of_delegator_stops_machine_mandate(controller,probe):
    request,_,_=controller
    record=mandate(request)
    token=probe.token(changes={'sub':'owner-fixture'})
    import jwt
    claims=jwt.decode(token,options={'verify_signature':False})
    sessions.revoke_session(claims,token)
    assert request('authorize',actor='worker-fixture',kind='service',identifier=record['id'],
        payload={'amount':3},action='tool:fixture-write').status_code==401


def test_atomic_call_budget_prevents_extra_effect_and_replay(controller,monkeypatch):
    request,effects,client=controller
    monkeypatch.setattr(control.settings,'IDENTITY_MAX_JOB_CALLS',2)
    assert request('job',id='bounded-job',calls=3).status_code==429
    assert effects==['bounded-job','bounded-job']
    assert request('job',id='bounded-job').status_code==409
    assert client.zcard(control.key('tenant-a','active_jobs'))==0


def test_parallel_job_admission_is_shared_between_request_workers(controller,monkeypatch):
    request,effects,client=controller
    monkeypatch.setattr(control.settings,'IDENTITY_MAX_PARALLEL_JOBS',1)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first=workers.submit(request,'job',id='first-job',pause=0.4)
        deadline=time.monotonic()+3
        while client.zcard(control.key('tenant-a','active_jobs'))==0:
            assert time.monotonic()<deadline
            time.sleep(0.01)
        assert request('job',id='second-job').status_code==429
        assert first.result().status_code==200
    assert effects==['first-job']
    assert client.zcard(control.key('tenant-a','active_jobs'))==0

