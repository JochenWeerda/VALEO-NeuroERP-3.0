"""Kontenrahmen SKR03 und die vier Regel-Steuerschluessel fuer einen Mandanten einrichten.

    python scripts/seed_steuerschluessel_skr03.py --tenant <mandant>           # zeigt, was angelegt wuerde
    python scripts/seed_steuerschluessel_skr03.py --tenant <mandant> --apply   # legt an

Angelegt wird nur, was fehlt (siehe ``app.finance.steuerschluessel.richte_skr03_ein``). Steuerfreie
Umsaetze, innergemeinschaftliche Lieferungen, Export und Paragraf 24 UStG gehoeren nicht zur
Grundausstattung — die ordnet die Buchhaltung in der Maske „Steuerschluessel“ ein.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.finance.steuerschluessel import richte_skr03_ein  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="SKR03-Grundausstattung der Steuerschluessel")
    parser.add_argument("--tenant", required=True, help="Mandant")
    parser.add_argument("--apply", action="store_true", help="festschreiben (sonst nur zeigen)")
    args = parser.parse_args()

    with SessionLocal() as db:
        angelegt = richte_skr03_ein(db, args.tenant)
        if args.apply:
            db.commit()
        else:
            db.rollback()
    verb = "Angelegt" if args.apply else "Wuerde anlegen"
    print(f"{verb} fuer {args.tenant}: Kontenrahmen SKR03; "
          f"Steuerschluessel {', '.join(angelegt['steuerschluessel']) or 'keine'}; "
          f"Konten {', '.join(angelegt['konten']) or 'keine'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
