"""SPEC-P0-03 harte Regel: Finance-/Bestands-Endpoints duerfen bei DB-Fehlern
niemals still leere Daten liefern — sie muessen 5xx mit Problem-Details liefern
und die Alerting-Metrik critical_data_path_errors_total erhoehen.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app

HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}


class _BrokenSession:
    """Session-Stub, dessen Queries wie bei DB-/Schemafehlern scheitern."""

    def execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("simulierter DB-Ausfall"))

    def query(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("simulierter DB-Ausfall"))

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture()
def broken_db_client():
    app.dependency_overrides[get_db] = lambda: _BrokenSession()
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.pop(get_db, None)


def _metric_value(endpoint: str) -> float:
    from app.core.metrics import critical_data_path_errors_total

    return critical_data_path_errors_total.labels(
        endpoint=endpoint, error_type="db_error"
    )._value.get()


def test_journal_entries_db_error_returns_problem_details_not_empty_list(broken_db_client):
    before = _metric_value("journal_entries_list")
    resp = broken_db_client.get("/api/v1/journal-entries/", headers=HEADERS)
    assert resp.status_code == 503, resp.text
    body = resp.json()
    assert "items" not in body
    assert "nicht verfuegbar" in str(body.get("detail", ""))
    assert _metric_value("journal_entries_list") == before + 1


def test_inventory_bestand_db_error_returns_problem_details_not_empty_list(broken_db_client):
    before = _metric_value("inventory_bestand")
    resp = broken_db_client.get("/api/v1/lager/bestaende", headers=HEADERS)
    assert resp.status_code == 503, resp.text
    body = resp.json()
    assert body != []
    assert "nicht verfuegbar" in str(body.get("detail", ""))
    assert _metric_value("inventory_bestand") == before + 1


@pytest.mark.parametrize(
    "path,endpoint_label,metric_key",
    [
        (
            "/api/v1/finance/open-items/OP-1/settlements",
            "OP-Ausgleichshistorie",
            "open_items_settlements",
        ),
        (
            "/api/v1/finance/payments/unmatched",
            "Unmatched-Zahlungen",
            "payments_unmatched",
        ),
        (
            "/api/v1/finance/payments/open-items/CUST-1",
            "Offene Posten fuer Matching",
            "payments_open_items_match",
        ),
        (
            "/api/v1/finance/payments/match-suggestions/PAY-1",
            "Matching-Vorschlaege",
            "payments_match_suggestions",
        ),
        (
            "/api/v1/finance/bank-statements/STMT-1/lines",
            "Kontoauszugszeilen",
            "bank_statement_lines",
        ),
    ],
)
def test_finance_list_db_error_returns_503_not_empty_list(
    broken_db_client, path, endpoint_label, metric_key
):
    before = _metric_value(metric_key)
    resp = broken_db_client.get(path, headers=HEADERS)
    assert resp.status_code == 503, resp.text
    body = resp.json()
    assert body != []
    assert "items" not in body or body.get("items") is None
    detail = str(body.get("detail", ""))
    assert "nicht verfuegbar" in detail
    assert endpoint_label.split()[0] in detail or "nicht verfuegbar" in detail
    assert _metric_value(metric_key) == before + 1
