#!/usr/bin/env python3
"""Demo-Mandant mit rein synthetischen Daten — anlegen und wieder löschen.

    DATABASE_URL="$TEST_DATABASE_URL" python scripts/demo_mandant.py --anlegen
    DATABASE_URL="$TEST_DATABASE_URL" python scripts/demo_mandant.py --loeschen
    DATABASE_URL="$TEST_DATABASE_URL" python scripts/demo_mandant.py --status

Ziel: ein Kommando für Schulung/Demo ohne echte Personen- oder L3-Daten
(M7, docs/roadmap/m7-m8-vorarbeiten.md). Vorgesehen gegen ``valeo_probe``
(``TEST_DATABASE_URL``).

Der Mandant hat eine feste synthetische UUID und den Namen „Demo (synthetisch)“.
Löschen entfernt nur diesen Mandanten und klar zugehörige Demo-Kontenrahmen-
Zeilen; fremde Mandanten bleiben unberührt.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.uuid7 import uuid7  # noqa: E402

DEMO_TENANT_ID = "00000000-0000-4000-8000-00000000d300"
DEMO_NAME = "Demo (synthetisch)"
DEMO_DOMAIN = "demo-synthetisch.invalid"


def _url() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise SystemExit(
            "DATABASE_URL oder TEST_DATABASE_URL setzen "
            "(empfohlen: postgresql://…/valeo_probe)."
        )
    return url


def _session():
    engine = create_engine(_url())
    return sessionmaker(bind=engine)()


def vorhanden(db, tenant_id: str = DEMO_TENANT_ID) -> bool:
    return bool(
        db.execute(
            text("SELECT 1 FROM domain_shared.tenants WHERE id = :id"),
            {"id": tenant_id},
        ).first()
    )


def anlegen(db, tenant_id: str = DEMO_TENANT_ID) -> dict[str, object]:
    """Legt den Demo-Mandanten und ein synthetisches Erfolgskonto an (ohne Commit)."""
    bericht: dict[str, object] = {"mandant": False, "konto_8000": False}
    if vorhanden(db, tenant_id):
        return bericht

    hat_domain = db.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'domain_shared' AND table_name = 'tenants' "
            "AND column_name = 'domain'"
        )
    ).first()
    if hat_domain:
        db.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :name, :domain, true)"
            ),
            {"id": tenant_id, "name": DEMO_NAME, "domain": DEMO_DOMAIN},
        )
    else:
        db.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, is_active) "
                "VALUES (:id, :name, true)"
            ),
            {"id": tenant_id, "name": DEMO_NAME},
        )
    bericht["mandant"] = True

    # Rein synthetisches Erfolgskonto — keine Personen-/L3-Daten.
    if db.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'domain_erp' AND table_name = 'chart_of_accounts'"
        )
    ).first() and not db.execute(
        text(
            "SELECT 1 FROM domain_erp.chart_of_accounts "
            "WHERE tenant_id = :t AND account_number = '8000'"
        ),
        {"t": tenant_id},
    ).first():
        db.execute(
            text(
                "INSERT INTO domain_erp.chart_of_accounts "
                "(id, tenant_id, account_number, account_name, account_type, category, "
                "is_active, created_at, updated_at) "
                "VALUES (:id, :t, '8000', 'Demo Erloese (synthetisch)', 'revenue', "
                "'operating_revenue', true, NOW(), NOW())"
            ),
            {"id": uuid7(), "t": tenant_id},
        )
        bericht["konto_8000"] = True
    return bericht


def loeschen(db, tenant_id: str = DEMO_TENANT_ID) -> dict[str, object]:
    """Entfernt Demo-Konten und den Demo-Mandanten (ohne Commit)."""
    bericht: dict[str, object] = {"konto_zeilen": 0, "mandant": False}
    if db.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'domain_erp' AND table_name = 'chart_of_accounts'"
        )
    ).first():
        res = db.execute(
            text("DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t"),
            {"t": tenant_id},
        )
        bericht["konto_zeilen"] = res.rowcount or 0
    if vorhanden(db, tenant_id):
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id = :id"), {"id": tenant_id})
        bericht["mandant"] = True
    return bericht


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    gruppe = parser.add_mutually_exclusive_group(required=True)
    gruppe.add_argument("--anlegen", action="store_true", help="Demo-Mandanten anlegen")
    gruppe.add_argument("--loeschen", action="store_true", help="Demo-Mandanten löschen")
    gruppe.add_argument("--status", action="store_true", help="nur prüfen, ob vorhanden")
    args = parser.parse_args(argv)

    os.environ.setdefault("PGAPPNAME", "agent:demo-mandant")
    with _session() as db:
        if args.status:
            print(f"Demo-Mandant {DEMO_TENANT_ID}: {'vorhanden' if vorhanden(db) else 'fehlt'}")
            return 0
        if args.anlegen:
            bericht = anlegen(db)
            db.commit()
            print(
                f"Angelegt {DEMO_TENANT_ID} ({DEMO_NAME}): "
                f"Mandant={'neu' if bericht['mandant'] else 'bereits da'}; "
                f"Konto 8000={'neu' if bericht['konto_8000'] else 'n/a oder da'}."
            )
            return 0
        bericht = loeschen(db)
        db.commit()
        print(
            f"Gelöscht {DEMO_TENANT_ID}: Mandant={'ja' if bericht['mandant'] else 'fehlte'}; "
            f"Kontenzeilen={bericht['konto_zeilen']}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
