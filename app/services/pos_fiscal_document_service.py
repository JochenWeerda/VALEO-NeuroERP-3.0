from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from app.services.pos_accounting_service import PosAccountingLine


@dataclass(frozen=True)
class MockTseCertificate:
    serial_number: str
    issuer: str
    fingerprint_sha256: str
    valid_from: date
    valid_until: date
    signature_algorithm: str = "ecdsa-plain-SHA256"
    public_key_id: str = "VALEO-TSE-MOCK-KEY-01"


@dataclass(frozen=True)
class FiscalReceiptDocument:
    receipt_number: str
    transaction_number: str
    started_at: datetime
    finished_at: datetime
    signature_counter: int
    signature: str
    qr_code_data: str
    gross_total: Decimal
    payments: tuple[tuple[str, Decimal], ...]
    lines: tuple[tuple[str, Decimal, Decimal], ...]
    certificate: MockTseCertificate


@dataclass(frozen=True)
class FiscalClosingDocument:
    closing_number: str
    business_date: date
    transaction_count: int
    gross_total: Decimal
    payments: tuple[tuple[str, Decimal], ...]
    cash_withdrawals: Decimal
    voucher_issues: Decimal
    voucher_redemptions: Decimal
    journal_entry_number: str
    accounting_lines: tuple[PosAccountingLine, ...]
    certificate: MockTseCertificate


@dataclass(frozen=True)
class VirtualPdfPrinter:
    """Deterministic PDF printer used for automated fiscal document acceptance."""

    output_directory: Path

    def _print(self, filename: str, payload: bytes) -> Path:
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Der virtuelle PDF-Drucker akzeptiert nur .pdf-Ziele")
        if not payload.startswith(b"%PDF-"):
            raise ValueError("Der Druckauftrag enthaelt kein gueltiges PDF-Dokument")
        self.output_directory.mkdir(parents=True, exist_ok=True)
        target = self.output_directory / filename
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        temporary.write_bytes(payload)
        temporary.replace(target)
        return target

    def print_receipt(self, document: FiscalReceiptDocument, filename: str) -> Path:
        return self._print(filename, print_fiscal_receipt_pdf(document))

    def print_closing(self, document: FiscalClosingDocument, filename: str) -> Path:
        return self._print(filename, print_fiscal_closing_pdf(document))


def _render_pdf(title: str, rows: Iterable[str]) -> bytes:
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4, pageCompression=0)
    width, height = A4
    y = height - 42
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(42, y, title)
    y -= 26
    canvas.setFont("Helvetica", 9)
    for raw_row in rows:
        row = str(raw_row)
        while stringWidth(row, "Helvetica", 9) > width - 84 and len(row) > 1:
            split_at = min(95, len(row))
            while split_at > 1 and stringWidth(row[:split_at], "Helvetica", 9) > width - 84:
                split_at -= 1
            canvas.drawString(42, y, row[:split_at])
            y -= 13
            row = row[split_at:]
        canvas.drawString(42, y, row)
        y -= 13
        if y < 42:
            canvas.showPage()
            canvas.setFont("Helvetica", 9)
            y = height - 42
    canvas.save()
    return buffer.getvalue()


def _certificate_rows(certificate: MockTseCertificate) -> list[str]:
    return [
        "TSE-Zertifikat (MOCK - NICHT PRODUKTIV)",
        f"Seriennummer: {certificate.serial_number}",
        f"Aussteller: {certificate.issuer}",
        f"Fingerprint SHA-256: {certificate.fingerprint_sha256}",
        f"Gueltig: {certificate.valid_from.isoformat()} bis {certificate.valid_until.isoformat()}",
        f"Signaturalgorithmus: {certificate.signature_algorithm}",
        f"Public-Key-ID: {certificate.public_key_id}",
    ]


def print_fiscal_receipt_pdf(document: FiscalReceiptDocument) -> bytes:
    rows = [
        f"Belegnummer: {document.receipt_number}",
        f"Transaktionsnummer: {document.transaction_number}",
        f"Start: {document.started_at.isoformat()}",
        f"Ende: {document.finished_at.isoformat()}",
        f"Signaturzaehler: {document.signature_counter}",
        f"Signatur: {document.signature}",
        f"QR-Daten: {document.qr_code_data}",
        "",
        "Positionen",
    ]
    rows.extend(
        f"{label}: {quantity} x {unit_price:.2f} EUR"
        for label, quantity, unit_price in document.lines
    )
    rows.extend(["", f"Brutto gesamt: {document.gross_total:.2f} EUR", "Zahlungen"])
    rows.extend(f"{method}: {amount:.2f} EUR" for method, amount in document.payments)
    rows.extend(["", *_certificate_rows(document.certificate)])
    return _render_pdf("KASSENBON / TSE-BELEG", rows)


def print_fiscal_closing_pdf(document: FiscalClosingDocument) -> bytes:
    rows = [
        f"Abschlussnummer: {document.closing_number}",
        f"Geschaeftstag: {document.business_date.isoformat()}",
        f"Transaktionen: {document.transaction_count}",
        f"Brutto gesamt: {document.gross_total:.2f} EUR",
        f"Barentnahmen: {document.cash_withdrawals:.2f} EUR",
        f"Gutscheinausgaben: {document.voucher_issues:.2f} EUR",
        f"Gutscheinannahmen: {document.voucher_redemptions:.2f} EUR",
        f"FiBu-Belegnummer: {document.journal_entry_number}",
        "",
        "Zahlungsarten",
    ]
    rows.extend(f"{method}: {amount:.2f} EUR" for method, amount in document.payments)
    rows.extend(["", "FiBu-Buchungszeilen"])
    rows.extend(
        (
            f"{line.account_number} {line.description}: "
            f"Soll {line.debit:.2f} EUR / Haben {line.credit:.2f} EUR"
        )
        for line in document.accounting_lines
    )
    rows.extend(["", *_certificate_rows(document.certificate)])
    return _render_pdf("KASSEN-TAGESABSCHLUSS / TSE-NACHWEIS", rows)
