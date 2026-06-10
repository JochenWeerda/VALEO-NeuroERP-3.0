"""Service for creating FIBU journal entries along the Auftrag → Lieferschein → Rechnung chain."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.core.uuid7 import uuid7
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

    def _ensure_account(
        self,
        account_number: str,
        account_name: str,
        account_type: str,
        category: str,
    ) -> str:
        row = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_erp.chart_of_accounts
                WHERE account_number = :account_number
                LIMIT 1
                """
            ),
            {"account_number": account_number},
        ).first()
        if row:
            return str(row[0])
        account_id = str(uuid7())
        self.db.execute(
            text(
                """
                INSERT INTO domain_erp.chart_of_accounts
                (id, tenant_id, account_number, account_name, account_type, category,
                 is_active, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :account_number, :account_name, :account_type, :category,
                 TRUE, NOW(), NOW())
                """
            ),
            {
                "id": account_id,
                "tenant_id": self.tenant_id,
                "account_number": account_number,
                "account_name": account_name,
                "account_type": account_type,
                "category": category,
            },
        )
        self.db.commit()
        return account_id

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

    def post_ausgangsrechnung_with_op(
        self,
        *,
        invoice_number: str,
        invoice_date: date | str | None,
        customer_id: str,
        net_amount: Decimal | float,
        tax_amount: Decimal | float,
        gross_amount: Decimal | float,
        posted_by: str | None = None,
        due_date: date | str | None = None,
    ) -> dict[str, str]:
        """Create or reuse the posted AR journal entry and debtor open item."""
        net = Decimal(str(net_amount)).quantize(Decimal("0.01"))
        tax = Decimal(str(tax_amount)).quantize(Decimal("0.01"))
        gross = Decimal(str(gross_amount)).quantize(Decimal("0.01"))
        if gross <= Decimal("0.00"):
            raise ValidationFailedError("Sales invoice gross amount must be positive")

        entry_date = _coerce_date(invoice_date) or datetime.utcnow().date()
        effective_due_date = _coerce_date(due_date) or entry_date + timedelta(days=30)
        period = str(entry_date)[:7]
        existing = self.db.execute(
            text(
                """
                SELECT id, status
                FROM domain_erp.journal_entries
                WHERE tenant_id = :tenant_id
                  AND source = 'sales_invoice'
                  AND (document_number = :invoice_number OR reference = :invoice_number)
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id, "invoice_number": invoice_number},
        ).mappings().first()

        if existing:
            journal_entry_id = str(existing["id"])
            status = str(existing.get("status") or "draft")
            if status == "draft":
                self._fin.post(journal_entry_id, posted_by)
            elif status != "posted":
                raise ValidationFailedError(
                    f"Sales invoice journal entry is already {status}"
                )
        else:
            self._ensure_account(
                self.ACCOUNT_RECEIVABLES,
                "Forderungen aus Lieferungen und Leistungen",
                "asset",
                "current_assets",
            )
            self._ensure_account(
                self.ACCOUNT_REVENUE,
                "Umsatzerloese",
                "revenue",
                "sales",
            )
            if tax > Decimal("0.00"):
                self._ensure_account(
                    self.ACCOUNT_TAX,
                    "Umsatzsteuer",
                    "liability",
                    "tax",
                )
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
                    "description": "Umsatzerloes",
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
            journal = self._fin.create(
                entry_number=f"AR-{invoice_number}",
                description=f"Ausgangsrechnung {invoice_number}",
                entry_date=entry_date,
                lines=lines,
                reference=invoice_number,
                source="sales_invoice",
                document_type="AR_INVOICE",
                period=period,
            )
            journal_entry_id = str(journal.id)
            self._fin.post(journal_entry_id, posted_by)

        customer_name_row = self.db.execute(
            text(
                """
                SELECT COALESCE(company_name, customer_number, id)
                FROM domain_crm.customers
                WHERE tenant_id = :tenant_id AND id = :customer_id
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id, "customer_id": customer_id},
        ).first()
        customer_name = (
            str(customer_name_row[0]) if customer_name_row and customer_name_row[0] else customer_id
        )
        existing_op = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_erp.offene_posten
                WHERE tenant_id = :tenant_id
                  AND rechnungsnr = :invoice_number
                  AND konto_typ = 'debitoren'
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id, "invoice_number": invoice_number},
        ).first()
        open_item_id = str(existing_op[0]) if existing_op else str(uuid7())
        if existing_op:
            self.db.execute(
                text(
                    """
                    UPDATE domain_erp.offene_posten
                    SET datum = :invoice_date,
                        rechnungsdatum = :invoice_date,
                        faelligkeit = :due_date,
                        due_date = :due_date,
                        kunde_id = :customer_id,
                        kunde_name = :customer_name,
                        betrag = :amount,
                        open_amount = :amount,
                        offen = :amount,
                        op_status = 'offen',
                        updated_at = NOW()
                    WHERE tenant_id = :tenant_id AND id = :id
                    """
                ),
                {
                    "id": open_item_id,
                    "tenant_id": self.tenant_id,
                    "invoice_date": entry_date,
                    "due_date": effective_due_date,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "amount": gross,
                },
            )
        else:
            self.db.execute(
                text(
                    """
                    INSERT INTO domain_erp.offene_posten
                    (id, tenant_id, rechnungsnr, datum, rechnungsdatum, faelligkeit, due_date,
                     konto_typ, kunde_id, kunde_name, waehrung, betrag, open_amount, offen,
                     op_status, zahlbar, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :invoice_number, :invoice_date, :invoice_date, :due_date, :due_date,
                     'debitoren', :customer_id, :customer_name, 'EUR', :amount, :amount, :amount,
                     'offen', TRUE, NOW(), NOW())
                    """
                ),
                {
                    "id": open_item_id,
                    "tenant_id": self.tenant_id,
                    "invoice_number": invoice_number,
                    "invoice_date": entry_date,
                    "due_date": effective_due_date,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "amount": gross,
                },
            )
        self.db.commit()
        return {
            "journal_entry_id": journal_entry_id,
            "open_item_id": open_item_id,
        }

    def reverse_ausgangsrechnung(
        self,
        *,
        invoice_number: str,
        reason: str,
    ) -> dict[str, str]:
        row = self.db.execute(
            text(
                """
                SELECT id, status
                FROM domain_erp.journal_entries
                WHERE tenant_id = :tenant_id
                  AND source = 'sales_invoice'
                  AND (document_number = :invoice_number OR reference = :invoice_number)
                LIMIT 1
                """
            ),
            {"tenant_id": self.tenant_id, "invoice_number": invoice_number},
        ).mappings().first()
        if not row:
            raise ValidationFailedError(
                f"No journal entry found for sales invoice {invoice_number}"
            )
        if str(row.get("status")) != "posted":
            raise ValidationFailedError(
                f"Sales invoice journal entry is already {row.get('status')}"
            )
        original, reversal = self._fin.reverse(str(row["id"]), reason=reason)
        self.db.execute(
            text(
                """
                UPDATE domain_erp.offene_posten
                SET op_status = 'storniert',
                    open_amount = 0,
                    offen = 0,
                    updated_at = NOW()
                WHERE tenant_id = :tenant_id
                  AND rechnungsnr = :invoice_number
                  AND konto_typ = 'debitoren'
                """
            ),
            {"tenant_id": self.tenant_id, "invoice_number": invoice_number},
        )
        self.db.commit()
        return {
            "journal_entry_id": str(original.id),
            "reversal_entry_id": str(reversal.id),
        }


def _coerce_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except Exception:
        return None
