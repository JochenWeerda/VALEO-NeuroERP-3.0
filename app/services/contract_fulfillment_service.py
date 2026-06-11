"""Kontrakt-Erfüllungsstand (DOM-CON-004).

Read-only Sicht auf domain_ops.kon_contract(_line/_movement): je Kontrakt die
kontrahierte Menge vs. abgerufene/gelieferte Menge (Bewegungen) → Erfüllungsgrad,
offene Menge, Status (offen/teilerfüllt/erfüllt/übererfüllt) und Lücken
(überfällig untererfüllt; Übererfüllung ohne Erlaubnis). Basis für Engagement,
Abruf-Disposition und Kontraktmahnung. Keine Schreibvorgänge.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_TOLERANZ = Decimal("0.5")  # % Toleranz für „erfüllt"


def fulfillment_status(qty_contract: Decimal, abgerufen: Decimal,
                       allow_over: bool = False) -> dict:
    """Reine Erfüllungs-Einstufung einer Position/eines Kontrakts."""
    qty = Decimal(str(qty_contract or 0))
    ab = Decimal(str(abgerufen or 0))
    offen = qty - ab
    if qty <= 0:
        return {"status": "ohne_menge", "offen": float(offen), "erfuellung_pct": 0.0, "abweichung": False}
    pct = (ab / qty * 100).quantize(Decimal("0.01"))
    if ab <= 0:
        status = "offen"
    elif ab < qty * (1 - _TOLERANZ / 100):
        status = "teilerfuellt"
    elif ab > qty * (1 + _TOLERANZ / 100):
        status = "uebererfuellt"
    else:
        status = "erfuellt"
    return {
        "status": status,
        "offen": float(offen),
        "erfuellung_pct": float(pct),
        "abweichung": status == "uebererfuellt" and not allow_over,
    }


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def _iso(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


class ContractFulfillmentService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _contract(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT contract_id, contract_no, contract_type, party_id, valid_from, valid_to, "
                "total_quantity, unit, status, allow_overdelivery, pricing_model, premium_type, "
                "premium_value, min_price, basis_reference "
                "FROM domain_ops.kon_contract "
                "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"
            ),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _abgerufen_by_line(self, contract_id: str) -> dict[str, Decimal]:
        rows = self.db.execute(
            text("SELECT line_id, COALESCE(SUM(quantity),0) AS menge "
                 "FROM domain_ops.kon_contract_movement "
                 "WHERE contract_id::text = :cid AND tenant_id = :t "
                 "AND COALESCE(is_storniert,false) = false GROUP BY line_id"),
            {"cid": contract_id, "t": self.tenant_id},
        ).mappings().all()
        return {str(r["line_id"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def detail(self, ref: str) -> dict:
        c = self._contract(ref)
        if not c:
            return {"found": False, "detail": "Kontrakt nicht gefunden."}
        cid = str(c["contract_id"])
        lines = self.db.execute(
            text("SELECT line_id, position_no, article_id, description1, qty_contract, unit_price, is_matif "
                 "FROM domain_ops.kon_contract_line WHERE contract_id::text = :cid AND tenant_id = :t "
                 "ORDER BY position_no"),
            {"cid": cid, "t": self.tenant_id},
        ).mappings().all()
        abgerufen = self._abgerufen_by_line(cid)
        allow_over = bool(c["allow_overdelivery"])

        positionen = []
        sum_contract = Decimal("0")
        sum_ab = Decimal("0")
        for ln in lines:
            ab = abgerufen.get(str(ln["line_id"]), Decimal("0"))
            qc = Decimal(str(ln["qty_contract"] or 0))
            fs = fulfillment_status(qc, ab, allow_over)
            sum_contract += qc
            sum_ab += ab
            positionen.append({
                "position_no": ln["position_no"], "artikel": ln["article_id"],
                "bezeichnung": ln["description1"], "menge_kontrakt": _f(qc),
                "abgerufen": _f(ab), "is_matif": bool(ln["is_matif"]), **fs,
            })

        gesamt = fulfillment_status(sum_contract, sum_ab, allow_over)
        today = date.today()
        valid_to = c["valid_to"].date() if isinstance(c["valid_to"], datetime) else c["valid_to"]
        ueberfaellig = bool(valid_to and valid_to < today and gesamt["offen"] > 0)

        luecken = []
        if ueberfaellig:
            luecken.append({"schwere": "warnung",
                            "text": f"Kontrakt überfällig (gültig bis {valid_to}) mit offener Menge {gesamt['offen']:.0f} {c['unit'] or ''}."})
        for p in positionen:
            if p["abweichung"]:
                luecken.append({"schwere": "warnung",
                                "text": f"Position {p['position_no']} übererfüllt ohne Übermengen-Erlaubnis."})

        return {
            "found": True,
            "contract_no": c["contract_no"],
            "contract_type": c["contract_type"],
            "party_id": c["party_id"],
            "status": c["status"],
            "einheit": c["unit"],
            "valid_from": _iso(c["valid_from"]),
            "valid_to": _iso(c["valid_to"]),
            "ueberfaellig": ueberfaellig,
            "pricing": {"modell": c["pricing_model"], "praemie_typ": c["premium_type"],
                        "praemie_wert": _f(c["premium_value"]), "mindestpreis": _f(c["min_price"]),
                        "basis": c["basis_reference"]},
            "positionen": positionen,
            "luecken": luecken,
            "summary": {
                "menge_kontrakt": _f(sum_contract), "abgerufen": _f(sum_ab),
                "offen": gesamt["offen"], "erfuellung_pct": gesamt["erfuellung_pct"],
                "status": gesamt["status"], "offene_luecken": len(luecken),
            },
        }

    def list_contracts(self, typ: str = "alle", limit: int = 100) -> list[dict]:
        typ_norm = (typ or "alle").upper()
        ct = typ_norm if typ_norm in ("EINKAUF", "VERKAUF") else None
        rows = self.db.execute(
            text(
                """
                SELECT c.contract_no, c.contract_type, c.party_id, c.valid_to, c.unit, c.status,
                       COALESCE((SELECT SUM(l.qty_contract) FROM domain_ops.kon_contract_line l
                                 WHERE l.contract_id = c.contract_id AND l.tenant_id = c.tenant_id),0) AS qty,
                       COALESCE((SELECT SUM(m.quantity) FROM domain_ops.kon_contract_movement m
                                 WHERE m.contract_id = c.contract_id AND m.tenant_id = c.tenant_id
                                 AND COALESCE(m.is_storniert,false) = false),0) AS ab
                FROM domain_ops.kon_contract c
                WHERE c.tenant_id = :t AND (:ct IS NULL OR c.contract_type = :ct)
                ORDER BY c.valid_to NULLS LAST, c.contract_no LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "ct": ct, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        today = date.today()
        out = []
        for r in rows:
            fs = fulfillment_status(Decimal(str(r["qty"] or 0)), Decimal(str(r["ab"] or 0)))
            valid_to = r["valid_to"].date() if isinstance(r["valid_to"], datetime) else r["valid_to"]
            out.append({
                "contract_no": r["contract_no"], "typ": r["contract_type"], "party_id": r["party_id"],
                "einheit": r["unit"], "status": r["status"], "valid_to": _iso(r["valid_to"]),
                "menge_kontrakt": _f(r["qty"]), "abgerufen": _f(r["ab"]),
                "erfuellung_pct": fs["erfuellung_pct"], "erfuellung_status": fs["status"],
                "ueberfaellig": bool(valid_to and valid_to < today and fs["offen"] > 0),
            })
        return out
