from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.data_quality_enforcement import DQValidationException
from app.core.data_quality_rules import DQRuleSet, DQValidationResult, get_default_dq_rulesets, validate_datensatz


def _failing_result(entity_typ: str, datensatz: dict) -> DQValidationException:
    ruleset = get_default_dq_rulesets()[entity_typ]
    result = validate_datensatz(ruleset, datensatz)
    return DQValidationException(entity_typ, result)


def test_fibu_connector_import_rejects_invalid_payroll_csv_with_422(monkeypatch):
    from app.main import app
    from app.api.v1.endpoints import fibu_connectors

    def _create_run(db, tenant_id, connector_type, profile_id, idempotency_key, created_by):
        return "run-1"

    def _set_run_artifact(db, run_id, tenant_id, file_content, file_name, storage_key):
        return None

    def _parse_run(db, run_id, tenant_id, file_content):
        raise _failing_result(
            "PayrollConnectorImport",
            {"booking_date": "2026-03-15", "account": "", "amount": "120.00", "dc": "S"},
        )

    monkeypatch.setattr(fibu_connectors.workflow, "create_run", _create_run)
    monkeypatch.setattr(fibu_connectors.workflow, "set_run_artifact", _set_run_artifact)
    monkeypatch.setattr(fibu_connectors.workflow, "parse_run", _parse_run)

    client = TestClient(app)
    response = client.post(
        "/api/v1/finance/connectors/PAYROLL/imports",
        files={"file": ("payroll.csv", b"buchungsdatum;konto;betrag;soll_haben\n2026-03-15;;120;S\n", "text/csv")},
        headers={"X-Tenant-ID": "tenant-1"},
    )

    assert response.status_code == 422
    body = response.json()["detail"]
    assert body["entity_typ"] == "PayrollConnectorImport"


def test_connector_workflow_marks_run_failed_on_dq_exception():
    from app.core.connectors import workflow

    class FakeDB:
        def __init__(self):
            self.updates = []

        def execute(self, query, params):
            sql = str(query)
            if "SELECT connector_type, profile_id FROM domain_erp.fibu_connector_runs" in sql:
                return _Result(("PAYROLL", None))
            if "UPDATE domain_erp.fibu_connector_runs" in sql:
                self.updates.append(params)
                return _Result(None)
            raise AssertionError(f"Unexpected SQL: {sql}")

        def commit(self):
            return None

    class _Result:
        def __init__(self, row):
            self._row = row

        def fetchone(self):
            return self._row

    class FailingParser:
        def parse(self, raw, settings, mapping):
            raise _failing_result(
                "AssetLedgerConnectorImport",
                {"booking_date": "", "account": "0840", "amount": "500.00", "dc": "S"},
            )

    fake_db = FakeDB()
    original_get_parser = workflow.get_parser
    workflow.get_parser = lambda connector_type: FailingParser()
    try:
        try:
            workflow.parse_run(fake_db, "run-1", "tenant-1", b"broken")
        except DQValidationException as exc:
            assert exc.entity_typ == "AssetLedgerConnectorImport"
        else:
            raise AssertionError("DQValidationException expected")
    finally:
        workflow.get_parser = original_get_parser

    assert len(fake_db.updates) == 1
    assert fake_db.updates[0]["id"] == "run-1"
    assert fake_db.updates[0]["tenant_id"] == "tenant-1"
    assert "\"entity_typ\": \"AssetLedgerConnectorImport\"" in fake_db.updates[0]["err"]
