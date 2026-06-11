"""Kreditlimit-Prüfung & Rechnungs-/Billing-Status im O2C-Kontext (DOM-SALES-004.3).

Kreditlimit-Prüfung je Kundenauftrag: Kreditlimit (domain_crm.customers.credit_limit)
gegen die offene Exposure (Summe offener Kundenaufträge). Liefert Ampel
(ok/warnung/blockiert), verfügbaren Rahmen und die Wirkung des konkreten Auftrags.

Zusätzlich der Billing-Status je Lieferschein (berechnet/offen) aus dem O2C-Beleg-
fluss. Hinweis: Die tiefere Buchungs-/OP-Verknüpfung (FIBU-Journal, Debitoren-OP)
setzt die Finanztabellen voraus; diese sind im DEV-Stand nicht durchgängig vorhanden,
daher wird der Billing-Status tolerant aus den O2C-Belegen abgeleitet (fail-safe).
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_WARN_PCT = 80.0
_BLOCK_PCT = 100.0


def credit_check(limit, exposure, betrag: float = 0.0,
                 warn_pct: float = _WARN_PCT, block_pct: float = _BLOCK_PCT) -> dict:
    """Reine Kreditlimit-Prüfung. Ampel auf Basis Exposure (+ optionalem Betrag).

    - kein_limit: kein Kreditlimit hinterlegt (keine Sperre).
    - ok/warnung/blockiert: nach Auslastung gegen Warn-/Sperrschwelle."""
    limit = float(limit or 0)
    exposure = float(exposure or 0)
    betrag = float(betrag or 0)
    exposure_neu = exposure + betrag
    if limit <= 0:
        return {"ampel": "kein_limit", "limit": 0.0, "exposure": round(exposure, 2),
                "verfuegbar": None, "auslastung_pct": 0.0, "auslastung_neu_pct": 0.0}
    util = exposure / limit * 100
    util_neu = exposure_neu / limit * 100
    if util_neu >= block_pct:
        ampel = "blockiert"
    elif util_neu >= warn_pct:
        ampel = "warnung"
    else:
        ampel = "ok"
    return {
        "ampel": ampel,
        "limit": round(limit, 2),
        "exposure": round(exposure, 2),
        "verfuegbar": round(limit - exposure, 2),
        "auslastung_pct": round(util, 2),
        "auslastung_neu_pct": round(util_neu, 2),
    }


class SalesCreditService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _limit(self, customer_id: str) -> float:
        row = self.db.execute(
            text("SELECT credit_limit FROM domain_crm.customers WHERE id = :cid AND tenant_id = :t"),
            {"cid": customer_id, "t": self.tenant_id},
        ).mappings().first()
        return float(row["credit_limit"]) if row and row.get("credit_limit") else 0.0

    def _exposure(self, customer_id: str, exclude_order: Optional[str] = None) -> float:
        return float(self.db.execute(
            text("SELECT COALESCE(SUM(total_amount),0) FROM domain_crm.sales_orders "
                 "WHERE customer_id = :cid AND tenant_id = :t AND deleted_at IS NULL "
                 "AND status NOT IN ('storniert','abgeschlossen','invoiced') "
                 "AND (:ex IS NULL OR order_number <> :ex)"),
            {"cid": customer_id, "t": self.tenant_id, "ex": exclude_order},
        ).scalar() or 0.0)

    def _order(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, order_number, customer_id, customer_name, status, total_amount "
                 "FROM domain_crm.sales_orders WHERE tenant_id = :t "
                 "AND (id::text = :v OR order_number = :v) AND deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _billing(self, order_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT delivery_note_number, invoice_number, status, delivery_date "
                 "FROM domain_sales.delivery_notes WHERE sales_order_id::text = :oid AND tenant_id = :t "
                 "ORDER BY delivery_date"),
            {"oid": order_id, "t": self.tenant_id},
        ).mappings().all()
        return [{"lieferschein": r["delivery_note_number"], "rechnung": r["invoice_number"],
                 "billing_status": "berechnet" if r["invoice_number"] else "offen",
                 "datum": r["delivery_date"].isoformat() if r["delivery_date"] else None}
                for r in rows]

    def order_credit(self, ref: str) -> dict[str, Any]:
        order = self._order(ref)
        if not order:
            return {"found": False, "detail": "Auftrag nicht auflösbar."}
        cid = order["customer_id"]
        limit = self._limit(cid)
        exposure_andere = self._exposure(cid, exclude_order=order["order_number"])
        betrag = float(order["total_amount"] or 0)
        credit = credit_check(limit, exposure_andere, betrag=betrag)
        billing = self._billing(str(order["id"]))
        offen_billing = sum(1 for b in billing if b["billing_status"] == "offen")
        return {
            "found": True,
            "order_number": order["order_number"],
            "kunde": order.get("customer_name"),
            "customer_id": cid,
            "auftrag_betrag": round(betrag, 2),
            "kredit": credit,
            "billing": billing,
            "summary": {
                "ampel": credit["ampel"],
                "verfuegbar": credit["verfuegbar"],
                "lieferscheine": len(billing),
                "offen_unberechnet": offen_billing,
            },
        }

    def list_customers(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT o.customer_id, MAX(o.customer_name) AS kunde,
                       COALESCE(SUM(o.total_amount),0) AS exposure, count(*) AS auftraege
                FROM domain_crm.sales_orders o
                WHERE o.tenant_id = :t AND o.deleted_at IS NULL
                  AND o.status NOT IN ('storniert','abgeschlossen','invoiced')
                GROUP BY o.customer_id ORDER BY exposure DESC LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        out = []
        for r in rows:
            kl = self._limit(r["customer_id"])
            c = credit_check(kl, float(r["exposure"] or 0))
            out.append({"customer_id": r["customer_id"], "kunde": r["kunde"],
                        "auftraege": int(r["auftraege"]), **c})
        return out
