"""Service layer for purchase-order compat routes."""
from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import (
    cache_key,
    doc_repo,
    enqueue_event,
    list_docs,
    now_iso,
    safe_float,
)

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _invalidate(self) -> None:
        try:
            from app.core.cache import cache_delete_prefix
            cache_delete_prefix(cache_key("procurement", self.tenant_id))
        except Exception:
            pass

    def _find_po(self, po_id: str) -> dict[str, Any]:
        docs = list_docs(self.db, "purchase_order", tenant_id=self.tenant_id)
        if not docs:
            docs = list_docs(self.db, "purchase_order")
        for d in docs:
            if str(d.get("id")) == po_id or str(d.get("purchaseOrderNumber")) == po_id:
                return d
        raise EntityNotFoundError(f"Purchase order {po_id} not found")

    # ── List / Get ──────────────────────────────────────────────────────────────

    def list_purchase_orders(
        self,
        *,
        status: Optional[str] = None,
        supplier_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        docs = list_docs(self.db, "purchase_order", limit=5000, tenant_id=self.tenant_id)
        if not docs:
            docs = list_docs(self.db, "purchase_order", limit=5000)

        def _match(d: dict) -> bool:
            if status and str(d.get("status")) != status:
                return False
            if supplier_id and str(d.get("supplierId")) != supplier_id:
                return False
            if search:
                s = search.lower()
                if s not in str(d.get("purchaseOrderNumber", "")).lower() and s not in str(d.get("subject", "")).lower():
                    return False
            return True

        filtered = [d for d in docs if _match(d)]
        total = len(filtered)
        start = (page - 1) * page_size
        items = filtered[start: start + page_size]
        return {
            "data": items,
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": max((total + page_size - 1) // page_size, 1),
        }

    def get_purchase_order(self, po_id: str) -> dict:
        return self._find_po(po_id)

    # ── Create ──────────────────────────────────────────────────────────────────

    async def create_purchase_order(self, payload: dict) -> dict:
        now = now_iso()
        po_number = payload.get("purchaseOrderNumber") or (
            f"PO-{now[:10].replace('-', '')}-{str(uuid4())[:6].upper()}"
        )
        item_list = payload.get("items", [])
        subtotal = float(sum(
            float(i.get("quantity", 0)) * float(i.get("unitPrice", 0))
            for i in item_list
        ))
        tax_rate = float(payload.get("taxRate", 19))
        tax_amount = round(subtotal * tax_rate / 100, 2)
        doc: dict[str, Any] = {
            "id": str(uuid4()),
            "purchaseOrderNumber": po_number,
            "supplierId": payload.get("supplierId"),
            "subject": payload.get("subject") or "",
            "description": payload.get("description") or "",
            "status": "ENTWURF",
            "orderDate": payload.get("orderDate") or now[:10],
            "deliveryDate": payload.get("deliveryDate"),
            "contactPerson": payload.get("contactPerson"),
            "paymentTerms": payload.get("paymentTerms"),
            "currency": payload.get("currency") or "EUR",
            "incoterms": payload.get("incoterms"),
            "deliveryTerms": payload.get("deliveryTerms"),
            "externalReference": payload.get("externalReference"),
            "items": item_list,
            "subtotal": round(subtotal, 2),
            "taxRate": tax_rate,
            "taxAmount": tax_amount,
            "totalAmount": round(subtotal + tax_amount, 2),
            "shippingAddress": payload.get("shippingAddress"),
            "notes": payload.get("notes"),
            "createdBy": "system",
            "createdAt": now,
            "updatedAt": now,
            "tenantId": self.tenant_id,
            "version": 1,
            "changelog": [
                {
                    "id": str(uuid4()),
                    "changeType": "CREATED",
                    "changedBy": "system",
                    "changedAt": now,
                    "fieldChanges": [],
                }
            ],
        }
        repo = doc_repo(self.db)
        repo.save("purchase_order", po_number, doc)
        await enqueue_event(
            self.db,
            event_type="purchase_order.created",
            aggregate_id=doc["id"],
            payload={
                "purchaseOrderNumber": po_number,
                "supplierId": doc.get("supplierId"),
                "status": doc.get("status"),
                "totalAmount": doc.get("totalAmount"),
                "createdAt": doc.get("createdAt"),
            },
            tenant_id=self.tenant_id,
        )
        self._invalidate()
        self.db.commit()
        return doc

    # ── Patch ───────────────────────────────────────────────────────────────────

    async def patch_purchase_order(self, po_id: str, payload: dict) -> dict:
        doc = self._find_po(po_id)
        now = now_iso()
        changes = []
        for key, value in payload.items():
            if key in {"id", "purchaseOrderNumber", "createdAt", "createdBy"}:
                continue
            old = doc.get(key)
            if old != value:
                doc[key] = value
                changes.append({"field": key, "oldValue": str(old), "newValue": str(value)})
        doc["updatedAt"] = now
        doc["version"] = int(doc.get("version", 1)) + 1
        doc.setdefault("changelog", []).append(
            {
                "id": str(uuid4()),
                "changeType": "UPDATED",
                "changedBy": "system",
                "changedAt": now,
                "fieldChanges": changes,
            }
        )
        repo = doc_repo(self.db)
        repo.save("purchase_order", doc["purchaseOrderNumber"], doc)
        self._invalidate()
        return doc

    # ── Approve / Cancel ────────────────────────────────────────────────────────

    async def approve_purchase_order(self, po_id: str) -> dict:
        doc = self._find_po(po_id)
        now = now_iso()
        doc["status"] = "FREIGEGEBEN"
        doc["approvedAt"] = now
        doc["approvedBy"] = "system"
        doc["updatedAt"] = now
        doc.setdefault("changelog", []).append(
            {
                "id": str(uuid4()),
                "changeType": "APPROVED",
                "changedBy": "system",
                "changedAt": now,
                "fieldChanges": [],
            }
        )
        repo = doc_repo(self.db)
        repo.save("purchase_order", doc["purchaseOrderNumber"], doc)
        await enqueue_event(
            self.db,
            event_type="purchase_order.approved",
            aggregate_id=doc["id"],
            payload={"purchaseOrderNumber": doc.get("purchaseOrderNumber"), "approvedAt": now},
            tenant_id=self.tenant_id,
        )
        self._invalidate()
        self.db.commit()
        return doc

    async def cancel_purchase_order(self, po_id: str, reason: str = "") -> dict:
        doc = self._find_po(po_id)
        now = now_iso()
        doc["status"] = "STORNIERT"
        doc["notes"] = (doc.get("notes") or "") + f"\nStorno: {reason}"
        doc["updatedAt"] = now
        doc.setdefault("changelog", []).append(
            {
                "id": str(uuid4()),
                "changeType": "CANCELLED",
                "changedBy": "system",
                "changedAt": now,
                "fieldChanges": [{"field": "status", "oldValue": "", "newValue": "STORNIERT"}],
            }
        )
        repo = doc_repo(self.db)
        repo.save("purchase_order", doc["purchaseOrderNumber"], doc)
        await enqueue_event(
            self.db,
            event_type="purchase_order.cancelled",
            aggregate_id=doc["id"],
            payload={"purchaseOrderNumber": doc.get("purchaseOrderNumber"), "reason": reason},
            tenant_id=self.tenant_id,
        )
        self._invalidate()
        self.db.commit()
        return doc

    # ── Statistics / Changelog ──────────────────────────────────────────────────

    def get_statistics(self) -> dict:
        docs = list_docs(self.db, "purchase_order", limit=5000, tenant_id=self.tenant_id)
        by_status: dict[str, int] = {}
        total_value = 0.0
        for d in docs:
            st = str(d.get("status") or "ENTWURF")
            by_status[st] = by_status.get(st, 0) + 1
            total_value += safe_float(d.get("totalAmount"))
        return {"totalOrders": len(docs), "totalValue": round(total_value, 2), "byStatus": by_status}

    def get_changelog(self, po_id: str) -> list:
        doc = self._find_po(po_id)
        return doc.get("changelog", [])

    # ── Communications ──────────────────────────────────────────────────────────

    def get_communications(self, po_id: str) -> list:
        doc = self._find_po(po_id)
        return doc.get("communications", [])

    async def add_communication(self, po_id: str, payload: dict) -> dict:
        doc = self._find_po(po_id)
        now = now_iso()
        item = {
            "id": str(uuid4()),
            "channel": payload.get("channel") or "email",
            "subject": payload.get("subject") or f"PO {doc.get('purchaseOrderNumber')}",
            "message": payload.get("message") or "",
            "recipient": payload.get("recipient"),
            "status": payload.get("status") or "sent",
            "createdAt": now,
        }
        doc.setdefault("communications", []).append(item)
        doc.setdefault("changelog", []).append(
            {
                "id": str(uuid4()),
                "changeType": "COMMUNICATION",
                "changedBy": "system",
                "changedAt": now,
                "fieldChanges": [],
            }
        )
        repo = doc_repo(self.db)
        repo.save("purchase_order", doc["purchaseOrderNumber"], doc)
        await enqueue_event(
            self.db,
            event_type="purchase_order.communication.sent",
            aggregate_id=str(doc.get("id") or po_id),
            payload={"channel": item["channel"], "recipient": item.get("recipient")},
            tenant_id=self.tenant_id,
        )
        self._invalidate()
        self.db.commit()
        return item
