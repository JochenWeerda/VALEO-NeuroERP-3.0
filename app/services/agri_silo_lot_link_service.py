"""WM-AGRI-LOT-LINK — Sync silo_lots (DOM-SUPPLY) ↔ silo_cells (Materialfluss-Graph)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
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

    def sync_lots_from_transfer(
        self,
        *,
        from_cell_id: str,
        to_cell_id: str,
        quantity_kg: Decimal,
        lot_id: str | None,
        article_id: str,
    ) -> dict:
        """Rücksync WMS-FLOW-001 → silo_lots: Materialtransfer aktualisiert Lot-Mengen.

        Fail-soft: gibt ok=False + reason zurück statt Exception wenn kein Mapping vorhanden.
        Kein eigenes commit — Caller (book_material_transfer) commitet die gesamte Transaktion.
        """
        qty_tons = quantity_kg / Decimal("1000")
        updated: list[str] = []

        # legacy_silo_id für Quell- und Zielzelle ermitteln
        from_row = self.db.execute(
            text("SELECT legacy_silo_id FROM domain_inventory.silo_cells WHERE id = :cid AND tenant_id = :tid"),
            {"cid": from_cell_id, "tid": self.tenant_id},
        ).fetchone()
        to_row = self.db.execute(
            text("SELECT legacy_silo_id FROM domain_inventory.silo_cells WHERE id = :cid AND tenant_id = :tid"),
            {"cid": to_cell_id, "tid": self.tenant_id},
        ).fetchone()

        from_silo_id = str(from_row.legacy_silo_id) if from_row and from_row.legacy_silo_id else None
        to_silo_id = str(to_row.legacy_silo_id) if to_row and to_row.legacy_silo_id else None

        if not from_silo_id and not to_silo_id:
            return {"ok": False, "reason": "Keine legacy_silo_id-Mappings auf Quell-/Zielzelle"}

        # ── Quell-Lot: Menge reduzieren ─────────────────────────────────────
        src_lot = None
        if lot_id:
            src_lot = self.db.execute(
                text("""
                    SELECT id, quantity_tons FROM domain_inventory.silo_lots
                    WHERE id::text = :lid AND tenant_id = :tid AND status = 'active'
                    LIMIT 1
                """),
                {"lid": lot_id, "tid": self.tenant_id},
            ).fetchone()
        elif from_silo_id:
            src_lot = self.db.execute(
                text("""
                    SELECT id, quantity_tons FROM domain_inventory.silo_lots
                    WHERE silo_id = :sid AND tenant_id = :tid AND status = 'active'
                      AND article_id = :art AND quantity_tons > 0
                    ORDER BY quantity_tons DESC, created_at DESC
                    LIMIT 1
                """),
                {"sid": from_silo_id, "art": article_id, "tid": self.tenant_id},
            ).fetchone()

        if src_lot:
            src_new_qty = max(Decimal("0"), Decimal(str(src_lot.quantity_tons)) - qty_tons)
            src_status = "closed" if src_new_qty == Decimal("0") else "active"
            self.db.execute(
                text("""
                    UPDATE domain_inventory.silo_lots
                    SET quantity_tons = :qty, status = :st, updated_at = NOW()
                    WHERE id = :id
                """),
                {"qty": float(src_new_qty), "st": src_status, "id": str(src_lot.id)},
            )
            self.db.execute(
                text("""
                    INSERT INTO domain_inventory.silo_lot_movements
                        (id, silo_lot_id, movement_type, quantity_tons, note, tenant_id, created_at)
                    VALUES (:id, :lid, 'out', :qty, :note, :tid, NOW())
                """),
                {
                    "id": str(uuid7()),
                    "lid": str(src_lot.id),
                    "qty": float(qty_tons),
                    "note": f"WMS-Transfer → Zielzelle {to_cell_id}",
                    "tid": self.tenant_id,
                },
            )
            updated.append(f"src:{src_lot.id}:out:{float(qty_tons)}t")

        # ── Ziel-Lot: Menge erhöhen (falls aktives Lot mit passendem Artikel im Ziel-Silo) ──
        if to_silo_id:
            dest_lot = None
            if lot_id:
                # Bevorzuge gleiches Lot wenn es bereits im Ziel-Silo ist
                dest_lot = self.db.execute(
                    text("""
                        SELECT id, quantity_tons FROM domain_inventory.silo_lots
                        WHERE id::text = :lid AND silo_id = :sid AND tenant_id = :tid AND status = 'active'
                        LIMIT 1
                    """),
                    {"lid": lot_id, "sid": to_silo_id, "tid": self.tenant_id},
                ).fetchone()
            if not dest_lot:
                # Aktivstes Lot mit passendem Artikel im Ziel-Silo
                dest_lot = self.db.execute(
                    text("""
                        SELECT id, quantity_tons FROM domain_inventory.silo_lots
                        WHERE silo_id = :sid AND tenant_id = :tid AND status = 'active'
                          AND article_id = :art
                        ORDER BY quantity_tons DESC, created_at DESC
                        LIMIT 1
                    """),
                    {"sid": to_silo_id, "art": article_id, "tid": self.tenant_id},
                ).fetchone()

            if dest_lot:
                dest_new_qty = Decimal(str(dest_lot.quantity_tons)) + qty_tons
                self.db.execute(
                    text("""
                        UPDATE domain_inventory.silo_lots
                        SET quantity_tons = :qty, updated_at = NOW()
                        WHERE id = :id
                    """),
                    {"qty": float(dest_new_qty), "id": str(dest_lot.id)},
                )
                self.db.execute(
                    text("""
                        INSERT INTO domain_inventory.silo_lot_movements
                            (id, silo_lot_id, movement_type, quantity_tons, note, tenant_id, created_at)
                        VALUES (:id, :lid, 'in', :qty, :note, :tid, NOW())
                    """),
                    {
                        "id": str(uuid7()),
                        "lid": str(dest_lot.id),
                        "qty": float(qty_tons),
                        "note": f"WMS-Transfer ← Quellzelle {from_cell_id}",
                        "tid": self.tenant_id,
                    },
                )
                updated.append(f"dest:{dest_lot.id}:in:{float(qty_tons)}t")

        return {"ok": True, "updated": updated}
