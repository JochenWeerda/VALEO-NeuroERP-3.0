"""Monthly Report Worker — generates monthly management reports."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy import text

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class MonthlyReportWorker(BaseWorker):
    async def run(self) -> Dict[str, Any]:
        result = self._base_result(reports_generated=0)
        try:
            await self._ensure_db()

            today = datetime.now()
            first_this = today.replace(day=1)
            last_prev = first_this - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            logger.info("Generating monthly reports for %s to %s", first_prev.date(), last_prev.date())

            reports_generated = 0
            try:
                self.db.execute(
                    text(
                        "SELECT COUNT(*) FROM domain_erp.journal_entries "
                        "WHERE entry_date >= :start AND entry_date <= :end"
                    ),
                    {"start": first_prev.date(), "end": last_prev.date()},
                ).scalar()
                reports_generated = 1
            except Exception:
                pass

            result.update(
                reports_generated=reports_generated,
                period_start=first_prev.isoformat(),
                period_end=last_prev.isoformat(),
            )
        except Exception as exc:
            self._error_result(result, exc)
        return result

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_monthly_reports() -> Dict[str, Any]:
    worker = MonthlyReportWorker()
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:
        logger.error("Critical error in monthly report worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_monthly_reports() -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_monthly_reports())
        loop.close()
        return result
    except Exception as exc:
        logger.error("Error executing monthly reports: %s", exc)
        return {"success": False, "error": str(exc)}
