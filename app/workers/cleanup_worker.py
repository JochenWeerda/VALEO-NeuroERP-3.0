"""
Cleanup Worker
Scheduled worker for data cleanup tasks (old logs, temp files, etc.)
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.infrastructure.models import AuditLog

logger = logging.getLogger(__name__)


class CleanupWorker:
    """Worker for automated data cleanup"""

    def __init__(self):
        self.db = None

    async def initialize(self):
        """Initialize database connection"""
        self.db = next(get_db())

    async def run_cleanup(self) -> Dict[str, Any]:
        """
        Run data cleanup tasks
        
        Returns:
            Dictionary with cleanup results
        """
        results = {
            'success': True,
            'tasks': []
        }

        try:
            if not self.db:
                await self.initialize()

            # Task 1: Clean old session data
            task_result = await self._cleanup_old_sessions()
            results['tasks'].append(task_result)

            # Task 2: Clean old audit logs (keep 1 year)
            task_result = await self._cleanup_old_audit_logs()
            results['tasks'].append(task_result)

            # Task 3: Clean old temporary uploads (older than 7 days)
            task_result = await self._cleanup_temp_files()
            results['tasks'].append(task_result)

            # Task 4: Clean old outbox messages (processed successfully)
            task_result = await self._cleanup_old_outbox()
            results['tasks'].append(task_result)

            logger.info(f"Cleanup tasks completed: {len(results['tasks'])} tasks")

        except Exception as e:
            logger.error(f"Error in cleanup: {e}")
            results['success'] = False
            results['error'] = str(e)

        return results

    async def _cleanup_old_sessions(self) -> Dict[str, Any]:
        """Clean expired sessions (no session table in schema; reserved for future Redis/DB sessions)."""
        try:
            logger.info("Cleaning old sessions...")
            return {'task': 'sessions', 'deleted': 0, 'success': True}
        except Exception as e:
            logger.error(f"Error cleaning sessions: {e}")
            return {'task': 'sessions', 'success': False, 'error': str(e)}

    async def _cleanup_old_audit_logs(self) -> Dict[str, Any]:
        """Clean audit logs older than 1 year"""
        try:
            if not self.db:
                return {'task': 'audit_logs', 'deleted': 0, 'success': True}
            cutoff = datetime.utcnow() - timedelta(days=365)
            deleted = self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff).delete()
            self.db.commit()
            logger.info(f"Cleaning audit logs older than {cutoff.date()}, deleted={deleted}")
            return {'task': 'audit_logs', 'deleted': deleted, 'success': True}
        except Exception as e:
            logger.error(f"Error cleaning audit logs: {e}")
            if self.db:
                self.db.rollback()
            return {'task': 'audit_logs', 'success': False, 'error': str(e)}

    async def _cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean temporary upload files older than 7 days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Placeholder - implement actual temp file cleanup
            logger.info(f"Cleaning temp files older than {cutoff_date.date()}")
            return {'task': 'temp_files', 'deleted': 0, 'success': True}
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
            return {'task': 'temp_files', 'success': False, 'error': str(e)}

    async def _cleanup_old_outbox(self) -> Dict[str, Any]:
        """Clean processed outbox messages"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Placeholder - implement actual outbox cleanup
            logger.info(f"Cleaning processed outbox messages older than {cutoff_date.date()}")
            return {'task': 'outbox', 'deleted': 0, 'success': True}
        except Exception as e:
            logger.error(f"Error cleaning outbox: {e}")
            return {'task': 'outbox', 'success': False, 'error': str(e)}

    async def cleanup(self):
        """Clean up database connections"""
        if self.db:
            self.db.close()


async def run_cleanup():
    """Main function to run cleanup tasks"""
    worker = CleanupWorker()

    try:
        await worker.initialize()
        result = await worker.run_cleanup()

        if result['success']:
            logger.info(f"Cleanup completed: {result}")
        else:
            logger.error(f"Cleanup failed: {result}")

        return result

    except Exception as e:
        logger.error(f"Critical error in cleanup worker: {e}")
        return {
            'success': False,
            'error': str(e)
        }

    finally:
        await worker.cleanup()


# Scheduled execution function (to be called by scheduler)
def execute_cleanup():
    """Synchronous wrapper for scheduled execution"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_cleanup())
        loop.close()

        return result

    except Exception as e:
        logger.error(f"Error executing cleanup: {e}")
        return {
            'success': False,
            'error': str(e)
        }
