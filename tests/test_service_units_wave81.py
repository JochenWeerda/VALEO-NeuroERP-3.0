"""Wave 81 — Unit-Tests fuer compliance_service (nutrient_stream, hazard_export) und einkauf_compat cache_key."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# compliance_service — compute_nutrient_stream  (pure aggregation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compute_nutrient_stream_basic() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    deliveries = [{"date": "2024-01-15", "totalNutrientNKg": 180.0, "totalNutrientP2o5Kg": 50.0}]
    result = compute_nutrient_stream(deliveries, year=2024)
    assert result["year"] == 2024
    assert result["deliveryCount"] == 1
    assert result["totalNutrientNKg"] == pytest.approx(180.0)
    assert result["totalNutrientP2o5Kg"] == pytest.approx(50.0)


@pytest.mark.unit
def test_compute_nutrient_stream_empty() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    result = compute_nutrient_stream([], year=2024)
    assert result["deliveryCount"] == 0
    assert result["totalNutrientNKg"] == 0.0


@pytest.mark.unit
def test_compute_nutrient_stream_filters_by_year() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    deliveries = [
        {"date": "2024-03-01", "totalNutrientNKg": 100.0, "totalNutrientP2o5Kg": 20.0},
        {"date": "2023-03-01", "totalNutrientNKg": 999.0, "totalNutrientP2o5Kg": 999.0},
    ]
    result = compute_nutrient_stream(deliveries, year=2024)
    assert result["deliveryCount"] == 1
    assert result["totalNutrientNKg"] == pytest.approx(100.0)


@pytest.mark.unit
def test_compute_nutrient_stream_by_month() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    deliveries = [
        {"date": "2024-01-15", "totalNutrientNKg": 100.0, "totalNutrientP2o5Kg": 10.0},
        {"date": "2024-02-10", "totalNutrientNKg": 200.0, "totalNutrientP2o5Kg": 20.0},
    ]
    result = compute_nutrient_stream(deliveries, year=2024)
    assert "2024-01" in result["byMonth"]
    assert "2024-02" in result["byMonth"]
    assert result["byMonth"]["2024-01"]["n_kg"] == pytest.approx(100.0)


@pytest.mark.unit
def test_compute_nutrient_stream_sum() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    deliveries = [
        {"date": "2024-01-01", "totalNutrientNKg": 100.0, "totalNutrientP2o5Kg": 10.0},
        {"date": "2024-01-15", "totalNutrientNKg": 50.0, "totalNutrientP2o5Kg": 5.0},
    ]
    result = compute_nutrient_stream(deliveries, year=2024)
    assert result["totalNutrientNKg"] == pytest.approx(150.0)


# ---------------------------------------------------------------------------
# compliance_service — extract_hazard_export_rows  (pure filter)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_extract_hazard_export_rows_with_psm_line() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    deliveries = [{
        "date": "2024-01-15",
        "number": "DEL-001",
        "supplierName": "Agrar GmbH",
        "lines": [{"bvlZulassungsnummer": "BVL-123", "bezeichnung": "Glyphosat", "menge_to": 5}],
    }]
    rows = extract_hazard_export_rows(deliveries, year=2024)
    assert len(rows) == 1
    assert rows[0]["deliveryNumber"] == "DEL-001"


@pytest.mark.unit
def test_extract_hazard_export_rows_no_psm_lines_empty() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    deliveries = [{
        "date": "2024-01-15",
        "number": "DEL-002",
        "lines": [{"bezeichnung": "Weizen", "menge_to": 1000}],
    }]
    rows = extract_hazard_export_rows(deliveries, year=2024)
    assert rows == []


@pytest.mark.unit
def test_extract_hazard_export_rows_year_filter() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    deliveries = [{
        "date": "2023-06-15",
        "number": "DEL-003",
        "lines": [{"bvlZulassungsnummer": "BVL-456"}],
    }]
    rows = extract_hazard_export_rows(deliveries, year=2024)
    assert rows == []  # 2023 delivery filtered out for year=2024


@pytest.mark.unit
def test_extract_hazard_export_rows_result_fields() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    deliveries = [{
        "date": "2024-01-15",
        "number": "DEL-001",
        "supplierName": "Test Lieferant",
        "lines": [{"bvlZulassungsnummer": "BVL-789"}],
    }]
    rows = extract_hazard_export_rows(deliveries)
    assert len(rows) == 1
    for key in ("deliveryNumber", "deliveryDate", "supplierName", "bvlZulassungsnummer"):
        assert key in rows[0]


# ---------------------------------------------------------------------------
# einkauf_compat_service — cache_key  (pure string building)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_cache_key_basic() -> None:
    from app.services.einkauf_compat_service import cache_key
    key = cache_key("order", "ORD-001", "T001")
    assert "order" in key
    assert "ORD-001" in key
    assert "T001" in key


@pytest.mark.unit
def test_cache_key_single_part() -> None:
    from app.services.einkauf_compat_service import cache_key
    key = cache_key("article")
    assert "article" in key


@pytest.mark.unit
def test_cache_key_prefix_consistent() -> None:
    from app.services.einkauf_compat_service import cache_key
    key = cache_key("order", "ORD-001")
    assert key.startswith("compat:")
