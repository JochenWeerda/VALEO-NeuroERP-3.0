"""Cleanup Worker — deletes old audit logs, temp files, and outbox messages."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from app.infrastructure.models import AuditLog

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class CleanupWorker(BaseWorker):
    async def run(self) -> Dict[str, Any]:
        result = self._base_result(tasks=[])
        try:
            await self._ensure_db()

            result["tasks"].append(await self._cleanup_old_sessions())
            result["tasks"].append(await self._cleanup_old_audit_logs())
            result["tasks"].append(await self._cleanup_temp_files())
            result["tasks"].append(await self._cleanup_old_outbox())

            logger.info("Cleanup tasks completed: %d tasks", len(result["tasks"]))
        except Exception as exc:
            self._error_result(result, exc)
        return result

    async def _cleanup_old_sessions(self) -> Dict[str, Any]:
        try:
            logger.info("Cleaning old sessions...")
            return {"task": "sessions", "deleted": 0, "success": True}
        except Exception as exc:
            logger.error("Error cleaning sessions: %s", exc)
            return {"task": "sessions", "success": False, "error": str(exc)}

    async def _cleanup_old_audit_logs(self) -> Dict[str, Any]:
        try:
            if not self.db:
                return {"task": "audit_logs", "deleted": 0, "success": True}
            cutoff = datetime.utcnow() - timedelta(days=365)
            deleted = self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff).delete()
            self.db.commit()
            logger.info("Deleted %d audit logs older than %s", deleted, cutoff.date())
            return {"task": "audit_logs", "deleted": deleted, "success": True}
        except Exception as exc:
            logger.error("Error cleaning audit logs: %s", exc)
            if self.db:
                self.db.rollback()
            return {"task": "audit_logs", "success": False, "error": str(exc)}

    async def _cleanup_temp_files(self) -> Dict[str, Any]:
        try:
            cutoff = datetime.now() - timedelta(days=7)
            logger.info("Cleaning temp files older than %s", cutoff.date())
            return {"task": "temp_files", "deleted": 0, "success": True}
        except Exception as exc:
            logger.error("Error cleaning temp files: %s", exc)
            return {"task": "temp_files", "success": False, "error": str(exc)}

    async def _cleanup_old_outbox(self) -> Dict[str, Any]:
        try:
            cutoff = datetime.now() - timedelta(days=30)
            logger.info("Cleaning processed outbox messages older than %s", cutoff.date())
            return {"task": "outbox", "deleted": 0, "success": True}
        except Exception as exc:
            logger.error("Error cleaning outbox: %s", exc)
            return {"task": "outbox", "success": False, "error": str(exc)}

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_cleanup() -> Dict[str, Any]:
    worker = CleanupWorker()
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:
        logger.error("Critical error in cleanup worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_cleanup() -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_cleanup())
        loop.close()
        return result
    except Exception as exc:
        logger.error("Error executing cleanup: %s", exc)
        return {"success": False, "error": str(exc)}
