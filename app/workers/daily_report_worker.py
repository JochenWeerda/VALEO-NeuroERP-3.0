"""
Daily Report Worker
Scheduled worker for generating and sending daily CRM reports
"""

import logging
import asyncio
from datetime import datetime, time
from typing import Dict, Any

from ..core.config import settings
from ..core.database import get_db
from ..domains.crm.services.daily_report_service import DailyReportService

logger = logging.getLogger(__name__)


class DailyReportWorker:
    """Worker for automated daily report generation"""

    def __init__(self):
        self.service = None
        self.db = None

    async def initialize(self):
        """Initialize database connection"""
        self.db = next(get_db())
        self.service = DailyReportService(self.db)

    async def generate_daily_reports(self) -> Dict[str, Any]:
        """
        Generate daily reports for all sales reps

        Returns:
            Dictionary with generation results
        """
        try:
            if not self.service:
                await self.initialize()

            # Generate reports for yesterday
            reports = self.service.generate_daily_reports()

            if reports:
                # Send reports
                send_results = self.service.send_daily_reports(reports)

                logger.info(f"Generated and sent {len(reports)} daily reports")

                return {
                    'success': True,
                    'reports_generated': len(reports),
                    'reports_sent': len([r for r in send_results.values() if r.get('success')]),
                    'details': send_results
                }
            else:
                logger.info("No daily reports to generate")
                return {
                    'success': True,
                    'reports_generated': 0,
                    'message': 'No activities or visits found for report generation'
                }

        except Exception as e:
            logger.error(f"Error in daily report generation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def cleanup(self):
        """Clean up database connections"""
        if self.db:
            self.db.close()


async def run_daily_reports():
    """Main function to run daily report generation"""
    worker = DailyReportWorker()

    try:
        await worker.initialize()
        result = await worker.generate_daily_reports()

        # Log results
        if result['success']:
            logger.info(f"Daily reports completed successfully: {result}")
        else:
            logger.error(f"Daily reports failed: {result}")

        return result

    except Exception as e:
        logger.error(f"Critical error in daily report worker: {e}")
        return {
            'success': False,
            'error': str(e)
        }

    finally:
        await worker.cleanup()


# Scheduled execution function (to be called by scheduler)
def execute_daily_reports():
    """Synchronous wrapper for scheduled execution"""
    try:
        # Run in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_daily_reports())
        loop.close()

        return result

    except Exception as e:
        logger.error(f"Error executing daily reports: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # For testing
    result = execute_daily_reports()
    print(f"Daily report execution result: {result}")