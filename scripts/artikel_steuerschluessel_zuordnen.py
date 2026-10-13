#!/usr/bin/env python3
"""Ordnet bestehenden Artikeln eines Mandanten Steuerschluessel zu — nur wo es eindeutig ist.

    python scripts/artikel_steuerschluessel_zuordnen.py --tenant <id>           # Trockenlauf
    python scripts/artikel_steuerschluessel_zuordnen.py --tenant <id> --apply   # schreiben

Ein Artikel mit ``mehrwertsteuer_prozent`` und ohne Schluessel bekommt den Verkaufs- bzw. Einkaufsschluessel,
wenn der Mandant fuer die Richtung **genau einen** gueltigen Schluessel mit diesem Satz hat. Gibt es keinen
oder mehrere, bleibt der Artikel offen und wird genannt — die Buchhaltung ordnet ihn in der Maske Artikelstamm zu.
Artikel ohne Satz bleiben unberuehrt: Es gibt keinen Vorgabewert.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.finance.steuerschluessel import schluessel_auswahl  # noqa: E402

FELD = {"verkauf": "steuerschluessel_verkauf", "einkauf": "steuerschluessel_einkauf"}


def zuordnen(db, tenant_id: str) -> tuple[Counter, list[str]]:
    """Setzt eindeutige Schluessel (ohne Commit). Rueckgabe: Zaehler je Feld, offene Faelle."""
    gesetzt: Counter = Counter()
    offen: list[str] = []
    for richtung, feld in FELD.items():
        je_satz: dict[Decimal, list[str]] = {}
        for wahl in schluessel_auswahl(db, tenant_id, richtung):
            je_satz.setdefault(wahl.steuersatz, []).append(wahl.code)
        if feld == "steuerschluessel_verkauf":
            sql_lesen = ("SELECT id, article_number, mehrwertsteuer_prozent FROM domain_inventory.articles "
                         "WHERE tenant_id = :t AND deleted_at IS NULL AND mehrwertsteuer_prozent IS NOT NULL "
                         "AND steuerschluessel_verkauf IS NULL ORDER BY article_number")
            sql_setzen = "UPDATE domain_inventory.articles SET steuerschluessel_verkauf = :code WHERE id = :id AND tenant_id = :t"
        else:
            sql_lesen = ("SELECT id, article_number, mehrwertsteuer_prozent FROM domain_inventory.articles "
                         "WHERE tenant_id = :t AND deleted_at IS NULL AND mehrwertsteuer_prozent IS NOT NULL "
                         "AND steuerschluessel_einkauf IS NULL ORDER BY article_number")
            sql_setzen = "UPDATE domain_inventory.articles SET steuerschluessel_einkauf = :code WHERE id = :id AND tenant_id = :t"
        for artikel_id, nummer, satz in db.execute(text(sql_lesen), {"t": tenant_id}).fetchall():
            codes = je_satz.get(Decimal(str(satz)), [])
            if len(codes) == 1:
                db.execute(text(sql_setzen), {"code": codes[0], "id": artikel_id, "t": tenant_id})
                gesetzt[feld] += 1
            else:
                grund = "kein Schluessel" if not codes else f"mehrere Schluessel ({', '.join(codes)})"
                offen.append(f"{nummer}: {richtung}, Satz {Decimal(str(satz)).normalize():f} % — {grund}")
    return gesetzt, offen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--apply", action="store_true", help="schreiben (sonst Trockenlauf)")
    args = parser.parse_args()
    with SessionLocal() as db:
        gesetzt, offen = zuordnen(db, args.tenant)
        print(f"Verkaufsschluessel: {gesetzt['steuerschluessel_verkauf']}, "
              f"Einkaufsschluessel: {gesetzt['steuerschluessel_einkauf']}, offen: {len(offen)}")
        for zeile in offen:
            print("  offen —", zeile)
        if args.apply:
            db.commit()
            print("geschrieben.")
        else:
            db.rollback()
            print("Trockenlauf: nichts geschrieben (--apply schreibt).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
