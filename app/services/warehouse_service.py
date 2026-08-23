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

    # ── Gänge (Aisles) ─────────────────────────────────────────

    def list_aisles(self, zone_id: str) -> list[dict]:
        """Alle aktiven Gänge einer Zone."""
        rows = self.db.execute(text("""
            SELECT * FROM domain_inventory.warehouse_aisles
            WHERE zone_id = :zid AND tenant_id = :tid AND is_active = true
            ORDER BY aisle_code
        """), {"zid": zone_id, "tid": self.tenant_id}).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_aisle(self, zone_id: str, payload: dict) -> dict:
        """Gang in einer Zone anlegen (warehouse_id aus Zone)."""
        z = self.db.execute(text("""
            SELECT id, warehouse_id FROM domain_inventory.warehouse_zones
            WHERE id = :zid AND tenant_id = :tid AND is_active = true
        """), {"zid": zone_id, "tid": self.tenant_id}).fetchone()
        if not z:
            raise ValueError("Zone nicht gefunden oder inaktiv")
        wid = str(z.warehouse_id)
        aisle_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.warehouse_aisles
              (id, zone_id, warehouse_id, aisle_code, name, description, tenant_id, is_active)
            VALUES (:id, :zid, :wid, :aisle_code, :name, :desc, :tid, true)
        """), {
            "id": aisle_id, "zid": zone_id, "wid": wid,
            "aisle_code": payload["aisle_code"],
            "name": payload.get("name"),
            "desc": payload.get("description"),
            "tid": self.tenant_id,
        })
        self.db.commit()
        return {"id": aisle_id, "zone_id": zone_id, "warehouse_id": wid, **payload}

    # ── Bins ───────────────────────────────────────────────────

    def list_bins(self, warehouse_id: str | None = None, zone_id: str | None = None,
                  aisle_id: str | None = None, only_active: bool = True) -> list[dict]:
        filters = ["tenant_id = :tid"]
        params: dict = {"tid": self.tenant_id}
        if warehouse_id:
            filters.append("warehouse_id = :wid")
            params["wid"] = warehouse_id
        if zone_id:
            filters.append("zone_id = :zid")
            params["zid"] = zone_id
        if aisle_id:
            filters.append("aisle_id = :aid")
            params["aid"] = aisle_id
        if only_active:
            filters.append("is_active = true")
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_inventory.warehouse_bins WHERE {where} ORDER BY bin_code"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params).fetchall()
        return [dict(r._mapping) for r in rows]

    def create_bin(self, zone_id: str, warehouse_id: str, payload: dict) -> dict:
        bin_id = str(uuid4())
        aisle_id = payload.get("aisle_id")
        if aisle_id:
            row = self.db.execute(text("""
                SELECT id FROM domain_inventory.warehouse_aisles
                WHERE id = :aid AND zone_id = :zid AND warehouse_id = :wid
                  AND tenant_id = :tid AND is_active = true
            """), {
                "aid": aisle_id, "zid": zone_id, "wid": warehouse_id, "tid": self.tenant_id,
            }).fetchone()
            if not row:
                raise ValueError(
                    "Gang (aisle_id) nicht gefunden, passt nicht zur Zone/Lager oder ist inaktiv"
                )
            self.db.execute(text("""
                INSERT INTO domain_inventory.warehouse_bins
                  (id, zone_id, warehouse_id, aisle_id, bin_code, bin_type, capacity_kg,
                   tenant_id, is_active, is_blocked)
                VALUES (:id, :zid, :wid, :aisle_id, :bin_code, :bin_type, :cap, :tid, true, false)
            """), {
                "id": bin_id, "zid": zone_id, "wid": warehouse_id, "aisle_id": aisle_id,
                "bin_code": payload["bin_code"], "bin_type": payload.get("bin_type", "standard"),
                "cap": payload.get("capacity_kg"), "tid": self.tenant_id,
            })
        else:
            self.db.execute(text("""
                INSERT INTO domain_inventory.warehouse_bins
                  (id, zone_id, warehouse_id, bin_code, bin_type, capacity_kg, tenant_id, is_active, is_blocked)
                VALUES (:id, :zid, :wid, :bin_code, :bin_type, :cap, :tid, true, false)
            """), {"id": bin_id, "zid": zone_id, "wid": warehouse_id,
                   "bin_code": payload["bin_code"], "bin_type": payload.get("bin_type", "standard"),
                   "cap": payload.get("capacity_kg"), "tid": self.tenant_id})
        self.db.commit()
        return {"id": bin_id, "zone_id": zone_id, "warehouse_id": warehouse_id, **payload}

    def get_bin(self, bin_id: str) -> dict | None:
        """Einzelnen Lagerplatz inkl. Tenant-Scope."""
        row = self.db.execute(text("""
            SELECT * FROM domain_inventory.warehouse_bins
            WHERE id = :id AND tenant_id = :tid
        """), {"id": bin_id, "tid": self.tenant_id}).fetchone()
        return dict(row._mapping) if row else None

    def update_bin(self, bin_id: str, payload: dict) -> dict:
        """Teilupdate (Kapazität, Typ, Sperre, Gang). Nur übergebene Keys aus exclude_unset."""
        allowed = frozenset({"bin_type", "capacity_kg", "is_blocked", "block_reason", "aisle_id"})
        patch = {k: v for k, v in payload.items() if k in allowed}
        existing = self.get_bin(bin_id)
        if not existing:
            raise ValueError("Bin nicht gefunden")
        zone_id = str(existing["zone_id"])
        wh_id = str(existing["warehouse_id"])
        if "aisle_id" in patch:
            aid = patch["aisle_id"]
            if aid is not None:
                row = self.db.execute(text("""
                    SELECT id FROM domain_inventory.warehouse_aisles
                    WHERE id = :aid AND zone_id = :zid AND warehouse_id = :wid
                      AND tenant_id = :tid AND is_active = true
                """), {
                    "aid": aid, "zid": zone_id, "wid": wh_id, "tid": self.tenant_id,
                }).fetchone()
                if not row:
                    raise ValueError(
                        "Gang (aisle_id) nicht gefunden, passt nicht zur Zone/Lager oder ist inaktiv"
                    )
        set_parts: list[str] = []
        params: dict = {"bid": bin_id, "tid": self.tenant_id}
        for k in ("bin_type", "capacity_kg", "is_blocked", "block_reason", "aisle_id"):
            if k not in patch:
                continue
            set_parts.append(f"{k} = :{k}")
            params[k] = patch[k]
        if not set_parts:
            return existing
        sql = (
            "UPDATE domain_inventory.warehouse_bins SET "
            + ", ".join(set_parts)
            + " WHERE id = :bid AND tenant_id = :tid"
        )
        self.db.execute(text(sql), params)
        self.db.commit()
        refreshed = self.get_bin(bin_id)
        return refreshed or {}

    def _assert_bin_total_within_capacity(self, bin_id: str) -> None:
        """Nach Buchung auf bin_stock: Summe kg vs. warehouse_bins.capacity_kg."""
        cap_row = self.db.execute(text("""
            SELECT capacity_kg FROM domain_inventory.warehouse_bins
            WHERE id = :bid AND tenant_id = :tid
        """), {"bid": bin_id, "tid": self.tenant_id}).fetchone()
        if not cap_row or cap_row.capacity_kg is None:
            return
        ck = cap_row.capacity_kg
        if not isinstance(ck, (Decimal, int, float, str)):
            return
        if isinstance(ck, str) and ck.strip() == "":
            return
        try:
            cap = Decimal(str(ck))
        except Exception:
            return
        total_row = self.db.execute(text("""
            SELECT COALESCE(SUM(quantity_kg), 0) AS t FROM domain_inventory.bin_stock
            WHERE bin_id = :bid AND tenant_id = :tid
        """), {"bid": bin_id, "tid": self.tenant_id}).fetchone()
        try:
            tot = Decimal(str(total_row.t if total_row and total_row.t is not None else 0))
        except Exception:
            return
        if tot > cap:
            self.db.rollback()
            raise ValueError(
                f"Lagerplatz-Kapazitaet ueberschritten ({tot} kg > {cap} kg)"
            )

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

    def set_bin_stock_line_quantity(self, bin_id: str, stock_line_id: str, quantity_kg: Decimal) -> dict:
        """Absolute Menge einer bin_stock-Zeile setzen (Korrektur/Inventur)."""
        if quantity_kg < 0:
            raise ValueError("Menge darf nicht negativ sein")
        row = self.db.execute(text("""
            SELECT bs.id FROM domain_inventory.bin_stock bs
            WHERE bs.id = :sid AND bs.bin_id = :bid AND bs.tenant_id = :tid
        """), {"sid": stock_line_id, "bid": bin_id, "tid": self.tenant_id}).fetchone()
        if not row:
            raise ValueError("Bestandszeile nicht gefunden oder gehoert nicht zu diesem Lagerplatz")
        self.db.execute(text("""
            UPDATE domain_inventory.bin_stock
            SET quantity_kg = :qty, last_movement_at = :now
            WHERE id = :sid AND tenant_id = :tid
        """), {"qty": quantity_kg, "now": datetime.now(timezone.utc), "sid": stock_line_id, "tid": self.tenant_id})
        self._assert_bin_total_within_capacity(bin_id)
        self.db.commit()
        out = self.db.execute(text("""
            SELECT * FROM domain_inventory.bin_stock WHERE id = :sid AND tenant_id = :tid
        """), {"sid": stock_line_id, "tid": self.tenant_id}).fetchone()
        return dict(out._mapping) if out else {}

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
            old_qty = Decimal(str(existing.quantity_kg))
            new_qty = old_qty + quantity_kg
            if new_qty < 0:
                raise ValueError(f"Unterdeckung: Bestand {existing.quantity_kg} kg, Entnahme {abs(quantity_kg)} kg")
            # Weighted-average unit_cost: update only on inbound movements with a known cost
            new_cost: Decimal | None = None
            if quantity_kg > 0 and unit_cost is not None:
                existing_cost_row = self.db.execute(text(
                    "SELECT unit_cost FROM domain_inventory.bin_stock WHERE id = :id"
                ), {"id": existing.id}).fetchone()
                old_cost = Decimal(str(existing_cost_row.unit_cost or 0)) if existing_cost_row and existing_cost_row.unit_cost else Decimal("0")
                if new_qty > 0:
                    new_cost = ((old_qty * old_cost) + (quantity_kg * unit_cost)) / new_qty
            self.db.execute(text("""
                UPDATE domain_inventory.bin_stock
                SET quantity_kg = :qty,
                    unit_cost = COALESCE(:cost, unit_cost),
                    last_movement_at = :now
                WHERE id = :id
            """), {"qty": new_qty, "cost": new_cost, "now": datetime.now(timezone.utc), "id": existing.id})
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

        self._assert_bin_total_within_capacity(bin_id)

        # StockMovement-Protokoll
        mv_id = str(uuid4())
        self.db.execute(text("""
            INSERT INTO domain_inventory.inventory_stock_movements
              (id, article_id, warehouse_id, bin_id, movement_type, quantity, unit_cost,
               reference_number, movement_date, movement_time, notes, tenant_id, auto_created,
               ownership_type, storage_fee_relevant, previous_stock, new_stock)
            SELECT :id, :aid, wb.warehouse_id,
                   :bid, :mtype, :qty, :cost, :ref, CURRENT_DATE, CURRENT_TIME, NULL, :tid, false,
                   'owned', false,
                   -- bin_stock ist an dieser Stelle bereits fortgeschrieben:
                   -- aktueller Lagersummenstand = new_stock, davor = new_stock - qty
                   COALESCE(ws.total, 0) - :qty,
                   COALESCE(ws.total, 0)
            FROM domain_inventory.warehouse_bins wb
            LEFT JOIN LATERAL (
                SELECT SUM(bs.quantity_kg) AS total
                FROM domain_inventory.bin_stock bs
                JOIN domain_inventory.warehouse_bins wb2 ON wb2.id = bs.bin_id
                WHERE wb2.warehouse_id = wb.warehouse_id
                  AND bs.article_id = :aid AND bs.tenant_id = :tid
            ) ws ON true
            WHERE wb.id = :bid
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
        # Lieferschein → versandt wenn Pick-Liste komplett (Belegkette schließen)
        if new_pl_status == "COMPLETED":
            pl_meta = self.db.execute(text("""
                SELECT source_doc_ref, source_doc_type FROM domain_inventory.pick_lists
                WHERE id = :plid
            """), {"plid": pick_list_id}).fetchone()
            if pl_meta and pl_meta.source_doc_type == "DELIVERY_NOTE" and pl_meta.source_doc_ref:
                self.db.execute(text("""
                    UPDATE domain_sales.delivery_notes
                    SET status = 'shipped', updated_at = NOW()
                    WHERE id = :id AND tenant_id = :tid AND status IN ('posted', 'printed')
                """), {"id": pl_meta.source_doc_ref, "tid": self.tenant_id})

        self.db.commit()
        return {"pick_list_id": pick_list_id, "status": new_pl_status}

    def create_pick_list_from_delivery_note(
        self,
        ls_id: str,
        warehouse_id: str | None = None,
        strategy: str = "FEFO",
        created_by: str | None = None,
    ) -> dict:
        """Erstellt eine WMS-Pick-Liste aus einem gebuchten/gedruckten Lieferschein.

        Schließt den Belegbruch Lieferschein → Kommissionierliste:
        - Status muss posted/printed sein, sonst ValueError (→ 409)
        - Positionen mit artikel_id werden als Pick-Positionen übernommen
        - FEFO-Vorschlag je Position aus bin_stock
        """
        dn = self.db.execute(text("""
            SELECT id, status, delivery_note_number
            FROM domain_sales.delivery_notes
            WHERE id = :id AND tenant_id = :tid
        """), {"id": ls_id, "tid": self.tenant_id}).fetchone()
        if not dn:
            raise ValueError(f"Lieferschein {ls_id} nicht gefunden")
        if dn.status not in ("posted", "printed"):
            raise ValueError(
                f"Lieferschein muss gebucht oder gedruckt sein (Status: {dn.status})"
            )

        # Check no open pick list exists for this delivery note
        existing = self.db.execute(text("""
            SELECT id FROM domain_inventory.pick_lists
            WHERE source_doc_ref = :ref AND source_doc_type = 'DELIVERY_NOTE'
              AND tenant_id = :tid AND status NOT IN ('COMPLETED', 'CANCELLED')
        """), {"ref": ls_id, "tid": self.tenant_id}).fetchone()
        if existing:
            raise ValueError(
                f"Für diesen Lieferschein existiert bereits eine offene Pick-Liste ({existing.id})"
            )

        positions = self.db.execute(text("""
            SELECT artikel_id, menge, einheit
            FROM domain_sales.delivery_note_positions
            WHERE delivery_note_id = :id
              AND artikel_id IS NOT NULL AND menge > 0
            ORDER BY pos_nr
        """), {"id": ls_id}).fetchall()

        if not positions:
            raise ValueError("Lieferschein hat keine Positionen mit Artikel-Referenz")

        items = [
            {
                "article_id": p.artikel_id,
                "quantity_required": float(p.menge),
                "unit": p.einheit or "Stk",
            }
            for p in positions
        ]

        result = self.create_pick_list(
            warehouse_id=warehouse_id or "",
            items=items,
            source_doc_ref=ls_id,
            source_doc_type="DELIVERY_NOTE",
            strategy=strategy,
            created_by=created_by,
        )
        result["delivery_note_id"] = ls_id
        result["delivery_note_number"] = dn.delivery_note_number
        return result

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
        """), params).fetchall()  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        return [{"article_id": r.article_id, "batch_number": r.batch_number,
                 "total_quantity_kg": float(r.total_qty),
                 "total_value_eur": float(r.total_value),
                 "avg_cost_per_kg": float(r.avg_cost)} for r in rows]

    # ── Einlagerungsstrategie (Putaway) ────────────────────────

    def suggest_putaway_bin(
        self,
        warehouse_id: str,
        article_id: str,
        quantity_kg: Decimal,
        best_before_date: date | None = None,
        strategy: str = "CAPACITY",
    ) -> list[dict]:
        """Einlagerungsvorschlag: welche Bins haben genug Restkapazität.

        Strategies:
        - CAPACITY: Bins mit grösster Restkapazität zuerst (space-out)
        - CONSOLIDATE: Bins, die den selben Artikel bereits enthalten (reduziert Fragmentation)
        - FEFO_ZONE: Bins im selben Zone/Gang wie bestehende Chargen dieses Artikels (FEFO-kompatibel)
        """
        rows = self.db.execute(text("""
            SELECT wb.id AS bin_id, wb.bin_code, wb.bin_type,
                   COALESCE(wb.capacity_kg, 0) as capacity_kg,
                   COALESCE(SUM(bs.quantity_kg), 0) as used_kg,
                   COALESCE(wb.capacity_kg, 0) - COALESCE(SUM(bs.quantity_kg), 0) as free_kg,
                   EXISTS (
                       SELECT 1 FROM domain_inventory.bin_stock bs2
                       WHERE bs2.bin_id = wb.id AND bs2.article_id = :aid
                         AND bs2.tenant_id = :tid AND bs2.quantity_kg > 0
                   ) as has_same_article
            FROM domain_inventory.warehouse_bins wb
            LEFT JOIN domain_inventory.bin_stock bs ON bs.bin_id = wb.id AND bs.tenant_id = :tid
            WHERE wb.warehouse_id = :wid
              AND wb.is_blocked = false
              AND wb.tenant_id = :tid
            GROUP BY wb.id, wb.bin_code, wb.bin_type, wb.capacity_kg
            HAVING COALESCE(wb.capacity_kg, 0) - COALESCE(SUM(bs.quantity_kg), 0) >= :qty
               OR COALESCE(wb.capacity_kg, 0) = 0
        """), {"wid": warehouse_id, "aid": article_id, "qty": float(quantity_kg), "tid": self.tenant_id}).fetchall()

        candidates = [
            {
                "bin_id": str(r.bin_id),
                "bin_code": str(r.bin_code),
                "bin_type": str(r.bin_type) if r.bin_type else None,
                "capacity_kg": float(r.capacity_kg),
                "used_kg": float(r.used_kg),
                "free_kg": float(r.free_kg),
                "has_same_article": bool(r.has_same_article),
            }
            for r in rows
        ]

        if strategy == "CONSOLIDATE":
            # Bins with same article first, then by most free space
            candidates.sort(key=lambda c: (not c["has_same_article"], -c["free_kg"]))
        else:
            # CAPACITY or FEFO_ZONE: sort by free space descending
            candidates.sort(key=lambda c: -c["free_kg"])

        return candidates[:10]  # top 10 suggestions
