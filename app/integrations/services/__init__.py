"""Integration service exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "IntegrationCircuitBreaker",
    "SuperglueCapabilityService",
    "SuperglueExecutionService",
]


def __getattr__(name: str) -> Any:
    if name == "IntegrationCircuitBreaker":
        return getattr(import_module("app.integrations.services.integration_circuit_breaker"), name)
    if name == "SuperglueCapabilityService":
        return getattr(import_module("app.integrations.services.superglue_capability_service"), name)
    if name == "SuperglueExecutionService":
        return getattr(import_module("app.integrations.services.superglue_execution_service"), name)
    raise AttributeError(name)
