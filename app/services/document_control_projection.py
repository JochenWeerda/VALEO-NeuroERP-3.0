"""Project document-control exceptions from canonical source documents."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.document_control_service import DocumentControlService

Collector = Callable[[Session, str], list[dict[str, Any]]]


def _safe_rows(db: Session, sql: str, params: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Return mappings or None when the source relation is unavailable."""
    try:
        return [dict(row) for row in db.execute(text(sql), params).mappings().all()]
    except Exception:  # noqa: BLE001 - heterogeneous schemas; mark source unavailable
        db.rollback()
        return None


def collect_open_purchase_orders(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        """
        SELECT CAST(id AS TEXT) AS document_ref,
               COALESCE(order_number, document_number, CAST(id AS TEXT)) AS document_number,
               CAST(supplier_id AS TEXT) AS partner_ref,
               supplier_name AS partner_name
          FROM domain_procurement.purchase_orders
         WHERE tenant_id=:tid
           AND LOWER(COALESCE(status,'')) IN ('open','partial','freigegeben','bestellt')
         LIMIT 500
        """,
        {"tid": tenant_id},
    )
    if rows is None:
        return []
    return [
        {
            "exception_type": "open_purchase_order",
            "document_ref": row["document_ref"],
            "document_number": row["document_number"],
            "partner_ref": row.get("partner_ref"),
            "partner_name": row.get("partner_name"),
            "source_route": f"/einkauf/bestellung/{row['document_ref']}",
            "source_key": f"proj:open_purchase_order:{row['document_ref']}",
            "notes": "Projiziert: unerledigte Bestellung",
            "reason": "Live-Projektion Belegkontrolle",
        }
        for row in rows
    ]


def collect_missing_inbound_documents(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        """
        SELECT CAST(po.id AS TEXT) AS document_ref,
               COALESCE(po.order_number, CAST(po.id AS TEXT)) AS document_number,
               CAST(po.supplier_id AS TEXT) AS partner_ref,
               po.supplier_name AS partner_name
          FROM domain_procurement.purchase_orders po
     LEFT JOIN domain_procurement.goods_receipts gr
            ON gr.tenant_id=po.tenant_id AND gr.purchase_order_id=po.id
         WHERE po.tenant_id=:tid
           AND LOWER(COALESCE(po.status,'')) IN ('open','partial','bestellt','freigegeben')
           AND gr.id IS NULL
         LIMIT 500
        """,
        {"tid": tenant_id},
    )
    if rows is None:
        return []
    return [
        {
            "exception_type": "missing_inbound_document",
            "document_ref": row["document_ref"],
            "document_number": row["document_number"],
            "partner_ref": row.get("partner_ref"),
            "partner_name": row.get("partner_name"),
            "source_route": f"/einkauf/bestellung/{row['document_ref']}",
            "source_key": f"proj:missing_inbound_document:{row['document_ref']}",
            "notes": "Projiziert: Bestellung ohne Wareneingang",
            "reason": "Live-Projektion Belegkontrolle",
        }
        for row in rows
    ]


def collect_blocked_delivery_notes(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        """
        SELECT CAST(id AS TEXT) AS document_ref,
               COALESCE(delivery_number, document_number, CAST(id AS TEXT)) AS document_number,
               CAST(customer_id AS TEXT) AS partner_ref,
               customer_name AS partner_name
          FROM domain_sales.delivery_notes
         WHERE tenant_id=:tid
           AND (
                LOWER(COALESCE(status,'')) IN ('blocked','gesperrt','hold')
                OR COALESCE(blocked, FALSE) = TRUE
           )
         LIMIT 500
        """,
        {"tid": tenant_id},
    )
    if rows is None:
        return []
    return [
        {
            "exception_type": "blocked_delivery_note",
            "document_ref": row["document_ref"],
            "document_number": row["document_number"],
            "partner_ref": row.get("partner_ref"),
            "partner_name": row.get("partner_name"),
            "source_route": f"/verkauf/lieferschein/{row['document_ref']}",
            "source_key": f"proj:blocked_delivery_note:{row['document_ref']}",
            "notes": "Projiziert: gesperrter Lieferschein",
            "reason": "Live-Projektion Belegkontrolle",
        }
        for row in rows
    ]


def collect_uninvoiced_delivery_notes(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        """
        SELECT CAST(id AS TEXT) AS document_ref,
               COALESCE(delivery_number, document_number, CAST(id AS TEXT)) AS document_number,
               CAST(customer_id AS TEXT) AS partner_ref,
               customer_name AS partner_name
          FROM domain_sales.delivery_notes
         WHERE tenant_id=:tid
           AND LOWER(COALESCE(status,'')) IN ('delivered','shipped','offen','open','gebucht')
           AND COALESCE(invoiced, FALSE) = FALSE
           AND invoice_id IS NULL
         LIMIT 500
        """,
        {"tid": tenant_id},
    )
    if rows is None:
        return []
    return [
        {
            "exception_type": "uninvoiced_delivery_note",
            "document_ref": row["document_ref"],
            "document_number": row["document_number"],
            "partner_ref": row.get("partner_ref"),
            "partner_name": row.get("partner_name"),
            "source_route": f"/verkauf/lieferschein/{row['document_ref']}",
            "source_key": f"proj:uninvoiced_delivery_note:{row['document_ref']}",
            "notes": "Projiziert: nicht fakturierter Lieferschein",
            "reason": "Live-Projektion Belegkontrolle",
        }
        for row in rows
    ]


DEFAULT_COLLECTORS: list[Collector] = [
    collect_open_purchase_orders,
    collect_missing_inbound_documents,
    collect_blocked_delivery_notes,
    collect_uninvoiced_delivery_notes,
]


class DocumentControlProjectionService:
    def __init__(
        self,
        db: Session,
        tenant_id: str,
        *,
        collectors: list[Collector] | None = None,
    ) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.collectors = collectors or DEFAULT_COLLECTORS
        self.control = DocumentControlService(db, tenant_id)

    def refresh(self, *, actor: str) -> dict[str, Any]:
        created = 0
        refreshed = 0
        skipped = 0
        collected = 0
        for collector in self.collectors:
            candidates = collector(self.db, self.tenant_id)
            collected += len(candidates)
            for payload in candidates:
                result = self.control.upsert_projected(payload, actor=actor)
                status = result.get("projection")
                if status == "created":
                    created += 1
                elif status == "refreshed":
                    refreshed += 1
                else:
                    skipped += 1
        return {
            "tenant_id": self.tenant_id,
            "collected": collected,
            "created": created,
            "refreshed": refreshed,
            "skipped": skipped,
        }
