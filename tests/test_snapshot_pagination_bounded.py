"""Real SQL and memory pagination agree; this does not verify production auth."""
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.core.read_model_persistence import ReadModelSnapshot, ReadModelSnapshotStore, SnapshotCursor
from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord
from app.api.v1.endpoints import read_model_snapshots as endpoint


@pytest.fixture(scope='module')
def engine():
    database = create_engine('sqlite:///:memory:')
    ReadModelSnapshotRecord.__table__.create(database)
    yield database
    database.dispose()


@pytest.mark.parametrize('anchor,expected', [
    (None, ['a', 'b']), ('a', ['b', 'c']), ('b', ['c', 'd']),
    ('d', []), ('missing', ['a', 'b']), ('foreign', ['a', 'b']),
    ('other-model', ['a', 'b']),
])
def test_keyset_matches_memory_and_bounds_actual_sql(engine, anchor, expected):
    snapshots = {}
    for identifier, tenant, model in [
        *[(letter, 'tenant-a', 'orders') for letter in 'abcd'],
        ('foreign', 'tenant-b', 'orders'), ('other-model', 'tenant-a', 'inventory'),
    ]:
        snapshot = ReadModelSnapshot.build(model, tenant, {'value': identifier})
        snapshot.snapshot_id = identifier
        snapshot.created_at = datetime(2026, 10, 12)
        snapshots[identifier] = snapshot
    statements = []

    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    with Session(engine) as db:
        db.add_all([ReadModelSnapshotRecord(**snapshot.model_dump()) for snapshot in snapshots.values()])
        db.flush()
        event.listen(engine, 'before_cursor_execute', capture)
        try:
            cursor = SnapshotCursor(last_snapshot_id=anchor, limit=2)
            sql_page = ReadModelSnapshotStore(db_session=db).get_page('orders', 'tenant-a', cursor)
            memory_page = ReadModelSnapshotStore(snapshots=snapshots).get_page('orders', 'tenant-a', cursor)
            assert [row.snapshot_id for row in sql_page] == expected
            assert sql_page == memory_page
            page_query = statements[-1].upper()
            assert 'LIMIT' in page_query and 'TENANT_ID =' in page_query and 'MODEL_NAME =' in page_query
            if anchor in {'a', 'b', 'c', 'd'}:
                assert 'CREATED_AT >' in page_query and 'SNAPSHOT_ID >' in page_query
        finally:
            event.remove(engine, 'before_cursor_execute', capture)
            db.rollback()


@pytest.mark.parametrize('limit,status', [(0, 422), (-1, 422), (101, 422), (1000000, 422), (1, 200), (100, 200)])
def test_http_page_limit_is_validated_before_store_effects(limit, status):
    app = FastAPI()
    app.include_router(endpoint.router)
    app.dependency_overrides[endpoint._get_store] = lambda: ReadModelSnapshotStore()
    with TestClient(app) as client:
        response = client.get('/read-models/snapshots/page', params={
            'model_name': 'orders', 'tenant_id': 'tenant-a', 'limit': limit,
        })
    assert response.status_code == status
