"""
ISO 27001 Operations Security Management
Information Security Operations Framework

Dieses Modul implementiert das Operations Security Management Framework
gemäß ISO 27001 Annex A.12 für VALEO-NeuroERP mit Secure Operations, Change Management und Capacity Management.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes"""
    EMERGENCY = "emergency"
    STANDARD = "standard"
    MINOR = "minor"
    MAJOR = "major"


class ChangeStatus(Enum):
    """Change request status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ChangePriority(Enum):
    """Change priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChangeRisk(Enum):
    """Change risk assessment"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class BackupType(Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup status"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class CapacityMetric(Enum):
    """Capacity management metrics"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    STORAGE_UTILIZATION = "storage_utilization"
    NETWORK_UTILIZATION = "network_utilization"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"


class MonitoringThreshold(Enum):
    """Monitoring threshold levels"""
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "info"


@dataclass
class ChangeRequest:
    """Change request record"""
    id: str
    title: str
    description: str
    change_type: ChangeType
    priority: ChangePriority
    risk_assessment: ChangeRisk
    affected_systems: List[str]
    planned_start: datetime
    planned_end: datetime
    requested_by: str
    approver: str
    status: ChangeStatus = ChangeStatus.DRAFT
    rollback_plan: str = ""
    test_plan: str = ""
    communication_plan: str = ""
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    implementation_notes: str = ""
    post_implementation_review: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChangeApproval:
    """Change approval record"""
    id: str
    change_request_id: str
    approver: str
    approval_level: str  # technical, business, security
    decision: str  # approved, rejected, conditional
    comments: str = ""
    approved_at: datetime = field(default_factory=datetime.utcnow)
    conditions: List[str] = field(default_factory=list)


@dataclass
class BackupJob:
    """Backup job configuration"""
    id: str
    name: str
    backup_type: BackupType
    source_systems: List[str]
    destination: str
    schedule: str  # cron expression
    retention_days: int
    encryption_enabled: bool = True
    compression_enabled: bool = True
    verification_enabled: bool = True
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BackupExecution:
    """Backup execution record"""
    id: str
    backup_job_id: str
    status: BackupStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    data_size_bytes: Optional[int] = None
    compression_ratio: Optional[float] = None
    verification_status: Optional[str] = None
    error_message: str = ""
    executed_by: str = "system"


@dataclass
class CapacityBaseline:
    """Capacity baseline metrics"""
    id: str
    system_id: str
    metric: CapacityMetric
    baseline_value: float
    unit: str
    measurement_period: str  # daily, weekly, monthly
    tolerance_percent: float = 10.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    trend: str = "stable"  # increasing, decreasing, stable


@dataclass
class CapacityAlert:
    """Capacity alert"""
    id: str
    system_id: str
    metric: CapacityMetric
    current_value: float
    threshold_value: float
    threshold_type: MonitoringThreshold
    severity: str
    message: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class OperationsLog:
    """Operations log entry"""
    id: str
    timestamp: datetime
    system_id: str
    event_type: str
    severity: str
    message: str
    operator: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolution_status: str = "open"
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


@dataclass
class MaintenanceWindow:
    """Maintenance window schedule"""
    id: str
    name: str
    description: str
    systems_affected: List[str]
    start_time: datetime
    end_time: datetime
    frequency: str  # daily, weekly, monthly
    approval_required: bool = True
    notification_days: int = 7
    contact_groups: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class OperationsDashboard:
    """Operations dashboard data"""
    id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    system_health: Dict[str, Any] = field(default_factory=dict)
    capacity_metrics: Dict[str, Any] = field(default_factory=dict)
    change_management: Dict[str, Any] = field(default_factory=dict)
    backup_status: Dict[str, Any] = field(default_factory=dict)
    alerts_summary: Dict[str, Any] = field(default_factory=dict)
    maintenance_schedule: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ISO27001OperationsSecurity:
    """
    ISO 27001 Operations Security Management
    Implements Annex A.12 - Operations Security
    """

    def __init__(self, db_session, monitoring_service=None, change_service=None):
        self.db = db_session
        self.monitoring = monitoring_service
        self.change_svc = change_service

        # Operations security components
        self.change_requests: Dict[str, ChangeRequest] = {}
        self.change_approvals: List[ChangeApproval] = {}
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.backup_executions: List[BackupExecution] = {}
        self.capacity_baselines: Dict[str, CapacityBaseline] = {}
        self.capacity_alerts: List[CapacityAlert] = {}
        self.operations_logs: List[OperationsLog] = {}
        self.maintenance_windows: Dict[str, MaintenanceWindow] = {}

        # Operations configuration
        self.operations_config = self._initialize_operations_config()

        # Default maintenance schedules
        self._initialize_default_maintenance()

    def _initialize_operations_config(self) -> Dict[str, Any]:
        """Initialize operations security configuration"""
        return {
            'change_management': {
                'approval_levels': ['technical', 'business', 'security'],
                'emergency_change_window': 4,  # hours
                'standard_change_window': 168,  # hours (1 week)
                'post_implementation_review': 72,  # hours
                'rollback_time_limit': 24  # hours
            },
            'backup_operations': {
                'retention_periods': {
                    'daily': 30, 'weekly': 365, 'monthly': 2555, 'yearly': 2555
                },
                'verification_frequency': 'daily',
                'encryption_standard': 'AES-256',
                'offsite_replication': True
            },
            'capacity_management': {
                'monitoring_interval': 300,  # seconds
                'baseline_calculation_period': 90,  # days
                'forecasting_period': 180,  # days
                'alert_thresholds': {
                    'cpu': {'warning': 70, 'critical': 90},
                    'memory': {'warning': 75, 'critical': 95},
                    'storage': {'warning': 80, 'critical': 95},
                    'response_time': {'warning': 1000, 'critical': 5000}  # milliseconds
                }
            },
            'maintenance_scheduling': {
                'blackout_windows': ['02:00-04:00'],  # UTC
                'notification_period': 7,  # days
                'approval_levels': ['system_owner', 'business_owner']
            }
        }

    def _initialize_default_maintenance(self):
        """Initialize default maintenance windows"""
        default_windows = [
            {
                'name': 'Database Maintenance',
                'description': 'Weekly database optimization and cleanup',
                'systems_affected': ['database', 'reporting'],
                'start_time': datetime.utcnow().replace(hour=2, minute=0, second=0, microsecond=0),
                'end_time': datetime.utcnow().replace(hour=4, minute=0, second=0, microsecond=0),
                'frequency': 'weekly'
            },
            {
                'name': 'Security Updates',
                'description': 'Monthly security patch deployment',
                'systems_affected': ['all_servers', 'network_devices'],
                'start_time': datetime.utcnow().replace(hour=1, minute=0, second=0, microsecond=0),
                'end_time': datetime.utcnow().replace(hour=3, minute=0, second=0, microsecond=0),
                'frequency': 'monthly'
            },
            {
                'name': 'System Health Check',
                'description': 'Daily system health verification',
                'systems_affected': ['monitoring_system'],
                'start_time': datetime.utcnow().replace(hour=3, minute=0, second=0, microsecond=0),
                'end_time': datetime.utcnow().replace(hour=3, minute=30, second=0, microsecond=0),
                'frequency': 'daily'
            }
        ]

        for window_data in default_windows:
            window = MaintenanceWindow(**window_data)
            self.maintenance_windows[window.id] = window

    def create_change_request(self, change_data: Dict[str, Any]) -> str:
        """
        Create a change request
        Returns change request ID
        """
        change_id = str(uuid.uuid4())

        # Assess change risk automatically
        risk_assessment = self._assess_change_risk(change_data)

        change = ChangeRequest(
            id=change_id,
            title=change_data['title'],
            description=change_data['description'],
            change_type=ChangeType[change_data['change_type'].upper()],
            priority=ChangePriority[change_data['priority'].upper()],
            risk_assessment=risk_assessment,
            affected_systems=change_data.get('affected_systems', []),
            planned_start=change_data['planned_start'],
            planned_end=change_data['planned_end'],
            requested_by=change_data['requested_by'],
            approver=change_data.get('approver', ''),
            rollback_plan=change_data.get('rollback_plan', ''),
            test_plan=change_data.get('test_plan', ''),
            communication_plan=change_data.get('communication_plan', '')
        )

        self.change_requests[change_id] = change

        # Log change request creation
        self._log_operations_event(
            system_id='change_management',
            event_type='change_request_created',
            severity='info',
            message=f"Change request created: {change.title}",
            operator=change.requested_by,
            details={'change_id': change_id, 'priority': change.priority.value}
        )

        logger.info(f"Change request created: {change.title} (Risk: {change.risk_assessment.value})")
        return change_id

    def _assess_change_risk(self, change_data: Dict[str, Any]) -> ChangeRisk:
        """Automatically assess change risk"""
        risk_score = 0

        # Risk factors
        if change_data.get('affects_production', False):
            risk_score += 3
        if change_data.get('affects_customers', False):
            risk_score += 2
        if change_data.get('requires_downtime', False):
            risk_score += 2
        if change_data.get('complexity', 'low') == 'high':
            risk_score += 2
        if len(change_data.get('affected_systems', [])) > 3:
            risk_score += 1

        # Map score to risk level
        if risk_score >= 8:
            return ChangeRisk.VERY_HIGH
        elif risk_score >= 6:
            return ChangeRisk.HIGH
        elif risk_score >= 4:
            return ChangeRisk.MEDIUM
        elif risk_score >= 2:
            return ChangeRisk.LOW
        else:
            return ChangeRisk.VERY_LOW

    def approve_change_request(self, change_id: str, approval_data: Dict[str, Any]) -> bool:
        """
        Approve a change request
        """
        if change_id not in self.change_requests:
            return False

        change = self.change_requests[change_id]

        # Create approval record
        approval = ChangeApproval(
            id=str(uuid.uuid4()),
            change_request_id=change_id,
            approver=approval_data['approver'],
            approval_level=approval_data['approval_level'],
            decision=approval_data['decision'],
            comments=approval_data.get('comments', ''),
            conditions=approval_data.get('conditions', [])
        )

        if change_id not in self.change_approvals:
            self.change_approvals[change_id] = []

        self.change_approvals[change_id].append(approval)

        # Update change status if all required approvals are received
        if approval.decision == 'approved':
            change.status = ChangeStatus.APPROVED
        else:
            change.status = ChangeStatus.REJECTED

        logger.info(f"Change request {change_id} {approval.decision} by {approval.approver}")
        return True

    def schedule_change_implementation(self, change_id: str, schedule_data: Dict[str, Any]) -> bool:
        """
        Schedule change implementation
        """
        if change_id not in self.change_requests:
            return False

        change = self.change_requests[change_id]
        change.status = ChangeStatus.SCHEDULED
        change.actual_start = schedule_data.get('actual_start')
        change.actual_end = schedule_data.get('actual_end')

        # Check for maintenance window conflicts
        conflicts = self._check_maintenance_conflicts(change)
        if conflicts:
            logger.warning(f"Change {change_id} conflicts with maintenance windows: {conflicts}")

        logger.info(f"Change {change_id} scheduled for implementation")
        return True

    def _check_maintenance_conflicts(self, change: ChangeRequest) -> List[str]:
        """Check for conflicts with maintenance windows"""
        conflicts = []

        for window in self.maintenance_windows.values():
            if not window.is_active:
                continue

            # Check if change overlaps with maintenance window
            if (change.actual_start and window.start_time <= change.actual_start <= window.end_time) or \
               (change.actual_end and window.start_time <= change.actual_end <= window.end_time):
                conflicts.append(f"Conflicts with {window.name}")

        return conflicts

    def execute_change(self, change_id: str, execution_data: Dict[str, Any]) -> bool:
        """
        Execute a scheduled change
        """
        if change_id not in self.change_requests:
            return False

        change = self.change_requests[change_id]
        change.status = ChangeStatus.IMPLEMENTING
        change.actual_start = datetime.utcnow()
        change.implementation_notes = execution_data.get('notes', '')

        # Log execution start
        self._log_operations_event(
            system_id='change_management',
            event_type='change_execution_started',
            severity='info',
            message=f"Change execution started: {change.title}",
            operator=execution_data.get('executed_by', 'system'),
            details={'change_id': change_id}
        )

        logger.info(f"Change {change_id} execution started")
        return True

    def complete_change(self, change_id: str, completion_data: Dict[str, Any]) -> bool:
        """
        Complete change implementation
        """
        if change_id not in self.change_requests:
            return False

        change = self.change_requests[change_id]
        change.status = ChangeStatus.DEPLOYED
        change.actual_end = datetime.utcnow()
        change.post_implementation_review = completion_data.get('review', '')

        # Schedule post-implementation review
        review_time = datetime.utcnow() + timedelta(hours=self.operations_config['change_management']['post_implementation_review'])
        self._schedule_post_implementation_review(change_id, review_time)

        # Log completion
        self._log_operations_event(
            system_id='change_management',
            event_type='change_completed',
            severity='info',
            message=f"Change completed: {change.title}",
            operator=completion_data.get('completed_by', 'system'),
            details={'change_id': change_id, 'duration': str(change.actual_end - change.actual_start)}
        )

        logger.info(f"Change {change_id} completed successfully")
        return True

    def _schedule_post_implementation_review(self, change_id: str, review_time: datetime):
        """Schedule post-implementation review"""
        # In production, this would create a scheduled task
        logger.info(f"Post-implementation review scheduled for change {change_id} at {review_time}")

    def create_backup_job(self, backup_data: Dict[str, Any]) -> str:
        """
        Create a backup job
        Returns backup job ID
        """
        job_id = str(uuid.uuid4())

        job = BackupJob(
            id=job_id,
            name=backup_data['name'],
            backup_type=BackupType[backup_data['backup_type'].upper()],
            source_systems=backup_data['source_systems'],
            destination=backup_data['destination'],
            schedule=backup_data['schedule'],
            retention_days=backup_data['retention_days'],
            encryption_enabled=backup_data.get('encryption_enabled', True),
            compression_enabled=backup_data.get('compression_enabled', True),
            verification_enabled=backup_data.get('verification_enabled', True)
        )

        self.backup_jobs[job_id] = job

        logger.info(f"Backup job created: {job.name} ({job.backup_type.value})")
        return job_id

    def execute_backup(self, job_id: str, execution_data: Dict[str, Any]) -> str:
        """
        Execute a backup job
        Returns execution ID
        """
        if job_id not in self.backup_jobs:
            raise ValueError(f"Backup job {job_id} not found")

        execution_id = str(uuid.uuid4())

        execution = BackupExecution(
            id=execution_id,
            backup_job_id=job_id,
            status=BackupStatus.RUNNING,
            start_time=datetime.utcnow(),
            executed_by=execution_data.get('executed_by', 'system')
        )

        self.backup_executions.append(execution)

        # Log backup start
        self._log_operations_event(
            system_id='backup_system',
            event_type='backup_started',
            severity='info',
            message=f"Backup started: {self.backup_jobs[job_id].name}",
            operator=execution.executed_by,
            details={'job_id': job_id, 'execution_id': execution_id}
        )

        logger.info(f"Backup execution started: {execution_id}")
        return execution_id

    def complete_backup(self, execution_id: str, completion_data: Dict[str, Any]) -> bool:
        """
        Complete backup execution
        """
        execution = None
        for exec_record in self.backup_executions:
            if exec_record.id == execution_id:
                execution = exec_record
                break

        if not execution:
            return False

        execution.status = BackupStatus(completion_data.get('status', 'completed'))
        execution.end_time = datetime.utcnow()
        execution.data_size_bytes = completion_data.get('data_size_bytes')
        execution.compression_ratio = completion_data.get('compression_ratio')
        execution.verification_status = completion_data.get('verification_status')
        execution.error_message = completion_data.get('error_message', '')

        # Log completion
        severity = 'error' if execution.status == BackupStatus.FAILED else 'info'
        self._log_operations_event(
            system_id='backup_system',
            event_type='backup_completed',
            severity=severity,
            message=f"Backup completed: {execution.status.value}",
            operator=execution.executed_by,
            details={
                'execution_id': execution_id,
                'status': execution.status.value,
                'duration': str(execution.end_time - execution.start_time)
            }
        )

        logger.info(f"Backup execution {execution_id} completed with status: {execution.status.value}")
        return True

    def monitor_capacity(self, system_id: str, metrics_data: Dict[str, Any]) -> List[str]:
        """
        Monitor system capacity and generate alerts
        Returns list of alert IDs
        """
        alert_ids = []

        for metric_name, metric_value in metrics_data.items():
            try:
                metric = CapacityMetric[metric_name.upper()]
                alert_id = self._check_capacity_threshold(system_id, metric, metric_value)
                if alert_id:
                    alert_ids.append(alert_id)
            except KeyError:
                continue  # Skip unknown metrics

        return alert_ids

    def _check_capacity_threshold(self, system_id: str, metric: CapacityMetric, current_value: float) -> Optional[str]:
        """Check if capacity metric exceeds thresholds"""
        thresholds = self.operations_config['capacity_management']['alert_thresholds']

        metric_key = metric.value.lower()
        if metric_key not in thresholds:
            return None

        threshold_config = thresholds[metric_key]

        # Determine threshold type and severity
        if current_value >= threshold_config['critical']:
            threshold_type = MonitoringThreshold.CRITICAL
            severity = 'critical'
        elif current_value >= threshold_config['warning']:
            threshold_type = MonitoringThreshold.WARNING
            severity = 'warning'
        else:
            return None  # No alert needed

        # Create alert
        alert_id = str(uuid.uuid4())

        alert = CapacityAlert(
            id=alert_id,
            system_id=system_id,
            metric=metric,
            current_value=current_value,
            threshold_value=threshold_config[threshold_type.value],
            threshold_type=threshold_type,
            severity=severity,
            message=f"{metric.value} threshold exceeded: {current_value:.1f}",
            triggered_at=datetime.utcnow()
        )

        self.capacity_alerts.append(alert)

        # Log alert
        self._log_operations_event(
            system_id=system_id,
            event_type='capacity_alert',
            severity=severity,
            message=alert.message,
            operator='system',
            details={
                'alert_id': alert_id,
                'metric': metric.value,
                'current_value': current_value,
                'threshold': alert.threshold_value
            }
        )

        logger.warning(f"Capacity alert created: {alert.message}")
        return alert_id

    def _log_operations_event(self, system_id: str, event_type: str, severity: str,
                            message: str, operator: str, details: Dict[str, Any] = None):
        """Log operations event"""
        log_entry = OperationsLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            system_id=system_id,
            event_type=event_type,
            severity=severity,
            message=message,
            operator=operator,
            details=details or {}
        )

        self.operations_logs.append(log_entry)

    def create_maintenance_window(self, window_data: Dict[str, Any]) -> str:
        """
        Create a maintenance window
        Returns window ID
        """
        window_id = str(uuid.uuid4())

        window = MaintenanceWindow(
            id=window_id,
            name=window_data['name'],
            description=window_data['description'],
            systems_affected=window_data['systems_affected'],
            start_time=window_data['start_time'],
            end_time=window_data['end_time'],
            frequency=window_data['frequency'],
            approval_required=window_data.get('approval_required', True),
            notification_days=window_data.get('notification_days', 7),
            contact_groups=window_data.get('contact_groups', [])
        )

        self.maintenance_windows[window_id] = window

        logger.info(f"Maintenance window created: {window.name}")
        return window_id

    def get_operations_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive operations dashboard"""
        # Get current system health
        system_health = self._calculate_system_health()

        # Get capacity metrics summary
        capacity_summary = self._get_capacity_summary()

        # Get change management status
        change_summary = self._get_change_management_summary()

        # Get backup status
        backup_summary = self._get_backup_summary()

        # Get active alerts
        active_alerts = [alert for alert in self.capacity_alerts
                        if not alert.resolved_at][:10]  # Last 10

        # Get upcoming maintenance
        upcoming_maintenance = self._get_upcoming_maintenance()

        # Generate recommendations
        recommendations = self._generate_operations_recommendations(
            system_health, capacity_summary, change_summary, backup_summary
        )

        dashboard = OperationsDashboard(
            id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            system_health=system_health,
            capacity_metrics=capacity_summary,
            change_management=change_summary,
            backup_status=backup_summary,
            alerts_summary={
                'total_active': len([a for a in self.capacity_alerts if not a.resolved_at]),
                'critical': len([a for a in self.capacity_alerts if a.severity == 'critical' and not a.resolved_at]),
                'warning': len([a for a in self.capacity_alerts if a.severity == 'warning' and not a.resolved_at])
            },
            maintenance_schedule=upcoming_maintenance,
            recommendations=recommendations
        )

        return {
            'dashboard_id': dashboard.id,
            'generated_at': dashboard.generated_at.isoformat(),
            'period': f"{dashboard.period_start.date()} to {dashboard.period_end.date()}",
            'system_health': dashboard.system_health,
            'capacity_metrics': dashboard.capacity_metrics,
            'change_management': dashboard.change_management,
            'backup_status': dashboard.backup_status,
            'alerts_summary': dashboard.alerts_summary,
            'upcoming_maintenance': dashboard.maintenance_schedule,
            'recommendations': dashboard.recommendations
        }

    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health"""
        # Get recent operations logs (last 24 hours)
        recent_logs = [log for log in self.operations_logs
                      if (datetime.utcnow() - log.timestamp).days < 1]

        total_logs = len(recent_logs)
        error_logs = len([log for log in recent_logs if log.severity in ['error', 'critical']])
        warning_logs = len([log for log in recent_logs if log.severity == 'warning'])

        # Calculate health score (simplified)
        if total_logs == 0:
            health_score = 100
        else:
            error_rate = error_logs / total_logs
            warning_rate = warning_logs / total_logs

            health_score = max(0, 100 - (error_rate * 50) - (warning_rate * 20))

        return {
            'health_score': round(health_score, 1),
            'total_events': total_logs,
            'error_events': error_logs,
            'warning_events': warning_logs,
            'health_status': 'GOOD' if health_score >= 80 else 'FAIR' if health_score >= 60 else 'POOR'
        }

    def _get_capacity_summary(self) -> Dict[str, Any]:
        """Get capacity metrics summary"""
        # Get recent alerts (last 7 days)
        recent_alerts = [alert for alert in self.capacity_alerts
                        if (datetime.utcnow() - alert.triggered_at).days <= 7]

        return {
            'total_alerts': len(recent_alerts),
            'critical_alerts': len([a for a in recent_alerts if a.severity == 'critical']),
            'warning_alerts': len([a for a in recent_alerts if a.severity == 'warning']),
            'resolved_alerts': len([a for a in self.capacity_alerts if a.resolved_at]),
            'avg_resolution_time': self._calculate_avg_resolution_time()
        }

    def _calculate_avg_resolution_time(self) -> Optional[float]:
        """Calculate average alert resolution time in hours"""
        resolved_alerts = [a for a in self.capacity_alerts if a.resolved_at and a.acknowledged_at]

        if not resolved_alerts:
            return None

        total_time = sum((a.resolved_at - a.acknowledged_at).total_seconds() for a in resolved_alerts)
        return round(total_time / len(resolved_alerts) / 3600, 1)  # hours

    def _get_change_management_summary(self) -> Dict[str, Any]:
        """Get change management summary"""
        changes = list(self.change_requests.values())

        return {
            'total_changes': len(changes),
            'approved_changes': len([c for c in changes if c.status == ChangeStatus.APPROVED]),
            'completed_changes': len([c for c in changes if c.status == ChangeStatus.DEPLOYED]),
            'failed_changes': len([c for c in changes if c.status in [ChangeStatus.ROLLED_BACK, ChangeStatus.REJECTED]]),
            'pending_approvals': len([c for c in changes if c.status == ChangeStatus.SUBMITTED]),
            'success_rate': self._calculate_change_success_rate(changes)
        }

    def _calculate_change_success_rate(self) -> float:
        """Calculate change success rate"""
        completed_changes = len([c for c in self.change_requests.values()
                                if c.status == ChangeStatus.DEPLOYED])
        total_changes = len([c for c in self.change_requests.values()
                           if c.status in [ChangeStatus.DEPLOYED, ChangeStatus.ROLLED_BACK, ChangeStatus.REJECTED]])

        return (completed_changes / total_changes * 100) if total_changes > 0 else 100

    def _get_backup_summary(self) -> Dict[str, Any]:
        """Get backup operations summary"""
        recent_executions = [exec for exec in self.backup_executions
                           if (datetime.utcnow() - exec.start_time).days <= 7]

        return {
            'total_backups': len(recent_executions),
            'successful_backups': len([e for e in recent_executions if e.status == BackupStatus.COMPLETED]),
            'failed_backups': len([e for e in recent_executions if e.status == BackupStatus.FAILED]),
            'verified_backups': len([e for e in recent_executions if e.verification_status == 'passed']),
            'success_rate': self._calculate_backup_success_rate(recent_executions)
        }

    def _calculate_backup_success_rate(self, executions: List[BackupExecution]) -> float:
        """Calculate backup success rate"""
        if not executions:
            return 100.0

        successful = len([e for e in executions if e.status == BackupStatus.COMPLETED])
        return round(successful / len(executions) * 100, 1)

    def _get_upcoming_maintenance(self) -> List[Dict[str, Any]]:
        """Get upcoming maintenance windows"""
        upcoming = []

        for window in self.maintenance_windows.values():
            if not window.is_active:
                continue

            # Calculate next occurrence (simplified - assumes weekly)
            if window.frequency == 'weekly':
                days_until = (window.start_time.weekday() - datetime.utcnow().weekday()) % 7
                next_occurrence = datetime.utcnow() + timedelta(days=days_until)
                next_occurrence = next_occurrence.replace(
                    hour=window.start_time.hour,
                    minute=window.start_time.minute
                )
            else:
                next_occurrence = window.start_time

            if next_occurrence > datetime.utcnow():
                upcoming.append({
                    'id': window.id,
                    'name': window.name,
                    'description': window.description,
                    'start_time': next_occurrence.isoformat(),
                    'end_time': (next_occurrence + (window.end_time - window.start_time)).isoformat(),
                    'systems_affected': window.systems_affected,
                    'days_until': (next_occurrence - datetime.utcnow()).days
                })

        return sorted(upcoming, key=lambda x: x['days_until'])[:5]  # Next 5

    def _generate_operations_recommendations(self, health: Dict, capacity: Dict,
                                           changes: Dict, backups: Dict) -> List[str]:
        """Generate operations recommendations"""
        recommendations = []

        if health['health_score'] < 80:
            recommendations.append("Review system health issues and address critical alerts")

        if capacity['critical_alerts'] > 0:
            recommendations.append("Address critical capacity alerts immediately")

        if changes['success_rate'] < 95:
            recommendations.append("Review change management process to improve success rate")

        if backups['success_rate'] < 98:
            recommendations.append("Review backup procedures to improve reliability")

        if not recommendations:
            recommendations.append("Continue monitoring operations and maintain current standards")

        return recommendations

    def check_operations_security_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 operations security compliance"""
        compliance_checks = {
            'change_management': self._check_change_management_compliance(),
            'backup_operations': self._check_backup_operations_compliance(),
            'capacity_management': self._check_capacity_management_compliance(),
            'maintenance_operations': self._check_maintenance_operations_compliance(),
            'logging_monitoring': self._check_logging_monitoring_compliance()
        }

        overall_score = sum(compliance_checks.values()) / len(compliance_checks)

        issues = []
        if compliance_checks['change_management'] < 80:
            issues.append("Change management processes need improvement")
        if compliance_checks['backup_operations'] < 90:
            issues.append("Backup operations require strengthening")
        if compliance_checks['capacity_management'] < 75:
            issues.append("Capacity management practices insufficient")

        return {
            'tenant_id': tenant_id,
            'compliance_score': round(overall_score, 1),
            'control_checks': compliance_checks,
            'issues': issues,
            'recommendations': self._generate_operations_compliance_recommendations(issues),
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.12 Operations Security',
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_change_management_compliance(self) -> float:
        """Check change management compliance"""
        changes = list(self.change_requests.values())

        if not changes:
            return 100.0  # No changes means no issues

        # Check approval rates
        approved_changes = len([c for c in changes if c.status in [ChangeStatus.APPROVED, ChangeStatus.DEPLOYED]])
        approval_rate = approved_changes / len(changes) * 100

        # Check documentation completeness
        documented_changes = len([c for c in changes if c.rollback_plan and c.test_plan])
        documentation_rate = documented_changes / len(changes) * 100

        return (approval_rate + documentation_rate) / 2

    def _check_backup_operations_compliance(self) -> float:
        """Check backup operations compliance"""
        executions = self.backup_executions[-50:]  # Last 50 executions

        if not executions:
            return 50.0  # Some compliance but no data

        # Check success rate
        successful = len([e for e in executions if e.status == BackupStatus.COMPLETED])
        success_rate = successful / len(executions) * 100

        # Check verification rate
        verified = len([e for e in executions if e.verification_status == 'passed'])
        verification_rate = verified / len(executions) * 100

        return (success_rate + verification_rate) / 2

    def _check_capacity_management_compliance(self) -> float:
        """Check capacity management compliance"""
        # Check if baselines are established
        systems_with_baselines = len(set(b.system_id for b in self.capacity_baselines.values()))
        total_systems = 10  # Assumed number of systems
        baseline_coverage = min(systems_with_baselines / total_systems * 100, 100)

        # Check alert response
        resolved_alerts = len([a for a in self.capacity_alerts if a.resolved_at])
        total_alerts = len(self.capacity_alerts)
        resolution_rate = (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 100

        return (baseline_coverage + resolution_rate) / 2

    def _check_maintenance_operations_compliance(self) -> float:
        """Check maintenance operations compliance"""
        active_windows = len([w for w in self.maintenance_windows.values() if w.is_active])

        # Assume minimum of 3 maintenance windows
        if active_windows >= 3:
            return 100.0
        elif active_windows >= 2:
            return 75.0
        elif active_windows >= 1:
            return 50.0
        else:
            return 25.0

    def _check_logging_monitoring_compliance(self) -> float:
        """Check logging and monitoring compliance"""
        recent_logs = len([log for log in self.operations_logs
                          if (datetime.utcnow() - log.timestamp).days <= 7])

        # Assume minimum of 100 log entries per week
        if recent_logs >= 100:
            return 100.0
        elif recent_logs >= 50:
            return 75.0
        elif recent_logs >= 25:
            return 50.0
        else:
            return 25.0

    def _generate_operations_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate operations compliance recommendations"""
        recommendations = []

        if any('change management' in issue.lower() for issue in issues):
            recommendations.append("Strengthen change management processes with better approval workflows and documentation")

        if any('backup' in issue.lower() for issue in issues):
            recommendations.append("Improve backup operations with better success rates and verification procedures")

        if any('capacity' in issue.lower() for issue in issues):
            recommendations.append("Enhance capacity management with comprehensive baselines and alert response procedures")

        if any('maintenance' in issue.lower() for issue in issues):
            recommendations.append("Establish regular maintenance windows and approval processes")

        if any('logging' in issue.lower() for issue in issues):
            recommendations.append("Improve logging and monitoring coverage across all systems")

        recommendations.append("Implement regular operations security reviews and continuous improvement processes")

        return recommendations