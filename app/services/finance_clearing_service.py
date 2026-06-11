"""Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3).

Erfasst einen Zahlungseingang gegen einen offenen Posten (domain_erp.offene_posten),
ziffert ihn aus (offene Menge reduzieren, optional Skonto) und protokolliert die
Auszifferung in domain_shared.op_auszifferungen. Schließt die Lücke der bestehenden
isolierten Skonto-Auszifferung, die den OP-Saldo im Aging-Cockpit nicht reduzierte.

Der Kreditoren-Zahlungslauf (SEPA) ist bereits über `payment_runs.py` abgedeckt und
wird hier nicht dupliziert.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_TOL = Decimal("0.01")


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def clearing_result(offen, zahlung, skonto_betrag=0) -> dict:
    """Reine Auszifferungs-Rechnung: Ausgleich (Zahlung + Skonto), Restsaldo, Status."""
    offen = Decimal(str(offen or 0))
    z = Decimal(str(zahlung or 0))
    sk = Decimal(str(skonto_betrag or 0))
    gesamt = z + sk
    neu = offen - gesamt
    return {
        "ausgleich": float(gesamt.quantize(Decimal("0.01"))),
        "neu_offen": float((neu if neu > 0 else Decimal("0")).quantize(Decimal("0.01"))),
        "voll_ausgeziffert": neu <= _TOL,
        "ueberzahlt": neu < -_TOL,
    }


class ClearingError(Exception):
    """Fachlicher Fehler bei der Auszifferung (→ HTTP 422)."""


class FinanceClearingService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _op(self, rechnungsnr: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, rechnungsnr, konto_typ, kunde_name, "
                 "COALESCE(offen, open_amount, betrag) AS offen, COALESCE(op_status,'offen') AS op_status "
                 "FROM domain_erp.offene_posten WHERE tenant_id = :t AND rechnungsnr = :r LIMIT 1"),
            {"t": self.tenant_id, "r": rechnungsnr},
        ).mappings().first()
        return dict(r) if r else None

    def record_payment(self, rechnungsnr: str, betrag: float, skonto_betrag: float = 0.0,
                       zahlungsdatum: Optional[date] = None, zahlungsart: str = "ueberweisung",
                       bediener: str = "KIM") -> dict[str, Any]:
        op = self._op(rechnungsnr)
        if not op:
            raise ClearingError(f"Offener Posten nicht gefunden: {rechnungsnr}")
        offen = Decimal(str(op["offen"] or 0))
        if offen <= 0:
            raise ClearingError("Posten ist bereits ausgeziffert.")
        if betrag is None or float(betrag) <= 0:
            raise ClearingError("Zahlungsbetrag muss größer 0 sein.")
        res = clearing_result(offen, betrag, skonto_betrag)
        if res["ueberzahlt"]:
            raise ClearingError(
                f"Ausgleich {res['ausgleich']:.2f} übersteigt offenen Betrag {float(offen):.2f}."
            )
        z = Decimal(str(betrag))
        sk = Decimal(str(skonto_betrag or 0))
        skonto_pct = (sk / offen * 100).quantize(Decimal("0.01")) if offen > 0 and sk > 0 else Decimal("0")
        today = zahlungsdatum or date.today()
        aid = str(uuid.uuid4())
        self.db.execute(
            text("INSERT INTO domain_shared.op_auszifferungen "
                 "(id, tenant_id, op_id, rechnungsnr, zahlungsdatum, zahlungsbetrag_eur, "
                 "skonto_betrag_eur, skonto_prozent, gesamtbetrag_eur, zahlungsart, buchungstext, "
                 "status, storniert) "
                 "VALUES (:id, :t, :op, :rnr, :zd, :zb, :sk, :skp, :ges, :za, :txt, "
                 ":st, false)"),
            {"id": aid, "t": self.tenant_id, "op": str(op["id"]), "rnr": rechnungsnr, "zd": today,
             "zb": z, "sk": sk, "skp": skonto_pct, "ges": Decimal(str(res["ausgleich"])),
             "za": zahlungsart, "txt": f"Zahlungseingang {rechnungsnr} ({bediener})",
             "st": "vollausgleich" if res["voll_ausgeziffert"] else "teilausgleich"},
        )
        new_status = "ausgeziffert" if res["voll_ausgeziffert"] else op["op_status"]
        self.db.execute(
            text("UPDATE domain_erp.offene_posten SET offen = :neu, op_status = :st "
                 "WHERE id = :id AND tenant_id = :t"),
            {"neu": Decimal(str(res["neu_offen"])), "st": new_status, "id": op["id"], "t": self.tenant_id},
        )
        self.db.commit()
        return {
            "ok": True,
            "rechnungsnr": rechnungsnr,
            "auszifferung_id": aid,
            "ausgleich": res["ausgleich"],
            "skonto": _f(sk),
            "neu_offen": res["neu_offen"],
            "voll_ausgeziffert": res["voll_ausgeziffert"],
            "op_status": new_status,
        }

    def clearings(self, rechnungsnr: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT zahlungsdatum, zahlungsbetrag_eur, skonto_betrag_eur, gesamtbetrag_eur, "
                 "zahlungsart, status, storniert FROM domain_shared.op_auszifferungen "
                 "WHERE tenant_id = :t AND rechnungsnr = :r ORDER BY zahlungsdatum DESC"),
            {"t": self.tenant_id, "r": rechnungsnr},
        ).mappings().all()
        return [{"datum": r["zahlungsdatum"].isoformat() if r["zahlungsdatum"] else None,
                 "betrag": _f(r["zahlungsbetrag_eur"]), "skonto": _f(r["skonto_betrag_eur"]),
                 "ausgleich": _f(r["gesamtbetrag_eur"]), "zahlungsart": r["zahlungsart"],
                 "status": r["status"], "storniert": bool(r["storniert"])} for r in rows]
