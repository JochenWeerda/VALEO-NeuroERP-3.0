#!/usr/bin/env python3
"""Demo-Seed: Offene Posten (FIBU) für DOM-FIN-004.

Idempotent (Präfix ``DEMO-RE-``). Erzeugt Debitoren-/Kreditoren-OP mit
unterschiedlicher Fälligkeit (nicht fällig / überfällig) und Skonto-Fenster,
damit das OP-Aging-Cockpit (/api/v1/finance/offene-posten) mit echten Daten
verifizierbar ist. Tenant = Dev-Standardtenant.

Lauf: docker exec valeo-neuro-erp-backend python scripts/seed_demo_finance.py
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"


def _exists(db, rechnungsnr: str) -> bool:
    return bool(db.execute(
        text("SELECT 1 FROM domain_erp.offene_posten WHERE rechnungsnr = :r AND tenant_id = :t"),
        {"r": rechnungsnr, "t": TENANT},
    ).first())


def _op(db, **kw) -> None:
    db.execute(
        text("INSERT INTO domain_erp.offene_posten "
             "(id, tenant_id, rechnungsnr, rechnungsdatum, faelligkeit, due_date, konto_typ, "
             "kunde_name, lieferant_name, waehrung, betrag, open_amount, offen, op_status, "
             "dunning_level, zahlbar, skonto_prozent, skonto_bis) "
             "VALUES (:id, :t, :nr, :rdat, :faell, :faell, :typ, :kn, :ln, 'EUR', :betrag, "
             ":offen, :offen, 'offen', :dl, true, :skp, :skb)"),
        {"id": str(uuid.uuid4()), "t": TENANT, "nr": kw["nr"], "rdat": kw["rdat"], "faell": kw["faell"],
         "typ": kw["typ"], "kn": kw.get("kunde"), "ln": kw.get("lieferant"),
         "betrag": kw["betrag"], "offen": kw["offen"], "dl": kw.get("dunning", 0),
         "skp": kw.get("skonto_prozent"), "skb": kw.get("skonto_bis")},
    )


def seed() -> dict:
    db = SessionLocal()
    today = date.today()
    created = []
    try:
        cases = [
            dict(nr="DEMO-RE-100", typ="debitoren", kunde="Hof Janßen GbR", betrag=5000, offen=5000,
                 rdat=today - timedelta(days=44), faell=today - timedelta(days=14), dunning=1),       # überfällig 1-30
            dict(nr="DEMO-RE-101", typ="debitoren", kunde="Milchhof Nord eG", betrag=1200, offen=1200,
                 rdat=today - timedelta(days=2), faell=today + timedelta(days=12),
                 skonto_prozent=2, skonto_bis=today + timedelta(days=5)),                              # nicht fällig + Skonto
            dict(nr="DEMO-RE-102", typ="kreditoren", lieferant="Demo Agrar-Lieferant GmbH", betrag=3400, offen=3400,
                 rdat=today - timedelta(days=5), faell=today + timedelta(days=20)),                    # nicht fällig (Kreditor)
            dict(nr="DEMO-RE-103", typ="debitoren", kunde="Ackerbau Müller KG", betrag=800, offen=800,
                 rdat=today - timedelta(days=95), faell=today - timedelta(days=75), dunning=2),        # überfällig 60+
        ]
        for c in cases:
            if not _exists(db, c["nr"]):
                _op(db, **c)
                created.append(c["nr"])
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
