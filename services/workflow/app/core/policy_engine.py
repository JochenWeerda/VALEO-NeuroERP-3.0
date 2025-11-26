"""
Policy- und Hook-Engine für Workflow-Entscheidungen.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional
import asyncio
import logging


logger = logging.getLogger(__name__)


PolicyCallable = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[bool] | bool]
ActionCallable = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[None] | None]


class PolicyEngine:
    """Verwalten und Ausführen deklarativer Policies und Aktionen."""

    def __init__(self) -> None:
        self._policies: Dict[str, PolicyCallable] = {}
        self._actions: Dict[str, ActionCallable] = {}
        self._register_builtin()

    def _register_builtin(self) -> None:
        async def always_allow(context: Dict[str, Any], config: Dict[str, Any]) -> bool:
            return True

        async def threshold_check(context: Dict[str, Any], config: Dict[str, Any]) -> bool:
            key = config.get("key")
            threshold = config.get("threshold")
            if key is None or threshold is None:
                logger.warning("Policy threshold_check ohne vollständige Konfiguration aufgerufen")
                return False
            value = context.get(key)
            try:
                return value is not None and float(value) <= float(threshold)
            except (TypeError, ValueError):
                logger.exception("Policy threshold_check konnte Wert nicht konvertieren")
                return False

        async def emit_event(context: Dict[str, Any], config: Dict[str, Any]) -> None:
            logger.info("PolicyEngine emit_event Hook: %s", config)

        self.register_policy("always_allow", always_allow)
        self.register_policy("threshold_check", threshold_check)
        self.register_action("emit_event", emit_event)

    def register_policy(self, name: str, policy: PolicyCallable) -> None:
        self._policies[name] = policy

    def register_action(self, name: str, action: ActionCallable) -> None:
        self._actions[name] = action

    async def evaluate(self, name: str, context: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> bool:
        if name not in self._policies:
            logger.warning("Unbekannte Policy %s", name)
            return False
        policy = self._policies[name]
        result = policy(context, config or {})
        if asyncio.iscoroutine(result):
            return bool(await result)
        return bool(result)

    async def execute(self, name: str, context: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> None:
        if name not in self._actions:
            logger.warning("Unbekannte Aktion %s", name)
            return
        action = self._actions[name]
        result = action(context, config or {})
        if asyncio.iscoroutine(result):
            await result


