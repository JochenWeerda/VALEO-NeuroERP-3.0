"""Daily Report Worker — generates and sends daily CRM reports."""

import asyncio
import logging
from typing import Any, Dict

from .base_worker import BaseWorker
from ..domains.crm.services.daily_report_service import DailyReportService

logger = logging.getLogger(__name__)


class DailyReportWorker(BaseWorker):
    def __init__(self) -> None:
        super().__init__()
        self.service: DailyReportService | None = None

    async def initialize(self) -> None:
        await super().initialize()
        self.service = DailyReportService(self.db)

    async def run(self) -> Dict[str, Any]:
        result = self._base_result(reports_generated=0)
        try:
            if not self.service:
                await self.initialize()

            reports = self.service.generate_daily_reports()
            if reports:
                send_results = self.service.send_daily_reports(reports)
                sent = len([r for r in send_results.values() if r.get("success")])
                logger.info("Generated and sent %d daily reports", len(reports))
                result.update(
                    reports_generated=len(reports),
                    reports_sent=sent,
                    details=send_results,
                )
            else:
                logger.info("No daily reports to generate")
                result["message"] = "No activities or visits found for report generation"
        except Exception as exc:
            self._error_result(result, exc)
        return result

    async def cleanup(self) -> None:
        if self.db:
            self.db.close()


async def run_daily_reports() -> Dict[str, Any]:
    worker = DailyReportWorker()
    try:
        await worker.initialize()
        return await worker.run()
    except Exception as exc:
        logger.error("Critical error in daily report worker: %s", exc)
        return {"success": False, "error": str(exc)}
    finally:
        await worker.cleanup()


def execute_daily_reports() -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_daily_reports())
        loop.close()
        return result
    except Exception as exc:
        logger.error("Error executing daily reports: %s", exc)
        return {"success": False, "error": str(exc)}


if __name__ == "__main__":
    print(execute_daily_reports())
