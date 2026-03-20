from __future__ import annotations

import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.bank_statement_import import import_bank_statement
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


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=True)


def test_bulk_operations_evaluate_detects_duplicate_journal_rows(client):
    payload = {
        "operation_typ": "CREATE",
        "domain": "finance",
        "ressource": "journal_entries",
        "entity_typ": "JournalImport",
        "items": [
            {
                "item_id": "row-1",
                "payload": {
                    "entry_date": "2026-03-15",
                    "account_number": "8400",
                    "description": "Import A",
                    "debit_amount": 100,
                    "credit_amount": 0,
                },
            },
            {
                "item_id": "row-1",
                "payload": {
                    "entry_date": "2026-03-15",
                    "account_number": "8400",
                    "description": "Import A",
                    "debit_amount": 100,
                    "credit_amount": 0,
                },
            },
        ],
        "trocken_lauf": True,
        "stop_bei_erstem_fehler": False,
    }

    resp = client.post("/api/v1/process/bulk-operations/evaluate", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["validation"]["gueltig"] is True
    assert data["bulk_result"]["duplicate_item_ids"] == ["row-1"]
    assert data["bulk_result"]["dq_fehler"] >= 1
    assert data["bulk_result"]["fehler_count"] >= 1


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


def test_payment_import_rejects_duplicate_rows_before_db_access():
    file = _upload(
        "payments.csv",
        "date,amount,reference\n2026-03-15,100.00,REF-1\n2026-03-15,100.00,REF-1\n",
    )

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
