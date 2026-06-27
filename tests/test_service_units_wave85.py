"""Wave 85 — Unit-Tests fuer accounting_export_profiles, agrar_contract_service,
atlas_customs_service (pure domain functions)."""

from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_datev_profile():
    from app.services.accounting_export_profiles import load_profile
    return load_profile("datev_accounting_csv")


def _make_export_line(debit_credit="S", amount=Decimal("1500")):
    from app.services.accounting_export_profiles import AccountingExportLine
    return AccountingExportLine(
        export_batch_id="BATCH-001",
        tenant_id="T001",
        external_profile="datev_accounting_csv",
        fiscal_year=2024,
        period="2024-01",
        booking_date=date(2024, 1, 15),
        document_date=date(2024, 1, 15),
        document_no="RE-001",
        document_type="RE",
        account_no="1400",
        contra_account_no="8400",
        debit_credit=debit_credit,
        amount_net=Decimal(str(amount)),
        currency="EUR",
        booking_text="Warenlieferung Weizen",
        amount_gross=Decimal(str(amount)),
    )


def _make_balanced_batch():
    from app.services.accounting_export_profiles import AccountingExportBatch
    return AccountingExportBatch(
        id="BATCH-001",
        tenant_id="T001",
        external_profile="datev_accounting_csv",
        fiscal_year=2024,
        period="2024-01",
        status="ready",
        lines=[_make_export_line("S", Decimal("1500")), _make_export_line("H", Decimal("1500"))],
    )


# ---------------------------------------------------------------------------
# accounting_export_profiles — load_profile, map_line, validate_batch, render_csv
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_load_profile_datev_returns_profile() -> None:
    from app.services.accounting_export_profiles import AccountingExportProfile
    profile = _load_datev_profile()
    assert isinstance(profile, AccountingExportProfile)
    assert profile.id == "datev_accounting_csv"


@pytest.mark.unit
def test_load_profile_has_fields() -> None:
    profile = _load_datev_profile()
    assert len(profile.fields) > 0


@pytest.mark.unit
def test_load_profile_unknown_raises_file_not_found() -> None:
    from app.services.accounting_export_profiles import load_profile
    with pytest.raises(FileNotFoundError):
        load_profile("nonexistent_profile_xyz")


@pytest.mark.unit
def test_map_line_returns_dict() -> None:
    from app.services.accounting_export_profiles import map_line
    profile = _load_datev_profile()
    line = _make_export_line()
    mapped = map_line(line, profile)
    assert isinstance(mapped, dict)
    assert len(mapped) > 0


@pytest.mark.unit
def test_map_line_contains_amount() -> None:
    from app.services.accounting_export_profiles import map_line
    profile = _load_datev_profile()
    line = _make_export_line("S", Decimal("9999"))
    mapped = map_line(line, profile)
    # Amount should appear in some column
    all_values = " ".join(str(v) for v in mapped.values())
    assert "9999" in all_values


@pytest.mark.unit
def test_validate_batch_balanced_exportable() -> None:
    from app.services.accounting_export_profiles import validate_batch
    profile = _load_datev_profile()
    batch = _make_balanced_batch()
    result = validate_batch(batch, profile)
    assert result.exportable is True
    assert result.errors == []


@pytest.mark.unit
def test_validate_batch_profile_mismatch_error() -> None:
    from app.services.accounting_export_profiles import validate_batch, AccountingExportBatch
    profile = _load_datev_profile()
    batch = AccountingExportBatch(
        id="B2", tenant_id="T001", external_profile="wrong_profile",
        fiscal_year=2024, period="2024-01", status="ready", lines=[],
    )
    result = validate_batch(batch, profile)
    assert "PROFILE_MISMATCH" in result.errors


@pytest.mark.unit
def test_render_csv_balanced_batch_has_header() -> None:
    from app.services.accounting_export_profiles import render_csv
    profile = _load_datev_profile()
    batch = _make_balanced_batch()
    csv_out = render_csv(batch, profile)
    first_line = csv_out.split("\n")[0]
    # Header row should contain column names
    assert ";" in first_line


@pytest.mark.unit
def test_render_csv_balanced_batch_has_data_rows() -> None:
    from app.services.accounting_export_profiles import render_csv
    profile = _load_datev_profile()
    batch = _make_balanced_batch()
    csv_out = render_csv(batch, profile)
    lines = [l for l in csv_out.strip().split("\n") if l]
    assert len(lines) >= 3  # header + 2 data rows


# ---------------------------------------------------------------------------
# agrar_contract_service — evaluate_contract_datensatz, build_dq_error_detail
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_evaluate_contract_datensatz_valid() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({"kontrakt_nr": "K-001", "lieferant_nr": "L-001", "ware": "WW"})
    assert result.bestanden is True
    assert result.fehler_anzahl == 0


@pytest.mark.unit
def test_evaluate_contract_datensatz_empty_fails() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({})
    assert result.bestanden is False
    assert result.fehler_anzahl > 0


@pytest.mark.unit
def test_evaluate_contract_datensatz_missing_ware() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({"kontrakt_nr": "K-001", "lieferant_nr": "L-001"})
    felder = [v.feld for v in result.verletzungen]
    assert "ware" in felder


@pytest.mark.unit
def test_evaluate_contract_has_ruleset_id() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz
    result = evaluate_contract_datensatz({})
    assert result.ruleset_id is not None


@pytest.mark.unit
def test_build_dq_error_detail_contract() -> None:
    from app.services.agrar_contract_service import evaluate_contract_datensatz, build_dq_error_detail
    result = evaluate_contract_datensatz({})
    detail = build_dq_error_detail("Kontrakt", result)
    assert detail["entity_typ"] == "Kontrakt"
    assert detail["fehler_anzahl"] == result.fehler_anzahl
    assert "verletzungen" in detail


# ---------------------------------------------------------------------------
# atlas_customs_service — validate_hs_code  (pure validation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_hs_code_valid_8_digits() -> None:
    from app.services.atlas_customs_service import validate_hs_code
    errors = validate_hs_code("10011900")
    assert errors == []


@pytest.mark.unit
def test_validate_hs_code_too_short() -> None:
    from app.services.atlas_customs_service import validate_hs_code
    errors = validate_hs_code("1234")
    assert len(errors) > 0
    assert any("8 Stellen" in e for e in errors)


@pytest.mark.unit
def test_validate_hs_code_non_numeric() -> None:
    from app.services.atlas_customs_service import validate_hs_code
    errors = validate_hs_code("ABCDEFGH")
    assert len(errors) > 0
    assert any("Ziffern" in e for e in errors)


@pytest.mark.unit
def test_validate_hs_code_empty_string() -> None:
    from app.services.atlas_customs_service import validate_hs_code
    errors = validate_hs_code("")
    assert len(errors) > 0
