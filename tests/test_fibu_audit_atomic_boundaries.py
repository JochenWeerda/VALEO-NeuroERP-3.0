"""Real audit INSERT failures must undo the associated account/period mutation."""
from uuid import uuid4
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event, text
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.core.fibu_audit import log_fibu_audit, _user_from_request
from app.infrastructure.models import Account, AuditLog
from app.api.v1.endpoints import chart_of_accounts, accounting_periods
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import keys, probe, subject_data  # noqa: F401


@pytest.fixture
def finance_case(subject_data):
    _, db, provider, tenant, *_ = subject_data
    account_id, period_id = str(uuid4()), str(uuid4())
    number = 'SYN' + uuid4().hex[:14]
    db.add(Account(id=account_id, tenant_id=tenant, account_number=number, account_name='Synthetic original', account_type='asset', category='current_assets', is_active=True))
    db.execute(text("INSERT INTO finance_accounting_periods (id,tenant_id,period,status,start_date,end_date) VALUES (:id,:t,'2026-11','OPEN','2026-11-01','2026-11-30')"), {'id': period_id, 't': tenant})
    db.commit()  # fixture savepoint only; shared outer transaction rolls back
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(chart_of_accounts.router, prefix='/api/v1/finance')
    app.include_router(accounting_periods.router, prefix='/api/v1/finance/accounting-periods')
    def shared_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise
    app.dependency_overrides[get_db] = shared_db
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    headers = {'Authorization': 'Bearer ' + provider.token(tenant, changes={'roles': ['FINANCE_ADMIN'], 'email': 'synthetic@example.org'})}
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db, tenant, account_id, period_id, headers


@pytest.mark.parametrize('operation', ['account_create', 'account_update', 'account_delete', 'period_create', 'period_update'])
@pytest.mark.parametrize('broken_audit', [False, True])
def test_business_and_required_audit_share_commit(finance_case, operation, broken_audit, caplog):
    client, db, tenant, account_id, period_id, headers = finance_case
    number = 'SYN' + uuid4().hex[:14]
    marker = 'SYNTHETIC_PRIVATE_AUDIT_INPUT' * 5
    def violate_database_column(session, *args):
        if broken_audit:
            for entry in session.new:
                if isinstance(entry, AuditLog):
                    entry.action = marker  # real varchar(50) INSERT failure, not a mocked exception
    event.listen(db, 'before_flush', violate_database_column)
    try:
        base = '/api/v1/finance/chart-of-accounts'
        periods = '/api/v1/finance/accounting-periods'
        if operation == 'account_create':
            response = client.post(base+'/', json={'tenant_id': tenant, 'account_number': number, 'account_name': 'Synthetic new', 'account_type': 'asset', 'category': 'current_assets'}, headers=headers)
        elif operation == 'account_update':
            response = client.put(base+'/'+account_id, json={'account_name': 'Synthetic changed'}, headers=headers)
        elif operation == 'account_delete':
            response = client.delete(base+'/'+account_id, headers=headers)
        elif operation == 'period_create':
            response = client.post(periods+'/', json={'tenant_id': tenant, 'period': '2026-12', 'status': 'OPEN', 'start_date': '2026-12-01', 'end_date': '2026-12-31'}, headers=headers)
        else:
            response = client.put(periods+'/'+period_id, json={'status': 'ADJUSTING'}, headers=headers)
        expected = 500 if broken_audit else {'account_create': 200, 'account_update': 200, 'account_delete': 200, 'period_create': 201, 'period_update': 200}[operation]
        assert response.status_code == expected, response.text
    finally:
        event.remove(db, 'before_flush', violate_database_column)
    assert marker not in response.text and marker not in caplog.text
    db.expire_all()
    if operation == 'account_create':
        assert db.query(Account).filter_by(tenant_id=tenant, account_number=number).count() == (0 if broken_audit else 1)
    elif operation == 'account_update':
        assert db.get(Account, account_id).account_name == ('Synthetic original' if broken_audit else 'Synthetic changed')
    elif operation == 'account_delete':
        assert db.get(Account, account_id).is_active is broken_audit
    elif operation == 'period_create':
        assert db.execute(text("SELECT COUNT(*) FROM finance_accounting_periods WHERE tenant_id=:t AND period='2026-12'"), {'t': tenant}).scalar_one() == (0 if broken_audit else 1)
    else:
        assert db.execute(text('SELECT status FROM finance_accounting_periods WHERE id=:id'), {'id': period_id}).scalar_one() == ('OPEN' if broken_audit else 'ADJUSTING')
    entries = db.query(AuditLog).filter(AuditLog.tenant_id == tenant, AuditLog.entity_type.in_(['finance_account','accounting_period'])).all()
    assert len(entries) == (0 if broken_audit else 1)
    if entries:
        assert entries[0].user_id == 'human-a' and entries[0].user_email == 'synthetic@example.org'


def test_http_audit_actor_cannot_be_overridden_and_outer_owner_can_flush():
    db = MagicMock()
    request = SimpleNamespace(state=SimpleNamespace(token_claims={'sub': 'synthetic-verified', 'email': 'synthetic@example.org'}), client=None, headers={})
    log_fibu_audit(db, 'synthetic-tenant', 'update', 'synthetic', 'own', {}, request=request, user_id='forged', user_email='forged@example.org', commit=False)
    assert db.add.call_args.args[0].user_id == 'synthetic-verified'
    db.flush.assert_called_once()
    db.commit.assert_not_called()


def test_http_audit_never_falls_back_to_system_without_identity():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as denied:
        _user_from_request(SimpleNamespace(state=SimpleNamespace()))
    assert denied.value.status_code == 403
