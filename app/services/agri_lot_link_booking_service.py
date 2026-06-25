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

    def suggest_lot_link(
        self,
        *,
        warehouse_id: str,
        lot_id: str | None = None,
        ticket_id: str | None = None,
        acceptance_id: str | None = None,
    ) -> dict:
        """Schlägt Ziel-Silozelle + Lot für Waage/WE vor (legacy_silo_id-Matching)."""
        lot_d = self._resolve_active_lot(
            lot_id=lot_id,
            ticket_ref=ticket_id,
            acceptance_ref=acceptance_id,
        )
        silo_id = str(lot_d["silo_id"])
        lot_kg = Decimal(str(lot_d.get("quantity_tons") or "0")) * Decimal("1000")

        rows = self.db.execute(
            text("""
                SELECT id, cell_code, legacy_silo_id, capacity_kg, current_stock_kg,
                       current_material_id, current_lot_id, qs_status
                FROM domain_inventory.silo_cells
                WHERE warehouse_id = :wid AND tenant_id = :tid AND is_active = true
                ORDER BY cell_code
            """),
            {"wid": warehouse_id, "tid": self.tenant_id},
        ).fetchall()

        candidates: list[dict] = []
        for row in rows:
            cell_d = dict(row._mapping)
            score = self._score_cell_for_lot(cell_d, lot_d, silo_id, lot_kg)
            if score is None:
                continue
            candidates.append(
                {
                    "cell_id": str(cell_d["id"]),
                    "cell_code": str(cell_d.get("cell_code") or ""),
                    "legacy_silo_id": cell_d.get("legacy_silo_id"),
                    "qs_status": cell_d.get("qs_status"),
                    "current_stock_kg": float(cell_d.get("current_stock_kg") or 0),
                    "capacity_kg": float(cell_d.get("capacity_kg") or 0),
                    "score": score,
                    "legacy_match": str(cell_d.get("legacy_silo_id") or "") == silo_id,
                }
            )

        candidates.sort(key=lambda c: (-c["score"], c["cell_code"]))
        best = candidates[0] if candidates else None

        return {
            "ok": True,
            "warehouse_id": warehouse_id,
            "lot_id": str(lot_d["id"]),
            "silo_id": silo_id,
            "virtual_lot_number": lot_d.get("virtual_lot_number"),
            "article_id": lot_d.get("article_id"),
            "source_ticket_id": lot_d.get("source_ticket_id"),
            "quantity_kg_available": float(lot_kg),
            "suggested_cell_id": best["cell_id"] if best else None,
            "suggested_cell_code": best["cell_code"] if best else None,
            "suggested_quantity_kg": float(lot_kg) if best else None,
            "candidate_cells": candidates,
        }

    def _resolve_active_lot(
        self,
        *,
        lot_id: str | None,
        ticket_ref: str | None,
        acceptance_ref: str | None,
    ) -> dict:
        if not any([lot_id, ticket_ref, acceptance_ref]):
            raise ValueError("lot_id, ticket_id oder acceptance_id erforderlich")

        ticket_uuid: str | None = None
        if acceptance_ref and not ticket_ref:
            acc = self.db.execute(
                text("""
                    SELECT weighing_ticket_id
                    FROM domain_inventory.harvest_acceptances
                    WHERE tenant_id = :tid
                      AND (id::text = :v OR acceptance_number = :v)
                    LIMIT 1
                """),
                {"tid": self.tenant_id, "v": acceptance_ref},
            ).fetchone()
            if acc and acc.weighing_ticket_id:
                ticket_uuid = str(acc.weighing_ticket_id)

        if ticket_ref:
            ticket = self.db.execute(
                text("""
                    SELECT id FROM domain_inventory.weighing_tickets
                    WHERE tenant_id = :tid
                      AND (id::text = :v OR ticket_number = :v)
                    LIMIT 1
                """),
                {"tid": self.tenant_id, "v": ticket_ref},
            ).fetchone()
            if ticket:
                ticket_uuid = str(ticket.id)

        lot_row = None
        if lot_id:
            lot_row = self.db.execute(
                text("""
                    SELECT l.id, l.silo_id, l.virtual_lot_number, l.source_ticket_id,
                           l.article_id, l.quantity_tons, l.status, s.silo_number
                    FROM domain_inventory.silo_lots l
                    JOIN domain_inventory.silos s
                      ON s.id = l.silo_id AND s.tenant_id = l.tenant_id
                    WHERE l.tenant_id = :tid AND l.status = 'active'
                      AND (l.id::text = :v OR l.virtual_lot_number = :v)
                    LIMIT 1
                """),
                {"tid": self.tenant_id, "v": lot_id},
            ).fetchone()
        elif ticket_uuid:
            lot_row = self.db.execute(
                text("""
                    SELECT l.id, l.silo_id, l.virtual_lot_number, l.source_ticket_id,
                           l.article_id, l.quantity_tons, l.status, s.silo_number
                    FROM domain_inventory.silo_lots l
                    JOIN domain_inventory.silos s
                      ON s.id = l.silo_id AND s.tenant_id = l.tenant_id
                    WHERE l.tenant_id = :tid AND l.status = 'active'
                      AND l.source_ticket_id::text = :ticket
                    ORDER BY l.created_at DESC
                    LIMIT 1
                """),
                {"tid": self.tenant_id, "ticket": ticket_uuid},
            ).fetchone()

        if not lot_row:
            raise ValueError("Kein aktives Silo-Lot für die Eingabe gefunden")
        return dict(lot_row._mapping)

    def auto_book_lot_link_by_lot_id(
        self,
        *,
        lot_id: str,
        warehouse_id: str | None = None,
        booked_by: str = "system",
    ) -> dict:
        """Vollautomatische LOT-LINK-Buchung: löst Lot → beste Silozelle ohne Operator-Schritt.

        Schlägt fehl-soft: wenn kein eindeutiger legacy_silo_id-Match gefunden wird,
        wird kein Fehler geworfen — stattdessen ok=False + reason.
        """
        lot_row = self.db.execute(
            text("""
                SELECT l.id, l.silo_id, l.virtual_lot_number, l.source_ticket_id,
                       l.article_id, l.quantity_tons, l.status, s.silo_number
                FROM domain_inventory.silo_lots l
                JOIN domain_inventory.silos s
                  ON s.id = l.silo_id AND s.tenant_id = l.tenant_id
                WHERE l.tenant_id = :tid AND l.status = 'active'
                  AND (l.id::text = :v OR l.virtual_lot_number = :v)
                LIMIT 1
            """),
            {"tid": self.tenant_id, "v": lot_id},
        ).fetchone()
        if not lot_row:
            return {"ok": False, "lot_id": lot_id, "reason": "Kein aktives Silo-Lot gefunden"}

        lot_d = dict(lot_row._mapping)
        silo_id = str(lot_d["silo_id"])
        lot_kg = Decimal(str(lot_d.get("quantity_tons") or "0")) * Decimal("1000")

        cell_filter = {"sid": silo_id, "tid": self.tenant_id}
        wid_clause = ""
        if warehouse_id:
            wid_clause = " AND warehouse_id = :wid"
            cell_filter["wid"] = warehouse_id

        # nosec S608 - wid_clause is code-controlled and only adds a static
        # parameterized warehouse predicate; all values remain bound params.
        rows = self.db.execute(
            text(f"""
                SELECT id, warehouse_id, cell_code, legacy_silo_id,
                       capacity_kg, current_stock_kg, current_material_id,
                       current_lot_id, qs_status
                FROM domain_inventory.silo_cells
                WHERE legacy_silo_id = :sid
                  AND tenant_id = :tid
                  AND is_active = true
                  {wid_clause}
                ORDER BY cell_code
            """),  # noqa: S608 — column names code-controlled
            cell_filter,
        ).fetchall()

        used_rule_engine = False
        if not rows:
            # Fallback: Regelengine-Vorschlag wenn kein legacy_silo_id-Match vorhanden
            artikel_id = str(lot_d.get("article_id") or "")
            best_v = self._rule_engine_best_cell(
                artikel_id=artikel_id,
                lot_kg=lot_kg,
                warehouse_id=warehouse_id,
            )
            if best_v:
                result = self.book_lot_to_cell(
                    lot_id=lot_id,
                    target_cell_id=best_v["cell_id"],
                    warehouse_id=best_v["warehouse_id"],
                    quantity_kg=lot_kg,
                    booked_by=booked_by,
                )
                result["auto_booked"] = True
                result["auto_score"] = 0
                result["rule_engine_used"] = True
                result["rule_engine_grund"] = best_v.get("grund")
                return result
            return {
                "ok": False,
                "lot_id": lot_id,
                "silo_id": silo_id,
                "reason": "Kein legacy_silo_id-Mapping und keine freie Zelle via Regelengine",
            }

        best_cell: dict | None = None
        best_score = -1
        for row in rows:
            cell_d = dict(row._mapping)
            score = self._score_cell_for_lot(cell_d, lot_d, silo_id, lot_kg)
            if score is not None and score > best_score:
                best_score = score
                best_cell = cell_d

        if best_cell is None:
            # Zweiter Fallback: Regelengine wenn alle legacy-Kandidaten blockiert
            artikel_id = str(lot_d.get("article_id") or "")
            best_v = self._rule_engine_best_cell(
                artikel_id=artikel_id,
                lot_kg=lot_kg,
                warehouse_id=warehouse_id,
            )
            if best_v:
                result = self.book_lot_to_cell(
                    lot_id=lot_id,
                    target_cell_id=best_v["cell_id"],
                    warehouse_id=best_v["warehouse_id"],
                    quantity_kg=lot_kg,
                    booked_by=booked_by,
                )
                result["auto_booked"] = True
                result["auto_score"] = 0
                result["rule_engine_used"] = True
                result["rule_engine_grund"] = best_v.get("grund")
                return result
            return {
                "ok": False,
                "lot_id": lot_id,
                "silo_id": silo_id,
                "reason": "Alle Kandidaten-Silozellen gesperrt oder Kapazität/Materialkonflikt",
            }

        result = self.book_lot_to_cell(
            lot_id=lot_id,
            target_cell_id=str(best_cell["id"]),
            warehouse_id=str(best_cell["warehouse_id"]),
            quantity_kg=lot_kg,
            booked_by=booked_by,
        )
        result["auto_booked"] = True
        result["auto_score"] = best_score
        result["rule_engine_used"] = False
        return result

    def _rule_engine_best_cell(
        self,
        *,
        artikel_id: str,
        lot_kg: Decimal,
        warehouse_id: str | None,
    ) -> dict | None:
        if not artikel_id:
            return None
        try:
            from app.services.silo_rule_engine_service import SiloRuleEngineService  # noqa: PLC0415

            rule_svc = SiloRuleEngineService(db=self.db, tenant_id=self.tenant_id)
            vorschlaege = rule_svc.vorschlag(
                artikel_id=artikel_id,
                menge_kg=float(lot_kg),
                warehouse_id=warehouse_id,
                max_vorschlaege=1,
            )
        except Exception:
            return None
        return vorschlaege[0] if vorschlaege else None

    @staticmethod
    def _score_cell_for_lot(
        cell_d: dict,
        lot_d: dict,
        silo_id: str,
        lot_kg: Decimal,
    ) -> int | None:
        if str(cell_d.get("qs_status") or "") == "gesperrt":
            return None
        article_id = lot_d.get("article_id")
        current_mat = cell_d.get("current_material_id")
        if current_mat and article_id and str(current_mat) != str(article_id):
            return None
        current_lot = cell_d.get("current_lot_id")
        if current_lot and str(current_lot) != str(lot_d["id"]):
            return None
        stock = Decimal(str(cell_d.get("current_stock_kg") or "0"))
        capacity = Decimal(str(cell_d.get("capacity_kg") or "0"))
        if capacity > Decimal("0") and stock + lot_kg > capacity:
            return None
        score = 0
        if str(cell_d.get("legacy_silo_id") or "") == silo_id:
            score += 100
        score += max(0, 50 - int(stock / Decimal("1000")))
        return score
