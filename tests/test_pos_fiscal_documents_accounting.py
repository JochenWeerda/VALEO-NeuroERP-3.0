from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import pdfplumber

from app.services.pos_accounting_service import PosClosingAmounts, build_pos_closing_lines
from app.services.pos_fiscal_document_service import (
    FiscalClosingDocument,
    FiscalReceiptDocument,
    MockTseCertificate,
    VirtualPdfPrinter,
)


def _mock_certificate() -> MockTseCertificate:
    return MockTseCertificate(
        serial_number="MOCK-TSE-DE-0004711",
        issuer="VALEO Test Trust Center",
        fingerprint_sha256="AA:11:BB:22:CC:33:DD:44",
        valid_from=date(2026, 1, 1),
        valid_until=date(2030, 12, 31),
    )


def _pdf_text(path) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def test_fiscal_receipt_is_printed_as_complete_pdf_with_mock_certificate(tmp_path):
    receipt = FiscalReceiptDocument(
        receipt_number="BON-2026-0001",
        transaction_number="TSE-TX-4711",
        started_at=datetime(2026, 6, 10, 8, 15, tzinfo=timezone.utc),
        finished_at=datetime(2026, 6, 10, 8, 16, tzinfo=timezone.utc),
        signature_counter=17,
        signature="MOCK-SIGNATURE-ABC123",
        qr_code_data="V0;BON-2026-0001;TSE-TX-4711;17",
        gross_total=Decimal("357.00"),
        payments=(("BAR", Decimal("119.00")), ("EC/KARTE", Decimal("238.00"))),
        lines=(
            ("Duenger", Decimal("1"), Decimal("119.00")),
            ("Saatgut", Decimal("2"), Decimal("119.00")),
        ),
        certificate=_mock_certificate(),
    )

    output = VirtualPdfPrinter(tmp_path).print_receipt(receipt, "kassenbon.pdf")

    assert output.read_bytes().startswith(b"%PDF-")
    text = _pdf_text(output)
    for expected in (
        "KASSENBON / TSE-BELEG",
        "BON-2026-0001",
        "TSE-TX-4711",
        "Signaturzaehler: 17",
        "Brutto gesamt: 357.00 EUR",
        "BAR: 119.00 EUR",
        "EC/KARTE: 238.00 EUR",
        "MOCK-TSE-DE-0004711",
        "AA:11:BB:22:CC:33:DD:44",
        "MOCK - NICHT PRODUKTIV",
    ):
        assert expected in text


def test_closing_pdf_and_accounting_cover_all_requested_pos_transactions(tmp_path):
    amounts = PosClosingAmounts(
        cash_sales=Decimal("119.00"),
        card_sales=Decimal("238.00"),
        voucher_redemptions=Decimal("50.00"),
        voucher_issues=Decimal("100.00"),
        cash_withdrawals=Decimal("80.00"),
    )
    lines = build_pos_closing_lines(amounts)

    debit = sum(line.debit for line in lines)
    credit = sum(line.credit for line in lines)
    assert amounts.sales_total == Decimal("407.00")
    assert debit == credit == Decimal("587.00")
    assert {(line.account_number, line.debit, line.credit) for line in lines} == {
        ("1000", Decimal("219.00"), Decimal("0.00")),
        ("1200", Decimal("238.00"), Decimal("0.00")),
        ("1600", Decimal("50.00"), Decimal("0.00")),
        ("8400", Decimal("0.00"), Decimal("407.00")),
        ("1600", Decimal("0.00"), Decimal("100.00")),
        ("1800", Decimal("80.00"), Decimal("0.00")),
        ("1000", Decimal("0.00"), Decimal("80.00")),
    }

    closing = FiscalClosingDocument(
        closing_number="KA-2026-06-10",
        business_date=date(2026, 6, 10),
        transaction_count=5,
        gross_total=amounts.sales_total,
        payments=(
            ("BAR", amounts.cash_sales),
            ("EC/KARTE", amounts.card_sales),
            ("GUTSCHEIN", amounts.voucher_redemptions),
        ),
        cash_withdrawals=amounts.cash_withdrawals,
        voucher_issues=amounts.voucher_issues,
        voucher_redemptions=amounts.voucher_redemptions,
        journal_entry_number="KA-2026-06-10",
        accounting_lines=tuple(lines),
        certificate=_mock_certificate(),
    )

    output = VirtualPdfPrinter(tmp_path).print_closing(closing, "tagesabschluss.pdf")

    assert output.read_bytes().startswith(b"%PDF-")
    text = _pdf_text(output)
    for expected in (
        "KASSEN-TAGESABSCHLUSS / TSE-NACHWEIS",
        "KA-2026-06-10",
        "Brutto gesamt: 407.00 EUR",
        "Barentnahmen: 80.00 EUR",
        "Gutscheinausgaben: 100.00 EUR",
        "Gutscheinannahmen: 50.00 EUR",
        "1000 Kasseneinnahmen Bar: Soll 219.00 EUR",
        "1200 EC- und Kartenzahlungen: Soll 238.00 EUR",
        "1600 Ausgegebene Gutscheine: Soll 0.00 EUR / Haben 100.00 EUR",
        "8400 Umsatzerloese POS: Soll 0.00 EUR / Haben 407.00 EUR",
        "MOCK-TSE-DE-0004711",
    ):
        assert expected in text


def test_virtual_pdf_printer_rejects_non_pdf_jobs(tmp_path):
    printer = VirtualPdfPrinter(tmp_path)

    try:
        printer._print("kassenbon.txt", b"not-a-pdf")
    except ValueError as exc:
        assert "nur .pdf" in str(exc)
    else:
        raise AssertionError("Nicht-PDF-Druckauftrag wurde akzeptiert")
