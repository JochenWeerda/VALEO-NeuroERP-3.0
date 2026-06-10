#!/usr/bin/env python3
"""Demo-Seed: Beschaffung (Bestellung + Wareneingang) für DOM-PROC-004.

Erzeugt idempotent realistische Test-Belege, damit der 3-Wege-Match-Spine
(/api/v1/procurement/match) und die zugehörige UI mit echten Daten verifizierbar
sind. Alle Belege tragen das Präfix ``DEMO-`` und werden bei erneutem Lauf
übersprungen (kein Duplikat). Tenant = Dev-Standardtenant.

Fälle: vollständig geliefert · teilgeliefert · überliefert.

Lauf:
    docker exec valeo-neuro-erp-backend python -m scripts.seed_demo_procurement
    python -m scripts.seed_demo_procurement            # lokal mit DATABASE_URL
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import text

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"


def _exists(db, bestellnummer: str) -> bool:
    return bool(db.execute(
        text("SELECT 1 FROM domain_einkauf.bestellungen WHERE bestellnummer = :b AND tenant_id = :t"),
        {"b": bestellnummer, "t": TENANT},
    ).first())


def _lieferant(db) -> str:
    r = db.execute(text("SELECT id FROM domain_einkauf.lieferanten LIMIT 1")).first()
    if r:
        return str(r[0])
    lid = str(uuid.uuid4())
    db.execute(
        text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
             "VALUES (:id, :t, :nr, :fn)"),
        {"id": lid, "t": TENANT, "nr": "DEMO-LF-001", "fn": "Demo Agrar-Lieferant GmbH"},
    )
    return lid


def _warehouse_location(db) -> tuple[str, str]:
    """Get-or-create ein Demo-Lager + -Lagerplatz (FK-Ziele der WE-Zeilen)."""
    now = datetime.utcnow()
    wh = db.execute(text("SELECT id FROM public.inventory_warehouses WHERE code = 'DEMO-WH'")).first()
    if wh:
        wh_id = str(wh[0])
    else:
        wh_id = str(uuid.uuid4())
        db.execute(
            text("INSERT INTO public.inventory_warehouses (id, code, name, tenant_id, is_active, created_at, updated_at) "
                 "VALUES (:id, 'DEMO-WH', 'Demo-Lager', :t, true, :ts, :ts)"),
            {"id": wh_id, "t": TENANT, "ts": now},
        )
    loc = db.execute(text("SELECT id FROM public.inventory_locations WHERE code = 'DEMO-LOC'")).first()
    if loc:
        loc_id = str(loc[0])
    else:
        loc_id = str(uuid.uuid4())
        db.execute(
            text("INSERT INTO public.inventory_locations (id, warehouse_id, code, location_type, created_at) "
                 "VALUES (:id, :wh, 'DEMO-LOC', 'bulk', :ts)"),
            {"id": loc_id, "wh": wh_id, "ts": now},
        )
    return wh_id, loc_id


def _po(db, lieferant_id: str, nummer: str, positionen: list[dict]) -> str:
    pid = str(uuid.uuid4())
    netto = sum(p["menge"] * p["einzelpreis"] for p in positionen)
    db.execute(
        text("INSERT INTO domain_einkauf.bestellungen "
             "(id, tenant_id, bestellnummer, lieferant_id, bestelldatum, status, waehrung, netto_summe, brutto_summe) "
             "VALUES (:id, :t, :nr, :lf, :dt, 'bestellt', 'EUR', :netto, :brutto)"),
        {"id": pid, "t": TENANT, "nr": nummer, "lf": lieferant_id, "dt": date.today(),
         "netto": netto, "brutto": round(netto * 1.19, 2)},
    )
    for p in positionen:
        db.execute(
            text("INSERT INTO domain_einkauf.bestellung_positionen "
                 "(id, bestellung_id, pos_nr, artikel_nr, artikel_bezeichnung, menge, einheit, "
                 "einzelpreis, netto_betrag, mwst_satz, status) "
                 "VALUES (:id, :bid, :pos, :anr, :abez, :menge, :einheit, :preis, :netto, 19, 'offen')"),
            {"id": str(uuid.uuid4()), "bid": pid, "pos": p["pos"], "anr": p["artikel_nr"],
             "abez": p["bezeichnung"], "menge": p["menge"], "einheit": p["einheit"],
             "preis": p["einzelpreis"], "netto": round(p["menge"] * p["einzelpreis"], 2)},
        )
    return pid


def _gr(db, po_id: str, po_number: str, lieferant_id: str, gr_number: str, zeilen: list[dict],
        wh_id: str, loc_id: str) -> None:
    gid = str(uuid.uuid4())
    now = datetime.utcnow()
    db.execute(
        text("INSERT INTO public.inventory_goods_receipts "
             "(id, tenant_id, gr_number, po_number, po_id, supplier_id, supplier_name, "
             "receipt_date, status, notes, created_by, created_at, updated_at) "
             "VALUES (:id, :t, :grn, :pon, :pid, :sid, :sn, :dt, 'POSTED', '', 'seed', :ts, :ts)"),
        {"id": gid, "t": TENANT, "grn": gr_number, "pon": po_number, "pid": po_id,
         "sid": lieferant_id, "sn": "Demo Agrar-Lieferant GmbH", "dt": now, "ts": now},
    )
    for z in zeilen:
        db.execute(
            text("INSERT INTO public.inventory_goods_receipt_lines "
                 "(id, goods_receipt_id, po_line_number, sku, description, ordered_quantity, "
                 "received_quantity, unit, warehouse_id, location_id, quality_status, notes, created_at) "
                 "VALUES (:id, :gid, :pos, :sku, :desc, :ord, :rec, :unit, :wh, :loc, 'ok', '', :ts)"),
            {"id": str(uuid.uuid4()), "gid": gid, "pos": z["pos"], "sku": z["sku"], "desc": z["bezeichnung"],
             "ord": z["bestellt"], "rec": z["geliefert"], "unit": z["einheit"],
             "wh": wh_id, "loc": loc_id, "ts": now},
        )


def seed() -> dict:
    db = SessionLocal()
    created = []
    try:
        lieferant_id = _lieferant(db)
        wh_id, loc_id = _warehouse_location(db)

        if not _exists(db, "DEMO-PO-001"):
            po1 = _po(db, lieferant_id, "DEMO-PO-001", [
                {"pos": 1, "artikel_nr": "WEIZEN-A", "bezeichnung": "Weizen A-Qualität", "menge": 100, "einheit": "t", "einzelpreis": 220.0},
                {"pos": 2, "artikel_nr": "GERSTE-B", "bezeichnung": "Futtergerste", "menge": 50, "einheit": "t", "einzelpreis": 190.0},
            ])
            _gr(db, po1, "DEMO-PO-001", lieferant_id, "DEMO-GR-001", [
                {"pos": 1, "sku": "WEIZEN-A", "bezeichnung": "Weizen A-Qualität", "bestellt": 100, "geliefert": 100, "einheit": "t"},  # vollständig
                {"pos": 2, "sku": "GERSTE-B", "bezeichnung": "Futtergerste", "bestellt": 50, "geliefert": 30, "einheit": "t"},        # teilgeliefert
            ], wh_id, loc_id)
            created.append("DEMO-PO-001")

        if not _exists(db, "DEMO-PO-002"):
            po2 = _po(db, lieferant_id, "DEMO-PO-002", [
                {"pos": 1, "artikel_nr": "RAPS-00", "bezeichnung": "Raps 00", "menge": 20, "einheit": "t", "einzelpreis": 480.0},
            ])
            _gr(db, po2, "DEMO-PO-002", lieferant_id, "DEMO-GR-002", [
                {"pos": 1, "sku": "RAPS-00", "bezeichnung": "Raps 00", "bestellt": 20, "geliefert": 22, "einheit": "t"},  # überliefert
            ], wh_id, loc_id)
            created.append("DEMO-PO-002")

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
