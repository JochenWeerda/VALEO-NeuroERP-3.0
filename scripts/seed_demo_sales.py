#!/usr/bin/env python3
"""Demo-Seed: Order-to-Cash (Angebot→Auftrag→Lieferschein→Rechnung) für DOM-SALES-004.

Idempotent (Präfix ``DEMO-``). Erzeugt eine vollständige O2C-Kette sowie einen
Auftrag ohne Lieferschein (Lücke), damit die O2C-Sicht (/api/v1/sales/o2c) mit
echten Daten verifizierbar ist. Tenant = Dev-Standardtenant.

Lauf:
    docker exec valeo-neuro-erp-backend python scripts/seed_demo_sales.py

Optional danach (Tour-Stopp mit Referenz DEMO-LS-001, LOG-SPINE-001):
    python scripts/seed_demo_logistics_spine.py
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"
CUST = "DEMO-CUST-001"
CUST_NAME = "Demo Landhandel Nord eG"


def _exists(db, order_number: str) -> bool:
    return bool(db.execute(
        text("SELECT 1 FROM domain_crm.sales_orders WHERE order_number = :o AND tenant_id = :t"),
        {"o": order_number, "t": TENANT},
    ).first())


def _offer(db, nummer: str, total: float) -> str:
    oid = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO domain_crm.sales_offers "
             "(id, tenant_id, offer_number, customer_id, customer_name, subject, total_amount, currency, status) "
             "VALUES (:id, :t, :nr, :cid, :cn, :subj, :total, 'EUR', 'angenommen')"),
        {"id": oid, "t": TENANT, "nr": nummer, "cid": CUST, "cn": CUST_NAME,
         "subj": "Futtermittel Q3", "total": total},
    )
    return oid


def _order(db, nummer: str, offer_id, total: float, positionen: list[dict]) -> str:
    oid = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO domain_crm.sales_orders "
             "(id, tenant_id, sales_offer_id, order_number, customer_id, customer_name, subject, "
             "total_amount, currency, status) "
             "VALUES (:id, :t, :off, :nr, :cid, :cn, :subj, :total, 'EUR', 'bestaetigt')"),
        {"id": oid, "t": TENANT, "off": offer_id, "nr": nummer, "cid": CUST, "cn": CUST_NAME,
         "subj": "Futtermittel Q3", "total": total},
    )
    for p in positionen:
        db.execute(
            text("INSERT INTO domain_crm.sales_order_items "
                 "(id, tenant_id, order_id, line_number, article_number, description, quantity, unit, "
                 "unit_price, line_total) "
                 "VALUES (:id, :t, :oid, :ln, :anr, :desc, :qty, :unit, :price, :lt)"),
            {"id": str(uuid.uuid4()), "t": TENANT, "oid": oid, "ln": p["ln"], "anr": p["artikel_nr"],
             "desc": p["bezeichnung"], "qty": p["menge"], "unit": p["einheit"],
             "price": p["preis"], "lt": round(p["menge"] * p["preis"], 2)},
        )
    return oid


def _delivery(db, order_id: str, nummer: str, invoice_number: str | None) -> None:
    db.execute(
        text("INSERT INTO domain_sales.delivery_notes "
             "(id, tenant_id, delivery_note_number, sales_order_id, customer_id, delivery_date, "
             "status, is_delivered, invoice_number, created_at, updated_at) "
             "VALUES (:id, :t, :nr, :oid, :cid, :dt, 'geliefert', true, :inv, :ts, :ts)"),
        {"id": str(uuid.uuid4()), "t": TENANT, "nr": nummer, "oid": order_id, "cid": CUST,
         "dt": date.today(), "inv": invoice_number, "ts": datetime.utcnow()},
    )


def _ensure_ls_positions(db) -> bool:
    """Lieferschein-Positionen für DEMO-LS-001 (DOM-SALES-004.2): MILCHLEISTUNG-18
    25/25 (vollständig), MINERAL-RIND 3/5 (teilgeliefert). Idempotent."""
    dn = db.execute(
        text("SELECT id FROM domain_sales.delivery_notes WHERE delivery_note_number = 'DEMO-LS-001' "
             "AND tenant_id = :t"), {"t": TENANT},
    ).scalar()
    if not dn:
        return False
    if db.execute(text("SELECT 1 FROM domain_sales.delivery_note_positions WHERE delivery_note_id = :d LIMIT 1"),
                  {"d": dn}).first():
        return False
    for pos, anr, bez, menge, preis in [
        (1, "MILCHLEISTUNG-18", "Milchleistungsfutter 18/3", 25, 320.0),
        (2, "MINERAL-RIND", "Mineralfutter Rind", 3, 900.0),
    ]:
        db.execute(
            text("INSERT INTO domain_sales.delivery_note_positions "
                 "(id, delivery_note_id, pos_nr, artikel_nr, bezeichnung, menge, einheit, netto_preis, netto_betrag) "
                 "VALUES (:id, :d, :p, :a, :b, :m, 't', :pr, :nb)"),
            {"id": str(uuid.uuid4()), "d": dn, "p": pos, "a": anr, "b": bez, "m": menge,
             "pr": preis, "nb": round(menge * preis, 2)},
        )
    return True


def _ensure_customer_credit(db) -> bool:
    """Kundensatz DEMO-CUST-001 mit Kreditlimit (DOM-SALES-004.3). Exposure aus
    offenen Aufträgen = 17.300 € bei Limit 20.000 € → Ampel „warnung". Idempotent."""
    exists = db.execute(text("SELECT credit_limit FROM domain_crm.customers WHERE id = :id AND tenant_id = :t"),
                        {"id": CUST, "t": TENANT}).mappings().first()
    if exists is None:
        db.execute(
            text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, credit_limit) "
                 "VALUES (:id, :t, :nr, :name, 20000)"),
            {"id": CUST, "t": TENANT, "nr": CUST, "name": CUST_NAME},
        )
        return True
    if not exists.get("credit_limit"):
        db.execute(text("UPDATE domain_crm.customers SET credit_limit = 20000 WHERE id = :id AND tenant_id = :t"),
                   {"id": CUST, "t": TENANT})
        return True
    return False


def seed() -> dict:
    db = SessionLocal()
    created = []
    try:
        if not _exists(db, "DEMO-AUF-001"):
            off1 = _offer(db, "DEMO-ANG-001", 12500.0)
            o1 = _order(db, "DEMO-AUF-001", off1, 12500.0, [
                {"ln": 1, "artikel_nr": "MILCHLEISTUNG-18", "bezeichnung": "Milchleistungsfutter 18/3", "menge": 25, "einheit": "t", "preis": 320.0},
                {"ln": 2, "artikel_nr": "MINERAL-RIND", "bezeichnung": "Mineralfutter Rind", "menge": 5, "einheit": "t", "preis": 900.0},
            ])
            _delivery(db, o1, "DEMO-LS-001", "DEMO-RE-001")  # vollständige Kette
            created.append("DEMO-AUF-001")

        if not _exists(db, "DEMO-AUF-002"):
            off2 = _offer(db, "DEMO-ANG-002", 4800.0)
            _order(db, "DEMO-AUF-002", off2, 4800.0, [
                {"ln": 1, "artikel_nr": "SCHWEIN-MAST", "bezeichnung": "Schweinemastfutter", "menge": 15, "einheit": "t", "preis": 320.0},
            ])  # kein Lieferschein → Lücke
            created.append("DEMO-AUF-002")

        if _ensure_ls_positions(db):
            created.append("DEMO-LS-001-Positionen")

        if _ensure_customer_credit(db):
            created.append("DEMO-CUST-001-Kreditlimit")

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
