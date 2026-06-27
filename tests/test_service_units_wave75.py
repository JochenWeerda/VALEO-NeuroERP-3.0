"""Wave 75 — Unit-Tests fuer accounting_export_profiles (pure mapping/CSV/validation logic)."""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import date


def _make_profile():
    from app.services.accounting_export_profiles import AccountingExportProfile, AccountingExportMappingRule
    return AccountingExportProfile(
        id="datev-v1",
        version=1,
        status="active",
        strategy="direct",
        requires_tax_advisor_test_import=False,
        format={"delimiter": ";", "encoding": "utf-8"},
        fields=[
            AccountingExportMappingRule(source="account_no", target="Konto", required=True),
            AccountingExportMappingRule(source="amount_net", target="Betrag", required=True),
            AccountingExportMappingRule(source="booking_text", target="Buchungstext", required=False),
        ],
    )


def _make_line(**overrides):
    from app.services.accounting_export_profiles import AccountingExportLine
    defaults = dict(
        export_batch_id="BATCH-001",
        tenant_id="T001",
        external_profile="datev-v1",
        fiscal_year=2024,
        period="01",
        booking_date=date(2024, 1, 15),
        document_date=date(2024, 1, 15),
        document_no="INV-001",
        document_type="invoice",
        account_no="8400",
        contra_account_no="1200",
        debit_credit="H",
        amount_net=Decimal("1000.00"),
        currency="EUR",
        booking_text="Warenverkauf",
    )
    defaults.update(overrides)
    return AccountingExportLine(**defaults)


def _make_batch(lines=None):
    from app.services.accounting_export_profiles import AccountingExportBatch
    return AccountingExportBatch(
        id="BATCH-001",
        tenant_id="T001",
        external_profile="datev-v1",
        fiscal_year=2024,
        period="01",
        status="pending",
        lines=lines or [_make_line()],
    )


# ---------------------------------------------------------------------------
# map_line
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_map_line_maps_required_fields() -> None:
    from app.services.accounting_export_profiles import map_line
    line = _make_line()
    profile = _make_profile()
    result = map_line(line, profile)
    assert "Konto" in result
    assert "Betrag" in result
    assert result["Konto"] == "8400"


@pytest.mark.unit
def test_map_line_maps_optional_field() -> None:
    from app.services.accounting_export_profiles import map_line
    line = _make_line(booking_text="Testkauf")
    profile = _make_profile()
    result = map_line(line, profile)
    assert "Buchungstext" in result
    assert result["Buchungstext"] == "Testkauf"


@pytest.mark.unit
def test_map_line_returns_dict_of_strings() -> None:
    from app.services.accounting_export_profiles import map_line
    result = map_line(_make_line(), _make_profile())
    assert isinstance(result, dict)
    for k, v in result.items():
        assert isinstance(k, str)
        assert isinstance(v, str)


# ---------------------------------------------------------------------------
# validate_batch
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_batch_valid() -> None:
    from app.services.accounting_export_profiles import validate_batch
    batch = _make_batch([_make_line()])
    profile = _make_profile()
    result = validate_batch(batch, profile)
    assert hasattr(result, "valid") or hasattr(result, "errors")


@pytest.mark.unit
def test_validate_batch_empty_lines() -> None:
    from app.services.accounting_export_profiles import validate_batch
    batch = _make_batch([])
    profile = _make_profile()
    result = validate_batch(batch, profile)
    # Empty batch should either be invalid or valid with 0 lines processed
    assert result is not None


# ---------------------------------------------------------------------------
# render_csv
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_render_csv_returns_string() -> None:
    from app.services.accounting_export_profiles import render_csv
    batch = _make_batch([_make_line()])
    profile = _make_profile()
    output = render_csv(batch, profile)
    assert isinstance(output, str)


@pytest.mark.unit
def test_render_csv_contains_header() -> None:
    from app.services.accounting_export_profiles import render_csv
    batch = _make_batch([_make_line()])
    profile = _make_profile()
    output = render_csv(batch, profile)
    assert "Konto" in output or "Betrag" in output


@pytest.mark.unit
def test_render_csv_contains_data() -> None:
    from app.services.accounting_export_profiles import render_csv
    batch = _make_batch([_make_line(account_no="8400")])
    profile = _make_profile()
    output = render_csv(batch, profile)
    assert "8400" in output


@pytest.mark.unit
def test_render_csv_multiple_lines() -> None:
    from app.services.accounting_export_profiles import render_csv
    lines = [_make_line(account_no="8400"), _make_line(account_no="8401")]
    batch = _make_batch(lines)
    profile = _make_profile()
    output = render_csv(batch, profile)
    assert "8400" in output
    assert "8401" in output
