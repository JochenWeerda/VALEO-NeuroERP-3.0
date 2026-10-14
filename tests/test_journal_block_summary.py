"""Actual PostgreSQL aggregation through the manual journal endpoint."""
import os
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import journal_entries
from testgrenze import pruefstand_erlaubt


@pytest.fixture
def accounts():
    raw = os.environ.get('TEST_DATABASE_URL')
    assert raw, 'Existing shared probe connection required'
    url = make_url(raw)
    assert pruefstand_erlaubt(url), "Nur Pruefstand oder CI-Testdatenbank"
    engine = create_engine(url)
    tenant = str(uuid4())
    ids = {number: str(uuid4()) for number in ['1500', '1400', '1600']}
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection) as db:
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,is_active) VALUES (:id,:id,true)'), {'id': tenant})
            for number, account in ids.items():
                db.execute(text(
                    'INSERT INTO domain_erp.chart_of_accounts '
                    '(id,account_number,account_name,account_type,category,tenant_id,is_active,posting_blocked) '
                    "VALUES (:id,:number,'Synthetic journal test','asset','inventory',:tenant,true,:blocked)"
                ), {'id': account, 'number': number, 'tenant': tenant, 'blocked': number != '1600'})
            yield db, tenant, ids
        transaction.rollback()
    engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize('numbers,expected', [
    (['1500', '1400', '1500'], 'Konto 1400, 1500 ist fuer Buchungen gesperrt.'),
    (['1500', '1600'], 'Konto 1500 ist fuer Buchungen gesperrt.'),
    (['1600', '1600'], None),
])
async def test_complete_sorted_summary_and_open_accounts(accounts, monkeypatch, numbers, expected):
    db, tenant, ids = accounts
    lines = [SimpleNamespace(account_id=ids[number], debit_amount=Decimal('0'), credit_amount=Decimal('0')) for number in numbers]
    entry = SimpleNamespace(lines=lines, reference='synthetic-document', period=None,
                            model_dump=lambda: {})

    class RepositoryBoundary:
        async def create(self, *args):
            raise HTTPException(418, 'Repository reached after successful block check')

    monkeypatch.setattr(journal_entries.container, 'resolve', lambda *args: RepositoryBoundary())
    with pytest.raises(HTTPException) as error:
        await journal_entries.create_journal_entry(entry, None, tenant_id=tenant, db=db)
    if expected:
        assert error.value.status_code == 409
        assert error.value.detail == expected
    else:
        assert error.value.status_code == 418
