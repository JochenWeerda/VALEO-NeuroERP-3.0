#!/usr/bin/env python3
"""Traegt Altbelegen des Dokumentspeichers ihren Mandanten nach — wo er sich eindeutig aus der Buchung ergibt.

Ausgangsrechnungen des alten Rechnungswegs und Lieferantengutschriften/-belastungen entstanden bis 13.10.2026 ohne
Mandant (``data->>'tenantId'``). Seither liefern die Lesewege einen Beleg ohne Mandant niemandem aus. Dieses Skript
ordnet zu, was sich belegen laesst: Hat genau ein Mandant eine Buchung oder einen offenen Posten zu der Belegnummer,
gehoert der Beleg ihm. Alles andere bleibt unzugeordnet und wird ausgewiesen — geraten wird nicht.

Verwendung:
    python scripts/belege_mandant_nachtragen.py            # nur zeigen
    python scripts/belege_mandant_nachtragen.py --apply    # zuordnen
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BELEGARTEN = ("sales_invoice", "credit_memo", "debit_memo")


def ordne_zu(db: Session, *, apply: bool = False) -> dict[str, list[dict[str, Any]]]:
    """Gibt ``{"zugeordnet": [...], "offen": [...]}`` zurueck; schreibt nur mit ``apply`` (ohne eigenen Commit)."""
    belege = db.execute(
        text(
            "SELECT id, doc_type, doc_number FROM documents WHERE doc_type = ANY(:arten) "
            "AND COALESCE(CAST(data AS jsonb)->>'tenantId', '') = '' ORDER BY doc_type, doc_number"
        ),
        {"arten": list(BELEGARTEN)},
    ).fetchall()
    ergebnis: dict[str, list[dict[str, Any]]] = {"zugeordnet": [], "offen": []}
    for kennung, art, nummer in belege:
        mandanten = [
            str(z[0])
            for z in db.execute(
                text(
                    "SELECT tenant_id FROM domain_erp.offene_posten WHERE rechnungsnr = :n "
                    "UNION SELECT tenant_id FROM domain_erp.journal_entries WHERE document_number = :n OR reference = :n"
                ),
                {"n": nummer},
            ).fetchall()
            if z[0]
        ]
        eintrag = {"art": art, "nummer": nummer, "mandanten": sorted(set(mandanten))}
        if len(eintrag["mandanten"]) != 1:
            ergebnis["offen"].append(eintrag)
            continue
        ergebnis["zugeordnet"].append(eintrag)
        if apply:
            db.execute(
                text(
                    "UPDATE documents SET data = jsonb_set(CAST(data AS jsonb), '{tenantId}', to_jsonb(CAST(:t AS text))), "
                    "updated_at = now() WHERE id = :id AND COALESCE(CAST(data AS jsonb)->>'tenantId', '') = ''"
                ),
                {"t": eintrag["mandanten"][0], "id": kennung},
            )
    return ergebnis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Zuordnung schreiben (sonst nur zeigen)")
    args = parser.parse_args()

    from app.core.database import SessionLocal

    with SessionLocal() as db:
        ergebnis = ordne_zu(db, apply=args.apply)
        if args.apply:
            db.commit()
    for eintrag in ergebnis["zugeordnet"]:
        print(f"{'zugeordnet' if args.apply else 'zuordenbar'}: {eintrag['art']} {eintrag['nummer']} -> {eintrag['mandanten'][0]}")
    for eintrag in ergebnis["offen"]:
        grund = "keine Buchung" if not eintrag["mandanten"] else f"mehrere Mandanten ({', '.join(eintrag['mandanten'])})"
        print(f"offen: {eintrag['art']} {eintrag['nummer']} - {grund}")
    print(f"{len(ergebnis['zugeordnet'])} {'zugeordnet' if args.apply else 'zuordenbar'}, {len(ergebnis['offen'])} offen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
