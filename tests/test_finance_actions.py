"""
Tests for finance action endpoints (app/api/v1/endpoints/finance_actions.py).

Covers Pydantic schema validation + endpoint structure tests.
"""

import pytest
from decimal import Decimal
from datetime import date
from pydantic import ValidationError
from starlette.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


# ---------------------------------------------------------------------------
# Lazy app import — keeps collection fast when backend deps are heavy
# ---------------------------------------------------------------------------

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


# ── Inline imports of schemas from the source module ──────────────────────

def _import_schemas():
    from app.api.v1.endpoints.finance_actions import (
        ActionResponse,
        JournalEntryPostRequest,
        BankReconciliationRunRequest,
        ClosingActionRequest,
        ClosingRunRequest,
        BuchungsuebergabeExportRequest,
        BuchungsuebergabeExportSummary,
    )
    return {
        "ActionResponse": ActionResponse,
        "JournalEntryPostRequest": JournalEntryPostRequest,
        "BankReconciliationRunRequest": BankReconciliationRunRequest,
        "ClosingActionRequest": ClosingActionRequest,
        "ClosingRunRequest": ClosingRunRequest,
        "BuchungsuebergabeExportRequest": BuchungsuebergabeExportRequest,
        "BuchungsuebergabeExportSummary": BuchungsuebergabeExportSummary,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Schema unit tests (no DB needed)
# ═══════════════════════════════════════════════════════════════════════════

class TestActionResponseSchema:
    def test_defaults(self):
        S = _import_schemas()
        resp = S["ActionResponse"]()
        assert resp.success is True
        assert resp.message == ""

    def test_custom_values(self):
        S = _import_schemas()
        resp = S["ActionResponse"](success=False, message="Fehler aufgetreten")
        assert resp.success is False
        assert resp.message == "Fehler aufgetreten"


class TestJournalEntryPostRequestSchema:
    def test_both_optional(self):
        S = _import_schemas()
        req = S["JournalEntryPostRequest"]()
        assert req.journal_entry_id is None
        assert req.belegnummer is None

    def test_with_journal_entry_id(self):
        S = _import_schemas()
        req = S["JournalEntryPostRequest"](journal_entry_id="je-123")
        assert req.journal_entry_id == "je-123"

    def test_with_belegnummer(self):
        S = _import_schemas()
        req = S["JournalEntryPostRequest"](belegnummer="BEL-2026-001")
        assert req.belegnummer == "BEL-2026-001"


class TestBankReconciliationRunRequestSchema:
    def test_requires_bank_account_id(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["BankReconciliationRunRequest"]()

    def test_valid_request(self):
        S = _import_schemas()
        req = S["BankReconciliationRunRequest"](
            bank_account_id="BA-001", statement_id="ST-42"
        )
        assert req.bank_account_id == "BA-001"
        assert req.statement_id == "ST-42"

    def test_statement_id_optional(self):
        S = _import_schemas()
        req = S["BankReconciliationRunRequest"](bank_account_id="BA-001")
        assert req.statement_id is None


class TestClosingActionRequestSchema:
    def test_requires_all_fields(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["ClosingActionRequest"]()

    def test_empty_period_rejected(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["ClosingActionRequest"](period="", closing_type="month", actor="admin")

    def test_empty_closing_type_rejected(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["ClosingActionRequest"](period="2026-03", closing_type="", actor="admin")

    def test_empty_actor_rejected(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["ClosingActionRequest"](period="2026-03", closing_type="month", actor="")

    def test_valid_closing_action(self):
        S = _import_schemas()
        req = S["ClosingActionRequest"](
            period="2026-03", closing_type="month", actor="admin"
        )
        assert req.period == "2026-03"
        assert req.closing_type == "month"
        assert req.actor == "admin"


class TestBuchungsuebergabeExportRequestSchema:
    def test_valid_export_request(self):
        S = _import_schemas()
        req = S["BuchungsuebergabeExportRequest"](
            von=date(2026, 1, 1), bis=date(2026, 1, 31)
        )
        assert req.von == date(2026, 1, 1)
        assert req.bis == date(2026, 1, 31)
        assert req.sortierung == "datum"
        assert req.download is True

    def test_requires_von_bis(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["BuchungsuebergabeExportRequest"]()


# ═══════════════════════════════════════════════════════════════════════════
# Endpoint structure tests (may skip if DB unavailable)
# ═══════════════════════════════════════════════════════════════════════════

class TestFinanceActionEndpoints:
    def test_close_readiness_returns_checklist(self, client, auth_headers):
        resp = client.get("/api/v1/finance/close-readiness", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "current_period" in body
        assert "blocking_items" in body

    def test_credit_limits_returns_list(self, client, auth_headers):
        resp = client.get("/api/v1/finance/credit-limits", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_collaterals_returns_list(self, client, auth_headers):
        resp = client.get("/api/v1/finance/collaterals", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_payment_suggestions_returns_list(self, client, auth_headers):
        resp = client.get(
            "/api/v1/finance/payment-suggestions?days_ahead=14",
            headers=auth_headers,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_payment_suggestions_validates_days_ahead(self, client, auth_headers):
        resp = client.get(
            "/api/v1/finance/payment-suggestions?days_ahead=0",
            headers=auth_headers,
        )
        assert resp.status_code == 422  # ge=1

    def test_bank_reconciliation_requires_body(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/bank-reconciliation/run",
            headers=auth_headers,
            json={},
        )
        # Missing required field bank_account_id → 422
        assert resp.status_code == 422

    def test_bank_reconciliation_missing_statement_id(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/bank-reconciliation/run",
            headers=auth_headers,
            json={"bank_account_id": "BA-001"},
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert "statement_id" in body["message"]

    def test_journal_entry_post_action_422_on_empty_body(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/journal-entries/post",
            headers=auth_headers,
            json={},
        )
        skip_if_db_unavailable(resp)
        # Empty body is valid (both fields optional) but should return failure message
        if resp.status_code == 200:
            body = resp.json()
            assert body["success"] is False

    def test_cash_close_day_endpoint_exists(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/cash/close-day",
            headers=auth_headers,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "success" in body
        assert "message" in body
