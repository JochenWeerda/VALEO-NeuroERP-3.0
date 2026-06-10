#!/usr/bin/env python3
"""Demo-Seed: Kontrakte mit Erfüllung (DOM-CON-004).

Idempotent (Präfix ``DEMO-KT-``). Kontrakt → Position → Bewegungen (Abrufe) unter
dem Dev-Standardtenant, mit Fällen teilerfüllt / überfällig-untererfüllt / erfüllt,
damit der Kontrakt-Erfüllungsstand (/api/v1/contracts/fulfillment) verifizierbar ist.

Lauf: docker exec valeo-neuro-erp-backend python scripts/seed_demo_contracts.py
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"


def _exists(db, contract_no: str) -> bool:
    return bool(db.execute(
        text("SELECT 1 FROM domain_ops.kon_contract WHERE contract_no = :c AND tenant_id = :t"),
        {"c": contract_no, "t": TENANT},
    ).first())


def _contract(db, no: str, typ: str, total: float, unit: str, valid_to, article: str,
              qty: float, abrufe: list[float]) -> None:
    now = datetime.now(timezone.utc)
    cid = str(uuid.uuid4())
    lid = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO domain_ops.kon_contract "
             "(contract_id, contract_no, contract_type, party_id, quantity_type, total_quantity, "
             "unit, allow_overdelivery, status, tenant_id, contract_date, valid_from, valid_to, created_at) "
             "VALUES (:cid, :no, :typ, 'DEMO-P1', 'GESAMTKONTRAKT', :total, :unit, false, 'aktiv', :t, "
             ":cdat, :vfrom, :vto, :ts)"),
        {"cid": cid, "no": no, "typ": typ, "total": total, "unit": unit, "t": TENANT,
         "cdat": now - timedelta(days=40), "vfrom": now - timedelta(days=40), "vto": valid_to, "ts": now},
    )
    db.execute(
        text("INSERT INTO domain_ops.kon_contract_line "
             "(line_id, contract_id, position_no, article_id, qty_contract, is_bio, is_matif, tenant_id, created_at) "
             "VALUES (:lid, :cid, 1, :art, :qty, false, false, :t, :ts)"),
        {"lid": lid, "cid": cid, "art": article, "qty": qty, "t": TENANT, "ts": now},
    )
    for i, menge in enumerate(abrufe):
        db.execute(
            text("INSERT INTO domain_ops.kon_contract_movement "
                 "(movement_id, contract_id, line_id, quantity, movement_date, is_invoiced, is_archived, tenant_id, created_at) "
                 "VALUES (:mid, :cid, :lid, :q, :md, false, false, :t, :ts)"),
            {"mid": str(uuid.uuid4()), "cid": cid, "lid": lid, "q": menge,
             "md": now - timedelta(days=30 - i * 5), "t": TENANT, "ts": now},
        )


def seed() -> dict:
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    created = []
    try:
        if not _exists(db, "DEMO-KT-001"):
            _contract(db, "DEMO-KT-001", "EINKAUF", 200, "t", now + timedelta(days=30),
                      "Raps 00", 200, [80, 40])  # 120/200 teilerfüllt
            created.append("DEMO-KT-001")
        if not _exists(db, "DEMO-KT-002"):
            _contract(db, "DEMO-KT-002", "VERKAUF", 100, "t", now - timedelta(days=10),
                      "Weizen A", 100, [40])  # 40/100, überfällig
            created.append("DEMO-KT-002")
        if not _exists(db, "DEMO-KT-003"):
            _contract(db, "DEMO-KT-003", "EINKAUF", 50, "t", now + timedelta(days=20),
                      "Futtergerste", 50, [25, 25])  # 50/50 erfüllt
            created.append("DEMO-KT-003")
        db.commit()
        return {"created": created, "skipped": not created}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import json

    print(json.dumps(seed(), ensure_ascii=False))
