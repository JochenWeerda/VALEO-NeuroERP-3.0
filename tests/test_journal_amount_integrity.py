"""Exact journal amount and persisted lifecycle contracts."""

import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.services.finance_transaction_service import FinanceTransactionService


def balanced(value=10):
    return [
        {"account_id": "a", "debit_amount": value, "credit_amount": 0},
        {"account_id": "b", "debit_amount": 0, "credit_amount": value},
    ]


BAD = [
    None,
    [None, None],
    [],
    balanced(0),
    balanced(-10),
    balanced("NaN"),
    balanced("Infinity"),
    balanced("-Infinity"),
    balanced("0.001"),
    balanced("10000000000000"),
    balanced(None),
    balanced(True),
    balanced("abc"),
    [{"debit_amount": 10, "credit_amount": 10}],
    [
        {"debit_amount": 10, "credit_amount": 10},
        {"debit_amount": 1, "credit_amount": 1},
    ],
    [{"debit_amount": 10, "credit_amount": 0}, {"debit_amount": 0}],
    balanced(10) + [{"debit_amount": 0, "credit_amount": 0}],
    [{"debit_amount": 10, "credit_amount": 0}, {"debit_amount": 0, "credit_amount": 9}],
    balanced("9999999999999.99") * 2,
]

BAD += [
    [{**balanced()[0], alias: 99}, balanced()[1]]
    for alias in ("debit", "credit", "debitAmount", "creditAmount")
]


@pytest.mark.parametrize("lines", BAD)
def test_invalid_amounts_prevent_every_database_access(lines):
    db = MagicMock()
    service = FinanceTransactionService(db, "tenant")
    with pytest.raises(ValidationFailedError):
        service.create("PROOF", "Proof", datetime(2026, 10, 2), lines, reference="REF")
    db.execute.assert_not_called()
    db.add.assert_not_called()
    db.flush.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize(
    "value", ["0.01", Decimal("123.45"), 123.45, "9999999999999.99"]
)
def test_exact_positive_cents_are_accepted_without_rounding(value):
    assert FinanceTransactionService(MagicMock(), "tenant").validate_balanced(
        balanced(value)
    ) == Decimal(str(value))


@pytest.fixture(scope="module")
def store():
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Existing shared PostgreSQL required")
    url = make_url(raw)
    assert url.database == "valeo_probe" or "test" in url.database.lower()
    engine = create_engine(url)
    name = "journalamount_" + uuid4().hex
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        for table in ("chart_of_accounts", "journal_entries", "journal_entry_lines"):
            conn.execute(
                text(
                    f'CREATE TABLE "{name}".{table} (LIKE domain_erp.{table} INCLUDING ALL)'
                )
            )

    with engine.begin() as conn:
        conn.execute(text(f'CREATE TABLE "{name}".finance_accounting_periods (LIKE public.finance_accounting_periods INCLUDING ALL)'))

    class OwnedSession(Session):
        def execute(self, statement, params=None, **kwargs):
            if isinstance(statement, TextClause):
                sql = (
                    str(statement)
                    .replace("FROM finance_accounting_periods", "FROM public.finance_accounting_periods")
                    .replace("INSERT INTO finance_accounting_periods", "INSERT INTO public.finance_accounting_periods")
                    .replace("UPDATE finance_accounting_periods", "UPDATE public.finance_accounting_periods")
                    .replace("domain_erp.", f'"{name}".')
                    .replace("public.finance_accounting_periods", f'"{name}".finance_accounting_periods')
                    .replace("(__[POSTCOMPILE_account_ids])", ":account_ids")
                )
                statement = text(sql)
                if "account_ids" in sql:
                    statement = statement.bindparams(
                        bindparam("account_ids", expanding=True)
                    )
            return super().execute(statement, params, **kwargs)

    try:
        yield (
            engine.execution_options(schema_translate_map={"domain_erp": name}),
            OwnedSession,
        )
    finally:
        assert (
            name.startswith("journalamount_")
            and len(name) == len("journalamount_") + 32
        )
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
        engine.dispose()


@pytest.fixture
def case(store):
    engine, factory = store
    with factory(engine) as db:
        tenant, account, contra, journal = (str(uuid4()) for _ in range(4))
        for ident in (account, contra):
            db.execute(
                text("""INSERT INTO domain_erp.chart_of_accounts
                (id,tenant_id,account_number,account_name,account_type,is_active,is_summary)
                VALUES (:id,:t,:n,'Amount proof','ASSET',TRUE,FALSE)"""),
                {"id": ident, "t": tenant, "n": uuid4().hex[:20]},
            )
        db.execute(
            text("""INSERT INTO domain_erp.journal_entries
            (id,tenant_id,entry_number,entry_date,posting_date,description,reference,status,
             total_debit,total_credit,sequence_number,hash_current,hash_prev)
            VALUES (:id,:t,:n,'2026-10-02','2026-10-02','Amount proof','REF','draft',10,10,1,:hash,NULL)"""),
            {"id": journal, "t": tenant, "n": uuid4().hex[:8], "hash": "a" * 64},
        )
        for index, (ident, debit, credit) in enumerate(
            ((account, 10, 0), (contra, 0, 10)), 1
        ):
            db.execute(
                text("""INSERT INTO domain_erp.journal_entry_lines
                (id,tenant_id,journal_entry_id,account_id,line_number,debit,credit,debit_amount,credit_amount)
                VALUES (:id,:t,:j,:a,:n,:d,:c,:d,:c)"""),
                {
                    "id": str(uuid4()),
                    "t": tenant,
                    "j": journal,
                    "a": ident,
                    "n": index,
                    "d": debit,
                    "c": credit,
                },
            )
        yield db, tenant, journal, account
        db.rollback()


@pytest.mark.parametrize("operation", ["post", "reverse"])
@pytest.mark.parametrize(
    "fault", ["empty", "zero", "negative", "nan", "alias", "header", "foreign", "inactive"]
)
def test_persisted_contradictions_prevent_lifecycle_changes(case, operation, fault):
    db, tenant, journal, account = case
    status = "draft" if operation == "post" else "posted"
    db.execute(
        text("UPDATE domain_erp.journal_entries SET status=:s WHERE id=:j"),
        {"s": status, "j": journal},
    )
    if fault == "empty":
        db.execute(
            text(
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": journal},
        )
    elif fault == "header":
        db.execute(
            text("UPDATE domain_erp.journal_entries SET total_debit=9 WHERE id=:j"),
            {"j": journal},
        )
    elif fault == "inactive":
        db.execute(
            text("UPDATE domain_erp.chart_of_accounts SET is_active=FALSE WHERE id=:a"),
            {"a": account},
        )
    else:
        assignments = {
            "zero": "debit=0,credit=0,debit_amount=0,credit_amount=0",
            "negative": "debit=-10,debit_amount=-10",
            "nan": "debit='NaN',debit_amount='NaN'",
            "alias": "debit=9",
            "foreign": "tenant_id='foreign-proof'",
        }
        db.execute(
            text(
                "UPDATE domain_erp.journal_entry_lines SET "
                + assignments[fault]
                + " WHERE journal_entry_id=:j AND line_number=1"
            ),
            {"j": journal},
        )
    service = FinanceTransactionService(db, tenant)
    with pytest.raises(ValidationFailedError):
        getattr(service, operation)(journal)
    assert (
        db.execute(
            text("SELECT status FROM domain_erp.journal_entries WHERE id=:j"),
            {"j": journal},
        ).scalar_one()
        == status
    )
    assert (
        db.execute(
            text("SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"),
            {"t": tenant},
        ).scalar_one()
        == 1
    )


def test_valid_persisted_journal_can_be_posted(case):
    db, tenant, journal, _ = case
    result = FinanceTransactionService(db, tenant).post(journal)
    assert result.status == "posted" and result.total_debit == Decimal("10.00")


def test_valid_persisted_journal_can_be_reversed_with_two_real_legs(case):
    db, tenant, journal, _ = case
    db.execute(
        text("UPDATE domain_erp.journal_entries SET status='posted' WHERE id=:j"),
        {"j": journal},
    )
    original, reversal = FinanceTransactionService(db, tenant).reverse(journal)
    assert original.status == "reversed" and reversal.total_debit == Decimal("10.00")
    assert (
        db.execute(
            text(
                "SELECT count(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id=:j"
            ),
            {"j": reversal.id},
        ).scalar_one()
        == 2
    )


def test_production_without_valuation_cannot_create_a_synthetic_journal():
    from app.api.v1.endpoints import produktion_mischfutter
    order = MagicMock(chargen_id="PROOF")
    order.fibu_journal_ref = None
    with patch("app.services.finance_transaction_service.FinanceTransactionService") as journal:
        produktion_mischfutter._report_missing_production_valuation(order)
        journal.assert_not_called()
    assert order.fibu_journal_ref is None
    assert not hasattr(produktion_mischfutter, "_post_produktion_to_fibu")
