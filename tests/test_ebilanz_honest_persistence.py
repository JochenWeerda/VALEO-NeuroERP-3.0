"""Real eBilanz draft persistence, tenant/role guards and no simulated authority receipts."""
import os
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.endpoints import ebilanz_elster
from app.auth.deps import get_current_user
from app.core.database import get_db

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]
PAYLOAD = {"wirtschaftsjahr": 2025, "bilanzart": "HGB", "berichtsperiode_von": "2025-01-01",
           "berichtsperiode_bis": "2025-12-31", "steuernummer": "Testnummer", "finanzamt_nr": "Testamt"}


@pytest.fixture
def context():
    strict = os.getenv('PYTEST_REQUIRE_DB_STRICT') == '1'
    url = os.getenv('TEST_DATABASE_URL')
    if not url and (strict or os.getenv('CI') == 'true'):
        url = os.getenv('DATABASE_URL')
    if not url:
        if strict:
            pytest.fail('The CI job must provide its existing PostgreSQL database')
        pytest.skip('TEST_DATABASE_URL required; no database is created')
    engine = create_engine(url)
    queries = []
    event.listen(engine, 'before_cursor_execute', lambda conn, cursor, sql, parameters, ctx, many: queries.append(sql))
    with engine.connect() as conn:
        outer = conn.begin()
        db = Session(bind=conn, join_transaction_mode='create_savepoint')
        tenant, foreign = str(uuid.uuid4()), str(uuid.uuid4())
        for tid in (tenant, foreign):
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id,:name,:domain,TRUE)'),
                       {'id': tid, 'name': 'Export persistence test', 'domain': tid+'.test.invalid'})
        db.commit()
        app = FastAPI()
        app.include_router(ebilanz_elster.router)
        user = {'sub': 'export-test', 'roles': ['FINANCE_ADMIN']}
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user] = lambda: user
        with TestClient(app) as client:
            client.headers['X-Tenant-ID'] = tenant
            yield db, client, tenant, foreign, user, queries
        db.close()
        outer.rollback()
    engine.dispose()


def create(context):
    response = context[1].post('/ebilanz/export/erstellen', json=PAYLOAD)
    assert response.status_code == 201, response.text
    return response.json()['export_id']


def _xbrl_payload():
    return {'entity_identifier': 'Test-Entity', 'entity_scheme': 'https://example.invalid/entity',
            'facts': dict(zip(ebilanz_elster.CORE_FIELDS,
                             ['Test & Betrieb', 'Deutschland', '2025-01-01', '2025-12-31']))}


def test_xbrl_real_download_with_tenant_roles_and_no_status_mutation(context):
    from xml.etree import ElementTree as ET
    db, client, tenant, foreign, user, queries = context
    export_id = create(context)
    row = db.execute(text('SELECT taxonomie_version FROM domain_finance.ebilanz_exports WHERE id=:id'), {'id':export_id}).scalar()
    assert row == '6.9'
    url = f'/ebilanz/export/{export_id}/xbrl-entwurf'
    response = client.post(url, json=_xbrl_payload())
    assert response.status_code == 200, response.text
    assert response.headers['x-xbrl-status'] == 'DRAFT_UNVALIDATED'
    assert response.headers['cache-control'] == 'no-store'
    assert ET.fromstring(response.content).tag == '{http://www.xbrl.org/2003/instance}xbrl'
    assert client.post(url, json=_xbrl_payload(), headers={'X-Tenant-ID':foreign}).status_code == 404
    user['roles'] = ['FINANCE_READ']
    assert client.post(url, json=_xbrl_payload()).status_code == 403
    user['roles'] = ['FINANCE_ADMIN']
    assert db.execute(text('SELECT status,elster_transfer_ticket,xbrl_paketgroesse_kb FROM domain_finance.ebilanz_exports WHERE id=:id'), {'id':export_id}).one() == ('ERSTELLT', None, 0)


def test_xbrl_conflicting_period_and_historical_version_are_rejected(context):
    db, client, tenant, foreign, user, queries = context
    export_id = create(context); payload = _xbrl_payload()
    payload['facts'][ebilanz_elster.CORE_FIELDS[3]] = '2025-12-30'
    url = f'/ebilanz/export/{export_id}/xbrl-entwurf'
    assert client.post(url, json=payload).status_code == 422
    db.execute(text("UPDATE domain_finance.ebilanz_exports SET taxonomie_version='6.7' WHERE id=:id"), {'id':export_id})
    assert client.post(url, json=_xbrl_payload()).status_code == 409


def test_official_catalog_paging_and_unknown_fact_precheck(context):
    client = context[1]
    assert len(client.get('/ebilanz/taxonomie-felder?limit=2&skip=2').json()) == 2
    assert client.get('/ebilanz/taxonomie-felder?limit=1001').status_code == 422
    assert client.get('/ebilanz/taxonomie-felder?skip=3944').json() == []
    fields = _xbrl_payload()['facts']; fields['de-gcd:invented'] = 'value'
    body = client.post('/ebilanz/validieren', json={'felder':fields}).json()
    assert body['valid'] is False and any('Unbekanntes Konzept' in text for text in body['warnungen'])


def test_real_draft_no_request_ddl_or_invented_package(context):
    db, client, tenant, foreign, user, queries = context
    export_id = create(context)
    row = db.execute(text('SELECT * FROM domain_finance.ebilanz_exports WHERE id=:id'), {'id':export_id}).mappings().one()
    assert row['tenant_id'] == tenant and row['status'] == 'ERSTELLT'
    assert row['xbrl_paketgroesse_kb'] == 0 and row['elster_transfer_ticket'] is None
    for path in ('meldungen', 'exports'):
        listing = client.get('/ebilanz/'+path).json()
        assert len(listing) == 1 and listing[0]['export_id'] == export_id
        assert listing[0]['uebertragung_bestaetigt'] is False
        assert client.get('/ebilanz/'+path, headers={'X-Tenant-ID':foreign}).json() == []
    assert not any(q.lstrip().upper().startswith(('CREATE ', 'ALTER ', 'DROP ')) for q in queries)


@pytest.mark.parametrize('suffix', ['validieren', 'uebertragen'])
def test_unimplemented_validation_and_transmission_are_explicit(context, suffix):
    db, client, tenant, foreign, user, queries = context
    export_id = create(context)
    response = client.post(f'/ebilanz/export/{export_id}/{suffix}')
    assert response.status_code == 409
    assert client.post(f'/ebilanz/export/{export_id}/{suffix}', headers={'X-Tenant-ID':foreign}).status_code == 404
    assert client.post(f'/ebilanz/export/{uuid.uuid4()}/{suffix}').status_code == 404
    row = db.execute(text('SELECT status,elster_transfer_ticket,uebertragen_am FROM domain_finance.ebilanz_exports WHERE id=:id'), {'id':export_id}).one()
    assert tuple(row) == ('ERSTELLT', None, None)


def test_historical_simulator_record_is_not_an_authority_receipt(context):
    db, client, tenant, foreign, user, queries = context
    export_id = create(context)
    db.execute(text("UPDATE domain_finance.ebilanz_exports SET status='UEBERTRAGEN',elster_transfer_ticket='OLD-SIMULATION',xbrl_paketgroesse_kb=42,uebertragen_am=NOW() WHERE id=:id"), {'id':export_id})
    db.commit()
    result = client.get(f'/ebilanz/export/{export_id}/uebertragungsstatus').json()
    assert result['status'] == 'NICHT_BESTAETIGT' and result['ticket'] is None
    assert result['uebertragung_bestaetigt'] is False
    assert client.get('/ebilanz/meldungen').json()[0]['xbrl_paketgroesse_kb'] == 0
    assert db.execute(text('SELECT elster_transfer_ticket FROM domain_finance.ebilanz_exports WHERE id=:id'), {'id':export_id}).scalar() == 'OLD-SIMULATION'
    assert client.get(f'/ebilanz/export/{export_id}/uebertragungsstatus',headers={'X-Tenant-ID':foreign}).status_code == 404


def test_commit_failure_rolls_back_insert_and_never_returns_201(context,monkeypatch):
    db, client, tenant, foreign, user, queries = context
    def fail():
        raise SQLAlchemyError('Injected commit failure')
    with monkeypatch.context() as patch:
        patch.setattr(db, 'commit', fail)
        response = client.post('/ebilanz/export/erstellen', json=PAYLOAD)
        assert response.status_code == 503
    assert db.execute(text('SELECT count(*) FROM domain_finance.ebilanz_exports WHERE tenant_id=:tid'), {'tid':tenant}).scalar() == 0


@pytest.mark.parametrize('path', ['meldungen','exports','export/missing/uebertragungsstatus','elster/ustva'])
def test_database_error_is_503_not_empty_list_or_missing_object(context,monkeypatch,path):
    db, client, tenant, foreign, user, queries = context
    def fail(*args,**kwargs):
        raise SQLAlchemyError('Injected read failure')
    monkeypatch.setattr(db,'execute',fail)
    response = client.get('/ebilanz/'+path)
    assert response.status_code == 503
    assert 'Injected' not in response.text


def test_finance_read_role_cannot_write_or_transmit(context):
    db, client, tenant, foreign, user, queries = context
    export_id = create(context)
    user['roles'] = ['FINANCE_LESEN']
    before = len(queries)
    assert client.post('/ebilanz/export/erstellen',json=PAYLOAD).status_code == 403
    assert client.post(f'/ebilanz/export/{export_id}/uebertragen').status_code == 403
    assert client.post(f'/ebilanz/export/{export_id}/validieren').status_code == 403
    assert len(queries) == before
    assert client.get('/ebilanz/exports').status_code == 200


def test_ustva_cannot_create_simulated_transfer_record(context):
    db, client, tenant, foreign, user, queries = context
    before = len(queries)
    response = client.post('/ebilanz/elster/ustva',json={'steuernummer':'Testnummer','finanzamt_nr':'Testamt','voranmeldungszeitraum':'2025-01'})
    assert response.status_code == 409 and 'nichts uebertragen' in response.json()['detail']
    assert len(queries) == before


@pytest.mark.parametrize('params',['limit=0','limit=1001','skip=-1'])
def test_pagination_rejects_unbounded_or_negative_requests(context,params):
    assert context[1].get('/ebilanz/exports?'+params).status_code == 422


@pytest.mark.parametrize('changes',[{'berichtsperiode_von':'2026-01-01'}, {'bilanzart':'made-up'}, {'steuernummer':'   '}])
def test_invalid_draft_never_persists(context,changes):
    db, client, tenant, foreign, user, queries = context
    assert client.post('/ebilanz/export/erstellen',json={**PAYLOAD,**changes}).status_code == 422
    assert db.execute(text('SELECT count(*) FROM domain_finance.ebilanz_exports WHERE tenant_id=:tid'), {'tid':tenant}).scalar() == 0


def test_missing_and_blank_required_fields_are_not_valid(context):
    result = context[1].post('/ebilanz/validieren',json={'felder':{key:' ' for key in ebilanz_elster._GCD_PFLICHTFELDER}}).json()
    assert result['valid'] is False and set(result['fehlende_felder']) == set(ebilanz_elster.CORE_FIELDS)
    ready = context[1].get('/ebilanz/eric-readiness').json()
    assert ready['repo_contract_ready'] is False and ready['status'] == 'NOT_READY_EXTERNAL_GATE'
