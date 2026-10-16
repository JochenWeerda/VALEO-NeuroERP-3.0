"""Service layer for the canonical Docflow command pipeline (DOCFLOW-P0-01..03)."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.finance.steuerschluessel import Steuerklaerung, satz_des_schluessels, steuergruppen, vorsteuergruppen
from app.services.finance_belegbuchung import (
    buche_einkaufsgutschrift, buche_verkaufsgutschrift, storniere_eingangsrechnung,
)
from app.services.finance_eingangsrechnung_buchung import buche_eingangsrechnung
from app.services.customer_sales_eligibility import assert_customer_allowed_for_invoice
from app.services.sales_posting_service import SalesPostingService

# ── document-type constants ───────────────────────────────────────────────────

TRANSITIONS: dict[str, dict[str, str]] = {
    "sales_offer": {"sales_order": "offer_to_order"},
    "sales_order": {"sales_delivery": "order_to_delivery", "sales_invoice": "order_to_invoice"},
    "sales_delivery": {"sales_invoice": "delivery_to_invoice"},
    "sales_invoice": {"sales_credit_memo": "invoice_to_credit_memo"},
    "pos_receipt": {"sales_invoice": "receipt_to_invoice", "pos_storno": "receipt_to_storno", "pos_retoure": "receipt_to_retoure"},
    "pos_retoure": {"sales_credit_memo": "retoure_to_credit_memo"},
    # Einkauf (seit 13.10.2026): dieselbe Kette in Gegenrichtung.
    "purchase_order": {"goods_receipt": "order_to_receipt", "purchase_invoice": "order_to_purchase_invoice"},
    "goods_receipt": {"purchase_invoice": "receipt_to_purchase_invoice"},
    "purchase_invoice": {"purchase_credit_memo": "purchase_invoice_to_credit_memo"},
}

# Einkaufsbelege nehmen Vorsteuerschluessel; alles andere Umsatzsteuerschluessel.
EINKAUF_TYPES: frozenset[str] = frozenset({"purchase_order", "goods_receipt", "purchase_invoice", "purchase_credit_memo"})
# Rechnung aus dem Auftrag direkt oder aus dessen Lieferungen — nie beides (sonst waere die Menge doppelt fakturiert).
RECHNUNGSWEGE: dict[str, tuple[str, str, str]] = {
    # Auftragsart: (Folgeart Lieferung, Uebergang Auftrag->Rechnung, Uebergang Lieferung->Rechnung)
    "sales_order": ("sales_delivery", "order_to_invoice", "delivery_to_invoice"),
    "purchase_order": ("goods_receipt", "order_to_purchase_invoice", "receipt_to_purchase_invoice"),
}


def steuerrichtung(doc_type: str) -> str:
    return "einkauf" if doc_type in EINKAUF_TYPES else "verkauf"

DOC_PREFIX: dict[str, str] = {
    "sales_offer": "SOF",
    "sales_order": "SOR",
    "sales_delivery": "SDL",
    "sales_invoice": "SIV",
    "sales_credit_memo": "SCM",
    "pos_receipt": "POS",
    "pos_storno": "PST",
    "pos_retoure": "PRT",
    "purchase_order": "POR",
    "goods_receipt": "GRN",
    "purchase_invoice": "PIV",
    "purchase_credit_memo": "PCM",
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
    def __init__(self, db: Session, tenant_id: str, akteur: Optional[str] = None) -> None:
        # Wer handelt: die Kennung aus der geprueften Anmeldung. Ist sie gesetzt, gilt sie fuer Statushistorie
        # und Protokoll — nicht das, was die Anfrage als ``*_by`` mitschickt.
        self.akteur = (akteur or "").strip() or None
        self.db = db
        self.tenant_id = tenant_id

    def _assert_invoice_customer_allowed(self, customer_id: Any) -> None:
        if customer_id:
            assert_customer_allowed_for_invoice(self.db, self.tenant_id, str(customer_id))

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
            """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).mappings().all()
        return [str(r["id"]) for r in rows]

    def delete_draft_document(self, doc_id: str) -> None:
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if str(header.get("status") or "").lower() not in {"draft", "open"}:
            raise ValidationFailedError("Only draft/open documents can be deleted")
        posting = self.db.execute(
            text("""
                SELECT 1 FROM domain_docflow.document_postings
                WHERE tenant_id = :tenant_id AND header_id = :header_id
                LIMIT 1
            """),
            {"tenant_id": self.tenant_id, "header_id": doc_id},
        ).first()
        if posting:
            raise ValidationFailedError("Posted documents cannot be deleted")
        self._kommando("delete_draft")
        self.db.execute(
            text("""
                UPDATE domain_docflow.document_headers
                SET deleted_at = NOW(), updated_at = NOW()
                WHERE tenant_id = :tenant_id AND id = :id AND deleted_at IS NULL
            """),
            {"tenant_id": self.tenant_id, "id": doc_id},
        )
        self._protokolliere("delete_draft", doc_id, {"status": header.get("status")})
        self.best_effort_audit(
            "docflow_delete_draft",
            "docflow_document",
            doc_id,
            {"status": header.get("status")},
        )
        self.db.commit()

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

    def _wer(self, angabe: Optional[str]) -> Optional[str]:
        return self.akteur or angabe

    def _sperre(self, doc_id: str) -> None:
        """Sperrt den Beleg bis zum Ende der Transaktion: Zwei Kommandos auf demselben Beleg laufen nacheinander.

        Erst danach wird die Idempotenz geprueft — sonst saehen zwei gleichzeitige Wiederholungen beide „neu“.
        """
        self.db.execute(
            text("SELECT id FROM domain_docflow.document_headers WHERE id = :id AND tenant_id = :t FOR UPDATE"),
            {"id": doc_id, "t": self.tenant_id},
        )

    @staticmethod
    def _anfrage_hash(inhalt: Optional[dict[str, Any]]) -> Optional[str]:
        if inhalt is None:
            return None
        return hashlib.sha256(json.dumps(inhalt, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def load_idempotent_response(self, command_name: str, resource_id: str, idempotency_key: str,
                                 inhalt: Optional[dict[str, Any]] = None) -> Optional[dict[str, Any]]:
        """Die Antwort auf denselben Auftrag — oder ``None``. Derselbe Schluessel mit anderem Inhalt ist ein Konflikt."""
        row = self.db.execute(
            text("""
                SELECT response_payload, request_hash FROM domain_docflow.command_idempotency_keys
                WHERE tenant_id=:t AND command_name=:c AND resource_id=:r AND idempotency_key=:k
            """),
            {"t": self.tenant_id, "c": command_name, "r": resource_id, "k": idempotency_key},
        ).mappings().first()
        if not row or not row.get("response_payload"):
            return None
        neu = self._anfrage_hash(inhalt)
        if neu is not None and row.get("request_hash") and row["request_hash"] != neu:
            raise ConflictError(
                "Der Idempotenzschlüssel wurde bereits mit anderem Inhalt verwendet; für eine andere Anfrage einen neuen Schlüssel nehmen."
            )
        return dict(row["response_payload"])

    def store_idempotent_response(self, command_name: str, resource_id: str, idempotency_key: str,
                                  response_payload: dict[str, Any], inhalt: Optional[dict[str, Any]] = None) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.command_idempotency_keys
                (id, tenant_id, command_name, resource_id, idempotency_key, response_payload, request_hash, created_at)
                VALUES (:id, :t, :c, :r, :k, CAST(:p AS jsonb), :h, NOW())
                ON CONFLICT ON CONSTRAINT uq_docflow_command_idempotency
                DO UPDATE SET response_payload = EXCLUDED.response_payload, request_hash = EXCLUDED.request_hash
            """),
            {"id": str(uuid4()), "t": self.tenant_id, "c": command_name, "r": resource_id, "k": idempotency_key,
             "p": json.dumps(response_payload), "h": self._anfrage_hash(inhalt)},
        )

    def _protokolliere(self, command: str, doc_id: str, payload: dict[str, Any]) -> None:
        """Haelt das Kommando verbindlich fest — in dieser Transaktion. Scheitert der Eintrag, scheitert das Kommando.

        ``best_effort_audit`` spiegelt zusaetzlich ins zentrale Audit-Log, wo es eines gibt; verlassen kann sich
        der Beleg nur auf dieses Protokoll.
        """
        self.db.execute(
            text(
                "INSERT INTO domain_docflow.document_command_log (tenant_id, header_id, command, actor, payload) "
                "VALUES (:t, :h, :c, :a, CAST(:p AS jsonb))"
            ),
            {"t": self.tenant_id, "h": doc_id, "c": command, "a": self.akteur, "p": json.dumps(payload, default=str)},
        )

    def fetch_command_log(self, doc_id: str) -> list[dict[str, Any]]:
        zeilen = self.db.execute(
            text(
                "SELECT command, actor, payload, logged_at FROM domain_docflow.document_command_log "
                "WHERE tenant_id = :t AND header_id = :id ORDER BY logged_at, id"
            ),
            {"t": self.tenant_id, "id": doc_id},
        ).mappings().all()
        return [dict(z) for z in zeilen]

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

    def _kommando(self, name: str, grund: Optional[str] = None) -> None:
        """Nennt der Statushistorie Kommando und Grund dieser Transaktion.

        Die Historie selbst schreibt ein Trigger auf ``document_headers`` — sie kann nicht vergessen werden
        und nicht still ausfallen. Hier kommt nur dazu, *welches* Kommando den Wechsel ausloest.
        """
        self.db.execute(
            text("SELECT set_config('valeo.docflow_command', :n, true), set_config('valeo.docflow_reason', :g, true)"),
            {"n": name, "g": grund or ""},
        )

    # ── Freigabe (APPROVAL-001) ───────────────────────────────────────────────

    def _freigabe_vor_buchung(self, doc_id: str, header: dict[str, Any]) -> None:
        """Braucht die Buchung eine zweite Person, muss ihre Freigabe vorliegen — in jedem Zugang.

        Erst die Pruefung von Finance: Ein Beleg, der sich nicht buchen laesst, meldet das und nicht die fehlende
        Freigabe. Die Freigabe wird in dieser Transaktion verbraucht; scheitert die Buchung, bleibt sie erteilt.
        """
        art = str(header.get("doc_type") or "")
        variante = BELEGARTEN.get(art)
        if variante is None or not variante.bucht:
            return
        nummer = str(header["doc_number"])
        if variante.richtung == "einkauf":
            self._vorsteuergruppen_des_belegs(doc_id, nummer)
        else:
            self._steuergruppen_der_rechnung(doc_id, nummer)
        from app.services.docflow_freigabe import DocflowFreigabe
        DocflowFreigabe(self.db, self.tenant_id).verlange(header, "post", self.akteur)

    def _freigabe_vor_storno(self, header: dict[str, Any]) -> None:
        """Der Storno eines gebuchten Belegs braucht die Freigabe einer zweiten Person mit erhoehter Berechtigung."""
        art, stand = str(header.get("doc_type") or ""), str(header.get("status") or "")
        variante = BELEGARTEN.get(art)
        # Nur wo der Storno sachlich moeglich ist: Eine gebuchte Gutschrift wird noch gar nicht storniert.
        if variante is None or not variante.bucht or stand != "posted" or art.endswith("_credit_memo"):
            return
        from app.services.docflow_freigabe import DocflowFreigabe
        DocflowFreigabe(self.db, self.tenant_id).verlange(header, "reverse", self.akteur)

    def _aktive_folgebelege(self, doc_id: str, relation_type: str) -> int:
        return int(self.db.execute(
            text(
                """
                SELECT count(*) FROM domain_docflow.document_header_links k
                JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id
                WHERE k.tenant_id = :t AND k.from_header_id = :f AND k.relation_type = :r
                  AND z.deleted_at IS NULL AND z.status NOT IN ('reversed', 'cancelled')
                """
            ),
            {"t": self.tenant_id, "f": doc_id, "r": relation_type},
        ).scalar() or 0)

    def _pruefe_rechnungsweg(self, doc_id: str, source_type: str, relation_type: str) -> None:
        """Ein Auftrag wird direkt fakturiert oder ueber seine Lieferungen — nicht beides.

        Die Restmenge gilt je Folgeart; ohne diese Regel liesse sich derselbe Auftrag einmal direkt und noch
        einmal ueber den Lieferschein berechnen.
        """
        for auftragsart, (lieferart, direkt, ueber_lieferung) in RECHNUNGSWEGE.items():
            if source_type == auftragsart and relation_type == direkt:
                if self._aktive_folgebelege(doc_id, TRANSITIONS[auftragsart][lieferart]):
                    raise ConflictError(
                        "Der Auftrag hat bereits Lieferungen; berechnet wird dann aus der Lieferung, nicht aus dem Auftrag."
                    )
            if source_type == lieferart and relation_type == ueber_lieferung:
                auftraege = self.db.execute(
                    text(
                        "SELECT from_header_id FROM domain_docflow.document_header_links "
                        "WHERE tenant_id = :t AND to_header_id = :z AND relation_type = :r"
                    ),
                    {"t": self.tenant_id, "z": doc_id, "r": TRANSITIONS[auftragsart][lieferart]},
                ).fetchall()
                for (auftrag_id,) in auftraege:
                    if self._aktive_folgebelege(str(auftrag_id), direkt):
                        raise ConflictError(
                            "Der Auftrag dieser Lieferung ist bereits direkt berechnet; eine zweite Rechnung aus der "
                            "Lieferung waere eine Doppelberechnung."
                        )

    def _bezugsnummer(self, doc_id: str, relation_type: str) -> Optional[str]:
        """Die Nummer des Belegs, aus dem dieser entstanden ist (Rechnung einer Gutschrift)."""
        return self.db.execute(
            text(
                "SELECT q.doc_number FROM domain_docflow.document_header_links k "
                "JOIN domain_docflow.document_headers q ON q.id = k.from_header_id AND q.tenant_id = k.tenant_id "
                "WHERE k.tenant_id = :t AND k.to_header_id = :z AND k.relation_type = :r LIMIT 1"
            ),
            {"t": self.tenant_id, "z": doc_id, "r": relation_type},
        ).scalar()

    def _vorsteuergruppen_des_belegs(self, doc_id: str, nummer: str) -> list[Any]:
        """Aufwand und Vorsteuer des Einkaufsbelegs je Steuerschluessel und Aufwandskonto — oder der Pruefgrund.

        Wie im Verkauf: Die Steuer je Gruppe ist die Summe der Positionssteuern des Belegs.
        """
        items = self.fetch_items(doc_id)
        try:
            gruppen = vorsteuergruppen(self.db, self.tenant_id, [
                (int(i.get("line_number") or 0), i.get("tax_code"), i.get("tax_rate"),
                 Decimal(str(i.get("line_total_net") or 0)), i.get("expense_account"))
                for i in items
            ])
        except Steuerklaerung as klaerung:
            raise ConflictError(f"Beleg {nummer} nicht gebucht, bitte prüfen: {klaerung}") from klaerung
        # Eine Position ohne eigenes Aufwandskonto gehoert zur Gruppe des Kontos ihres Steuerschluessels.
        schluesselkonto = {
            str(z[0]): (z[1] or "").strip()
            for z in self.db.execute(
                text("SELECT code, expense_account FROM domain_erp.tax_keys WHERE tenant_id = :t AND code = ANY(:codes)"),
                {"t": self.tenant_id, "codes": sorted({g.tax_code for g in gruppen})},
            ).fetchall()
        }
        for gruppe in gruppen:
            eigene = [
                i for i in items
                if str(i.get("tax_code") or "").strip() == gruppe.tax_code
                and ((i.get("expense_account") or "").strip() or schluesselkonto.get(gruppe.tax_code, "")) == gruppe.aufwandskonto
            ]
            gruppe.netto = _money(sum((Decimal(str(i.get("line_total_net") or 0)) for i in eigene), Decimal("0")))
            gruppe.steuer = _money(sum((Decimal(str(i.get("line_total_tax") or 0)) for i in eigene), Decimal("0")))
        return gruppen

    def umgewandelte_mengen(self, doc_id: str, relation_type: str) -> dict[str, Decimal]:
        """Je Quellposition die Menge, die schon in Folgebelege dieser Art gegangen ist.

        Stornierte, abgebrochene und geloeschte Folgebelege zaehlen nicht: Ihre Menge ist wieder frei.
        """
        zeilen = self.db.execute(
            text(
                """
                SELECT l.from_item_id, COALESCE(SUM(l.quantity_linked), 0)
                FROM domain_docflow.document_links l
                JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id
                WHERE l.tenant_id = :t AND l.from_header_id = :f AND l.relation_type = :r
                  AND z.deleted_at IS NULL AND z.status NOT IN ('reversed', 'cancelled')
                GROUP BY l.from_item_id
                """
            ),
            {"t": self.tenant_id, "f": doc_id, "r": relation_type},
        ).fetchall()
        return {str(z[0]): Decimal(str(z[1])) for z in zeilen}

    def fetch_status_history(self, doc_id: str) -> list[dict[str, Any]]:
        zeilen = self.db.execute(
            text(
                """
                SELECT from_status, to_status, command, actor, reason, changed_at
                FROM domain_docflow.document_status_history
                WHERE tenant_id = :t AND header_id = :id ORDER BY changed_at, id
                """
            ),
            {"t": self.tenant_id, "id": doc_id},
        ).mappings().all()
        return [dict(z) for z in zeilen]

    def best_effort_audit(self, action: str, resource_type: str, resource_id: str, payload: dict[str, Any]) -> None:
        try:
            with self.db.begin_nested():
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
        except Exception:  # noqa: BLE001 — Audit-Log-Eintrag fehlgeschlagen; Hauptoperation wird fortgesetzt
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

    def _steuer_der_position(self, nr: int, line: Any, saetze: dict[str, Decimal],
                             richtung: str = "verkauf") -> tuple[Optional[str], Decimal]:
        """Steuerschluessel und Satz der Position. Mit Schluessel kommt der Satz aus ``tax_keys``.

        Der Schluessel muss zur Belegart passen: Umsatzsteuerschluessel im Verkauf, Vorsteuerschluessel im Einkauf.
        """
        code = (getattr(line, "tax_code", None) or "").strip() or None
        angegeben = getattr(line, "tax_rate", None)
        if code is None:
            return None, Decimal(str(angegeben or 0))
        if code not in saetze:
            try:
                saetze[code] = satz_des_schluessels(self.db, self.tenant_id, code, richtung)
            except Steuerklaerung as klaerung:
                raise ValidationFailedError(f"Position {nr}: {klaerung}") from klaerung
        if angegeben is not None and Decimal(str(angegeben)) != saetze[code]:
            raise ValidationFailedError(
                f"Position {nr}: Steuersatz {Decimal(str(angegeben)).normalize():f} % widerspricht dem "
                f"Steuerschlüssel {code} ({saetze[code].normalize():f} %)."
            )
        return code, saetze[code]

    def _insert_items(self, header_id: str, items: list[Any], richtung: str = "verkauf") -> tuple[Decimal, Decimal, Decimal]:
        total_net = total_tax = total_gross = Decimal("0")
        saetze: dict[str, Decimal] = {}
        for idx, line in enumerate(items, start=1):
            qty = _qty(Decimal(str(line.quantity)))
            price = Decimal(str(line.unit_price))
            discount = Decimal(str(line.discount_percent))
            tax_code, tax_rate = self._steuer_der_position(idx, line, saetze, richtung)
            line_net, line_tax, line_gross = _line_amounts(qty, price, discount, tax_rate)
            total_net += line_net; total_tax += line_tax; total_gross += line_gross
            self.db.execute(
                text("""
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_code, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, expense_account, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                     :unit_price, :discount_percent, :tax_code, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, :expense_account, NOW(), NOW())
                """),
                {
                    "id": str(uuid4()), "tenant_id": self.tenant_id, "header_id": header_id,
                    "line_number": idx, "article_number": line.article_number, "description": line.description,
                    "quantity": qty, "unit": line.unit, "unit_price": price, "discount_percent": discount,
                    "tax_code": tax_code, "tax_rate": tax_rate, "line_total_net": line_net, "line_total_tax": line_tax,
                    "line_total_gross": line_gross, "batch_id": getattr(line, "batch_id", None),
                    "charge": getattr(line, "charge", None),
                    "expense_account": (getattr(line, "expense_account", None) or "").strip() or None,
                },
            )
        return total_net, total_tax, total_gross

    # ── commands ──────────────────────────────────────────────────────────────

    def create_document(self, payload: Any) -> str:
        return str(self.create_document_snapshot(payload)['header']['id'])

    def create_document_snapshot(self, payload: Any) -> dict[str, Any]:
        from app.services.docflow_create_command import create_snapshot
        return create_snapshot(self, payload)

    def update_document(self, doc_id: str, payload: Any) -> dict[str, Any]:
        from app.services.docflow_update_command import update_document
        return update_document(self, doc_id, payload)

    def release(self, doc_id: str, idempotency_key: str, expected_version: Optional[int], released_by: Optional[str]) -> dict[str, Any]:
        self._sperre(doc_id)
        cached = self.load_idempotent_response("release", doc_id, idempotency_key, {})
        if cached:
            # Die Belegsperre nicht ueber die Rueckkehr hinaus halten: Der naechste Aufruf wartete sonst darauf.
            self.db.rollback()
            return {**cached, "idempotent_hit": True}
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if expected_version and int(header.get("version") or 1) != expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) != "draft":
            raise ValidationFailedError("Nur Dokumente im Status Entwurf (draft) können freigegeben werden")
        now = datetime.now(timezone.utc)
        self._kommando("release")
        new_number = self.allocate_doc_number(str(header.get("doc_type") or ""), now)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET doc_number=:doc_number, status='open', updated_at=NOW(), version=version+1, updated_by=:updated_by WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "doc_number": new_number, "updated_by": self._wer(released_by)},
        )
        response = {"command": "release", "source_doc_id": doc_id, "target_doc_id": None, "status": "ok",
                    "payload": {"doc_number": new_number, "doc_type": str(header.get("doc_type") or "")}}
        self.store_idempotent_response("release", doc_id, idempotency_key, response, {})
        self._protokolliere("release", doc_id, {"doc_number": new_number})
        self.best_effort_audit("docflow_release", "docflow_document", doc_id, {"doc_number": new_number, "released_by": self._wer(released_by)})
        self.db.commit()
        return response

    def record_print(self, doc_id: str, printed_by: Optional[str]) -> None:
        if not self.fetch_header(doc_id):
            raise EntityNotFoundError("DocflowDocument", doc_id)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET printed_at=NOW(), printed_by=:printed_by, print_count=COALESCE(print_count,0)+1, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "printed_by": self._wer(printed_by)},
        )
        self._protokolliere("record_print", doc_id, {})
        self.best_effort_audit("docflow_record_print", "docflow_document", doc_id, {"printed_by": self._wer(printed_by)})
        self.db.commit()

    def record_export(self, doc_id: str, exported_by: Optional[str]) -> None:
        if not self.fetch_header(doc_id):
            raise EntityNotFoundError("DocflowDocument", doc_id)
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET exported_at=NOW(), exported_by=:exported_by, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "exported_by": self._wer(exported_by)},
        )
        self._protokolliere("record_export", doc_id, {})
        self.best_effort_audit("docflow_record_export", "docflow_document", doc_id, {"exported_by": self._wer(exported_by)})
        self.db.commit()

    def convert(self, doc_id: str, payload: Any) -> dict[str, Any]:
        source = self.bootstrap_doc(doc_id)
        if not source:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        # Zwei Umwandlungen derselben Quelle laufen nacheinander: Restmenge und Idempotenz stimmen nur so.
        self._sperre(doc_id)
        inhalt = {
            "target_doc_type": payload.target_doc_type,
            "quantities": {str(k): str(Decimal(str(v)).normalize()) for k, v in (payload.quantities_by_source_item_id or {}).items()},
        }
        cached = None if payload.dry_run else self.load_idempotent_response("convert", doc_id, payload.idempotency_key, inhalt)
        if cached:
            # Die Belegsperre nicht ueber die Rueckkehr hinaus halten: Der naechste Aufruf wartete sonst darauf.
            self.db.rollback()
            return {**cached, "idempotent_hit": True}
        if payload.target_doc_type == "sales_invoice":
            self._assert_invoice_customer_allowed(source.get("customer_id"))
        if payload.expected_version and int(source.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        source_type = str(source["doc_type"])
        relation_type = TRANSITIONS.get(source_type, {}).get(payload.target_doc_type)
        if not relation_type:
            raise ValidationFailedError(f"Transition not allowed: {source_type} -> {payload.target_doc_type}")
        self._pruefe_rechnungsweg(doc_id, source_type, relation_type)
        # Ein Auftrag kann mehrere Teillieferscheine und mehrere Rechnungen haben.
        schon = self.umgewandelte_mengen(doc_id, relation_type)
        if any(menge > 0 for menge in schon.values()) and not payload.quantities_by_source_item_id:
            # Ein blosser Wiederholungsaufruf erzeugt keinen weiteren Folgebeleg: Teilmengen werden ausdruecklich verlangt.
            raise ConflictError(
                f"Der Beleg ist für {payload.target_doc_type} bereits (teilweise) umgewandelt. Für einen weiteren "
                "Folgebeleg die Mengen je Position ausdrücklich angeben."
            )
        source_pos = self.fetch_pos_compliance(doc_id)
        if payload.target_doc_type in POS_TYPES and not source_pos:
            raise ValidationFailedError("POS conversion requires source POS compliance")
        source_items = self.fetch_items(doc_id)
        selected_items: list[dict[str, Any]] = []
        rest_gesamt = Decimal("0")
        for item in source_items:
            src_qty = Decimal(str(item.get("quantity") or 0))
            rest = src_qty - schon.get(str(item["id"]), Decimal("0"))
            if rest < 0:
                rest = Decimal("0")
            rest_gesamt += rest
            # Ohne Mengenangabe geht der ganze Rest in den Folgebeleg.
            target_qty = rest
            if payload.quantities_by_source_item_id:
                raw = payload.quantities_by_source_item_id.get(str(item["id"]))
                if raw is None:
                    continue
                target_qty = Decimal(str(raw))
                if target_qty < 0:
                    raise ValidationFailedError("Negative quantity in partial conversion")
                if target_qty > rest:
                    raise ValidationFailedError(
                        f"Position {item.get('line_number')}: Menge {_qty(target_qty).normalize():f} übersteigt die "
                        f"Restmenge {_qty(rest).normalize():f} (Beleg {_qty(src_qty).normalize():f}, bereits umgewandelt "
                        f"{_qty(src_qty - rest).normalize():f})."
                    )
            if target_qty > 0:
                selected_items.append({"item": item, "target_qty": _qty(target_qty)})
        if source_items and rest_gesamt <= 0:
            raise ConflictError(
                f"Der Beleg ist für {payload.target_doc_type} vollständig umgewandelt; es gibt keine Restmenge."
            )
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
            self.db.rollback()  # Trockenlauf: nichts geschrieben, Sperre frei
            return {"command": "convert", "source_doc_id": doc_id, "target_doc_id": None, "status": "dry_run",
                    "payload": {"source_doc_type": source_type, "target_doc_type": payload.target_doc_type,
                                "relation_type": relation_type, "item_count": len(selected_items),
                                "total_net": float(_money(total_net)), "total_tax": float(_money(total_tax)),
                                "total_gross": float(_money(total_gross))}}
        now = datetime.now(timezone.utc)
        target_id = str(uuid4())
        self._kommando("convert", f"aus {source_type} {source.get('doc_number')}")
        target_number = self.allocate_doc_number(payload.target_doc_type, now)
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
                "document_date": now, "created_by": self._wer(payload.created_by), "updated_by": self._wer(payload.created_by),
            },
        )
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_header_links
                (id, tenant_id, from_header_id, to_header_id, relation_type, created_at)
                VALUES (:id, :tenant_id, :from_header_id, :to_header_id, :relation_type, NOW())
            """),
            {"id": str(uuid4()), "tenant_id": self.tenant_id, "from_header_id": doc_id, "to_header_id": target_id, "relation_type": relation_type},
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
                     unit, unit_price, discount_percent, tax_code, tax_rate, line_total_net, line_total_tax, line_total_gross, expense_account, metadata, created_at, updated_at)
                    VALUES (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description, :quantity,
                     :unit, :unit_price, :discount_percent, :tax_code, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :expense_account, CAST(:metadata AS jsonb), NOW(), NOW())
                """),
                {
                    "id": target_item_id, "tenant_id": self.tenant_id, "header_id": target_id,
                    "line_number": line_no, "source_line_id": str(src["id"]),
                    "article_number": src.get("article_number") or "", "description": src.get("description"),
                    "quantity": qty, "unit": src.get("unit"), "unit_price": price, "discount_percent": discount,
                    "tax_code": src.get("tax_code"), "expense_account": src.get("expense_account"),
                    "tax_rate": tax_rate, "line_total_net": line_net,
                    "line_total_tax": line_tax,
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
            {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": self._wer(payload.created_by)},
        )
        response = {"command": "convert", "source_doc_id": doc_id, "target_doc_id": target_id, "status": "ok",
                    "payload": {"target_doc_number": target_number, "target_doc_type": payload.target_doc_type,
                                "outbox_event_id": event_id, "total_gross": float(_money(total_gross)), "item_count": len(selected_items)}}
        self.store_idempotent_response("convert", doc_id, payload.idempotency_key, response, inhalt)
        self._protokolliere("convert", doc_id, {"target_doc_id": target_id, "target_doc_type": payload.target_doc_type,
                                                "quantities": {str(e["item"]["id"]): str(e["target_qty"]) for e in selected_items}})
        self._protokolliere("create", target_id, {"aus": doc_id, "doc_type": payload.target_doc_type})
        self.best_effort_audit("docflow_convert", "docflow_document", target_id, response)
        self.db.commit()
        return response

    def _steuergruppen_der_rechnung(self, doc_id: str, nummer: str) -> list[Any]:
        """Erloes und Umsatzsteuer der Rechnung je Steuerschluessel — oder der Grund, warum nicht gebucht wird.

        Bis zum 13.10.2026 gingen die Kopfsummen fest auf 8400 und 1776, gleich welcher Satz in den Positionen
        stand. Finance ist die Buchungsautoritaet: Konten und Satz kommen aus ``tax_keys``; der Beleg nennt je
        Position nur den Schluessel. Beleg und Buchung stimmen auf den Cent — die Steuer je Schluessel ist die
        Summe der Positionssteuern des Belegs, nicht neu gerechnet.
        """
        items = self.fetch_items(doc_id)
        try:
            gruppen = steuergruppen(self.db, self.tenant_id, [
                (int(i.get("line_number") or 0), i.get("tax_code"), i.get("tax_rate"), Decimal(str(i.get("line_total_net") or 0)))
                for i in items
            ])
        except Steuerklaerung as klaerung:
            raise ConflictError(f"Rechnung {nummer} nicht gebucht, bitte prüfen: {klaerung}") from klaerung
        for gruppe in gruppen:
            eigene = [i for i in items if str(i.get("tax_code") or "").strip() == gruppe.tax_code]
            gruppe.netto = _money(sum((Decimal(str(i.get("line_total_net") or 0)) for i in eigene), Decimal("0")))
            gruppe.steuer = _money(sum((Decimal(str(i.get("line_total_tax") or 0)) for i in eigene), Decimal("0")))
        return gruppen

    def post_document(self, doc_id: str, payload: Any) -> dict[str, Any]:
        self._sperre(doc_id)
        cached = self.load_idempotent_response("post", doc_id, payload.idempotency_key, {"posting_date": str(payload.posting_date or "")})
        if cached:
            # Die Belegsperre nicht ueber die Rueckkehr hinaus halten: Der naechste Aufruf wartete sonst darauf.
            self.db.rollback()
            return {**cached, "idempotent_hit": True}
        header = self.bootstrap_doc(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) == "posted":
            raise ConflictError("Document already posted")
        if str(header.get("status")) in {"reversed", "cancelled"}:
            raise ValidationFailedError("Document cannot be posted in current status")
        if str(header.get("doc_type") or "") in POS_TYPES:
            if not self.fetch_pos_compliance(doc_id):
                raise ValidationFailedError("POS posting requires POS/TSE compliance payload")
        self._freigabe_vor_buchung(doc_id, header)
        finance_result: dict[str, str] = {}
        if str(header.get("doc_type") or "") == "sales_invoice":
            customer_id = str(header.get("customer_id") or "")
            if not customer_id:
                raise ValidationFailedError("Sales invoice posting requires customer_id")
            gruppen = self._steuergruppen_der_rechnung(doc_id, str(header["doc_number"]))
            # Kein eigener Commit: Buchung, Buchungsnachweis und Belegstatus werden gemeinsam festgeschrieben.
            finance_result = SalesPostingService(
                self.db, self.tenant_id, commit=False
            ).post_ausgangsrechnung_with_op(
                invoice_number=str(header["doc_number"]),
                invoice_date=header.get("document_date"),
                customer_id=customer_id,
                net_amount=Decimal(str(header.get("total_net") or 0)),
                tax_amount=Decimal(str(header.get("total_tax") or 0)),
                gross_amount=Decimal(str(header.get("total_gross") or 0)),
                posted_by=self._wer(payload.posted_by),
                steuergruppen=gruppen,
            )
        doc_type = str(header.get("doc_type") or "")
        nummer = str(header["doc_number"])
        wer = self._wer(payload.posted_by)
        try:
            if doc_type == "sales_credit_memo":
                gruppen = self._steuergruppen_der_rechnung(doc_id, nummer)
                finance_result = {"journal_entry_id": buche_verkaufsgutschrift(
                    self.db, self.tenant_id, nummer=nummer, datum=header.get("document_date"), gruppen=gruppen,
                    rechnungsnummer=self._bezugsnummer(doc_id, "invoice_to_credit_memo"), posted_by=wer)}
            elif doc_type in {"purchase_invoice", "purchase_credit_memo"}:
                if not str(header.get("supplier_id") or ""):
                    raise ValidationFailedError("Ein Einkaufsbeleg wird nur mit Lieferant gebucht.")
                gruppen = self._vorsteuergruppen_des_belegs(doc_id, nummer)
                beleg = {"number": nummer, "date": str(header.get("document_date") or "")[:10] or None,
                         "customerId": header.get("supplier_id"), "currency": header.get("currency")}
                if doc_type == "purchase_invoice":
                    journal_id, _gruppen = buche_eingangsrechnung(
                        self.db, self.tenant_id, invoice_id=doc_id, invoice=beleg, posted_by=wer,
                        quelle="purchase_invoice", gruppen=gruppen)
                else:
                    journal_id = buche_einkaufsgutschrift(
                        self.db, self.tenant_id, nummer=nummer, datum=header.get("document_date"), gruppen=gruppen,
                        rechnungsnummer=self._bezugsnummer(doc_id, "purchase_invoice_to_credit_memo"),
                        posted_by=wer, beleg=beleg)
                finance_result = {"journal_entry_id": journal_id}
        except Steuerklaerung as klaerung:
            raise ConflictError(f"Beleg {nummer} nicht gebucht, bitte prüfen: {klaerung}") from klaerung
        self._kommando("post")
        posting_id = str(uuid4())
        outbox_event_id = self.upsert_outbox_event("docflow.document.posted", doc_id, {
            "doc_id": doc_id, "doc_type": header.get("doc_type"), "idempotency_key": payload.idempotency_key,
        })
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES (:id, :tenant_id, :header_id, 'post', :journal_entry_id, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
            """),
            {
                "id": posting_id, "tenant_id": self.tenant_id, "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "journal_entry_id": finance_result.get("journal_entry_id"),
                "idempotency_key": payload.idempotency_key, "outbox_event_id": outbox_event_id,
                "posted_by": self._wer(payload.posted_by),
            },
        )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET status='posted', posting_date=:posting_date, updated_at=NOW(), updated_by=:updated_by, version=version+1 WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "posting_date": payload.posting_date or date.today(), "updated_by": self._wer(payload.posted_by)},
        )
        response = {"command": "post", "source_doc_id": doc_id, "posting_id": posting_id, "status": "ok",
                    "payload": {"outbox_event_id": outbox_event_id, "posting_date": str(payload.posting_date or date.today()),
                                **finance_result}}
        self.store_idempotent_response("post", doc_id, payload.idempotency_key, response, {"posting_date": str(payload.posting_date or "")})
        self._protokolliere("post", doc_id, {"posting_id": posting_id, **finance_result})
        self.best_effort_audit("docflow_post", "docflow_document", doc_id, response)
        self.db.commit()
        return response

    def reverse_document(self, doc_id: str, payload: Any) -> dict[str, Any]:
        self._sperre(doc_id)
        cached = self.load_idempotent_response("reverse", doc_id, payload.idempotency_key, {"reason": payload.reason})
        if cached:
            # Die Belegsperre nicht ueber die Rueckkehr hinaus halten: Der naechste Aufruf wartete sonst darauf.
            self.db.rollback()
            return {**cached, "idempotent_hit": True}
        header = self.fetch_header(doc_id)
        if not header:
            raise EntityNotFoundError("DocflowDocument", doc_id)
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise ConflictError("Version conflict")
        if str(header.get("status")) == "reversed":
            raise ConflictError("Document already reversed")
        self._freigabe_vor_storno(header)
        finance_result: dict[str, str] = {}
        if str(header.get("doc_type") or "") == "sales_invoice":
            if str(header.get("status")) != "posted":
                raise ValidationFailedError("Only posted sales invoices can be reversed")
            # Kein eigener Commit: Stornobuchung, Nachweis, Statushistorie und Belegstatus gemeinsam.
            finance_result = SalesPostingService(
                self.db, self.tenant_id, commit=False
            ).reverse_ausgangsrechnung(
                invoice_number=str(header["doc_number"]),
                reason=payload.reason,
            )
        doc_type = str(header.get("doc_type") or "")
        if doc_type == "purchase_invoice":
            if str(header.get("status")) != "posted":
                raise ValidationFailedError("Nur eine gebuchte Eingangsrechnung wird storniert.")
            finance_result = storniere_eingangsrechnung(
                self.db, self.tenant_id, nummer=str(header["doc_number"]), grund=payload.reason)
        elif doc_type in {"sales_credit_memo", "purchase_credit_memo"} and str(header.get("status")) == "posted":
            # Ohne Gegenbuchung waere der Beleg „storniert“ und die Buchung stuende weiter.
            raise ValidationFailedError(
                "Eine gebuchte Gutschrift wird hier noch nicht storniert: Die Gegenbuchung dafür fehlt."
            )
        self._kommando("reverse", payload.reason)
        posting_id = str(uuid4())
        outbox_event_id = self.upsert_outbox_event("docflow.document.reversed", doc_id, {
            "doc_id": doc_id, "doc_type": header.get("doc_type"), "reason": payload.reason, "idempotency_key": payload.idempotency_key,
        })
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES (:id, :tenant_id, :header_id, 'reverse', :journal_entry_id, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
            """),
            {
                "id": posting_id, "tenant_id": self.tenant_id, "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "journal_entry_id": finance_result.get("reversal_entry_id"),
                "idempotency_key": payload.idempotency_key, "outbox_event_id": outbox_event_id,
                "posted_by": self._wer(payload.reversed_by),
            },
        )
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET status='reversed', updated_at=NOW(), updated_by=:updated_by, version=version+1 WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": self._wer(payload.reversed_by)},
        )
        response = {"command": "reverse", "source_doc_id": doc_id, "posting_id": posting_id, "status": "ok",
                    "payload": {"reason": payload.reason, "outbox_event_id": outbox_event_id,
                                **finance_result}}
        self.store_idempotent_response("reverse", doc_id, payload.idempotency_key, response, {"reason": payload.reason})
        self._protokolliere("reverse", doc_id, {"posting_id": posting_id, "reason": payload.reason, **finance_result})
        self.best_effort_audit("docflow_reverse", "docflow_document", doc_id, response)
        self.db.commit()
        return response
