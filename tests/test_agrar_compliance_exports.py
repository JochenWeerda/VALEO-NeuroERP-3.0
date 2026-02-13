from types import SimpleNamespace

from app.api.v1.endpoints.compliance import (
    _build_lot_trace_report,
    _compute_nutrient_stream,
    _extract_hazard_export_rows,
)


def test_extract_hazard_export_rows_filters_psm_lines():
    deliveries = [
        {
            "number": "LS-1",
            "date": "2026-01-10",
            "supplierName": "Supplier A",
            "customerId": "C-1",
            "psmCompliance": {"compliant": True, "sachkundeStatus": "geprueft", "sdsMitgeliefert": "ja"},
            "lines": [
                {"article": "PSM A", "bvlZulassungsnummer": "024567-00", "hazardHinweise": "H302", "sdsReference": "SDS-1"},
                {"article": "Normal", "qty": 1},
            ],
        }
    ]
    rows = _extract_hazard_export_rows(deliveries, year=2026)
    assert len(rows) == 1
    assert rows[0]["bvlZulassungsnummer"] == "024567-00"


def test_compute_nutrient_stream_monthly_aggregation():
    deliveries = [
        {"date": "2026-01-10", "totalNutrientNKg": 100, "totalNutrientP2o5Kg": 30},
        {"date": "2026-01-20", "totalNutrientNKg": 50, "totalNutrientP2o5Kg": 20},
        {"date": "2026-02-02", "totalNutrientNKg": 80, "totalNutrientP2o5Kg": 25},
    ]
    data = _compute_nutrient_stream(deliveries, year=2026)
    assert data["deliveryCount"] == 3
    assert data["totalNutrientNKg"] == 230.0
    assert data["byMonth"]["2026-01"]["p2o5_kg"] == 50.0


def test_build_lot_trace_report_links_matching_delivery_lines():
    lot = SimpleNamespace(
        id="CH-1",
        chargen_id="LOT-2026-001",
        artikel="Weizen",
        artikel_id="ART-1",
        menge=25.0,
        lagerort="Silo 1",
        status="freigegeben",
        qualitaetsstatus="ok",
        herkunft="Landwirt A",
        eingang=None,
        updated_at=None,
    )
    deliveries = [
        {"number": "LS-1", "date": "2026-02-01", "customerId": "C-1", "lines": [{"articleId": "ART-1", "article": "Weizen", "qty": 5}]},
        {"number": "LS-2", "date": "2026-02-03", "customerId": "C-2", "lines": [{"batchNumber": "LOT-2026-001", "article": "Weizen", "qty": 3}]},
    ]
    report = _build_lot_trace_report(lot, deliveries)
    assert report["deliveryCount"] == 2
