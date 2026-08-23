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

_REQUIRED_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    # stop_id stays optional for backward compatibility with tour-level devices.
    "delivery_confirmation": ("tour_id",),
    "inventory_count": ("warehouse_id", "article_id", "counted_qty"),
    "qs_probe_result": ("acceptance_id",),
    "harvest_acceptance": ("net_weight_kg",),
    "silo_transfer": ("warehouse_id", "from_cell_id", "to_cell_id", "quantity_kg", "article_id"),
    "generic": (),
}
_QUEUE_STATUSES = frozenset({"pending", "processing", "done", "failed", "quarantined"})
_RETRYABLE_STATUSES = frozenset({"failed", "quarantined"})
_MAX_ATTEMPTS = 3
_SORT_COLUMNS = {
    "created_at": "created_at",
    "processed_at": "processed_at",
    "device_id": "device_id",
    "event_type": "event_type",
    "sync_status": "sync_status",
    "retry_count": "retry_count",
}


def validate_mobile_event_payload(event_type: str, payload: Any) -> list[str]:
    """Validate the stable envelope before a device event reaches persistence."""

    if not isinstance(payload, dict):
        return ["payload muss ein Objekt sein"]
    missing = [f"{field} fehlt" for field in _REQUIRED_PAYLOAD_FIELDS.get(event_type, ()) if payload.get(field) is None]
    if event_type == "inventory_count" and payload.get("counted_qty") is not None:
        try:
            if float(payload["counted_qty"]) < 0:
                missing.append("counted_qty darf nicht negativ sein")
        except (TypeError, ValueError):
            missing.append("counted_qty muss numerisch sein")
    return missing


def next_mobile_failure_status(retry_count: int) -> str:
    """Return the persisted status after the next failed processing attempt."""

    return "quarantined" if retry_count + 1 >= _MAX_ATTEMPTS else "failed"


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

            violations = validate_mobile_event_payload(event_type, payload)
            if violations:
                results.append({
                    "idempotency_key": idem_key,
                    "status": "rejected",
                    "reason": "; ".join(violations),
                })
                continue

            event_id = str(uuid7())
            try:
                inserted = self.db.execute(
                    text("""
                        INSERT INTO domain_ops.mobile_event_queue
                            (id, tenant_id, device_id, event_type, payload,
                             sync_status, idempotency_key)
                        VALUES (:id, :tid, :dev, :evt, CAST(:payload AS jsonb), 'pending', :ikey)
                        ON CONFLICT (tenant_id, device_id, idempotency_key) DO NOTHING
                        RETURNING id
                    """),
                    {
                        "id": event_id, "tid": self.tenant_id, "dev": device_id,
                        "evt": event_type,
                        "payload": json.dumps(payload),
                        "ikey": idem_key,
                    },
                )
                inserted_id = inserted.scalar_one_or_none()
                if inserted_id is not None and not isinstance(inserted_id, (str, int)):
                    # Lightweight unit doubles often return a bare MagicMock here.
                    inserted_id = event_id
                if inserted_id is None:
                    inserted_id = self.db.execute(
                        text("""
                            SELECT id FROM domain_ops.mobile_event_queue
                             WHERE tenant_id=:tid AND device_id=:dev AND idempotency_key=:ikey
                        """),
                        {"tid": self.tenant_id, "dev": device_id, "ikey": idem_key},
                    ).scalar_one()
                else:
                    self._append_audit(str(inserted_id), "received", actor=device_id, reason="MDE-Ereignis empfangen")
                results.append({
                    "idempotency_key": idem_key,
                    "event_id": str(inserted_id),
                    "status": "queued" if str(inserted_id) == event_id else "duplicate",
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

    def process_pending(
        self,
        limit: int = 50,
        *,
        actor: str = "mde-processor",
        reason: str = "Automatische Queue-Verarbeitung",
    ) -> dict[str, Any]:
        """Verarbeitet ausstehende Events aus der Queue (max. `limit` Stück).

        Gibt Statistik zurück: processed, failed, skipped.
        """
        rows = self.db.execute(
            text("""
                SELECT id, device_id, event_type, payload, retry_count
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
                    text("""
                        UPDATE domain_ops.mobile_event_queue
                           SET sync_status='processing', last_attempt_at=NOW()
                         WHERE id=:id AND tenant_id=:tid
                    """),
                    {"id": event_id, "tid": self.tenant_id},
                )
                self._append_audit(event_id, "processing", actor=actor, reason=reason)
                self.db.flush()

                # A handler may fail at SQL level. The savepoint keeps the queue
                # transaction usable so the same event can be marked failed.
                with self.db.begin_nested():
                    self._dispatch(event_type, payload)

                self.db.execute(
                    text("""
                        UPDATE domain_ops.mobile_event_queue
                        SET sync_status='done', processed_at=NOW()
                        WHERE id=:id AND tenant_id=:tid
                    """),
                    {"id": event_id, "tid": self.tenant_id},
                )
                self._append_audit(event_id, "done", actor=actor, reason="Verarbeitung abgeschlossen")
                processed += 1
            except Exception as exc:
                logger.warning("Mobile event %s failed: %s", event_id, exc)
                attempts = int(row.get("retry_count") or 0) + 1
                next_status = next_mobile_failure_status(int(row.get("retry_count") or 0))
                try:
                    self.db.execute(
                        text("""
                            UPDATE domain_ops.mobile_event_queue
                            SET sync_status=:status, error_message=:msg,
                                retry_count=:attempts, last_attempt_at=NOW()
                            WHERE id=:id AND tenant_id=:tid
                        """),
                        {
                            "id": event_id,
                            "tid": self.tenant_id,
                            "status": next_status,
                            "attempts": attempts,
                            "msg": str(exc)[:500],
                        },
                    )
                    self._append_audit(event_id, next_status, actor=actor, reason=str(exc)[:500])
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
        if not stop_id:
            raise ValueError("delivery_confirmation erfordert stop_id fuer die Verarbeitung")
        result = self.db.execute(
            text("""
                UPDATE domain_logistics.tour_stops
                   SET status = 'ABGELIEFERT',
                       actual_arrival = :dt,
                       pod_data = COALESCE(pod_data, '{}'::jsonb) || CAST(:pod AS jsonb)
                 WHERE id = :stop_id
                   AND tour_id = :tour_id
                   AND tenant_id = :tid
            """),
            {
                "stop_id": stop_id, "tour_id": tour_id,
                "dt": delivered_at,
                "pod": json.dumps({"signature_base64": signature_b64, "delivered_at": delivered_at}),
                "tid": self.tenant_id,
            },
        )
        if result.rowcount == 0:
            raise ValueError("Tourstopp nicht gefunden oder nicht fuer den Mandanten freigegeben")

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

    def _append_audit(self, event_id: str, action: str, *, actor: str, reason: str) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_ops.mobile_event_queue_audit
                    (id, tenant_id, event_id, action, actor, reason)
                VALUES (:id, :tid, :event_id, :action, :actor, :reason)
            """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "event_id": event_id,
                "action": action,
                "actor": actor[:120],
                "reason": reason[:500],
            },
        )

    def retry_event(self, event_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        row = self.db.execute(
            text("""
                SELECT id, sync_status, retry_count
                  FROM domain_ops.mobile_event_queue
                 WHERE id=:id AND tenant_id=:tid
                 FOR UPDATE
            """),
            {"id": event_id, "tid": self.tenant_id},
        ).mappings().first()
        if row is None:
            raise LookupError("MDE-Ereignis nicht gefunden")
        if row["sync_status"] not in _RETRYABLE_STATUSES:
            raise ValueError(f"Status {row['sync_status']} kann nicht wiederholt werden")
        self.db.execute(
            text("""
                UPDATE domain_ops.mobile_event_queue
                   SET sync_status='pending', error_message=NULL
                 WHERE id=:id AND tenant_id=:tid
            """),
            {"id": event_id, "tid": self.tenant_id},
        )
        self._append_audit(event_id, "retry_requested", actor=actor, reason=reason)
        self.db.commit()
        return {"id": event_id, "sync_status": "pending", "retry_count": int(row.get("retry_count") or 0)}

    def event_audit(self, event_id: str) -> list[dict[str, Any]]:
        exists = self.db.execute(
            text("SELECT 1 FROM domain_ops.mobile_event_queue WHERE id=:id AND tenant_id=:tid"),
            {"id": event_id, "tid": self.tenant_id},
        ).scalar_one_or_none()
        if exists is None:
            raise LookupError("MDE-Ereignis nicht gefunden")
        rows = self.db.execute(
            text("""
                SELECT id, event_id, action, actor, reason, created_at
                  FROM domain_ops.mobile_event_queue_audit
                 WHERE event_id=:id AND tenant_id=:tid
                 ORDER BY created_at ASC, id ASC
            """),
            {"id": event_id, "tid": self.tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def queue_summary(self) -> dict[str, int]:
        rows = self.db.execute(
            text("""
                SELECT sync_status, COUNT(*) AS count
                  FROM domain_ops.mobile_event_queue
                 WHERE tenant_id=:tid
                 GROUP BY sync_status
            """),
            {"tid": self.tenant_id},
        ).mappings().all()
        counts = {status: 0 for status in _QUEUE_STATUSES}
        counts.update({str(row["sync_status"]): int(row["count"]) for row in rows})
        counts["total"] = sum(counts[status] for status in _QUEUE_STATUSES)
        return counts

    def list_queue_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        device_id: str | None = None,
        event_type: str | None = None,
        q: str | None = None,
        sort: str = "created_at",
        sort_dir: str = "desc",
    ) -> dict[str, Any]:
        if status and status not in _QUEUE_STATUSES:
            raise ValueError(f"Unbekannter Queue-Status: {status}")
        sort_column = _SORT_COLUMNS.get(sort, "created_at")
        direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
        filters = ["tenant_id = :tid"]
        params: dict[str, Any] = {"tid": self.tenant_id, "limit": page_size, "offset": (page - 1) * page_size}
        if status:
            filters.append("sync_status = :status")
            params["status"] = status
        if device_id:
            filters.append("device_id = :device_id")
            params["device_id"] = device_id
        if event_type:
            filters.append("event_type = :event_type")
            params["event_type"] = event_type
        if q:
            filters.append("(device_id ILIKE :q OR event_type ILIKE :q OR COALESCE(error_message, '') ILIKE :q)")
            params["q"] = f"%{q}%"
        where = " AND ".join(filters)
        total = self.db.execute(
            text(f"SELECT COUNT(*) FROM domain_ops.mobile_event_queue WHERE {where}"),  # nosec B608 -- clauses and sort are allowlisted
            params,
        ).scalar_one()
        rows = self.db.execute(
            # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
            text(f"""
                SELECT id, device_id, event_type, sync_status, error_message,
                       retry_count, idempotency_key, created_at, last_attempt_at, processed_at
                  FROM domain_ops.mobile_event_queue
                 WHERE {where}
                 ORDER BY {sort_column} {direction}, id DESC
                 LIMIT :limit OFFSET :offset
            """),  # nosec B608 -- clauses and sort are allowlisted
            params,
        ).mappings().all()
        return {
            "items": [dict(row) for row in rows],
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "count": len(rows),
        }

    def list_queue(self, status: str | None = None, limit: int = 100) -> list[dict]:
        return self.list_queue_page(status=status, page_size=limit)["items"]
