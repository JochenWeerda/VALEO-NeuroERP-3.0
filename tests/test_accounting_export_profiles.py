from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.services.accounting_export_profiles import (
    AccountingExportBatch,
    AccountingExportLine,
    load_profile,
    render_csv,
    validate_batch,
)


def _line(profile: str, side: str = "S", amount: str = "100.00", **overrides):
    data = {
        "export_batch_id": "draft",
        "tenant_id": "tenant-1",
        "external_profile": profile,
        "fiscal_year": 2026,
        "period": "2026-06",
        "booking_date": date(2026, 6, 30),
        "document_date": date(2026, 6, 30),
        "document_no": "LOHN-2026-06",
        "document_type": "Lohn",
        "account_no": "6000",
        "contra_account_no": "1740",
        "debit_credit": side,
        "amount_net": Decimal(amount),
        "amount_gross": Decimal(amount),
        "tax_amount": Decimal("0.00"),
        "tax_key": "0",
        "currency": "EUR",
        "booking_text": "Payroll Juni 2026",
        "customer_vendor_no": "PN-1",
        "cost_center_1": "HR",
        "cost_center_2": "ADMIN",
        "profit_center": "PERS",
        "archive_id": "ARCH-1",
        "document_link": "dms://ARCH-1",
    }
    data.update(overrides)
    return AccountingExportLine(**data)


def _batch(profile: str, *lines: AccountingExportLine) -> AccountingExportBatch:
    return AccountingExportBatch.create(
        tenant_id="tenant-1",
        external_profile=profile,
        fiscal_year=2026,
        period="2026-06",
        lines=lines or [_line(profile, "S"), _line(profile, "H")],
    )


def test_datev_profile_maps_kost1_kost2_and_checksum():
    profile = load_profile("datev_accounting_csv")
    csv_body = render_csv(_batch(profile.id), profile)

    assert "KOST1;KOST2" in csv_body
    assert "HR;ADMIN" in csv_body
    assert "checksum" in csv_body


def test_agenda_profile_is_datev_compatible_fallback_and_not_certified():
    profile = load_profile("agenda_datev_compatible_csv")
    validation = validate_batch(_batch(profile.id), profile)

    assert profile.strategy == "datev_compatible_first"
    assert profile.status == "not_certified"
    assert profile.requires_tax_advisor_test_import is True
    assert validation.exportable is True


def test_addison_profile_validates_required_fields():
    profile = load_profile("addison_datev_compatible_csv")
    bad_batch = _batch(profile.id, _line(profile.id, "S", account_no=""), _line(profile.id, "H"))
    validation = validate_batch(bad_batch, profile)

    assert validation.exportable is False
    assert any("ACCOUNT_REQUIRED" in error for error in validation.errors)


def test_simba_profile_maps_person_account_and_cost_fields():
    profile = load_profile("simba_datev_compatible_csv")
    csv_body = render_csv(_batch(profile.id), profile)

    assert "DebitorKreditor" in csv_body
    assert "PN-1" in csv_body
    assert "HR;ADMIN" in csv_body


def test_lexware_profile_renders_simple_csv_output():
    profile = load_profile("lexware_datev_csv")
    csv_body = render_csv(_batch(profile.id), profile)

    assert csv_body.startswith("Belegnummer;Belegdatum;Buchungsdatum")
    assert "100,00" in csv_body


def test_sage_profile_exposes_accounting_and_payroll_subprofiles():
    profile = load_profile("sage_datev_csv")

    assert {"sage_50_datev_csv", "sage_100_datev_csv", "sage_hr_payroll_pre_export"} <= set(profile.subprofiles)
    assert profile.requires_tax_advisor_test_import is True


def test_sbs_wk_profile_is_not_certified_and_requires_test_import():
    profile = load_profile("sbs_wolterskluwer_datev_csv")

    assert profile.status == "not_certified"
    assert profile.requires_tax_advisor_test_import is True


def test_batch_not_exportable_with_missing_account_contra_amount_or_date():
    profile = load_profile("datev_accounting_csv")
    bad = AccountingExportBatch.create(
        tenant_id="tenant-1",
        external_profile=profile.id,
        fiscal_year=2026,
        period="2026-06",
        lines=[
            _line(profile.id, "S", "0.00", account_no="", booking_date=None),
            _line(profile.id, "H", "0.00", contra_account_no="", document_date=None),
        ],
    )
    validation = validate_batch(bad, profile)

    assert validation.exportable is False
    assert any("ACCOUNT_REQUIRED" in error for error in validation.errors)
    assert any("CONTRA_ACCOUNT_REQUIRED" in error for error in validation.errors)
    assert any("NON_ZERO_AMOUNT_REQUIRED" in error for error in validation.errors)
    assert any("DATE_REQUIRED" in error for error in validation.errors)


def test_correction_export_creates_new_version_without_overwriting_old_batch():
    original = _batch("datev_accounting_csv").transition("exported")
    correction = original.correction([_line("datev_accounting_csv", "S", "50.00"), _line("datev_accounting_csv", "H", "50.00")])

    assert correction.id != original.id
    assert correction.version == 2
    assert correction.correction_of_export_id == original.id
    with pytest.raises(ValueError):
        original.transition("validated")
