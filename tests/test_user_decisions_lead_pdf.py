"""Canonical leads and durable PDF actions on the existing shared PostgreSQL probe.

An outer transaction isolates every test, including endpoint commits and immutable
archive records. No database, container, schema reset or destructive cleanup.
"""
import hashlib
import os
import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.api.v1.endpoints import leads, mask_actions, agrar_settlements
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.services import crm_lead_service as lead_service
from app.services import settlement_document_archive_service as archive

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture
def context():
    strict = os.environ.get('PYTEST_REQUIRE_DB_STRICT') == '1'
    url = os.environ.get('TEST_DATABASE_URL')
    if not url and (strict or os.environ.get('CI') == 'true'):
        url = os.environ.get('DATABASE_URL')  # Reuse only the database already provided by the CI job.
    if not url and strict:
        pytest.fail('CI must provide its existing PostgreSQL test database')
    if not url:
        pytest.skip('Existing TEST_DATABASE_URL required; no test database is created')
    development_url = os.environ.get('DEVELOPMENT_DATABASE_URL')
    if development_url:
        assert make_url(url) != make_url(development_url), 'Never write tests to the development database'
    engine = create_engine(url)
    with engine.connect() as connection:
        outer = connection.begin()
        db = Session(bind=connection, join_transaction_mode='create_savepoint')
        tenant, foreign, customer, other_customer, lead, settlement = [str(uuid.uuid4()) for _ in range(6)]
        for tid in (tenant, foreign):
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id, :name, :domain, TRUE)'), {'id': tid, 'name': 'Decision integration test', 'domain': tid+'.test.invalid'})
        for cid, tid in ((customer, tenant), (other_customer, foreign)):
            db.execute(text('INSERT INTO domain_crm.customers (id,tenant_id,customer_number,company_name,is_active) VALUES (:id,:tid,:number,:name,TRUE)'), {'id': cid,'tid':tid,'number':cid,'name':'Qualification test customer'})
        db.execute(text("INSERT INTO public.crm_leads (id,tenant_id,company,status,potential) VALUES (:id,:tid,'Decision test lead','NEW',12500)"), {'id':lead,'tid':tenant})
        db.execute(text("""INSERT INTO domain_inventory.agrar_settlements
            (id,tenant_id,settlement_number,supplier_id,gross_quantity_kg,billing_quantity_kg,
             unit_price_eur_per_ton,gross_amount_eur,total_deductions_eur,net_amount_eur,currency,status,drying_result,row_version)
            VALUES (:id,:tid,:number,:supplier,1000,1000,200,200,0,200,'EUR','draft','{}',1)"""), {'id':settlement,'tid':tenant,'number':'TEST-'+settlement,'supplier':customer})
        db.commit()  # Release only the savepoint; the outer transaction owns cleanup.
        app = FastAPI()
        app.include_router(leads.router,prefix='/api/v1/crm/leads')
        app.include_router(mask_actions.router,prefix='/api/v1')
        app.include_router(agrar_settlements.router,prefix='/api/v1/agrar/settlements')
        app.dependency_overrides[get_db] = lambda: db
        user = {'sub':'decision-test','roles':['admin']}
        app.dependency_overrides[get_current_user] = lambda: user
        with TestClient(app) as client:
            client.headers['X-Tenant-ID'] = tenant
            yield SimpleNamespace(db=db,client=client,tenant=tenant,foreign=foreign,customer=customer,
                                  other_customer=other_customer,lead=lead,settlement=settlement,user=user)
        db.close()
        outer.rollback()
    engine.dispose()


def action(c, **body):
    return c.client.post(f'/api/v1/crm/leads/{c.lead}/actions/qualifizieren',json={'customer_id':c.customer,**body})


@pytest.mark.parametrize("collection",["/api/v1/crm/leads/", "/api/v1/crm/leads"])
def test_local_crud_pagination_and_tenant_authority(context,collection):
    c = context
    response = c.client.post(collection,json={'company_name':'Second canonical lead','tenant_id':c.foreign})
    assert response.status_code == 201, response.text
    created = response.json()
    assert created['tenant_id'] == c.tenant
    listing = c.client.get('/api/v1/crm/leads/?limit=1').json()
    assert listing['total'] == 2 and listing['has_next'] is True
    assert c.client.get('/api/v1/crm/leads/?search=Second').json()['total'] == 1
    response = c.client.put('/api/v1/crm/leads/'+created['id'],json={'email':None,'status':'contacted'})
    assert response.status_code == 200 and response.json()['status'] == 'CONTACTED'
    assert c.client.get('/api/v1/crm/leads/'+created['id'],headers={'X-Tenant-ID':c.foreign}).status_code == 404
    assert c.client.delete('/api/v1/crm/leads/'+created['id'],headers={'X-Tenant-ID':c.foreign}).status_code == 404
    assert c.client.delete('/api/v1/crm/leads/'+created['id']).status_code == 204


@pytest.mark.parametrize('mode',['dryRun','validate','propose'])
def test_qualification_preview_writes_nothing(context,mode):
    c=context
    assert action(c,_mode=mode).json()['success'] is True
    assert lead_service.get_row(c.db,c.tenant,c.lead)['status'] == 'NEW'
    assert c.db.execute(text('SELECT count(*) FROM domain_crm.crm_opportunities WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar() == 0
    assert c.db.execute(text('SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar() == 0


def test_qualification_real_opportunity_and_no_duplicate(context):
    c=context
    result=action(c).json()
    assert result['success'] is True, result
    row=lead_service.get_row(c.db,c.tenant,c.lead)
    assert row['status']=='QUALIFIED' and row['qualified_opportunity_id']
    opportunity=c.db.execute(text('SELECT customer_id,estimated_value,stage FROM domain_crm.crm_opportunities WHERE id=:id AND tenant_id=:tid'),{'id':row['qualified_opportunity_id'],'tid':c.tenant}).mappings().one()
    assert opportunity['customer_id']==c.customer and opportunity['estimated_value']==12500
    assert result['auditEntryId'] and result['outboxEventId']
    assert action(c).json()['success'] is False
    assert c.db.execute(text('SELECT count(*) FROM domain_crm.crm_opportunities WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar() == 1
    assert c.client.put('/api/v1/crm/leads/'+c.lead,json={'status':'NEW'}).status_code==409


def test_foreign_customer_lead_and_read_only_role_rejected(context):
    c=context
    assert action(c,customer_id=c.other_customer).json()['success'] is False
    assert c.client.post(f'/api/v1/crm/leads/{c.lead}/actions/qualifizieren',headers={'X-Tenant-ID':c.foreign},json={'customer_id':c.other_customer}).json()['success'] is False
    c.user['roles']=['CRM_LESEN']
    assert c.client.get('/api/v1/crm/leads/'+c.lead).status_code==200
    assert action(c).status_code==403


def test_qualification_failure_rolls_back_opportunity_audit_and_event(context,monkeypatch):
    c=context
    original=lead_service.qualify
    def fail(*args):
        original(*args)
        raise RuntimeError('Injected failure after actual qualification mutation')
    monkeypatch.setattr(lead_service,'qualify',fail)
    assert action(c).json()['success'] is False
    assert lead_service.get_row(c.db,c.tenant,c.lead)['status']=='NEW'
    for table in ('domain_crm.crm_opportunities','domain_crm.crm_action_audit_log','outbox_events'):
        assert c.db.execute(text('SELECT count(*) FROM '+table+' WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar()==0


def test_print_archive_bytes_download_versions_and_immutable_content(context):
    c=context
    path=f'/api/v1/agrar/settlements/{c.settlement}/actions/drucken'
    assert c.client.post(path,json={'_mode':'dryRun'}).json()['success'] is True
    assert c.db.execute(text('SELECT count(*) FROM domain_docflow.document_artifacts WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar()==0
    for version in (1,2):
        result=c.client.post(path,json={}).json()
        assert result['success'] is True, result
        row=c.db.execute(text('SELECT * FROM domain_docflow.document_artifacts WHERE tenant_id=:tid AND version=:v'),{'tid':c.tenant,'v':version}).mappings().one()
        content=bytes(row['content_bytes'])
        assert content.startswith(b'%PDF-') and len(content)>1000
        assert hashlib.sha256(content).hexdigest()==row['content_hash_sha256']
        assert row['created_by']=='decision-test' and row['freigabe_status']=='archiviert'
        download=c.client.get('/api/v1/agrar/settlements/archive/'+row['id'])
        assert download.status_code==200 and download.content==content
        assert download.headers['content-type']=='application/pdf'
        assert c.client.get('/api/v1/agrar/settlements/archive/'+row['id'],headers={'X-Tenant-ID':c.foreign}).status_code==404
    for sql in ("UPDATE domain_docflow.document_artifacts SET content_bytes='tampered' WHERE id=:id", 'DELETE FROM domain_docflow.document_artifacts WHERE id=:id'):
        with pytest.raises(DBAPIError), c.db.begin_nested():
            c.db.execute(text(sql),{'id':row['id']})
    assert archive.read_pdf(c.db,c.tenant,row['id'])[0]==content


def test_failed_pdf_archive_cannot_report_success(context,monkeypatch):
    c=context
    def fail(*args,**kwargs):
        raise RuntimeError('Injected PostgreSQL archive failure')
    monkeypatch.setattr('app.services.settlement_pdf_service.archive_pdf',fail)
    result=c.client.post(f'/api/v1/agrar/settlements/{c.settlement}/actions/drucken',json={}).json()
    assert result['success'] is False
    for table in ('domain_docflow.document_headers','domain_docflow.document_artifacts','domain_crm.crm_action_audit_log','outbox_events'):
        assert c.db.execute(text('SELECT count(*) FROM '+table+' WHERE tenant_id=:tid'),{'tid':c.tenant}).scalar()==0


def test_pdf_integrity_failure_is_explicit():
    db=Mock()
    db.execute.return_value.mappings.return_value.first.return_value={'content_bytes':b'%PDF-corrupt','content_hash_sha256':'0'*64,'file_name':'test.pdf'}
    with pytest.raises(HTTPException) as exc:
        archive.read_pdf(db,'tenant','artifact')
    assert exc.value.status_code==409
