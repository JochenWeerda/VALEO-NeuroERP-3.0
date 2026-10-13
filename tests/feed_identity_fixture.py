"""Scoped sessions on the existing probe, never independent test databases."""
from contextvars import ContextVar
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from test_system_tenant_binding import keys, probe
from app.core.database import engine, get_db
from main import app

_connection = ContextVar('feed_test_connection')


def scoped_session():
    return Session(bind=_connection.get(), join_transaction_mode='create_savepoint')


@pytest.fixture
def feed_context(require_db, probe):
    tenant = str(uuid4())
    previous = app.dependency_overrides.get(get_db)
    with engine.connect() as connection:
        outer = connection.begin()
        marker = _connection.set(connection)
        db = scoped_session()
        try:
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id,:name,:domain,TRUE)'),
                       {'id': tenant, 'name': 'Synthetic feed tenant', 'domain': tenant+'.test.invalid'})
            db.commit()
            app.dependency_overrides[get_db] = lambda: db
            yield SimpleNamespace(tenant=tenant, headers={
                'Authorization': 'Bearer '+probe.token(tenant, changes={'roles': ['admin']}), 'X-Tenant-ID': tenant})
        finally:
            if previous is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = previous
            db.close()
            outer.rollback()
            _connection.reset(marker)
