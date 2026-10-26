"""Abstract base class for all background workers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, TypeVar

from app.core.database import get_db
from app.core.tenant_context import (
    TenantContextMissing,
    cross_tenant_reason,
    cross_tenant_scope,
    current_tenant_or_none,
)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def cross_tenant_job(reason: str) -> Callable[[F], F]:
    """Run a maintenance or aggregate job deliberately across tenants (RLS plan P1)."""
    def decorate(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with cross_tenant_scope(reason):
                return func(*args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorate


class BaseWorker(ABC):
    """Common scaffolding for all async background workers."""

    def __init__(self) -> None:
        self.db = None

    async def initialize(self) -> None:
        if current_tenant_or_none() is None and cross_tenant_reason() is None:
            raise TenantContextMissing(
                f"{type(self).__name__} ohne tenant_scope/cross_tenant_scope gestartet"
            )
        self.db = next(get_db())

    async def _ensure_db(self) -> None:
        if not self.db:
            await self.initialize()

    def _base_result(self, **extra) -> Dict[str, Any]:
        return {"success": True, **extra}

    def _error_result(self, base: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
        logger.error("%s failed: %s", self.__class__.__name__, exc)
        base["success"] = False
        base["error"] = str(exc)
        return base

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Execute the worker's main task and return a result dict."""
