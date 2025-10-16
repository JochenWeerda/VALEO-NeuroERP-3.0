"""
Advanced Sync Scheduler Service
Handles scheduled synchronization with timers, article group separation, and monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SyncSchedule:
    """Sync schedule configuration"""
    name: str
    interval_hours: int
    enabled: bool
    article_groups: List[str]
    max_items: int
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_status: str = "idle"


@dataclass
class SyncJob:
    """Individual sync job"""
    schedule_name: str
    article_group: str
    start_time: datetime
    status: str = "running"
    processed_items: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SyncScheduler:
    """Advanced scheduler for PSM and article data synchronization"""

    def __init__(self):
        self.schedules: Dict[str, SyncSchedule] = {}
        self.active_jobs: Dict[str, SyncJob] = {}
        self.config_file = Path("config/sync_schedules.json")
        self.load_schedules()

    def load_schedules(self):
        """Load sync schedules from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for name, config in data.items():
                        schedule = SyncSchedule(
                            name=name,
                            interval_hours=config.get('interval_hours', 24),
                            enabled=config.get('enabled', True),
                            article_groups=config.get('article_groups', ['PSM']),
                            max_items=config.get('max_items', 1000)
                        )
                        # Calculate next run time
                        if schedule.enabled:
                            schedule.next_run = self._calculate_next_run(schedule)
                        self.schedules[name] = schedule
                logger.info(f"Loaded {len(self.schedules)} sync schedules")
            except Exception as e:
                logger.error(f"Failed to load sync schedules: {e}")

        # Create default schedules if none exist
        if not self.schedules:
            self._create_default_schedules()

    def _create_default_schedules(self):
        """Create default sync schedules"""
        default_schedules = {
            "psm_weekly": {
                "interval_hours": 168,  # Weekly
                "enabled": True,
                "article_groups": ["PSM"],
                "max_items": 1000
            },
            "psm_monthly": {
                "interval_hours": 720,  # Monthly
                "enabled": True,
                "article_groups": ["PSM"],
                "max_items": 2000
            },
            "articles_weekend": {
                "interval_hours": 168,  # Weekly on weekends
                "enabled": True,
                "article_groups": ["DUENGER", "SAATGUT", "BIOSTIMULANZ"],
                "max_items": 5000
            },
            "prices_nightly": {
                "interval_hours": 24,  # Daily
                "enabled": True,
                "article_groups": ["PRICES", "COMPETITOR_PRICES"],
                "max_items": 10000
            }
        }

        for name, config in default_schedules.items():
            schedule = SyncSchedule(
                name=name,
                interval_hours=config['interval_hours'],
                enabled=config['enabled'],
                article_groups=config['article_groups'],
                max_items=config['max_items']
            )
            schedule.next_run = self._calculate_next_run(schedule)
            self.schedules[name] = schedule

        self.save_schedules()
        logger.info("Created default sync schedules")

    def _calculate_next_run(self, schedule: SyncSchedule) -> datetime:
        """Calculate next run time based on schedule configuration"""
        now = datetime.now()

        if schedule.name == "articles_weekend":
            # Schedule for next Saturday 2:00 AM
            days_until_saturday = (5 - now.weekday()) % 7
            if days_until_saturday == 0 and now.time() >= time(2, 0):
                days_until_saturday = 7
            next_run = now + timedelta(days=days_until_saturday)
            return next_run.replace(hour=2, minute=0, second=0, microsecond=0)

        elif schedule.name == "prices_nightly":
            # Schedule for next day 1:00 AM
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=1, minute=0, second=0, microsecond=0)

        else:
            # Regular interval-based scheduling
            return now + timedelta(hours=schedule.interval_hours)

    def save_schedules(self):
        """Save sync schedules to configuration file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            for name, schedule in self.schedules.items():
                data[name] = {
                    'interval_hours': schedule.interval_hours,
                    'enabled': schedule.enabled,
                    'article_groups': schedule.article_groups,
                    'max_items': schedule.max_items,
                    'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                    'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                    'last_status': schedule.last_status
                }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved {len(self.schedules)} sync schedules")
        except Exception as e:
            logger.error(f"Failed to save sync schedules: {e}")

    def add_schedule(self, name: str, interval_hours: int, article_groups: List[str],
                    max_items: int = 1000, enabled: bool = True) -> SyncSchedule:
        """Add a new sync schedule"""
        schedule = SyncSchedule(
            name=name,
            interval_hours=interval_hours,
            enabled=enabled,
            article_groups=article_groups,
            max_items=max_items
        )

        if enabled:
            schedule.next_run = self._calculate_next_run(schedule)

        self.schedules[name] = schedule
        self.save_schedules()
        logger.info(f"Added sync schedule: {name}")
        return schedule

    def update_schedule(self, name: str, **updates):
        """Update an existing sync schedule"""
        if name not in self.schedules:
            raise ValueError(f"Schedule {name} not found")

        schedule = self.schedules[name]

        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)

        if schedule.enabled and not schedule.next_run:
            schedule.next_run = self._calculate_next_run(schedule)

        self.save_schedules()
        logger.info(f"Updated sync schedule: {name}")

    def start_sync_job(self, schedule_name: str, article_group: str) -> str:
        """Start a sync job"""
        job_id = f"{schedule_name}_{article_group}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        job = SyncJob(
            schedule_name=schedule_name,
            article_group=article_group,
            start_time=datetime.now()
        )

        self.active_jobs[job_id] = job
        logger.info(f"Started sync job: {job_id}")
        return job_id

    def update_job_status(self, job_id: str, status: str, processed_items: int = 0, error: str = None):
        """Update job status"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = status
            job.processed_items = processed_items

            if error:
                job.errors.append(error)

            if status in ['completed', 'failed']:
                # Update schedule last run
                if job.schedule_name in self.schedules:
                    schedule = self.schedules[job.schedule_name]
                    schedule.last_run = job.start_time
                    schedule.last_status = status
                    if status == 'completed':
                        schedule.next_run = self._calculate_next_run(schedule)
                    self.save_schedules()

                # Remove completed job
                del self.active_jobs[job_id]

            logger.info(f"Updated job {job_id}: {status} ({processed_items} items)")

    def get_due_schedules(self) -> List[SyncSchedule]:
        """Get schedules that are due for execution"""
        now = datetime.now()
        due_schedules = []

        for schedule in self.schedules.values():
            if (schedule.enabled and schedule.next_run and
                schedule.next_run <= now):
                due_schedules.append(schedule)

        return due_schedules

    def get_schedule_status(self) -> Dict:
        """Get comprehensive status of all schedules and jobs"""
        return {
            'schedules': {
                name: {
                    'enabled': schedule.enabled,
                    'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                    'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                    'last_status': schedule.last_status,
                    'article_groups': schedule.article_groups,
                    'interval_hours': schedule.interval_hours
                }
                for name, schedule in self.schedules.items()
            },
            'active_jobs': {
                job_id: {
                    'schedule_name': job.schedule_name,
                    'article_group': job.article_group,
                    'start_time': job.start_time.isoformat(),
                    'status': job.status,
                    'processed_items': job.processed_items,
                    'errors': job.errors
                }
                for job_id, job in self.active_jobs.items()
            },
            'summary': {
                'total_schedules': len(self.schedules),
                'enabled_schedules': len([s for s in self.schedules.values() if s.enabled]),
                'active_jobs': len(self.active_jobs),
                'due_schedules': len(self.get_due_schedules())
            }
        }


# Global scheduler instance
sync_scheduler = SyncScheduler()