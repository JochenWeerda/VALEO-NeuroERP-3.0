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


# Quelle ist DocFlow, der einzige Belegspeicher (BELEG-052). Vorher lasen die Sammler
# domain_procurement.purchase_orders - eine Tabelle, die keine Migration anlegt (die Projektion fand nie eine
# Bestellung) - und domain_sales.delivery_notes, in die seit Phase 1b nichts mehr geschrieben wird.
_BESTELLUNGEN_OFFEN = """
    SELECT CAST(h.id AS TEXT) AS document_ref,
           COALESCE(h.doc_number, CAST(h.id AS TEXT)) AS document_number,
           h.supplier_id AS partner_ref,
           l.firmenname AS partner_name
      FROM domain_docflow.document_headers h
 LEFT JOIN domain_einkauf.lieferanten l
        ON l.tenant_id::text = h.tenant_id::text
       AND (l.id::text = h.supplier_id OR l.lieferantennummer = h.supplier_id)
     WHERE h.tenant_id::text = :tid AND h.doc_type = 'purchase_order' AND h.deleted_at IS NULL
       AND h.status IN ('open', 'confirmed')
       AND (NOT :ohne_wareneingang OR NOT EXISTS (
            SELECT 1 FROM domain_docflow.document_links k
              JOIN domain_docflow.document_headers g ON g.id = k.to_header_id
             WHERE k.tenant_id = h.tenant_id AND k.from_header_id = h.id
               AND g.doc_type = 'goods_receipt' AND g.deleted_at IS NULL
               AND g.status NOT IN ('cancelled', 'reversed')))
     LIMIT 500
"""

_LIEFERSCHEINE_OHNE_RECHNUNG = """
    SELECT CAST(h.id AS TEXT) AS document_ref,
           COALESCE(h.doc_number, CAST(h.id AS TEXT)) AS document_number,
           h.customer_id AS partner_ref,
           c.company_name AS partner_name
      FROM domain_docflow.document_headers h
 LEFT JOIN domain_crm.customers c
        ON c.tenant_id::text = h.tenant_id::text
       AND (c.id::text = h.customer_id OR c.customer_number = h.customer_id)
     WHERE h.tenant_id::text = :tid AND h.doc_type = 'sales_delivery' AND h.deleted_at IS NULL
       AND h.status IN ('open', 'completed')
       AND NOT EXISTS (
            SELECT 1 FROM domain_docflow.document_links k
              JOIN domain_docflow.document_headers r ON r.id = k.to_header_id
             WHERE k.tenant_id = h.tenant_id AND k.from_header_id = h.id
               AND r.doc_type = 'sales_invoice' AND r.deleted_at IS NULL
               AND r.status NOT IN ('cancelled', 'reversed'))
     LIMIT 500
"""


def _faelle(rows: list[dict[str, Any]] | None, art: str, belegart: str, notiz: str) -> list[dict[str, Any]]:
    if rows is None:
        return []
    return [
        {
            "exception_type": art,
            "document_ref": row["document_ref"],
            "document_number": row["document_number"],
            "partner_ref": row.get("partner_ref"),
            "partner_name": row.get("partner_name"),
            "source_route": f"/belege/{belegart}/{row['document_ref']}",
            "source_key": f"proj:{art}:{row['document_ref']}",
            "notes": notiz,
            "reason": "Live-Projektion Belegkontrolle",
        }
        for row in rows
    ]


def collect_open_purchase_orders(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(db, _BESTELLUNGEN_OFFEN, {"tid": tenant_id, "ohne_wareneingang": False})
    return _faelle(rows, "open_purchase_order", "purchase_order", "Projiziert: unerledigte Bestellung")


def collect_missing_inbound_documents(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(db, _BESTELLUNGEN_OFFEN, {"tid": tenant_id, "ohne_wareneingang": True})
    return _faelle(rows, "missing_inbound_document", "purchase_order", "Projiziert: Bestellung ohne Wareneingang")


def collect_uninvoiced_delivery_notes(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    rows = _safe_rows(db, _LIEFERSCHEINE_OHNE_RECHNUNG, {"tid": tenant_id})
    return _faelle(rows, "uninvoiced_delivery_note", "sales_delivery", "Projiziert: nicht fakturierter Lieferschein")


# Gesperrte Lieferscheine projiziert nichts mehr: DocFlow kennt keinen Sperrstand am Lieferschein; der Sammler las
# nur den stillgelegten Altspeicher.
DEFAULT_COLLECTORS: list[Collector] = [
    collect_open_purchase_orders,
    collect_missing_inbound_documents,
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
