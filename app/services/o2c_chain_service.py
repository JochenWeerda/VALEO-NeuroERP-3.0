"""Order-to-Cash-Kette (DOM-SALES-004) — Angebot → Auftrag → Lieferschein → Rechnung.

Read-only Sicht je Kundenauftrag über die (jetzt verknüpften) O2C-Stufen:
  Angebot (domain_crm.sales_offers) → Auftrag (domain_crm.sales_orders)
  → Lieferschein (domain_sales.delivery_notes.sales_order_id) → Rechnung
  (delivery_notes.invoice_number).
Liefert kanonischen Status (angebot→auftrag→geliefert→berechnet) und Lücken
(kein Lieferschein, keine Rechnung). Keine Schreibvorgänge.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _f(v):
    return float(v) if hasattr(v, "__float__") and not isinstance(v, bool) else v


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


class O2CChainService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT id, order_number, sales_offer_id, customer_id, customer_name, status, "
                "total_amount, currency, created_at FROM domain_crm.sales_orders "
                "WHERE tenant_id = :t AND (id::text = :v OR order_number = :v) "
                "AND deleted_at IS NULL LIMIT 1"
            ),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _offer(self, offer_id) -> Optional[dict]:
        if not offer_id:
            return None
        r = self.db.execute(
            text("SELECT id, offer_number, status, total_amount, created_at "
                 "FROM domain_crm.sales_offers WHERE id = :id LIMIT 1"),
            {"id": offer_id},
        ).mappings().first()
        return dict(r) if r else None

    def _deliveries(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT id, delivery_note_number, delivery_date, status, invoice_number, is_delivered "
                 "FROM domain_sales.delivery_notes WHERE sales_order_id::text = :oid AND tenant_id = :t "
                 "ORDER BY delivery_date"),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def trace(self, ref: str) -> dict[str, Any]:
        order = self._order(ref)
        if not order:
            return {"found": False, "detail": "Auftrag nicht auflösbar."}
        oid = str(order["id"])
        offer = self._offer(order.get("sales_offer_id"))
        deliveries = self._deliveries(oid)
        invoices = sorted({d["invoice_number"] for d in deliveries if d.get("invoice_number")})

        nodes: list[dict] = []
        if offer:
            nodes.append({"stage": "angebot", "label": "Angebot", "ref": offer["offer_number"],
                          "status": offer["status"], "betrag": _f(offer["total_amount"]),
                          "zeitpunkt": _iso(offer["created_at"])})
        nodes.append({"stage": "auftrag", "label": "Auftrag", "ref": order["order_number"],
                      "status": order["status"], "betrag": _f(order["total_amount"]),
                      "kunde": order.get("customer_name"), "zeitpunkt": _iso(order["created_at"])})
        for d in deliveries:
            nodes.append({"stage": "lieferschein", "label": "Lieferschein", "ref": d["delivery_note_number"],
                          "status": d["status"], "zeitpunkt": _iso(d["delivery_date"]),
                          "rechnung": d.get("invoice_number")})
        for inv in invoices:
            nodes.append({"stage": "rechnung", "label": "Rechnung", "ref": inv, "status": None})

        luecken: list[dict] = []
        if not offer:
            luecken.append({"stufe": "angebot", "schwere": "info", "text": "Kein Angebot verknüpft."})
        if not deliveries:
            luecken.append({"stufe": "lieferschein", "schwere": "warnung", "text": "Kein Lieferschein zum Auftrag."})
        if deliveries and not invoices:
            luecken.append({"stufe": "rechnung", "schwere": "warnung", "text": "Lieferung(en) ohne Rechnung."})

        # Kanonischer Status (höchste erreichte Stufe).
        if invoices:
            status = "berechnet"
        elif deliveries:
            status = "geliefert"
        elif order:
            status = "auftrag"
        else:
            status = "angebot"

        return {
            "found": True,
            "order_number": order["order_number"],
            "kunde": order.get("customer_name"),
            "kette": nodes,
            "luecken": luecken,
            "summary": {
                "stufen": len(nodes),
                "lieferscheine": len(deliveries),
                "rechnungen": len(invoices),
                "status": status,
                "vollstaendig": bool(deliveries and invoices),
                "offene_luecken": len(luecken),
            },
        }

    def list_orders(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT o.order_number, o.customer_name, o.status, o.total_amount, o.created_at,
                       (SELECT count(*) FROM domain_sales.delivery_notes d
                        WHERE d.sales_order_id::text = o.id AND d.tenant_id = o.tenant_id) AS n_ls,
                       (SELECT count(*) FROM domain_sales.delivery_notes d
                        WHERE d.sales_order_id::text = o.id AND d.tenant_id = o.tenant_id
                        AND d.invoice_number IS NOT NULL) AS n_rg
                FROM domain_crm.sales_orders o
                WHERE o.tenant_id = :t AND o.deleted_at IS NULL
                ORDER BY o.created_at DESC LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        out = []
        for r in rows:
            n_ls, n_rg = int(r["n_ls"]), int(r["n_rg"])
            out.append({
                "order_number": r["order_number"], "kunde": r["customer_name"], "status": r["status"],
                "betrag": _f(r["total_amount"]), "datum": _iso(r["created_at"]),
                "hat_lieferschein": n_ls > 0, "hat_rechnung": n_rg > 0,
                "vollstaendig": n_ls > 0 and n_rg > 0,
            })
        return out
