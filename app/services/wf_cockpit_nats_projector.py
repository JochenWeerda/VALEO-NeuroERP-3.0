"""WF-COCKPIT-PERSIST-001 — NATS-JetStream-Projector fuer Workflow-Cockpit.

Abonniert NATS-Subjects fuer Domain-Events und schreibt Cockpit-Snapshots
in domain_workflow.wf_cockpit_instances via WorkflowCockpitPersistService.

Subjects (Wildcard): workflow.>
  workflow.{process_key}.created
  workflow.{process_key}.status_changed
  workflow.{process_key}.blocker_added
  workflow.{process_key}.blocker_resolved
  workflow.{process_key}.completed
  workflow.{process_key}.failed

Alle Domain-Events werden auch unter domain.> abonniert und als DOMAIN_EVENT
im Cockpit gespeichert wenn eine process_instance_id im Header enthalten ist.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# NATS importiert optional — fehlt in Unit-Test-Umgebung
try:
    import nats  # type: ignore
    from nats.aio.client import Client as NatsClient  # type: ignore
    _NATS_AVAILABLE = True
except ImportError:
    _NATS_AVAILABLE = False

from app.services.wf_cockpit_persist_service import WorkflowCockpitPersistService


class WfCockpitNatsProjector:
    """Subscribes to NATS and projects domain events into the cockpit DB."""

    WORKFLOW_SUBJECT = "workflow.>"
    DOMAIN_EVENT_SUBJECT = "domain.>"

    def __init__(self, persist_service: WorkflowCockpitPersistService) -> None:
        self._svc = persist_service
        self._nc: Any = None
        self._running = False

    async def start(self, nats_url: str = "nats://localhost:4222") -> None:
        if not _NATS_AVAILABLE:
            logger.warning("NATS nicht verfuegbar — Cockpit-Projector bleibt offline")
            return
        self._nc = await nats.connect(nats_url)  # type: ignore[attr-defined]
        await self._nc.subscribe(self.WORKFLOW_SUBJECT, cb=self._handle_workflow)
        await self._nc.subscribe(self.DOMAIN_EVENT_SUBJECT, cb=self._handle_domain)
        self._running = True
        logger.info("WfCockpitNatsProjector gestartet auf %s", nats_url)

    async def stop(self) -> None:
        if self._nc:
            await self._nc.drain()
            self._running = False

    async def _handle_workflow(self, msg: Any) -> None:
        try:
            data: dict[str, Any] = json.loads(msg.data.decode())
            subject_parts = msg.subject.split(".")
            event_type = subject_parts[-1] if len(subject_parts) >= 3 else "unknown"
            process_key = subject_parts[1] if len(subject_parts) >= 3 else "unknown"

            tenant_id = data.get("tenant_id", "unknown")
            instance_id = data.get("process_instance_id") or data.get("instance_id", "")
            correlation_id = data.get("correlation_id", instance_id)
            status = data.get("status", "running")
            current_step = data.get("current_step")
            business_object_ref = data.get("business_object_ref")

            if not instance_id:
                logger.debug("workflow event ohne process_instance_id — ignoriert: %s", msg.subject)
                return

            await self._svc.upsert_from_event(
                tenant_id=tenant_id,
                process_instance_id=instance_id,
                process_key=process_key,
                status=status,
                correlation_id=correlation_id,
                current_step=current_step,
                business_object_ref=business_object_ref,
                event_kind=_map_event_kind(event_type),
                event_message=f"NATS: {msg.subject}",
                event_payload=data,
            )
        except Exception:
            logger.exception("Fehler in _handle_workflow: %s", msg.subject)

    async def _handle_domain(self, msg: Any) -> None:
        try:
            data: dict[str, Any] = json.loads(msg.data.decode())
            instance_id = (
                data.get("process_instance_id")
                or data.get("workflow_instance_id")
                or data.get("instance_id")
            )
            if not instance_id:
                return

            tenant_id = data.get("tenant_id", "unknown")
            await self._svc.append_event(
                tenant_id=tenant_id,
                process_instance_id=instance_id,
                kind="domain_event",
                message=f"Domain-Event: {msg.subject}",
                source=msg.subject,
                payload=data,
            )
        except Exception:
            logger.exception("Fehler in _handle_domain: %s", msg.subject)


def _map_event_kind(event_type: str) -> str:
    mapping = {
        "created": "created",
        "status_changed": "status_changed",
        "blocker_added": "external_gate",
        "blocker_resolved": "domain_event",
        "completed": "status_changed",
        "failed": "status_changed",
        "retry_requested": "retry_requested",
    }
    return mapping.get(event_type, "domain_event")
