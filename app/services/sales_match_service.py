"""Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2).

Gleicht je Auftragsposition (domain_crm.sales_order_items) die bestellte Menge gegen
die gelieferte Menge (Summe domain_sales.delivery_note_positions über alle Liefer-
scheine des Auftrags, Schlüssel = Artikelnummer) ab → offene Menge/Wert, Teil-/
Überlieferung (Toleranz), Lücken. Spiegelt das PROC-Match-Muster (gleiche reine
Vergleichslogik ``match_position``). Read-only.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Reine, bereits getestete Mengen-Vergleichslogik aus dem Beschaffungs-Match.
from app.services.procurement_match_service import match_position

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


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
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, order_number, customer_name, status, total_amount "
                 "FROM domain_crm.sales_orders WHERE tenant_id = :t "
                 "AND (id::text = :v OR order_number = :v) AND deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _items(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT line_number, article_number, description, quantity, unit, unit_price "
                 "FROM domain_crm.sales_order_items WHERE order_id::text = :oid AND tenant_id = :t "
                 "ORDER BY line_number"),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def _delivered_by_article(self, order_id: str) -> dict[str, Decimal]:
        rows = self.db.execute(
            text(
                "SELECT p.artikel_nr AS anr, COALESCE(SUM(p.menge),0) AS menge "
                "FROM domain_sales.delivery_notes dn "
                "JOIN domain_sales.delivery_note_positions p ON p.delivery_note_id = dn.id "
                "WHERE dn.sales_order_id::text = :oid AND dn.tenant_id = :t "
                "GROUP BY p.artikel_nr"
            ),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return {str(r["anr"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def _deliveries(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT delivery_note_number, delivery_date, status, invoice_number "
                 "FROM domain_sales.delivery_notes WHERE sales_order_id::text = :oid AND tenant_id = :t "
                 "ORDER BY delivery_date"),
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
        delivered = self._delivered_by_article(oid)

        zeilen: list[dict] = []
        luecken: list[dict] = []
        for it in items:
            anr = it["article_number"]
            geliefert = delivered.get(str(anr), Decimal("0"))
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
                SELECT o.id, o.order_number, o.customer_name, o.status, o.total_amount, o.created_at,
                       (SELECT count(*) FROM domain_crm.sales_order_items i
                        WHERE i.order_id::text = o.id AND i.tenant_id = o.tenant_id) AS n_pos,
                       EXISTS(SELECT 1 FROM domain_sales.delivery_notes d
                              WHERE d.sales_order_id::text = o.id AND d.tenant_id = o.tenant_id) AS hat_ls
                FROM domain_crm.sales_orders o
                WHERE o.tenant_id = :t AND o.deleted_at IS NULL
                ORDER BY o.created_at DESC LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"order_number": r["order_number"], "kunde": r["customer_name"], "status": r["status"],
                 "betrag": _f(r["total_amount"]), "positionen": int(r["n_pos"]),
                 "hat_lieferschein": bool(r["hat_ls"])} for r in rows]
