"""PostgreSQL count-sheet contracts on shared probe; each test rolls back its rows."""
import os
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.services import inventory_count_sheet_command as service

TENANT = '00000000-0000-0000-0000-000000000001'
OTHER = '00000000-0000-0000-0000-000000000002'


@pytest.fixture
def probe(monkeypatch):
    raw = os.environ.get('TEST_DATABASE_URL')
    if not raw:
        pytest.skip('explicit shared probe URL required')
    url = make_url(raw)
    assert url.database == 'valeo_probe'
    engine = create_engine(url, connect_args={'connect_timeout': 5, 'application_name': 'agent:inventory-count-sheet'})
    identity = SimpleNamespace(subject='inventory-count-sheet-test', tenant_id=TENANT,
                               roles={'LAGER_BEARBEITEN'}, scopes={'masks:write'},
                               claims={'identity_type': 'human'})
    monkeypatch.setattr(service, 'current_identity', lambda: identity)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL lock_timeout = '3s'"))
            yield connection, identity
        finally:
            transaction.rollback()
    engine.dispose()


def seed(connection, tenant):
    ids = {name: str(uuid4()) for name in ('warehouse', 'article', 'count', 'line', 'user')}
    ids['tenant'] = tenant
    ids['email'] = ids['user'] + '@example.invalid'
    ids['warehouse_code'] = ids['warehouse'][:18]
    ids['article_number'] = ids['article'][:18]
    connection.execute(text('INSERT INTO domain_shared.users (id,keycloak_id,username,email) '
                            'VALUES (:user,:user,:user,:email)'), ids)
    connection.execute(text('INSERT INTO domain_inventory.warehouses (id,tenant_id,warehouse_code,name) '
                            "VALUES (:warehouse,:tenant,:warehouse_code,'Probe')"), ids)
    connection.execute(text('INSERT INTO domain_inventory.articles (id,tenant_id,article_number,name,purchase_price) '
                            "VALUES (:article,:tenant,:article_number,'Probe',2)"), ids)
    connection.execute(text('INSERT INTO domain_inventory.inventory_counts '
                            '(id,tenant_id,warehouse_id,counted_by,status) '
                            "VALUES (:count,:tenant,:warehouse,:user,'open')"), ids)
    connection.execute(text('INSERT INTO domain_inventory.inventory_count_lines '
                            '(id,tenant_id,inventory_count_id,article_id,warehouse_id,expected_qty,counted_qty) '
                            'VALUES (:line,:tenant,:count,:article,:warehouse,10,5)'), ids)
    return ids


def cmd(count, revision, key=None):
    return service.CountSheetCommand(inventory_count_id=count, expected_revision=revision,
                                     idempotency_key=key or str(uuid4()), reason='Isolierter Testlauf')


def set_app(connection, tenant):
    connection.exec_driver_sql('SET LOCAL ROLE valeo_app')
    connection.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {'tenant': tenant})


def test_real_rls_snapshot_and_replay(probe):
    connection, _ = probe
    own, foreign = seed(connection, TENANT), seed(connection, OTHER)
    set_app(connection, TENANT)
    with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
        version = service.snapshot(db, TENANT, own['count'])
        assert version['line_count'] == 1 and len(version['revision']) == 64
        with pytest.raises(HTTPException) as exc:
            service.snapshot(db, TENANT, foreign['count'])
        assert exc.value.status_code == 404
        request = cmd(own['count'], version['revision'])
        first = service.create_count_sheet(db, TENANT, request)
        db.commit()
        assert service.create_count_sheet(db, TENANT, request) == {**first, 'replayed': True}
        db.commit()
    connection.exec_driver_sql('RESET ROLE')
    assert connection.execute(text('SELECT count(*) FROM domain_inventory.inventory_auxiliary_batches '
                                   'WHERE tenant_id=:tenant AND inventory_count_id=:count'), own).scalar_one() == 1
    assert connection.execute(text('SELECT count(*) FROM domain_inventory.inventory_auxiliary_audit '
                                   'WHERE tenant_id=:tenant AND batch_id=:id'),
                              {'tenant': TENANT, 'id': first['id']}).scalar_one() == 1


def test_stale_line_or_article_value_is_rejected(probe):
    connection, _ = probe
    own = seed(connection, TENANT)
    with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
        version = service.snapshot(db, TENANT, own['count'])['revision']
        connection.execute(text('UPDATE domain_inventory.articles SET purchase_price=3 WHERE id=:article AND tenant_id=:tenant'), own)
        with pytest.raises(HTTPException) as exc:
            service.create_count_sheet(db, TENANT, cmd(own['count'], version))
        assert exc.value.status_code == 409
        db.rollback()
    assert connection.execute(text('SELECT count(*) FROM domain_inventory.inventory_auxiliary_batches '
                                   'WHERE tenant_id=:tenant AND inventory_count_id=:count'), own).scalar_one() == 0


def test_outbox_failure_rolls_back_business_audit_and_replay(probe):
    connection, _ = probe
    own = seed(connection, TENANT)
    with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
        version = service.snapshot(db, TENANT, own['count'])['revision']
        with patch.object(service, '_write_outbox', side_effect=RuntimeError('synthetic')):
            with pytest.raises(RuntimeError):
                service.create_count_sheet(db, TENANT, cmd(own['count'], version))
            db.rollback()
    assert connection.execute(text('SELECT count(*) FROM domain_inventory.inventory_auxiliary_batches '
                                   'WHERE tenant_id=:tenant AND inventory_count_id=:count'), own).scalar_one() == 0
