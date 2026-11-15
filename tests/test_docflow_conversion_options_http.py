from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import docflow
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_service import DocflowService


@pytest.fixture
def boundary(monkeypatch):
    db = MagicMock()
    seen = []
    state = {'source_type': 'sales_order'}

    def header(svc, doc_id):
        seen.append(('header', svc.tenant_id, doc_id))
        if doc_id != 'own' or svc.tenant_id != 'tenant-a':
            return None
        return {'doc_type': state['source_type'], 'version': 3}

    def items(svc, doc_id):
        seen.append(('items', svc.tenant_id, doc_id))
        return [{'id': 'p1', 'line_number': 1, 'article_number': 'A-1', 'description': 'Weizen',
                 'unit': 'kg', 'quantity': 10, 'unit_price': 123, 'tax_code': 'secret'}]

    monkeypatch.setattr(DocflowService, 'fetch_header', header)
    monkeypatch.setattr(DocflowService, 'fetch_items', items)
    monkeypatch.setattr(DocflowService, 'umgewandelte_mengen', lambda svc, doc_id, relation: {'p1': Decimal('4')})
    app = FastAPI()
    app.include_router(docflow.router, prefix='/api/v1/docflow')
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: 'tenant-a'
    with TestClient(app, raise_server_exceptions=False) as client:
        yield app, client, db, seen, state


def login(app, *roles):
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'test-user', 'roles': list(roles)}


def read(client, doc_id='own', **params):
    return client.get(f'/api/v1/docflow/{doc_id}/conversion-options', params={'target_doc_type': 'sales_delivery', **params})


def test_ohne_anmeldung_401(boundary):
    app, client, db, seen, _ = boundary
    response = read(client)
    assert response.status_code == 401
    assert seen == []
    db.execute.assert_not_called()


def test_ohne_zielbearbeitung_403_vor_quellzugriff(boundary):
    app, client, db, seen, _ = boundary
    login(app, 'SALES_LESEN')
    assert read(client).status_code == 403
    assert seen == []
    db.execute.assert_not_called()


def test_ohne_quellleserecht_403(boundary):
    app, client, db, seen, state = boundary
    login(app, 'SALES_BEARBEITEN')
    state['source_type'] = 'purchase_order'
    assert read(client).status_code == 403
    assert seen == [('header', 'tenant-a', 'own')]
    db.execute.assert_not_called()


def test_fremder_tenant_parameter_wird_vor_zugriff_abgewiesen(boundary):
    app, client, db, seen, _ = boundary
    login(app, 'SALES_BEARBEITEN')
    assert read(client, tenant_id='tenant-b').status_code == 403
    assert seen == []
    db.execute.assert_not_called()


def test_fremde_id_ist_nicht_sichtbar(boundary):
    app, client, db, seen, _ = boundary
    login(app, 'SALES_BEARBEITEN')
    assert read(client, 'foreign').status_code == 404
    assert all(tenant == 'tenant-a' for _, tenant, _ in seen)
    assert not any(kind == 'items' for kind, _, _ in seen)
    db.execute.assert_not_called()


def test_antwort_nutzt_verifizierten_mandanten_und_ist_preisfrei_und_schreibfrei(boundary):
    app, client, db, seen, _ = boundary
    login(app, 'SALES_BEARBEITEN')
    response = read(client, tenant_id='tenant-a')
    assert response.status_code == 200, response.text
    assert response.json() == {'source_doc_id': 'own', 'source_doc_type': 'sales_order',
        'target_doc_type': 'sales_delivery', 'version': 3, 'items': [{'source_item_id': 'p1',
        'line_number': 1, 'article_number': 'A-1', 'description': 'Weizen', 'unit': 'kg',
        'quantity': 10.0, 'remaining_quantity': 6.0}]}
    assert seen and all(tenant == 'tenant-a' for _, tenant, _ in seen)
    db.execute.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()
