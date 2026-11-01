"""Scoped CRM requests and segments, signed identities and rollback-only probe SQL."""
import importlib.util
from pathlib import Path
from uuid import uuid4
import pytest
from sqlalchemy import text
from alembic.migration import MigrationContext
from alembic.operations import Operations
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401
from app.api.v1.endpoints import gdpr_requests, crm_segments
from app.services.crm_segment_service import criteria_rules
from fastapi import HTTPException

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

@pytest.fixture(scope='session', autouse=True)
def _seed_contract_test_tenants():
    yield

@pytest.fixture
def crm(subject_data):
    client, db, provider, tenant, foreign, *_ = subject_data
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/gdpr_request_processing_20261031.py'
    spec = importlib.util.spec_from_file_location('privacy_migration_test', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    db.execute(text("SET LOCAL lock_timeout='5s'"))
    # A fresh probe at head already carries the migration; only older databases need it applied here.
    applied = db.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='gdpr_requests' AND column_name='data_scope'")).first()
    if applied is None:
        with Operations.context(MigrationContext.configure(db.connection())):
            migration.upgrade()
    client.app.include_router(gdpr_requests.router, prefix='/api/v1')
    client.app.include_router(crm_segments.router, prefix='/api/v1')
    def headers(tid=tenant, roles=None):
        return {'Authorization': 'Bearer '+provider.token(tid, changes={'roles': roles or ['admin'], 'identity_type':'human','sub':'human-a'})}
    customer = str(uuid4())
    db.execute(text("INSERT INTO domain_crm.customers (id,tenant_id,customer_number,company_name,email,is_active) VALUES (:id,:tenant,:number,'Synthetic',:email,TRUE)"), {'id':customer,'tenant':tenant,'number':'PRIV-'+customer[:12],'email':'probe@example.invalid'})
    return client, db, headers, customer, tenant, foreign

def test_scoped_export_replay_and_foreign_isolation(crm):
    client, db, headers, customer, tenant, foreign = crm
    path='/api/v1/gdpr/requests'
    create={'subject_type':'CUSTOMER','data_scope':'LOCAL_CRM_SUBJECT','subject_id':customer,'subject_email':'probe@example.invalid','request_type':'ACCESS','_idempotencyKey':uuid4().hex}
    a=client.post(path,headers=headers(),json=create)
    assert a.status_code==201,a.text
    rid=a.json()['id']
    assert client.post(path,headers=headers(),json=create).json()['id']==rid
    assert client.post(path,headers=headers(foreign),json=create).status_code==404
    assert client.get(path+'/'+rid,headers=headers(foreign)).status_code==404
    verified=client.post(path+'/'+rid+'/verify',headers=headers())
    assert verified.status_code==200,verified.text
    payload={'subject_type':'CUSTOMER','data_scope':'LOCAL_CRM_SUBJECT','reason':'Synthetic test','expected_version':verified.json()['version'],'_idempotencyKey':uuid4().hex}
    export=client.post(path+'/'+rid+'/export',headers=headers(),json=payload)
    assert export.status_code==200,export.text
    assert export.json()['status']=='PARTIALLY_COMPLETED'
    assert client.post(path+'/'+rid+'/export',headers=headers(),json=payload).status_code==200
    assert client.post(path+'/'+rid+'/export',headers=headers(),json={**payload,'reason':'Changed reason'}).status_code==409
    download=client.get(path+'/'+rid+'/download',headers=headers())
    assert download.status_code==200,download.text
    assert download.json()['scope']=='LOCAL_CRM_SUBJECT'
    assert download.json()['retained']

def test_segment_rules_closed_and_empty_dynamic_rejected():
    with pytest.raises(HTTPException): criteria_rules({'tenant_id':'anything'})
    with pytest.raises(HTTPException): criteria_rules({'city':{'op':'sql','value':'x'}})
    assert criteria_rules({'city':{'op':'prefix','value':'Ber'}})[0]['value']=='Ber'

def test_segment_signed_tenant_replay(crm):
    client,db,headers,_,tenant,foreign=crm
    path='/api/v1/crm/segments'
    payload={'name':'Synthetic segment','segment_type':'static','_idempotencyKey':uuid4().hex}
    first=client.post(path,headers=headers(),json=payload)
    assert first.status_code==201,first.text
    sid=first.json()['id']
    assert client.post(path,headers=headers(),json=payload).json()['id']==sid
    assert client.post(path,headers=headers(),json={**payload,'name':'changed'}).status_code==409
    assert client.get(path+'/'+sid,headers=headers(foreign)).status_code==404
    assert client.put(path+'/'+sid,headers=headers(),json={'name':'bad','expected_version':first.json()['version']+1,'_idempotencyKey':uuid4().hex}).status_code==409
    assert client.get(path+'/'+sid,headers=headers()).json()['name']=='Synthetic segment'


def test_failed_erasure_rolls_back_all_changes(crm, monkeypatch):
    from app.api.v1.endpoints import compliance_dsgvo
    client, db, headers, customer, tenant, _ = crm
    path = '/api/v1/gdpr/requests'
    created = client.post(path, headers=headers(), json={'subject_type':'CUSTOMER', 'data_scope':'LOCAL_CRM_SUBJECT', 'subject_id':customer, 'subject_email':'probe@example.invalid', 'request_type':'ERASURE', '_idempotencyKey':uuid4().hex})
    assert created.status_code == 201, created.text
    rid = created.json()['id']
    verified = client.post(path+'/'+rid+'/verify', headers=headers())
    assert verified.status_code == 200, verified.text
    def failing_step(session, subject_type, subject_id, tenant_id):
        session.execute(text("UPDATE domain_crm.customers SET company_name='partial' WHERE id=:id AND tenant_id=:tid"), {'id':subject_id, 'tid':tenant_id})
        return [{'table':'synthetic', 'error':'injected failure'}]
    monkeypatch.setattr(compliance_dsgvo, '_anonymize_subject', failing_step)
    response = client.post(path+'/'+rid+'/delete', headers=headers(), json={'subject_type':'CUSTOMER', 'data_scope':'LOCAL_CRM_SUBJECT', 'reason':'Synthetic test', 'expected_version':verified.json()['version'], '_idempotencyKey':uuid4().hex})
    assert response.status_code == 422, response.text
    assert db.execute(text('SELECT company_name FROM domain_crm.customers WHERE id=:id'), {'id':customer}).scalar() == 'Synthetic'
    assert client.get(path+'/'+rid,headers=headers()).json()['status'] == 'VERIFIED'
