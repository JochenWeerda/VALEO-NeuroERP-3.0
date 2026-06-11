"""Kontrakt-Settlement-Übergabe & Storno (DOM-CON-004.4).

Übergabe einer Abruf-Bewegung an die Abrechnung (``is_invoiced``/``invoice_no``/
``settled_at``) sowie Storno von Bewegungen (frei werdender Abruf) und Fixierungen
(frei werdende Fixiermenge). Fail-closed: bereits abgerechnete Bewegungen blockieren
den Storno (zuerst Abrechnung stornieren).

Stornierte Bewegungen (``is_storniert``) zählen nicht mehr als abgerufen — die
Erfüllungs-/Engagement-Sichten filtern sie entsprechend.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class SettlementError(Exception):
    """Fachlicher Fehler bei Settlement/Storno (→ HTTP 422)."""


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def _iso(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


def movement_state(is_storniert: bool, is_invoiced: bool) -> str:
    """Reine Zustandsableitung einer Abruf-Bewegung."""
    if is_storniert:
        return "storniert"
    if is_invoiced:
        return "abgerechnet"
    return "offen"


class ContractSettlementService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _contract(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT contract_id, contract_no, unit FROM domain_ops.kon_contract "
                 "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _movement(self, movement_id: str) -> dict:
        r = self.db.execute(
            text("SELECT movement_id, contract_id, line_id, quantity, is_invoiced, "
                 "COALESCE(is_storniert,false) AS is_storniert, invoice_no "
                 "FROM domain_ops.kon_contract_movement "
                 "WHERE movement_id::text = :id AND tenant_id = :t LIMIT 1"),
            {"id": movement_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            raise SettlementError(f"Bewegung nicht gefunden: {movement_id}")
        return dict(r)

    # ── Übergabe Bewegung → Abrechnung ────────────────────────────────────────────
    def handover(self, contract_ref: str, movement_id: Optional[str] = None,
                 invoice_no: Optional[str] = None, bediener: str = "KIM") -> dict:
        c = self._contract(contract_ref)
        if not c:
            raise SettlementError(f"Kontrakt nicht gefunden: {contract_ref}")
        if movement_id:
            m = self._movement(movement_id)
            if str(m["contract_id"]) != str(c["contract_id"]):
                raise SettlementError("Bewegung gehört nicht zu diesem Kontrakt.")
            if m["is_storniert"]:
                raise SettlementError("Stornierte Bewegung kann nicht abgerechnet werden.")
            if m["is_invoiced"]:
                raise SettlementError("Bewegung ist bereits abgerechnet.")
            targets = [m]
        else:
            rows = self.db.execute(
                text("SELECT movement_id, quantity FROM domain_ops.kon_contract_movement "
                     "WHERE contract_id::text = :cid AND tenant_id = :t "
                     "AND is_invoiced = false AND COALESCE(is_storniert,false) = false "
                     "ORDER BY movement_date"),
                {"cid": str(c["contract_id"]), "t": self.tenant_id},
            ).mappings().all()
            targets = [dict(r) for r in rows]
        if not targets:
            raise SettlementError("Keine offenen Bewegungen zur Übergabe.")

        settled = []
        for i, m in enumerate(targets, start=1):
            inv = invoice_no or f"ABR-{c['contract_no']}-{i}"
            self.db.execute(
                text("UPDATE domain_ops.kon_contract_movement "
                     "SET is_invoiced = true, invoice_no = :inv, settled_at = now() "
                     "WHERE movement_id = :id AND tenant_id = :t"),
                {"inv": inv, "id": m["movement_id"], "t": self.tenant_id},
            )
            settled.append({"movement_id": str(m["movement_id"]), "menge": _f(m["quantity"]), "invoice_no": inv})
        self.db.commit()
        return {"ok": True, "contract_no": c["contract_no"], "uebergeben": len(settled), "bewegungen": settled}

    # ── Storno ────────────────────────────────────────────────────────────────────
    def storno_movement(self, movement_id: str, grund: str, bediener: str = "KIM") -> dict:
        if not (grund or "").strip():
            raise SettlementError("Storno-Grund ist erforderlich.")
        m = self._movement(movement_id)
        if m["is_invoiced"]:
            raise SettlementError("Bewegung ist bereits abgerechnet — bitte zuerst die Abrechnung stornieren.")
        if m["is_storniert"]:
            raise SettlementError("Bewegung ist bereits storniert.")
        self.db.execute(
            text("UPDATE domain_ops.kon_contract_movement "
                 "SET is_storniert = true, storno_grund = :g, is_archived = true "
                 "WHERE movement_id = :id AND tenant_id = :t"),
            {"g": grund, "id": movement_id, "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "movement_id": movement_id, "frei_menge": _f(m["quantity"]), "status": "storniert"}

    def storno_fixing(self, fixing_id: str, grund: str, bediener: str = "KIM") -> dict:
        if not (grund or "").strip():
            raise SettlementError("Storno-Grund ist erforderlich.")
        r = self.db.execute(
            text("SELECT fixing_id, quantity, COALESCE(is_storniert,false) AS is_storniert "
                 "FROM domain_ops.kon_contract_fixing WHERE fixing_id::text = :id AND tenant_id = :t LIMIT 1"),
            {"id": fixing_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            raise SettlementError(f"Fixierung nicht gefunden: {fixing_id}")
        if r["is_storniert"]:
            raise SettlementError("Fixierung ist bereits storniert.")
        self.db.execute(
            text("UPDATE domain_ops.kon_contract_fixing "
                 "SET is_storniert = true, storniert_grund = :g WHERE fixing_id = :id AND tenant_id = :t"),
            {"g": grund, "id": fixing_id, "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "fixing_id": fixing_id, "frei_menge": _f(r["quantity"]), "status": "storniert"}

    # ── Status ────────────────────────────────────────────────────────────────────
    def settlement_status(self, contract_ref: str) -> dict:
        c = self._contract(contract_ref)
        if not c:
            return {"found": False, "detail": "Kontrakt nicht gefunden."}
        cid = str(c["contract_id"])
        movements = self.db.execute(
            text("SELECT movement_id, line_id, quantity, movement_date, invoice_no, settled_at, "
                 "is_invoiced, COALESCE(is_storniert,false) AS is_storniert, storno_grund "
                 "FROM domain_ops.kon_contract_movement WHERE contract_id::text = :cid AND tenant_id = :t "
                 "ORDER BY movement_date"),
            {"cid": cid, "t": self.tenant_id},
        ).mappings().all()
        fixings = self.db.execute(
            text("SELECT fixing_id, fixing_no, quantity, effective_price, "
                 "COALESCE(is_storniert,false) AS is_storniert, storniert_grund "
                 "FROM domain_ops.kon_contract_fixing WHERE contract_id::text = :cid AND tenant_id = :t "
                 "ORDER BY fixing_no"),
            {"cid": cid, "t": self.tenant_id},
        ).mappings().all()

        bewegungen = []
        abgerufen = Decimal("0")
        abgerechnet = Decimal("0")
        for m in movements:
            st = movement_state(bool(m["is_storniert"]), bool(m["is_invoiced"]))
            q = Decimal(str(m["quantity"] or 0))
            if st != "storniert":
                abgerufen += q
                if st == "abgerechnet":
                    abgerechnet += q
            bewegungen.append({
                "movement_id": str(m["movement_id"]), "menge": _f(q), "datum": _iso(m["movement_date"]),
                "status": st, "invoice_no": m["invoice_no"], "settled_at": _iso(m["settled_at"]),
                "storno_grund": m["storno_grund"],
            })
        fix = []
        fixiert_aktiv = Decimal("0")
        for f in fixings:
            storno = bool(f["is_storniert"])
            if not storno:
                fixiert_aktiv += Decimal(str(f["quantity"] or 0))
            fix.append({
                "fixing_no": f["fixing_no"], "menge": _f(f["quantity"]),
                "effektiv_preis": _f(f["effective_price"]),
                "status": "storniert" if storno else "aktiv",
                "fixing_id": str(f["fixing_id"]), "storno_grund": f["storniert_grund"],
            })

        return {
            "found": True,
            "contract_no": c["contract_no"],
            "einheit": c["unit"],
            "bewegungen": bewegungen,
            "fixierungen": fix,
            "summary": {
                "abgerufen": _f(abgerufen),
                "abgerechnet": _f(abgerechnet),
                "offen_abruf": _f(abgerufen - abgerechnet),
                "fixiert_aktiv": _f(fixiert_aktiv),
            },
        }
