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


def _matif_contract(db, no: str, typ: str, total: float, unit: str, valid_to, article: str,
                    symbol: str, premium: float, fixings: list[tuple[float, float]],
                    quote_price: float) -> None:
    """MATIF-Kontrakt (DOM-CON-004.2): Position is_matif=True + Prämie/Basis-Symbol,
    bestehende Teilfixierungen und eine aktuelle Marktnotierung."""
    now = datetime.now(timezone.utc)
    cid = str(uuid.uuid4())
    lid = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO domain_ops.kon_contract "
             "(contract_id, contract_no, contract_type, party_id, quantity_type, total_quantity, "
             "unit, allow_overdelivery, status, tenant_id, contract_date, valid_from, valid_to, created_at, "
             "pricing_model, premium_type, premium_value, basis_reference) "
             "VALUES (:cid, :no, :typ, 'DEMO-P1', 'GESAMTKONTRAKT', :total, :unit, false, 'aktiv', :t, "
             ":cdat, :vfrom, :vto, :ts, 'MATIF', 'AUFSCHLAG', :prem, :sym)"),
        {"cid": cid, "no": no, "typ": typ, "total": total, "unit": unit, "t": TENANT,
         "cdat": now - timedelta(days=40), "vfrom": now - timedelta(days=40), "vto": valid_to, "ts": now,
         "prem": premium, "sym": symbol},
    )
    db.execute(
        text("INSERT INTO domain_ops.kon_contract_line "
             "(line_id, contract_id, position_no, article_id, description1, qty_contract, is_bio, is_matif, tenant_id, created_at) "
             "VALUES (:lid, :cid, 1, :art, :art, :qty, false, true, :t, :ts)"),
        {"lid": lid, "cid": cid, "art": article, "qty": total, "t": TENANT, "ts": now},
    )
    for i, (menge, preis) in enumerate(fixings, start=1):
        db.execute(
            text("INSERT INTO domain_ops.kon_contract_fixing "
                 "(fixing_id, contract_id, line_id, fixing_no, quantity, matif_price, premium, "
                 "effective_price, matif_reference, bediener, tenant_id, fixing_date, created_at) "
                 "VALUES (:fid, :cid, :lid, :no, :q, :mp, :pr, :eff, :sym, 'SEED', :t, :fd, :ts)"),
            {"fid": str(uuid.uuid4()), "cid": cid, "lid": lid, "no": i, "q": menge, "mp": preis,
             "pr": premium, "eff": preis + premium, "sym": symbol, "t": TENANT,
             "fd": now - timedelta(days=20 - i * 5), "ts": now},
        )
    db.execute(
        text("INSERT INTO domain_ops.matif_quote (quote_id, symbol, quote_date, price, unit, source, tenant_id) "
             "VALUES (:qid, :sym, :d, :p, :u, 'SEED', :t) "
             "ON CONFLICT (tenant_id, symbol, quote_date) DO UPDATE SET price = EXCLUDED.price"),
        {"qid": str(uuid.uuid4()), "sym": symbol, "d": now.date(), "p": quote_price, "u": unit, "t": TENANT},
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
        if not _exists(db, "DEMO-KT-004"):
            # MATIF-Verkaufskontrakt: 300/500 t fixiert (Ø effektiv 220,33), Markt 208 + Prämie 12.
            _matif_contract(db, "DEMO-KT-004", "VERKAUF", 500, "t", now + timedelta(days=60),
                            "Weizen B MATIF", "MATIF-WEIZEN-DEZ26", 12.0,
                            [(200, 210.0), (100, 205.0)], 208.0)
            created.append("DEMO-KT-004")
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
