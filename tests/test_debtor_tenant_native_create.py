"""No database required: verified tenant reaches every debtor aggregate query."""
import asyncio

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.debtors import get_debtor, update_debtor, delete_debtor, get_debtor_balance
from app.api.v1.endpoints.finance_stammdaten import DebitorCreate, create_debitor
from app.api.v1.schemas.finance import DebtorUpdate


class EmptyResult:
    def fetchone(self):
        return None


class CaptureDB:
    def __init__(self):
        self.calls = []
        self.commits = 0

    def execute(self, sql, params):
        self.calls.append((str(sql), params))
        return EmptyResult()

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


def payload(**kwargs):
    return DebitorCreate(debtor_number='123456', company_name='Hof', street='Weg 1', postal_code='12345', city='Ort', **kwargs)


def test_body_tenant_cannot_override_verified_tenant():
    db = CaptureDB()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_debitor(payload(tenant_id='foreign'), tenant_id='own', db=db))
    assert exc.value.status_code == 403
    assert db.calls == []


@pytest.mark.parametrize('field,value', [('iban', 'DE89370400440532013000'), ('discount_percent', 2.0),
                                         ('notes', 'Hinweis'), ('tax_number', '12/345/67890')])
def test_fields_the_customer_master_does_not_hold_are_rejected_not_dropped(field, value):
    db = CaptureDB()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_debitor(payload(**{field: value}), tenant_id='own', db=db))
    assert exc.value.status_code == 422
    assert field in exc.value.detail
    assert db.calls == []


@pytest.mark.parametrize('op', ['get', 'update', 'delete', 'balance'])
def test_foreign_debtor_does_not_escape_tenant_scope(op):
    db = CaptureDB()
    call = {
        'get': lambda: get_debtor('foreign-id', tenant_id='own', db=db),
        'update': lambda: update_debtor('foreign-id', DebtorUpdate(company_name='Changed'), tenant_id='own', db=db),
        'delete': lambda: delete_debtor('foreign-id', tenant_id='own', db=db),
        'balance': lambda: get_debtor_balance('foreign-id', tenant_id='own', db=db),
    }[op]
    with pytest.raises(HTTPException) as exc:
        asyncio.run(call())
    assert exc.value.status_code == 404
    assert db.commits == 0
    assert len(db.calls) == 1
    assert 'tenant_id = :tenant_id' in db.calls[0][0]
    assert db.calls[0][1]['tenant_id'] == 'own'
