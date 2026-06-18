"""MOB-SYNC-001: Mobile Offline-Sync Service.

Nimmt Events aus der Offline-Queue entgegen und verarbeitet sie idempotent.
Unterstützte Event-Typen:
  - delivery_confirmation  — Lieferrückmeldung (Tourenplanung)
  - inventory_count        — Inventurzählung (Lager)
  - qs_probe_result        — QS-Probe-Ergebnis (Qualitätssicherung)
  - harvest_acceptance     — Ernte-Annahme (Agrar)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

_SUPPORTED_EVENT_TYPES = frozenset({
    "delivery_confirmation",
    "inventory_count",
    "qs_probe_result",
    "harvest_acceptance",
    "silo_transfer",
    "generic",
})


class MobileSyncService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def enqueue_events(self, device_id: str, events: list[dict]) -> list[dict]:
        """Nimmt eine Liste von Offline-Events entgegen und schreibt sie in die Queue.

        Jedes Event muss folgende Felder haben:
          - event_type: str (aus _SUPPORTED_EVENT_TYPES)
          - payload: dict
          - idempotency_key: str (Client-generiert, z.B. UUID)

        Duplikate werden erkannt (UNIQUE auf idempotency_key) und übersprungen.
        """
        results = []
        for ev in events:
            event_type = ev.get("event_type", "generic")
            payload = ev.get("payload", {})
            idem_key = ev.get("idempotency_key") or str(uuid7())

            if event_type not in _SUPPORTED_EVENT_TYPES:
                results.append({
                    "idempotency_key": idem_key,
                    "status": "rejected",
                    "reason": f"Unbekannter event_type: {event_type}",
                })
                continue

            event_id = str(uuid7())
            try:
                self.db.execute(
                    text("""
                        INSERT INTO domain_ops.mobile_event_queue
                            (id, tenant_id, device_id, event_type, payload,
                             sync_status, idempotency_key)
                        VALUES (:id, :tid, :dev, :evt, :payload::jsonb, 'pending', :ikey)
                        ON CONFLICT (tenant_id, device_id, idempotency_key) DO NOTHING
                    """),
                    {
                        "id": event_id, "tid": self.tenant_id, "dev": device_id,
                        "evt": event_type,
                        "payload": json.dumps(payload),
                        "ikey": idem_key,
                    },
                )
                results.append({
                    "idempotency_key": idem_key,
                    "event_id": event_id,
                    "status": "queued",
                })
            except Exception as exc:
                logger.warning("Event enqueue failed: %s — %s", idem_key, exc)
                results.append({
                    "idempotency_key": idem_key,
                    "status": "error",
                    "reason": str(exc),
                })

        self.db.commit()
        return results

    def process_pending(self, limit: int = 50) -> dict[str, Any]:
        """Verarbeitet ausstehende Events aus der Queue (max. `limit` Stück).

        Gibt Statistik zurück: processed, failed, skipped.
        """
        rows = self.db.execute(
            text("""
                SELECT id, device_id, event_type, payload
                FROM domain_ops.mobile_event_queue
                WHERE tenant_id = :tid AND sync_status = 'pending'
                ORDER BY created_at ASC
                LIMIT :lim
                FOR UPDATE SKIP LOCKED
            """),
            {"tid": self.tenant_id, "lim": limit},
        ).mappings().all()

        processed = failed = skipped = 0

        for row in rows:
            event_id = str(row["id"])
            event_type = str(row["event_type"])
            payload = row["payload"] if isinstance(row["payload"], dict) else {}

            try:
                self.db.execute(
                    text("UPDATE domain_ops.mobile_event_queue SET sync_status='processing' WHERE id=:id"),
                    {"id": event_id},
                )
                self.db.flush()

                self._dispatch(event_type, payload)

                self.db.execute(
                    text("""
                        UPDATE domain_ops.mobile_event_queue
                        SET sync_status='done', processed_at=NOW()
                        WHERE id=:id
                    """),
                    {"id": event_id},
                )
                processed += 1
            except Exception as exc:
                logger.warning("Mobile event %s failed: %s", event_id, exc)
                try:
                    self.db.execute(
                        text("""
                            UPDATE domain_ops.mobile_event_queue
                            SET sync_status='failed', error_message=:msg
                            WHERE id=:id
                        """),
                        {"id": event_id, "msg": str(exc)[:500]},
                    )
                except Exception:
                    pass
                failed += 1

        self.db.commit()
        return {"processed": processed, "failed": failed, "skipped": skipped, "total": len(rows)}

    def _dispatch(self, event_type: str, payload: dict) -> None:
        """Verteilt Events auf fachliche Handler."""
        if event_type == "delivery_confirmation":
            self._handle_delivery_confirmation(payload)
        elif event_type == "inventory_count":
            self._handle_inventory_count(payload)
        elif event_type == "qs_probe_result":
            self._handle_qs_probe(payload)
        elif event_type == "harvest_acceptance":
            self._handle_harvest_acceptance(payload)
        elif event_type == "silo_transfer":
            self._handle_silo_transfer(payload)
        # generic: nur in Queue gespeichert, keine weitere Aktion

    def _handle_delivery_confirmation(self, payload: dict) -> None:
        tour_id = payload.get("tour_id")
        stop_id = payload.get("stop_id")
        delivered_at = payload.get("delivered_at") or datetime.now(timezone.utc).isoformat()
        signature_b64 = payload.get("signature_b64")
        if not tour_id:
            raise ValueError("delivery_confirmation erfordert tour_id")
        self.db.execute(
            text("""
                UPDATE domain_ops.logistics_tour_stops
                SET status = 'geliefert',
                    actual_delivery_at = :dt,
                    signature_b64 = :sig,
                    updated_at = NOW()
                WHERE id = :stop_id
                  AND (SELECT tenant_id FROM domain_ops.logistics_tours WHERE id = :tour_id) = :tid
            """),
            {
                "stop_id": stop_id, "tour_id": tour_id,
                "dt": delivered_at, "sig": signature_b64, "tid": self.tenant_id,
            },
        )

    def _handle_inventory_count(self, payload: dict) -> None:
        warehouse_id = payload.get("warehouse_id")
        article_id = payload.get("article_id")
        counted_qty = payload.get("counted_qty")
        if not all([warehouse_id, article_id, counted_qty is not None]):
            raise ValueError("inventory_count erfordert warehouse_id, article_id, counted_qty")
        movement_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, article_id, warehouse_id, movement_type, quantity, unit,
                     reference_number, movement_date, movement_time,
                     notes, booking_user, auto_created, ownership_type, tenant_id, created_at)
                VALUES (:id, :art, :wid, 'inventory_count', :qty, 'EA',
                        :ref, CURRENT_DATE, NOW()::time,
                        'Inventurzählung via Mobile', 'mobile_app', true, 'owned', :tid, NOW())
            """),
            {
                "id": movement_id, "art": article_id, "wid": warehouse_id,
                "qty": float(counted_qty),
                "ref": f"INV-MOB-{movement_id[:8].upper()}",
                "tid": self.tenant_id,
            },
        )

    def _handle_qs_probe(self, payload: dict) -> None:
        acceptance_id = payload.get("acceptance_id")
        moisture_pct = payload.get("moisture_pct")
        impurities_pct = payload.get("impurities_pct")
        hl_weight = payload.get("hl_weight_kg_per_hl")
        if not acceptance_id:
            raise ValueError("qs_probe_result erfordert acceptance_id")
        # Qualitätsprotokoll anlegen (Best-Effort)
        qp_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_agrar.quality_protocols
                    (id, tenant_id, harvest_acceptance_id, protocol_number,
                     version, moisture_pct, impurities_pct, hl_weight_kg_per_hl,
                     source_type, is_final, created_at)
                VALUES (:id, :tid, :aid, :pnr, 1,
                        :moist, :imp, :hl,
                        'device', false, NOW())
                ON CONFLICT DO NOTHING
            """),
            {
                "id": qp_id, "tid": self.tenant_id, "aid": acceptance_id,
                "pnr": f"QS-MOB-{qp_id[:8].upper()}",
                "moist": moisture_pct, "imp": impurities_pct, "hl": hl_weight,
            },
        )

    def _handle_harvest_acceptance(self, payload: dict) -> None:
        acceptance_number = payload.get("acceptance_number") or f"ANA-MOB-{uuid7()[:8].upper()}"
        supplier_id = payload.get("supplier_id")
        net_weight_kg = payload.get("net_weight_kg")
        if not net_weight_kg:
            raise ValueError("harvest_acceptance erfordert net_weight_kg")
        ana_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_agrar.harvest_acceptances
                    (id, tenant_id, acceptance_number, supplier_id,
                     net_weight_kg, status, accepted_at, created_at)
                VALUES (:id, :tid, :nr, :sup, :nw, 'erfasst', NOW(), NOW())
                ON CONFLICT DO NOTHING
            """),
            {
                "id": ana_id, "tid": self.tenant_id, "nr": acceptance_number,
                "sup": supplier_id, "nw": float(net_weight_kg),
            },
        )

    def _handle_silo_transfer(self, payload: dict) -> None:
        """Delegiert an AgriSiloMaterialFlowService."""
        from decimal import Decimal
        from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService
        svc = AgriSiloMaterialFlowService(self.db, self.tenant_id)
        svc.book_material_transfer(
            warehouse_id=payload["warehouse_id"],
            from_cell_id=payload["from_cell_id"],
            to_cell_id=payload["to_cell_id"],
            quantity_kg=Decimal(str(payload["quantity_kg"])),
            article_id=payload["article_id"],
            lot_id=payload.get("lot_id"),
            booked_by=payload.get("booked_by", "mobile_app"),
            reference=payload.get("reference"),
        )

    def list_queue(self, status: str | None = None, limit: int = 100) -> list[dict]:
        filters = ["tenant_id = :tid"]
        params: dict = {"tid": self.tenant_id, "lim": limit}
        if status:
            filters.append("sync_status = :status")
            params["status"] = status
        where = " AND ".join(filters)
        rows = self.db.execute(
            text(f"SELECT * FROM domain_ops.mobile_event_queue WHERE {where} ORDER BY created_at DESC LIMIT :lim"),  # nosec S608 -- reviewed-safe: where fragments are code-controlled, values parameterized
            params,
        ).mappings().all()
        return [dict(r) for r in rows]
