#!/usr/bin/env python3
"""Veroeffentlicht die neun Varianten der Belegmaske fuer den Testmandanten der Sichtpruefung — wiederholbar.

    python scripts/belegmasken_veroeffentlichen.py            # zeigt, was veroeffentlicht wuerde
    python scripts/belegmasken_veroeffentlichen.py --apply    # veroeffentlicht
    python scripts/belegmasken_veroeffentlichen.py --adressen # Adressen der Belege in der Maske

Entscheidung des Auftraggebers vom 13.10.2026: Die Belegdefinitionen duerfen registriert werden, zunaechst **nur
fuer den autorisierten Testmandanten** der Sichtpruefung. Das ist keine Produktivfreigabe.

Deshalb stehen sie nicht in der Registry aller Mandanten (``_SCREEN_DEFINITIONS``), sondern werden ueber den
vorhandenen Weg fuer mandantenbezogene Masken veroeffentlicht (``studio_draft_store``, Stand ``published_temp``).
Ein anderer Mandant bekommt fuer ``beleg/…`` weiterhin „nicht gefunden". Das Skript nimmt nur Mandanten aus
``ERLAUBTE_MANDANTEN`` an.

Der Weg verlangt zwei Kennungen (Bearbeiter und Veroeffentlicher). Das Skript benutzt zwei ausgewiesene Kennungen
der Referenzdaten; beide stehen am Entwurf.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.screen_definitions_beleg import alle_beleg_screen_definitions  # noqa: E402
from app.core.screen_governance import governance_errors  # noqa: E402
from app.services import studio_draft_store  # noqa: E402

TESTMANDANT = "00000000-0000-0000-0000-000000000051"
ERLAUBTE_MANDANTEN: frozenset[str] = frozenset({TESTMANDANT})
BEARBEITER = "belegmasken"
VEROEFFENTLICHER = "belegmasken-zweitfreigabe"


def veroeffentliche(tenant_id: str, *, erlaubte: frozenset[str] = ERLAUBTE_MANDANTEN) -> dict[str, str]:
    """Bringt jede Variante auf ``published_temp`` — mit dem aktuellen Stand der Definition. Kennung -> was geschah."""
    if tenant_id not in erlaubte:
        raise PermissionError(f"Mandant {tenant_id} ist fuer die Belegmasken nicht freigegeben.")
    bericht: dict[str, str] = {}
    vorhanden = {str(e.get("screen_id")): e for e in studio_draft_store.list_drafts(tenant_id)}
    for kennung, definition in alle_beleg_screen_definitions().items():
        fehler = governance_errors(definition)
        if fehler:
            raise ValueError(f"{kennung}: {'; '.join(fehler)}")
        alt = vorhanden.get(kennung)
        if alt and alt.get("status") == "published_temp" and alt.get("definition") == definition:
            bericht[kennung] = "aktuell"
            continue
        if alt and alt.get("status") not in ("draft", "review"):
            # Eine veroeffentlichte Maske wird erst zurueckgenommen, dann neu vorgelegt.
            studio_draft_store.set_status(tenant_id, str(alt["id"]), BEARBEITER, "draft")
        entwurf = studio_draft_store.save_draft(tenant_id, BEARBEITER, definition, draft_id=str(alt["id"]) if alt else None)
        studio_draft_store.set_status(tenant_id, str(entwurf["id"]), BEARBEITER, "review")
        studio_draft_store.set_status(tenant_id, str(entwurf["id"]), VEROEFFENTLICHER, "published_temp")
        bericht[kennung] = "erneuert" if alt else "veroeffentlicht"
    return bericht


def adressen(tenant_id: str) -> list[str]:
    """Je Beleg des Mandanten die Adresse der Belegmaske — fuer die Sichtpruefung im Browser."""
    from sqlalchemy import text

    from app.core.belegvertrag import BELEGARTEN
    from app.core.database import SessionLocal

    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT doc_type, id, doc_number, status FROM domain_docflow.document_headers "
            "WHERE tenant_id = :t AND deleted_at IS NULL AND doc_type = ANY(:arten) ORDER BY doc_type, doc_number"),
            {"t": tenant_id, "arten": sorted(BELEGARTEN)}).fetchall()
    return [f"/belege/{art}/{beleg_id}    {nummer} ({status})" for art, beleg_id, nummer, status in zeilen]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tenant", default=TESTMANDANT)
    parser.add_argument("--apply", action="store_true", help="veroeffentlichen (sonst nur zeigen)")
    parser.add_argument("--adressen", action="store_true", help="die Adressen der Belege des Mandanten in der Maske zeigen")
    args = parser.parse_args()
    if args.tenant not in ERLAUBTE_MANDANTEN:
        print(f"Abgelehnt: Mandant {args.tenant} ist nicht freigegeben (nur {', '.join(sorted(ERLAUBTE_MANDANTEN))}).",
              file=sys.stderr)
        return 1
    if args.adressen:
        for zeile in adressen(args.tenant):
            print(zeile)
        return 0
    if not args.apply:
        for kennung in alle_beleg_screen_definitions():
            print(f"wuerde veroeffentlichen: {kennung}  ->  {studio_draft_store.studio_run_route(kennung)}")
        return 0
    for kennung, was in veroeffentliche(args.tenant).items():
        print(f"{was:16} {kennung}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
