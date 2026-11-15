"""Order-to-Cash-Kette (DOM-SALES-004) — Angebot → Auftrag → Lieferschein → Rechnung.

Read-only Sicht je Kundenauftrag. Quelle ist DocFlow, der einzige Belegspeicher (BELEG-052): die Belege stehen in
``domain_docflow.document_headers``, ihre Folge in ``document_header_links`` (``offer_to_order``,
``order_to_delivery``, ``delivery_to_invoice``, ``order_to_invoice``). Stornierte Folgebelege zaehlen nicht als
erreichte Stufe. Liefert den kanonischen Stand (angebot→auftrag→geliefert→berechnet) und Luecken (kein
Lieferschein, keine Rechnung). Keine Schreibvorgaenge.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session



def _f(v):
    return float(v) if hasattr(v, "__float__") and not isinstance(v, bool) else v


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


class O2CChainService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        if not tenant_id:  # kein Rueckfall auf den Standardmandanten (bis 28.10.2026)
            raise ValueError("Mandant fehlt")
        self.tenant_id = tenant_id

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT h.id, h.doc_number AS order_number, h.customer_id, h.status, h.total_gross AS total_amount, "
                "h.currency, h.created_at, "
                "(SELECT c.company_name FROM domain_crm.customers c WHERE c.id = h.customer_id "
                " AND c.tenant_id = h.tenant_id LIMIT 1) AS customer_name "
                "FROM domain_docflow.document_headers h "
                "WHERE h.tenant_id = :t AND h.doc_type = 'sales_order' AND (h.id = :v OR h.doc_number = :v) "
                "AND h.deleted_at IS NULL LIMIT 1"
            ),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _offer(self, order_id: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT a.id, a.doc_number AS offer_number, a.status, a.total_gross AS total_amount, a.created_at "
                 "FROM domain_docflow.document_header_links k "
                 "JOIN domain_docflow.document_headers a ON a.id = k.from_header_id AND a.tenant_id = k.tenant_id "
                 "WHERE k.tenant_id = :t AND k.to_header_id = :oid AND k.relation_type = 'offer_to_order' "
                 "AND a.deleted_at IS NULL ORDER BY k.created_at LIMIT 1"),
            {"t": self.tenant_id, "oid": order_id},
        ).mappings().first()
        return dict(r) if r else None

    def _deliveries(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT d.id, d.doc_number AS delivery_note_number, d.document_date AS delivery_date, d.status, "
                 "(SELECT r.doc_number FROM domain_docflow.document_header_links kr "
                 "  JOIN domain_docflow.document_headers r ON r.id = kr.to_header_id AND r.tenant_id = kr.tenant_id "
                 "  WHERE kr.tenant_id = d.tenant_id AND kr.from_header_id = d.id "
                 "  AND kr.relation_type = 'delivery_to_invoice' AND r.deleted_at IS NULL "
                 "  AND r.status NOT IN ('cancelled', 'reversed') ORDER BY kr.created_at LIMIT 1) AS invoice_number "
                 "FROM domain_docflow.document_header_links k "
                 "JOIN domain_docflow.document_headers d ON d.id = k.to_header_id AND d.tenant_id = k.tenant_id "
                 "WHERE k.tenant_id = :t AND k.from_header_id = :oid AND k.relation_type = 'order_to_delivery' "
                 "AND d.deleted_at IS NULL AND d.status NOT IN ('cancelled', 'reversed') "
                 "ORDER BY d.document_date"),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def _direct_invoices(self, order_id: str) -> list[str]:
        """Rechnungen, die unmittelbar aus dem Auftrag entstanden sind (ohne Lieferschein)."""
        return [str(n) for n in self.db.execute(
            text("SELECT r.doc_number FROM domain_docflow.document_header_links k "
                 "JOIN domain_docflow.document_headers r ON r.id = k.to_header_id AND r.tenant_id = k.tenant_id "
                 "WHERE k.tenant_id = :t AND k.from_header_id = :oid AND k.relation_type = 'order_to_invoice' "
                 "AND r.deleted_at IS NULL AND r.status NOT IN ('cancelled', 'reversed')"),
            {"oid": order_id, "t": self.tenant_id},
        ).scalars().all()]

    def trace(self, ref: str) -> dict[str, Any]:
        order = self._order(ref)
        if not order:
            return {"found": False, "detail": "Auftrag nicht auflösbar."}
        oid = str(order["id"])
        offer = self._offer(oid)
        deliveries = self._deliveries(oid)
        invoices = sorted({d["invoice_number"] for d in deliveries if d.get("invoice_number")}
                          | set(self._direct_invoices(oid)))

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
                SELECT o.doc_number AS order_number, o.status, o.total_gross AS total_amount, o.created_at,
                       (SELECT c.company_name FROM domain_crm.customers c
                         WHERE c.id = o.customer_id AND c.tenant_id = o.tenant_id LIMIT 1) AS customer_name,
                       (SELECT count(*) FROM domain_docflow.document_header_links k
                         JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id
                         WHERE k.tenant_id = o.tenant_id AND k.from_header_id = o.id
                           AND k.relation_type = 'order_to_delivery' AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed')) AS n_ls,
                       (SELECT count(*) FROM domain_docflow.document_header_links k
                         JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id
                         WHERE k.tenant_id = o.tenant_id AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed')
                           AND ((k.from_header_id = o.id AND k.relation_type = 'order_to_invoice')
                             OR (k.relation_type = 'delivery_to_invoice' AND k.from_header_id IN (
                                   SELECT kl.to_header_id FROM domain_docflow.document_header_links kl
                                    WHERE kl.tenant_id = o.tenant_id AND kl.from_header_id = o.id
                                      AND kl.relation_type = 'order_to_delivery')))) AS n_rg
                FROM domain_docflow.document_headers o
                WHERE o.tenant_id = :t AND o.doc_type = 'sales_order' AND o.deleted_at IS NULL
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
