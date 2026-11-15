"""HTTP contract with explicit identity and database doubles; no PostgreSQL/RLS proof."""
import copy
from types import SimpleNamespace
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from app.api.v1.endpoints import rohware_schema as endpoint
from app.api.v1.endpoints import rohwarengruppen as groups
from app.core.database import get_db
from app.core.security import require_bearer_token

pytestmark = pytest.mark.unit
URL = '/api/v1/rohware/schemata'
TOKEN = {'Authorization': 'Bearer synthetic'}

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

class Result:
    def __init__(self, rows=(), rowcount=0):
        self.rows, self.rowcount = list(rows), rowcount
    def mappings(self): return self
    def fetchone(self): return self.rows[0] if self.rows else None
    def all(self): return self.rows
    def fetchall(self): return self.rows

class DB:
    def __init__(self):
        self.schemas = {'a': {'id': 'a', 'tenant_id': 'A', 'status': 'ENTWURF', 'gueltig_ab': '2026-01-01'},
                        'b': {'id': 'b', 'tenant_id': 'B', 'status': 'ENTWURF', 'gueltig_ab': '2026-01-01'}}
        self.lines = {'la': {'id': 'la', 'schema_id': 'a', 'positions_typ': 'GRUNDPREIS', 'bezeichnung': 'A', 'berechnungsformel': 'basis_preis', 'einheit': 'EUR/t'},
                      'lb': {'id': 'lb', 'schema_id': 'b', 'positions_typ': 'GRUNDPREIS', 'bezeichnung': 'B', 'berechnungsformel': 'basis_preis', 'einheit': 'EUR/t'}}
        self.calls = []
        self.commits = self.rollbacks = 0
        self.fail = None
    def rollback(self): self.rollbacks += 1
    def commit(self): self.commits += 1
    def execute(self, statement, params=None):
        sql = str(statement); p = params or {}; self.calls.append((sql, dict(p)))
        if self.fail == 'probe' or (self.fail == 'query' and not sql.startswith('SELECT 1')):
            raise RuntimeError('private SQL secret')
        if sql.startswith('SELECT 1'): return Result()
        if sql.startswith('SELECT id FROM domain_shared.rohware_abrechnungsschemata WHERE tenant_id = :tid'):
            return Result([v for v in self.schemas.values() if v['tenant_id'] == p['tid'] and v.get('schema_code') == p['nr']])
        if sql.startswith('SELECT * FROM domain_shared.rohware_abrechnungsschemata WHERE id = :id AND tenant_id = :tid'):
            v = self.schemas.get(p['id']); return Result([SimpleNamespace(_mapping=v)] if v and v['tenant_id'] == p['tid'] else [])
        if sql.startswith('SELECT * FROM domain_shared.rohware_abrechnungsschemata WHERE tenant_id = :tid'):
            return Result([SimpleNamespace(_mapping=v) for v in self.schemas.values() if v['tenant_id'] == p['tid'] and v.get('gruppe_id') == p.get('gid') and v.get('aktiv')])
        if sql.startswith('SELECT id FROM domain_shared.rohwarengruppen'):
            return Result([('ga',)] if p.get('tenant_id') == 'A' and p.get('value') in ('ga', 'GE') else [])
        tenant = p.get('tenant_id')
        if 'rohware_schema_lines' in sql:
            assert 's.tenant_id = :tenant_id' in sql
            parent = p.get('schema_id', p.get('id'))
            allowed = self.schemas.get(parent, {}).get('tenant_id') == tenant
            if sql.lstrip().startswith('SELECT *'):
                return Result([v for v in self.lines.values() if allowed and v['schema_id'] == parent])
            if sql.lstrip().startswith('DELETE'):
                line = self.lines.get(p['line_id'])
                if allowed and line and line['schema_id'] == parent:
                    del self.lines[p['line_id']]; return Result(rowcount=1)
                return Result()
            if sql.lstrip().startswith('INSERT'):
                if allowed: self.lines[p['id']] = dict(p); return Result(rowcount=1)
                return Result()
        if sql.lstrip().startswith('INSERT INTO domain_shared.rohware_abrechnungsschemata'):
            self.schemas[p['id']] = {'id': p['id'], 'tenant_id': tenant, 'name': p['name'], 'schema_code': p['code'], 'gruppe_id': p['group_id'], 'rohwaren_gruppe': 'GE', 'gueltig_ab': p['valid_from'], 'status': p['status'], 'aktiv': p['active'], 'schema_nr': p['code'], 'bezeichnung': p['name'], 'artikel_nr': p['article'], 'created_at': '2026-01-01T00:00:00'}
            return Result(rowcount=1)
        if sql.lstrip().startswith('UPDATE domain_shared.rohware_abrechnungsschemata'):
            assert 'tenant_id = :tenant_id' in sql
            row = self.schemas.get(p['id'])
            if row and row['tenant_id'] == tenant:
                if 'status = :status' in sql: row['status'] = p['status']; row['aktiv'] = p['active']
                else:
                    row.update({('name' if k == 'bezeichnung' else 'schema_code' if k == 'schema_nr' else k): v for k, v in p.items() if k not in ('id', 'tenant_id')})
                return Result(rowcount=1)
            return Result()
        if sql.lstrip().startswith('SELECT'):
            assert 'tenant_id = :tenant_id' in sql
            if 'id' in p:
                row = self.schemas.get(p['id'])
                return Result([row] if row and row['tenant_id'] == tenant else [])
            return Result([v for v in self.schemas.values() if v['tenant_id'] == tenant])
        raise AssertionError(sql)

@pytest.fixture
def client():
    db = DB(); identity = {'tenant': 'A', 'verified': True}
    async def boundary(request: Request):
        if request.headers.get('authorization') != TOKEN['Authorization']: raise HTTPException(401)
        if identity['verified']:
            request.state.tenant_id = identity['tenant']; request.state.tenant_verified = True
        return 'synthetic'
    app = FastAPI(); app.include_router(endpoint.router, prefix=URL); app.include_router(groups.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_bearer_token] = boundary
    app.dependency_overrides[endpoint.SCHREIBEN['LAGER'][0].dependency] = lambda: None
    with TestClient(app, raise_server_exceptions=False) as c: yield c, db, identity

@pytest.mark.parametrize('method,path,body', [
    ('get', '/b', None), ('patch', '/b', {'name':'x'}),
    ('post', '/b/aktivieren', None), ('post', '/b/archivieren', None),
    ('get', '/b/lines', None), ('post', '/b/lines', {}),
    ('delete', '/b/lines/lb', None), ('post', '/b/testrechnung', {}),
    ('delete', '/a/lines/lb', None),
])
def test_foreign_ids_return_404_without_mutation(client, method, path, body):
    c, db, _ = client; before = copy.deepcopy((db.schemas, db.lines))
    r = c.request(method, URL + path, headers=TOKEN, json=body)
    assert r.status_code == 404, r.text
    assert (db.schemas, db.lines) == before

def test_list_and_details_use_verified_tenant(client):
    c, db, identity = client
    assert [x['id'] for x in c.get(URL, headers=TOKEN, params={'tenant_id':'B'}).json()] == ['a']
    assert c.get(URL + '/a', headers=TOKEN).json()['lines'][0]['id'] == 'la'
    identity['tenant'] = 'B'
    assert [x['id'] for x in c.get(URL, headers=TOKEN).json()] == ['b']
    assert c.get(URL + '/a', headers=TOKEN).status_code == 404

@pytest.mark.parametrize('path,method', [('', 'post'), ('/a', 'patch'), ('/a/lines','post'), ('/a/testrechnung','post')])
def test_conflicting_payload_rejected(client, path, method):
    c, db, _ = client; before = copy.deepcopy((db.schemas, db.lines))
    assert c.request(method, URL + path, headers=TOKEN, json={'tenant_id':'B'}).status_code == 403
    assert (db.schemas, db.lines) == before
    assert not db.calls

def test_identity_required(client):
    c, db, identity = client
    assert c.get(URL).status_code == 401
    identity['verified'] = False
    assert c.get(URL, headers=TOKEN).status_code == 403
    assert not db.calls

def test_same_tenant_calculation_and_line_deletion(client):
    c, db, _ = client
    assert c.post(URL + '/a/testrechnung', headers=TOKEN, json={'basis_preis': 100}).json()['gesamt_preis'] == 100
    assert c.delete(URL + '/a/lines/la', headers=TOKEN).status_code == 204
    assert 'la' not in db.lines and 'lb' in db.lines


def test_own_lifecycle_and_state_invariants(client):
    c, db, _ = client
    foreign = copy.deepcopy((db.schemas['b'], db.lines['lb']))
    response = c.post(URL, headers=TOKEN, json={'name': 'Getreide', 'rohwaren_gruppe': 'GE', 'gueltig_ab': '2026-01-01'})
    assert response.status_code == 201, response.text
    schema_id = response.json()['id']
    assert db.schemas[schema_id]['tenant_id'] == 'A'
    detail = c.get(URL + '/' + schema_id, headers=TOKEN)
    assert detail.status_code == 200 and detail.json()['status'] == 'ENTWURF'
    patch = c.patch(URL + '/' + schema_id, headers=TOKEN, json={'name': 'Raps'})
    assert patch.status_code == 200 and patch.json()['name'] == 'Raps'
    line = c.post(URL + '/' + schema_id + '/lines', headers=TOKEN,
                  json={'bezeichnung': 'Grundpreis', 'berechnungsformel': 'basis_preis'})
    assert line.status_code == 201, line.text
    line_id = line.json()['id']
    assert db.lines[line_id]['tenant_id'] == 'A'
    assert c.get(URL + '/' + schema_id + '/lines', headers=TOKEN).json()[0]['id'] == line_id
    assert c.post(URL + '/' + schema_id + '/aktivieren', headers=TOKEN).json()['status'] == 'AKTIV'
    before = copy.deepcopy(db.schemas[schema_id])
    assert c.patch(URL + '/' + schema_id, headers=TOKEN, json={'name':'verboten'}).status_code == 422
    assert c.post(URL + '/' + schema_id + '/aktivieren', headers=TOKEN).status_code == 422
    assert db.schemas[schema_id] == before
    assert c.delete(URL + '/' + schema_id + '/lines/' + line_id, headers=TOKEN).status_code == 204
    assert c.get(URL + '/' + schema_id + '/lines', headers=TOKEN).json() == []
    assert c.post(URL + '/' + schema_id + '/archivieren', headers=TOKEN).json()['status'] == 'ARCHIV'
    before = copy.deepcopy(db.schemas[schema_id])
    assert c.post(URL + '/' + schema_id + '/archivieren', headers=TOKEN).status_code == 422
    assert db.schemas[schema_id] == before
    assert (db.schemas['b'], db.lines['lb']) == foreign
    assert db.commits == 6

@pytest.mark.parametrize('failure', ['probe', 'query'])
def test_db_failure_rolls_back_and_redacts_details(client, failure):
    c, db, _ = client
    db.fail = failure
    response = c.get(URL, headers=TOKEN)
    assert response.status_code == 503
    assert 'private' not in response.text and 'SQL' not in response.text
    assert db.rollbacks == 1 and db.commits == 0



def test_group_route_uses_verified_parent_and_active_catalog(client):
    c, db, identity = client
    db.schemas['a'].update({'gruppe_id':'ga', 'aktiv':True, 'schema_nr':'S-A', 'bezeichnung':'A', 'artikel_nr':None, 'created_at':'2026-01-01T00:00:00'})
    r = c.get('/api/v1/rohware/gruppen/ga/schemata', headers=TOKEN)
    assert r.status_code == 200, r.text
    assert [row['id'] for row in r.json()] == ['a']
    identity['tenant'] = 'B'
    assert c.get('/api/v1/rohware/gruppen/ga/schemata', headers=TOKEN).status_code == 404
    assert c.get('/api/v1/rohware/gruppen/ga/schemata').status_code == 401


def test_legacy_create_shares_canonical_active_catalog(client):
    c, db, _ = client
    r = c.post('/api/v1/rohware/gruppen/schemata', headers=TOKEN,
               json={'schema_nr':'GE1', 'bezeichnung':'Getreide', 'gruppe_id':'ga'})
    assert r.status_code == 201, r.text
    schema_id = r.json()['id']
    assert db.schemas[schema_id]['status'] == 'AKTIV'
    assert db.schemas[schema_id]['gueltig_ab'] is not None
    detail = c.get(URL + '/' + schema_id, headers=TOKEN)
    assert detail.status_code == 200 and detail.json()['schema_code'] == 'GE1'
    assert c.get('/api/v1/rohware/gruppen/ga/schemata', headers=TOKEN).json()[0]['id'] == schema_id


@pytest.mark.parametrize('invalid', [
    {'version': None}, {'version': '2'}, {'version': 0}, {'version': True},
    {'version': 2147483648}, {'name': ''}, {'name': '  '}, {'name': 'x' * 201},
    {'schema_code': ''}, {'schema_code': 'x' * 21}, {'gueltig_ab': '2026-02-30'},
    {'gueltig_bis': '20260101'}, {'gueltig_ab': '2026-03-01', 'gueltig_bis': '2026-02-01'},
    {'gruppe_id': None}, {'rohwaren_gruppe': []},
])
def test_invalid_header_rejected_before_insert(client, invalid):
    c, db, _ = client
    body = {'name': 'Getreide', 'rohwaren_gruppe': 'GE'}
    if 'gruppe_id' in invalid: body.pop('rohwaren_gruppe')
    body.update(invalid)
    before = copy.deepcopy((db.schemas, db.lines))
    response = c.post(URL, headers=TOKEN, json=body)
    assert response.status_code == 422, response.text
    assert not db.calls and db.commits == 0
    assert (db.schemas, db.lines) == before

@pytest.mark.parametrize('invalid', [
    {'version': 'invalid'}, {'name': ''}, {'gueltig_ab': '2026-02-30'},
    {'gueltig_bis': '2025-12-31'},
])
def test_invalid_patch_never_writes_and_checks_merged_dates(client, invalid):
    c, db, _ = client
    before = copy.deepcopy((db.schemas, db.lines))
    response = c.patch(URL + '/a', headers=TOKEN, json=invalid)
    assert response.status_code == 422, response.text
    assert not any(sql.lstrip().startswith(('UPDATE', 'INSERT', 'DELETE')) for sql, _ in db.calls)
    assert db.commits == 0 and (db.schemas, db.lines) == before


@pytest.mark.parametrize('field,value', [('schema_nr', '  '), ('bezeichnung', '  '), ('bezeichnung', 'x' * 201)])
def test_legacy_create_rejects_invalid_header_without_writes(client, field, value):
    c, db, _ = client
    body = {'schema_nr': 'GE1', 'bezeichnung': 'Getreide', 'gruppe_id': 'ga'}
    body[field] = value
    before = copy.deepcopy((db.schemas, db.lines))
    response = c.post('/api/v1/rohware/gruppen/schemata', headers=TOKEN, json=body)
    assert response.status_code == 422, response.text
    assert not any(sql.lstrip().startswith(('UPDATE', 'INSERT', 'DELETE')) for sql, _ in db.calls)
    assert db.commits == 0 and (db.schemas, db.lines) == before


def test_legacy_activation_uses_business_day(monkeypatch):
    from datetime import date
    from unittest.mock import Mock
    from app.services import rohware_schema_service as schemas
    business_day = date(2026, 12, 1)
    monkeypatch.setattr(schemas, 'business_today', lambda: business_day)
    db = Mock()
    schemas.create(db, 'tenant', schema_code='S', name='Probe', group='own', activate=True)
    assert db.execute.call_args.args[1]['valid_from'] == business_day
    assert db.execute.call_args.args[1]['active'] is True
