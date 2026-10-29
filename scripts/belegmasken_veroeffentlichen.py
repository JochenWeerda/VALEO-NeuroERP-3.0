#!/usr/bin/env python3
"""Check code-defined document masks for the approved visual-test tenant.

Native definitions are deployed with the application. This command does not
create Studio drafts, invent approvers or bypass Studio release evidence.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_beleg import NATIVE_BELEG_TENANTS, alle_beleg_screen_definitions
from app.core.screen_governance import governance_errors

TESTMANDANT = "00000000-0000-0000-0000-000000000051"


def pruefe_native_definitionen(tenant_id: str) -> dict[str, str]:
    if tenant_id not in NATIVE_BELEG_TENANTS:
        raise PermissionError("Mandant ist fuer die native Beleg-Sichtpruefung nicht freigegeben.")
    result = {}
    for screen_id in alle_beleg_screen_definitions():
        definition = get_screen_definition(screen_id, tenant_id=tenant_id)
        errors = governance_errors(definition) if definition else ["Definition fehlt"]
        if errors:
            raise ValueError(f"{screen_id}: {'; '.join(errors)}")
        result[screen_id] = "native_definition_geprueft"
    return result


def adressen(tenant_id: str) -> list[str]:
    """Je Beleg des Mandanten die Adresse der Belegmaske — fuer die Sichtpruefung im Browser."""
    if tenant_id not in NATIVE_BELEG_TENANTS:
        raise PermissionError("Mandant ist fuer die Sichtpruefung nicht freigegeben.")
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
    parser.add_argument("--adressen", action="store_true", help="Nur Adressen der vorhandenen Referenzbelege anzeigen")
    parser.add_argument("--apply", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.apply:
        parser.error("Native Belegmasken werden mit dem Code ausgeliefert. Keine Studio-Veroeffentlichung aus diesem Skript.")
    if args.adressen:
        for address in adressen(args.tenant):
            print(address)
        return 0
    for screen_id, result in pruefe_native_definitionen(args.tenant).items():
        print(f"{result}: {screen_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
