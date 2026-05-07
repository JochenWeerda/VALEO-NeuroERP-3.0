"""
Tests for Journal Entries API endpoints.

Covers /api/v1/journal-entries — GET /new, POST /, GET /, GET /{id},
PUT /{id}, POST /{id}/post, POST /{id}/reverse, DELETE /{id}
"""

from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
BASE = "/api/v1/journal-entries"

_BALANCED_PAYLOAD = {
    "entry_date": "2026-01-01T00:00:00",
    "description": "Test buchung",
    "reference": "REF-001",
    "lines": [
        {"account_id": "1000", "description": "Debit line", "debit_amount": "100.00", "credit_amount": "0.00"},
        {"account_id": "2000", "description": "Credit line", "debit_amount": "0.00", "credit_amount": "100.00"},
    ],
}

_UNBALANCED_PAYLOAD = {
    "entry_date": "2026-01-01T00:00:00",
    "description": "Unbalanced",
    "reference": "REF-002",
    "lines": [
        {"account_id": "1000", "description": "Debit", "debit_amount": "100.00", "credit_amount": "0.00"},
        {"account_id": "2000", "description": "Credit", "debit_amount": "0.00", "credit_amount": "50.00"},
    ],
}

_NO_REF_PAYLOAD = {
    "entry_date": "2026-01-01T00:00:00",
    "description": "Missing reference",
    "reference": "",
    "lines": [
        {"account_id": "1000", "description": "Debit", "debit_amount": "100.00", "credit_amount": "0.00"},
        {"account_id": "2000", "description": "Credit", "debit_amount": "0.00", "credit_amount": "100.00"},
    ],
}


# ---------------------------------------------------------------------------
# Integration tests (main app)
# ---------------------------------------------------------------------------

class TestJournalEntriesIntegration:
    def setup_method(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_get_new_template_no_db_needed(self):
        """GET /new only uses get_tenant_id — no DB touch."""
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        # Should return 200 even without DB
        assert r.status_code == 200

    def test_list_journal_entries_integration(self):
        r = self.client.get(f"{BASE}/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_get_nonexistent_entry_integration(self):
        r = self.client.get(f"{BASE}/DOES-NOT-EXIST-999", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)

    def test_delete_nonexistent_entry_integration(self):
        r = self.client.delete(f"{BASE}/DOES-NOT-EXIST-999", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)


# ---------------------------------------------------------------------------
# Unit tests — GET /new (no DB required)
# ---------------------------------------------------------------------------

class TestGetNewTemplate:
    def setup_method(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_get_new_returns_200(self):
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        assert r.status_code == 200

    def test_get_new_has_required_keys(self):
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        data = r.json()
        for key in ("id", "tenant_id", "belegart", "status"):
            assert key in data

    def test_get_new_id_is_none(self):
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        assert r.json()["id"] is None

    def test_get_new_status_is_draft(self):
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        assert r.json()["status"] == "draft"

    def test_get_new_tenant_id_present(self):
        r = self.client.get(f"{BASE}/new", headers=AUTH)
        assert r.json()["tenant_id"] is not None


# ---------------------------------------------------------------------------
# Unit tests — POST / validation (400 errors happen before DB)
# ---------------------------------------------------------------------------

class TestCreateJournalEntryValidation:
    def setup_method(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_post_unbalanced_returns_400(self):
        r = self.client.post(f"{BASE}/", json=_UNBALANCED_PAYLOAD, headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 400
        assert "balance" in r.json()["detail"].lower() or "debit" in r.json()["detail"].lower()

    def test_post_missing_reference_returns_400(self):
        r = self.client.post(f"{BASE}/", json=_NO_REF_PAYLOAD, headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 400

    def test_post_balanced_with_valid_ref_passes_validation(self):
        """Validation passes — may 500/201 depending on DB availability."""
        r = self.client.post(f"{BASE}/", json=_BALANCED_PAYLOAD, headers=AUTH)
        skip_if_db_unavailable(r)
        # If DB is up it might 201; validation did not reject it (not 400)
        assert r.status_code != 400
