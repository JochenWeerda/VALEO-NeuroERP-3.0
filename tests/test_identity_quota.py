"""Shared Redis transactions, real RSA HTTP identity and budget conservation."""
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import pytest
from fastapi import Body
from app.core import identity_quota as quota, identity_session as sessions
from test_identity_sessions import session, ORIGINAL_VALIDATE
from test_system_tenant_binding import keys, probe


@pytest.fixture
def budget_api(probe, session, monkeypatch):
    prefix='valeo:identity:quota-contract:'+uuid4().hex+':'
    monkeypatch.setattr(quota,'PREFIX',prefix)
    monkeypatch.setattr(sessions,'validate',ORIGINAL_VALIDATE)
    @probe.app.post('/api/quota-contract')
    def endpoint(body: dict=Body(...)):
        operation=body.pop('operation')
        return {'result':getattr(quota,operation)(**body)}
    from app.api.v1.endpoints.identity_management import router
    probe.app.include_router(router,prefix='/api')
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    install_tenant_bindings(probe.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    def request(operation,actor='platform-fixture',tenant='tenant-a',identity_type='human',
                scopes=('platform:quota:manage',),roles=('admin',),**body):
        if operation=='allocate': body.setdefault('request_id',uuid4().hex)
        token=probe.token(tenant,changes={'sub':actor,'identity_type':identity_type,
            'erp_scopes':list(scopes),'roles':list(roles)})
        return probe.client.post('/api/quota-contract',json={'operation':operation,**body},
                                 headers={'Authorization':'Bearer '+token})
    yield request,session[0]
    own=list(session[0].scan_iter(prefix+'*'))
    if own: session[0].delete(*own)


def root(request,tokens=100,children=3):
    response=request('create_root',tokens=tokens,max_children=children)
    assert response.status_code==200,response.text
    return response.json()['result']['id']


def test_only_explicit_platform_scope_can_issue_capacity(budget_api):
    request,_=budget_api
    assert request('create_root',scopes=('admin:all',),tokens=100,max_children=2).status_code==403
    assert request('create_root',identity_type='service',tokens=100,max_children=2).status_code==403
    parent=root(request)
    assert request('create_root',tokens=100,max_children=2).status_code==409
    assert request('allocate',tenant='tenant-b',parent=parent,owner='user-fixture',kind='user',
        tokens=10,max_children=1).status_code==404


def test_nested_allocations_do_not_inflate_capacity(budget_api):
    request,_=budget_api
    parent=root(request)
    child=request('allocate',parent=parent,owner='user-fixture',kind='user',tokens=80,max_children=1).json()['result']['id']
    args=dict(actor='user-fixture',roles=(),scopes=('identity:quota:allocate',),parent=child,owner='agent-fixture',kind='agent',tokens=60,max_children=1)
    agent=request('allocate',**args).json()['result']['id']
    assert request('allocate',**args).status_code==429
    assert request('allocate',parent=parent,owner='other',kind='user',tokens=21,max_children=0).status_code==429
    assert request('allocate',actor='stranger',roles=(),parent=child,owner='other',kind='agent',tokens=1,max_children=0).status_code==403
    assert request('allocate',actor='agent-fixture',identity_type='service',scopes=('agent:delegate',),parent=agent,
                   owner='subagent-fixture',tokens=40,max_children=0,kind='agent').status_code==200


def test_agent_cannot_issue_user_budgets_or_delegate_without_permission(budget_api):
    request,_=budget_api
    parent=root(request)
    agent=request('allocate',parent=parent,owner='worker-fixture',kind='agent',tokens=50,max_children=2).json()['result']['id']
    assert request('allocate',actor='worker-fixture',identity_type='service',scopes=(),parent=agent,
        owner='sub-fixture',tokens=1,max_children=0,kind='agent').status_code==403
    assert request('allocate',actor='worker-fixture',identity_type='service',scopes=('agent:delegate',),parent=agent,
        owner='user-fixture',tokens=1,max_children=0,kind='user').status_code==403


def test_reservation_settlement_replay_and_unused_capacity(budget_api):
    request,client=budget_api
    parent=root(request)
    budget=request('allocate',parent=parent,owner='user-fixture',kind='user',tokens=80,max_children=0).json()['result']['id']
    reserve=dict(actor='user-fixture',budget=budget,request_id='request-fixture',job='job-fixture',tokens=60)
    assert request('reserve',**reserve).status_code==200
    assert request('reserve',**reserve).status_code==200
    assert request('reserve',**dict(reserve,tokens=59)).status_code==409
    assert request('reserve',**dict(reserve,request_id='another',tokens=21)).status_code==429
    assert request('settle',actor='stranger',request_id='request-fixture',actual_tokens=30,outcome='completed').status_code==403
    finish=dict(actor='user-fixture',request_id='request-fixture',actual_tokens=30,outcome='completed')
    assert request('settle',**dict(finish,actual_tokens=61)).status_code==409
    assert request('settle',**finish).status_code==200
    assert request('settle',**finish).status_code==200
    rows=request('overview').json()['result']
    own=next(r for r in rows if r['id']==budget)
    top=next(r for r in rows if r['id']==parent)
    assert (own['reserved'],own['spent'],own['available'])==(0,30,50)
    assert (top['total_spent'],top['available'])==(30,20)
    assert client.xlen(quota.locations('tenant-a')[1])==4
    assert request('ledger',tenant='tenant-b').json()['result']==[]
    assert request('ledger',roles=()).status_code==403
    assert request('reserve',**reserve).json()['result']['status']=='settled'


def test_parallel_reservations_share_one_atomic_budget(budget_api):
    request,_=budget_api
    parent=root(request,tokens=10)
    with ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda n:request('reserve',budget=parent,request_id=str(n),job='parallel',tokens=3),range(8)))
    assert sum(r.status_code==200 for r in responses)==3
    assert sum(r.status_code==429 for r in responses)==5
    row=request('overview').json()['result'][0]
    assert (row['reserved'],row['available'])==(9,1)


@pytest.mark.parametrize('value',[True,-1,1.5,10**12+1])
def test_invalid_token_amounts_cannot_reach_redis(budget_api,value):
    request,_=budget_api
    assert request('create_root',tokens=value,max_children=1).status_code==422


def test_production_budget_route_uses_signed_context_and_rejects_actor_override(probe,budget_api):
    _,_=budget_api
    token=probe.token('tenant-a',changes={'sub':'typed-route-fixture','identity_type':'human',
        'erp_scopes':['platform:quota:manage'],'roles':['admin']})
    headers={'Authorization':'Bearer '+token}
    endpoint='/api/identity/budgets/root'
    bad=probe.client.post(endpoint,headers=headers,json={'tokens':100,'max_children':2,'actor':'forged'})
    assert bad.status_code==422
    created=probe.client.post(endpoint,headers=headers,json={'tokens':100,'max_children':2})
    assert created.status_code==201 and created.json()['owner']=='typed-route-fixture'
    listed=probe.client.get('/api/identity/budgets',headers=headers)
    assert listed.status_code==200 and listed.json()[0]['available']==100
    ledger=probe.client.get('/api/identity/consumption-ledger',headers=headers)
    assert ledger.status_code==200 and ledger.json()[0]['actor']=='typed-route-fixture'


def test_repeated_allocation_preserves_capacity_and_detects_payload_change(budget_api):
    request,_=budget_api
    parent=root(request)
    args=dict(parent=parent,owner='user-fixture',kind='user',tokens=60,max_children=1,request_id='stable-allocation')
    first=request('allocate',**args)
    assert first.status_code==200
    again=request('allocate',**args)
    assert again.status_code==200 and again.json()==first.json()
    assert request('allocate',**dict(args,tokens=59)).status_code==409
    rows=request('overview').json()['result']
    assert len(rows)==2 and next(r for r in rows if r['id']==parent)['available']==40


def test_mask_preview_checks_real_capacity_without_writing_ledger(probe,budget_api):
    request,client=budget_api
    token=probe.token('tenant-a',changes={'sub':'platform-fixture','identity_type':'human',
        'erp_scopes':['platform:quota:manage'],'roles':['admin']})
    headers={'Authorization':'Bearer '+token}
    payload={'tokens':100,'max_children':2,'_mode':'dryRun'}
    endpoint='/api/identity/budgets/actions/root'
    preview=probe.client.post(endpoint,headers=headers,json=payload)
    assert preview.status_code==200 and preview.json()['success']
    assert not client.exists(quota.locations('tenant-a')[0])
    assert not client.exists(quota.locations('tenant-a')[1])
    assert probe.client.post(endpoint,headers=headers,json={**payload,'_mode':'execute'}).status_code==422
    result=probe.client.post(endpoint,headers=headers,json={**payload,'_mode':'execute','_auditReason':'Synthetic training capacity'})
    assert result.status_code==200 and result.json()['success'] and result.json()['affectedIds']
    assert client.xlen(quota.locations('tenant-a')[1])==1
    rejected=probe.client.post(endpoint,headers=headers,json=payload)
    assert rejected.status_code==409
