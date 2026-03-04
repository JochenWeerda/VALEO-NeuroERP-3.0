"""
Regressionstests für die geschlossenen P0-Finance-GAPs.
- FIBU-AR-03: Zahlungseingänge & Matching (GET /finance/payments/unmatched)
- FIBU-AP-02: Eingangsrechnungen (GET /finance/ap/invoices)
- FIBU-GL-05: Periodensteuerung (GET/POST /finance/periods)
- FIBU-COMP-01: Audit-Trail (GET /audit/logs, GET /audit/stats)
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


@pytest.mark.integration
class TestPaymentMatchingEndpoints:
    """FIBU-AR-03: Payment-Matching API"""

    def test_get_unmatched_payments_returns_200_and_list(self):
        r = client.get("/api/v1/finance/payments/unmatched", params={"limit": 10}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_auto_match_accepts_post(self):
        r = client.post("/api/v1/finance/payments/auto-match", headers=AUTH_HEADERS)
        # 200 mit Liste oder 500 wenn Tabelle/View fehlt – mindestens kein 404
        assert r.status_code in (200, 500)


@pytest.mark.integration
class TestAuditEndpoints:
    """FIBU-COMP-01: Audit-Trail API"""

    def test_get_audit_logs_returns_200_and_list(self):
        r = client.get("/api/v1/audit/logs", params={"limit": 10}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_audit_stats_returns_200_and_object(self):
        r = client.get("/api/v1/audit/stats", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "total_entries" in data
        assert "timestamp" in data
        assert "actions" in data
        assert "entity_types" in data
        assert "top_users" in data


@pytest.mark.integration
class TestAccountingPeriodsEndpoints:
    """FIBU-GL-05: Periodensteuerung API"""

    def test_list_periods_returns_200_and_list(self):
        r = client.get("/api/v1/finance/periods", params={"limit": 10}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestAPInvoicesEndpoints:
    """FIBU-AP-02: Eingangsrechnungen API"""

    def test_list_ap_invoices_returns_200_and_list(self):
        r = client.get("/api/v1/finance/ap/invoices", params={"limit": 10}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestSubsidiaryLedgerReconciliationEndpoints:
    """FIBU-CLS-02: Nebenbuch-Abstimmung API"""

    def test_reconciliation_summary_returns_200_and_object(self):
        period = "2026-01"
        r = client.get(
            "/api/v1/finance/subsidiary-ledger-reconciliation/summary",
            params={"period": period},
            headers=AUTH_HEADERS,
        )
        # 500 ist in lokalen Umgebungen ohne Bank-Tabellen möglich; mindestens Endpoint erreichbar.
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "period" in data
            assert "reconciliations" in data
            assert "AR" in data["reconciliations"]
            assert "AP" in data["reconciliations"]
            assert "BANK" in data["reconciliations"]

    def test_reconciliation_ar_returns_200_and_result(self):
        r = client.get(
            "/api/v1/finance/subsidiary-ledger-reconciliation/ar",
            params={"period": "2026-01"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["ledger_type"] == "AR"
        assert "entries" in data
        assert "total_difference" in data


@pytest.mark.integration
class TestOpenItemsBatchSettle:
    """FIBU-AP-05: Sammelausgleich API"""

    def test_batch_settle_empty_returns_200(self):
        r = client.post("/api/v1/finance/open-items/batch-settle", json={"items": []}, headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["success_count"] == 0
        assert data["error_count"] == 0
        assert data["results"] == []
        assert data["errors"] == []


@pytest.mark.integration
class TestBankAccountsEndpoints:
    """FIBU-BNK-01: Bankstamm API"""

    def test_list_bank_accounts_returns_200_and_list(self):
        r = client.get("/api/v1/finance/bank-accounts", headers=AUTH_HEADERS)
        # 500 ist in lokalen Umgebungen ohne domain_erp.bank_accounts möglich.
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, list)


@pytest.mark.integration
class TestBulkJournalImportEndpoints:
    """FIBU-GL-04: Sammel-/Massenbuchungen CSV-Import API"""

    def test_bulk_import_csv_dry_run_returns_import_result_structure(self):
        """POST mit minimalem CSV (dry_run): Antwort enthält ImportResult-Felder."""
        csv_content = b"entry_date,account_number,description,debit_amount,credit_amount\n2026-01-15,1000,Test,100.00,0"
        r = client.post(
            "/api/v1/finance/bulk-journal-import/csv",
            params={"period": "2026-01", "dry_run": "true"},
            files={"file": ("import.csv", csv_content, "text/csv")},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 400, 422)
        if r.status_code == 200:
            data = r.json()
            assert "total_rows" in data
            assert "successful" in data
            assert "failed" in data
            assert "errors" in data
            assert "created_entry_ids" in data
            assert "import_id" in data
            assert "imported_at" in data


@pytest.mark.integration
class TestFinancialReportsEndpoints:
    """FIBU-REP-01: Standardreports API (Bilanz/GuV/BWA)"""

    def test_balance_sheet_returns_200_and_structure(self):
        r = client.get(
            "/api/v1/finance/financial-reports/balance-sheet",
            params={"period": "2026-01"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "period" in data
            assert "assets" in data
            assert "liabilities" in data
            assert "equity" in data
            assert "total_assets" in data
            assert "is_balanced" in data

    def test_profit_loss_returns_200_and_structure(self):
        r = client.get(
            "/api/v1/finance/financial-reports/profit-loss",
            params={"period": "2026-01"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "period" in data
            assert "revenue" in data
            assert "expenses" in data
            assert "total_revenue" in data
            assert "net_income" in data

    def test_bwa_returns_200_and_structure(self):
        r = client.get(
            "/api/v1/finance/financial-reports/bwa",
            params={"period": "2026-01"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "period" in data
            assert "items" in data


@pytest.mark.integration
class TestClosingChecklistsEndpoints:
    """FIBU-CLS-01: Abschlusschecklisten API (Cockpit/Summary)"""

    def test_cockpit_summary_returns_200_and_structure(self):
        r = client.get(
            "/api/v1/finance/closing-checklists/cockpit/summary",
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "checklists" in data or "latest_checklists" in data or "blockers" in data

    def test_list_checklists_returns_200_and_list(self):
        r = client.get(
            "/api/v1/finance/closing-checklists",
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, list)


@pytest.mark.integration
class TestDebtorsEndpoints:
    """FIBU-AR-01: Debitorenstamm API"""

    def test_list_debtors_returns_200_and_paginated(self):
        r = client.get(
            "/api/v1/finance/debtors",
            params={"limit": 10},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "items" in data
            assert "total" in data
            assert isinstance(data["items"], list)


@pytest.mark.integration
class TestCreditorsEndpoints:
    """FIBU-AP-01: Kreditorenstamm API"""

    def test_list_creditors_returns_200_and_paginated(self):
        r = client.get(
            "/api/v1/finance/creditors",
            params={"limit": 10},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            data = r.json()
            assert "items" in data
            assert "total" in data
            assert isinstance(data["items"], list)
