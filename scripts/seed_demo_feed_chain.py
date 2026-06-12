#!/usr/bin/env python3
"""Demo-Seed: Mischfutter-Produktionskette (FEED-CHAIN-001).

Idempotent. Legt drei Einzelfuttermittel mit Bestand und ein aktives Rezept
``DEMO-MLF-18`` (Milchleistungsfutter 18 % RP, Rind) mit Komponenten an —
Grundlage für Produktionsauftrag → Freigabe → fertig → Fertigwaren-Charge.

Lauf:
  python scripts/seed_demo_feed_chain.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.database import SessionLocal  # noqa: E402

TENANT = "00000000-0000-0000-0000-000000000001"
REZEPT_CODE = "DEMO-MLF-18"

EINZELFUTTER = [
    # (id-suffix, artikel_nummer, name, art, protein, verfuegbar_t, gvo_status)
    ("weizen", "DEMO-EF-WEIZEN", "Demo Weizen", "Energiefutter", 12.0, 250, "gvo-frei"),
    ("soja", "DEMO-EF-SOJA", "Demo Sojaschrot 44", "Eiweißfutter", 44.0, 120, "gvo-frei-zertifiziert"),
    ("mineral", "DEMO-EF-MINERAL", "Demo Mineralfutter Rind", "Mineralfutter", 0.0, 40, "gvo-frei"),
]

KOMPONENTEN = [
    # (einzelfutter-suffix, name, anteil, sortierung)
    ("weizen", "Demo Weizen", 0.62, 0),
    ("soja", "Demo Sojaschrot 44", 0.34, 1),
    ("mineral", "Demo Mineralfutter Rind", 0.04, 2),
]


def main() -> int:
    db = SessionLocal()
    try:
        ef_ids: dict[str, str] = {}
        for suffix, artikel_nummer, name, art, protein, bestand, gvo in EINZELFUTTER:
            existing = db.execute(
                text(
                    "SELECT id FROM domain_shared.futtermittel_einzelfutter "
                    "WHERE tenant_id = :t AND artikel_nummer = :an LIMIT 1"
                ),
                {"t": TENANT, "an": artikel_nummer},
            ).scalar()
            if existing:
                ef_ids[suffix] = str(existing)
                continue
            ef_id = f"demo-ef-{suffix}"
            db.execute(
                text(
                    "INSERT INTO domain_shared.futtermittel_einzelfutter "
                    "(id, tenant_id, artikel_nummer, name, art, protein, verfuegbar_t, "
                    " gvo_status, qs_milch, aktiv) "
                    "VALUES (:id, :t, :an, :name, :art, :protein, :bestand, :gvo, true, true)"
                ),
                {"id": ef_id, "t": TENANT, "an": artikel_nummer, "name": name,
                 "art": art, "protein": protein, "bestand": bestand, "gvo": gvo},
            )
            ef_ids[suffix] = ef_id

        rezept_id = db.execute(
            text(
                "SELECT id FROM domain_shared.futtermittel_rezepte "
                "WHERE tenant_id = :t AND rezept_code = :c LIMIT 1"
            ),
            {"t": TENANT, "c": REZEPT_CODE},
        ).scalar()
        if rezept_id:
            db.commit()
            print("OK: Demo-Rezept existiert bereits (Einzelfutter ggf. ergänzt).")
            return 0

        rezept_id = "demo-rezept-mlf18"
        db.execute(
            text(
                "INSERT INTO domain_shared.futtermittel_rezepte "
                "(id, tenant_id, rezept_code, name, tierart, protein_ziel, aktiv) "
                "VALUES (:id, :t, :c, 'Demo Milchleistungsfutter 18', 'Rind', 18.0, true)"
            ),
            {"id": rezept_id, "t": TENANT, "c": REZEPT_CODE},
        )
        for suffix, name, anteil, sortierung in KOMPONENTEN:
            db.execute(
                text(
                    "INSERT INTO domain_shared.futtermittel_rezept_komponenten "
                    "(id, rezept_id, komponente_name, anteil, einzelfutter_id, sortierung) "
                    "VALUES (:id, :r, :name, :anteil, :ef, :sort)"
                ),
                {"id": f"demo-rk-{suffix}", "r": rezept_id, "name": name,
                 "anteil": anteil, "ef": ef_ids[suffix], "sort": sortierung},
            )
        db.commit()
        print(f"OK: Demo-Futtermittelkette angelegt (Rezept {REZEPT_CODE}, 3 Komponenten).")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
