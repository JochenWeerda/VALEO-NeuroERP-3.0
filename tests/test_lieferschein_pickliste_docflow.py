"""Lieferschein (DocFlow) -> WMS-Pickliste -> Lagerabgang genau einmal (BELEG-052 Phase 1, 09.11.2026).

Der Lagerabgang eines Lieferscheins entsteht beim Bestaetigen der Pickliste. Bis 09.11.2026 scheiterte jede Anlage
einer Pickliste am Schema (Nummer, Mandant und Sollmenge fehlten - es gab keine einzige), eine wiederholte Bestaetigung
haette den Bestand ein zweites Mal ausgebucht, und die Pickliste kannte nur den Altspeicher des Lieferscheins.
Gegen den frischen Pruefstand, in einer Transaktion, die zurueckgerollt wird.
"""
from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def lager():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    if not verbindung.execute(sa.text(
            "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_inventory' "
            "AND table_name = 'pick_list_lines' AND column_name = 'status'")).scalar():
        import importlib.util
        from pathlib import Path

        from alembic.migration import MigrationContext
        from alembic.operations import Operations

        datei = Path(__file__).resolve().parents[1] / "alembic/versions/wms_pickposition_stand_20261110.py"
        spec = importlib.util.spec_from_file_location("m", datei)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        with Operations.context(MigrationContext.configure(verbindung)):
            modul.upgrade()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t = f"pl-{uuid.uuid4().hex[:8]}"
    ids = {k: str(uuid.uuid4()) for k in ("lager", "zone", "platz", "artikel", "bestand", "ls", "pos")}
    nr = f"W-{uuid.uuid4().hex[:6]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                      "VALUES (:id, :t, 'L1', 'Hauptlager')"), {"id": ids["lager"], "t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.warehouse_zones (id, warehouse_id, zone_code, name, tenant_id) "
                      "VALUES (:id, :w, 'Z1', 'Halle 1', :t)"), {"id": ids["zone"], "w": ids["lager"], "t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.warehouse_bins (id, zone_id, warehouse_id, bin_code, tenant_id) "
                      "VALUES (:id, :z, :w, 'F1', :t)"), {"id": ids["platz"], "z": ids["zone"], "w": ids["lager"], "t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit, current_stock) "
                      "VALUES (:id, :t, :nr, 'Weizen A', 'kg', 5000)"), {"id": ids["artikel"], "t": t, "nr": nr})
    s.execute(sa.text("INSERT INTO domain_inventory.bin_stock (id, bin_id, article_id, quantity_kg, tenant_id) "
                      "VALUES (:id, :b, :a, 5000, :t)"), {"id": ids["bestand"], "b": ids["platz"], "a": ids["artikel"], "t": t})
    s.execute(sa.text(
        "INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, status, source_system, "
        "currency, total_net, total_tax, total_gross, document_date, version, created_at, updated_at) "
        "VALUES (:id, :t, 'sales_delivery', :nr, 'open', 'test', 'EUR', 0, 0, 0, NOW(), 1, NOW(), NOW())"),
        {"id": ids["ls"], "t": t, "nr": f"LS-{uuid.uuid4().hex[:6]}"})
    s.execute(sa.text(
        "INSERT INTO domain_docflow.document_items (id, tenant_id, header_id, line_number, article_number, quantity, "
        "unit, unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, created_at, "
        "updated_at) VALUES (:id, :t, :h, 1, :nr, 30, 'dt', 0, 0, 0, 0, 0, 0, NOW(), NOW())"),
        {"id": ids["pos"], "t": t, "h": ids["ls"], "nr": nr})
    s.flush()
    try:
        yield {"db": s, "t": t, **ids}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _bestand(l) -> float:
    return float(l["db"].execute(sa.text("SELECT quantity_kg FROM domain_inventory.bin_stock WHERE id = :id"),
                                 {"id": l["bestand"]}).scalar())


def test_lieferschein_wird_genau_einmal_ausgebucht(lager):
    from app.services.warehouse_service import WarehouseService

    wms = WarehouseService(db=lager["db"], tenant_id=lager["t"])
    liste = wms.create_pick_list_from_delivery_note(lager["ls"], warehouse_id=lager["lager"])
    assert liste["delivery_note_id"] == lager["ls"]
    zeilen = lager["db"].execute(sa.text(
        "SELECT id, quantity_required, unit, bin_id FROM domain_inventory.pick_list_lines WHERE pick_list_id = :p"),
        {"p": liste["id"]}).mappings().all()
    assert [(float(z["quantity_required"]), z["unit"], z["bin_id"]) for z in zeilen] == [(3000.0, "kg", lager["platz"])]
    zeile = str(zeilen[0]["id"])

    # Teilmenge, dann der Rest: ausgebucht wird nur der Zuwachs
    assert wms.confirm_pick_list(liste["id"], [{"line_id": zeile, "quantity_picked": 1000}])["status"] == "IN_PROGRESS"
    assert _bestand(lager) == 4000.0
    assert wms.confirm_pick_list(liste["id"], [{"line_id": zeile, "quantity_picked": 3000}])["status"] == "COMPLETED"
    assert _bestand(lager) == 2000.0

    kopf = lager["db"].execute(sa.text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"),
                               {"id": lager["ls"]}).scalar()
    assert kopf == "completed"
    historie = lager["db"].execute(sa.text(
        "SELECT command FROM domain_docflow.document_status_history WHERE header_id = :id AND to_status = 'completed'"),
        {"id": lager["ls"]}).scalars().all()
    assert historie == ["deliver"]
    with pytest.raises(ValueError, match="bereits abgeschlossen"):
        wms.confirm_pick_list(liste["id"], [{"line_id": zeile, "quantity_picked": 3000}])
    assert _bestand(lager) == 2000.0


def test_nicht_freigegebener_lieferschein_wird_nicht_kommissioniert(lager):
    from app.services.warehouse_service import WarehouseService

    lager["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET status = 'draft' WHERE id = :id"),
                        {"id": lager["ls"]})
    with pytest.raises(ValueError, match="freigegeben"):
        WarehouseService(db=lager["db"], tenant_id=lager["t"]).create_pick_list_from_delivery_note(lager["ls"])


def test_picklistennummer_laeuft_je_mandant(lager):
    from app.services.warehouse_service import WarehouseService

    wms = WarehouseService(db=lager["db"], tenant_id=lager["t"])
    eins = wms.create_pick_list(lager["lager"], [{"article_id": lager["artikel"], "quantity_required": 1}])
    zwei = wms.create_pick_list(lager["lager"], [{"article_id": lager["artikel"], "quantity_required": 1}])
    nummern = lager["db"].execute(sa.text(
        "SELECT pick_list_number FROM domain_inventory.pick_lists WHERE id IN (:a, :b) ORDER BY pick_list_number"),
        {"a": eins["id"], "b": zwei["id"]}).scalars().all()
    assert nummern == [1, 2]
