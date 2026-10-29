"""Generated master data: real DDL/commands on shared probe, outer rollback only."""
import json
from uuid import uuid4
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError
from alembic.migration import MigrationContext
from alembic.operations import Operations
from pydantic import ValidationError
from fastapi import HTTPException
from app.core.tenant_binding import install_tenant_bindings
from main import BearerAuthMiddleware
from app.services.studio_entity_contracts import EntitySpec, EntityCommand
from app.services.studio_entity_compiler import compile_entity
from app.services.studio_entity_router import build_router
from app.services.studio_entity_commands import execute, tables, read
from app.infrastructure.eventbus.outbox import OutboxEvent
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


def specification():
    return EntitySpec(name='studio_probe_' + uuid4().hex[:12], domain='crm', label='Synthetischer Stammsatz', columns=[
        {'name':'name','type':'text','nullable':False},
        {'name':'quantity','type':'decimal','nullable':False},
        {'name':'active','type':'boolean'}])


def command(data=None, *, version=None, key=None, mode='execute'):
    return {'_idempotencyKey':key or str(uuid4()), '_auditReason':'Synthetische Vertragsabnahme',
            '_mode':mode, 'expected_version':version, 'data':data or {}}


def values(): return {'name':'Synthetic','quantity':'1.2345','active':True}


@pytest.fixture
def entity(subject_data):
    client, db, provider, tenant, foreign, *_ = subject_data
    spec = specification()
    bundle = compile_entity(spec)
    namespace = {}
    exec(bundle['files']['migration.py'], namespace)
    with Operations.context(MigrationContext.configure(db.connection())):
        namespace['upgrade']()
    client.app.include_router(build_router(spec, writes_enabled=True), prefix='/api/v1/studio')
    install_tenant_bindings(client.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    return client, db, provider, tenant, foreign, spec, bundle


def auth(entity, role='CRM_BEARBEITEN', tenant=None):
    return {'Authorization':'Bearer '+entity[2].token(tenant or entity[3],
        changes={'sub':'synthetic-editor','roles':[role] if role else [], 'identity_type':'human'})}


def path(entity): return '/api/v1/studio/entities/'+entity[5].name


def test_sql_crud_replay_audit_outbox_and_deactivation(entity):
    client,db,_,tenant,foreign,spec,_=entity
    body=command(values());url=path(entity)
    created=client.post(url+'/actions/create',headers=auth(entity),json=body)
    assert created.status_code==200,created.text
    row=created.json()['result'];assert row['tenant_id']==tenant and row['version']==1
    assert client.post(url+'/actions/create',headers=auth(entity),json=body).json()==created.json()
    assert client.get(url,headers=auth(entity)).json()=={'items':[row], 'total':1, 'limit':50, 'skip':0}
    detail=url+'/'+row['id']
    assert client.get(detail,headers=auth(entity,tenant=foreign)).status_code==404
    changed={**values(),'quantity':'2.5000'}
    update=command(changed,version=1)
    result=client.post(detail+'/actions/update',headers=auth(entity),json=update)
    assert result.status_code==200,result.text
    assert result.json()['result']['version']==2
    assert client.post(detail+'/actions/update',headers=auth(entity),json=update).json()==result.json()
    assert client.post(detail+'/actions/update',headers=auth(entity),json=command(changed,version=1)).status_code==409
    assert client.post(detail+'/actions/delete',headers=auth(entity),json=command(version=2)).status_code==200
    assert client.get(detail,headers=auth(entity)).status_code==404
    assert client.get(url,headers=auth(entity)).json()['items']==[]
    rows,events=tables(spec)
    assert db.scalar(sa.select(sa.func.count()).select_from(rows))==1
    history=db.execute(sa.select(events).order_by(events.c.recorded_at)).mappings().all()
    assert len(history)==3 and history[-1]['audit']['before']['version']==2
    assert all(event['actor']=='synthetic-editor' for event in history)
    assert db.query(OutboxEvent).filter_by(tenant_id=tenant,event_type='StudioEntityChanged').count()==3
    with pytest.raises(DBAPIError), db.begin_nested():
        db.execute(events.update().values(actor='forged'))


@pytest.mark.parametrize('kind,status', [('role',403),('tenant_header',403),('actor_payload',422),
    ('unknown_field',422),('precision',422),('identity',403),('no_token',401)])
def test_signed_negative_commands_leave_no_row_or_receipt(entity,kind,status):
    client,db,_,tenant,foreign,spec,_=entity
    headers=auth(entity,role=None if kind=='role' else 'CRM_BEARBEITEN')
    body=command(values())
    if kind=='tenant_header':headers['X-Tenant-ID']=foreign
    if kind=='actor_payload':body['actor']='forged'
    if kind=='unknown_field':body['data']['unknown']=1
    if kind=='precision':body['data']['quantity']='1.12345'
    if kind=='identity':body['data']['tenant_id']=foreign
    if kind=='no_token':headers={}
    response=client.post(path(entity)+'/actions/create',headers=headers,json=body)
    assert response.status_code==status,response.text
    for table in tables(spec): assert db.scalar(sa.select(sa.func.count()).select_from(table))==0


@pytest.mark.parametrize('mode',['dryRun','validate','propose'])
def test_preview_applies_same_validation_without_business_effect(entity,mode):
    client,db,_,tenant,_,spec,_=entity
    response=client.post(path(entity)+'/actions/create',headers=auth(entity),json=command(values(),mode=mode))
    assert response.status_code==200 and response.json()['result']['persisted'] is False
    for table in tables(spec): assert db.scalar(sa.select(sa.func.count()).select_from(table))==0
    assert client.post(path(entity)+'/actions/create',headers=auth(entity,role=None),json=command(values(),mode=mode)).status_code==403


def test_outbox_failure_rolls_back_row_and_receipt(entity,monkeypatch):
    _,db,_,tenant,_,spec,_=entity
    original=db.flush
    def fail(*args,**kwargs):
        if any(isinstance(item,OutboxEvent) for item in db.new): raise RuntimeError('synthetic_outbox_failure')
        return original(*args,**kwargs)
    monkeypatch.setattr(db,'flush',fail)
    with pytest.raises(RuntimeError,match='synthetic_outbox_failure'):
        execute(db,spec,'create',tenant,'editor',EntityCommand.model_validate(command(values())))
    monkeypatch.setattr(db,'flush',original)
    for table in tables(spec): assert db.scalar(sa.select(sa.func.count()).select_from(table))==0


def test_flat_native_action_fields_share_typed_domain_validation(entity):
    client=entity[0]
    body=command(values())
    data=body.pop('data'); body.update(data)
    response=client.post(path(entity)+'/actions/create',headers=auth(entity),json=body)
    assert response.status_code==200,response.text
    assert response.json()['result']['quantity']=='1.2345'
    body['_idempotencyKey']=str(uuid4());body['quantity']='1.12345'
    assert client.post(path(entity)+'/actions/create',headers=auth(entity),json=body).status_code==422


def test_agent_role_needs_capability_enablement_beyond_normal_writer_role(entity):
    token=entity[2].token(entity[3],changes={'sub':'synthetic-agent',
        'roles':['CRM_BEARBEITEN'],'scope':'masks:write','identity_type':'agent'})
    response=entity[0].post(path(entity)+'/actions/create',headers={'Authorization':'Bearer '+token},json=command(values()))
    assert response.status_code==403 and response.json()['detail']=='agent_capability_not_enabled_for_role'


def test_deployment_marker_rejects_runtime_or_contract_drift(entity,monkeypatch):
    from app.services import studio_entity_contracts
    monkeypatch.setattr(studio_entity_contracts,'contract_hash',lambda _: '0'*64)
    response=entity[0].post(path(entity)+'/actions/create',headers=auth(entity),json=command(values()))
    assert response.status_code==409
    for table in tables(entity[5]): assert entity[1].scalar(sa.select(sa.func.count()).select_from(table))==0


def test_compile_authoring_api_and_cli_return_same_disabled_bundle(entity,monkeypatch,tmp_path):
    from app.api.v1.endpoints import studio_drafts
    from valeo_cli import cli
    client,_,provider,tenant,_,spec,_=entity
    client.app.include_router(studio_drafts.router,prefix='/api/v1')
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    token=provider.token(tenant,changes={'sub':'synthetic-author','roles':['EINKAUF_BEARBEITEN']})
    response=client.post('/api/v1/studio/entity-bundle',headers={'Authorization':'Bearer '+token},json=spec.model_dump())
    assert response.status_code==200,response.text
    source=tmp_path/'spec.json';source.write_text(spec.model_dump_json(),encoding='utf-8')
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',token)
    lines=[]
    assert cli.main(['studio','entitaet-generieren',str(source)],http=client,out=lines.append)==0
    assert json.loads(lines[0])==response.json()
