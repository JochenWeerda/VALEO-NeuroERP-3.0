"""
COV-FIN-002: Tests for Finance Read Models API endpoints.

Covers /api/v1/finance/read-models — cockpits, cash closings,
settlement, projections status and rebuild.

Unit-Tests (kein DB, kein HTTP) für reine Projektionsfunktionen und Helper:
  _as_float, _parse_items_blob, _iso_date, _iso_datetime,
  _reporting_period_key, _map_cash_workflow_status,
  project_ap_invoice_cockpit, project_payment_run_cockpit,
  project_process_observation,
  project_cash_closing_snapshot, project_cash_closing_read_model,
  project_cash_closing_analysis, project_cash_closing_reporting,
  project_cash_closing_detail, default_process_observation_instances
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

from app.api.v1.endpoints.finance_read_models import (
    _as_float,
    _parse_items_blob,
    _iso_date,
    _iso_datetime,
    _reporting_period_key,
    _map_cash_workflow_status,
    project_ap_invoice_cockpit,
    project_payment_run_cockpit,
    project_process_observation,
    project_cash_closing_snapshot,
    project_cash_closing_read_model,
    project_cash_closing_analysis,
    project_cash_closing_reporting,
    project_cash_closing_detail,
    default_process_observation_instances,
    CashClosingReadModel,
    WorkflowInstanceSummary,
)

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestAPInvoiceCockpit:
    """GET /finance/read-models/ap-invoice-cockpit"""

    def test_returns_structured_cockpit(self):
        r = client.get("/api/v1/finance/read-models/ap-invoice-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "buckets" in data
        assert "total_count" in data


class TestPaymentRunCockpit:
    """GET /finance/read-models/payment-run-cockpit"""

    def test_returns_structured_cockpit(self):
        r = client.get("/api/v1/finance/read-models/payment-run-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "draft_count" in data
        assert "total_pending_amount" in data


class TestCashClosings:
    """GET /finance/read-models/cash-closings*"""

    def test_list_cash_closings(self):
        r = client.get("/api/v1/finance/read-models/cash-closings", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total_count" in data

    def test_cash_closings_analysis(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/analysis", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "total_count" in data
        assert "exception_count" in data

    def test_cash_closings_reporting(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/reporting", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "periods" in data
        assert "total_count" in data

    def test_get_closing_nonexistent_404(self):
        r = client.get("/api/v1/finance/read-models/cash-closings/NONEXISTENT", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestProcessObservation:
    """GET /finance/read-models/process-observation"""

    def test_returns_structured_observation(self):
        r = client.get("/api/v1/finance/read-models/process-observation", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data


class TestSettlementCockpit:
    """GET /finance/read-models/settlement-cockpit"""

    def test_returns_dict(self):
        r = client.get("/api/v1/finance/read-models/settlement-cockpit", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), dict)


class TestProjectionManagement:
    """POST/GET /finance/read-models/_rebuild, _status"""

    def test_status_returns_projection_state(self):
        r = client.get("/api/v1/finance/read-models/_status", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "projection_count" in data

    def test_rebuild_triggers_projection_refresh(self):
        r = client.post("/api/v1/finance/read-models/_rebuild", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "tenant_id" in data
        assert "rebuilt_at" in data
        assert "projections" in data


# ---------------------------------------------------------------------------
# Helper / utility unit tests (keine DB, kein HTTP)
# ---------------------------------------------------------------------------

NOW_UTC = datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc)
TENANT_UNIT = "unit-tenant"


def _closing_row(
    closing_id: str = "c-1",
    status: str = "offen",
    gross: float = 500.0,
    bar: float = 300.0,
    ec: float = 200.0,
    datum: str = "2026-05-04",
) -> dict[str, Any]:
    items: dict[str, Any] = {
        "umsatz_gesamt": gross,
        "umsatz_bar": bar,
        "bargeld_gezaehlt": bar,
        "differenz_bar": 0.0,
        "umsatz_ec": ec,
        "ec_abrechnung": ec,
        "umsatz_paypal": 0.0,
        "paypal_abrechnung": 0.0,
        "umsatz_b2b": 0.0,
        "tse_transaktionen": 10,
    }
    return {
        "id": closing_id,
        "periode": datum[:7],
        "status": status,
        "verantwortlicher": "Max Muster",
        "abschluss_datum": datum,
        "items": json.dumps(items),
        "created_at": NOW_UTC.isoformat(),
    }


def _snap(closing_id: str = "c-1", **kw):
    return project_cash_closing_snapshot(
        row=_closing_row(closing_id, **kw),
        tenant_cash_movement_count=5,
        journal_row=None,
    )


class TestAsFloat:
    def test_none(self):
        assert _as_float(None) == 0.0

    def test_string_number(self):
        assert _as_float("3.14") == pytest.approx(3.14)

    def test_integer(self):
        assert _as_float(42) == 42.0

    def test_invalid_string(self):
        assert _as_float("nope") == 0.0

    def test_empty_string(self):
        assert _as_float("") == 0.0


class TestParseItemsBlob:
    def test_none(self):
        assert _parse_items_blob(None) == {}

    def test_dict_passthrough(self):
        assert _parse_items_blob({"a": 1}) == {"a": 1}

    def test_json_string(self):
        assert _parse_items_blob('{"x": 99}') == {"x": 99}

    def test_invalid_json(self):
        assert _parse_items_blob("not-json") == {}

    def test_json_array_not_dict(self):
        assert _parse_items_blob("[1,2,3]") == {}


class TestIsoDate:
    def test_none(self):
        assert _iso_date(None) is None

    def test_datetime(self):
        assert _iso_date(datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc)) == "2026-05-04"

    def test_string_passthrough(self):
        assert _iso_date("2026-05-04") == "2026-05-04"


class TestIsoDatetime:
    def test_none(self):
        assert _iso_datetime(None) is None

    def test_datetime(self):
        result = _iso_datetime(datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc))
        assert "2026-05-04" in result
        assert "08:00" in result

    def test_string_passthrough(self):
        assert _iso_datetime("2026-05-04T08:00:00") == "2026-05-04T08:00:00"


class TestReportingPeriodKey:
    def test_none(self):
        assert _reporting_period_key(None) == "ohne-periode"

    def test_truncates(self):
        assert _reporting_period_key("2026-05-04") == "2026-05"

    def test_short_value(self):
        assert _reporting_period_key("2026") == "2026"


class TestMapCashWorkflowStatus:
    def test_missing_posting_trumps_all(self):
        assert _map_cash_workflow_status("gebucht", has_posting=False, has_missing_posting=True) == "exception"

    def test_gebucht_with_posting(self):
        assert _map_cash_workflow_status("gebucht", has_posting=True, has_missing_posting=False) == "posted"

    def test_gebucht_without_posting(self):
        assert _map_cash_workflow_status("gebucht", has_posting=False, has_missing_posting=False) == "booked"

    def test_reconciled_variants(self):
        for raw in ("reconciled", "abgeglichen"):
            assert _map_cash_workflow_status(raw, has_posting=True, has_missing_posting=False) == "reconciled"

    def test_draft_variants(self):
        for raw in ("draft", "offen", "open"):
            assert _map_cash_workflow_status(raw, has_posting=False, has_missing_posting=False) == "draft"

    def test_unknown_with_posting(self):
        assert _map_cash_workflow_status(None, has_posting=True, has_missing_posting=False) == "posted"

    def test_unknown_without_posting(self):
        assert _map_cash_workflow_status(None, has_posting=False, has_missing_posting=False) == "draft"


class TestProjectApInvoiceCockpit:
    def test_empty(self):
        r = project_ap_invoice_cockpit(TENANT_UNIT, [])
        assert r.total_count == 0
        assert r.pending_approval_count == 0

    def test_bucket_aggregation(self):
        invoices = [
            {"semantic_status": "ZUR_FREIGABE", "amount": 100.0},
            {"semantic_status": "ZUR_FREIGABE", "amount": 200.0},
            {"semantic_status": "GEBUCHT", "amount": 500.0},
        ]
        r = project_ap_invoice_cockpit(TENANT_UNIT, invoices)
        assert r.total_count == 3
        assert r.pending_approval_count == 2
        buckets = {b.status: b for b in r.buckets}
        assert buckets["ZUR_FREIGABE"].total_amount == pytest.approx(300.0)

    def test_ready_to_post_flag(self):
        invoices = [{"semantic_status": "ZUR_FREIGABE", "amount": 0, "approval_can_post": True}]
        r = project_ap_invoice_cockpit(TENANT_UNIT, invoices)
        assert r.ready_to_post_count == 1

    def test_overdue_draft_detection(self):
        old = (datetime.now(tz=timezone.utc) - timedelta(days=35)).isoformat()
        recent = datetime.now(tz=timezone.utc).isoformat()
        invoices = [
            {"semantic_status": "ENTWURF", "amount": 0, "created_at": old},
            {"semantic_status": "ENTWURF", "amount": 0, "created_at": recent},
        ]
        r = project_ap_invoice_cockpit(TENANT_UNIT, invoices)
        assert r.overdue_count == 1

    def test_fallback_to_status_field(self):
        invoices = [{"status": "ENTWURF", "netAmount": 50.0}]
        r = project_ap_invoice_cockpit(TENANT_UNIT, invoices)
        assert r.total_count == 1
        assert r.buckets[0].total_amount == pytest.approx(50.0)


class TestProjectPaymentRunCockpit:
    def test_empty(self):
        r = project_payment_run_cockpit(TENANT_UNIT, [])
        assert r.draft_count == 0
        assert r.total_pending_amount == 0.0

    def test_draft_run(self):
        r = project_payment_run_cockpit(TENANT_UNIT, [{"status": "draft", "total_amount": 1000.0}])
        assert r.draft_count == 1
        assert r.total_pending_amount == pytest.approx(1000.0)

    def test_approved_via_flag(self):
        r = project_payment_run_cockpit(
            TENANT_UNIT, [{"status": "pending", "total_amount": 500.0, "approval_can_execute": True}]
        )
        assert r.approved_count == 1

    def test_approved_via_status(self):
        r = project_payment_run_cockpit(TENANT_UNIT, [{"status": "approved", "total_amount": 200.0}])
        assert r.approved_count == 1

    def test_executed_not_in_pending(self):
        r = project_payment_run_cockpit(TENANT_UNIT, [{"status": "executed", "total_amount": 999.0}])
        assert r.executed_count == 1
        assert r.total_pending_amount == 0.0

    def test_mixed_runs(self):
        runs = [
            {"status": "draft", "total_amount": 100.0},
            {"status": "approved", "total_amount": 200.0},
            {"status": "executed", "total_amount": 300.0},
        ]
        r = project_payment_run_cockpit(TENANT_UNIT, runs)
        assert r.draft_count == 1
        assert r.approved_count == 1
        assert r.executed_count == 1
        assert r.total_pending_amount == pytest.approx(300.0)


class TestProjectProcessObservation:
    def test_default_instances_four_processes(self):
        instances = default_process_observation_instances()
        assert len(instances) == 4
        keys = {i.process_key for i in instances}
        assert "ap_approval" in keys
        assert "payment_run" in keys

    def test_aggregates_counts(self):
        instances = [
            WorkflowInstanceSummary(process_key="ap_approval", running_count=3, waiting_count=1),
            WorkflowInstanceSummary(process_key="payment_run", running_count=2, waiting_count=0),
        ]
        r = project_process_observation(TENANT_UNIT, instances, sla_profiles=[], overdue_instances=5)
        assert r.total_running == 5
        assert r.total_waiting == 1
        assert r.overdue_instances == 5


class TestProjectCashClosingSnapshot:
    def test_basic_fields(self):
        s = _snap("c-1")
        assert s.id == "c-1"
        assert s.totals.gross_total == pytest.approx(500.0)
        assert s.source == "POS"

    def test_missing_posting_flag_when_gross_and_no_journal(self):
        s = _snap("c-2", gross=100.0)
        assert s.exception_flags.has_missing_posting is True

    def test_no_missing_posting_when_journal_present(self):
        row = _closing_row("c-3", gross=500.0, status="gebucht")
        journal = {"id": "j-1", "entry_number": "BU-001", "posting_date": NOW_UTC, "status": "posted"}
        s = project_cash_closing_snapshot(row=row, tenant_cash_movement_count=0, journal_row=journal)
        assert s.exception_flags.has_missing_posting is False
        assert s.posting.journal_entry_id == "j-1"
        assert s.workflow_status == "posted"

    def test_cash_difference_detected(self):
        row = _closing_row("c-4")
        items = json.loads(row["items"])
        items["differenz_bar"] = 15.0
        row["items"] = json.dumps(items)
        s = project_cash_closing_snapshot(row=row, tenant_cash_movement_count=0, journal_row=None)
        assert s.exception_flags.has_difference is True

    def test_no_difference_when_balanced(self):
        s = _snap("c-5", gross=500.0)  # differenz_bar=0 by default
        assert s.exception_flags.has_difference is False

    def test_import_source_label_set_when_movements(self):
        s = _snap("c-6")  # tenant_cash_movement_count=5
        assert s.import_context.import_source_label == "cash_movements"

    def test_import_source_label_none_without_movements(self):
        row = _closing_row("c-7")
        s = project_cash_closing_snapshot(row=row, tenant_cash_movement_count=0, journal_row=None)
        assert s.import_context.import_source_label is None

    def test_tse_transaction_count(self):
        assert _snap("c-8").reference_context.tse_transaction_count == 10

    def test_source_document_refs_include_checkliste(self):
        s = _snap("c-9")
        assert any("abschluss_checklisten:c-9" in ref for ref in s.reference_context.source_document_refs)


class TestProjectCashClosingReadModel:
    def test_empty(self):
        r = project_cash_closing_read_model(
            tenant_id=TENANT_UNIT, closing_rows=[], tenant_cash_movement_count=0,
            journal_resolver=lambda _: None,
        )
        assert r.total_count == 0
        assert r.items == []

    def test_multiple_rows(self):
        rows = [_closing_row("c-1"), _closing_row("c-2")]
        r = project_cash_closing_read_model(
            tenant_id=TENANT_UNIT, closing_rows=rows, tenant_cash_movement_count=0,
            journal_resolver=lambda _: None,
        )
        assert r.total_count == 2
        assert {i.id for i in r.items} == {"c-1", "c-2"}


class TestProjectCashClosingAnalysis:
    def _model(self, snaps: list) -> CashClosingReadModel:
        return CashClosingReadModel(tenant_id=TENANT_UNIT, items=snaps, total_count=len(snaps), schema_version=1)

    def test_no_exceptions_on_zero_gross(self):
        row = _closing_row("c-clean", gross=0.0, bar=0.0, ec=0.0)
        s = project_cash_closing_snapshot(row=row, tenant_cash_movement_count=0, journal_row=None)
        a = project_cash_closing_analysis(self._model([s]))
        assert a.missing_posting_count == 0

    def test_missing_posting_counted(self):
        snaps = [_snap("c-1"), _snap("c-2")]  # both have gross>0, no journal
        a = project_cash_closing_analysis(self._model(snaps))
        assert a.missing_posting_count == 2
        assert a.total_count == 2

    def test_top_exception_operators_sorted(self):
        snaps = [_snap(f"c-{i}") for i in range(3)]
        a = project_cash_closing_analysis(self._model(snaps))
        assert a.top_exception_operators[0].key == "Max Muster"
        assert a.top_exception_operators[0].count == 3


class TestProjectCashClosingReporting:
    def _model(self, snaps: list) -> CashClosingReadModel:
        return CashClosingReadModel(tenant_id=TENANT_UNIT, items=snaps, total_count=len(snaps), schema_version=1)

    def test_single_period_aggregation(self):
        snaps = [_snap("c-1"), _snap("c-2")]
        r = project_cash_closing_reporting(self._model(snaps))
        assert len(r.periods) == 1
        assert r.periods[0].period_key == "2026-05"
        assert r.periods[0].closing_count == 2
        assert r.total_gross == pytest.approx(1000.0)

    def test_two_periods(self):
        row_b = {**_closing_row("c-b"), "abschluss_datum": "2026-04-15", "periode": "2026-04"}
        s_a = _snap("c-a")
        s_b = project_cash_closing_snapshot(row=row_b, tenant_cash_movement_count=0, journal_row=None)
        r = project_cash_closing_reporting(self._model([s_a, s_b]))
        keys = {p.period_key for p in r.periods}
        assert "2026-05" in keys
        assert "2026-04" in keys

    def test_missing_posting_counted_in_period(self):
        snaps = [_snap("c-1")]  # has_missing_posting=True
        r = project_cash_closing_reporting(self._model(snaps))
        assert r.periods[0].missing_posting_count == 1


class TestProjectCashClosingDetail:
    def _model(self, *ids: str) -> CashClosingReadModel:
        snaps = [_snap(i) for i in ids]
        return CashClosingReadModel(tenant_id=TENANT_UNIT, items=snaps, total_count=len(snaps), schema_version=1)

    def test_found(self):
        m = self._model("c-target", "c-other")
        result = project_cash_closing_detail(m, "c-target")
        assert result is not None
        assert result.id == "c-target"

    def test_not_found(self):
        m = CashClosingReadModel(tenant_id=TENANT_UNIT, items=[], total_count=0, schema_version=1)
        assert project_cash_closing_detail(m, "missing") is None
