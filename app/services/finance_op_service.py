"""Offene-Posten-Cockpit / OP-Aging (DOM-FIN-004).

Read-only Sicht auf domain_erp.offene_posten: offene Beträge mit Fälligkeit,
Überfälligkeit, Aging-Buckets (nicht fällig / 1–30 / 31–60 / 60+) und aktivem
Skonto-Fenster. Basis für Mahnwesen/Zahlungsdisposition. Keine Schreibvorgänge.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

BUCKETS = ["nicht_faellig", "1-30", "31-60", "60+"]


def aging_bucket(faelligkeit: Optional[date], today: date) -> tuple[str, int]:
    """Reine Aging-Einstufung. Liefert (bucket, tage_ueberfaellig)."""
    if not faelligkeit:
        return ("nicht_faellig", 0)
    tage = (today - faelligkeit).days
    if tage <= 0:
        return ("nicht_faellig", 0)
    if tage <= 30:
        return ("1-30", tage)
    if tage <= 60:
        return ("31-60", tage)
    return ("60+", tage)


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


class FinanceOpService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def list_open_items(self, typ: str = "alle", limit: int = 500) -> dict:
        # Kontotyp-Filter: debitor(en) / kreditor(en) / alle.
        typ_norm = (typ or "alle").lower()
        konto = None
        if typ_norm.startswith("debit"):
            konto = "debitoren"
        elif typ_norm.startswith("kredit"):
            konto = "kreditoren"

        rows = self.db.execute(
            text(
                "SELECT rechnungsnr, rechnungsdatum, COALESCE(faelligkeit, due_date) AS faellig, "
                "konto_typ, kunde_name, lieferant_name, waehrung, betrag, "
                "COALESCE(offen, open_amount, betrag) AS offen, op_status, dunning_level, "
                "skonto_prozent, skonto_bis "
                "FROM domain_erp.offene_posten "
                "WHERE tenant_id = :t AND COALESCE(op_status,'') <> 'storniert' "
                "AND COALESCE(offen, open_amount, betrag, 0) > 0 "
                "AND (:konto IS NULL OR konto_typ = :konto) "
                "ORDER BY COALESCE(faelligkeit, due_date) NULLS LAST LIMIT :lim"
            ),
            {"t": self.tenant_id, "konto": konto, "lim": max(1, min(limit, 2000))},
        ).mappings().all()

        today = date.today()
        items = []
        sums = {b: Decimal("0") for b in BUCKETS}
        counts = {b: 0 for b in BUCKETS}
        total_offen = Decimal("0")
        total_ueberfaellig = Decimal("0")
        for r in rows:
            offen = Decimal(str(r["offen"] or 0))
            bucket, tage = aging_bucket(r["faellig"], today)
            skonto_aktiv = bool(r["skonto_bis"] and r["skonto_bis"] >= today)
            items.append({
                "rechnungsnr": r["rechnungsnr"],
                "rechnungsdatum": r["rechnungsdatum"].isoformat() if r["rechnungsdatum"] else None,
                "faelligkeit": r["faellig"].isoformat() if r["faellig"] else None,
                "konto_typ": r["konto_typ"],
                "partner": r["kunde_name"] or r["lieferant_name"],
                "waehrung": r["waehrung"] or "EUR",
                "betrag": _f(r["betrag"]),
                "offen": _f(offen),
                "bucket": bucket,
                "tage_ueberfaellig": tage,
                "ueberfaellig": tage > 0,
                "mahnstufe": int(r["dunning_level"] or 0),
                "skonto_aktiv": skonto_aktiv,
                "skonto_prozent": _f(r["skonto_prozent"]),
                "skonto_bis": r["skonto_bis"].isoformat() if r["skonto_bis"] else None,
            })
            sums[bucket] += offen
            counts[bucket] += 1
            total_offen += offen
            if tage > 0:
                total_ueberfaellig += offen

        return {
            "items": items,
            "summary": {
                "anzahl": len(items),
                "summe_offen": _f(total_offen),
                "summe_ueberfaellig": _f(total_ueberfaellig),
                "buckets": [{"bucket": b, "anzahl": counts[b], "summe": _f(sums[b])} for b in BUCKETS],
            },
        }
