"""WM-AGRI-LOT-LINK-001: Waage/WE-Lot in Materialfluss-Silozelle buchen."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.agri_material_flow_trace_integration import (
    append_material_flow_supply_chain_event,
    store_material_flow_outbox_best_effort,
)


class AgriLotLinkBookingService:
    """Transaktionaler Link von aktivem `silo_lots`-Lot zu `silo_cells`."""

    def __init__(self, db: Session, tenant_id: str, *, trace_hooks_enabled: bool = True) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.trace_hooks_enabled = trace_hooks_enabled

    def book_lot_to_cell(
        self,
        *,
        lot_id: str,
        target_cell_id: str,
        warehouse_id: str,
        quantity_kg: Decimal | None = None,
        booked_by: str = "system",
        reference: str | None = None,
    ) -> dict:
        lot = self.db.execute(
            text("""
                SELECT l.id, l.silo_id, l.virtual_lot_number, l.source_ticket_id,
                       l.article_id, l.quantity_tons, l.status,
                       s.silo_number
                FROM domain_inventory.silo_lots l
                JOIN domain_inventory.silos s
                  ON s.id = l.silo_id AND s.tenant_id = l.tenant_id
                WHERE l.id = :lot_id
                  AND l.tenant_id = :tid
                  AND l.status = 'active'
                  AND s.is_active = true
            """),
            {"lot_id": lot_id, "tid": self.tenant_id},
        ).fetchone()
        if not lot:
            raise ValueError("Aktives Silo-Lot nicht gefunden")
        lot_d = dict(lot._mapping)

        cell = self.db.execute(
            text("""
                SELECT id, warehouse_id, cell_code, capacity_kg, current_stock_kg,
                       current_material_id, current_lot_id, qs_status, legacy_silo_id
                FROM domain_inventory.silo_cells
                WHERE id = :cell_id
                  AND warehouse_id = :warehouse_id
                  AND tenant_id = :tid
                  AND is_active = true
            """),
            {"cell_id": target_cell_id, "warehouse_id": warehouse_id, "tid": self.tenant_id},
        ).fetchone()
        if not cell:
            raise ValueError("Ziel-Silozelle nicht gefunden")
        cell_d = dict(cell._mapping)

        if str(cell_d.get("qs_status") or "") == "gesperrt":
            raise ValueError("Ziel-Silozelle ist QS-gesperrt")

        article_id = lot_d.get("article_id")
        if not article_id:
            raise ValueError("Silo-Lot hat keinen article_id und kann nicht gebucht werden")

        lot_qty_kg = Decimal(str(lot_d.get("quantity_tons") or "0")) * Decimal("1000")
        qty = Decimal(str(quantity_kg if quantity_kg is not None else lot_qty_kg))
        if qty <= Decimal("0"):
            raise ValueError("quantity_kg muss positiv sein")
        if qty > lot_qty_kg:
            raise ValueError("quantity_kg ueberschreitet die Lot-Restmenge")

        current_stock = Decimal(str(cell_d.get("current_stock_kg") or "0"))
        capacity_kg = Decimal(str(cell_d.get("capacity_kg") or "0"))
        new_stock = current_stock + qty
        if capacity_kg > Decimal("0") and new_stock > capacity_kg:
            raise ValueError("Kapazitaet der Ziel-Silozelle wuerde ueberschritten")

        current_material_id = cell_d.get("current_material_id")
        if current_material_id and str(current_material_id) != str(article_id):
            raise ValueError("Materialkonflikt in Ziel-Silozelle")
        current_lot_id = cell_d.get("current_lot_id")
        if current_lot_id and str(current_lot_id) != str(lot_id):
            raise ValueError("Lotkonflikt in Ziel-Silozelle")

        ref = reference or f"LOT-LINK-{lot_d['virtual_lot_number']}-{cell_d['cell_code']}"
        existing = self.db.execute(
            text("""
                SELECT id
                FROM domain_inventory.inventory_stock_movements
                WHERE tenant_id = :tid
                  AND reference_number = :ref
                  AND source_document_type = 'silo_lot_link'
                  AND source_document_id = :lot_id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"tid": self.tenant_id, "ref": ref, "lot_id": lot_id},
        ).fetchone()
        if existing:
            return {
                "ok": True,
                "idempotent": True,
                "movement_id": str(existing.id),
                "cell_id": target_cell_id,
                "warehouse_id": warehouse_id,
                "lot_id": lot_id,
                "article_id": str(article_id),
                "quantity_kg": float(qty),
                "cell_stock_kg": float(current_stock),
                "reference": ref,
            }

        movement_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
                     warehouse_location, reference_number, movement_date, movement_time,
                     notes, booking_user, auto_created, ownership_type, tenant_id,
                     weighing_ticket_id, source_document_type, source_document_id, created_at)
                VALUES (:id, :article_id, :warehouse_id, 'in', :quantity, 'kg', :charge,
                        :warehouse_location, :reference_number, :movement_date, NOW()::time,
                        :notes, :booking_user, true, 'owned', :tenant_id,
                        :weighing_ticket_id, 'silo_lot_link', :source_document_id, NOW())
            """),
            {
                "id": movement_id,
                "article_id": str(article_id),
                "warehouse_id": warehouse_id,
                "quantity": float(qty),
                "charge": lot_id,
                "warehouse_location": str(cell_d.get("cell_code")),
                "reference_number": ref,
                "movement_date": date.today(),
                "notes": f"WE/Waage-Lot {lot_d.get('virtual_lot_number')} in Silozelle {cell_d.get('cell_code')}",
                "booking_user": booked_by,
                "tenant_id": self.tenant_id,
                "weighing_ticket_id": lot_d.get("source_ticket_id"),
                "source_document_id": lot_id,
            },
        )
        self.db.execute(
            text("""
                UPDATE domain_inventory.silo_cells
                SET current_stock_kg = :stock,
                    current_material_id = :article_id,
                    current_lot_id = :lot_id,
                    legacy_silo_id = COALESCE(legacy_silo_id, :legacy_silo_id),
                    updated_at = NOW()
                WHERE id = :cell_id
                  AND warehouse_id = :warehouse_id
                  AND tenant_id = :tid
            """),
            {
                "stock": float(new_stock),
                "article_id": str(article_id),
                "lot_id": lot_id,
                "legacy_silo_id": str(lot_d["silo_id"]),
                "cell_id": target_cell_id,
                "warehouse_id": warehouse_id,
                "tid": self.tenant_id,
            },
        )

        result = {
            "ok": True,
            "idempotent": False,
            "movement_id": movement_id,
            "cell_id": target_cell_id,
            "warehouse_id": warehouse_id,
            "lot_id": lot_id,
            "silo_id": str(lot_d["silo_id"]),
            "article_id": str(article_id),
            "quantity_kg": float(qty),
            "cell_stock_kg": float(new_stock),
            "previous_cell_stock_kg": float(current_stock),
            "reference": ref,
            "source_ticket_id": lot_d.get("source_ticket_id"),
        }
        if self.trace_hooks_enabled:
            append_material_flow_supply_chain_event(
                self.db,
                self.tenant_id,
                event_type="silo_lot_link_booked",
                ref_type="silo_cell",
                ref_id=target_cell_id,
                ref_label=str(cell_d.get("cell_code") or target_cell_id),
                status_from=str(float(current_stock)),
                status_to=str(float(new_stock)),
                payload=result,
                ticket_id=lot_d.get("source_ticket_id"),
            )
            store_material_flow_outbox_best_effort(
                self.db,
                self.tenant_id,
                event_type="inventory.material_flow.silo_lot_link_booked",
                aggregate_id=warehouse_id,
                payload=result,
            )
        self.db.commit()
        return result
