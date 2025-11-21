"""
Einfache Saga-Koordinator Implementierung.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4, UUID
import asyncio
import logging


logger = logging.getLogger(__name__)


SagaCallable = Callable[[Dict[str, Any]], asyncio.Future | Any]


class SagaStep:
    """Einzelner Schritt innerhalb einer Saga."""

    def __init__(self, name: str, action: SagaCallable, compensation: Optional[SagaCallable] = None) -> None:
        self.name = name
        self.action = action
        self.compensation = compensation


class SagaDefinition:
    """Deklaration einer Saga."""

    def __init__(self, name: str, steps: List[SagaStep]) -> None:
        self.name = name
        self.steps = steps


class SagaInstance:
    """Aktive Saga-Ausführung."""

    def __init__(self, definition: SagaDefinition, context: Dict[str, Any]) -> None:
        self.id: UUID = uuid4()
        self.definition = definition
        self.context = context
        self.completed_steps: List[str] = []
        self.status: str = "running"
        self.error: Optional[str] = None


class SagaCoordinator:
    """Koordiniert Langläuferprozesse und Kompensationen."""

    def __init__(self) -> None:
        self._definitions: Dict[str, SagaDefinition] = {}
        self._instances: Dict[UUID, SagaInstance] = {}
        self._lock = asyncio.Lock()

    async def register(self, definition: SagaDefinition) -> None:
        async with self._lock:
            self._definitions[definition.name] = definition
        logger.info("Saga %s registriert", definition.name)

    async def start(self, saga_name: str, context: Dict[str, Any]) -> SagaInstance:
        async with self._lock:
            definition = self._definitions.get(saga_name)
            if not definition:
                raise KeyError(f"Saga {saga_name} nicht registriert.")
            instance = SagaInstance(definition, context)
            self._instances[instance.id] = instance
        asyncio.create_task(self._execute(instance))
        return instance

    async def _execute(self, instance: SagaInstance) -> None:
        logger.info("Starte Saga %s (%s)", instance.definition.name, instance.id)
        for step in instance.definition.steps:
            try:
                result = step.action(instance.context)
                if asyncio.iscoroutine(result):
                    await result
                instance.completed_steps.append(step.name)
            except Exception as exc:
                logger.error("Saga-Schritt %s fehlgeschlagen: %s", step.name, exc, exc_info=True)
                instance.status = "compensating"
                instance.error = str(exc)
                await self._compensate(instance)
                return
        instance.status = "completed"
        logger.info("Saga %s (%s) abgeschlossen", instance.definition.name, instance.id)

    async def _compensate(self, instance: SagaInstance) -> None:
        for step_name in reversed(instance.completed_steps):
            step = next(step for step in instance.definition.steps if step.name == step_name)
            if step.compensation:
                try:
                    result = step.compensation(instance.context)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as exc:
                    logger.error("Kompensation für Schritt %s fehlgeschlagen: %s", step.name, exc, exc_info=True)
        instance.status = "compensated" if instance.error else "rolled_back"
        logger.info("Saga %s (%s) kompensiert", instance.definition.name, instance.id)

    async def status(self, instance_id: UUID) -> SagaInstance:
        async with self._lock:
            instance = self._instances.get(instance_id)
            if not instance:
                raise KeyError(f"Saga Instanz {instance_id} nicht gefunden.")
            return instance


