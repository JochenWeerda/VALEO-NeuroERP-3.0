"""Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2).

Erzeugt Mahnungen (domain_erp.dunning_notices) für überfällige Debitoren-OP
(domain_erp.offene_posten) und eskaliert die Mahnstufe (dunning_level). Mahn-
gebühren/Zinsen/Zahlungsfrist kommen aus dunning_rules; ist keine Regel hinterlegt,
greifen konservative Default-Regeln (fail-safe). Reine Mahnlogik ist DB-frei testbar.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# Default-Mahnstufen, falls domain_erp.dunning_rules leer ist.
_DEFAULT_RULES: dict[int, dict] = {
    1: {"fee_amount": 5.0, "interest_rate": 0.0, "payment_deadline_days": 14, "block": False},
    2: {"fee_amount": 10.0, "interest_rate": 5.0, "payment_deadline_days": 10, "block": False},
    3: {"fee_amount": 20.0, "interest_rate": 8.0, "payment_deadline_days": 7, "block": True},
}


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def days_based_level(tage_ueberfaellig: int) -> int:
    """Mahnstufe nach Überfälligkeit: 1–30→1, 31–60→2, 60+→3, sonst 0."""
    if tage_ueberfaellig <= 0:
        return 0
    if tage_ueberfaellig <= 30:
        return 1
    if tage_ueberfaellig <= 60:
        return 2
    return 3


def next_dunning_level(current_level: int, tage_ueberfaellig: int) -> int:
    """Nächste Mahnstufe: eskaliert gegenüber der aktuellen Stufe und der nach
    Überfälligkeit fälligen Stufe (gedeckelt bei 3). 0, wenn nicht überfällig."""
    if tage_ueberfaellig <= 0:
        return 0
    return min(max(int(current_level or 0) + 1, days_based_level(tage_ueberfaellig)), 3)


def compute_dunning(open_amount, level: int, rule: dict, tage_ueberfaellig: int) -> dict:
    """Reine Mahnbetrag-Berechnung: Gebühr + (anteilige) Zinsen + Gesamtbetrag."""
    offen = Decimal(str(open_amount or 0))
    fee = Decimal(str(rule.get("fee_amount", 0) or 0))
    zins_pa = Decimal(str(rule.get("interest_rate", 0) or 0))
    interest = (offen * zins_pa / 100 * Decimal(str(max(tage_ueberfaellig, 0))) / 365).quantize(Decimal("0.01"))
    total = (offen + fee + interest).quantize(Decimal("0.01"))
    return {
        "dunning_level": level,
        "dunning_fee": float(fee),
        "interest": float(interest),
        "total_amount": float(total),
        "payment_deadline_days": int(rule.get("payment_deadline_days", 14) or 14),
    }


class FinanceDunningService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _rules(self) -> dict[int, dict]:
        rows = self.db.execute(
            text("SELECT level, fee_amount, interest_rate, payment_deadline_days, block_customer "
                 "FROM domain_erp.dunning_rules WHERE tenant_id = :t AND COALESCE(active,true) = true"),
            {"t": self.tenant_id},
        ).mappings().all()
        rules = {int(r["level"]): {"fee_amount": _f(r["fee_amount"]), "interest_rate": _f(r["interest_rate"]),
                                   "payment_deadline_days": r["payment_deadline_days"],
                                   "block": bool(r["block_customer"])} for r in rows}
        return rules or dict(_DEFAULT_RULES)

    def _overdue_ops(self, rechnungsnr: Optional[str] = None) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, op_id_src, rechnungsnr, debtor_id, kunde_id, kunde_name, "
                "COALESCE(faelligkeit, due_date) AS faellig, "
                "COALESCE(offen, open_amount, betrag) AS offen, COALESCE(dunning_level,0) AS level "
                "FROM (SELECT *, id AS op_id_src FROM domain_erp.offene_posten) o "
                "WHERE tenant_id = :t AND konto_typ = 'debitoren' "
                "AND COALESCE(op_status,'') <> 'storniert' "
                "AND COALESCE(offen, open_amount, betrag, 0) > 0 "
                "AND COALESCE(faelligkeit, due_date) < CURRENT_DATE "
                "AND (:rnr IS NULL OR rechnungsnr = :rnr) "
                "ORDER BY COALESCE(faelligkeit, due_date)"
            ),
            {"t": self.tenant_id, "rnr": rechnungsnr},
        ).mappings().all()
        today = date.today()
        out = []
        for r in rows:
            faellig = r["faellig"]
            tage = (today - faellig).days if faellig else 0
            out.append({
                "op_id": str(r["op_id_src"]), "rechnungsnr": r["rechnungsnr"],
                "debtor_id": r["debtor_id"] or r["kunde_id"], "partner": r["kunde_name"],
                "faelligkeit": faellig.isoformat() if faellig else None,
                "tage_ueberfaellig": tage, "offen": _f(r["offen"]),
                "aktuelle_stufe": int(r["level"]), "naechste_stufe": next_dunning_level(int(r["level"]), tage),
            })
        return out

    def candidates(self) -> list[dict]:
        rules = self._rules()
        out = []
        for op in self._overdue_ops():
            lvl = op["naechste_stufe"]
            rule = rules.get(lvl, _DEFAULT_RULES.get(lvl, _DEFAULT_RULES[1]))
            calc = compute_dunning(op["offen"], lvl, rule, op["tage_ueberfaellig"])
            out.append({**op, **calc})
        return out

    def run_dunning(self, rechnungsnr: Optional[str] = None, bediener: str = "KIM") -> dict[str, Any]:
        rules = self._rules()
        ops = self._overdue_ops(rechnungsnr)
        if not ops:
            return {"ok": True, "erzeugt": 0, "mahnungen": [], "detail": "Keine überfälligen Debitoren-OP."}
        today = date.today()
        erzeugt = []
        for op in ops:
            lvl = op["naechste_stufe"]
            rule = rules.get(lvl, _DEFAULT_RULES.get(lvl, _DEFAULT_RULES[1]))
            calc = compute_dunning(op["offen"], lvl, rule, op["tage_ueberfaellig"])
            deadline = today + timedelta(days=calc["payment_deadline_days"])
            nid = str(uuid.uuid4())
            self.db.execute(
                text("INSERT INTO domain_erp.dunning_notices "
                     "(id, tenant_id, op_id, debtor_id, dunning_level, dunning_date, open_amount, "
                     "dunning_fee, interest, total_amount, payment_deadline, status, notes) "
                     "VALUES (:id, :t, :op, :deb, :lvl, :dd, :open, :fee, :int, :tot, :pd, 'offen', :notes)"),
                {"id": nid, "t": self.tenant_id, "op": op["op_id"], "deb": op["debtor_id"], "lvl": lvl,
                 "dd": today, "open": op["offen"], "fee": calc["dunning_fee"], "int": calc["interest"],
                 "tot": calc["total_amount"], "pd": deadline,
                 "notes": f"Mahnlauf {today.isoformat()} ({bediener}) zu {op['rechnungsnr']}"},
            )
            self.db.execute(
                text("UPDATE domain_erp.offene_posten SET dunning_level = :lvl "
                     "WHERE id = :id AND tenant_id = :t"),
                {"lvl": lvl, "id": op["op_id"], "t": self.tenant_id},
            )
            erzeugt.append({"rechnungsnr": op["rechnungsnr"], "stufe": lvl,
                            "gebuehr": calc["dunning_fee"], "zinsen": calc["interest"],
                            "gesamt": calc["total_amount"], "frist": deadline.isoformat()})
        self.db.commit()
        return {"ok": True, "erzeugt": len(erzeugt), "mahnungen": erzeugt}

    def list_notices(self, limit: int = 100) -> list[dict]:
        rows = self.db.execute(
            text("SELECT n.dunning_level, n.dunning_date, n.open_amount, n.dunning_fee, n.interest, "
                 "n.total_amount, n.payment_deadline, n.status, o.rechnungsnr, o.kunde_name "
                 "FROM domain_erp.dunning_notices n "
                 "LEFT JOIN domain_erp.offene_posten o ON o.id = n.op_id AND o.tenant_id = n.tenant_id "
                 "WHERE n.tenant_id = :t ORDER BY n.dunning_date DESC, n.dunning_level DESC LIMIT :lim"),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"stufe": r["dunning_level"], "datum": r["dunning_date"].isoformat() if r["dunning_date"] else None,
                 "offen": _f(r["open_amount"]), "gebuehr": _f(r["dunning_fee"]), "zinsen": _f(r["interest"]),
                 "gesamt": _f(r["total_amount"]), "frist": r["payment_deadline"].isoformat() if r["payment_deadline"] else None,
                 "status": r["status"], "rechnungsnr": r["rechnungsnr"], "partner": r["kunde_name"]} for r in rows]
