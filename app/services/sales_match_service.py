"""Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2).

Gleicht je Auftragsposition die bestellte Menge gegen die gelieferte ab → offene Menge/Wert, Teil-/Ueberlieferung
(Toleranz), Luecken. Quelle ist DocFlow (BELEG-052): geliefert ist, was die Belegverknuepfung ``order_to_delivery``
je Position (``document_links.quantity_linked``) an nicht stornierte Lieferscheine uebergeben hat - genau die Menge
der Umwandlung, nicht mehr ein Abgleich ueber die Artikelnummer. Spiegelt das PROC-Match-Muster (gleiche reine
Vergleichslogik ``match_position``). Read-only.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Reine, bereits getestete Mengen-Vergleichslogik aus dem Beschaffungs-Match.
from app.services.procurement_match_service import match_position



def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def match_summary(zeilen: list[dict]) -> dict:
    """Reine Aggregation des Positions-Match (ohne DB, testbar)."""
    return {
        "positionen": len(zeilen),
        "vollstaendig_geliefert": bool(zeilen) and all(
            z["status"] in ("vollstaendig", "ueberliefert") for z in zeilen),
        "hat_abweichung": any(z.get("abweichung") for z in zeilen),
        "offen_positionen": sum(1 for z in zeilen if z["status"] in ("offen", "teilgeliefert")),
    }


class SalesMatchService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        if not tenant_id:  # kein Rueckfall auf den Standardmandanten (bis 28.10.2026)
            raise ValueError("Mandant fehlt")
        self.tenant_id = tenant_id

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT h.id, h.doc_number AS order_number, h.status, h.total_gross AS total_amount, "
                 "(SELECT c.company_name FROM domain_crm.customers c WHERE c.id = h.customer_id "
                 " AND c.tenant_id = h.tenant_id LIMIT 1) AS customer_name "
                 "FROM domain_docflow.document_headers h WHERE h.tenant_id = :t AND h.doc_type = 'sales_order' "
                 "AND (h.id = :v OR h.doc_number = :v) AND h.deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _items(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT id, line_number, article_number, description, quantity, unit, unit_price "
                 "FROM domain_docflow.document_items WHERE header_id = :oid AND tenant_id = :t "
                 "ORDER BY line_number"),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def _delivered_by_item(self, order_id: str) -> dict[str, Decimal]:
        """Gelieferte Menge je Auftragsposition: Summe der Umwandlungen in nicht stornierte Lieferscheine."""
        rows = self.db.execute(
            text(
                "SELECT l.from_item_id AS pos, COALESCE(SUM(l.quantity_linked), 0) AS menge "
                "FROM domain_docflow.document_links l "
                "JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id "
                "WHERE l.tenant_id = :t AND l.from_header_id = :oid AND l.relation_type = 'order_to_delivery' "
                "AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed') "
                "GROUP BY l.from_item_id"
            ),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return {str(r["pos"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def _deliveries(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT d.doc_number AS delivery_note_number, d.document_date AS delivery_date, d.status, "
                "(SELECT r.doc_number FROM domain_docflow.document_header_links kr   JOIN "
                "domain_docflow.document_headers r ON r.id = kr.to_header_id AND r.tenant_id = kr.tenant_id   "
                "WHERE kr.tenant_id = d.tenant_id AND kr.from_header_id = d.id   AND kr.relation_type = "
                "'delivery_to_invoice' AND r.deleted_at IS NULL   AND r.status NOT IN ('cancelled', 'reversed') "
                "ORDER BY kr.created_at LIMIT 1) AS invoice_number FROM domain_docflow.document_header_links k "
                "JOIN domain_docflow.document_headers d ON d.id = k.to_header_id AND d.tenant_id = k.tenant_id "
                "WHERE k.tenant_id = :t AND k.from_header_id = :oid AND k.relation_type = 'order_to_delivery' "
                "AND d.deleted_at IS NULL AND d.status NOT IN ('cancelled', 'reversed') ORDER BY d.document_date"
            ),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [{"lieferschein": r["delivery_note_number"],
                 "datum": r["delivery_date"].isoformat() if r["delivery_date"] else None,
                 "status": r["status"], "rechnung": r["invoice_number"]} for r in rows]

    def match(self, ref: str) -> dict[str, Any]:
        order = self._order(ref)
        if not order:
            return {"found": False, "detail": "Auftrag nicht auflösbar."}
        oid = str(order["id"])
        items = self._items(oid)
        delivered = self._delivered_by_item(oid)

        zeilen: list[dict] = []
        luecken: list[dict] = []
        for it in items:
            anr = it["article_number"]
            geliefert = delivered.get(str(it["id"]), Decimal("0"))
            m = match_position(it["quantity"], geliefert)
            preis = _f(it["unit_price"])
            wert_offen = (m["offen"] or 0) * (preis or 0) if preis is not None else None
            zeilen.append({
                "pos_nr": it["line_number"], "artikel_nr": anr, "bezeichnung": it["description"],
                "einheit": it["unit"], "einzelpreis": preis, "wert_offen": wert_offen, **m,
            })
            if m["status"] == "offen":
                luecken.append({"pos_nr": it["line_number"], "schwere": "warnung",
                                "text": f"Position {it['line_number']} ({anr}) nicht geliefert."})
            elif m["status"] == "teilgeliefert":
                luecken.append({"pos_nr": it["line_number"], "schwere": "warnung",
                                "text": f"Position {it['line_number']} nur teilgeliefert ({m['geliefert']}/{m['bestellt']})."})
            elif m["status"] == "ueberliefert":
                luecken.append({"pos_nr": it["line_number"], "schwere": "warnung",
                                "text": f"Position {it['line_number']} überliefert ({m['geliefert']}/{m['bestellt']})."})

        deliveries = self._deliveries(oid)
        summary = match_summary(zeilen)
        summary["lieferscheine"] = len(deliveries)
        summary["offene_luecken"] = len(luecken)
        return {
            "found": True,
            "order_number": order["order_number"],
            "kunde": order.get("customer_name"),
            "status": order["status"],
            "positionen": zeilen,
            "lieferscheine": deliveries,
            "luecken": luecken,
            "summary": summary,
        }

    def list_orders(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT o.id, o.doc_number AS order_number, o.status, o.total_gross AS total_amount, o.created_at,
                       (SELECT c.company_name FROM domain_crm.customers c
                         WHERE c.id = o.customer_id AND c.tenant_id = o.tenant_id LIMIT 1) AS customer_name,
                       (SELECT count(*) FROM domain_docflow.document_items i
                         WHERE i.header_id = o.id AND i.tenant_id = o.tenant_id) AS n_pos,
                       EXISTS(SELECT 1 FROM domain_docflow.document_header_links k
                               JOIN domain_docflow.document_headers z
                                 ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id
                              WHERE k.tenant_id = o.tenant_id AND k.from_header_id = o.id
                                AND k.relation_type = 'order_to_delivery' AND z.deleted_at IS NULL
                                AND z.status NOT IN ('cancelled', 'reversed')) AS hat_ls
                FROM domain_docflow.document_headers o
                WHERE o.tenant_id = :t AND o.doc_type = 'sales_order' AND o.deleted_at IS NULL
                ORDER BY o.created_at DESC LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"order_number": r["order_number"], "kunde": r["customer_name"], "status": r["status"],
                 "betrag": _f(r["total_amount"]), "positionen": int(r["n_pos"]),
                 "hat_lieferschein": bool(r["hat_ls"])} for r in rows]
