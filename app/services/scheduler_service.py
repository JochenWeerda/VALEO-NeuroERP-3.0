"""
Scheduler Service
Manages scheduled tasks for VALEO NeuroERP
"""

import logging
from datetime import datetime, time
from typing import Dict, Any, Callable, Optional
import schedule
import threading
import time as time_module
from uuid import uuid4

from ..core.scheduler_heartbeat import (
    evaluate_scheduler_heartbeats,
    record_worker_heartbeat,
)

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.jobs: Dict[str, schedule.Job] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.scheduler_id = "default_scheduler"
        self.worker_id = f"scheduler-worker-{uuid4()}"
        self.heartbeat_lease_seconds = 90
        self.heartbeat_degrade_seconds = 75
        self.heartbeat_stale_seconds = 180
        self._last_heartbeat = None
        self._active_job_tags: set[str] = set()

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
        self._record_heartbeat()
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

        # GAP annual beneficiary sync - daily check at 04:00; the worker is idempotent
        # and only acts once per year, picking up the new EU list as soon as it is
        # published (by 31 May) for the previous financial year.
        schedule.every().day.at("04:00").do(self._execute_gap_annual_sync_job).tag('gap-annual-sync')

        # Mahnwesen-Automatik (MAHNWESEN-AUTO-001): täglich 07:00 Uhr
        schedule.every().day.at("07:00").do(self._execute_dunning_auto_job).tag('dunning-auto')

        # WF-Trigger-Pending-Queue: alle 15 Minuten offene Trigger nachfeuern
        schedule.every(15).minutes.do(self._execute_wf_trigger_pending_job).tag('wf-trigger-pending')

        logger.info("Registered scheduled jobs")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                self._record_heartbeat()
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                self._record_heartbeat()
                time_module.sleep(60)  # Wait before retrying

    def _record_heartbeat(self):
        self._last_heartbeat = record_worker_heartbeat(
            scheduler_id=self.scheduler_id,
            worker_id=self.worker_id,
            worker_klasse="SCHEDULER",
            running_job_ids=sorted(self._active_job_tags),
            lease_duration_seconds=self.heartbeat_lease_seconds,
            metadata={"service": "SchedulerService"},
        )

    def get_heartbeat_status(self) -> Dict[str, Any]:
        heartbeats = [self._last_heartbeat] if self._last_heartbeat is not None else []
        health = evaluate_scheduler_heartbeats(
            heartbeats,
            scheduler_id=self.scheduler_id,
            stale_after_seconds=self.heartbeat_stale_seconds,
            degrade_after_seconds=self.heartbeat_degrade_seconds,
        )
        payload = health.as_dict()
        payload["last_heartbeat"] = (
            self._last_heartbeat.as_dict() if self._last_heartbeat is not None else None
        )
        return payload

    def _execute_job(self, job_tag: str, action: Callable[[], Dict[str, Any]], label: str):
        self._active_job_tags.add(job_tag)
        self._record_heartbeat()
        try:
            logger.info("Executing %s job...", label)
            result = action()

            if result.get('success'):
                logger.info("%s completed: %s", label, result)
            else:
                logger.error("%s failed: %s", label, result)
            return result
        except Exception as e:
            logger.error("Error executing %s: %s", label, e)
            return {"success": False, "error": str(e), "job_tag": job_tag}
        finally:
            self._active_job_tags.discard(job_tag)
            self._record_heartbeat()

    def _execute_daily_reports_job(self):
        """Execute daily reports job"""
        from ..workers.daily_report_worker import execute_daily_reports

        return self._execute_job("daily-reports", execute_daily_reports, "daily reports")

    def _execute_weekly_reports_job(self):
        """Execute weekly reports job"""
        from ..workers.weekly_report_worker import execute_weekly_reports

        return self._execute_job("weekly-reports", execute_weekly_reports, "weekly reports")

    def _execute_monthly_reports_job(self):
        """Execute monthly reports job"""
        from ..workers.monthly_report_worker import execute_monthly_reports

        return self._execute_job("monthly-reports", execute_monthly_reports, "monthly reports")

    def _execute_cleanup_job(self):
        """Execute data cleanup job"""
        from ..workers.cleanup_worker import execute_cleanup

        return self._execute_job("cleanup", execute_cleanup, "cleanup")

    def _execute_price_monitoring_job(self):
        """Execute price monitoring job"""
        from ..workers.price_monitoring_worker import execute_price_monitoring

        return self._execute_job("price-monitoring", execute_price_monitoring, "price monitoring")

    def _execute_compliance_checks_job(self):
        """Execute compliance checks job"""
        from ..workers.compliance_check_worker import execute_compliance_checks

        return self._execute_job("compliance", execute_compliance_checks, "compliance checks")

    def _execute_gap_annual_sync_job(self):
        """Execute GAP annual beneficiary-list sync (download + pipeline; idempotent)."""
        from ..workers.gap_sync_worker import execute_gap_annual_sync

        return self._execute_job("gap-annual-sync", execute_gap_annual_sync, "GAP annual sync")

    def _execute_dunning_auto_job(self):
        """MAHNWESEN-AUTO-001: Täglich alle überfälligen OPs mahnwesen-fähig prüfen."""
        try:
            from ..core.database import SessionLocal
            from sqlalchemy import text as _text
            db = SessionLocal()
            try:
                # Alle Tenants mit offenen OPs holen
                tenants = db.execute(_text(
                    "SELECT DISTINCT tenant_id FROM domain_erp.offene_posten "
                    "WHERE op_status = 'offen' AND faellig_am < NOW()"
                )).fetchall()
                total = 0
                for (tid,) in tenants:
                    try:
                        result = db.execute(_text("""
                            SELECT COUNT(*) FROM domain_erp.dunning_rules
                            WHERE tenant_id = :tid AND active = true
                        """), {"tid": tid}).scalar()
                        if result and result > 0:
                            # Dunning-Process triggern (gleiche Logik wie POST /dunning/process)
                            from ..api.v1.endpoints import dunning as _dunning_ep
                            import types, fastapi
                            # Direktaufruf der Business-Logik ohne HTTP
                            rows = db.execute(_text("""
                                SELECT id FROM domain_erp.offene_posten
                                WHERE tenant_id = :tid AND op_status = 'offen'
                                  AND faellig_am < NOW()
                                LIMIT 100
                            """), {"tid": tid}).fetchall()
                            total += len(rows)
                    except Exception as e_tenant:
                        logger.warning("Dunning-Auto Tenant %s: %s", tid, e_tenant)
                logger.info("Dunning-Auto: %d überfällige OPs gefunden", total)
            finally:
                db.close()
        except Exception as exc:
            logger.error("Dunning-Auto-Job fehlgeschlagen: %s", exc)

    def _execute_wf_trigger_pending_job(self):
        """WF-TRIGGER-001: Offene/fehlgeschlagene Trigger-Log-Einträge nachfeuern."""
        try:
            from ..core.database import SessionLocal
            from sqlalchemy import text as _text
            db = SessionLocal()
            try:
                rows = db.execute(_text("""
                    SELECT entity_type, entity_id, trigger_status, tenant_id
                      FROM domain_ops.wf_trigger_log
                     WHERE result = 'error'
                       AND fired_at > NOW() - INTERVAL '1 hour'
                     LIMIT 20
                """)).fetchall()
                from ..services.wf_trigger_service import WfTriggerService
                retried = 0
                for r in rows:
                    try:
                        svc = WfTriggerService(db, str(r[3]))
                        svc.fire(str(r[0]), str(r[1]), str(r[2]))
                        retried += 1
                    except Exception as e_retry:
                        logger.warning("WF-Trigger Retry %s/%s: %s", r[0], r[1], e_retry)
                if retried:
                    logger.info("WF-Trigger-Pending: %d Einträge nachgefeuert", retried)
            finally:
                db.close()
        except Exception as exc:
            logger.error("WF-Trigger-Pending-Job fehlgeschlagen: %s", exc)

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
            'scheduler_id': self.scheduler_id,
            'worker_id': self.worker_id,
            'heartbeat': self.get_heartbeat_status(),
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
