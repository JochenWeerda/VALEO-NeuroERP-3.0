"""
Scheduler Service
Manages scheduled tasks for VALEO NeuroERP
"""

import logging
import asyncio
from datetime import datetime, time
from typing import Dict, List, Any, Callable, Optional
import schedule
import threading
import time as time_module

from ..workers.daily_report_worker import execute_daily_reports

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.jobs: Dict[str, schedule.Job] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the scheduler service"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting scheduler service...")

        # Register scheduled jobs
        self._register_jobs()

        # Start scheduler in background thread
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

        logger.info("Scheduler service started successfully")

    def stop(self):
        """Stop the scheduler service"""
        if not self.running:
            return

        logger.info("Stopping scheduler service...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=5)

        logger.info("Scheduler service stopped")

    def _register_jobs(self):
        """Register all scheduled jobs"""

        # Daily reports - every day at 20:00 (8 PM)
        schedule.every().day.at("20:00").do(self._execute_daily_reports_job).tag('daily-reports')

        # Weekly reports - every Monday at 08:00
        schedule.every().monday.at("08:00").do(self._execute_weekly_reports_job).tag('weekly-reports')

        # Monthly reports - first day of month at 09:00
        schedule.every().month.at("09:00").do(self._execute_monthly_reports_job).tag('monthly-reports')

        # Data cleanup - every Sunday at 02:00
        schedule.every().sunday.at("02:00").do(self._execute_cleanup_job).tag('cleanup')

        # Price monitoring - every 4 hours
        schedule.every(4).hours.do(self._execute_price_monitoring_job).tag('price-monitoring')

        # Compliance checks - every day at 06:00
        schedule.every().day.at("06:00").do(self._execute_compliance_checks_job).tag('compliance')

        logger.info("Registered scheduled jobs")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time_module.sleep(60)  # Wait before retrying

    def _execute_daily_reports_job(self):
        """Execute daily reports job"""
        try:
            logger.info("Executing daily reports job...")
            result = execute_daily_reports()

            if result.get('success'):
                logger.info(f"Daily reports completed: {result}")
            else:
                logger.error(f"Daily reports failed: {result}")

        except Exception as e:
            logger.error(f"Error executing daily reports: {e}")

    def _execute_weekly_reports_job(self):
        """Execute weekly reports job"""
        try:
            logger.info("Executing weekly reports job...")
            # TODO: Implement weekly report generation
            logger.info("Weekly reports job completed (placeholder)")

        except Exception as e:
            logger.error(f"Error executing weekly reports: {e}")

    def _execute_monthly_reports_job(self):
        """Execute monthly reports job"""
        try:
            logger.info("Executing monthly reports job...")
            # TODO: Implement monthly report generation
            logger.info("Monthly reports job completed (placeholder)")

        except Exception as e:
            logger.error(f"Error executing monthly reports: {e}")

    def _execute_cleanup_job(self):
        """Execute data cleanup job"""
        try:
            logger.info("Executing cleanup job...")
            # TODO: Implement data cleanup (old logs, temp files, etc.)
            logger.info("Cleanup job completed (placeholder)")

        except Exception as e:
            logger.error(f"Error executing cleanup job: {e}")

    def _execute_price_monitoring_job(self):
        """Execute price monitoring job"""
        try:
            logger.info("Executing price monitoring job...")
            # TODO: Implement price monitoring
            logger.info("Price monitoring job completed (placeholder)")

        except Exception as e:
            logger.error(f"Error executing price monitoring: {e}")

    def _execute_compliance_checks_job(self):
        """Execute compliance checks job"""
        try:
            logger.info("Executing compliance checks job...")
            # TODO: Implement compliance checks (certificates, licenses, etc.)
            logger.info("Compliance checks job completed (placeholder)")

        except Exception as e:
            logger.error(f"Error executing compliance checks: {e}")

    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs"""
        jobs_status = {}

        for job in schedule.jobs:
            job_info = {
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'last_run': job.last_run.isoformat() if job.last_run else None,
                'tags': list(job.tags),
                'enabled': True
            }
            jobs_status[str(job)] = job_info

        return {
            'running': self.running,
            'jobs': jobs_status,
            'total_jobs': len(schedule.jobs)
        }

    def execute_job_now(self, job_tag: str) -> Dict[str, Any]:
        """Execute a specific job immediately"""
        try:
            jobs = schedule.jobs

            for job in jobs:
                if job_tag in job.tags:
                    logger.info(f"Executing job {job_tag} immediately...")
                    job.run()
                    return {
                        'success': True,
                        'job_tag': job_tag,
                        'executed_at': datetime.now().isoformat()
                    }

            return {
                'success': False,
                'error': f'Job with tag "{job_tag}" not found'
            }

        except Exception as e:
            logger.error(f"Error executing job {job_tag}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global scheduler instance
scheduler = SchedulerService()


def start_scheduler():
    """Start the global scheduler"""
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler.stop()


def get_scheduler_status():
    """Get scheduler status"""
    return scheduler.get_job_status()


def execute_job_immediately(job_tag: str):
    """Execute a job immediately"""
    return scheduler.execute_job_now(job_tag)


# For testing
if __name__ == "__main__":
    # Start scheduler
    start_scheduler()

    try:
        # Keep running for testing
        while True:
            time_module.sleep(60)
            status = get_scheduler_status()
            print(f"Scheduler status: {status}")

    except KeyboardInterrupt:
        print("Stopping scheduler...")
        stop_scheduler()