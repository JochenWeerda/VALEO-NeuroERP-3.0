"""Physical flush regression against the existing shared probe; own rows rolled back."""
import os
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService


@pytest.fixture
def flush_sql():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Shared TEST_DATABASE_URL required")
    assert make_url(url).database == "valeo_probe" or os.environ.get("GITHUB_ACTIONS") == "true"
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        ids = {key: str(uuid4()) for key in ("tenant", "warehouse", "system", "article", "source", "target", "n1", "n2", "n3")}
        def execute(sql, **params):
            return connection.execute(text(sql), {**ids, **params})
        execute("INSERT INTO domain_shared.tenants(id,name) VALUES(:tenant,'synthetic flush SQL')")
        execute("INSERT INTO domain_inventory.articles(id,article_number,name,tenant_id) VALUES(:article,:article,'synthetic',:tenant)")
        execute("INSERT INTO domain_inventory.warehouses(id,warehouse_code,name,tenant_id) VALUES(:warehouse,'flush-test','synthetic',:tenant)")
        execute("INSERT INTO domain_inventory.silo_systems(id,warehouse_id,system_code,name,tenant_id) VALUES(:system,:warehouse,'flush-test','synthetic',:tenant)")
        for key, stock in (("source", 100), ("target", 20)):
            execute("""INSERT INTO domain_inventory.silo_cells
                (id,silo_system_id,warehouse_id,cell_code,name,tenant_id,current_stock_kg,current_material_id,capacity_kg)
                VALUES(:id,:system,:warehouse,:code,'synthetic',:tenant,:stock,:article,200)""",
                    id=ids[key], code=key, stock=stock)
        for key, ref in (("n1", "source"), ("n2", "target"), ("n3", "target")):
            execute("""INSERT INTO domain_inventory.material_flow_nodes
                (id,warehouse_id,node_type,ref_type,ref_id,code,name,tenant_id)
                VALUES(:id,:warehouse,'silo_cell',:ref_type,:ref,:code,'synthetic',:tenant)""",
                    id=ids[key], ref=ids[ref], ref_type="silo_cell" if key != "n3" else None, code=key)
        for left, right in (("n1", "n2"), ("n1", "n3")):
            execute("""INSERT INTO domain_inventory.material_flow_edges
                (id,warehouse_id,from_node_id,to_node_id,tenant_id,flush_required)
                VALUES(:id,:warehouse,:left,:right,:tenant,true)""",
                    id=str(uuid4()), left=ids[left], right=ids[right])
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        service = AgriSiloMaterialFlowService(session, ids["tenant"], trace_hooks_enabled=False)
        args = dict(warehouse_id=ids["warehouse"], from_cell_id=ids["source"], to_cell_id=ids["target"],
                    flush_material_id=ids["article"], flush_quantity_kg=Decimal("30"), booked_by="synthetic-verified-actor")
        try:
            yield service, args, execute, ids
        finally:
            session.close()
            transaction.rollback()
    engine.dispose()


def test_flush_physically_moves_stock_and_only_clears_traversed_edge(flush_sql):
    service, args, execute, ids = flush_sql
    result = service.book_flush_charge(**args)
    assert result["ok"]
    stocks = dict(execute("SELECT cell_code,current_stock_kg FROM domain_inventory.silo_cells WHERE tenant_id=:tenant").all())
    assert stocks == {"source": Decimal("70"), "target": Decimal("50")}
    movements = execute("""SELECT movement_type,quantity,previous_stock,new_stock,ownership_type,booked_by
        FROM domain_inventory.inventory_stock_movements WHERE tenant_id=:tenant ORDER BY movement_type""").all()
    assert movements == [("in", 30, 20, 50, "owned", args["booked_by"]), ("out", 30, 100, 70, "owned", args["booked_by"])]
    flags = dict(execute("SELECT to_node_id,flush_required FROM domain_inventory.material_flow_edges WHERE tenant_id=:tenant").all())
    assert flags == {ids["n2"]: False, ids["n3"]: True}


@pytest.mark.parametrize("change", ["overdraw", "capacity", "warehouse", "tenant", "same", "nan", "material", "blocked"])
def test_flush_rejects_without_partial_movements(flush_sql, change):
    service, args, execute, ids = flush_sql
    if change == "overdraw": args["flush_quantity_kg"] = Decimal("101")
    if change == "capacity": execute("UPDATE domain_inventory.silo_cells SET capacity_kg=25 WHERE id=:target")
    if change == "warehouse": args["warehouse_id"] = str(uuid4())
    if change == "tenant": service.tenant_id = str(uuid4())
    if change == "same": args["to_cell_id"] = args["from_cell_id"]
    if change == "nan": args["flush_quantity_kg"] = Decimal("NaN")
    if change == "material": args["flush_material_id"] = str(uuid4())
    if change == "blocked": execute("UPDATE domain_inventory.silo_cells SET qs_status='gesperrt' WHERE id=:source")
    with pytest.raises(ValueError): service.book_flush_charge(**args)
    assert execute("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id=:tenant").scalar_one() == 0
    assert execute("SELECT sum(current_stock_kg) FROM domain_inventory.silo_cells WHERE tenant_id=:tenant").scalar_one() == 120


def test_flush_rolls_back_both_movements_and_stocks_if_audit_fails(flush_sql, monkeypatch):
    service, args, execute, ids = flush_sql
    def fail(**kwargs):
        raise RuntimeError("synthetic audit failure")
    monkeypatch.setattr(service, "_emit_material_flow_hooks", fail)
    with pytest.raises(RuntimeError): service.book_flush_charge(**args)
    assert execute("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id=:tenant").scalar_one() == 0
    assert execute("SELECT current_stock_kg FROM domain_inventory.silo_cells WHERE id=:source").scalar_one() == 100


def test_route_audit_cannot_commit_booking_before_later_failure(flush_sql, monkeypatch):
    service, args, execute, ids = flush_sql
    service._trace_hooks_enabled = True
    calls = []
    def hook(**kwargs):
        calls.append(kwargs["sc_event_type"])
        if len(calls) == 2:
            raise RuntimeError("synthetic later audit failure")
    monkeypatch.setattr(service, "_emit_material_flow_hooks", hook)
    with pytest.raises(RuntimeError): service.book_flush_charge(**args)
    assert calls == ["route_validated", "flush_charge_booked"]
    assert execute("SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE tenant_id=:tenant").scalar_one() == 0
    assert execute("SELECT current_stock_kg FROM domain_inventory.silo_cells WHERE id=:source").scalar_one() == 100
