"""DATEV-Export (DOM-FIN-004.5).

Exportiert offene Posten als vereinfachten DATEV-Buchungsstapel-CSV (Umsatz, Soll/
Haben, Konto/Gegenkonto, Belegdatum, Belegfeld1, Buchungstext). Bewusst KEIN
zertifizierter EXTF-Header — dient als prüfbarer Übergabe-/Cutover-Vertrag; die
finale Steuerberater-/DATEV-Abnahme bleibt ein externes Gate.

Default-Konten (SKR03): Debitoren 1400 / Erlöse 8400; Kreditoren 1600 / Aufwand 3400.
Reine Formatierung ist DB-frei testbar.
"""

from __future__ import annotations

import csv
import io
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

DATEV_HEADER = ["Umsatz", "Soll/Haben", "Konto", "Gegenkonto", "Belegdatum",
                "Belegfeld1", "Buchungstext", "Währung"]

_KONTEN = {
    "debitoren": {"konto": "1400", "gegen": "8400", "sh": "S"},
    "kreditoren": {"konto": "1600", "gegen": "3400", "sh": "H"},
}


def datev_row(offen, konto_typ: str, belegdatum, belegfeld1, buchungstext, waehrung="EUR") -> list:
    """Reine DATEV-Buchungszeile (eine OP-Position)."""
    kt = (konto_typ or "debitoren").lower()
    kfg = _KONTEN.get("kreditoren" if kt.startswith("kredit") else "debitoren")
    umsatz = Decimal(str(offen or 0)).quantize(Decimal("0.01"))
    return [
        f"{umsatz:.2f}".replace(".", ","),  # DATEV: Dezimalkomma
        kfg["sh"], kfg["konto"], kfg["gegen"],
        belegdatum.strftime("%d%m%Y") if hasattr(belegdatum, "strftime") else (belegdatum or ""),
        belegfeld1 or "", (buchungstext or "")[:60], waehrung or "EUR",
    ]


def datev_csv(rows: list[list]) -> str:
    """Rendert Zeilen als DATEV-Buchungsstapel-CSV (Semikolon, Header)."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\n")
    w.writerow(DATEV_HEADER)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


class FinanceDatevService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def export_open_items(self, typ: str = "alle") -> dict:
        typ_norm = (typ or "alle").lower()
        konto = None
        if typ_norm.startswith("debit"):
            konto = "debitoren"
        elif typ_norm.startswith("kredit"):
            konto = "kreditoren"
        rows = self.db.execute(
            text("SELECT rechnungsnr, rechnungsdatum, konto_typ, kunde_name, lieferant_name, "
                 "COALESCE(waehrung,'EUR') AS waehrung, COALESCE(offen, open_amount, betrag) AS offen "
                 "FROM domain_erp.offene_posten WHERE tenant_id = :t "
                 "AND COALESCE(op_status,'') <> 'storniert' "
                 "AND COALESCE(offen, open_amount, betrag, 0) > 0 "
                 "AND (:konto IS NULL OR konto_typ = :konto) "
                 "ORDER BY rechnungsdatum NULLS LAST"),
            {"t": self.tenant_id, "konto": konto},
        ).mappings().all()
        datev_rows = [
            datev_row(r["offen"], r["konto_typ"], r["rechnungsdatum"], r["rechnungsnr"],
                      r["kunde_name"] or r["lieferant_name"], r["waehrung"])
            for r in rows
        ]
        summe = sum((Decimal(str(r["offen"] or 0)) for r in rows), Decimal("0"))
        return {
            "filename": f"DATEV_Buchungsstapel_{typ_norm}.csv",
            "zeilen": len(datev_rows),
            "summe": float(summe),
            "csv": datev_csv(datev_rows),
        }

    # ── INT-DATEV-001: Journal-Export mit KOST1/KOST2 ────────────────────────

    DATEV_JOURNAL_HEADER = [
        "Umsatz", "Soll/Haben", "Konto", "Gegenkonto",
        "Belegdatum", "Belegfeld1", "Buchungstext", "Währung",
        "KOST1", "KOST2", "Periode",
    ]

    def export_journal(self, periode_von: str, periode_bis: str) -> dict:
        """Exportiert Journal-Einträge als DATEV-EXTF-kompatibler Buchungsstapel
        (vereinfacht; KOST1/KOST2 aus kostenstelle_id wenn vorhanden).

        periode_von / periode_bis: YYYY-MM Format.
        """
        rows = self.db.execute(
            text("""
                SELECT
                    jel.debit_amount,
                    jel.credit_amount,
                    jel.account_id,
                    jel.description,
                    je.entry_date,
                    je.entry_number,
                    je.description AS je_desc,
                    COALESCE(je.period, LEFT(je.entry_date::text, 7)) AS periode,
                    jel.cost_center_id
                FROM domain_erp.journal_entries je
                JOIN domain_erp.journal_entry_lines jel ON jel.journal_entry_id = je.id
                WHERE je.tenant_id = :tid
                  AND je.status = 'posted'
                  AND LEFT(je.entry_date::text, 7) BETWEEN :von AND :bis
                ORDER BY je.entry_date, je.sequence_number, jel.id
            """),
            {"tid": self.tenant_id, "von": periode_von, "bis": periode_bis},
        ).mappings().all()

        datev_rows: list[list] = []
        total_debit = Decimal("0")

        for r in rows:
            debit = Decimal(str(r["debit_amount"] or 0))
            credit = Decimal(str(r["credit_amount"] or 0))
            is_debit = debit > Decimal("0")
            betrag = debit if is_debit else credit
            if betrag <= Decimal("0"):
                continue
            total_debit += betrag if is_debit else Decimal("0")

            entry_date = r["entry_date"]
            belegdatum = (
                entry_date.strftime("%d%m%Y")
                if hasattr(entry_date, "strftime")
                else str(entry_date or "")[:10].replace("-", "")
            )

            datev_rows.append([
                f"{betrag:.2f}".replace(".", ","),
                "S" if is_debit else "H",
                str(r["account_id"] or "")[:13],
                "",  # Gegenkonto — aus Buchungssatz komplex; vereinfacht leer
                belegdatum,
                str(r["entry_number"] or "")[:36],
                (str(r["description"] or r["je_desc"] or ""))[:60],
                "EUR",
                str(r["cost_center_id"] or "")[:36],  # KOST1
                "",  # KOST2 — Kostenträger, ggf. erweiterbar
                str(r["periode"] or ""),
            ])

        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";", lineterminator="\n")
        w.writerow(self.DATEV_JOURNAL_HEADER)
        for row in datev_rows:
            w.writerow(row)

        return {
            "filename": f"DATEV_Journal_{periode_von}_{periode_bis}.csv",
            "zeilen": len(datev_rows),
            "summe_debit": float(total_debit),
            "csv": buf.getvalue(),
        }
