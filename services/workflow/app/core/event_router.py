"""
Event-Routing und Integration zum Workflow-Engine.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING
import logging

from ..schemas.workflow import EventPayload
from .workflow_engine import WorkflowEngine

if TYPE_CHECKING:
    from app.integration.event_bus import EventBus


logger = logging.getLogger(__name__)


class EventRouter:
    """Vereinfacht die Entgegennahme und Zuordnung von Domain-Events."""

    def __init__(self, engine: WorkflowEngine, event_bus: Optional["EventBus"] = None) -> None:
        self._engine = engine
        self._event_bus = event_bus

    async def route_event(self, payload: EventPayload) -> Dict[str, Any]:
        logger.info("EventRouter verarbeitet Event %s", payload.event_type)
        updated_instances = await self._engine.handle_event(payload.event_type, payload.tenant, payload.data)
        return {
            "event_type": payload.event_type,
            "tenant": payload.tenant,
            "affected_instances": [str(instance.id) for instance in updated_instances],
            "count": len(updated_instances),
        }

    async def emit_event(self, event_type: str, tenant: str, data: Optional[Dict[str, Any]] = None) -> None:
        payload = data or {}
        if self._event_bus:
            await self._event_bus.publish(event_type, tenant, payload)
        else:
            logger.debug("EventRouter emit_event (kein EventBus konfiguriert): %s %s %s", event_type, tenant, payload)


