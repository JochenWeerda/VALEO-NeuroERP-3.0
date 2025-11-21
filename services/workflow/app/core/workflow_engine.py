"""
In-Memory Workflow-Engine mit Hook-Integration.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
import asyncio
import logging

from ..schemas.workflow import WorkflowDefinition, WorkflowInstance, HookConfig
from .policy_engine import PolicyEngine

if TYPE_CHECKING:
    from app.storage.repository import WorkflowRepository


logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Verwaltung von Workflow-Definitionen und -Instanzen."""

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        repository: Optional["WorkflowRepository"] = None,
        event_bus: Any | None = None,
    ) -> None:
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._instances: Dict[UUID, WorkflowInstance] = {}
        self._policy_engine = policy_engine or PolicyEngine()
        self._lock = asyncio.Lock()
        self._repository = repository
        self._event_bus = event_bus

    @staticmethod
    def _definition_key(definition: WorkflowDefinition) -> str:
        return WorkflowEngine.definition_key(definition.name, definition.version, definition.tenant)

    @staticmethod
    def definition_key(name: str, version: str, tenant: str) -> str:
        return f"{tenant}:{name}:{version}"

    async def register_definition(self, definition: WorkflowDefinition) -> WorkflowDefinition:
        if definition.initial_state not in definition.states:
            raise ValueError("Initialzustand muss zu den States gehören.")
        for transition in definition.transitions:
            if transition.source not in definition.states or transition.target not in definition.states:
                raise ValueError(f"Transition {transition.name} verweist auf unbekannte States.")
        async with self._lock:
            self._definitions[self._definition_key(definition)] = definition
        logger.info("Workflow-Definition %s v%s (%s) registriert", definition.name, definition.version, definition.tenant)
        if self._repository:
            await self._repository.save_definition(definition)
        return definition

    async def list_definitions(
        self,
        name: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> Iterable[WorkflowDefinition]:
        async with self._lock:
            definitions = list(self._definitions.values())
        if name:
            definitions = [definition for definition in definitions if definition.name == name]
        if tenant:
            definitions = [definition for definition in definitions if definition.tenant == tenant]
        return definitions

    async def get_definition(self, name: str, version: Optional[str], tenant: Optional[str]) -> WorkflowDefinition:
        async with self._lock:
            if version:
                key = self.definition_key(name, version, tenant or "default")
                definition = self._definitions.get(key)
                if not definition:
                    raise KeyError(f"Workflow {key} nicht gefunden.")
                return definition
            else:
                candidates = [
                    definition
                    for definition in self._definitions.values()
                    if definition.name == name and definition.tenant == (tenant or definition.tenant)
                ]
                if not candidates:
                    raise KeyError(f"Workflow {name} ({tenant or 'default'}) nicht gefunden.")
                candidates.sort(key=lambda d: d.version, reverse=True)
                return candidates[0]

    async def create_instance(
        self,
        definition: WorkflowDefinition,
        context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowInstance:
        instance = WorkflowInstance(
            workflow_name=definition.name,
            workflow_version=definition.version,
            tenant=definition.tenant,
            state=definition.initial_state,
            context=context or {},
        )
        async with self._lock:
            self._instances[instance.id] = instance
        logger.info("Workflow-Instanz %s gestartet (%s v%s)", instance.id, definition.name, definition.version)
        if self._repository:
            await self._repository.save_instance(instance)
        return instance

    async def get_instance(self, instance_id: UUID) -> WorkflowInstance:
        async with self._lock:
            instance = self._instances.get(instance_id)
        if not instance:
            if self._repository:
                persisted = await self._repository.get_instance(instance_id)
                if persisted:
                    async with self._lock:
                        self._instances[instance_id] = persisted
                    return persisted
            raise KeyError(f"Workflow-Instanz {instance_id} nicht gefunden.")
        return instance

    async def trigger_transition(
        self,
        instance_id: UUID,
        transition_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> WorkflowInstance:
        payload = payload or {}
        async with self._lock:
            instance = self._instances.get(instance_id)
            if not instance:
                raise KeyError(f"Workflow-Instanz {instance_id} nicht gefunden.")
            definition_key = self.definition_key(instance.workflow_name, instance.workflow_version, instance.tenant)
            definition = self._definitions.get(definition_key)
            if not definition:
                raise KeyError(f"Definition {definition_key} nicht gefunden.")
            transition = definition.transition_lookup().get(transition_name)
            if not transition:
                raise KeyError(f"Transition {transition_name} nicht bekannt.")
            if transition.source != instance.state:
                raise ValueError(f"Transition {transition_name} ist im Zustand {instance.state} nicht erlaubt.")

        context = {**instance.context, **payload}

        if not await self._evaluate_hooks(transition.conditions, context):
            raise PermissionError(f"Transition {transition_name} verweigert durch Policy.")

        await self._execute_hooks(transition.actions, context)

        async with self._lock:
            instance.state = transition.target
            instance.context.update(payload)
            instance.updated_at = datetime.utcnow()
            self._instances[instance_id] = instance

        logger.info("Transition %s auf Instanz %s ausgeführt (neuer Zustand: %s)", transition_name, instance_id, instance.state)
        if self._repository:
            await self._repository.save_instance(instance)
        return instance

    async def handle_event(self, event_type: str, tenant: str, data: Dict[str, Any]) -> List[WorkflowInstance]:
        async with self._lock:
            matching_definitions = [
                definition
                for definition in self._definitions.values()
                if definition.tenant == tenant and any(t.event_type == event_type for t in definition.transitions)
            ]
        updated_instances: List[WorkflowInstance] = []
        for definition in matching_definitions:
            relevant_transitions = [t for t in definition.transitions if t.event_type == event_type]
            async with self._lock:
                instances = [
                    instance
                    for instance in self._instances.values()
                    if instance.workflow_name == definition.name
                    and instance.workflow_version == definition.version
                    and instance.tenant == tenant
                ]
            for instance in instances:
                for transition in relevant_transitions:
                    if transition.source != instance.state:
                        continue
                    try:
                        updated_instance = await self.trigger_transition(instance.id, transition.name, data)
                        updated_instances.append(updated_instance)
                    except Exception as exc:
                        logger.warning(
                            "Transition %s durch Event %s fehlgeschlagen: %s",
                            transition.name,
                            event_type,
                            exc,
                        )
        return updated_instances

    async def simulate(self, definition: WorkflowDefinition, context: Dict[str, Any], transitions: List[str]) -> Dict[str, Any]:
        state = definition.initial_state
        history: List[Dict[str, Any]] = []
        errors: List[str] = []
        simulation_context = context.copy()
        for transition_name in transitions:
            transition = definition.transition_lookup().get(transition_name)
            if not transition:
                errors.append(f"Transition {transition_name} nicht gefunden.")
                break
            if transition.source != state:
                errors.append(f"Transition {transition_name} ist im Zustand {state} nicht erlaubt.")
                break
            allowed = await self._evaluate_hooks(transition.conditions, simulation_context)
            history.append(
                {
                    "transition": transition_name,
                    "from": state,
                    "to": transition.target,
                    "allowed": allowed,
                }
            )
            if not allowed:
                errors.append(f"Transition {transition_name} wurde durch Policy verhindert.")
                break
            await self._execute_hooks(transition.actions, simulation_context)
            state = transition.target
        return {
            "succeeded": len(errors) == 0,
            "final_state": state if not errors else None,
            "history": history,
            "errors": errors,
        }

    async def bootstrap_from_repository(self) -> None:
        if not self._repository:
            return
        definitions = await self._repository.load_definitions()
        count = len(definitions)
        async with self._lock:
            for definition in definitions:
                self._definitions[self._definition_key(definition)] = definition
        logger.info("Bootstrapped %s Workflow-Definition(en) aus Persistenz", count)

    async def _evaluate_hooks(self, hooks: List[HookConfig], context: Dict[str, Any]) -> bool:
        for hook in hooks:
            if hook.type == "policy":
                allowed = await self._policy_engine.evaluate(hook.name, context, hook.configuration)
                if not allowed:
                    return False
            elif hook.type == "before_transition":
                await self._policy_engine.execute(hook.name, context, hook.configuration)
        return True

    async def _execute_hooks(self, hooks: List[HookConfig], context: Dict[str, Any]) -> None:
        for hook in hooks:
            if hook.type in {"after_transition", "action"}:
                await self._policy_engine.execute(hook.name, context, hook.configuration)


