#!/usr/bin/env python3
"""Abstimmbericht Bestandshauptbuch (DOM-INV-006).

Macht das Abgleich-Gate aus DOM-INV-005 ausfuehrbar: statt zuzusichern, dass
die neuen Bestandszahlen stimmen, laesst sich der Bestand hier gegen seine
Buchungen nachrechnen.

Verwendung:
    python scripts/inventory_balance_reconciliation.py
    python scripts/inventory_balance_reconciliation.py --tenant <id>
    python scripts/inventory_balance_reconciliation.py --json > abstimmung.json

Exit-Code 1, wenn der Saldo nicht vollstaendig erklaerbar ist - also wenn
Buchungen mit unbekannter Belegart im Hauptbuch stehen. Damit ist der Bericht
auch als Betriebs-Gate verwendbar.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal  # noqa: E402
from app.services.inventory_balance_reconciliation import (  # noqa: E402
    als_text,
    erstelle_bericht,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant", default=None, help="Nur diesen Mandanten abstimmen")
    parser.add_argument("--json", action="store_true", help="Maschinenlesbare Ausgabe")
    parser.add_argument(
        "--zeilen", type=int, default=20, help="Detailzeilen je Abschnitt (Textausgabe)"
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        bericht = erstelle_bericht(db, args.tenant)
    finally:
        db.close()

    if args.json:
        print(json.dumps(bericht.als_dict(), indent=2, ensure_ascii=False))
    else:
        print(als_text(bericht, max_zeilen=args.zeilen))

    return 0 if bericht.ist_abstimmbar else 1


if __name__ == "__main__":
    raise SystemExit(main())
