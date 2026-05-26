from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session


class WarehouseService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    # ── Zonen ──────────────────────────────────────────────────

    def list_zones(self, warehouse_id: str) -> list[dict]:
        """Alle aktiven Zonen eines Lagers."""
        rows = self.db.execute(text("""
            SELECT * FROM domain_inventory.warehouse_zones
            WHERE warehouse_id = :wid AND tenant_id = :tid AND is_active = true
            ORDER BY zone_code
        """), {"wid": warehouse_id, "tid": self.tenant_id}).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_zone(self, warehouse_id: str, payload: dict) -> dict:
        zone_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.warehouse_zones
              (id, warehouse_id, zone_code, name, zone_type, description, tenant_id, is_active)
            VALUES (:id, :wid, :zone_code, :name, :zone_type, :desc, :tid, true)
        """), {"id": zone_id, "wid": warehouse_id, "zone_code": payload["zone_code"],
               "name": payload["name"], "zone_type": payload.get("zone_type", "standard"),
               "desc": payload.get("description"), "tid": self.tenant_id})
        self.db.commit()
        return {"id": zone_id, **payload}

    # ── Bins ───────────────────────────────────────────────────

    def list_bins(self, warehouse_id: str | None = None, zone_id: str | None = None,
                  only_active: bool = True) -> list[dict]:
        filters = ["tenant_id = :tid"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        if zone_id:
            filters.append("zone_id = :zid")
            params["zid"] = zone_id
        if only_active:
            filters.append("is_active = true")
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.warehouse_bins WHERE {where} ORDER BY bin_code"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_bin(self, zone_id: str, warehouse_id: str, payload: dict) -> dict:
        bin_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.warehouse_bins
              (id, zone_id, warehouse_id, bin_code, bin_type, capacity_kg, tenant_id, is_active, is_blocked)
            VALUES (:id, :zid, :wid, :bin_code, :bin_type, :cap, :tid, true, false)
        """), {"id": bin_id, "zid": zone_id, "wid": warehouse_id,
               "bin_code": payload["bin_code"], "bin_type": payload.get("bin_type", "standard"),
               "cap": payload.get("capacity_kg"), "tid": self.tenant_id})
        self.db.commit()
        return {"id": bin_id, "zone_id": zone_id, "warehouse_id": warehouse_id, **payload}

    def get_bin_stock(self, bin_id: str) -> list[dict]:
        """Alle Artikel/Chargen auf einem Lagerplatz."""
        rows = self.db.execute(text("""
            SELECT bs.*, wb.bin_code, wb.warehouse_id
            FROM domain_inventory.bin_stock bs
            JOIN domain_inventory.warehouse_bins wb ON wb.id = bs.bin_id
            WHERE bs.bin_id = :bid AND bs.tenant_id = :tid AND bs.quantity_kg > 0
            ORDER BY bs.best_before_date NULLS LAST, bs.batch_number
        """), {"bid": bin_id, "tid": self.tenant_id}).fetchall()
        return [dict(r._mapping) for r in rows]

    # ── Bestandsbuchung ────────────────────────────────────────

    def book_stock_movement(self, bin_id: str, article_id: str, batch_number: str | None,
                             best_before_date: date | None, quantity_kg: Decimal,
                             unit_cost: Decimal | None, movement_type: str,
                             reference: str | None = None) -> str:
        """Einlagerung (positiv) oder Auslagerung (negativ) auf Bin-Ebene buchen."""
        # Upsert bin_stock
        existing = self.db.execute(text("""
            SELECT id, quantity_kg FROM domain_inventory.bin_stock
            WHERE bin_id = :bid AND article_id = :aid
              AND COALESCE(batch_number,'') = COALESCE(:batch,'')
              AND tenant_id = :tid
        """), {"bid": bin_id, "aid": article_id, "batch": batch_number, "tid": self.tenant_id}).fetchone()

        if existing:
            new_qty = Decimal(str(existing.quantity_kg)) + quantity_kg
            if new_qty < 0:
                raise ValueError(f"Unterdeckung: Bestand {existing.quantity_kg} kg, Entnahme {abs(quantity_kg)} kg")
            self.db.execute(text("""
                UPDATE domain_inventory.bin_stock
                SET quantity_kg = :qty, last_movement_at = :now
                WHERE id = :id
            """), {"qty": new_qty, "now": datetime.now(timezone.utc), "id": existing.id})
        else:
            if quantity_kg < 0:
                raise ValueError("Auslagerung ohne vorhandenen Bestand")
            stock_id = str(uuid4())
            self.db.execute(text("""
                INSERT INTO domain_inventory.bin_stock
                  (id, bin_id, article_id, batch_number, best_before_date, quantity_kg, unit_cost, last_movement_at, tenant_id)
                VALUES (:id, :bid, :aid, :batch, :bbd, :qty, :cost, :now, :tid)
            """), {"id": stock_id, "bid": bin_id, "aid": article_id, "batch": batch_number,
                   "bbd": best_before_date, "qty": quantity_kg, "cost": unit_cost,
                   "now": datetime.now(timezone.utc), "tid": self.tenant_id})

        # StockMovement-Protokoll
        mv_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.inventory_stock_movements
              (id, article_id, warehouse_id, bin_id, movement_type, quantity, unit_cost,
               reference_number, movement_date, movement_time, notes, tenant_id, auto_created)
            SELECT :id, :aid,
                   (SELECT warehouse_id FROM domain_inventory.warehouse_bins WHERE id = :bid),
                   :bid, :mtype, :qty, :cost, :ref, CURRENT_DATE, CURRENT_TIME, NULL, :tid, false
        """), {"id": mv_id, "aid": article_id, "bid": bin_id, "mtype": movement_type,
               "qty": quantity_kg, "cost": unit_cost, "ref": reference, "tid": self.tenant_id})
        self.db.commit()
        return mv_id

    # ── FEFO-Picking ───────────────────────────────────────────

    def fefo_pick_suggestion(self, warehouse_id: str, article_id: str,
                              quantity_needed: Decimal) -> list[dict]:
        """
        FEFO-Entnahme-Vorschlag: liefert eine Liste von (bin_id, bin_code, batch_number,
        best_before_date, pick_quantity) sortiert nach frühestem MHD (FEFO).
        Summe der pick_quantity == quantity_needed (sofern Bestand ausreicht).
        """
        rows = self.db.execute(text("""
            SELECT bs.bin_id, wb.bin_code, bs.batch_number, bs.best_before_date, bs.quantity_kg
            FROM domain_inventory.bin_stock bs
            JOIN domain_inventory.warehouse_bins wb ON wb.id = bs.bin_id
            WHERE wb.warehouse_id = :wid
              AND bs.article_id = :aid
              AND bs.tenant_id = :tid
              AND bs.quantity_kg > 0
              AND wb.is_active = true
              AND wb.is_blocked = false
            ORDER BY bs.best_before_date NULLS LAST, bs.batch_number, bs.quantity_kg DESC
        """), {"wid": warehouse_id, "aid": article_id, "tid": self.tenant_id}).fetchall()

        suggestion: list[dict] = []
        remaining = quantity_needed
        for row in rows:
            if remaining <= 0:
                break
            pick_qty = min(Decimal(str(row.quantity_kg)), remaining)
            suggestion.append({
                "bin_id": row.bin_id,
                "bin_code": row.bin_code,
                "batch_number": row.batch_number,
                "best_before_date": row.best_before_date.isoformat() if row.best_before_date else None,
                "available_kg": float(row.quantity_kg),
                "pick_kg": float(pick_qty),
            })
            remaining -= pick_qty

        return suggestion  # Caller prüft ob sum(pick_kg) == quantity_needed

    # ── Pick-Listen ────────────────────────────────────────────

    def create_pick_list(self, warehouse_id: str, items: list[dict],
                          source_doc_ref: str | None = None,
                          source_doc_type: str = "MANUAL",
                          strategy: str = "FEFO",
                          created_by: str | None = None) -> dict:
        """
        Erstellt eine Pick-Liste mit FEFO-Vorschlägen je Position.
        items: [{article_id, quantity_required, unit}]
        """
        pl_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.pick_lists
              (id, tenant_id, warehouse_id, source_doc_ref, source_doc_type, status, strategy, created_by)
            VALUES (:id, :tid, :wid, :src_ref, :src_type, 'OPEN', :strategy, :created_by)
        """), {"id": pl_id, "tid": self.tenant_id, "wid": warehouse_id,
               "src_ref": source_doc_ref, "src_type": source_doc_type,
               "strategy": strategy, "created_by": created_by})

        lines_created = []
        for i, item in enumerate(items):
            suggestion = self.fefo_pick_suggestion(
                warehouse_id, item["article_id"], Decimal(str(item["quantity_required"]))
            ) if strategy == "FEFO" else []

            for sug in suggestion or [{"bin_id": None, "batch_number": None, "best_before_date": None, "pick_kg": item["quantity_required"]}]:
                line_id = str(uuid4())
                self.db.execute(text("""
                    INSERT INTO domain_inventory.pick_list_lines
                      (id, pick_list_id, article_id, bin_id, batch_number, best_before_date,
                       quantity_required, quantity_picked, unit, status, sort_order)
                    VALUES (:id, :plid, :aid, :bid, :batch, :bbd, :qty, 0, :unit, 'OPEN', :sort)
                """), {"id": line_id, "plid": pl_id, "aid": item["article_id"],
                       "bid": sug.get("bin_id"), "batch": sug.get("batch_number"),
                       "bbd": sug.get("best_before_date"), "qty": sug["pick_kg"],
                       "unit": item.get("unit", "kg"), "sort": i})
                lines_created.append({"id": line_id, "article_id": item["article_id"], **sug})

        self.db.commit()
        return {"id": pl_id, "status": "OPEN", "lines": lines_created}

    def confirm_pick_list(self, pick_list_id: str, picked_lines: list[dict]) -> dict:
        """
        Bestätigt gescannte/gepickte Mengen und bucht Lagerbestand aus.
        picked_lines: [{line_id, quantity_picked}]
        """
        pl = self.db.execute(text("""
            SELECT id, status, warehouse_id FROM domain_inventory.pick_lists
            WHERE id = :plid AND tenant_id = :tid
        """), {"plid": pick_list_id, "tid": self.tenant_id}).fetchone()
        if not pl:
            raise ValueError(f"PickList {pick_list_id} not found")
        if pl.status == "COMPLETED":
            raise ValueError("Pick-Liste bereits abgeschlossen")

        for pl_line in picked_lines:
            line = self.db.execute(text("""
                SELECT * FROM domain_inventory.pick_list_lines WHERE id = :lid
            """), {"lid": pl_line["line_id"]}).fetchone()
            if not line or not line.bin_id:
                continue
            qty = Decimal(str(pl_line["quantity_picked"]))
            self.book_stock_movement(
                bin_id=line.bin_id,
                article_id=line.article_id,
                batch_number=line.batch_number,
                best_before_date=line.best_before_date,
                quantity_kg=-qty,  # negativ = Auslagerung
                unit_cost=None,
                movement_type="pick_out",
                reference=pick_list_id,
            )
            new_status = "DONE" if qty >= Decimal(str(line.quantity_required)) else "PARTIAL"
            self.db.execute(text("""
                UPDATE domain_inventory.pick_list_lines
                SET quantity_picked = :qty, status = :status
                WHERE id = :lid
            """), {"qty": qty, "status": new_status, "lid": line.id})

        # Pick-Liste abschliessen wenn alle Linien DONE/SKIPPED
        all_lines = self.db.execute(text("""
            SELECT status FROM domain_inventory.pick_list_lines WHERE pick_list_id = :plid
        """), {"plid": pick_list_id}).fetchall()
        all_done = all(r.status in ("DONE", "SKIPPED") for r in all_lines)
        new_pl_status = "COMPLETED" if all_done else "IN_PROGRESS"
        self.db.execute(text("""
            UPDATE domain_inventory.pick_lists SET status = :st,
              completed_at = CASE WHEN :st = 'COMPLETED' THEN NOW() ELSE completed_at END
            WHERE id = :plid
        """), {"st": new_pl_status, "plid": pick_list_id})
        self.db.commit()
        return {"pick_list_id": pick_list_id, "status": new_pl_status}

    # ── MHD-Ampel ──────────────────────────────────────────────

    def get_mhd_alert(self, warehouse_id: str, days_warning: int = 30,
                       days_critical: int = 7) -> list[dict]:
        """
        MHD-Ampel: Artikel/Chargen mit nahendem Verfallsdatum.
        Gibt zurück: article_id, batch_number, best_before_date, quantity_kg, bin_code,
                     alert_level (critical/warning/ok)
        """
        rows = self.db.execute(text("""
            SELECT bs.article_id, bs.batch_number, bs.best_before_date,
                   SUM(bs.quantity_kg) as total_qty,
                   STRING_AGG(wb.bin_code, ', ') as bin_codes,
                   MIN(bs.best_before_date - CURRENT_DATE) as days_remaining
            FROM domain_inventory.bin_stock bs
            JOIN domain_inventory.warehouse_bins wb ON wb.id = bs.bin_id
            WHERE wb.warehouse_id = :wid
              AND bs.tenant_id = :tid
              AND bs.quantity_kg > 0
              AND bs.best_before_date IS NOT NULL
              AND bs.best_before_date <= CURRENT_DATE + :warn_days
            GROUP BY bs.article_id, bs.batch_number, bs.best_before_date
            ORDER BY bs.best_before_date ASC
        """), {"wid": warehouse_id, "tid": self.tenant_id, "warn_days": days_warning}).fetchall()

        result = []
        for r in rows:
            days = r.days_remaining if r.days_remaining is not None else 999
            level = "critical" if days <= days_critical else "warning"
            result.append({
                "article_id": r.article_id,
                "batch_number": r.batch_number,
                "best_before_date": r.best_before_date.isoformat() if r.best_before_date else None,
                "total_quantity_kg": float(r.total_qty),
                "bin_codes": r.bin_codes,
                "days_remaining": int(days),
                "alert_level": level,
            })
        return result

    # ── Bin-to-Bin Transfer ────────────────────────────────────

    def transfer_bin_to_bin(self, from_bin_id: str, to_bin_id: str,
                             article_id: str, batch_number: str | None,
                             quantity_kg: Decimal, best_before_date: date | None = None) -> dict:
        """Umlagerung zwischen zwei Lagerplaetzen."""
        mv_out = self.book_stock_movement(
            from_bin_id, article_id, batch_number, best_before_date, -quantity_kg, None, "transfer_out"
        )
        mv_in = self.book_stock_movement(
            to_bin_id, article_id, batch_number, best_before_date, quantity_kg, None, "transfer_in"
        )
        return {"from_movement_id": mv_out, "to_movement_id": mv_in, "quantity_kg": float(quantity_kg)}

    # ── FIFO-Bestandsbewertung ─────────────────────────────────

    def get_stock_valuation(self, warehouse_id: str | None = None) -> list[dict]:
        """
        FIFO-Bestandsbewertung: Wert je Artikel/Charge als SUM(quantity_kg * unit_cost).
        Gibt None-unit_cost als 0 zurück.
        """
        filters = ["bs.tenant_id = :tid", "bs.quantity_kg > 0"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("wb.warehouse_id = :wid")
            params["wid"] = warehouse_id
        where = " AND ".join(filters)
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        rows = self.db.execute(text(f"""
            SELECT bs.article_id, bs.batch_number,
                   SUM(bs.quantity_kg) as total_qty,
                   SUM(bs.quantity_kg * COALESCE(bs.unit_cost, 0)) as total_value,
                   AVG(COALESCE(bs.unit_cost, 0)) as avg_cost
            FROM domain_inventory.bin_stock bs
            JOIN domain_inventory.warehouse_bins wb ON wb.id = bs.bin_id
            WHERE {where}
            GROUP BY bs.article_id, bs.batch_number
            ORDER BY bs.article_id
        """), params).fetchall()
        return [{"article_id": r.article_id, "batch_number": r.batch_number,
                 "total_quantity_kg": float(r.total_qty),
                 "total_value_eur": float(r.total_value),
                 "avg_cost_per_kg": float(r.avg_cost)} for r in rows]
