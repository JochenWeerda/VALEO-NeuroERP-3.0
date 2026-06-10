"""Lager-Lot-Folgeaktionen mit Abweichungsgrund (DOM-SUPPLY-004.3).

Operative Folgeaktionen auf einem Silo-Lot der Lieferkette — jeweils mit Pflicht-
Grund, einer Lager-Bewegung (silo_lot_movements) und einem revisionsfesten Eintrag
im Ketten-Event-Log (SupplyChainEventService):

  • block      — Sperrbestand setzen (status='gesperrt')
  • release    — QS-Freigabe (status='active')
  • shrinkage  — Schwund buchen (Menge reduzieren, Bewegung 'schwund')

Mengen in der UI/Anfrage in kg; silo_lots/Bewegungen führen Tonnen.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.supply_chain_event_service import SupplyChainEventService

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


class LotActionError(Exception):
    """Fachlicher Fehler bei einer Lot-Folgeaktion (→ HTTP 422)."""


class SupplyChainLotService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _lot(self, lot_id: str) -> dict:
        r = self.db.execute(
            text(
                "SELECT id, virtual_lot_number, source_ticket_id, quantity_tons, status "
                "FROM domain_inventory.silo_lots WHERE (id::text = :v OR virtual_lot_number = :v) "
                "AND tenant_id = :t LIMIT 1"
            ),
            {"v": lot_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            raise LotActionError(f"Silo-Lot nicht gefunden: {lot_id}")
        return dict(r)

    def _add_movement(self, lot_id: str, mtype: str, qty_tons: Decimal, note: str) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_inventory.silo_lot_movements "
                "(id, silo_lot_id, movement_type, quantity_tons, note, tenant_id) "
                "VALUES (:id, :lid, :mt, :q, :note, :t)"
            ),
            {"id": str(uuid.uuid4()), "lid": lot_id, "mt": mtype, "q": qty_tons,
             "note": note, "t": self.tenant_id},
        )

    def _event(self, lot: dict, event_type: str, *, grund: str,
               status_from: Optional[str], status_to: Optional[str],
               menge_kg: Optional[float], bediener: str) -> dict:
        return SupplyChainEventService(self.db, self.tenant_id).record(
            ticket_id=str(lot["source_ticket_id"]) if lot.get("source_ticket_id") else None,
            stage="lager",
            event_type=event_type,
            ref_type="silo_lot",
            ref_id=str(lot["id"]),
            ref_label=lot["virtual_lot_number"],
            status_from=status_from,
            status_to=status_to,
            menge_kg=menge_kg,
            abweichung_grund=grund,
            bediener=bediener,
            source="manual",
        )

    # ── Aktionen ────────────────────────────────────────────────────────────────
    def block(self, lot_id: str, grund: str, bediener: str = "KIM") -> dict:
        if not grund.strip():
            raise LotActionError("Sperrgrund ist erforderlich.")
        lot = self._lot(lot_id)
        if lot["status"] == "gesperrt":
            raise LotActionError("Lot ist bereits gesperrt.")
        self.db.execute(
            text("UPDATE domain_inventory.silo_lots SET status='gesperrt', updated_at=now() "
                 "WHERE id = :id AND tenant_id = :t"),
            {"id": lot["id"], "t": self.tenant_id},
        )
        self._add_movement(lot["id"], "sperre", Decimal("0"), grund)
        ev = self._event(lot, "gesperrt", grund=grund, status_from=lot["status"],
                         status_to="gesperrt", menge_kg=None, bediener=bediener)
        self.db.commit()
        return {"ok": True, "lot": lot["virtual_lot_number"], "status": "gesperrt", "event": ev}

    def release(self, lot_id: str, grund: str, bediener: str = "KIM") -> dict:
        if not grund.strip():
            raise LotActionError("Freigabegrund ist erforderlich.")
        lot = self._lot(lot_id)
        if lot["status"] != "gesperrt":
            raise LotActionError("Nur gesperrte Lots können freigegeben werden.")
        self.db.execute(
            text("UPDATE domain_inventory.silo_lots SET status='active', updated_at=now() "
                 "WHERE id = :id AND tenant_id = :t"),
            {"id": lot["id"], "t": self.tenant_id},
        )
        self._add_movement(lot["id"], "freigabe", Decimal("0"), grund)
        ev = self._event(lot, "qs_freigabe", grund=grund, status_from=lot["status"],
                         status_to="active", menge_kg=None, bediener=bediener)
        self.db.commit()
        return {"ok": True, "lot": lot["virtual_lot_number"], "status": "active", "event": ev}

    def shrinkage(self, lot_id: str, menge_kg: float, grund: str, bediener: str = "KIM") -> dict:
        if not grund.strip():
            raise LotActionError("Schwundgrund ist erforderlich.")
        if menge_kg is None or menge_kg <= 0:
            raise LotActionError("Schwundmenge (kg) muss größer 0 sein.")
        lot = self._lot(lot_id)
        menge_t = Decimal(str(menge_kg)) / Decimal("1000")
        bestand = Decimal(str(lot["quantity_tons"] or 0))
        if menge_t > bestand:
            raise LotActionError(
                f"Schwund ({menge_kg} kg) übersteigt den Lot-Bestand ({float(bestand) * 1000:.0f} kg)."
            )
        neu = bestand - menge_t
        self.db.execute(
            text("UPDATE domain_inventory.silo_lots SET quantity_tons = :q, updated_at=now() "
                 "WHERE id = :id AND tenant_id = :t"),
            {"q": neu, "id": lot["id"], "t": self.tenant_id},
        )
        self._add_movement(lot["id"], "schwund", -menge_t, grund)
        ev = self._event(lot, "schwund", grund=grund, status_from=None, status_to=None,
                         menge_kg=-float(menge_kg), bediener=bediener)
        self.db.commit()
        return {"ok": True, "lot": lot["virtual_lot_number"],
                "bestand_kg": float(neu) * 1000, "event": ev}
