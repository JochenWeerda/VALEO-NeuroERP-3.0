"""Real signed personal-file roles, probe persistence, failures and tenant boundaries."""
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.api.v1.endpoints.personal import router
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import keys, probe, subject_data


@pytest.fixture
def personal_case(subject_data):
    _, db, provider, tenant, other_tenant, *_ = subject_data
    ref = 'synthetic-' + str(uuid4())
    for tid in (tenant, other_tenant):
        db.execute(text("""INSERT INTO domain_hr.employee_file_documents
            (id,tenant_id,employee_ref,document_type,title,visibility,retention_until,audit_ref,created_by)
            VALUES (:id,:tid,:ref,'certificate',:title,'employee',CURRENT_DATE+365,:audit,'synthetic-seed')"""),
            {'id':str(uuid4()),'tid':tid,'ref':ref,'title':tid,'audit':str(uuid4())})
    db.commit()  # savepoint release only; outer fixture transaction owns rollback
    app=FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(router,prefix='/api/v1')
    def shared_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise
    app.dependency_overrides[get_db]=shared_db
    install_tenant_bindings(app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    with TestClient(app,raise_server_exceptions=False) as client:
        yield client,db,provider,tenant,other_tenant,ref


def headers(case,roles,tenant=None):
    return {'Authorization':'Bearer '+case[2].token(tenant or case[3],changes={'roles':roles})}


def path(case):
    return '/api/v1/personal/employee-files/'+case[5]


@pytest.mark.parametrize('roles',[[],['manager'],['LAGER_ADMIN'],['FINANCE_ADMIN']])
@pytest.mark.parametrize('view',['hr','admin','manager','payroll','employee'])
def test_query_role_cannot_grant_read_or_write(personal_case,monkeypatch,roles,view):
    case=personal_case
    monkeypatch.setattr(case[1],'execute',lambda *args,**kwargs:pytest.fail('Unauthorized personal SQL'))
    assert case[0].get(path(case),params={'actorRole':view},headers=headers(case,roles)).status_code==403
    result=case[0].post(path(case)+'/documents',params={'actorRole':view},headers=headers(case,roles),
        json={'documentType':'certificate','title':'Synthetic'})
    assert result.status_code==403


def test_reader_gets_only_tenant_documents_and_cannot_create(personal_case):
    case=personal_case
    response=case[0].get(path(case),headers=headers(case,['PERSONAL_LESEN']))
    assert response.status_code==200,response.text
    assert response.json()['source']=='database'
    assert [row['title'] for row in response.json()['documents']]==[case[3]]
    assert case[0].post(path(case)+'/documents',headers=headers(case,['PERSONAL_LESEN']),
        json={'documentType':'certificate','title':'Synthetic','createdBy':'forged'}).status_code==403
    assert case[0].get(path(case),headers={**headers(case,['PERSONAL_ADMIN']),'X-Tenant-ID':case[4]}).status_code==403
    assert case[0].get(path(case)).status_code==401


def test_writer_persists_verified_subject_and_empty_file_has_no_demo(personal_case):
    case=personal_case
    response=case[0].post(path(case)+'/documents',params={'actorRole':'employee'},headers=headers(case,['PERSONAL_BEARBEITEN']),
        json={'documentType':'certificate','title':'Synthetic persisted','createdBy':'forged','issuedAt':'2026-01-01'})
    assert response.status_code==201,response.text
    row=case[1].execute(text('SELECT tenant_id,created_by,title FROM domain_hr.employee_file_documents WHERE id=:id'),{'id':response.json()['id']}).one()
    assert tuple(row)==(case[3],'human-a','Synthetic persisted')
    empty=case[0].get(path(case)+'-empty',headers=headers(case,['PERSONAL_LESEN']))
    assert empty.status_code==200
    assert empty.json()['documents']==[] and empty.json()['source']=='database'


@pytest.mark.parametrize('operation',['read','write'])
def test_real_database_error_is_not_pilot_or_success(personal_case,monkeypatch,caplog,operation):
    case=personal_case
    execute=case[1].execute
    def failed(statement,*args,**kwargs):
        if 'domain_hr.employee_file_documents' in str(statement):
            return execute(text('SELECT * FROM synthetic_missing_personal_relation'))
        return execute(statement,*args,**kwargs)
    monkeypatch.setattr(case[1],'execute',failed)
    if operation=='read':
        response=case[0].get(path(case),headers=headers(case,['PERSONAL_LESEN']))
    else:
        response=case[0].post(path(case)+'/documents',headers=headers(case,['PERSONAL_BEARBEITEN']),
            json={'documentType':'certificate','title':'private-personal-marker'})
    assert response.status_code==503,response.text
    assert 'private-personal-marker' not in response.text+caplog.text
    assert 'synthetic_missing_personal_relation' not in response.text+caplog.text
    monkeypatch.setattr(case[1],'execute',execute)
    assert case[1].execute(text('SELECT count(*) FROM domain_hr.employee_file_documents WHERE tenant_id=:t AND employee_ref=:r'),{'t':case[3],'r':case[5]}).scalar_one()==1


@pytest.mark.parametrize('dates',[{'issuedAt':'2026-02-30'},{'issuedAt':'20260101'},
    {'issuedAt':'2026-04-01','validUntil':'2026-03-01'}])
def test_invalid_dates_are_rejected_before_persistence(personal_case,monkeypatch,dates):
    case=personal_case
    monkeypatch.setattr(case[1],'execute',lambda *args,**kwargs:pytest.fail('Invalid date reached SQL'))
    result=case[0].post(path(case)+'/documents',headers=headers(case,['PERSONAL_BEARBEITEN']),
        json={'documentType':'certificate','title':'Synthetic',**dates})
    assert result.status_code==422,result.text
