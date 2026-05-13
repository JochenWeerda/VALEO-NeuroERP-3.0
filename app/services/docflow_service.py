"""Service layer for the canonical Docflow command pipeline (DOCFLOW-P0-01..03)."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError

# ── document-type constants ───────────────────────────────────────────────────

TRANSITIONS: dict[str, dict[str, str]] = {
    "sales_offer": {"sales_order": "offer_to_order"},
    "sales_order": {"sales_delivery": "order_to_delivery", "sales_invoice": "order_to_invoice"},
    "sales_delivery": {"sales_invoice": "delivery_to_invoice"},
    "sales_invoice": {"sales_credit_memo": "invoice_to_credit_memo"},
    "pos_receipt": {"sales_invoice": "receipt_to_invoice", "pos_storno": "receipt_to_storno", "pos_retoure": "receipt_to_retoure"},
    "pos_retoure": {"sales_credit_memo": "retoure_to_credit_memo"},
}

DOC_PREFIX: dict[str, str] = {
    "sales_offer": "SOF",
    "sales_order": "SOR",
    "sales_delivery": "SDL",
    "sales_invoice": "SIV",
    "sales_credit_memo": "SCM",
    "pos_receipt": "POS",
    "pos_storno": "PST",
    "pos_retoure": "PRT",
}

POS_TYPES: frozenset[str] = frozenset({"pos_receipt", "pos_storno", "pos_retoure"})


# ── amount helpers ────────────────────────────────────────────────────────────

def _money(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _qty(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def _line_amounts(
    quantity: Decimal, unit_price: Decimal, discount_percent: Decimal, tax_rate: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    net = _money(quantity * unit_price * (Decimal("100") - discount_percent) / Decimal("100"))
    tax = _money(net * tax_rate / Decimal("100"))
    return net, tax, _money(net + tax)


class DocflowService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── reads ─────────────────────────────────────────────────────────────────

    def fetch_header(self, doc_id: str) -> Optional[dict[str, Any]]:
        row = self.db.execute(
            text("""
                SELECT * FROM domain_docflow.document_headers
                WHERE tenant_id = :tenant_id AND id = :id AND deleted_at IS NULL
            """),
            {"tenant_id": self.tenant_id, "id": doc_id},
        ).mappings().first()
        return dict(row) if row else None

    def fetch_items(self, doc_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text("""
                SELECT * FROM domain_docflow.document_items
                WHERE tenant_id = :tenant_id AND header_id = :header_id
                ORDER BY line_number ASC
            """),
            {"tenant_id": self.tenant_id, "header_id": doc_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def fetch_pos_compliance(self, doc_id: str) -> Optional[dict[str, Any]]:
        row = self.db.execute(
            text("""
                SELECT * FROM domain_docflow.pos_receipt_compliance
                WHERE tenant_id = :tenant_id AND header_id = :header_id
            """),
            {"tenant_id": self.tenant_id, "header_id": doc_id},
        ).mappings().first()
        return dict(row) if row else None

    def list_documents(self, doc_type: Optional[str], limit: int) -> list[str]:
        """Returns list of doc IDs ordered by created_at DESC."""
        where = ["tenant_id = :tenant_id", "deleted_at IS NULL"]
        params: dict[str, Any] = {"tenant_id": self.tenant_id, "limit": limit}
        if doc_type:
            where.append("doc_type = :doc_type")
            params["doc_type"] = doc_type
        rows = self.db.execute(
            text(f"""
                SELECT id FROM domain_docflow.document_headers
                WHERE {" AND ".join(where)}
                ORDER BY created_at DESC LIMIT :limit
            """),
            params,
        ).mappings().all()
        return [str(r["id"]) for r in rows]

    # ── bootstrap ─────────────────────────────────────────────────────────────

    def _bootstrap_sales_order(self, doc_id: str) -> Optional[dict[str, Any]]:
        existing = self.fetch_header(doc_id)
        if existing:
            return existing
        src = self.db.execute(
            text("""
                SELECT id, tenant_id, order_number, customer_id, currency, status, created_at, updated_at
                FROM domain_crm.sales_orders
                WHERE tenant_id = :tenant_id AND id = :id AND deleted_at IS NULL
            """),
            {"tenant_id": self.tenant_id, "id": doc_id},
        ).mappings().first()
        if not src:
            return None
        src_d = dict(src)
        src_items = self.db.execute(
            text("""
                SELECT id, line_number, article_number, description, quantity, unit_price, discount_percent
                FROM domain_crm.sales_order_items WHERE order_id = :order_id ORDER BY line_number ASC
            """),
            {"order_id": doc_id},
        ).mappings().all()
        total_net = total_tax = total_gross = Decimal("0.00")
        now = datetime.now(timezone.utc)
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, version, created_at, updated_at)
                VALUES (:id, :tenant_id, 'sales_order', :doc_number, :status, 'domain_crm.sales_orders', :source_ref,
                 :customer_id, NULL, :currency, 0, 0, 0, :document_date, 1, :created_at, :updated_at)
            """),
            {
                "id": str(src_d["id"]), "tenant_id": self.tenant_id,
                "doc_number": src_d["order_number"],
                "status": "open" if (src_d.get("status") or "open") not in {"posted", "reversed"} else src_d["status"],
                "source_ref": str(src_d["id"]),
                "customer_id": str(src_d["customer_id"]) if src_d.get("customer_id") else None,
                "currency": src_d.get("currency") or "EUR",
                "document_date": src_d.get("created_at") or now,
                "created_at": src_d.get("created_at") or now,
                "updated_at": src_d.get("updated_at") or now,
            },
        )
        for item in src_items:
            qty = Decimal(str(item.get("quantity") or 0))
            price = Decimal(str(item.get("unit_price") or 0))
            discount = Decimal(str(item.get("discount_percent") or 0))
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, Decimal("0"))
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description,
                     :quantity, NULL, :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, NOW(), NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": doc_id,
                    "line_number": int(item.get("line_number") or 0),
                    "source_line_id": str(item["id"]),
                    "article_number": item.get("article_number") or "",
                    "description": item.get("description"),
                    "quantity": _qty(qty), "unit_price": price, "discount_percent": discount,
                    "tax_rate": Decimal("0"),
                    "line_total_net": line_net, "line_total_tax": line_tax, "line_total_gross": line_gross,
                },
            )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET total_net=:n, total_tax=:t, total_gross=:g, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "n": _money(total_net), "t": _money(total_tax), "g": _money(total_gross)},
        )
        return self.fetch_header(doc_id)

    def _bootstrap_sales_delivery(self, doc_id: str) -> Optional[dict[str, Any]]:
        existing = self.fetch_header(doc_id)
        if existing:
            return existing
        src = self.db.execute(
            text("""
                SELECT id, tenant_id, delivery_note_number, customer_id, status, delivery_date, totals, created_at, updated_at
                FROM domain_sales.delivery_notes WHERE tenant_id = :tenant_id AND id = :id
            """),
            {"tenant_id": self.tenant_id, "id": doc_id},
        ).mappings().first()
        if not src:
            return None
        src_d = dict(src)
        src_items = self.db.execute(
            text("""
                SELECT id, pos_nr, artikel_nr, bezeichnung, menge, einheit, listenpreis, rabatt, mwst_prozent, netto_preis, netto_betrag
                FROM domain_sales.delivery_note_positions WHERE delivery_note_id = :delivery_note_id ORDER BY pos_nr ASC
            """),
            {"delivery_note_id": doc_id},
        ).mappings().all()
        total_net = total_tax = total_gross = Decimal("0.00")
        now = datetime.now(timezone.utc)
        raw_date = src_d.get("delivery_date") or src_d.get("created_at")
        if raw_date is None:
            doc_date = now
        elif isinstance(raw_date, datetime):
            doc_date = raw_date if raw_date.tzinfo else raw_date.replace(tzinfo=timezone.utc)
        else:
            try:
                doc_date = datetime.combine(raw_date, datetime.min.time(), tzinfo=timezone.utc)
            except Exception:
                doc_date = now
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, version, created_at, updated_at)
                VALUES (:id, :tenant_id, 'sales_delivery', :doc_number, :status, 'domain_sales.delivery_notes', :source_ref,
                 :customer_id, NULL, :currency, 0, 0, 0, :document_date, 1, :created_at, :updated_at)
            """),
            {
                "id": str(src_d["id"]), "tenant_id": self.tenant_id,
                "doc_number": src_d.get("delivery_note_number") or "",
                "status": "open" if (src_d.get("status") or "draft") not in {"posted", "reversed"} else (src_d.get("status") or "draft"),
                "source_ref": str(src_d["id"]),
                "customer_id": str(src_d["customer_id"]) if src_d.get("customer_id") else None,
                "currency": "EUR", "document_date": doc_date,
                "created_at": src_d.get("created_at") or now,
                "updated_at": src_d.get("updated_at") or now,
            },
        )
        for item in src_items:
            qty = Decimal(str(item.get("menge") or 0))
            price = Decimal(str(item.get("unit_price") or item.get("netto_preis") or item.get("listenpreis") or 0))
            discount = Decimal(str(item.get("rabatt") or 0))
            tax_rate = Decimal(str(item.get("mwst_prozent") or 0))
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description,
                     :quantity, :unit, :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, NOW(), NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": doc_id,
                    "line_number": int(item.get("pos_nr") or 0),
                    "source_line_id": str(item["id"]),
                    "article_number": (item.get("artikel_nr") or "").strip() or "",
                    "description": item.get("bezeichnung"),
                    "quantity": _qty(qty), "unit": item.get("einheit"),
                    "unit_price": price, "discount_percent": discount, "tax_rate": tax_rate,
                    "line_total_net": line_net, "line_total_tax": line_tax, "line_total_gross": line_gross,
                },
            )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET total_net=:n, total_tax=:t, total_gross=:g, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "n": _money(total_net), "t": _money(total_tax), "g": _money(total_gross)},
        )
        return self.fetch_header(doc_id)

    def bootstrap_doc(self, doc_id: str) -> Optional[dict[str, Any]]:
        existing = self.fetch_header(doc_id)
        if existing:
            return existing
        bootstrapped = self._bootstrap_sales_order(doc_id)
        if bootstrapped:
            return bootstrapped
        return self._bootstrap_sales_delivery(doc_id)

    # ── number series ─────────────────────────────────────────────────────────

    def allocate_doc_number(self, doc_type: str, now: datetime) -> str:
        year = now.year
        prefix = DOC_PREFIX.get(doc_type, "DOC")
        row = self.db.execute(
            text("""
                SELECT id, counter, prefix, width FROM domain_docflow.number_series
                WHERE tenant_id = :tenant_id AND doc_type = :doc_type AND year = :year FOR UPDATE
            """),
            {"tenant_id": self.tenant_id, "doc_type": doc_type, "year": year},
        ).mappings().first()
        if not row:
            current, width = 1, 6
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.number_series
                    (id, tenant_id, doc_type, year, prefix, counter, width, updated_at)
                    VALUES (:id, :tenant_id, :doc_type, :year, :prefix, 2, :width, NOW())
                """),
                {"id": str(uuid4()), "tenant_id": self.tenant_id, "doc_type": doc_type, "year": year, "prefix": prefix, "width": width},
            )
        else:
            current = int(row["counter"])
            width = int(row["width"])
            prefix = row.get("prefix") or prefix
            self.db.execute(
                text("UPDATE domain_docflow.number_series SET counter = :counter, updated_at = NOW() WHERE id = :id"),
                {"counter": current + 1, "id": row["id"]},
            )
        return f"{prefix}-{year}-{str(current).zfill(width)}"

    # ── idempotency ───────────────────────────────────────────────────────────

    def load_create_idempotency(self, idempotency_key: str) -> Optional[str]:
        row = self.db.execute(
            text("SELECT doc_id FROM domain_docflow.create_request_idempotency WHERE tenant_id=:t AND idempotency_key=:k"),
            {"t": self.tenant_id, "k": idempotency_key},
        ).mappings().first()
        return str(row["doc_id"]) if row and row.get("doc_id") else None

    def store_create_idempotency(self, idempotency_key: str, doc_id: str) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.create_request_idempotency
                (id, tenant_id, idempotency_key, doc_id, created_at)
                VALUES (:id, :tenant_id, :k, :doc_id, NOW())
                ON CONFLICT ON CONSTRAINT uq_docflow_create_idempotency DO NOTHING
            """),
            {"id": str(uuid4()), "tenant_id": self.tenant_id, "k": idempotency_key, "doc_id": doc_id},
        )

    def load_idempotent_response(self, command_name: str, resource_id: str, idempotency_key: str) -> Optional[dict[str, Any]]:
        row = self.db.execute(
            text("""
                SELECT response_payload FROM domain_docflow.command_idempotency_keys
                WHERE tenant_id=:t AND command_name=:c AND resource_id=:r AND idempotency_key=:k
            """),
            {"t": self.tenant_id, "c": command_name, "r": resource_id, "k": idempotency_key},
        ).mappings().first()
        return dict(row["response_payload"]) if row and row.get("response_payload") else None

    def store_idempotent_response(self, command_name: str, resource_id: str, idempotency_key: str, response_payload: dict[str, Any]) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.command_idempotency_keys
                (id, tenant_id, command_name, resource_id, idempotency_key, response_payload, created_at)
                VALUES (:id, :t, :c, :r, :k, CAST(:p AS jsonb), NOW())
                ON CONFLICT ON CONSTRAINT uq_docflow_command_idempotency
                DO UPDATE SET response_payload = EXCLUDED.response_payload
            """),
            {"id": str(uuid4()), "t": self.tenant_id, "c": command_name, "r": resource_id, "k": idempotency_key, "p": json.dumps(response_payload)},
        )

    # ── outbox & audit ────────────────────────────────────────────────────────

    def upsert_outbox_event(self, event_type: str, aggregate_id: str, payload: dict[str, Any]) -> str:
        event_id = str(uuid4())
        self.db.execute(
            text("""
                INSERT INTO outbox_events
                (id, event_type, aggregate_id, payload, timestamp, published, retry_count, tenant_id)
                VALUES (:id, :event_type, :aggregate_id, :payload, NOW(), FALSE, 0, :tenant_id)
            """),
            {"id": event_id, "event_type": event_type, "aggregate_id": aggregate_id, "payload": json.dumps(payload), "tenant_id": self.tenant_id},
        )
        return event_id

    def best_effort_audit(self, action: str, resource_type: str, resource_id: str, payload: dict[str, Any]) -> None:
        try:
            self.db.execute(
                text("""
                    INSERT INTO infrastructure.audit_log
                    (id, user_id, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, timestamp)
                    VALUES (CAST(:id AS uuid), NULL, :action, :resource_type, CAST(:resource_id AS uuid), '{}'::jsonb, CAST(:new_values AS jsonb), NULL, NULL, NOW())
                """),
                {
                    "id": str(uuid4()), "action": action, "resource_type": resource_type,
                    "resource_id": str(uuid5(NAMESPACE_URL, f"{resource_type}:{resource_id}")),
                    "new_values": json.dumps({"tenant_id": self.tenant_id, **payload}),
                },
            )
        except Exception:
            pass

    # ── POS compliance ────────────────────────────────────────────────────────

    def upsert_pos_compliance(self, header_id: str, pos: Any) -> None:
        if pos is None:
            return
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.pos_receipt_compliance
                (id, tenant_id, header_id, terminal_id, cash_register_id, transaction_type, payment_breakdown,
                 tse_transaction_id, tse_signature, tse_signature_counter, transaction_started_at, transaction_ended_at,
                 receipt_issued_at, dsfinvk_export_batch_id, correction_type, original_header_id, created_at, updated_at)
                VALUES (:id, :tenant_id, :header_id, :terminal_id, :cash_register_id, :transaction_type,
                 CAST(:payment_breakdown AS jsonb), :tse_transaction_id, :tse_signature, :tse_signature_counter,
                 :transaction_started_at, :transaction_ended_at, :receipt_issued_at, :dsfinvk_export_batch_id,
                 :correction_type, :original_header_id, NOW(), NOW())
                ON CONFLICT ON CONSTRAINT uq_pos_tse_header DO UPDATE SET
                  terminal_id=EXCLUDED.terminal_id, cash_register_id=EXCLUDED.cash_register_id,
                  transaction_type=EXCLUDED.transaction_type, payment_breakdown=EXCLUDED.payment_breakdown,
                  tse_transaction_id=EXCLUDED.tse_transaction_id, tse_signature=EXCLUDED.tse_signature,
                  tse_signature_counter=EXCLUDED.tse_signature_counter,
                  transaction_started_at=EXCLUDED.transaction_started_at, transaction_ended_at=EXCLUDED.transaction_ended_at,
                  receipt_issued_at=EXCLUDED.receipt_issued_at, dsfinvk_export_batch_id=EXCLUDED.dsfinvk_export_batch_id,
                  correction_type=EXCLUDED.correction_type, original_header_id=EXCLUDED.original_header_id, updated_at=NOW()
            """),
            {
                "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": header_id,
                "terminal_id": pos.terminal_id, "cash_register_id": pos.cash_register_id,
                "transaction_type": pos.transaction_type,
                "payment_breakdown": json.dumps(pos.payment_breakdown or {}),
                "tse_transaction_id": pos.tse_transaction_id, "tse_signature": pos.tse_signature,
                "tse_signature_counter": pos.tse_signature_counter,
                "transaction_started_at": pos.transaction_started_at,
                "transaction_ended_at": pos.transaction_ended_at,
                "receipt_issued_at": pos.receipt_issued_at,
                "dsfinvk_export_batch_id": pos.dsfinvk_export_batch_id,
                "correction_type": pos.correction_type, "original_header_id": pos.original_header_id,
            },
        )

    # ── line helpers ──────────────────────────────────────────────────────────

    def _insert_items(self, header_id: str, items: list[Any]) -> tuple[Decimal, Decimal, Decimal]:
        total_net = total_tax = total_gross = Decimal("0")
        for idx, line in enumerate(items, start=1):
            qty = _qty(Decimal(str(line.quantity)))
            price = Decimal(str(line.unit_price))
            discount = Decimal(str(line.discount_percent))
            tax_rate = Decimal(str(line.tax_rate))
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                     :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, NOW(), NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": header_id,
                    "line_number": idx, "article_number": line.article_number, "description": line.description,
                    "quantity": qty, "unit": line.unit, "unit_price": price, "discount_percent": discount,
                    "tax_rate": tax_rate, "line_total_net": line_net, "line_total_tax": line_tax,
                    "line_total_gross": line_gross, "batch_id": getattr(line, "batch_id", None),
                    "charge": getattr(line, "charge", None),
                },
            )
        return total_net, total_tax, total_gross

    # ── commands ──────────────────────────────────────────────────────────────

    def create_document(self, payload: Any) -> str:
        """Creates header + items + POS compliance. Returns doc_id."""
        if payload.idempotency_key:
            existing = self.load_create_idempotency(payload.idempotency_key)
            if existing:
                return existing
        now = datetime.now(timezone.utc)
        doc_id = str(uuid4())
        total_net, total_tax, total_gross = Decimal("0"), Decimal("0"), Decimal("0")
        for line in payload.items:
            line_net, line_tax, line_gross = _line_amounts(
                _qty(Decimal(str(line.quantity))), Decimal(str(line.unit_price)),
                Decimal(str(line.discount_percent)), Decimal(str(line.tax_rate)),
            )
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, posting_date, version, created_by, updated_by, created_at, updated_at)
                VALUES (:id, :tenant_id, :doc_type, :doc_number, :status, :source_system, :source_ref, :customer_id, :supplier_id,
                 :currency, :total_net, :total_tax, :total_gross, :document_date, :posting_date, 1, :created_by, :updated_by, NOW(), NOW())
            """),
            {
                "id": doc_id, "tenant_id": self.tenant_id, "doc_type": payload.doc_type,
                "doc_number": payload.doc_number, "status": payload.status,
                "source_system": payload.source_system or "docflow.ui",
                "source_ref": payload.source_ref, "customer_id": payload.customer_id,
                "supplier_id": payload.supplier_id, "currency": payload.currency,
                "total_net": _money(total_net), "total_tax": _money(total_tax), "total_gross": _money(total_gross),
                "document_date": payload.document_date or now,
                "posting_date": payload.posting_date,
                "created_by": payload.created_by, "updated_by": payload.created_by,
            },
        )
        for idx, line in enumerate(payload.items, start=1):
            qty = _qty(Decimal(str(line.quantity)))
            price = Decimal(str(line.unit_price))
            discount = Decimal(str(line.discount_percent))
            tax_rate = Decimal(str(line.tax_rate))
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                     :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, NOW(), NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": doc_id,
                    "line_number": idx, "article_number": line.article_number, "description": line.description,
                    "quantity": qty, "unit": line.unit, "unit_price": price, "discount_percent": discount,
                    "tax_rate": tax_rate, "line_total_net": line_net, "line_total_tax": line_tax,
                    "line_total_gross": line_gross, "batch_id": getattr(line, "batch_id", None),
                    "charge": getattr(line, "charge", None),
                },
            )
        self.upsert_pos_compliance(doc_id, payload.pos_compliance)
        self.best_effort_audit("docflow_create", "docflow_document", doc_id,
                               {"doc_type": payload.doc_type, "doc_number": payload.doc_number, "status": payload.status})
        if payload.idempotency_key:
            self.store_create_idempotency(payload.idempotency_key, doc_id)
        self.db.commit()
        return doc_id

    def update_document(self, doc_id: str, payload: Any) -> None:
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) in {"posted", "reversed", "cancelled"}:
            raise ConflictError("Posted/Reversed/Cancelled document cannot be edited")
        current_status = str(header.get("status") or "draft")
        if payload.items is not None and current_status != "draft":
            raise ValidationFailedError("Positionen können nur im Status Entwurf (draft) ersetzt werden")
        updates: dict[str, Any] = {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": payload.updated_by}
        set_parts = ["updated_at = NOW()", "version = version + 1", "updated_by = :updated_by"]
        for field in ("status", "customer_id", "source_system", "source_ref", "supplier_id", "currency", "document_date", "posting_date"):
            val = getattr(payload, field, None)
            if val is not None:
                set_parts.append(f"{field} = :{field}")
                updates[field] = val
        self.db.execute(
            text(f"UPDATE domain_docflow.document_headers SET {', '.join(set_parts)} WHERE id = :id AND tenant_id = :tenant_id"),
            updates,
        )
        if payload.items is not None:
            self.db.execute(
                text("DELETE FROM domain_docflow.document_items WHERE tenant_id = :tenant_id AND header_id = :header_id"),
                {"tenant_id": self.tenant_id, "header_id": doc_id},
            )
            total_net = total_tax = total_gross = Decimal("0")
            for idx, line in enumerate(payload.items, start=1):
                qty = _qty(Decimal(str(line.quantity)))
                price = Decimal(str(line.unit_price))
                discount = Decimal(str(line.discount_percent))
                tax_rate = Decimal(str(line.tax_rate))
                line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
                total_net += line_net; total_tax += line_tax; total_gross += line_gross
                self.db.execute(
                    text("""
                        INSERT INTO domain_docflow.document_items
                        (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                         unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, created_at, updated_at)
                        VALUES (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                         :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, NOW(), NOW())
                    """),
                    {
                        "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": doc_id,
                        "line_number": idx, "article_number": line.article_number, "description": line.description,
                        "quantity": qty, "unit": line.unit, "unit_price": price, "discount_percent": discount,
                        "tax_rate": tax_rate, "line_total_net": line_net, "line_total_tax": line_tax,
                        "line_total_gross": line_gross, "batch_id": getattr(line, "batch_id", None),
                        "charge": getattr(line, "charge", None),
                    },
                )
            self.db.execute(
                text("UPDATE domain_docflow.document_headers SET total_net=:n, total_tax=:t, total_gross=:g WHERE id=:id AND tenant_id=:tenant_id"),
                {"id": doc_id, "tenant_id": self.tenant_id, "n": _money(total_net), "t": _money(total_tax), "g": _money(total_gross)},
            )
        self.upsert_pos_compliance(doc_id, payload.pos_compliance)
        self.best_effort_audit("docflow_update", "docflow_document", doc_id, {"updated_by": payload.updated_by})
        self.db.commit()

    def release(self, doc_id: str, idempotency_key: str, expected_version: Optional[int], released_by: Optional[str]) -> dict[str, Any]:
        cached = self.load_idempotent_response("release", doc_id, idempotency_key)
        if cached:
            return {**cached, "idempotent_hit": True}
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if expected_version and int(header.get("version") or 1) != expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) != "draft":
            raise ValidationFailedError("Nur Dokumente im Status Entwurf (draft) können freigegeben werden")
        now = datetime.now(timezone.utc)
        new_number = self.allocate_doc_number(str(header.get("doc_type") or ""), now)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET doc_number=:doc_number, status='open', updated_at=NOW(), version=version+1, updated_by=:updated_by WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "doc_number": new_number, "updated_by": released_by},
        )
        response = {"command": "release", "source_doc_id": doc_id, "target_doc_id": None, "status": "ok",
                    "payload": {"doc_number": new_number, "doc_type": str(header.get("doc_type") or "")}}
        self.store_idempotent_response("release", doc_id, idempotency_key, response)
        self.best_effort_audit("docflow_release", "docflow_document", doc_id, {"doc_number": new_number, "released_by": released_by})
        self.db.commit()
        return response

    def record_print(self, doc_id: str, printed_by: Optional[str]) -> None:
        if not self.fetch_header(doc_id):
            raise EntityNotFoundError("DocflowDocument", doc_id)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET printed_at=NOW(), printed_by=:printed_by, print_count=COALESCE(print_count,0)+1, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "printed_by": printed_by},
        )
        self.best_effort_audit("docflow_record_print", "docflow_document", doc_id, {"printed_by": printed_by})
        self.db.commit()

    def record_export(self, doc_id: str, exported_by: Optional[str]) -> None:
        if not self.fetch_header(doc_id):
            raise EntityNotFoundError("DocflowDocument", doc_id)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET exported_at=NOW(), exported_by=:exported_by, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "exported_by": exported_by},
        )
        self.best_effort_audit("docflow_record_export", "docflow_document", doc_id, {"exported_by": exported_by})
        self.db.commit()

    def convert(self, doc_id: str, payload: Any) -> dict[str, Any]:
        cached = self.load_idempotent_response("convert", doc_id, payload.idempotency_key)
        if cached:
            return {**cached, "idempotent_hit": True}
        source = self.bootstrap_doc(doc_id)
        if not source:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(source.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        source_type = str(source["doc_type"])
        relation_type = TRANSITIONS.get(source_type, {}).get(payload.target_doc_type)
        if not relation_type:
            raise ValidationFailedError(f"Transition not allowed: {source_type} -> {payload.target_doc_type}")
        existing_link = self.db.execute(
            text("SELECT to_header_id FROM domain_docflow.document_header_links WHERE tenant_id=:t AND from_header_id=:f AND relation_type=:r"),
            {"t": self.tenant_id, "f": doc_id, "r": relation_type},
        ).mappings().first()
        if existing_link:
            existing_target_id = str(existing_link["to_header_id"])
            existing_header = self.fetch_header(existing_target_id)
            target_doc_number = str(existing_header.get("doc_number") or "") if existing_header else ""
            response = {"command": "convert", "source_doc_id": doc_id, "target_doc_id": existing_target_id, "status": "ok",
                        "payload": {"target_doc_number": target_doc_number, "target_doc_type": payload.target_doc_type, "total_gross": 0, "item_count": 0}}
            self.store_idempotent_response("convert", doc_id, payload.idempotency_key, response)
            self.db.commit()
            return response
        source_pos = self.fetch_pos_compliance(doc_id)
        if payload.target_doc_type in POS_TYPES and not source_pos:
            raise ValidationFailedError("POS conversion requires source POS compliance")
        source_items = self.fetch_items(doc_id)
        selected_items: list[dict[str, Any]] = []
        for item in source_items:
            src_qty = Decimal(str(item.get("quantity") or 0))
            target_qty = src_qty
            if payload.quantities_by_source_item_id:
                raw = payload.quantities_by_source_item_id.get(str(item["id"]))
                if raw is None:
                    continue
                target_qty = Decimal(str(raw))
                if target_qty < 0:
                    raise ValidationFailedError("Negative quantity in partial conversion")
                if target_qty > src_qty:
                    raise ValidationFailedError("Partial conversion exceeds source quantity")
            if target_qty > 0:
                selected_items.append({"item": item, "target_qty": _qty(target_qty)})
        if not selected_items:
            raise ValidationFailedError("No convertible item quantities provided")
        total_net = total_tax = total_gross = Decimal("0")
        for entry in selected_items:
            src = entry["item"]
            qty = entry["target_qty"]
            line_net, line_tax, line_gross = _line_amounts(
                qty, Decimal(str(src.get("unit_price") or 0)),
                Decimal(str(src.get("discount_percent") or 0)), Decimal(str(src.get("tax_rate") or 0)),
            )
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
        if payload.dry_run:
            return {"command": "convert", "source_doc_id": doc_id, "target_doc_id": None, "status": "dry_run",
                    "payload": {"source_doc_type": source_type, "target_doc_type": payload.target_doc_type,
                                "relation_type": relation_type, "item_count": len(selected_items),
                                "total_net": float(_money(total_net)), "total_tax": float(_money(total_tax)),
                                "total_gross": float(_money(total_gross))}}
        now = datetime.now(timezone.utc)
        target_id = str(uuid4())
        target_number = self.allocate_doc_number(payload.target_doc_type, now)
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_header_links
                (id, tenant_id, from_header_id, to_header_id, relation_type, created_at)
                VALUES (:id, :tenant_id, :from_header_id, :to_header_id, :relation_type, NOW())
            """),
            {"id": str(uuid4()), "tenant_id": self.tenant_id, "from_header_id": doc_id, "to_header_id": target_id, "relation_type": relation_type},
        )
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, version, created_by, updated_by, created_at, updated_at)
                VALUES (:id, :tenant_id, :doc_type, :doc_number, 'open', 'docflow.convert', :source_ref, :customer_id, :supplier_id,
                 :currency, :total_net, :total_tax, :total_gross, :document_date, 1, :created_by, :updated_by, NOW(), NOW())
            """),
            {
                "id": target_id, "tenant_id": self.tenant_id, "doc_type": payload.target_doc_type,
                "doc_number": target_number, "source_ref": doc_id,
                "customer_id": source.get("customer_id"), "supplier_id": source.get("supplier_id"),
                "currency": source.get("currency") or "EUR",
                "total_net": _money(total_net), "total_tax": _money(total_tax), "total_gross": _money(total_gross),
                "document_date": now, "created_by": payload.created_by, "updated_by": payload.created_by,
            },
        )
        for line_no, entry in enumerate(selected_items, start=1):
            src = entry["item"]
            qty = entry["target_qty"]
            price = Decimal(str(src.get("unit_price") or 0))
            discount = Decimal(str(src.get("discount_percent") or 0))
            tax_rate = Decimal(str(src.get("tax_rate") or 0))
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
            target_item_id = str(uuid4())
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity,
                     unit, unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, metadata, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description, :quantity,
                     :unit, :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, CAST(:metadata AS jsonb), NOW(), NOW())
                """),
                {
                    "id": target_item_id, "tenant_id": self.tenant_id, "header_id": target_id,
                    "line_number": line_no, "source_line_id": str(src["id"]),
                    "article_number": src.get("article_number") or "", "description": src.get("description"),
                    "quantity": qty, "unit": src.get("unit"), "unit_price": price, "discount_percent": discount,
                    "tax_rate": tax_rate, "line_total_net": line_net, "line_total_tax": line_tax,
                    "line_total_gross": line_gross, "metadata": json.dumps({"converted_from": str(src["id"])}),
                },
            )
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_links
                    (id, tenant_id, from_header_id, to_header_id, relation_type, from_item_id, to_item_id, quantity_linked, created_at)
                    VALUES (:id, :tenant_id, :from_header_id, :to_header_id, :relation_type, :from_item_id, :to_item_id, :quantity_linked, NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "from_header_id": doc_id, "to_header_id": target_id,
                    "relation_type": relation_type, "from_item_id": str(src["id"]),
                    "to_item_id": target_item_id, "quantity_linked": qty,
                },
            )
        if payload.target_doc_type in POS_TYPES and source_pos:
            correction_type = "storno" if payload.target_doc_type == "pos_storno" else "retoure"
            from app.api.v1.endpoints.docflow import PosComplianceInput
            self.upsert_pos_compliance(target_id, PosComplianceInput(
                terminal_id=str(source_pos.get("terminal_id") or ""),
                cash_register_id=source_pos.get("cash_register_id"),
                transaction_type="storno" if correction_type == "storno" else "retoure",
                payment_breakdown=source_pos.get("payment_breakdown") or {},
                tse_transaction_id=f"{source_pos.get('tse_transaction_id')}-R",
                tse_signature=str(source_pos.get("tse_signature") or ""),
                tse_signature_counter=source_pos.get("tse_signature_counter"),
                transaction_started_at=now, transaction_ended_at=now, receipt_issued_at=now,
                dsfinvk_export_batch_id=source_pos.get("dsfinvk_export_batch_id"),
                correction_type=correction_type, original_header_id=doc_id,
            ))
        event_id = self.upsert_outbox_event("docflow.document.converted", target_id, {
            "source_doc_id": doc_id, "target_doc_id": target_id, "source_doc_type": source_type,
            "target_doc_type": payload.target_doc_type, "relation_type": relation_type,
            "idempotency_key": payload.idempotency_key,
        })
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET updated_at=NOW(), version=version+1, updated_by=:updated_by WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": payload.created_by},
        )
        response = {"command": "convert", "source_doc_id": doc_id, "target_doc_id": target_id, "status": "ok",
                    "payload": {"target_doc_number": target_number, "target_doc_type": payload.target_doc_type,
                                "outbox_event_id": event_id, "total_gross": float(_money(total_gross)), "item_count": len(selected_items)}}
        self.store_idempotent_response("convert", doc_id, payload.idempotency_key, response)
        self.best_effort_audit("docflow_convert", "docflow_document", target_id, response)
        self.db.commit()
        return response

    def post_document(self, doc_id: str, payload: Any) -> dict[str, Any]:
        cached = self.load_idempotent_response("post", doc_id, payload.idempotency_key)
        if cached:
            return {**cached, "idempotent_hit": True}
        header = self.bootstrap_doc(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) in {"reversed", "cancelled"}:
            raise ValidationFailedError("Document cannot be posted in current status")
        if str(header.get("doc_type") or "") in POS_TYPES:
            if not self.fetch_pos_compliance(doc_id):
                raise ValidationFailedError("POS posting requires POS/TSE compliance payload")
        posting_id = str(uuid4())
        outbox_event_id = self.upsert_outbox_event("docflow.document.posted", doc_id, {
            "doc_id": doc_id, "doc_type": header.get("doc_type"), "idempotency_key": payload.idempotency_key,
        })
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES (:id, :tenant_id, :header_id, 'post', NULL, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
            """),
            {
                "id": posting_id, "tenant_id": self.tenant_id, "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "idempotency_key": payload.idempotency_key, "outbox_event_id": outbox_event_id,
                "posted_by": payload.posted_by,
            },
        )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET status='posted', posting_date=:posting_date, updated_at=NOW(), updated_by=:updated_by, version=version+1 WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "posting_date": payload.posting_date or date.today(), "updated_by": payload.posted_by},
        )
        response = {"command": "post", "source_doc_id": doc_id, "posting_id": posting_id, "status": "ok",
                    "payload": {"outbox_event_id": outbox_event_id, "posting_date": str(payload.posting_date or date.today())}}
        self.store_idempotent_response("post", doc_id, payload.idempotency_key, response)
        self.best_effort_audit("docflow_post", "docflow_document", doc_id, response)
        self.db.commit()
        return response

    def reverse_document(self, doc_id: str, payload: Any) -> dict[str, Any]:
        cached = self.load_idempotent_response("reverse", doc_id, payload.idempotency_key)
        if cached:
            return {**cached, "idempotent_hit": True}
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) == "reversed":
            raise ConflictError("Document already reversed")
        posting_id = str(uuid4())
        outbox_event_id = self.upsert_outbox_event("docflow.document.reversed", doc_id, {
            "doc_id": doc_id, "doc_type": header.get("doc_type"), "reason": payload.reason, "idempotency_key": payload.idempotency_key,
        })
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES (:id, :tenant_id, :header_id, 'reverse', NULL, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
            """),
            {
                "id": posting_id, "tenant_id": self.tenant_id, "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "idempotency_key": payload.idempotency_key, "outbox_event_id": outbox_event_id,
                "posted_by": payload.reversed_by,
            },
        )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET status='reversed', updated_at=NOW(), updated_by=:updated_by, version=version+1 WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": payload.reversed_by},
        )
        response = {"command": "reverse", "source_doc_id": doc_id, "posting_id": posting_id, "status": "ok",
                    "payload": {"reason": payload.reason, "outbox_event_id": outbox_event_id}}
        self.store_idempotent_response("reverse", doc_id, payload.idempotency_key, response)
        self.best_effort_audit("docflow_reverse", "docflow_document", doc_id, response)
        self.db.commit()
        return response
