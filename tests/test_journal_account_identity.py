"""Canonical tenant-owned account identity on the existing shared PostgreSQL."""

import os
import ast
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.services.finance_transaction_service import FinanceTransactionService


@pytest.fixture(scope="module")
def store():
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Existing shared PostgreSQL required")
    url = make_url(raw)
    assert url.database == "valeo_probe" or "test" in url.database.lower()
    engine = create_engine(url)
    name = "journalaccount_" + uuid4().hex
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        conn.execute(
            text(
                f'CREATE TABLE "{name}".chart_of_accounts (LIKE domain_erp.chart_of_accounts INCLUDING ALL)'
            )
        )

    class OwnedSession(Session):
        writes = 0
        account_reads = 0

        def execute(self, statement, params=None, **kwargs):
            if "SELECT id FROM domain_erp.chart_of_accounts" in str(statement):
                self.account_reads += 1
            sql = str(statement).replace("domain_erp.", f'"{name}".')
            sql = sql.replace("(__[POSTCOMPILE_account_ids])", ":account_ids")
            redirected = text(sql)
            if "account_ids" in str(statement):
                from sqlalchemy import bindparam

                redirected = redirected.bindparams(
                    bindparam("account_ids", expanding=True)
                )
            return super().execute(redirected, params, **kwargs)

        def add(self, obj, **kwargs):
            self.writes += 1
            return super().add(obj, **kwargs)

    try:
        yield engine, OwnedSession
    finally:
        assert name.startswith("journalaccount_") and len(name) == 47
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
        engine.dispose()


@pytest.fixture
def case(store):
    engine, factory = store
    with factory(engine) as db:
        tenant, other, account = (str(uuid4()) for _ in range(3))
        number = uuid4().hex[:20]
        db.execute(
            text("""INSERT INTO domain_erp.chart_of_accounts
            (id,tenant_id,account_number,account_name,account_type,is_active,deleted_at,is_summary)
            VALUES (:id,:tenant,:number,'Identity proof','ASSET',TRUE,NULL,FALSE)"""),
            {"id": account, "tenant": tenant, "number": number},
        )
        yield db, tenant, other, account, number
        db.rollback()  # only this test's uncommitted rows


def test_exact_id_and_explicit_number_are_separate_contracts(case):
    db, tenant, _, account, number = case
    service = FinanceTransactionService(db, tenant)
    assert service._resolve_account_id(account) == account
    assert service.account_id_for_number(number) == account
    with pytest.raises(ValidationFailedError):
        service._resolve_account_id(number)
    with pytest.raises(ValidationFailedError):
        service.account_id_for_number(account)


@pytest.mark.parametrize(
    "property", ["foreign", "shared", "inactive", "deleted", "summary"]
)
def test_only_own_active_bookable_accounts_can_be_used(case, property):
    db, tenant, other, account, number = case
    changes = {
        "foreign": ("tenant_id", other),
        "shared": ("tenant_id", None),
        "inactive": ("is_active", False),
        "deleted": ("deleted_at", datetime(2026, 10, 2)),
        "summary": ("is_summary", True),
    }
    column, value = changes[property]
    db.execute(
        text(f"UPDATE domain_erp.chart_of_accounts SET {column}=:value WHERE id=:id"),
        {"value": value, "id": account},
    )
    service = FinanceTransactionService(db, tenant)
    for lookup, value in (
        (service._resolve_account_id, account),
        (service.account_id_for_number, number),
    ):
        with pytest.raises(ValidationFailedError, match="Own active bookable"):
            lookup(value)


def test_foreign_id_equal_to_own_number_cannot_become_an_alias(case):
    db, tenant, other, account, number = case
    db.execute(
        text("""INSERT INTO domain_erp.chart_of_accounts
        (id,tenant_id,account_number,account_name,account_type,is_active,deleted_at,is_summary)
        VALUES (:id,:tenant,:number,'Foreign proof','ASSET',TRUE,NULL,FALSE)"""),
        {"id": number, "tenant": other, "number": uuid4().hex[:20]},
    )
    service = FinanceTransactionService(db, tenant)
    with pytest.raises(ValidationFailedError):
        service._resolve_account_id(number)
    assert service.account_id_for_number(number) == account


@pytest.mark.parametrize(
    "bad", ["number", "foreign", "camel", "missing", "number_field"]
)
def test_invalid_reference_prevents_all_journal_writes(case, bad):
    db, tenant, other, account, number = case
    first = {"account_id": account, "debit_amount": 10, "credit_amount": 0}
    second = {"account_id": account, "debit_amount": 0, "credit_amount": 10}
    if bad == "number":
        second["account_id"] = number
    elif bad == "foreign":
        db.execute(
            text(
                "UPDATE domain_erp.chart_of_accounts SET tenant_id=:tenant WHERE id=:id"
            ),
            {"tenant": other, "id": account},
        )
    elif bad == "camel":
        second["accountId"] = second.pop("account_id")
    elif bad == "number_field":
        second["account_number"] = number
    else:
        second.pop("account_id")
    with pytest.raises(ValidationFailedError):
        FinanceTransactionService(db, tenant).create(
            "PROOF", "Proof", datetime(2026, 10, 2), [first, second], reference="REF"
        )
    assert db.writes == 0


@pytest.mark.parametrize("value", [None, "", 42])
def test_empty_or_untyped_references_are_rejected(case, value):
    db, tenant, _, _, _ = case
    service = FinanceTransactionService(db, tenant)
    with pytest.raises(ValidationFailedError, match="nonempty"):
        service._resolve_account_id(value)


def test_retired_duplicate_invoice_booking_cannot_return():
    from app.api.v1.endpoints import finance_invoices

    assert not hasattr(finance_invoices, "_create_gl_booking_and_op")
    assert not hasattr(finance_invoices, "_ensure_account")


def test_many_lines_use_one_validation_query_before_any_journal_write(
    case, monkeypatch
):
    db, tenant, _, account, _ = case
    service = FinanceTransactionService(db, tenant)
    reached = []

    def stop(obj):
        reached.append(True)
        raise ValidationFailedError("Stop before journal writing")

    monkeypatch.setattr(service, "_stamp_gobd", stop)
    lines = [
        {"account_id": account, "debit_amount": 1, "credit_amount": 0},
        {"account_id": account, "debit_amount": 0, "credit_amount": 1},
    ] * 100
    with pytest.raises(ValidationFailedError, match="Stop before"):
        service.create("PROOF", "Proof", datetime(2026, 10, 2), lines, reference="REF")
    assert reached and db.account_reads == 1 and db.writes == 0


@pytest.mark.parametrize(
    "file",
    [
        "app/services/sales_posting_service.py",
        "app/services/agrar_settlement_service.py",
        "app/services/einkauf_compat_service.py",
        "app/services/harvest_acceptance_service.py",
        "app/services/procurement_service.py",
        "app/api/v1/endpoints/asset_accounting.py",
        "app/api/v1/endpoints/genossenschaft.py",
        "app/api/v1/endpoints/logistics_freight.py",
        "app/api/v1/endpoints/produktion_mischfutter.py",
    ],
)
def test_number_configured_service_callers_resolve_before_constructing_lines(file):
    tree = ast.parse(Path(file).read_text(encoding="utf-8"))
    references = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "account_id":
                    references.append(value)
    assert references
    assert all(
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == "account_id_for_number"
        for value in references
    )
