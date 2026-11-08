"""Physical flush transfer, sharing the caller's transaction and trusted tenant."""
from decimal import Decimal

from sqlalchemy import text

from app.core.uuid7 import uuid7


def book_flush_charge(service, *, warehouse_id, from_cell_id, to_cell_id,
                      material_id, quantity, actor, reference):
    quantity = Decimal(str(quantity))
    if not quantity.is_finite() or quantity <= 0:
        raise ValueError("Spuelmenge muss endlich und positiv sein")
    if from_cell_id == to_cell_id:
        raise ValueError("Quelle und Ziel muessen verschieden sein")
    db, tenant = service.db, service.tenant_id
    try:
        cells = {}
        for cell_id in sorted((from_cell_id, to_cell_id)):
            row = db.execute(text("""
                SELECT * FROM domain_inventory.silo_cells
                WHERE id=:id AND tenant_id=:tid AND warehouse_id=:wid
                  AND is_active=true FOR UPDATE
            """), {"id": cell_id, "tid": tenant, "wid": warehouse_id}).mappings().first()
            if row is None:
                raise ValueError("Aktive Zelle im angeforderten Lager nicht gefunden")
            cells[cell_id] = row
        source, target = cells[from_cell_id], cells[to_cell_id]
        article = db.execute(text("""
            SELECT id FROM domain_inventory.articles WHERE id=:id AND tenant_id=:tid
        """), {"id": material_id, "tid": tenant}).first()
        if article is None:
            raise ValueError("Spuelmaterial im Mandanten nicht gefunden")
        before = [Decimal(str(cell["current_stock_kg"] or 0)) for cell in (source, target)]
        after = [before[0] - quantity, before[1] + quantity]
        if after[0] < 0:
            raise ValueError("Unzureichender Quellbestand")
        capacity = Decimal(str(target["capacity_kg"] or 0))
        if capacity > 0 and after[1] > capacity:
            raise ValueError("Zielkapazitaet ueberschritten")
        for cell, stock in zip((source, target), before):
            if cell["qs_status"] != "frei":
                raise ValueError("Zelle ist nicht freigegeben")
            if stock > 0 and str(cell["current_material_id"] or "") != material_id:
                raise ValueError("Material stimmt nicht mit dem Zellbestand ueberein")
        nodes = []
        for cell_id in (from_cell_id, to_cell_id):
            node = db.execute(text("""
                SELECT id FROM domain_inventory.material_flow_nodes
                WHERE ref_type='silo_cell' AND ref_id=:cid
                  AND tenant_id=:tid AND warehouse_id=:wid
            """), {"cid": cell_id, "tid": tenant, "wid": warehouse_id}).first()
            nodes.append(str(node.id) if node else None)
        if not all(nodes):
            raise ValueError("Vollstaendige Spuelroute erforderlich")
        route = service.validate_route(warehouse_id=warehouse_id, from_node_id=nodes[0],
                                       to_node_id=nodes[1], material_id=material_id, commit=False)
        if not route["ok"]:
            raise ValueError("Spuelroute ist nicht freigegeben")
        ref = reference or f"FLUSH-{uuid7()}"
        movement_ids = [str(uuid7()), str(uuid7())]
        for i, (cell_id, direction) in enumerate(((from_cell_id, "out"), (to_cell_id, "in"))):
            db.execute(text("""
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, article_id, warehouse_id, movement_type, quantity, unit,
                     warehouse_location, reference_number, movement_date, notes,
                     booking_user, booked_by, auto_created, ownership_type, tenant_id,
                     previous_stock, new_stock)
                VALUES (:id,:art,:wid,:direction,:qty,'kg',:loc,:ref,CURRENT_DATE,
                        'Spuelcharge',:actor,:actor,true,'owned',:tid,:before,:after)
            """), {"id": movement_ids[i], "art": material_id, "wid": warehouse_id,
                    "direction": direction, "qty": quantity, "loc": cells[cell_id]["cell_code"],
                    "ref": ref, "actor": actor, "tid": tenant, "before": before[i], "after": after[i]})
            db.execute(text("""
                UPDATE domain_inventory.silo_cells SET current_stock_kg=:qty,
                    current_material_id=CASE WHEN :qty=0 THEN NULL ELSE :art END,
                    current_lot_id=CASE WHEN :qty=0 THEN NULL ELSE current_lot_id END,
                    updated_at=NOW()
                WHERE id=:id AND tenant_id=:tid AND warehouse_id=:wid
            """), {"qty": after[i], "art": material_id, "id": cell_id, "tid": tenant, "wid": warehouse_id})
        path = route.get("path", [])
        for left, right in zip(path, path[1:]):
            db.execute(text("""
                UPDATE domain_inventory.material_flow_edges SET flush_required=false
                WHERE from_node_id=:left AND to_node_id=:right
                  AND tenant_id=:tid AND warehouse_id=:wid
            """), {"left": left, "right": right, "tid": tenant, "wid": warehouse_id})
        result = dict(ok=True, flush_reference=ref, from_cell_id=from_cell_id,
                      to_cell_id=to_cell_id, flush_material_id=material_id,
                      flush_quantity_kg=float(quantity), move_out_id=movement_ids[0],
                      move_in_id=movement_ids[1], route_warnings=route.get("warnings", []))
        service._emit_material_flow_hooks(
            sc_event_type="flush_charge_booked", outbox_event_type="inventory.material_flow.flush_charge_booked",
            aggregate_id=warehouse_id, ref_type="silo_flush", ref_id=movement_ids[0],
            ref_label=ref, status_from=source["cell_code"], status_to=target["cell_code"], payload=result)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
