"""
Kernel PostAPInvoice: gleiche Fachlogik wie POST /ap/invoices/{id}/post, aber ohne
Repository-create mit Zwischen-commit — alles in einer Session (add/flush), Commit
erfolgt in apply_accepted_action_mutations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.fibu_audit import log_fibu_audit
from app.core.uuid7 import uuid7
from app.documents.router_helpers import get_from_store, get_repository
from app.domains.shared.process_events import APInvoicePosted
from app.finance.tax_resolver import resolve_partner_country, resolve_tax_key_accounts
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.infrastructure.models.journal import JournalEntry, JournalEntryLine

logger = logging.getLogger(__name__)


def post_ap_invoice_kernel_sync(
    db: Session,
    *,
    invoice_id: str,
    tenant_id: str,
    posted_by: str,
) -> None:
    """
    Bucht AP-Rechnung: Journal (domain_erp), OP, documents-Update, Outbox.
    Idempotent bei bereits VERBUCHT mit journalEntryId.
    """
    repo = get_repository(db)
    invoice = get_from_store("ap_invoice", invoice_id, repo)
    if not invoice:
        logger.debug("PostAPInvoice: keine Rechnung %s", invoice_id)
        return

    inv_tenant = str(invoice.get("tenantId") or invoice.get("tenant_id") or "system")
    if inv_tenant != tenant_id:
        logger.warning(
            "PostAPInvoice: Tenant-Mismatch invoice=%s request=%s", inv_tenant, tenant_id
        )
        return

    if str(invoice.get("status") or "") == "VERBUCHT" and invoice.get("journalEntryId"):
        logger.debug("PostAPInvoice: bereits verbucht %s", invoice_id)
        return

    if str(invoice.get("status") or "") != "FREIGEGEBEN":
        logger.debug(
            "PostAPInvoice: Status nicht FREIGEGEBEN (%s)", invoice.get("status")
        )
        return

    invoice_date = str(invoice.get("date") or datetime.utcnow().date().isoformat())[:10]
    period = invoice_date[:7]
    period_status = db.execute(
        text(
            """
            SELECT status
            FROM finance_accounting_periods
            WHERE tenant_id = :tenant_id AND period = :period
            LIMIT 1
            """
        ),
        {"tenant_id": inv_tenant, "period": period},
    ).fetchone()
    if period_status and str(period_status[0]) != "OPEN":
        logger.warning(
            "PostAPInvoice: Periode %s nicht offen (%s)", period, period_status[0]
        )
        return

    invoice_number = str(invoice.get("number") or invoice_id)
    total_gross = float(invoice.get("totalGross", 0) or 0)
    subtotal_net = float(invoice.get("subtotalNet", 0) or 0)
    total_tax = float(invoice.get("totalTax", 0) or 0)
    supplier_partner_id = str(
        invoice.get("customerId") or invoice.get("supplierId") or ""
    )
    invoice_country = invoice.get("country") or resolve_partner_country(
        db, supplier_partner_id, "DE"
    )
    line_rates: list[Decimal] = []
    for line in invoice.get("lines") or []:
        try:
            line_rates.append(
                Decimal(str(line.get("vatRate", 0) or 0)).quantize(Decimal("0.01"))
            )
        except Exception:
            continue
    max_rate = max(line_rates) if line_rates else Decimal("0.00")
    tax_key_cfg = resolve_tax_key_accounts(db, inv_tenant, max_rate, invoice_country)
    input_tax_account = str(tax_key_cfg.get("debit_account") or "1576")
    reverse_charge = bool(tax_key_cfg.get("reverse_charge"))

    je_id = str(uuid7())
    entry_number = f"AP-{invoice_number}"[:20]
    now = datetime.utcnow()
    entry_date = datetime.fromisoformat(invoice_date + "T12:00:00")

    je = JournalEntry(
        id=je_id,
        entry_number=entry_number,
        entry_date=entry_date,
        posting_date=entry_date,
        description=f"Eingangsrechnung {invoice_number}"[:200],
        reference=invoice_number[:50],
        source="ap_invoice_kernel",
        status="posted",
        total_debit=Decimal(str(total_gross)),
        total_credit=Decimal(str(subtotal_net + total_tax)),
        posted_by=None,
        posted_at=now,
        tenant_id=inv_tenant,
    )
    db.add(je)
    db.flush()

    db.add(
        JournalEntryLine(
            id=str(uuid7()),
            journal_entry_id=je_id,
            account_id=str(invoice.get("supplierAccountId") or "3300"),
            tenant_id=inv_tenant,
            debit=Decimal(str(total_gross)),
            credit=Decimal("0"),
            description=f"Eingangsrechnung {invoice_number}"[:200],
        )
    )
    db.add(
        JournalEntryLine(
            id=str(uuid7()),
            journal_entry_id=je_id,
            account_id=str(invoice.get("expenseAccountId") or "6000"),
            tenant_id=inv_tenant,
            debit=Decimal("0"),
            credit=Decimal(str(subtotal_net)),
            description="Aufwand"[:200],
        )
    )
    if total_tax > 0:
        db.add(
            JournalEntryLine(
                id=str(uuid7()),
                journal_entry_id=je_id,
                account_id=input_tax_account,
                tenant_id=inv_tenant,
                debit=Decimal("0"),
                credit=Decimal(str(total_tax)),
                description=(
                    "Vorsteuer (Reverse-Charge)"
                    if reverse_charge
                    else "Vorsteuer"
                )[:200],
            )
        )
    db.flush()

    log_fibu_audit(
        db,
        inv_tenant,
        "create",
        "journal_entry",
        je_id,
        {"source": "ap_invoice_kernel", "invoice_id": invoice_id},
        request=None,
    )

    invoice["status"] = "VERBUCHT"
    invoice["postedBy"] = posted_by
    invoice["postedAt"] = datetime.now().isoformat()
    invoice["journalEntryId"] = je_id

    try:
        op_insert = text(
            """
            INSERT INTO domain_erp.offene_posten
            (id, tenant_id, konto_typ, op_status, rechnungsnr, rechnungsdatum, datum, faelligkeit, op_betrag, betrag, offen,
             lieferant_id, lieferant_name, waehrung, zahlbar, created_at, updated_at)
            VALUES (:id, :tenant_id, 'kreditoren', 'offen', :rechnungsnr, :rechnungsdatum, :datum, :faelligkeit, :op_betrag, :betrag, :offen,
                    :lieferant_id, :lieferant_name, :waehrung, :zahlbar, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                offen = EXCLUDED.offen,
                op_status = EXCLUDED.op_status,
                updated_at = NOW()
            """
        )
        db.execute(
            op_insert,
            {
                "id": f"OP-AP-{invoice_id}",
                "tenant_id": inv_tenant,
                "rechnungsnr": invoice_number,
                "rechnungsdatum": invoice_date,
                "datum": invoice_date,
                "faelligkeit": str(
                    invoice.get("dueDate")
                    or (datetime.now() + timedelta(days=30)).isoformat()[:10]
                ),
                "op_betrag": total_gross,
                "betrag": total_gross,
                "offen": total_gross,
                "lieferant_id": supplier_partner_id,
                "lieferant_name": str(
                    invoice.get("supplierName") or invoice.get("customerName") or ""
                ),
                "waehrung": str(invoice.get("currency") or "EUR"),
                "zahlbar": True,
            },
        )
    except Exception as exc:
        logger.warning("PostAPInvoice: OP-Insert optional fehlgeschlagen: %s", exc)

    doc_row = db.execute(
        text(
            """
            SELECT id FROM documents
            WHERE doc_type = 'ap_invoice' AND doc_number = :num
            """
        ),
        {"num": invoice_id},
    ).fetchone()
    if doc_row:
        db.execute(
            text(
                """
                UPDATE documents
                SET data = CAST(:data AS jsonb), updated_at = :updated_at
                WHERE id = :id
                """
            ),
            {
                "id": doc_row.id,
                "data": json.dumps(invoice),
                "updated_at": datetime.utcnow(),
            },
        )

    try:
        event = APInvoicePosted(
            aggregate_id=invoice_id,
            timestamp=datetime.utcnow(),
            tenant_id=inv_tenant,
            workflow_instance_id=f"wf-ap-{invoice_id}",
            invoice_id=invoice_id,
            posted_by=posted_by,
            journal_entry_id=je_id,
        )
        payload = json.dumps(asdict(event), default=str)
        db.add(
            OutboxEvent(
                id=str(uuid4()),
                event_type="APInvoicePosted",
                aggregate_id=invoice_id,
                payload=payload,
                timestamp=event.timestamp,
                published=False,
                tenant_id=inv_tenant,
            )
        )
        db.flush()
    except Exception as exc:
        logger.warning("PostAPInvoice: Outbox optional fehlgeschlagen: %s", exc)
