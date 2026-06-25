"""WF-COCKPIT-PERSIST-001 — DB-backed Workflow-Cockpit-Service.

Schreibt und liest wf_cockpit_instances, wf_cockpit_events, wf_cockpit_blockers
aus Schema domain_workflow via SQLAlchemy-Core (kein ORM-Mapping noetig).

Verwendet von: WorkflowCockpitService als optionaler Persistenz-Layer
               WfCockpitNatsProjector als Schreib-Ziel
               /workflow/cockpit API-Endpoints (Dead-Letter-Sicht)
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return str(uuid4())


class WorkflowCockpitPersistService:
    """Synchroner DB-Layer fuer Cockpit-Snapshots."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ------------------------------------------------------------------
    # Schreiben
    # ------------------------------------------------------------------

    def upsert_instance(
        self,
        *,
        process_instance_id: str,
        process_key: str,
        status: str,
        correlation_id: str,
        idempotency_key: str | None = None,
        business_object_ref: str | None = None,
        current_step: str | None = None,
        audit_ref: str | None = None,
        active_blocker_count: int = 0,
        replayable: bool = False,
    ) -> None:
        existing = self.db.execute(
            text("""
                SELECT id FROM domain_workflow.wf_cockpit_instances
                WHERE id = :id AND tenant_id = :tid
            """),
            {"id": process_instance_id, "tid": self.tenant_id},
        ).fetchone()

        now = _now()
        if existing is None:
            self.db.execute(
                text("""
                    INSERT INTO domain_workflow.wf_cockpit_instances
                      (id, tenant_id, process_key, status, correlation_id,
                       idempotency_key, business_object_ref, current_step,
                       audit_ref, created_at, updated_at,
                       active_blocker_count, replayable)
                    VALUES
                      (:id, :tid, :pk, :status, :corr, :idem, :bor, :step,
                       :aref, :now, :now, :abc, :repl)
                """),
                dict(
                    id=process_instance_id, tid=self.tenant_id, pk=process_key,
                    status=status, corr=correlation_id, idem=idempotency_key,
                    bor=business_object_ref, step=current_step, aref=audit_ref,
                    now=now, abc=active_blocker_count, repl=replayable,
                ),
            )
        else:
            self.db.execute(
                text("""
                    UPDATE domain_workflow.wf_cockpit_instances
                    SET status = :status, current_step = :step,
                        business_object_ref = :bor, updated_at = :now,
                        active_blocker_count = :abc, replayable = :repl
                    WHERE id = :id AND tenant_id = :tid
                """),
                dict(
                    status=status, step=current_step, bor=business_object_ref,
                    now=now, abc=active_blocker_count, repl=replayable,
                    id=process_instance_id, tid=self.tenant_id,
                ),
            )
        self.db.commit()

    def append_event(
        self,
        *,
        process_instance_id: str,
        kind: str,
        message: str,
        source: str = "workflow-cockpit",
        payload: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> str:
        import json
        event_id = _uid()
        self.db.execute(
            text("""
                INSERT INTO domain_workflow.wf_cockpit_events
                  (id, process_instance_id, tenant_id, kind, message, source, payload, occurred_at)
                VALUES
                  (:id, :pid, :tid, :kind, :msg, :src, :payload::jsonb, :now)
            """),
            dict(
                id=event_id, pid=process_instance_id,
                tid=tenant_id or self.tenant_id,
                kind=kind, msg=message, src=source,
                payload=json.dumps(payload or {}),
                now=_now(),
            ),
        )
        self.db.commit()
        return event_id

    def upsert_blocker(
        self,
        *,
        process_instance_id: str,
        blocker_id: str | None = None,
        blocker_type: str,
        message: str,
        external_system: str | None = None,
        retryable: bool = True,
    ) -> str:
        bid = blocker_id or _uid()
        existing = self.db.execute(
            text("""
                SELECT id FROM domain_workflow.wf_cockpit_blockers
                WHERE id = :bid AND tenant_id = :tid
            """),
            {"bid": bid, "tid": self.tenant_id},
        ).fetchone()
        if existing is None:
            self.db.execute(
                text("""
                    INSERT INTO domain_workflow.wf_cockpit_blockers
                      (id, process_instance_id, tenant_id, blocker_type,
                       message, external_system, retryable, resolved, since)
                    VALUES
                      (:bid, :pid, :tid, :bt, :msg, :esys, :retry, false, :now)
                """),
                dict(
                    bid=bid, pid=process_instance_id, tid=self.tenant_id,
                    bt=blocker_type, msg=message, esys=external_system,
                    retry=retryable, now=_now(),
                ),
            )
            self.db.commit()
        return bid

    def resolve_blocker(self, *, blocker_id: str) -> bool:
        result = self.db.execute(
            text("""
                UPDATE domain_workflow.wf_cockpit_blockers
                SET resolved = true, resolved_at = :now
                WHERE id = :bid AND tenant_id = :tid AND resolved = false
            """),
            {"bid": blocker_id, "tid": self.tenant_id, "now": _now()},
        )
        self.db.commit()
        return (result.rowcount or 0) > 0

    async def upsert_from_event(
        self,
        *,
        tenant_id: str,
        process_instance_id: str,
        process_key: str,
        status: str,
        correlation_id: str,
        current_step: str | None = None,
        business_object_ref: str | None = None,
        event_kind: str = "domain_event",
        event_message: str = "",
        event_payload: dict[str, Any] | None = None,
    ) -> None:
        """Async-Wrapper fuer NATS-Projector (laeuft in executor)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._upsert_from_event_sync(
                tenant_id=tenant_id,
                process_instance_id=process_instance_id,
                process_key=process_key,
                status=status,
                correlation_id=correlation_id,
                current_step=current_step,
                business_object_ref=business_object_ref,
                event_kind=event_kind,
                event_message=event_message,
                event_payload=event_payload or {},
            ),
        )

    def _upsert_from_event_sync(self, **kwargs: Any) -> None:
        tid = kwargs["tenant_id"]
        orig_tid = self.tenant_id
        self.tenant_id = tid
        try:
            self.upsert_instance(
                process_instance_id=kwargs["process_instance_id"],
                process_key=kwargs["process_key"],
                status=kwargs["status"],
                correlation_id=kwargs["correlation_id"],
                current_step=kwargs.get("current_step"),
                business_object_ref=kwargs.get("business_object_ref"),
            )
            self.append_event(
                process_instance_id=kwargs["process_instance_id"],
                kind=kwargs.get("event_kind", "domain_event"),
                message=kwargs.get("event_message", ""),
                payload=kwargs.get("event_payload"),
                tenant_id=tid,
            )
        finally:
            self.tenant_id = orig_tid

    # ------------------------------------------------------------------
    # Lesen / Dead-Letter-Sicht
    # ------------------------------------------------------------------

    def list_instances(
        self,
        *,
        status: str | None = None,
        process_key: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        sql = """
            SELECT id, tenant_id, process_key, status, correlation_id,
                   idempotency_key, business_object_ref, current_step,
                   created_at, updated_at, active_blocker_count, replayable
            FROM domain_workflow.wf_cockpit_instances
            WHERE tenant_id = :tid
        """
        params: dict[str, Any] = {"tid": self.tenant_id}
        if status:
            sql += " AND status = :status"
            params["status"] = status
        if process_key:
            sql += " AND process_key = :pk"
            params["pk"] = process_key
        sql += " ORDER BY updated_at DESC LIMIT :lim OFFSET :off"
        params["lim"] = limit
        params["off"] = offset
        rows = self.db.execute(text(sql), params).fetchall()
        return [dict(r._mapping) for r in rows]

    def dead_letter_view(self, *, limit: int = 100) -> dict[str, Any]:
        """Prozesse in FAILED oder BLOCKED_EXTERNAL_GATE mit offenen Blockern."""
        failed_rows = self.db.execute(
            text("""
                SELECT i.id, i.process_key, i.status, i.correlation_id,
                       i.current_step, i.updated_at, i.replayable,
                       COUNT(b.id) FILTER (WHERE b.resolved = false) AS open_blocker_count
                FROM domain_workflow.wf_cockpit_instances i
                LEFT JOIN domain_workflow.wf_cockpit_blockers b
                  ON b.process_instance_id = i.id
                WHERE i.tenant_id = :tid
                  AND i.status IN ('failed', 'blocked_external_gate')
                GROUP BY i.id, i.process_key, i.status, i.correlation_id,
                         i.current_step, i.updated_at, i.replayable
                ORDER BY i.updated_at DESC
                LIMIT :lim
            """),
            {"tid": self.tenant_id, "lim": limit},
        ).fetchall()

        items = []
        for r in failed_rows:
            d = dict(r._mapping)
            d["updated_at"] = d["updated_at"].isoformat() if d.get("updated_at") else None
            items.append(d)

        return {
            "tenant_id": self.tenant_id,
            "dead_letter_count": len(items),
            "items": items,
        }

    def get_instance_detail(self, process_instance_id: str) -> dict[str, Any] | None:
        row = self.db.execute(
            text("""
                SELECT * FROM domain_workflow.wf_cockpit_instances
                WHERE id = :id AND tenant_id = :tid
            """),
            {"id": process_instance_id, "tid": self.tenant_id},
        ).fetchone()
        if not row:
            return None
        result = dict(row._mapping)
        result["created_at"] = result["created_at"].isoformat() if result.get("created_at") else None
        result["updated_at"] = result["updated_at"].isoformat() if result.get("updated_at") else None

        events = self.db.execute(
            text("""
                SELECT id, kind, message, source, payload, occurred_at
                FROM domain_workflow.wf_cockpit_events
                WHERE process_instance_id = :pid
                ORDER BY occurred_at ASC
            """),
            {"pid": process_instance_id},
        ).fetchall()
        blockers = self.db.execute(
            text("""
                SELECT id, blocker_type, message, external_system,
                       retryable, resolved, since, resolved_at
                FROM domain_workflow.wf_cockpit_blockers
                WHERE process_instance_id = :pid
                ORDER BY since DESC
            """),
            {"pid": process_instance_id},
        ).fetchall()

        def _ser_row(r: Any) -> dict:
            d = dict(r._mapping)
            for k, v in d.items():
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
            return d

        result["events"] = [_ser_row(e) for e in events]
        result["blockers"] = [_ser_row(b) for b in blockers]
        return result
