import os
import pytest
import importlib.util
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.core.database import engine, get_db
from app.core.tenant_context import tenant_scope
from app.auth import deps, deps_oidc
from app.api.v1.endpoints.waage import router
from app.api.v1.endpoints.weighing_tickets import router as ticket_router
from scripts.provision_db_roles import waage_only_grant_plan

@pytest.fixture(scope='session', autouse=True)
def _seed_contract_test_tenants():
    # This test creates all of its own rows in the outer rollback transaction.
    yield


base = Path('alembic/versions')
def load(name):
    spec = importlib.util.spec_from_file_location(name, base / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(os.getenv("WAAGE_TENANT_SQL_TEST") != "1", reason="requires coordinated valeo_probe rollback window")
def test_waage_tenant_http_rls_and_migration_rollback():
    conn = engine.connect()
    if conn.execute(text("SELECT current_database()")).scalar_one() != 'valeo_probe':
        conn.close()
        raise RuntimeError("Waage integration test requires the shared valeo_probe")
    conn.rollback()
    original_revision = conn.execute(text('SELECT version_num FROM alembic_version')).scalar_one()
    conn.rollback()
    transaction = conn.begin()
    conn.execute(text("SET LOCAL lock_timeout = '5s'"))
    conn.execute(text("SET LOCAL statement_timeout = '30s'"))
    try:
        conn.execute(text("INSERT INTO domain_ops.ops_waagen (id, standort, typ, max_kapazitaet) VALUES ('waage-legacy-unassigned-test', 'Test', 'LKW', 1)"))
        context = MigrationContext.configure(conn)
        with Operations.context(context):
            load('crm_activity_canonical_20261029').upgrade()
            load('waage_tenant_20261030').upgrade()
        conn.execute(text("INSERT INTO domain_shared.tenants (id,name,domain) VALUES ('waage-test-a','Synthetic Waage A','waage-a.invalid'), ('waage-test-b','Synthetic Waage B','waage-b.invalid')"))
        app = FastAPI()
        app.include_router(router)
        app.include_router(ticket_router, prefix="/weighing-tickets")
        def user(request: Request):
            tenant = request.headers.get('x-test-tenant', '')
            role = request.headers.get('x-test-role', 'LAGER_BEARBEITEN')
            return {'sub': 'verified-test-subject', 'roles': [role], 'raw': {'tenant_id': tenant}}
        async def db_override(request: Request):
            with tenant_scope(request.headers.get('x-test-tenant', '') or 'test-no-tenant', reason='waage-tenant-test'):
                session = Session(bind=conn, join_transaction_mode='create_savepoint')
                try:
                    yield session
                finally:
                    session.close()
        from app.core.security import require_bearer_token
        def bearer(request: Request):
            declared = user(request)
            request.state.tenant_verified = bool(declared['raw']['tenant_id'])
            request.state.tenant_id = declared['raw']['tenant_id']
            request.state.token_claims = {'sub': declared['sub'], **declared['raw']}
            return 'explicit-synthetic-test-token'
        app.dependency_overrides[require_bearer_token] = bearer
        app.dependency_overrides[deps.get_current_user] = user
        app.dependency_overrides[deps_oidc.get_current_user] = user
        app.dependency_overrides[get_db] = db_override
        with TestClient(app) as client:
            a = {'x-test-tenant': 'waage-test-a'}
            b = {'x-test-tenant': 'waage-test-b'}
            payload = {'standort': 'Test', 'typ': 'LKW', 'max_kapazitaet': 20}
            response = client.post('/waage/waagen', headers=a, json=payload)
            assert response.status_code == 201, ('create', response.status_code, response.text)
            ident = response.json()['id']
            assert client.get(f'/waage/waagen/{ident}', headers=a).status_code == 200
            assert client.get(f'/waage/waagen/{ident}', headers=b).status_code == 404
            assert client.get('/waage/waagen/waage-legacy-unassigned-test', headers=a).status_code == 404
            assert conn.execute(text("SELECT tenant_id IS NULL FROM domain_ops.ops_waagen WHERE id='waage-legacy-unassigned-test'")).scalar_one()
            assert client.patch(f'/waage/waagen/{ident}', headers=b, json={'typ': 'Fremd'}).status_code == 404
            assert client.delete(f'/waage/waagen/{ident}', headers=b).status_code == 404
            assert client.get(f'/waage/waagen/{ident}/kalibrierung', headers=b).status_code == 404
            assert client.get(f'/waage/waagen/{ident}/kalibrierung', headers=a).status_code == 200
            assert client.post('/waage/waagen', headers=a, json={**payload, 'tenant_id': 'waage-test-b'}).status_code == 422
            assert client.post('/waage/waagen', headers={'x-test-tenant': ''}, json=payload).status_code == 403
            assert client.post('/waage/waagen', headers={'x-test-tenant': 'waage-test-a', 'x-test-role': 'LAGER_LESEN'}, json=payload).status_code == 403
            assert client.post('/waage/wiegungen', headers=b, json={'waage_id': ident}).status_code == 410
            assert client.post('/waage/waagen/import/ascii', headers=b, data={'waage_id': ident}, files={'file': ('test.txt', b'ignored')}).status_code == 404
            assert client.patch(f'/waage/waagen/{ident}', headers=a, json={'typ': 'Aktualisiert'}).status_code == 200
            canonical = {'ticket_number':'SCALE-REF-FOREIGN', 'vehicle_plate':'TEST-123', 'gross_weight':1000, 'tare_weight':400, 'net_weight':600, 'scale_id':ident, 'reference_doc':'source-lot'}
            denied_ticket = client.post('/weighing-tickets/', headers=b, json=canonical)
            assert denied_ticket.status_code == 404, denied_ticket.text
            denied_dual = client.post('/waage/wiegungen/dual', headers=b, json={'waage_id':ident, 'kfz_kennzeichen':'TEST-123', 'wiegung_erweitert': {'brutto_kg':1000,'tara_kg':400}})
            assert denied_dual.status_code == 404, denied_dual.text
            assert conn.execute(text("SELECT count(*) FROM domain_inventory.weighing_tickets WHERE tenant_id='waage-test-b'")).scalar_one() == 0
            calibration = {'letztes_eichdatum': '2026-10-01', 'naechste_eichfaelligkeit': '2027-10-01', 'eichamt': 'Synthetic', 'zertifikat_nr': 'PROBE'}
            saved = client.patch(f'/waage/waagen/{ident}/kalibrierung', headers=a, json=calibration)
            assert saved.status_code == 200, saved.text
            assert saved.json()['zertifikat_nr'] == 'PROBE'
            assert client.patch(f'/waage/waagen/{ident}/kalibrierung', headers=a, json={'naechste_eichfaelligkeit': '2020-01-01'}).status_code == 422
            assert client.get(f'/waage/waagen/{ident}/kalibrierung', headers=a).json()['naechste_eichfaelligkeit'] == '2027-10-01'
            import_id = client.post('/waage/waagen', headers=a, json=payload).json()['id']
            row = 'W;ASCII-PROBE-1;2026-10-30;08:00;1000;400;600;TEST-123;source-supplier;;WW;source-lot;source-silo;14.5;78;1.2;0'
            def upload(content, tolerant):
                return client.post('/waage/waagen/import/ascii', headers=a,
                    data={'waage_id': import_id, 'fehler_toleranz': str(tolerant).lower()},
                    files={'file': ('probe.txt', content.encode())})
            first = upload(row + '\nQ;ASCII-PROBE-1;Protein;11.5;%', False)
            assert first.status_code == 200, first.text
            assert first.json()['imported'] == 1
            ticket_id = first.json()['wiegung_ids'][0]
            repeat = upload(row + '\nQ;ASCII-PROBE-1;Protein;11.5;%', False)
            assert repeat.json()['replayed'] == 1
            assert repeat.json()['imported'] == 0
            before = conn.execute(text('SELECT count(*) FROM domain_inventory.weighing_tickets WHERE tenant_id=:t'), {'t':'waage-test-a'}).scalar_one()
            strict = upload(row.replace('ASCII-PROBE-1', 'ASCII-PROBE-2') + '\nBROKEN', False)
            assert strict.status_code == 422
            assert conn.execute(text('SELECT count(*) FROM domain_inventory.weighing_tickets WHERE tenant_id=:t'), {'t':'waage-test-a'}).scalar_one() == before
            partial = upload('BROKEN', True)
            assert partial.json()['skipped'] == 1
            queue_id = partial.json()['errors'][0]['id']
            assert upload('BROKEN', False).status_code == 422
            assert len(client.get('/waage/waagen/import/fehlerqueue', headers=a).json()) == 1
            assert client.get('/waage/waagen/import/fehlerqueue', headers=b).json() == []
            assert client.post(f'/waage/waagen/import/fehlerqueue/{queue_id}/retry', headers=b).status_code == 404
            retried = client.post(f'/waage/waagen/import/fehlerqueue/{queue_id}/retry', headers=a)
            assert retried.status_code == 200, retried.text
            assert retried.json()['entry']['retry_count'] == 1
            assert client.delete(f'/waage/waagen/import/fehlerqueue/{queue_id}', headers=b).status_code == 404
            assert client.delete(f'/waage/waagen/import/fehlerqueue/{queue_id}', headers=a).status_code == 200
            assert client.get('/waage/waagen/import/fehlerqueue', headers=a).json() == []
            assert upload('BROKEN', True).json()['replayed'] == 1
            assert client.delete(f'/waage/waagen/{import_id}', headers=a).status_code == 409
            saved_ticket = conn.execute(text('SELECT scale_id, net_weight, quality_data FROM domain_inventory.weighing_tickets WHERE id=:id'), {'id':ticket_id}).one()
            assert saved_ticket.scale_id == import_id and float(saved_ticket.net_weight) == 600
            assert saved_ticket.quality_data['additional'][0]['parameter'] == 'Protein'
            for invalid_sql in [
                "INSERT INTO domain_ops.ops_waagen (id,standort,typ,max_kapazitaet) VALUES ('waage-new-null-denied','T','T',1)",
                "UPDATE domain_ops.ops_waagen SET status='edited' WHERE id='waage-legacy-unassigned-test'",
            ]:
                denied_write = conn.begin_nested()
                try:
                    with pytest.raises(Exception) as denied:
                        conn.execute(text(invalid_sql))
                    assert 'ck_ops_waagen_tenant_nonblank' in str(denied.value)
                finally:
                    denied_write.rollback()
            conn.execute(text('GRANT SELECT ON domain_ops.ops_wiegungen TO valeo_app'))
            try:
                waage_only_grant_plan(conn)
                raise AssertionError('unsafe other table should prevent schema grant')
            except RuntimeError:
                pass
            conn.execute(text('REVOKE SELECT ON domain_ops.ops_wiegungen FROM valeo_app'))
            grants = waage_only_grant_plan(conn)
            assert len(grants) == 4
            for grant in grants: conn.execute(text(grant))
            with tenant_scope('waage-test-a', reason='waage-tenant-test'):
                conn.execute(text('SET LOCAL ROLE valeo_app'))
                assert conn.execute(text('SELECT public.waage_reference_allowed(:id)'), {'id':ident}).scalar_one() is True
                assert conn.execute(text("SELECT public.waage_reference_allowed('waage-legacy-unassigned-test')")).scalar_one() is False
                assert conn.execute(text("SELECT public.waage_reference_allowed('EXTERNAL-NAME')")).scalar_one() is True
                visible_a = conn.execute(text('SELECT count(*) FROM domain_ops.ops_waagen WHERE id=:id'), {'id': ident}).scalar_one()
            with tenant_scope('waage-test-b', reason='waage-tenant-test'):
                assert conn.execute(text('SELECT public.waage_reference_allowed(:id)'), {'id':ident}).scalar_one() is False
                assert conn.execute(text('SELECT count(*) FROM domain_ops.waage_import_entries')).scalar_one() == 0
                visible_b = conn.execute(text('SELECT count(*) FROM domain_ops.ops_waagen WHERE id=:id'), {'id': ident}).scalar_one()
            with tenant_scope('waage-test-a', reason='waage-tenant-test'):
                nested = conn.begin_nested()
                try:
                    conn.execute(text("INSERT INTO domain_ops.ops_waagen (id, tenant_id, standort, typ, max_kapazitaet) VALUES ('foreign-write-test', 'waage-test-b', 'X', 'X', 1)"))
                    raise AssertionError('RLS allowed cross-tenant insert')
                except Exception as exc:
                    if isinstance(exc, AssertionError):
                        raise
                finally:
                    nested.rollback()
            conn.execute(text('RESET ROLE'))
            assert (visible_a, visible_b) == (1, 0), ('rls', visible_a, visible_b)
            conn.execute(text("INSERT INTO domain_ops.ops_wiegungen (id, kennzeichen, artikel, brutto, tara, netto, zeitstempel, waage_id) VALUES ('waage-test-child', 'T', 'T', 2, 1, 1, now(), :id)"), {'id': ident})
            assert client.delete(f'/waage/waagen/{ident}', headers=a).status_code == 409
            conn.execute(text("DELETE FROM domain_ops.ops_wiegungen WHERE id='waage-test-child'"))
            assert client.delete(f'/waage/waagen/{ident}', headers=a).status_code == 204
        print('HTTP tenant/roles/identity, foreign legacy reference, CRUD and valeo_app RLS: passed')
    finally:
        transaction.rollback()
        conn.close()
        with engine.connect() as check:
            assert check.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == original_revision
            assert check.execute(text("SELECT to_regclass('domain_ops.waage_import_entries') IS NULL")).scalar_one()
            assert check.execute(text("SELECT to_regprocedure('public.waage_reference_allowed(text)') IS NULL")).scalar_one()
            assert check.execute(text("SELECT count(*) FROM domain_ops.ops_waagen WHERE id='waage-legacy-unassigned-test'")).scalar_one() == 0
        print('Outer transaction rolled back; revision and temporary table/function/rows unchanged')
