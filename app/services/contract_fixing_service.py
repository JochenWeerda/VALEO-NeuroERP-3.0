"""Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2).

Arbeitsraum für die **Teilfixierung** MATIF-bepreister Kontrakte: je Position kann
die kontrahierte Menge in Tranchen zu einem MATIF-Preis (+ Prämie/Basis) fixiert
werden. Offen-zu-fixieren = kontrahiert − bereits fixiert. Mark-to-Market gegen die
jüngste Marktnotierung (``matif_quote``) bewertet den fixierten Anteil (realisierter
Vorteil/Nachteil je nach Einkauf/Verkauf) und den offenen Anteil (Marktwert).

Fixierungen sind append-only (``kon_contract_fixing``); Storno (``is_storniert``)
bleibt dem Folge-Slice 004.4 vorbehalten. Keine erfundenen Preise: fehlt eine
Notierung, wird die Bewertung als „keine Notierung" ausgewiesen (fail-closed).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_TOL = Decimal("0.001")  # Mengen-Toleranz (Rundung)


class FixingActionError(Exception):
    """Fachlicher Fehler bei einer Fixierung (→ HTTP 422)."""


# ── Reine Bewertungslogik (ohne DB, testbar) ─────────────────────────────────────
def effektiv_preis(matif_price, premium) -> Decimal:
    """Effektivpreis einer Tranche = MATIF-Preis + Prämie/Basis."""
    return Decimal(str(matif_price or 0)) + Decimal(str(premium or 0))


def restmenge(qty_contract, fixiert) -> Decimal:
    """Offen zu fixieren = kontrahiert − fixiert (nie negativ)."""
    offen = Decimal(str(qty_contract or 0)) - Decimal(str(fixiert or 0))
    return offen if offen > 0 else Decimal("0")


def mtm_fixiert(avg_eff, markt_eff, menge, einkauf: bool) -> Decimal:
    """Mark-to-Market des fixierten Anteils.

    Vorzeichenkonvention (positiv = vorteilhaft):
      • Einkauf: unter Markt fixiert ist gut → (Markt − Fix) · Menge.
      • Verkauf: über Markt fixiert ist gut → (Fix − Markt) · Menge.
    """
    sign = Decimal("1") if einkauf else Decimal("-1")
    delta = Decimal(str(markt_eff)) - Decimal(str(avg_eff))
    return (delta * Decimal(str(menge or 0)) * sign).quantize(Decimal("0.01"))


def marktwert_offen(offen, markt_eff) -> Decimal:
    """Marktwert des noch offenen (unfixierten) Anteils zum aktuellen Effektivpreis."""
    return (Decimal(str(offen or 0)) * Decimal(str(markt_eff))).quantize(Decimal("0.01"))


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def _iso(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


class ContractFixingService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Lesehilfen ────────────────────────────────────────────────────────────────
    def _contract(self, ref: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT contract_id, contract_no, contract_type, party_id, unit, status, "
                "premium_type, premium_value, basis_reference, pricing_model "
                "FROM domain_ops.kon_contract "
                "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"
            ),
            {"t": self.tenant_id, "v": ref},
        ).mappings().first()
        return dict(r) if r else None

    def _lines(self, contract_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT line_id, position_no, article_id, description1, qty_contract, is_matif "
                "FROM domain_ops.kon_contract_line WHERE contract_id::text = :cid AND tenant_id = :t "
                "ORDER BY position_no"
            ),
            {"cid": contract_id, "t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def _line(self, contract_id: str, line_ref: Optional[str]) -> dict:
        lines = self._lines(contract_id)
        if not lines:
            raise FixingActionError("Kontrakt hat keine Positionen.")
        if line_ref:
            for ln in lines:
                if str(ln["line_id"]) == str(line_ref) or str(ln["position_no"]) == str(line_ref):
                    return ln
            raise FixingActionError(f"Position nicht gefunden: {line_ref}")
        if len(lines) > 1:
            raise FixingActionError("Kontrakt hat mehrere Positionen — Position angeben.")
        return lines[0]

    def _fixings(self, contract_id: str, line_id: Optional[str] = None) -> list[dict]:
        sql = (
            "SELECT fixing_id, line_id, fixing_no, quantity, matif_price, premium, effective_price, "
            "matif_reference, fixing_date, note, bediener "
            "FROM domain_ops.kon_contract_fixing "
            "WHERE contract_id::text = :cid AND tenant_id = :t AND is_storniert = false "
        )
        params = {"cid": contract_id, "t": self.tenant_id}
        if line_id is not None:
            sql += "AND line_id::text = :lid "
            params["lid"] = str(line_id)
        sql += "ORDER BY fixing_no, fixing_date"
        return [dict(r) for r in self.db.execute(text(sql), params).mappings().all()]

    def _fixiert_menge(self, contract_id: str, line_id: str) -> Decimal:
        r = self.db.execute(
            text(
                "SELECT COALESCE(SUM(quantity),0) AS m FROM domain_ops.kon_contract_fixing "
                "WHERE contract_id::text = :cid AND line_id::text = :lid AND tenant_id = :t "
                "AND is_storniert = false"
            ),
            {"cid": contract_id, "lid": str(line_id), "t": self.tenant_id},
        ).scalar()
        return Decimal(str(r or 0))

    def _symbol_for(self, contract: dict, line: dict) -> str:
        return (contract.get("basis_reference") or line.get("article_id") or "").strip()

    def _latest_quote(self, symbol: str) -> Optional[dict]:
        if not symbol:
            return None
        r = self.db.execute(
            text(
                "SELECT symbol, quote_date, price, unit, source FROM domain_ops.matif_quote "
                "WHERE tenant_id = :t AND symbol = :s ORDER BY quote_date DESC LIMIT 1"
            ),
            {"t": self.tenant_id, "s": symbol},
        ).mappings().first()
        return dict(r) if r else None

    # ── Notierungen ───────────────────────────────────────────────────────────────
    def upsert_quote(self, symbol: str, quote_date, price: float, unit: Optional[str] = None,
                     source: str = "manual") -> dict:
        if not (symbol or "").strip():
            raise FixingActionError("Symbol ist erforderlich.")
        if price is None or float(price) <= 0:
            raise FixingActionError("Notierung (Preis) muss größer 0 sein.")
        qd = quote_date or date.today()
        self.db.execute(
            text(
                "INSERT INTO domain_ops.matif_quote (quote_id, symbol, quote_date, price, unit, source, tenant_id) "
                "VALUES (:id, :s, :d, :p, :u, :src, :t) "
                "ON CONFLICT (tenant_id, symbol, quote_date) DO UPDATE SET price = EXCLUDED.price, "
                "unit = EXCLUDED.unit, source = EXCLUDED.source"
            ),
            {"id": str(uuid.uuid4()), "s": symbol.strip(), "d": qd, "p": price,
             "u": unit, "src": source, "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "symbol": symbol.strip(), "quote_date": _iso(qd), "price": float(price)}

    # ── Fixierung anlegen ─────────────────────────────────────────────────────────
    def create_fixing(self, contract_ref: str, line_ref: Optional[str], quantity: float,
                      matif_price: float, premium: Optional[float] = None,
                      matif_reference: Optional[str] = None, note: Optional[str] = None,
                      bediener: str = "KIM") -> dict:
        c = self._contract(contract_ref)
        if not c:
            raise FixingActionError(f"Kontrakt nicht gefunden: {contract_ref}")
        line = self._line(str(c["contract_id"]), line_ref)
        if not bool(line["is_matif"]):
            raise FixingActionError(
                f"Position {line['position_no']} ist nicht MATIF-bepreist — Fixierung nur für MATIF-Kontrakte."
            )
        qty = Decimal(str(quantity or 0))
        if qty <= 0:
            raise FixingActionError("Fixiermenge muss größer 0 sein.")
        if matif_price is None or float(matif_price) <= 0:
            raise FixingActionError("MATIF-Preis muss größer 0 sein.")

        qty_contract = Decimal(str(line["qty_contract"] or 0))
        bereits = self._fixiert_menge(str(c["contract_id"]), str(line["line_id"]))
        offen = qty_contract - bereits
        if qty > offen + _TOL:
            raise FixingActionError(
                f"Fixiermenge {float(qty):.3f} übersteigt offene Menge {float(offen):.3f} "
                f"{c['unit'] or ''} (kontrahiert {float(qty_contract):.3f}, fixiert {float(bereits):.3f})."
            )

        prem = Decimal(str(premium if premium is not None else (c["premium_value"] or 0)))
        eff = effektiv_preis(matif_price, prem)
        next_no = self.db.execute(
            text("SELECT COALESCE(MAX(fixing_no),0)+1 FROM domain_ops.kon_contract_fixing "
                 "WHERE contract_id::text = :cid AND tenant_id = :t"),
            {"cid": str(c["contract_id"]), "t": self.tenant_id},
        ).scalar()
        fid = str(uuid.uuid4())
        self.db.execute(
            text(
                "INSERT INTO domain_ops.kon_contract_fixing "
                "(fixing_id, contract_id, line_id, fixing_no, quantity, matif_price, premium, "
                "effective_price, matif_reference, note, bediener, tenant_id) "
                "VALUES (:id, :cid, :lid, :no, :q, :mp, :pr, :eff, :ref, :note, :bed, :t)"
            ),
            {"id": fid, "cid": str(c["contract_id"]), "lid": str(line["line_id"]), "no": next_no,
             "q": qty, "mp": Decimal(str(matif_price)), "pr": prem, "eff": eff,
             "ref": matif_reference or c.get("basis_reference"), "note": note,
             "bed": bediener, "t": self.tenant_id},
        )
        self.db.commit()
        return {
            "ok": True,
            "fixing_id": fid,
            "fixing_no": next_no,
            "contract_no": c["contract_no"],
            "position_no": line["position_no"],
            "menge": _f(qty),
            "matif_price": float(matif_price),
            "praemie": _f(prem),
            "effektiv_preis": _f(eff),
            "offen_nach": _f(offen - qty),
        }

    # ── Arbeitsraum (Read) ────────────────────────────────────────────────────────
    def workspace(self, contract_ref: str) -> dict:
        c = self._contract(contract_ref)
        if not c:
            return {"found": False, "detail": "Kontrakt nicht gefunden."}
        cid = str(c["contract_id"])
        einkauf = (c["contract_type"] or "").upper() == "EINKAUF"
        prem_default = Decimal(str(c["premium_value"] or 0))

        positionen = []
        sum_contract = Decimal("0")
        sum_fixiert = Decimal("0")
        sum_bewertung = Decimal("0")
        sum_marktwert_offen = Decimal("0")
        bewertbar = False

        for ln in self._lines(cid):
            qc = Decimal(str(ln["qty_contract"] or 0))
            sum_contract += qc
            is_matif = bool(ln["is_matif"])
            fixings = self._fixings(cid, str(ln["line_id"])) if is_matif else []
            fixiert = sum((Decimal(str(f["quantity"] or 0)) for f in fixings), Decimal("0"))
            offen = restmenge(qc, fixiert)
            sum_fixiert += fixiert

            # Gewichteter Ø-Fixpreis (effektiv inkl. Prämie der jeweiligen Tranche).
            avg_eff = None
            if fixiert > 0:
                gewichtet = sum(
                    (Decimal(str(f["effective_price"] or 0)) * Decimal(str(f["quantity"] or 0))
                     for f in fixings), Decimal("0"))
                avg_eff = (gewichtet / fixiert).quantize(Decimal("0.0001"))

            symbol = self._symbol_for(c, ln) if is_matif else ""
            quote = self._latest_quote(symbol) if is_matif else None
            markt_eff = None
            bew_fix = None
            mw_offen = None
            if quote:
                bewertbar = True
                markt_eff = effektiv_preis(quote["price"], prem_default).quantize(Decimal("0.0001"))
                if avg_eff is not None and fixiert > 0:
                    bew_fix = mtm_fixiert(avg_eff, markt_eff, fixiert, einkauf)
                    sum_bewertung += bew_fix
                if offen > 0:
                    mw_offen = marktwert_offen(offen, markt_eff)
                    sum_marktwert_offen += mw_offen

            positionen.append({
                "position_no": ln["position_no"],
                "line_id": str(ln["line_id"]),
                "artikel": ln["article_id"],
                "bezeichnung": ln["description1"],
                "is_matif": is_matif,
                "menge_kontrakt": _f(qc),
                "fixiert": _f(fixiert),
                "offen_zu_fixieren": _f(offen if offen > 0 else Decimal("0")),
                "fixierungsgrad_pct": float((fixiert / qc * 100).quantize(Decimal("0.01"))) if qc > 0 else 0.0,
                "avg_fixpreis_effektiv": _f(avg_eff),
                "symbol": symbol or None,
                "notierung": {
                    "preis": _f(quote["price"]), "datum": _iso(quote["quote_date"]),
                    "markt_effektiv": _f(markt_eff), "quelle": quote.get("source"),
                } if quote else None,
                "bewertung_fixiert_eur": _f(bew_fix),
                "marktwert_offen_eur": _f(mw_offen),
                "fixings": [{
                    "fixing_no": f["fixing_no"], "menge": _f(f["quantity"]),
                    "matif_price": _f(f["matif_price"]), "praemie": _f(f["premium"]),
                    "effektiv_preis": _f(f["effective_price"]), "datum": _iso(f["fixing_date"]),
                    "referenz": f["matif_reference"], "notiz": f["note"], "bediener": f["bediener"],
                } for f in fixings],
            })

        offen_gesamt = sum_contract - sum_fixiert
        return {
            "found": True,
            "contract_no": c["contract_no"],
            "contract_type": c["contract_type"],
            "party_id": c["party_id"],
            "einheit": c["unit"],
            "status": c["status"],
            "pricing": {
                "modell": c["pricing_model"], "praemie_typ": c["premium_type"],
                "praemie_wert": _f(prem_default), "basis": c["basis_reference"],
            },
            "positionen": positionen,
            "summary": {
                "menge_kontrakt": _f(sum_contract),
                "fixiert": _f(sum_fixiert),
                "offen_zu_fixieren": _f(offen_gesamt if offen_gesamt > 0 else Decimal("0")),
                "fixierungsgrad_pct": float((sum_fixiert / sum_contract * 100).quantize(Decimal("0.01"))) if sum_contract > 0 else 0.0,
                "bewertbar": bewertbar,
                "bewertung_fixiert_eur": _f(sum_bewertung) if bewertbar else None,
                "marktwert_offen_eur": _f(sum_marktwert_offen) if bewertbar else None,
            },
        }

    def list_fixings(self, contract_ref: str) -> list[dict]:
        c = self._contract(contract_ref)
        if not c:
            return []
        out = []
        for f in self._fixings(str(c["contract_id"])):
            out.append({
                "fixing_no": f["fixing_no"], "line_id": str(f["line_id"]) if f["line_id"] else None,
                "menge": _f(f["quantity"]), "matif_price": _f(f["matif_price"]),
                "praemie": _f(f["premium"]), "effektiv_preis": _f(f["effective_price"]),
                "datum": _iso(f["fixing_date"]), "referenz": f["matif_reference"],
                "notiz": f["note"], "bediener": f["bediener"],
            })
        return out
