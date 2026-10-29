"""Real RSA dependencies and PostgreSQL isolation, without outer auth middleware."""
from types import SimpleNamespace
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from test_system_tenant_binding import keys, probe
from app.api.v1.endpoints import docflow
from app.core.database import engine, get_db
from app.services.docflow_service import DocflowService

ROUTES = [
    ('GET','/',None), ('POST','/',{'doc_type':'sales_offer','doc_number':'IT-rejected'}),
    ('GET','/{id}',None), ('DELETE','/{id}',None), ('PUT','/{id}',{'expected_version':1,'idempotency_key':'tenant-check-key'}),
    ('GET','/{id}/status-history',None), ('GET','/{id}/pos-compliance',None),
    ('POST','/{id}/release',{'idempotency_key':'IT-release'}),
    ('POST','/{id}/record-print',{}), ('POST','/{id}/record-export',{}),
    ('POST','/{id}/convert',{'target_doc_type':'sales_order','idempotency_key':'IT-convert'}),
    ('POST','/{id}/post',{'idempotency_key':'IT-posting'}),
    ('POST','/{id}/reverse',{'idempotency_key':'IT-reverse','reason':'test reason'}),
]

@pytest.fixture
def context(require_db, probe):
    tenant, foreign = str(uuid4()), str(uuid4())
    with engine.connect() as connection:
        outer = connection.begin()
        db = Session(bind=connection, join_transaction_mode='create_savepoint')
        try:
            for tid in (tenant, foreign):
                db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id,:id,:domain,TRUE)'), {'id':tid,'domain':tid+'.test.invalid'})
            db.commit()
            docs = [DocflowService(db, tid, 'synthetic-fixture').create_document(docflow.DocflowCreateRequest(
                doc_type='sales_offer', doc_number='IT-'+uuid4().hex[:12],
                items=[docflow.DocflowLineInput(article_number='TEST', quantity=1, unit_price=10)])) for tid in (tenant,foreign)]
            app = FastAPI()
            calls = []
            def database():
                calls.append('db')
                return db
            app.dependency_overrides[get_db] = database
            app.include_router(docflow.router, prefix='/api/v1/docflow')
            with TestClient(app, raise_server_exceptions=False) as client:
                yield SimpleNamespace(db=db,client=client,tenant=tenant,foreign=foreign,own=docs[0],other=docs[1],calls=calls,
                    headers={'Authorization':'Bearer '+probe.token(tenant,changes={'roles':['admin']})})
        finally:
            db.close()
            outer.rollback()


def test_queryless_list_and_create_use_verified_identity(context):
    c=context
    response=c.client.get('/api/v1/docflow/',headers=c.headers)
    assert response.status_code==200,response.text
    assert [row['id'] for row in response.json()]==[c.own]
    response=c.client.post('/api/v1/docflow/',headers=c.headers,json={'doc_type':'sales_offer','doc_number':'IT-'+uuid4().hex[:12]})
    assert response.status_code==200,response.text
    assert response.json()['tenant_id']==c.tenant
    assert c.db.execute(text('SELECT tenant_id FROM domain_docflow.document_headers WHERE id=:id'),{'id':response.json()['id']}).scalar()==c.tenant


def test_matching_legacy_selector_remains_supported(context):
    c=context
    response=c.client.get('/api/v1/docflow/',headers=c.headers,params={'tenant_id':c.tenant})
    assert response.status_code==200
    assert response.json()[0]['id']==c.own


@pytest.mark.parametrize('credential',[None,'dev-token'])
def test_missing_or_legacy_identity_stops_before_database(context,credential):
    c=context
    headers={'Authorization':'Bearer '+credential} if credential else {}
    response=c.client.get('/api/v1/docflow/',headers=headers,params={'tenant_id':c.tenant})
    assert response.status_code==401,response.text
    assert c.calls==[]


@pytest.mark.parametrize('method,path,payload',ROUTES)
def test_foreign_query_stops_before_database(context,method,path,payload):
    c=context
    response=c.client.request(method,'/api/v1/docflow'+path.format(id=c.other),headers=c.headers,params={'tenant_id':c.foreign},json=payload)
    assert response.status_code==403,response.text
    assert c.calls==[]


@pytest.mark.parametrize('method,path,payload',[r for r in ROUTES if '{id}' in r[1]])
def test_foreign_object_is_invisible_and_unchanged(context,method,path,payload):
    c=context
    query=text('SELECT status,version,print_count,exported_at,deleted_at FROM domain_docflow.document_headers WHERE id=:id')
    before=tuple(c.db.execute(query,{'id':c.other}).one())
    response=c.client.request(method,'/api/v1/docflow'+path.format(id=c.other),headers=c.headers,json=payload)
    assert response.status_code==404,response.text
    assert tuple(c.db.execute(query,{'id':c.other}).one())==before
