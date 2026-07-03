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
    return critical_data_path_errors_total.labels(endpoint=endpoint, error_type="db_error")._value.get()


def test_journal_entries_db_error_returns_problem_details_not_empty_list(broken_db_client):
    before = _metric_value("journal_entries_list")
    resp = broken_db_client.get("/api/v1/journal-entries/", headers=HEADERS)
    assert resp.status_code == 503, resp.text
    body = resp.json()
    # RFC-7807-Problem-Details statt stiller leerer Liste
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
