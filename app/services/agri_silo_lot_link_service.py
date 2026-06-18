"""WM-AGRI-LOT-LINK — Sync silo_lots (DOM-SUPPLY) → silo_cells (Materialfluss-Graph)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.agri_material_flow_trace_integration import (
    append_material_flow_supply_chain_event,
    store_material_flow_outbox_best_effort,
)


class AgriSiloLotLinkService:
    """Aggregiert aktive Silo-Lots und spiegelt Bestand auf verknüpfte Silozellen."""

    def __init__(self, db: Session, tenant_id: str, *, trace_hooks_enabled: bool = True) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.trace_hooks_enabled = trace_hooks_enabled

    def sync_cells_for_legacy_silo(self, legacy_silo_id: str, *, commit: bool = False) -> list[dict]:
        rows = self.db.execute(
            text("""
                SELECT id, warehouse_id, cell_code
                FROM domain_inventory.silo_cells
                WHERE legacy_silo_id = :sid AND tenant_id = :tid AND is_active = true
            """),
            {"sid": legacy_silo_id, "tid": self.tenant_id},
        ).fetchall()
        if not rows:
            return []
        results: list[dict] = []
        for row in rows:
            results.append(
                self.sync_cell_from_lots(
                    str(row.id),
                    str(row.warehouse_id),
                    commit=False,
                )
            )
        if commit:
            self.db.commit()
        return results

    def sync_cell_from_lots(self, cell_id: str, warehouse_id: str, *, commit: bool = True) -> dict:
        cell = self.db.execute(
            text("""
                SELECT id, warehouse_id, cell_code, legacy_silo_id,
                       current_stock_kg, current_material_id, current_lot_id
                FROM domain_inventory.silo_cells
                WHERE id = :cid AND warehouse_id = :wid AND tenant_id = :tid AND is_active = true
            """),
            {"cid": cell_id, "wid": warehouse_id, "tid": self.tenant_id},
        ).fetchone()
        if not cell:
            raise ValueError("Silozelle nicht gefunden")
        cell_d = dict(cell._mapping)
        legacy_silo_id = cell_d.get("legacy_silo_id")
        if not legacy_silo_id:
            raise ValueError("Silozelle hat kein legacy_silo_id — Mapping zuerst per PATCH setzen")

        silo = self.db.execute(
            text("""
                SELECT id FROM domain_inventory.silos
                WHERE id = :sid AND tenant_id = :tid AND is_active = true
            """),
            {"sid": legacy_silo_id, "tid": self.tenant_id},
        ).fetchone()
        if not silo:
            raise ValueError("Legacy-Silo nicht gefunden oder inaktiv")

        lots = self.db.execute(
            text("""
                SELECT id, article_id, quantity_tons, virtual_lot_number, created_at
                FROM domain_inventory.silo_lots
                WHERE silo_id = :sid AND tenant_id = :tid AND status = 'active'
                  AND quantity_tons > 0
                ORDER BY quantity_tons DESC, created_at DESC
            """),
            {"sid": legacy_silo_id, "tid": self.tenant_id},
        ).fetchall()

        stock_kg = Decimal("0")
        primary_lot_id: str | None = None
        primary_material_id: str | None = None
        primary_lot_label: str | None = None
        lot_count = 0

        for lot in lots:
            lot_d = dict(lot._mapping)
            qty_t = Decimal(str(lot_d.get("quantity_tons") or "0"))
            if qty_t <= 0:
                continue
            lot_count += 1
            stock_kg += qty_t * Decimal("1000")
            if primary_lot_id is None:
                primary_lot_id = str(lot_d["id"])
                primary_material_id = lot_d.get("article_id")
                primary_lot_label = str(lot_d.get("virtual_lot_number") or primary_lot_id)

        prev_stock = Decimal(str(cell_d.get("current_stock_kg") or "0"))

        self.db.execute(
            text("""
                UPDATE domain_inventory.silo_cells
                SET current_stock_kg = :stock,
                    current_material_id = :mat,
                    current_lot_id = :lot,
                    updated_at = NOW()
                WHERE id = :cid AND tenant_id = :tid
            """),
            {
                "stock": float(stock_kg),
                "mat": primary_material_id,
                "lot": primary_lot_id,
                "cid": cell_id,
                "tid": self.tenant_id,
            },
        )

        result = {
            "ok": True,
            "cell_id": cell_id,
            "warehouse_id": warehouse_id,
            "legacy_silo_id": str(legacy_silo_id),
            "active_lot_count": lot_count,
            "current_stock_kg": float(stock_kg),
            "current_material_id": primary_material_id,
            "current_lot_id": primary_lot_id,
            "primary_lot_label": primary_lot_label,
            "previous_stock_kg": float(prev_stock),
        }

        if self.trace_hooks_enabled:
            append_material_flow_supply_chain_event(
                self.db,
                self.tenant_id,
                event_type="silo_lot_synced",
                ref_type="silo_cell",
                ref_id=cell_id,
                ref_label=str(cell_d.get("cell_code") or cell_id),
                status_from=str(float(prev_stock)),
                status_to=str(float(stock_kg)),
                payload=result,
                ticket_id=None,
            )
            store_material_flow_outbox_best_effort(
                self.db,
                self.tenant_id,
                event_type="inventory.material_flow.silo_lot_synced",
                aggregate_id=warehouse_id,
                payload=result,
            )

        if commit:
            self.db.commit()
        return result
