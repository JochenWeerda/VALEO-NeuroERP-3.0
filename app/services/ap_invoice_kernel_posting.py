"""
Kernel PostAPInvoice: gleiche Fachlogik wie POST /ap/invoices/{id}/post, aber ohne
Repository-create mit Zwischen-commit — alles in einer Session (add/flush), Commit
erfolgt in apply_accepted_action_mutations.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today
from app.core.fibu_audit import log_fibu_audit
from app.documents.router_helpers import get_from_store, get_repository
from app.domains.shared.process_events import APInvoicePosted
from app.finance.steuerschluessel import Steuerklaerung
from app.services.finance_eingangsrechnung_buchung import buche_eingangsrechnung, summen
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.core import finance_periods

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

    # Ohne Mandant gehoert die Rechnung niemandem; bis 14.10.2026 galt sie als Rechnung des Mandanten "system".
    inv_tenant = str(invoice.get("tenantId") or invoice.get("tenant_id") or "")
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

    invoice_date = str(invoice.get("date") or business_today().isoformat())[:10]
    period = invoice_date[:7]
    gesperrt = finance_periods.gesperrter_zustand(db, inv_tenant, period)
    if gesperrt:
        logger.warning("PostAPInvoice: Periode %s ist %s", period, gesperrt)
        return

    # Zentrale Freigabe (APPROVAL-001): ohne gueltige Freigabe einer zweiten Person bucht auch der Kernel nicht.
    from app.core.exceptions import ConflictError
    from app.services.finance_freigabe import EingangsrechnungFreigabe

    freigabe = EingangsrechnungFreigabe(db, inv_tenant)
    try:
        freigabe.verlange_fuer(freigabe.vorgang_aus(invoice_id, invoice), "post", posted_by)
    except ConflictError as fehlt:
        db.rollback()
        logger.warning("PostAPInvoice: %s nicht gebucht: %s", invoice_id, fehlt.detail)
        return

    # Derselbe Buchungsweg wie REST: Aufwand und Vorsteuer je Steuerschluessel im Soll, Kreditor im Haben.
    try:
        je_id, gruppen = buche_eingangsrechnung(
            db, inv_tenant, invoice_id=invoice_id, invoice=invoice, posted_by=posted_by, quelle="ap_invoice_kernel")
    except Steuerklaerung as klaerung:
        logger.warning("PostAPInvoice: %s nicht gebucht, bitte pruefen: %s", invoice_id, klaerung)
        return
    netto, steuer, brutto = summen(gruppen)
    invoice["subtotalNet"], invoice["totalTax"], invoice["totalGross"] = float(netto), float(steuer), float(brutto)

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
