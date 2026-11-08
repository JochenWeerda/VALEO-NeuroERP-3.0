#!/usr/bin/env python3
"""Richtet einen eigenen Mandanten fuer Sicht- und Browserpruefungen ein — wiederholbar.

    python scripts/sichtpruefung_mandant_einrichten.py                     # zeigt, was angelegt wuerde
    python scripts/sichtpruefung_mandant_einrichten.py --apply             # legt an
    python scripts/sichtpruefung_mandant_einrichten.py --apply --belege    # dazu die Referenzbelege

Entscheidung des Auftraggebers vom 13.10.2026: Die Sichtpruefung laeuft in einer isolierten Umgebung mit
eigenem Testmandanten. Der bisherige Testmandant der gewachsenen Datenbank hat eine Luecke in der Journalkette
und kann nicht mehr buchen.

Angelegt wird nur, was fehlt: der Mandant, der Kontenrahmen SKR03 mit den vier Regel-Steuerschluesseln und
ihren Konten (``richte_skr03_ein``), das Forderungskonto 1400. Mit ``--belege`` folgen die Referenzbelege
(``scripts/referenzbelege_anlegen.py``).

Die Testkennung, die sich fuer die Browserpruefung anmeldet, muss an diesen Mandanten gebunden sein
(Identitaet); Zugangsdaten stehen nicht im Repository.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.core.uuid7 import uuid7  # noqa: E402
from app.finance.steuerschluessel import richte_skr03_ein  # noqa: E402

MANDANT = "00000000-0000-0000-0000-000000000051"
NAME = "Sichtpruefung (Referenzbelege)"
FORDERUNGEN = ("1400", "Forderungen aus Lieferungen und Leistungen", "asset", "current_assets")


def richte_ein(db, tenant_id: str = MANDANT, name: str = NAME) -> dict[str, object]:
    """Legt Fehlendes an (ohne Commit). Gibt zurueck, was angelegt wurde."""
    bericht: dict[str, object] = {"mandant": False, "konto_1400": False}
    if not db.execute(text("SELECT 1 FROM domain_shared.tenants WHERE id = :id"), {"id": tenant_id}).first():
        # Gewachsene Datenbanken verlangen ``domain``; frische kennen die Spalte je nach Stand nicht.
        hat_domain = db.execute(text(
            "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_shared' "
            "AND table_name = 'tenants' AND column_name = 'domain'")).first()
        if hat_domain:
            db.execute(text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:id, :name, :domain, true)"),
                {"id": tenant_id, "name": name, "domain": f"sichtpruefung-{tenant_id[-4:]}.invalid"})
        else:
            db.execute(text(
                "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :name, true)"),
                {"id": tenant_id, "name": name})
        bericht["mandant"] = True
    bericht.update(richte_skr03_ein(db, tenant_id))
    nummer, bezeichnung, art, kategorie = FORDERUNGEN
    if not db.execute(text(
            "SELECT 1 FROM domain_erp.chart_of_accounts WHERE tenant_id = :t AND account_number = :nr"),
            {"t": tenant_id, "nr": nummer}).first():
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at) "
            "VALUES (:id, :t, :nr, :name, :art, :kat, true, NOW(), NOW())"),
            {"id": uuid7(), "t": tenant_id, "nr": nummer, "name": bezeichnung, "art": art, "kat": kategorie})
        bericht["konto_1400"] = True
    return bericht


def _referenzbelege():
    spec = importlib.util.spec_from_file_location("referenzbelege_anlegen", ROOT / "scripts/referenzbelege_anlegen.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tenant", default=MANDANT)
    parser.add_argument("--name", default=NAME)
    parser.add_argument("--apply", action="store_true", help="anlegen (sonst nur zeigen)")
    parser.add_argument("--belege", action="store_true", help="nach dem Einrichten die Referenzbelege anlegen")
    args = parser.parse_args()
    with SessionLocal() as db:
        bericht = richte_ein(db, args.tenant, args.name)
        if args.apply:
            db.commit()
        else:
            db.rollback()
        verb = "Angelegt" if args.apply else "Wuerde anlegen"
        print(f"{verb} fuer {args.tenant}: Mandant {'ja' if bericht['mandant'] else 'vorhanden'}; "
              f"Steuerschluessel {', '.join(bericht['steuerschluessel']) or 'keine'}; "
              f"Konten {', '.join(bericht['konten']) or 'keine'}{', 1400' if bericht['konto_1400'] else ''}.")
        if args.belege:
            if not args.apply:
                print("Referenzbelege: nur mit --apply.")
                return 0
            belege = _referenzbelege().lege_an(db, args.tenant)
            print(f"Referenzbelege: {len(belege)}")
            for b in belege:
                print(f"  {b['rolle']:30} {b['doc_type']:22} {b['doc_number']:22} {b['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
