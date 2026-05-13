"""Abstract base class for all background workers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from app.core.database import get_db

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Common scaffolding for all async background workers."""

    def __init__(self) -> None:
        self.db = None

    async def initialize(self) -> None:
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
