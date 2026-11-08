from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from app.services.pricing_condition_read import read_pricing_conditions


class Database:
    def __init__(self, failure=False):
        self.failure = failure
        self.params = None
        self.rollback_count = 0
    def execute(self, statement, params):
        self.params = params
        assert 'g.tenant_id = :t' in str(statement)
        assert 'g.id = k.gruppe_id' in str(statement)
        if self.failure:
            raise OperationalError('private SQL', {}, RuntimeError('private details'))
        return SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: [{'id': 'own-condition'}]))
    def rollback(self): self.rollback_count += 1


@pytest.mark.parametrize('limit', [1, 200])
def test_query_uses_explicit_tenant_and_bounded_limit(limit):
    db = Database()
    assert read_pricing_conditions(db, 'tenant-a', limit=limit) == [{'id': 'own-condition'}]
    assert db.params == {'t': 'tenant-a', 'limit': limit}


def test_database_failure_is_not_a_fabricated_default_price():
    db = Database(failure=True)
    with pytest.raises(HTTPException) as failure:
        read_pricing_conditions(db, 'tenant-a', limit=1)
    assert failure.value.status_code == 503
    assert 'private' not in failure.value.detail
    assert db.rollback_count == 1


@pytest.mark.parametrize('limit', [0, 201, True, '1'])
def test_invalid_limit_is_rejected_before_query(limit):
    db = Database()
    with pytest.raises(ValueError): read_pricing_conditions(db, 'tenant-a', limit=limit)
    assert db.params is None


def test_missing_tenant_is_rejected_before_query():
    db = Database()
    with pytest.raises(HTTPException) as failure: read_pricing_conditions(db, '', limit=1)
    assert failure.value.status_code == 403
    assert db.params is None
