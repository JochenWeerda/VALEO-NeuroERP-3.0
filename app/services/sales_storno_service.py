"""Lieferungs-Storno & Gutschrift-Übersicht (DOM-SALES-004.4) — durchgängig.

Storniert einen Lieferschein (status='storniert' + Grund); stornierte Lieferscheine
zählen nicht mehr als geliefert, sodass der Auftrag im Match wieder offen erscheint
(durchgängig in `sales_match_service`). Fail-closed: bereits berechnete Lieferungen
blockieren den Storno (zuerst Gutschrift). Liefert zusätzlich die vorhandenen
Gutschriften des Kunden (domain_sales.sales_credit_notes) als Übersicht.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class StornoError(Exception):
    """Fachlicher Fehler beim Lieferungs-Storno (→ HTTP 422)."""


def can_storno(status: Optional[str], invoice_number: Optional[str]) -> tuple[bool, str]:
    """Reine Storno-Vorprüfung. Liefert (erlaubt, Grund-bei-Sperre)."""
    if (status or "").lower() == "storniert":
        return False, "Lieferschein ist bereits storniert."
    if invoice_number:
        return False, "Lieferschein ist bereits berechnet — bitte zuerst eine Gutschrift erstellen."
    return True, ""


class SalesStornoService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _delivery(self, delivery_no: str) -> dict:
        r = self.db.execute(
            text("SELECT id, delivery_note_number, sales_order_id, customer_id, status, invoice_number "
                 "FROM domain_sales.delivery_notes WHERE tenant_id = :t "
                 "AND (id::text = :v OR delivery_note_number = :v) LIMIT 1"),
            {"t": self.tenant_id, "v": delivery_no},
        ).mappings().first()
        if not r:
            raise StornoError(f"Lieferschein nicht gefunden: {delivery_no}")
        return dict(r)

    def storno_delivery(self, delivery_no: str, grund: str, bediener: str = "KIM") -> dict:
        if not (grund or "").strip():
            raise StornoError("Storno-Grund ist erforderlich.")
        d = self._delivery(delivery_no)
        ok, msg = can_storno(d["status"], d["invoice_number"])
        if not ok:
            raise StornoError(msg)
        self.db.execute(
            text("UPDATE domain_sales.delivery_notes SET status = 'storniert', storno_grund = :g, "
                 "is_delivered = false WHERE id = :id AND tenant_id = :t"),
            {"g": grund, "id": d["id"], "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "lieferschein": d["delivery_note_number"], "status": "storniert"}

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, order_number, customer_id, customer_name FROM domain_crm.sales_orders "
                 "WHERE tenant_id = :t AND (id::text = :v OR order_number = :v) AND deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _credit_notes(self, customer_id: Optional[str]) -> list[dict]:
        if not customer_id:
            return []
        try:
            rows = self.db.execute(
                text("SELECT credit_note_number, total_amount, status, reason "
                     "FROM domain_sales.sales_credit_notes WHERE customer_id = :cid AND tenant_id = :t "
                     "ORDER BY credit_note_number"),
                {"cid": customer_id, "t": self.tenant_id},
            ).mappings().all()
        except Exception:
            # Gutschrift-Modul optional: tolerant leer, falls Schema/Tabelle abweicht.
            self.db.rollback()
            return []
        return [{"gutschrift": r["credit_note_number"], "betrag": float(r["total_amount"]) if r["total_amount"] is not None else None,
                 "status": r["status"], "grund": r["reason"]} for r in rows]

    def order_storno_status(self, ref: str) -> dict[str, Any]:
        order = self._order(ref)
        if not order:
            return {"found": False, "detail": "Auftrag nicht auflösbar."}
        deliveries = self.db.execute(
            text("SELECT delivery_note_number, status, invoice_number, storno_grund, delivery_date "
                 "FROM domain_sales.delivery_notes WHERE sales_order_id::text = :oid AND tenant_id = :t "
                 "ORDER BY delivery_date"),
            {"oid": str(order["id"]), "t": self.tenant_id},
        ).mappings().all()
        lieferscheine = []
        for d in deliveries:
            ok, msg = can_storno(d["status"], d["invoice_number"])
            lieferscheine.append({
                "lieferschein": d["delivery_note_number"], "status": d["status"],
                "rechnung": d["invoice_number"], "storno_grund": d["storno_grund"],
                "storno_moeglich": ok, "storno_sperrgrund": None if ok else msg,
                "datum": d["delivery_date"].isoformat() if d["delivery_date"] else None,
            })
        gutschriften = self._credit_notes(order.get("customer_id"))
        return {
            "found": True,
            "order_number": order["order_number"],
            "kunde": order.get("customer_name"),
            "lieferscheine": lieferscheine,
            "gutschriften": gutschriften,
            "summary": {
                "lieferscheine": len(lieferscheine),
                "storniert": sum(1 for ls in lieferscheine if (ls["status"] or "").lower() == "storniert"),
                "gutschriften": len(gutschriften),
            },
        }
