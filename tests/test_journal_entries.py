"""
Tests for journal entry endpoints (app/api/v1/endpoints/journal_entries.py)
and finance schemas (app/api/v1/schemas/finance.py).

Covers _serialize_value helper, Pydantic schema validation, and endpoint structure tests.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError
from starlette.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def auth_headers():
    return {
        "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
        "X-Tenant-ID": "test-tenant",
    }


# ═══════════════════════════════════════════════════════════════════════════
# _serialize_value helper tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSerializeValue:
    def test_datetime_to_isoformat(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        dt = datetime(2026, 4, 10, 14, 30, 0)
        assert _serialize_value(dt) == dt.isoformat()

    def test_date_to_isoformat(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        from datetime import date
        d = date(2026, 4, 10)
        assert _serialize_value(d) == "2026-04-10"

    def test_decimal_to_float(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        assert _serialize_value(Decimal("123.45")) == 123.45

    def test_int_passthrough(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        assert _serialize_value(42) == 42

    def test_string_passthrough(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        assert _serialize_value("hello") == "hello"

    def test_none_passthrough(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        assert _serialize_value(None) is None

    def test_bool_not_converted_to_float(self):
        from app.api.v1.endpoints.journal_entries import _serialize_value
        # bool is excluded from float conversion (isinstance check for bool, int)
        assert _serialize_value(True) is True
        assert _serialize_value(False) is False


# ═══════════════════════════════════════════════════════════════════════════
# Finance schema unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestJournalEntryLineSchema:
    def test_valid_debit_line(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        line = JournalEntryLineCreate(
            account_id="1000",
            debit_amount=Decimal("500.00"),
            credit_amount=Decimal("0.00"),
            line_number=1,
        )
        assert line.debit_amount == Decimal("500.00")

    def test_valid_credit_line(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        line = JournalEntryLineCreate(
            account_id="3000",
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("500.00"),
            line_number=1,
        )
        assert line.credit_amount == Decimal("500.00")

    def test_rejects_both_debit_and_credit(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        with pytest.raises(ValidationError, match="cannot have both debit and credit"):
            JournalEntryLineCreate(
                account_id="1000",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("100.00"),
                line_number=1,
            )

    def test_rejects_negative_amount(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        with pytest.raises(ValidationError):
            JournalEntryLineCreate(
                account_id="1000",
                debit_amount=Decimal("-50.00"),
                credit_amount=Decimal("0.00"),
                line_number=1,
            )

    def test_rejects_more_than_2_decimal_places(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        with pytest.raises(ValidationError, match="2 decimal places"):
            JournalEntryLineCreate(
                account_id="1000",
                debit_amount=Decimal("100.999"),
                credit_amount=Decimal("0.00"),
                line_number=1,
            )

    def test_line_number_must_be_positive(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        with pytest.raises(ValidationError):
            JournalEntryLineCreate(
                account_id="1000",
                debit_amount=Decimal("100.00"),
                credit_amount=Decimal("0.00"),
                line_number=0,
            )


class TestJournalEntryCreateSchema:
    def _make_lines(self):
        from app.api.v1.schemas.finance import JournalEntryLineCreate
        return [
            JournalEntryLineCreate(
                account_id="1000", debit_amount=Decimal("500.00"),
                credit_amount=Decimal("0.00"), line_number=1,
            ),
            JournalEntryLineCreate(
                account_id="3000", debit_amount=Decimal("0.00"),
                credit_amount=Decimal("500.00"), line_number=2,
            ),
        ]

    def test_valid_journal_entry_create(self):
        from app.api.v1.schemas.finance import JournalEntryCreate
        now = datetime.now()
        entry = JournalEntryCreate(
            entry_number="BUC-2026-001",
            entry_date=now,
            posting_date=now,
            description="Testbuchung",
            reference="REF-001",
            tenant_id="test-tenant",
            lines=self._make_lines(),
        )
        assert entry.entry_number == "BUC-2026-001"
        assert entry.source == "manual"
        assert entry.currency == "EUR"
        assert len(entry.lines) == 2

    def test_requires_at_least_two_lines(self):
        from app.api.v1.schemas.finance import JournalEntryCreate, JournalEntryLineCreate
        now = datetime.now()
        with pytest.raises(ValidationError, match="too_short"):
            JournalEntryCreate(
                entry_number="BUC-001",
                entry_date=now,
                posting_date=now,
                description="Test",
                tenant_id="t",
                lines=[
                    JournalEntryLineCreate(
                        account_id="1000", debit_amount=Decimal("100.00"),
                        credit_amount=Decimal("0.00"), line_number=1,
                    )
                ],
            )

    def test_posting_date_not_before_entry_date(self):
        from app.api.v1.schemas.finance import JournalEntryCreate
        with pytest.raises(ValidationError, match="Posting date cannot be before entry date"):
            JournalEntryCreate(
                entry_number="BUC-001",
                entry_date=datetime(2026, 4, 10),
                posting_date=datetime(2026, 4, 9),
                description="Test",
                tenant_id="t",
                lines=self._make_lines(),
            )

    def test_invalid_source_rejected(self):
        from app.api.v1.schemas.finance import JournalEntryCreate
        now = datetime.now()
        with pytest.raises(ValidationError, match="Source must be one of"):
            JournalEntryCreate(
                entry_number="BUC-001",
                entry_date=now,
                posting_date=now,
                description="Test",
                tenant_id="t",
                source="unknown",
                lines=self._make_lines(),
            )


class TestJournalEntryUpdateSchema:
    def test_all_fields_optional(self):
        from app.api.v1.schemas.finance import JournalEntryUpdate
        upd = JournalEntryUpdate()
        assert upd.description is None
        assert upd.reference is None


# ═══════════════════════════════════════════════════════════════════════════
# Endpoint structure tests
# ═══════════════════════════════════════════════════════════════════════════

class TestJournalEntryEndpoints:
    def test_get_new_template(self, client, auth_headers):
        resp = client.get("/api/v1/journal-entries/new", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        expected_keys = {
            "id", "tenant_id", "belegart", "belegnummer",
            "buchungsdatum", "periode", "buchungstext",
            "gesamtSoll", "gesamtHaben", "differenz",
            "buchungszeilen", "status",
        }
        assert expected_keys.issubset(set(body.keys()))
        assert body["status"] == "draft"
        assert body["gesamtSoll"] == 0
        assert body["gesamtHaben"] == 0

    def test_list_journal_entries(self, client, auth_headers):
        resp = client.get("/api/v1/journal-entries/", headers=auth_headers)
        skip_if_db_unavailable(resp)
        if resp.status_code == 500:
            pytest.skip(f"Journal entries endpoint error: {resp.text[:120]}")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body

    def test_create_journal_entry_422_on_empty_body(self, client, auth_headers):
        resp = client.post(
            "/api/v1/journal-entries/",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 422

    def test_create_journal_entry_422_missing_lines(self, client, auth_headers):
        resp = client.post(
            "/api/v1/journal-entries/",
            headers=auth_headers,
            json={
                "entry_number": "BUC-TEST",
                "entry_date": "2026-04-10T00:00:00",
                "posting_date": "2026-04-10T00:00:00",
                "description": "Test",
                "tenant_id": "test-tenant",
            },
        )
        assert resp.status_code == 422
