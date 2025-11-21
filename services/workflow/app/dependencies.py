"""
Dependency Injection und konfigurierbare Singletons.
"""

from __future__ import annotations

from typing import Optional

from .core.workflow_engine import WorkflowEngine
from .core.policy_engine import PolicyEngine
from .core.event_router import EventRouter
from .core.saga import SagaCoordinator
from .integration.event_bus import EventBus
from .storage.repository import WorkflowRepository

_policy_engine: Optional[PolicyEngine] = None
_workflow_engine: Optional[WorkflowEngine] = None
_event_router: Optional[EventRouter] = None
_saga_coordinator: Optional[SagaCoordinator] = None


def configure_dependencies(repository: WorkflowRepository, event_bus: Optional[EventBus] = None) -> None:
    """Initialisiert die globalen Singletons (z. B. beim App-Startup)."""
    global _policy_engine, _workflow_engine, _event_router, _saga_coordinator

    _policy_engine = PolicyEngine()
    _workflow_engine = WorkflowEngine(policy_engine=_policy_engine, repository=repository, event_bus=event_bus)
    _event_router = EventRouter(_workflow_engine, event_bus=event_bus)
    _saga_coordinator = SagaCoordinator()

    if event_bus:
        async def emit_event_action(context, config):
            event_type = config.get("event_type")
            if not event_type:
                raise ValueError("Policy-Aktion 'emit_event' erfordert 'event_type' in der Konfiguration.")
            tenant = config.get("tenant") or context.get("tenant", "default")
            data = config.get("data") or context
            await _event_router.emit_event(event_type, tenant, data)

        _policy_engine.register_action("emit_event", emit_event_action)


def get_policy_engine() -> PolicyEngine:
    assert _policy_engine is not None, "Dependencies nicht konfiguriert. configure_dependencies() zuerst aufrufen."
    return _policy_engine


def get_engine() -> WorkflowEngine:
    assert _workflow_engine is not None, "Dependencies nicht konfiguriert. configure_dependencies() zuerst aufrufen."
    return _workflow_engine


def get_event_router() -> EventRouter:
    assert _event_router is not None, "Dependencies nicht konfiguriert. configure_dependencies() zuerst aufrufen."
    return _event_router


def get_saga_coordinator() -> SagaCoordinator:
    assert _saga_coordinator is not None, "Dependencies nicht konfiguriert. configure_dependencies() zuerst aufrufen."
    return _saga_coordinator

