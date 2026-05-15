"""Service for creating FIBU journal entries along the Auftrag → Lieferschein → Rechnung chain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.services.finance_transaction_service import FinanceTransactionService


class SalesPostingService:
    """Creates journal entries at key transitions in the sales document chain.

    Booking logic:
    - Delivery note posted (Warenabgang):
        Debit  7000 Wareneinsatz / Credit 2000 Warenbestand
    - Sales order confirmed (Obligo, optional):
        No GL entry — handled at invoice level.
    """

    # Default accounts (standard SKR03/SKR04 analogues)
    ACCOUNT_COGS = "7000"         # Wareneinsatz / cost of goods sold
    ACCOUNT_INVENTORY = "2000"    # Warenbestand
    ACCOUNT_REVENUE = "8400"      # Umsatzerlöse
    ACCOUNT_RECEIVABLES = "1200"  # Forderungen L+L
    ACCOUNT_TAX = "1776"          # Umsatzsteuer 19%

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self._fin = FinanceTransactionService(db, tenant_id)

    # ── Delivery note posted → Warenabgang ────────────────────────────────────

    def book_warenabgang(
        self,
        delivery_note_id: str,
        delivery_note_number: str,
        positions: list[dict[str, Any]],
        delivery_date: date | str | None = None,
    ) -> None:
        """Book inventory movement when a delivery note is posted.

        Creates: Debit 7000 Wareneinsatz / Credit 2000 Warenbestand
        Skips if no positions or total cost is zero.
        """
        total_cost = Decimal("0.00")
        for pos in positions:
            qty = Decimal(str(pos.get("menge") or pos.get("quantity") or pos.get("qty") or 0))
            cost = Decimal(str(pos.get("einstandspreis") or pos.get("cost_price") or pos.get("unit_price") or 0))
            total_cost += (qty * cost).quantize(Decimal("0.01"))

        if total_cost == Decimal("0.00"):
            return

        entry_date = _coerce_date(delivery_date) or datetime.utcnow().date()
        period = str(entry_date)[:7]

        self._fin.create(
            entry_number=f"WA-{delivery_note_number}",
            description=f"Warenabgang Lieferschein {delivery_note_number}",
            entry_date=entry_date,
            lines=[
                {
                    "account_id": self.ACCOUNT_COGS,
                    "debit_amount": float(total_cost),
                    "credit_amount": 0,
                    "description": "Wareneinsatz",
                },
                {
                    "account_id": self.ACCOUNT_INVENTORY,
                    "debit_amount": 0,
                    "credit_amount": float(total_cost),
                    "description": f"Bestandsabgang {delivery_note_number}",
                },
            ],
            reference=delivery_note_number,
            source="delivery_note",
            document_type="lieferschein",
            period=period,
        )

    # ── Invoice created → Forderung + Umsatz ─────────────────────────────────

    def book_ausgangsrechnung(
        self,
        invoice_number: str,
        invoice_date: date | str | None,
        net_amount: Decimal | float,
        tax_amount: Decimal | float,
        gross_amount: Decimal | float,
    ) -> None:
        """Book AR invoice: Debit 1200 Forderungen / Credit 8400 Umsatz + 1776 USt.

        This mirrors the existing _create_gl_booking_and_op logic but uses
        FinanceTransactionService for consistent GoBD chain stamping.
        Caller is responsible for idempotency (check if already booked).
        """
        net = Decimal(str(net_amount)).quantize(Decimal("0.01"))
        tax = Decimal(str(tax_amount)).quantize(Decimal("0.01"))
        gross = Decimal(str(gross_amount)).quantize(Decimal("0.01"))

        if gross == Decimal("0.00"):
            return

        entry_date = _coerce_date(invoice_date) or datetime.utcnow().date()
        period = str(entry_date)[:7]

        lines = [
            {
                "account_id": self.ACCOUNT_RECEIVABLES,
                "debit_amount": float(gross),
                "credit_amount": 0,
                "description": f"Forderung {invoice_number}",
            },
            {
                "account_id": self.ACCOUNT_REVENUE,
                "debit_amount": 0,
                "credit_amount": float(net),
                "description": "Umsatzerlös",
            },
        ]
        if tax > Decimal("0.00"):
            lines.append(
                {
                    "account_id": self.ACCOUNT_TAX,
                    "debit_amount": 0,
                    "credit_amount": float(tax),
                    "description": "Umsatzsteuer",
                }
            )

        self._fin.create(
            entry_number=f"AR-{invoice_number}",
            description=f"Ausgangsrechnung {invoice_number}",
            entry_date=entry_date,
            lines=lines,
            reference=invoice_number,
            source="sales_invoice",
            document_type="AR_INVOICE",
            period=period,
        )


def _coerce_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except Exception:
        return None
