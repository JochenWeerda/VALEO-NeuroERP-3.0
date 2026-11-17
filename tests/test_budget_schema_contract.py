"""Budget route contracts and PostgreSQL acceptance against the shared test DB."""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.endpoints.budget_planning import (
    BudgetLineCreate, BudgetLineUpdate, add_budget_line, approve_budget_plan,
    budget_vs_actual, update_budget_line,
)


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """These direct handler/role/SQL contracts never use the compatibility app."""
    yield


def row(value):
    return Mock(first=lambda: value)


@pytest.mark.unit
@pytest.mark.parametrize('account,cost_center', [(None, 'kst'), (('account',), None)])
def test_foreign_references_are_rejected_before_insert(account, cost_center):
    db = Mock()
    db.execute.side_effect = [Mock(), Mock(), row(('ENTWURF',)), row(account), row(cost_center)]
    body = BudgetLineCreate(account_id='account', kostenstelle_id='kst', period_month=1, budgeted_amount=Decimal('4.25'))
    with pytest.raises(HTTPException) as error:
        add_budget_line('plan', body, tenant_id='tenant', db=db)
    assert error.value.status_code == 422
    calls = db.execute.call_args_list
    assert calls[2].args[1] == {'id': 'plan', 'tid': 'tenant'}
    assert calls[3].args[1] == {'id': 'account', 'tid': 'tenant'}
    if account:
        assert calls[4].args[1] == {'id': 'kst', 'tid': 'tenant'}
    assert all('INSERT' not in str(call.args[0]) for call in calls)
    db.commit.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize('amount', ['NaN', 'Infinity', '-Infinity'])
def test_nonfinite_money_rejected(amount):
    with pytest.raises(ValidationError):
        BudgetLineCreate(account_id='a', period_month=1, budgeted_amount=amount)
    with pytest.raises(ValidationError):
        BudgetLineUpdate(budgeted_amount=amount)


@pytest.mark.unit
def test_vs_actual_failure_never_returns_zero():
    db = Mock()
    lines = [{'kostenstelle_id': None, 'account_id': 'a', 'period_month': 1, 'budgeted_amount': Decimal('5')}]
    db.execute.side_effect = [Mock(), Mock(), row((2026,)), Mock(mappings=lambda: SimpleNamespace(all=lambda: lines)), RuntimeError('private')]
    with pytest.raises(HTTPException) as error:
        budget_vs_actual('plan', tenant_id='tenant', db=db)
    assert error.value.status_code == 503
    assert 'private' not in str(error.value.detail)
    db.rollback.assert_called_once()


@pytest.mark.unit
def test_missing_plan_is_not_an_empty_actual_comparison():
    db = Mock()
    db.execute.side_effect = [Mock(), Mock(), row(None)]
    with pytest.raises(HTTPException) as error:
        budget_vs_actual('missing', tenant_id='tenant', db=db)
    assert error.value.status_code == 404
    db.commit.assert_not_called()


def _pg_error(conn, statement, params, error_type, code, constraint=None):
    savepoint = conn.begin_nested()
    try:
        with pytest.raises(error_type) as caught:
            conn.execute(text(statement), params)
        original = caught.value.orig
        assert getattr(original, 'pgcode', None) == code
        if constraint:
            assert original.diag.constraint_name == constraint
    finally:
        savepoint.rollback()


def test_postgres_schema_and_rls(require_db):
    """The canonical probe rolls migrations, grants and synthetic rows back together."""
    from app.core.tenant_context import tenant_scope
    from rls_domain_support import as_app, ensure_tenants, probe, seed_row

    plans, lines = 'domain_finance.budget_plans', 'domain_finance.budget_lines'
    with probe((plans, lines, 'domain_erp.chart_of_accounts', 'domain_finance.kostenstellen')) as conn:
        a, b = 'budget-a-' + uuid4().hex[:12], 'budget-b-' + uuid4().hex[:12]
        ensure_tenants(conn, a, b)
        fixtures = {}
        for tenant in (a, b):
            account = seed_row(conn, 'domain_erp.chart_of_accounts', tenant, is_active=True,
                               deleted_at=None, is_summary=False)
            kst = seed_row(conn, 'domain_finance.kostenstellen', tenant)
            plan = seed_row(conn, plans, tenant, plan_year=2026, plan_name='Probe', status='ENTWURF')
            fixtures[tenant] = (plan['id'], account['id'], kst['id'])
        pa, aa, ka = fixtures[a]
        pb, ab, kb = fixtures[b]
        foreign_line = seed_row(conn, lines, b, plan_id=pb, account_id=ab, kostenstelle_id=kb,
                                period_month=1, budgeted_amount=Decimal('3'))['id']
        as_app(conn)
        assert conn.execute(text('SELECT current_user')).scalar_one() == 'valeo_app'
        assert conn.execute(text("SELECT NOT rolsuper AND NOT rolbypassrls FROM pg_roles WHERE rolname = current_user")).scalar_one()
        insert = ("INSERT INTO domain_finance.budget_lines "
                  "(id,tenant_id,plan_id,account_id,kostenstelle_id,period_month,budgeted_amount) "
                  "VALUES (:id,:tenant,:plan,:account,:kst,1,5)")
        with tenant_scope(a, 'budget-test'):
            assert set(conn.execute(text('SELECT id FROM domain_finance.budget_plans WHERE id IN (:a,:b)'), {'a': pa, 'b': pb}).scalars()) == {pa}
            assert conn.execute(text('SELECT id FROM domain_finance.budget_lines WHERE id = :id'), {'id': foreign_line}).first() is None
            assert conn.execute(text("UPDATE domain_finance.budget_lines SET budgeted_amount=9 WHERE id=:id"), {'id': foreign_line}).rowcount == 0
            assert conn.execute(text('DELETE FROM domain_finance.budget_lines WHERE id=:id'), {'id': foreign_line}).rowcount == 0
            for plan, account, kst, constraint in ((pb, aa, ka, 'fk_budget_line_plan'),
                                                     (pa, ab, ka, 'fk_budget_line_account'),
                                                     (pa, aa, kb, 'fk_budget_line_kostenstelle')):
                params = {'id': str(uuid4()), 'tenant': a, 'plan': plan, 'account': account, 'kst': kst}
                _pg_error(conn, insert, params, IntegrityError, '23503', constraint)
                assert conn.execute(text('SELECT count(*) FROM domain_finance.budget_lines WHERE plan_id=:p AND tenant_id=:t'), {'p': pa, 't': a}).scalar_one() == 0
            own_id = str(uuid4())
            conn.execute(text(insert), {'id': own_id, 'tenant': a, 'plan': pa, 'account': aa, 'kst': ka})
            assert conn.execute(text('UPDATE domain_finance.budget_lines SET budgeted_amount=7 WHERE id=:id'), {'id': own_id}).rowcount == 1
            _pg_error(conn, 'UPDATE domain_finance.budget_lines SET tenant_id=:b WHERE id=:id', {'b': b, 'id': own_id}, DBAPIError, '42501')
            assert conn.execute(text('DELETE FROM domain_finance.budget_lines WHERE id=:id'), {'id': own_id}).rowcount == 1
            assert conn.execute(text('SELECT count(*) FROM domain_finance.budget_lines WHERE id=:id'), {'id': own_id}).scalar_one() == 0
            # Session commits release savepoints only; probe retains its outer rollback.
            with Session(bind=conn, join_transaction_mode='create_savepoint') as db:
                added = add_budget_line(pa, BudgetLineCreate(account_id=aa, kostenstelle_id=ka, period_month=2, budgeted_amount=Decimal('2.50')), tenant_id=a, db=db)
                assert update_budget_line(pa, added['id'], BudgetLineUpdate(budgeted_amount=Decimal('3')), tenant_id=a, db=db)['updated'] is True
                assert approve_budget_plan(pa, tenant_id=a, db=db)['approved'] is True
                with pytest.raises(HTTPException) as frozen_update:
                    update_budget_line(pa, added['id'], BudgetLineUpdate(budgeted_amount=Decimal('99')), tenant_id=a, db=db)
                assert frozen_update.value.status_code == 409
                with pytest.raises(HTTPException) as frozen_insert:
                    add_budget_line(pa, BudgetLineCreate(account_id=aa, kostenstelle_id=ka, period_month=2, budgeted_amount=Decimal('99')), tenant_id=a, db=db)
                assert frozen_insert.value.status_code == 409
                assert db.execute(text('SELECT budgeted_amount FROM domain_finance.budget_lines WHERE id=:id'), {'id': added['id']}).scalar_one() == Decimal('3')
                assert db.execute(text('SELECT count(*) FROM domain_finance.budget_lines WHERE plan_id=:id'), {'id': pa}).scalar_one() == 1
                with pytest.raises(HTTPException) as err:
                    approve_budget_plan(pa, tenant_id=a, db=db)
                assert err.value.status_code == 409
            conn.execute(text("UPDATE domain_finance.budget_plans SET status='GESPERRT' WHERE id=:id"), {'id': pa})
            with Session(bind=conn, join_transaction_mode='create_savepoint') as db:
                with pytest.raises(HTTPException) as err:
                    update_budget_line(pa, added['id'], BudgetLineUpdate(budgeted_amount=Decimal('99')), tenant_id=a, db=db)
                assert err.value.status_code == 409
                assert db.execute(text('SELECT budgeted_amount FROM domain_finance.budget_lines WHERE id=:id'), {'id': added['id']}).scalar_one() == Decimal('3')

@pytest.mark.unit
@pytest.mark.parametrize('status', ['GENEHMIGT', 'GESPERRT', 'invalid'])
def test_create_cannot_bypass_approval_and_does_not_query(status):
    from app.api.v1.endpoints.budget_planning import BudgetPlanCreate, create_budget_plan
    db = Mock()
    with pytest.raises(HTTPException) as error:
        # The domain handler must also reject a caller bypassing request parsing.
        create_budget_plan(BudgetPlanCreate.model_construct(plan_year=2026, plan_name='Probe', status=status), tenant_id='tenant', db=db)
    assert error.value.status_code == 422
    db.execute.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.unit
def test_create_schema_and_parser_only_allow_the_initial_draft_state():
    from app.api.v1.endpoints.budget_planning import BudgetPlanCreate
    assert BudgetPlanCreate.model_json_schema()['properties']['status']['const'] == 'ENTWURF'
    assert BudgetPlanCreate(plan_year=2026, plan_name='Probe', status='entwurf').status == 'ENTWURF'
    for status in ('GENEHMIGT', 'GESPERRT'):
        with pytest.raises(ValidationError):
            BudgetPlanCreate(plan_year=2026, plan_name='Probe', status=status)


@pytest.mark.unit
@pytest.mark.parametrize('amount', ['1.001', '100000000000000.00'])
def test_money_exceeding_database_precision_is_rejected(amount):
    with pytest.raises(ValidationError):
        BudgetLineCreate(account_id='a', period_month=1, budgeted_amount=amount)
    with pytest.raises(ValidationError):
        BudgetLineUpdate(budgeted_amount=amount)


@pytest.mark.unit
def test_create_and_approve_routes_bind_distinct_role_guards():
    from app.auth.finance_roles import finance_admin, finance_write
    from app.api.v1.endpoints.budget_planning import router

    create = next(route for route in router.routes if route.path == '/finance/budgets' and 'POST' in route.methods)
    approve = next(route for route in router.routes if route.path.endswith('/approve') and 'POST' in route.methods)
    assert finance_write in [d.call for d in create.dependant.dependencies]
    assert finance_admin in [d.call for d in approve.dependant.dependencies]
    writer = {'sub': 'synthetic', 'roles': ['FINANCE_BEARBEITEN']}
    admin = {'sub': 'synthetic', 'roles': ['FINANCE_ADMIN']}
    assert finance_write(user=writer) is writer
    with pytest.raises(HTTPException) as error:
        finance_admin(user=writer)
    assert error.value.status_code == 403
    assert finance_admin(user=admin) is admin

@pytest.mark.unit
def test_budget_list_pages_with_tenant_scoped_full_count():
    from app.api.v1.endpoints.budget_planning import list_budget_plans
    db = Mock()
    db.execute.side_effect = [Mock(), Mock(), Mock(scalar_one=lambda: 203),
                              Mock(mappings=lambda: SimpleNamespace(all=lambda: [{'id': 'own-101'}]))]
    result = list_budget_plans(skip=100, limit=1, tenant_id='tenant-a', db=db)
    assert result == {'items': [{'id': 'own-101'}], 'total': 203, 'skip': 100, 'limit': 1}
    count, page = db.execute.call_args_list[2:]
    assert 'COUNT(*)' in str(count.args[0]) and 'tenant_id = :tid' in str(count.args[0])
    assert count.args[1] == {'tid': 'tenant-a'}
    assert 'tenant_id = :tid' in str(page.args[0])
    assert 'LIMIT :limit OFFSET :skip' in str(page.args[0])
    assert 'plan_name, id' in str(page.args[0])
    assert page.args[1] == {'tid': 'tenant-a', 'limit': 1, 'skip': 100}


@pytest.mark.unit
def test_budget_list_query_parameter_boundaries():
    from app.api.v1.endpoints.budget_planning import router
    route = next(r for r in router.routes if r.path == '/finance/budgets' and 'GET' in r.methods)
    params = {p.name: p for p in route.dependant.query_params}
    assert params['skip'].default == 0 and params['limit'].default == 100
    for name, value in [('skip', -1), ('limit', 0), ('limit', 501)]:
        _, error = params[name].validate(value, {}, loc=('query', name))
        assert error
    for name, value in [('skip', 0), ('limit', 1), ('limit', 500)]:
        _, error = params[name].validate(value, {}, loc=('query', name))
        assert not error


@pytest.mark.unit
@pytest.mark.parametrize('status', ['GENEHMIGT', 'GESPERRT'])
@pytest.mark.parametrize('operation', ['insert', 'update'])
def test_non_draft_positions_cannot_change_under_the_existing_approval(status, operation):
    db = Mock()
    db.execute.side_effect = [Mock(), Mock(), row((status,))]
    with pytest.raises(HTTPException) as error:
        if operation == 'insert':
            add_budget_line('plan', BudgetLineCreate(account_id='a', period_month=1, budgeted_amount=Decimal('1')), tenant_id='tenant', db=db)
        else:
            update_budget_line('plan', 'line', BudgetLineUpdate(budgeted_amount=Decimal('1')), tenant_id='tenant', db=db)
    assert error.value.status_code == 409
    assert len(db.execute.call_args_list) == 3
    assert 'FOR UPDATE' in str(db.execute.call_args_list[-1].args[0])
    db.commit.assert_not_called()
