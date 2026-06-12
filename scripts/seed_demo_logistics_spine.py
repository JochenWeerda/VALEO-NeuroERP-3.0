#!/usr/bin/env python3
"""Demo-Seed: Tour-Stopp mit Lieferschein-Referenz (LOG-SPINE-001).

Idempotent. Voraussetzung: ``DEMO-LS-001`` aus ``scripts/seed_demo_sales.py`` (domain_sales.delivery_notes).

Lauf:
  python scripts/seed_demo_logistics_spine.py
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"
VEHICLE_ID = "DEMO-LOG-SPINE-TOUR"
REF_NUMBER = "DEMO-LS-001"


def main() -> int:
    db = SessionLocal()
    try:
        ls = db.execute(
            text(
                "SELECT id FROM domain_sales.delivery_notes "
                "WHERE tenant_id = :t AND delivery_note_number = :n LIMIT 1"
            ),
            {"t": TENANT, "n": REF_NUMBER},
        ).scalar()
        if not ls:
            print("SKIP: Kein Lieferschein DEMO-LS-001 — zuerst seed_demo_sales.py ausführen.")
            return 1

        tid = db.execute(
            text(
                "SELECT id FROM domain_logistics.tours "
                "WHERE tenant_id = :t AND vehicle_id = :v LIMIT 1"
            ),
            {"t": TENANT, "v": VEHICLE_ID},
        ).scalar()
        if tid:
            print("OK: Demo-Spine-Tour existiert bereits.")
            return 0

        tour_id = str(uuid.uuid4())
        stop_id = str(uuid.uuid4())
        now = datetime.utcnow()
        db.execute(
            text(
                """
                INSERT INTO domain_logistics.tours
                    (id, date, vehicle_id, driver_id, status, notes, tenant_id)
                VALUES (:id, :dt, :veh, :drv, 'GEPLANT', :notes, :tenant)
                """
            ),
            {
                "id": tour_id,
                "dt": now,
                "veh": VEHICLE_ID,
                "drv": "DEMO-FAHRER-SPINE",
                "notes": "LOG-SPINE-001 Demo: Stopp verknüpft mit DEMO-LS-001",
                "tenant": TENANT,
            },
        )
        db.execute(
            text(
                """
                INSERT INTO domain_logistics.tour_stops
                    (id, tour_id, stop_order, address, lat, lng, customer_id,
                     delivery_note_ref, planned_arrival, status, tenant_id)
                VALUES (:sid, :tid, 0, :addr, 52.5, 13.4, :cust, :dref, :dt, 'GEPLANT', :tenant)
                """
            ),
            {
                "sid": stop_id,
                "tid": tour_id,
                "addr": "Demo-Anlieferung LOG-SPINE",
                "cust": "DEMO-CUST-001",
                "dref": REF_NUMBER,
                "dt": now,
                "tenant": TENANT,
            },
        )
        db.commit()
        print(f"OK: Tour {tour_id} mit Stopp → delivery_note_ref={REF_NUMBER}")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"FEHLER: {exc}")
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
