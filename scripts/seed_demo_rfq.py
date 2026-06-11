#!/usr/bin/env python3
"""Demo-Seed: RFQ mit Angeboten für Beschaffungs-Anfrageprozess.

Erzeugt idempotent eine DEMO-RFQ für Weizen mit zwei Angeboten (Preisvergleich).
Voraussetzung: `scripts/seed_demo_procurement.py` (Lieferant DEMO-LF-001).

Lauf:
    python -m scripts.seed_demo_rfq
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"
DEMO_NOTES = "DEMO-RFQ-WEIZEN-2026"


def seed() -> dict:
    db = SessionLocal()
    try:
        existing = db.execute(
            text(
                "SELECT id FROM domain_einkauf.rfq_requests "
                "WHERE tenant_id = :t AND notes = :notes LIMIT 1"
            ),
            {"t": TENANT, "notes": DEMO_NOTES},
        ).first()
        if existing:
            return {"skipped": True, "rfq_id": int(existing[0])}

        lf = db.execute(
            text("SELECT id FROM domain_einkauf.lieferanten WHERE tenant_id = :t LIMIT 1"),
            {"t": TENANT},
        ).first()
        if not lf:
            return {"skipped": True, "reason": "Kein Lieferant — zuerst seed_demo_procurement ausführen"}

        lieferant_id = str(lf[0])
        rfq = db.execute(
            text(
                "INSERT INTO domain_einkauf.rfq_requests "
                "(article_id, quantity, needed_by_date, notes, status, tenant_id) "
                "VALUES (:art, :qty, :nbd, :notes, 'VERSENDET', :t) "
                "RETURNING id"
            ),
            {
                "art": "WEIZEN-A",
                "qty": 200,
                "nbd": date.today(),
                "notes": DEMO_NOTES,
                "t": TENANT,
            },
        ).fetchone()
        rfq_id = int(rfq[0])

        for supplier, price, days in (
            (lieferant_id, 218.50, 7),
            (lieferant_id, 221.00, 5),
        ):
            db.execute(
                text(
                    "INSERT INTO domain_einkauf.rfq_quotes "
                    "(rfq_id, supplier_id, unit_price, delivery_days, notes, status, tenant_id) "
                    "VALUES (:rid, :sid, :price, :days, :note, 'OFFEN', :t)"
                ),
                {
                    "rid": rfq_id,
                    "sid": supplier,
                    "price": price,
                    "days": days,
                    "note": f"DEMO-Angebot {price}",
                    "t": TENANT,
                },
            )

        db.execute(
            text(
                "UPDATE domain_einkauf.rfq_requests SET status = 'BEWERTET' "
                "WHERE id = :id AND tenant_id = :t"
            ),
            {"id": rfq_id, "t": TENANT},
        )
        db.commit()
        return {"created": True, "rfq_id": rfq_id}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import json

    print(json.dumps(seed(), ensure_ascii=False))
