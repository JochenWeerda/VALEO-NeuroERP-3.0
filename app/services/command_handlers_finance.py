"""
Domain-Mutationen fuer Process-Kernel-Commands (Finance / AP).

Registrierung: register_finance_command_mutations() aus app.api.v1.api.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.action_execution import ActionExecutionRequest, ActionExecutionResult

logger = logging.getLogger(__name__)


def _approve_ap_invoice_mutation(
    db: Session,
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
) -> None:
    """
    Setzt Freigabe-Status auf Eingangsrechnung (documents.ap_invoice), wenn Datensatz existiert.
    Idempotent: bei bereits FREIGEGEBEN keine Aenderung.
    """
    doc_number = request.aggregate_id
    row = db.execute(
        text(
            """
            SELECT id, data FROM documents
            WHERE doc_type = 'ap_invoice' AND doc_number = :num
            FOR UPDATE
            """
        ),
        {"num": doc_number},
    ).fetchone()
    if not row:
        logger.debug("ApproveAPInvoice: kein Dokument ap_invoice/%s", doc_number)
        return

    raw = row.data
    if raw is None:
        return
    if isinstance(raw, dict):
        data = dict(raw)
    elif isinstance(raw, str):
        data = json.loads(raw)
    else:
        logger.debug(
            "ApproveAPInvoice: Dokumentdaten nicht lesbar (Typ %s) — uebersprungen",
            type(raw).__name__,
        )
        return

    if (
        str(data.get("status") or "") == "FREIGEGEBEN"
        and str(data.get("approval_status") or "") == "approved"
    ):
        return

    data["status"] = "FREIGEGEBEN"
    data["approval_status"] = "approved"
    data["approved_at"] = datetime.now(timezone.utc).isoformat()
    data["approved_by_kernel"] = request.issuer_role or "kernel"

    db.execute(
        text(
            """
            UPDATE documents
            SET data = CAST(:data AS jsonb), updated_at = :updated_at
            WHERE id = :id
            """
        ),
        {
            "id": row.id,
            "data": json.dumps(data),
            "updated_at": datetime.utcnow(),
        },
    )


def register_finance_command_mutations() -> None:
    from app.services.action_execution_mutations import register_domain_mutation

    register_domain_mutation("ApproveAPInvoice", _approve_ap_invoice_mutation)
