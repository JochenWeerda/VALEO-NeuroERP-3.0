from __future__ import annotations

import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints.bank_statement_import import import_bank_statement
from app.api.v1.endpoints.bulk_journal_import import import_journal_entries_csv
from app.api.v1.endpoints.payment_matching import import_payments_csv


class FailImportDB:
    def execute(self, *args, **kwargs):
        raise AssertionError("DB write path should not be reached before DQ validation")

    def commit(self):
        raise AssertionError("commit should not happen before DQ validation")

    def rollback(self):
        raise AssertionError("rollback should not happen before DQ validation")


def _upload(name: str, content: str) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content.encode("utf-8")))


def test_bank_statement_csv_rejects_duplicate_rows_before_db_access():
    file = _upload(
        "statement.csv",
        "date,value_date,amount,reference\n2026-03-15,2026-03-15,100.00,REF-1\n2026-03-15,2026-03-15,100.00,REF-1\n",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            import_bank_statement(
                file=file,
                format="CSV",
                bank_account_id="bank-1",
                tenant_id="tenant-1",
                auto_match=False,
                db=FailImportDB(),
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "KontoauszugImport"


def test_bulk_journal_import_rejects_invalid_row_before_period_or_db_work():
    file = _upload("journal.csv", "entry_date,account_number,description,debit_amount,credit_amount\n2026-03-15,8400,Test,0,0\n")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            import_journal_entries_csv(
                file=file,
                period="2026-03",
                tenant_id="tenant-1",
                delimiter=",",
                dry_run=True,
                db=FailImportDB(),
                request=None,
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "JournalImport"


def test_payment_import_rejects_invalid_row_before_db_access():
    file = _upload("payments.csv", "date,amount,reference\n2026-03-15,-10.00,REF-1\n")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            import_payments_csv(
                file=file,
                tenant_id="tenant-1",
                bank_account="bank-1",
                db=FailImportDB(),
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Zahlungsimport"
