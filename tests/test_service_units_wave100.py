"""Wave 100 — Unit-Tests fuer compliance_service, articles_service,
action_execution_mutations (pure domain functions)."""

from __future__ import annotations

import pytest
from datetime import datetime
from types import SimpleNamespace


# ---------------------------------------------------------------------------
# compliance_service — dt, build_lot_trace_report, compute_nutrient_stream,
#                      extract_hazard_export_rows
# ---------------------------------------------------------------------------

def _fake_lot(**kwargs):
    defaults = dict(
        chargen_id="CH-WAVE100", id="CH-WAVE100", artikel_id="ART-001",
        artikel="Weizen", menge=1000, eingang=datetime(2024, 1, 1),
        herkunft="DE", lagerort="Silo-1", qualitaetsstatus="freigegeben",
        status="aktiv", updated_at=datetime(2024, 1, 1),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.mark.unit
def test_dt_none_returns_none() -> None:
    from app.services.compliance_service import dt
    assert dt(None) is None


@pytest.mark.unit
def test_dt_datetime_returns_string() -> None:
    from app.services.compliance_service import dt
    result = dt(datetime(2024, 1, 15, 10, 30))
    assert isinstance(result, str)
    assert "2024-01-15" in result


@pytest.mark.unit
def test_build_lot_trace_report_returns_dict() -> None:
    from app.services.compliance_service import build_lot_trace_report
    result = build_lot_trace_report(_fake_lot(), [])
    assert isinstance(result, dict)


@pytest.mark.unit
def test_build_lot_trace_report_has_required_keys() -> None:
    from app.services.compliance_service import build_lot_trace_report
    result = build_lot_trace_report(_fake_lot(), [])
    for key in ("lot", "events", "linkedDeliveries", "deliveryCount"):
        assert key in result


@pytest.mark.unit
def test_build_lot_trace_report_delivery_count_zero() -> None:
    from app.services.compliance_service import build_lot_trace_report
    result = build_lot_trace_report(_fake_lot(), [])
    assert result["deliveryCount"] == 0


@pytest.mark.unit
def test_compute_nutrient_stream_empty_deliveries() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    result = compute_nutrient_stream([], 2024)
    assert isinstance(result, dict)
    assert result["year"] == 2024
    assert result["deliveryCount"] == 0


@pytest.mark.unit
def test_compute_nutrient_stream_with_psm_delivery() -> None:
    from app.services.compliance_service import compute_nutrient_stream
    deliveries = [{"ware": "psm", "article_name": "Roundup", "menge_kg": 50, "flaeche_ha": 10, "datum": "2024-05-01"}]
    result = compute_nutrient_stream(deliveries, 2024)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_extract_hazard_export_rows_empty_returns_empty_list() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    result = extract_hazard_export_rows([], 2024)
    assert result == []


@pytest.mark.unit
def test_extract_hazard_export_rows_with_psm_delivery() -> None:
    from app.services.compliance_service import extract_hazard_export_rows
    deliveries = [{"ware": "psm", "article_name": "Roundup", "menge_kg": 50, "datum": "2024-05-01"}]
    result = extract_hazard_export_rows(deliveries, 2024)
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# articles_service — build_article_dq_datensatz, resolve_article_tenant
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_article_dq_datensatz_returns_dict() -> None:
    from app.services.articles_service import build_article_dq_datensatz
    result = build_article_dq_datensatz({"artikel_nr": "A001", "name": "Mais", "einheit": "kg"})
    assert isinstance(result, dict)


@pytest.mark.unit
def test_build_article_dq_datensatz_has_artikel_nr() -> None:
    from app.services.articles_service import build_article_dq_datensatz
    result = build_article_dq_datensatz({"artikel_nr": "A001", "name": "Mais", "einheit": "kg"})
    assert "artikel_nr" in result


@pytest.mark.unit
def test_build_article_dq_datensatz_has_bezeichnung() -> None:
    from app.services.articles_service import build_article_dq_datensatz
    result = build_article_dq_datensatz({"artikel_nr": "A001", "name": "Mais", "einheit": "kg"})
    assert "bezeichnung" in result


@pytest.mark.unit
def test_resolve_article_tenant_same_tenant() -> None:
    from app.services.articles_service import resolve_article_tenant
    result = resolve_article_tenant("tenant-A", "tenant-A")
    assert result == "tenant-A"


@pytest.mark.unit
def test_resolve_article_tenant_none_payload_uses_header() -> None:
    from app.services.articles_service import resolve_article_tenant
    result = resolve_article_tenant(None, "header-tenant")
    assert result == "header-tenant"


@pytest.mark.unit
def test_resolve_article_tenant_mismatch_raises() -> None:
    from app.services.articles_service import resolve_article_tenant
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        resolve_article_tenant("tenant-A", "tenant-B")
    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# action_execution_mutations — register_domain_mutation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_register_domain_mutation_returns_none() -> None:
    from app.services.action_execution_mutations import register_domain_mutation

    async def my_handler(payload):
        return {"ok": True}

    result = register_domain_mutation("wave100_test_command", my_handler)
    assert result is None


@pytest.mark.unit
def test_register_domain_mutation_accepts_callable() -> None:
    from app.services.action_execution_mutations import register_domain_mutation

    called = []

    async def handler(payload):
        called.append(payload)

    register_domain_mutation("wave100_test_command2", handler)
    # Registration itself should not crash
    assert True
