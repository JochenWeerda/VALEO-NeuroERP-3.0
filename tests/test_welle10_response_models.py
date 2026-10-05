"""SPEC-P1-06 Welle 10: L3-Berichtskatalog und Query-Center."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.api.v1.endpoints import l3_report_catalog as l3_module
from app.api.v1.endpoints import query_center as qc_module
from app.api.v1.schemas import reporting_bundle_schemas as rep

pytestmark = pytest.mark.unit

WELLE10_MODULE = [l3_module, qc_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = getattr(route, "response_model", None)
    return out


@pytest.mark.parametrize("module", WELLE10_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if model is None:
            # CSV-Exports nutzen response_class=Response ohne Body-Modell.
            continue
        text = str(model)
        if (
            model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


def test_l3_catalog_bonus_fact_run_drilldown():
    _assert_kein_feldverlust(
        rep.L3ReportCatalogOut,
        {
            "items": [
                {
                    "id": "sales-by-customer",
                    "title": "Umsatz",
                    "category": "verkauf",
                    "description": "desc",
                    "legacy_menu": "AW",
                    "dimension": "customer_id",
                    "parameters": ["from_date", "to_date"],
                    "sums": ["document_count", "quantity", "net_amount", "gross_amount"],
                    "export_formats": ["csv"],
                    "drilldown": True,
                }
            ],
            "count": 1,
        },
    )
    _assert_kein_feldverlust(
        rep.L3BonusRunListOut,
        {
            "items": [
                {
                    "id": "r1",
                    "report_id": "bonus-by-customer",
                    "from_date": date(2026, 1, 1),
                    "to_date": date(2026, 12, 31),
                    "rate_pct": Decimal("2.5"),
                    "status": "calculated",
                    "total_basis": Decimal("100"),
                    "total_bonus": Decimal("2.5"),
                    "currency": "EUR",
                    "correction_of": None,
                    "reason": "Jahresbonus",
                    "actor": "u1",
                    "created_at": datetime(2026, 9, 1),
                }
            ],
            "total": 1,
            "calculated": 1,
            "corrections": 0,
            "total_bonus": Decimal("2.5"),
        },
    )
    _assert_kein_feldverlust(
        rep.L3BonusRunCreatedOut,
        {
            "id": "r1",
            "status": "calculated",
            "lines": 3,
            "total_basis": Decimal("100"),
            "total_bonus": Decimal("2.5"),
        },
    )
    _assert_kein_feldverlust(
        rep.L3BonusCorrectionOut,
        {
            "id": "c1",
            "status": "correction",
            "correction_of": "r1",
            "total_bonus": Decimal("-1"),
        },
    )
    _assert_kein_feldverlust(
        rep.L3FactProjectedOut, {"id": "f1", "payload_hash": "abc"}
    )
    _assert_kein_feldverlust(
        rep.L3ReportRunOut,
        {
            "report_id": "sales-by-customer",
            "title": "Umsatz",
            "items": [
                {
                    "dimension_id": "K-1",
                    "dimension_name": "Hof",
                    "document_count": 2,
                    "quantity": 10.0,
                    "net_amount": 100.0,
                    "gross_amount": 119.0,
                    "currency": "EUR",
                }
            ],
            "totals": {
                "document_count": 2,
                "quantity": 10.0,
                "net_amount": 100.0,
                "gross_amount": 119.0,
            },
            "total": 1,
            "page": 1,
            "page_size": 100,
            "parameters": {"from_date": "2026-01-01", "to_date": "2026-12-31"},
        },
    )
    _assert_kein_feldverlust(
        rep.L3DrilldownRowOut,
        {
            "source_type": "invoice",
            "source_ref": "inv-1",
            "source_number": "RE-1",
            "source_route": "/verkauf/rechnungen/1",
            "occurred_on": date(2026, 6, 1),
            "fact_type": "sales",
            "quantity": 1.0,
            "net_amount": 50.0,
            "gross_amount": 59.5,
            "currency": "EUR",
            "payload_hash": "xyz",
        },
    )


def test_query_center_catalog_page_preview_save_export():
    _assert_kein_feldverlust(
        rep.QueryCatalogOut,
        {
            "items": [
                {
                    "id": "product-a",
                    "fields": ["a", "b"],
                    "aggregations": ["count", "sum:a"],
                }
            ],
            "count": 1,
        },
    )
    _assert_kein_feldverlust(
        rep.QueryDefinitionPageOut,
        {
            "items": [
                {
                    "id": "d1",
                    "name": "Meine Abfrage",
                    "data_product_id": "product-a",
                    "selected_fields": ["a"],
                    "filter_spec": {"a": "x"},
                    "aggregations": ["count"],
                    "is_favorite": True,
                    "created_at": datetime(2026, 9, 1),
                    "updated_at": datetime(2026, 9, 2),
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
        },
    )
    _assert_kein_feldverlust(
        rep.QueryPreviewOut,
        {
            "items": [{"a": 1, "b": "x"}],
            "total": 10,
            "limit": 100,
            "truncated": False,
        },
    )
    saved = {
        "id": "d1",
        "name": "Meine Abfrage",
        "data_product_id": "product-a",
        "selected_fields": ["a"],
        "filter_spec": {},
        "aggregations": [],
        "is_favorite": False,
    }
    _assert_kein_feldverlust(rep.QueryDefinitionSavedOut, saved)
    _assert_kein_feldverlust(
        rep.QueryExportBundleOut,
        {
            "schema_version": 1,
            "definition": saved,
            "algorithm": "HMAC-SHA256",
            "signature": "deadbeef",
        },
    )
