#!/usr/bin/env python3
"""Demo-Seed: WMS Zone → Gang → Fächer für Default-Tenant.

Idempotent. Legt ``DEMO-H``-Zone, Gang ``G01`` und Fächer ``DEMO-F-01``/``DEMO-F-02`` an,
sofern ein aktives Lager (warehouse) für den Tenant existiert.

Lauf:
  python scripts/seed_demo_wms_structure.py
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"
ZONE_CODE = "DEMO-H"
AISLE_CODE = "G01"


def main() -> int:
    db = SessionLocal()
    try:
        wid = db.execute(
            text(
                "SELECT id FROM domain_inventory.warehouses "
                "WHERE tenant_id = :t AND is_active = true "
                "ORDER BY warehouse_code LIMIT 1"
            ),
            {"t": TENANT},
        ).scalar()
        if not wid:
            print("SKIP: Kein aktives Lager für Demo-Tenant — zuerst Stammdaten-Lager anlegen.")
            return 1

        zid = db.execute(
            text(
                "SELECT id FROM domain_inventory.warehouse_zones "
                "WHERE warehouse_id = :w AND tenant_id = :t AND zone_code = :zc LIMIT 1"
            ),
            {"w": wid, "t": TENANT, "zc": ZONE_CODE},
        ).scalar()
        if not zid:
            zid = str(uuid.uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_inventory.warehouse_zones
                      (id, warehouse_id, zone_code, name, zone_type, tenant_id, is_active)
                    VALUES (:id, :wid, :zc, :name, 'standard', :tid, true)
                    """
                ),
                {
                    "id": zid,
                    "wid": wid,
                    "zc": ZONE_CODE,
                    "name": "Demo Hauptlager",
                    "tid": TENANT,
                },
            )
            print(f"OK: Zone {ZONE_CODE} angelegt ({zid}).")
        else:
            print(f"OK: Zone {ZONE_CODE} existiert bereits ({zid}).")

        aid = db.execute(
            text(
                "SELECT id FROM domain_inventory.warehouse_aisles "
                "WHERE zone_id = :z AND tenant_id = :t AND aisle_code = :ac LIMIT 1"
            ),
            {"z": zid, "t": TENANT, "ac": AISLE_CODE},
        ).scalar()
        if not aid:
            aid = str(uuid.uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_inventory.warehouse_aisles
                      (id, zone_id, warehouse_id, aisle_code, name, tenant_id, is_active)
                    VALUES (:id, :zid, :wid, :ac, 'Demo-Gang 1', :tid, true)
                    """
                ),
                {"id": aid, "zid": zid, "wid": wid, "ac": AISLE_CODE, "tid": TENANT},
            )
            print(f"OK: Gang {AISLE_CODE} angelegt ({aid}).")
        else:
            print(f"OK: Gang {AISLE_CODE} existiert bereits ({aid}).")

        for code, cap in (("DEMO-F-01", Decimal("50000")), ("DEMO-F-02", Decimal("50000"))):
            bid = db.execute(
                text(
                    "SELECT id FROM domain_inventory.warehouse_bins "
                    "WHERE warehouse_id = :w AND tenant_id = :t AND bin_code = :bc LIMIT 1"
                ),
                {"w": wid, "t": TENANT, "bc": code},
            ).scalar()
            if bid:
                print(f"OK: Fach {code} existiert bereits.")
                continue
            bid = str(uuid.uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_inventory.warehouse_bins
                      (id, zone_id, warehouse_id, aisle_id, bin_code, bin_type, capacity_kg,
                       tenant_id, is_active, is_blocked)
                    VALUES (:id, :zid, :wid, :aid, :bc, 'standard', :cap, :tid, true, false)
                    """
                ),
                {
                    "id": bid,
                    "zid": zid,
                    "wid": wid,
                    "aid": aid,
                    "bc": code,
                    "cap": cap,
                    "tid": TENANT,
                },
            )
            print(f"OK: Fach {code} angelegt ({bid}).")

        db.commit()
        return 0
    except Exception as e:
        db.rollback()
        print(f"FEHLER: {e}")
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
