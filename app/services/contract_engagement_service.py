"""Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3).

Engagement = offene (noch nicht abgerufene) Kontraktmenge, aggregiert je Artikel
(Netto-Position Einkauf − Verkauf) und je Partei. Read-only über
domain_ops.kon_contract(_line/_movement).

Kontraktmahnung = überfällig-untererfüllte Kontrakte (valid_to < heute, offen > 0)
als Mahnkandidaten; Mahnungen werden append-only in kon_contract_reminder erfasst.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class ReminderError(Exception):
    """Fachlicher Fehler bei einer Kontraktmahnung (→ HTTP 422)."""


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def _iso(v):
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return v


# ── Reine Aggregationslogik (ohne DB, testbar) ───────────────────────────────────
def netto_position(einkauf_offen, verkauf_offen) -> Decimal:
    """Netto-Engagement je Artikel: Einkauf offen − Verkauf offen (kann negativ sein)."""
    return Decimal(str(einkauf_offen or 0)) - Decimal(str(verkauf_offen or 0))


def offen_menge(qty_contract, abgerufen) -> Decimal:
    """Offene Kontraktmenge (nie negativ)."""
    o = Decimal(str(qty_contract or 0)) - Decimal(str(abgerufen or 0))
    return o if o > 0 else Decimal("0")


def naechste_mahnstufe(letzte: Optional[int]) -> int:
    """Nächste Mahnstufe (1, 2, 3 …); deckelt nicht — Eskalation bleibt sichtbar."""
    return (int(letzte) + 1) if letzte else 1


class ContractEngagementService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _line_rows(self) -> list[dict]:
        """Je Position: Artikel, Typ, Partei, kontrahiert, abgerufen (Summe Bewegungen)."""
        rows = self.db.execute(
            text(
                """
                SELECT c.contract_id, c.contract_no, c.contract_type, c.party_id, c.unit,
                       c.valid_to, l.line_id, l.article_id, l.qty_contract,
                       COALESCE((SELECT SUM(m.quantity) FROM domain_ops.kon_contract_movement m
                                 WHERE m.line_id = l.line_id AND m.tenant_id = c.tenant_id),0) AS abgerufen
                FROM domain_ops.kon_contract c
                JOIN domain_ops.kon_contract_line l
                  ON l.contract_id = c.contract_id AND l.tenant_id = c.tenant_id
                WHERE c.tenant_id = :t AND COALESCE(c.status,'') <> 'storniert'
                """
            ),
            {"t": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def engagement(self) -> dict:
        rows = self._line_rows()
        by_article: dict[str, dict] = {}
        by_party: dict[str, dict] = {}
        sum_ek = Decimal("0")
        sum_vk = Decimal("0")
        for r in rows:
            typ = (r["contract_type"] or "").upper()
            offen = offen_menge(r["qty_contract"], r["abgerufen"])
            if offen <= 0:
                continue
            art = r["article_id"] or "—"
            a = by_article.setdefault(art, {"artikel": art, "einkauf_offen": Decimal("0"),
                                            "verkauf_offen": Decimal("0"), "kontrakte": set()})
            if typ == "EINKAUF":
                a["einkauf_offen"] += offen
                sum_ek += offen
            elif typ == "VERKAUF":
                a["verkauf_offen"] += offen
                sum_vk += offen
            a["kontrakte"].add(r["contract_no"])

            p = r["party_id"] or "—"
            pp = by_party.setdefault(p, {"party_id": p, "offen": Decimal("0"), "kontrakte": set()})
            pp["offen"] += offen
            pp["kontrakte"].add(r["contract_no"])

        artikel = sorted(
            ({
                "artikel": a["artikel"],
                "einkauf_offen": _f(a["einkauf_offen"]),
                "verkauf_offen": _f(a["verkauf_offen"]),
                "netto": _f(netto_position(a["einkauf_offen"], a["verkauf_offen"])),
                "kontrakte": len(a["kontrakte"]),
            } for a in by_article.values()),
            key=lambda x: -abs(x["netto"]),
        )
        parteien = sorted(
            ({"party_id": p["party_id"], "offen": _f(p["offen"]), "kontrakte": len(p["kontrakte"])}
             for p in by_party.values()),
            key=lambda x: -x["offen"],
        )
        return {
            "by_article": artikel,
            "by_party": parteien,
            "summary": {
                "einkauf_offen": _f(sum_ek),
                "verkauf_offen": _f(sum_vk),
                "netto": _f(sum_ek - sum_vk),
                "artikel_anzahl": len(artikel),
                "parteien_anzahl": len(parteien),
            },
        }

    # ── Kontraktmahnung ───────────────────────────────────────────────────────────
    def _contract_open(self, contract_id: str) -> Decimal:
        rows = self.db.execute(
            text(
                """
                SELECT l.qty_contract,
                       COALESCE((SELECT SUM(m.quantity) FROM domain_ops.kon_contract_movement m
                                 WHERE m.line_id = l.line_id AND m.tenant_id = :t
                                 AND COALESCE(m.is_storniert,false) = false),0) AS abgerufen
                FROM domain_ops.kon_contract_line l
                WHERE l.contract_id::text = :cid AND l.tenant_id = :t
                """
            ),
            {"cid": contract_id, "t": self.tenant_id},
        ).mappings().all()
        return sum((offen_menge(r["qty_contract"], r["abgerufen"]) for r in rows), Decimal("0"))

    def _last_stufe(self, contract_id: str) -> Optional[int]:
        return self.db.execute(
            text("SELECT MAX(mahnstufe) FROM domain_ops.kon_contract_reminder "
                 "WHERE contract_id::text = :cid AND tenant_id = :t"),
            {"cid": contract_id, "t": self.tenant_id},
        ).scalar()

    def dunning_candidates(self) -> list[dict]:
        today = date.today()
        contracts = self.db.execute(
            text(
                "SELECT contract_id, contract_no, contract_type, party_id, unit, valid_to "
                "FROM domain_ops.kon_contract WHERE tenant_id = :t AND COALESCE(status,'') <> 'storniert' "
                "AND valid_to IS NOT NULL AND valid_to < :today ORDER BY valid_to"
            ),
            {"t": self.tenant_id, "today": datetime.now()},
        ).mappings().all()
        out = []
        for c in contracts:
            offen = self._contract_open(str(c["contract_id"]))
            if offen <= 0:
                continue
            valid_to = c["valid_to"].date() if isinstance(c["valid_to"], datetime) else c["valid_to"]
            last = self._last_stufe(str(c["contract_id"]))
            out.append({
                "contract_no": c["contract_no"], "typ": c["contract_type"], "party_id": c["party_id"],
                "einheit": c["unit"], "valid_to": _iso(c["valid_to"]),
                "tage_ueberfaellig": (today - valid_to).days if valid_to else None,
                "offen": _f(offen), "letzte_mahnstufe": last, "naechste_mahnstufe": naechste_mahnstufe(last),
            })
        return out

    def create_reminder(self, contract_ref: str, text_body: Optional[str] = None,
                        mahnstufe: Optional[int] = None, bediener: str = "KIM") -> dict:
        c = self.db.execute(
            text("SELECT contract_id, contract_no, valid_to FROM domain_ops.kon_contract "
                 "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"),
            {"t": self.tenant_id, "v": contract_ref},
        ).mappings().first()
        if not c:
            raise ReminderError(f"Kontrakt nicht gefunden: {contract_ref}")
        offen = self._contract_open(str(c["contract_id"]))
        if offen <= 0:
            raise ReminderError("Kontrakt ist vollständig erfüllt — keine Mahnung nötig.")
        stufe = int(mahnstufe) if mahnstufe else naechste_mahnstufe(self._last_stufe(str(c["contract_id"])))
        if stufe < 1:
            raise ReminderError("Mahnstufe muss ≥ 1 sein.")
        rid = str(uuid.uuid4())
        self.db.execute(
            text("INSERT INTO domain_ops.kon_contract_reminder "
                 "(reminder_id, contract_id, mahnstufe, offen_menge, text, bediener, tenant_id) "
                 "VALUES (:id, :cid, :st, :offen, :txt, :bed, :t)"),
            {"id": rid, "cid": str(c["contract_id"]), "st": stufe, "offen": offen,
             "txt": text_body, "bed": bediener, "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "reminder_id": rid, "contract_no": c["contract_no"],
                "mahnstufe": stufe, "offen": _f(offen)}

    def list_reminders(self, contract_ref: str) -> list[dict]:
        c = self.db.execute(
            text("SELECT contract_id FROM domain_ops.kon_contract "
                 "WHERE tenant_id = :t AND (contract_id::text = :v OR contract_no = :v) LIMIT 1"),
            {"t": self.tenant_id, "v": contract_ref},
        ).mappings().first()
        if not c:
            return []
        rows = self.db.execute(
            text("SELECT mahnstufe, offen_menge, text, bediener, created_at "
                 "FROM domain_ops.kon_contract_reminder WHERE contract_id::text = :cid AND tenant_id = :t "
                 "ORDER BY created_at DESC"),
            {"cid": str(c["contract_id"]), "t": self.tenant_id},
        ).mappings().all()
        return [{"mahnstufe": r["mahnstufe"], "offen": _f(r["offen_menge"]), "text": r["text"],
                 "bediener": r["bediener"], "datum": _iso(r["created_at"])} for r in rows]
