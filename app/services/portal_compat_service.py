"""Service layer for compat portal domain routes (supplier/customer portal)."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class PortalCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def get_dashboard(self) -> dict:
        orders = list_docs(self.db, "portal_order", tenant_id=self.tenant_id)
        contracts = list_docs(self.db, "portal_contract", tenant_id=self.tenant_id)
        return {
            "open_orders": len([o for o in orders if o.get("status") == "OFFEN"]),
            "active_contracts": len([c for c in contracts if c.get("status") == "AKTIV"]),
            "total_orders": len(orders),
            "generated_at": now_iso(),
        }

    # ── Orders ────────────────────────────────────────────────────────────────

    def list_orders(self, status: Optional[str] = None) -> list:
        orders = list_docs(self.db, "portal_order", tenant_id=self.tenant_id)
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return orders

    def get_order(self, order_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        return doc

    async def create_order(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("portal_order", doc["id"], doc)
        await enqueue_event(self.db, event_type="portal_order.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def update_order(self, order_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("portal_order", order_id, doc)
        return doc

    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        if doc.get("status") in ("STORNIERT", "ABGESCHLOSSEN"):
            from app.core.exceptions import ConflictError
            raise ConflictError("Order cannot be cancelled in current status")
        doc["status"] = "STORNIERT"
        if reason:
            doc["storno_reason"] = reason
        doc["cancelled_at"] = now_iso()
        repo.save("portal_order", order_id, doc)
        await enqueue_event(self.db, event_type="portal_order.cancelled",
                            aggregate_id=order_id, payload=doc, tenant_id=self.tenant_id)
        return doc

    # ── Products ──────────────────────────────────────────────────────────────

    def list_products(self) -> list:
        return list_docs(self.db, "portal_product", tenant_id=self.tenant_id)

    def get_product(self, product_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_product", product_id)
        if doc is None:
            raise EntityNotFoundError(f"Product {product_id} not found")
        return doc

    # ── Contracts ─────────────────────────────────────────────────────────────

    def list_contracts(self) -> list:
        return list_docs(self.db, "portal_contract", tenant_id=self.tenant_id)

    def get_contract(self, contract_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_contract", contract_id)
        if doc is None:
            raise EntityNotFoundError(f"Contract {contract_id} not found")
        return doc

    # ── Invoices ──────────────────────────────────────────────────────────────

    def list_invoices(self) -> list:
        return list_docs(self.db, "portal_invoice", tenant_id=self.tenant_id)

    def get_invoice(self, invoice_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_invoice", invoice_id)
        if doc is None:
            raise EntityNotFoundError(f"Invoice {invoice_id} not found")
        return doc

    # ── Notifications ─────────────────────────────────────────────────────────

    def list_notifications(self) -> list:
        return list_docs(self.db, "portal_notification", tenant_id=self.tenant_id)

    def mark_notification_read(self, notification_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_notification", notification_id)
        if doc is None:
            raise EntityNotFoundError(f"Notification {notification_id} not found")
        doc["read"] = True
        doc["read_at"] = now_iso()
        repo.save("portal_notification", notification_id, doc)
        return doc

    # ── Prices ────────────────────────────────────────────────────────────────

    def list_prices(self) -> list:
        return list_docs(self.db, "portal_price", tenant_id=self.tenant_id)

    # ── Documents ─────────────────────────────────────────────────────────────

    def list_documents(self, doc_type: Optional[str] = None) -> list:
        docs = list_docs(self.db, "portal_document", tenant_id=self.tenant_id)
        if doc_type:
            docs = [d for d in docs if d.get("doc_type") == doc_type]
        return docs

    async def upload_document(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "created_at": now_iso(), **payload}
        repo.save("portal_document", doc["id"], doc)
        return doc
