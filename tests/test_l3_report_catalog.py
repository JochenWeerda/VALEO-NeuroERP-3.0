from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock
import pytest

from app.services.l3_report_catalog_service import (
    L3ReportCatalogService,
    ReportCatalogError,
)

pytestmark = pytest.mark.unit


def test_catalog_covers_all_prioritized_dimensions() -> None:
    catalog = L3ReportCatalogService(MagicMock(), "tenant-1").catalog()
    dimensions = {item["dimension"] for item in catalog}
    assert {
        "representative_id",
        "customer_id",
        "article_id",
        "article_group_id",
        "batch_id",
        "harvest_id",
        "route_id",
    }.issubset(dimensions)
    assert all(
        item["drilldown"] and item["export_formats"] == ["csv"] for item in catalog
    )
    report_ids = {item["id"] for item in catalog}
    assert {
        "article-account",
        "batch-number-register",
        "batch-stock-valuation",
        "batch-use-trace",
        "fertilizer-quantities",
        "bonus-by-customer",
        "customer-order-disposition",
        "customer-gifts",
        "grain-notification",
        "mvo-notification",
        "daily-close-journal",
    }.issubset(report_ids)
    assert len(catalog) >= 30
    assert all(item["category"] and item["legacy_menu"] for item in catalog)


def test_unknown_report_and_filter_are_rejected() -> None:
    service = L3ReportCatalogService(MagicMock(), "tenant-1")
    with pytest.raises(ReportCatalogError, match="nicht freigegeben"):
        service.run("sql", from_date=date(2026, 1, 1), to_date=date(2026, 12, 31))
    with pytest.raises(ReportCatalogError, match="Filter"):
        service.run(
            "sales-by-customer",
            from_date=date(2026, 1, 1),
            to_date=date(2026, 12, 31),
            filters={"raw_sql": "x"},
        )


def test_run_returns_shared_totals_and_tenant_scope() -> None:
    db = MagicMock()
    count = MagicMock()
    count.scalar_one.return_value = 1
    sums = MagicMock()
    sums.mappings.return_value.one.return_value = {
        "document_count": 2,
        "quantity": 5,
        "net_amount": 10,
        "gross_amount": 11.9,
    }
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [
        {"dimension_id": "C1", "gross_amount": 11.9}
    ]
    db.execute.side_effect = [count, sums, rows]
    result = L3ReportCatalogService(db, "tenant-1").run(
        "sales-by-customer", from_date=date(2026, 1, 1), to_date=date(2026, 12, 31)
    )
    assert (
        result["totals"]["gross_amount"] == 11.9
        and result["items"][0]["dimension_id"] == "C1"
    )
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_project_fact_requires_internal_drilldown_route() -> None:
    payload = {
        "source_type": "invoice",
        "source_ref": "1",
        "source_route": "https://evil.invalid",
        "occurred_on": "2026-08-21",
        "fact_type": "sale",
    }
    with pytest.raises(ReportCatalogError, match="intern"):
        L3ReportCatalogService(MagicMock(), "tenant-1").project_fact(payload)


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("auswertungen/l3-berichtskatalog")
    assert definition and definition["layout"]["tableProfile"] == "financial"
    assert _check_readiness(definition)["generatorReady"] is True
    bonus = get_screen_definition("auswertungen/bonus-berechnung")
    assert bonus["workflow"]["status"] == "immutable-runs"
    assert _check_readiness(bonus)["generatorReady"] is True


def test_bonus_run_rejects_unapproved_report() -> None:
    from decimal import Decimal

    service = L3ReportCatalogService(MagicMock(), "tenant-1")
    with pytest.raises(ReportCatalogError, match="Bonusberichte"):
        service.create_bonus_run(
            report_id="sales-by-customer",
            from_date=date(2026, 1, 1),
            to_date=date(2026, 12, 31),
            rate_pct=Decimal("1.5"),
            actor="tester",
            reason="Regressionstest",
        )


def test_bonus_correction_creates_exportable_line() -> None:
    from decimal import Decimal

    db = MagicMock()
    source = MagicMock()
    source.mappings.return_value.first.return_value = {
        "report_id": "bonus-by-customer",
        "from_date": date(2026, 1, 1),
        "to_date": date(2026, 12, 31),
        "currency": "EUR",
    }
    db.execute.side_effect = [source, MagicMock(), MagicMock()]
    result = L3ReportCatalogService(db, "tenant-1").correct_bonus_run(
        "run-1", amount=Decimal("-12.50"), actor="tester", reason="Reklamation"
    )
    assert result["status"] == "correction"
    line_sql = str(db.execute.call_args_list[2].args[0])
    line_params = db.execute.call_args_list[2].args[1]
    assert "l3_bonus_run_lines" in line_sql
    assert line_params["tid"] == "tenant-1" and line_params["amount"] == Decimal("-12.50")
