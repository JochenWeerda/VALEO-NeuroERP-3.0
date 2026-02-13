"""
ISO Compliance Monitoring and Alerting
Comprehensive Compliance Monitoring Framework for ISO 27001, ISO 9001, and ISO 22301

Dieses Modul implementiert das Compliance Monitoring and Alerting Framework
für VALEO-NeuroERP mit Real-time Monitoring, Automated Alerts und Compliance Dashboards.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    ISO_27001 = "ISO 27001:2022"
    ISO_9001 = "ISO 9001:2015"
    ISO_22301 = "ISO 22301:2019"
    GDPR = "GDPR"
    SOX = "SOX"
    PCI_DSS = "PCI DSS"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FALSE_POSITIVE = "false_positive"


class MetricType(Enum):
    """Types of compliance metrics"""
    COMPLIANCE_SCORE = "compliance_score"
    CONTROL_EFFECTIVENESS = "control_effectiveness"
    AUDIT_FINDINGS = "audit_findings"
    INCIDENT_RATE = "incident_rate"
    TRAINING_COMPLETION = "training_completion"
    DOCUMENTATION_STATUS = "documentation_status"


class MonitoringFrequency(Enum):
    """Monitoring frequencies"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class ComplianceMetric:
    """Compliance metric definition"""
    id: str
    name: str
    standard: ComplianceStandard
    metric_type: MetricType
    target_value: float
    current_value: float
    unit: str
    monitoring_frequency: MonitoringFrequency
    last_updated: datetime
    responsible_party: str
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    trend: str = "stable"  # improving, stable, declining
    is_active: bool = True


@dataclass
class ComplianceAlert:
    """Compliance alert"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    standard: ComplianceStandard
    control_id: str
    metric_id: Optional[str]
    triggered_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    assigned_to: str = ""
    escalation_level: int = 0
    notification_channels: List[str] = field(default_factory=list)
    related_incidents: List[str] = field(default_factory=list)
    corrective_actions: List[str] = field(default_factory=list)


@dataclass
class ComplianceDashboard:
    """Compliance dashboard configuration"""
    id: str
    name: str
    standard: ComplianceStandard
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval: int = 300  # seconds
    user_roles: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MonitoringRule:
    """Monitoring rule definition"""
    id: str
    name: str
    standard: ComplianceStandard
    condition: str
    severity: AlertSeverity
    actions: List[Dict[str, Any]]
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceReport:
    """Compliance report"""
    id: str
    title: str
    standard: ComplianceStandard
    report_type: str  # daily, weekly, monthly, quarterly
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    generated_by: str
    overall_score: float
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    distribution_list: List[str] = field(default_factory=list)
    status: str = "draft"


@dataclass
class EscalationRule:
    """Alert escalation rule"""
    id: str
    name: str
    severity: AlertSeverity
    escalation_delays: List[int]  # minutes
    escalation_contacts: List[str]
    notification_channels: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class ISOComplianceMonitoring:
    """
    ISO Compliance Monitoring and Alerting
    Comprehensive monitoring framework for ISO standards
    """

    def __init__(self, db_session, alert_service=None, notification_service=None):
        self.db = db_session
        self.alert_service = alert_service
        self.notifications = notification_service

        # Monitoring components
        self.compliance_metrics: Dict[str, ComplianceMetric] = {}
        self.active_alerts: Dict[str, ComplianceAlert] = {}
        self.monitoring_rules: Dict[str, MonitoringRule] = {}
        self.compliance_dashboards: Dict[str, ComplianceDashboard] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.compliance_reports: List[ComplianceReport] = {}

        # Monitoring configuration
        self.monitoring_config = self._initialize_monitoring_config()

        # Alert thresholds
        self.alert_thresholds = self._initialize_alert_thresholds()

    def _initialize_monitoring_config(self) -> Dict[str, Any]:
        """Initialize monitoring configuration"""
        return {
            'monitoring_intervals': {
                'real_time': 60,    # seconds
                'hourly': 3600,     # seconds
                'daily': 86400,     # seconds
                'weekly': 604800,   # seconds
                'monthly': 2592000  # seconds
            },
            'alert_escalation': {
                'critical': {'initial_delay': 5, 'follow_up': 15, 'max_level': 3},
                'high': {'initial_delay': 15, 'follow_up': 60, 'max_level': 3},
                'medium': {'initial_delay': 60, 'follow_up': 240, 'max_level': 2},
                'low': {'initial_delay': 240, 'follow_up': 1440, 'max_level': 1}
            },
            'notification_channels': [
                'email', 'sms', 'slack', 'teams', 'dashboard'
            ],
            'report_schedules': {
                'daily': {'hour': 6, 'recipients': ['compliance_team']},
                'weekly': {'day': 1, 'hour': 9, 'recipients': ['management', 'compliance_team']},
                'monthly': {'day': 1, 'hour': 10, 'recipients': ['executives', 'board']}
            }
        }

    def _initialize_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize alert thresholds for different standards"""
        return {
            'ISO_27001': {
                'compliance_score': 95.0,
                'incident_rate': 0.1,  # incidents per month
                'control_effectiveness': 90.0,
                'audit_findings': 5.0   # max major findings
            },
            'ISO_9001': {
                'compliance_score': 95.0,
                'quality_incidents': 0.5,  # incidents per month
                'training_completion': 95.0,
                'process_performance': 90.0
            },
            'ISO_22301': {
                'compliance_score': 95.0,
                'recovery_time': 4.0,  # hours RTO
                'continuity_incidents': 0.2,  # incidents per month
                'backup_success': 99.5
            }
        }

    def create_compliance_metric(self, metric_data: Dict[str, Any]) -> str:
        """
        Create a compliance metric
        Returns metric ID
        """
        metric_id = str(uuid.uuid4())

        metric = ComplianceMetric(
            id=metric_id,
            name=metric_data['name'],
            standard=ComplianceStandard[metric_data['standard'].upper()],
            metric_type=MetricType[metric_data['metric_type'].upper()],
            target_value=metric_data['target_value'],
            current_value=metric_data.get('current_value', 0.0),
            unit=metric_data['unit'],
            monitoring_frequency=MonitoringFrequency[metric_data['monitoring_frequency'].upper()],
            last_updated=datetime.utcnow(),
            responsible_party=metric_data['responsible_party'],
            alert_thresholds=metric_data.get('alert_thresholds', {})
        )

        self.compliance_metrics[metric_id] = metric

        logger.info(f"Compliance metric created: {metric.name} ({metric.standard.value})")
        return metric_id

    def update_metric_value(self, metric_id: str, new_value: float, updated_by: str = "system") -> bool:
        """
        Update a metric value and check for alerts
        """
        if metric_id not in self.compliance_metrics:
            return False

        metric = self.compliance_metrics[metric_id]
        old_value = metric.current_value
        metric.current_value = new_value
        metric.last_updated = datetime.utcnow()

        # Determine trend
        if new_value > old_value:
            metric.trend = "improving"
        elif new_value < old_value:
            metric.trend = "declining"
        else:
            metric.trend = "stable"

        # Check for alerts
        self._check_metric_alerts(metric)

        logger.info(f"Metric updated: {metric.name} = {new_value} ({metric.trend})")
        return True

    def _check_metric_alerts(self, metric: ComplianceMetric):
        """Check if metric triggers any alerts"""
        thresholds = metric.alert_thresholds or self.alert_thresholds.get(metric.standard.value, {})

        for threshold_type, threshold_value in thresholds.items():
            if threshold_type == 'compliance_score' and metric.current_value < threshold_value:
                self._create_metric_alert(metric, threshold_value, 'below_threshold')
            elif threshold_type == 'incident_rate' and metric.current_value > threshold_value:
                self._create_metric_alert(metric, threshold_value, 'above_threshold')
            elif threshold_type == 'control_effectiveness' and metric.current_value < threshold_value:
                self._create_metric_alert(metric, threshold_value, 'below_threshold')

    def _create_metric_alert(self, metric: ComplianceMetric, threshold: float, condition: str):
        """Create an alert for metric threshold violation"""
        alert_id = str(uuid.uuid4())

        severity = AlertSeverity.MEDIUM
        if metric.metric_type == MetricType.COMPLIANCE_SCORE and metric.current_value < 90:
            severity = AlertSeverity.CRITICAL
        elif metric.current_value < threshold * 0.9:
            severity = AlertSeverity.HIGH

        alert = ComplianceAlert(
            id=alert_id,
            title=f"Compliance Metric Alert: {metric.name}",
            description=f"Metric {metric.name} is {condition} threshold ({metric.current_value:.1f} vs {threshold:.1f})",
            severity=severity,
            status=AlertStatus.ACTIVE,
            standard=metric.standard,
            control_id=f"metric_{metric.id}",
            metric_id=metric.id,
            triggered_value=metric.current_value,
            threshold_value=threshold,
            triggered_at=datetime.utcnow(),
            assigned_to=metric.responsible_party,
            notification_channels=['email', 'dashboard']
        )

        self.active_alerts[alert_id] = alert

        # Trigger notifications
        self._notify_alert(alert)

        logger.warning(f"Compliance alert created: {alert.title} (Severity: {alert.severity.value})")

    def _notify_alert(self, alert: ComplianceAlert):
        """Send alert notifications"""
        # In production, this would send actual notifications
        logger.info(f"Alert notification sent: {alert.title} to {alert.assigned_to}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert
        """
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by

        logger.info(f"Alert acknowledged: {alert.title} by {acknowledged_by}")
        return True

    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """
        Resolve an alert
        """
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by

        logger.info(f"Alert resolved: {alert.title} by {resolved_by}")
        return True

    def create_monitoring_rule(self, rule_data: Dict[str, Any]) -> str:
        """
        Create a monitoring rule
        Returns rule ID
        """
        rule_id = str(uuid.uuid4())

        rule = MonitoringRule(
            id=rule_id,
            name=rule_data['name'],
            standard=ComplianceStandard[rule_data['standard'].upper()],
            condition=rule_data['condition'],
            severity=AlertSeverity[rule_data['severity'].upper()],
            actions=rule_data.get('actions', [])
        )

        self.monitoring_rules[rule_id] = rule

        logger.info(f"Monitoring rule created: {rule.name} for {rule.standard.value}")
        return rule_id

    def create_compliance_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Create a compliance dashboard
        Returns dashboard ID
        """
        dashboard_id = str(uuid.uuid4())

        dashboard = ComplianceDashboard(
            id=dashboard_id,
            name=dashboard_data['name'],
            standard=ComplianceStandard[dashboard_data['standard'].upper()],
            widgets=dashboard_data.get('widgets', []),
            refresh_interval=dashboard_data.get('refresh_interval', 300),
            user_roles=dashboard_data.get('user_roles', [])
        )

        self.compliance_dashboards[dashboard_id] = dashboard

        logger.info(f"Compliance dashboard created: {dashboard.name}")
        return dashboard_id

    def generate_compliance_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a compliance report
        Returns report ID
        """
        report_id = str(uuid.uuid4())

        report = ComplianceReport(
            id=report_id,
            title=report_data['title'],
            standard=ComplianceStandard[report_data['standard'].upper()],
            report_type=report_data['report_type'],
            period_start=report_data['period_start'],
            period_end=report_data['period_end'],
            generated_at=datetime.utcnow(),
            generated_by=report_data['generated_by'],
            overall_score=report_data.get('overall_score', 0.0),
            findings=report_data.get('findings', []),
            recommendations=report_data.get('recommendations', []),
            distribution_list=report_data.get('distribution_list', [])
        )

        self.compliance_reports.append(report)

        logger.info(f"Compliance report generated: {report.title} ({report.standard.value})")
        return report_id

    def get_compliance_dashboard_data(self, dashboard_id: str, tenant_id: str = "system") -> Dict[str, Any]:
        """Get compliance dashboard data"""
        if dashboard_id not in self.compliance_dashboards:
            return {'error': 'Dashboard not found'}

        dashboard = self.compliance_dashboards[dashboard_id]

        # Get relevant metrics for this dashboard
        relevant_metrics = [
            m for m in self.compliance_metrics.values()
            if m.standard == dashboard.standard and m.is_active
        ]

        # Get active alerts
        active_alerts = [
            a for a in self.active_alerts.values()
            if a.standard == dashboard.standard and a.status == AlertStatus.ACTIVE
        ]

        # Calculate compliance scores
        compliance_data = self._calculate_compliance_scores(dashboard.standard, relevant_metrics)

        return {
            'dashboard_id': dashboard_id,
            'dashboard_name': dashboard.name,
            'standard': dashboard.standard.value,
            'last_updated': datetime.utcnow().isoformat(),
            'compliance_scores': compliance_data,
            'active_alerts': [
                {
                    'id': a.id,
                    'title': a.title,
                    'severity': a.severity.value,
                    'triggered_at': a.triggered_at.isoformat(),
                    'assigned_to': a.assigned_to
                } for a in active_alerts
            ],
            'metrics_summary': [
                {
                    'name': m.name,
                    'current_value': m.current_value,
                    'target_value': m.target_value,
                    'trend': m.trend,
                    'last_updated': m.last_updated.isoformat()
                } for m in relevant_metrics
            ],
            'widgets': dashboard.widgets
        }

    def _calculate_compliance_scores(self, standard: ComplianceStandard,
                                   metrics: List[ComplianceMetric]) -> Dict[str, Any]:
        """Calculate compliance scores for a standard"""
        if not metrics:
            return {'overall_score': 0, 'metrics_count': 0}

        total_score = 0
        compliant_metrics = 0

        for metric in metrics:
            score = min(100, (metric.current_value / metric.target_value) * 100) if metric.target_value > 0 else 0
            total_score += score

            if score >= 95:  # Consider compliant if >= 95%
                compliant_metrics += 1

        overall_score = total_score / len(metrics)

        return {
            'overall_score': round(overall_score, 1),
            'compliant_metrics': compliant_metrics,
            'total_metrics': len(metrics),
            'compliance_rate': round((compliant_metrics / len(metrics)) * 100, 1),
            'score_trend': self._calculate_score_trend(metrics)
        }

    def _calculate_score_trend(self, metrics: List[ComplianceMetric]) -> str:
        """Calculate overall score trend"""
        improving = sum(1 for m in metrics if m.trend == 'improving')
        declining = sum(1 for m in metrics if m.trend == 'declining')

        if improving > declining:
            return 'improving'
        elif declining > improving:
            return 'declining'
        else:
            return 'stable'

    def get_compliance_monitoring_report(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive compliance monitoring report"""
        # Get all active metrics
        active_metrics = [m for m in self.compliance_metrics.values() if m.is_active]

        # Get active alerts
        active_alerts = list(self.active_alerts.values())

        # Get recent reports
        recent_reports = [r for r in self.compliance_reports[-10:]]  # Last 10 reports

        # Calculate monitoring statistics
        monitoring_stats = self._calculate_monitoring_statistics(active_metrics, active_alerts)

        # Get compliance by standard
        compliance_by_standard = {}
        for standard in ComplianceStandard:
            standard_metrics = [m for m in active_metrics if m.standard == standard]
            if standard_metrics:
                compliance_by_standard[standard.value] = self._calculate_compliance_scores(standard, standard_metrics)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'monitoring_statistics': monitoring_stats,
            'compliance_by_standard': compliance_by_standard,
            'active_alerts_summary': {
                'total': len(active_alerts),
                'by_severity': self._count_alerts_by_severity(active_alerts),
                'by_standard': self._count_alerts_by_standard(active_alerts)
            },
            'recent_reports': [
                {
                    'id': r.id,
                    'title': r.title,
                    'standard': r.standard.value,
                    'overall_score': r.overall_score,
                    'generated_at': r.generated_at.isoformat()
                } for r in recent_reports
            ],
            'system_health': self._assess_system_health(active_metrics, active_alerts)
        }

    def _calculate_monitoring_statistics(self, metrics: List[ComplianceMetric],
                                       alerts: List[ComplianceAlert]) -> Dict[str, Any]:
        """Calculate monitoring statistics"""
        return {
            'total_metrics': len(metrics),
            'active_metrics': len([m for m in metrics if m.is_active]),
            'metrics_by_standard': self._count_metrics_by_standard(metrics),
            'metrics_by_frequency': self._count_metrics_by_frequency(metrics),
            'total_alerts': len(alerts),
            'active_alerts': len([a for a in alerts if a.status == AlertStatus.ACTIVE]),
            'alerts_last_24h': len([a for a in alerts if (datetime.utcnow() - a.triggered_at).days < 1]),
            'alerts_last_7d': len([a for a in alerts if (datetime.utcnow() - a.triggered_at).days <= 7])
        }

    def _count_metrics_by_standard(self, metrics: List[ComplianceMetric]) -> Dict[str, int]:
        """Count metrics by standard"""
        counts = {}
        for metric in metrics:
            standard = metric.standard.value
            counts[standard] = counts.get(standard, 0) + 1
        return counts

    def _count_metrics_by_frequency(self, metrics: List[ComplianceMetric]) -> Dict[str, int]:
        """Count metrics by monitoring frequency"""
        counts = {}
        for metric in metrics:
            frequency = metric.monitoring_frequency.value
            counts[frequency] = counts.get(frequency, 0) + 1
        return counts

    def _count_alerts_by_severity(self, alerts: List[ComplianceAlert]) -> Dict[str, int]:
        """Count alerts by severity"""
        counts = {}
        for alert in alerts:
            severity = alert.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _count_alerts_by_standard(self, alerts: List[ComplianceAlert]) -> Dict[str, int]:
        """Count alerts by standard"""
        counts = {}
        for alert in alerts:
            standard = alert.standard.value
            counts[standard] = counts.get(standard, 0) + 1
        return counts

    def _assess_system_health(self, metrics: List[ComplianceMetric],
                            alerts: List[ComplianceAlert]) -> Dict[str, Any]:
        """Assess overall system health"""
        # Calculate health score based on metrics and alerts
        metric_health = len([m for m in metrics if m.current_value >= m.target_value * 0.95]) / len(metrics) if metrics else 0
        alert_health = 1 - (len([a for a in alerts if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]]) / max(len(alerts), 1))

        overall_health = (metric_health + alert_health) / 2

        if overall_health >= 0.9:
            health_status = 'excellent'
        elif overall_health >= 0.8:
            health_status = 'good'
        elif overall_health >= 0.7:
            health_status = 'fair'
        elif overall_health >= 0.6:
            health_status = 'poor'
        else:
            health_status = 'critical'

        return {
            'health_score': round(overall_health * 100, 1),
            'health_status': health_status,
            'metric_health': round(metric_health * 100, 1),
            'alert_health': round(alert_health * 100, 1),
            'recommendations': self._generate_health_recommendations(health_status)
        }

    def _generate_health_recommendations(self, health_status: str) -> List[str]:
        """Generate health recommendations"""
        recommendations = []

        if health_status == 'critical':
            recommendations.extend([
                "Immediate action required - critical compliance issues detected",
                "Escalate to executive management",
                "Implement emergency remediation measures"
            ])
        elif health_status == 'poor':
            recommendations.extend([
                "Address high-priority alerts immediately",
                "Review and update compliance metrics",
                "Conduct comprehensive compliance assessment"
            ])
        elif health_status == 'fair':
            recommendations.extend([
                "Monitor active alerts closely",
                "Implement corrective actions for medium-risk issues",
                "Schedule management review"
            ])
        elif health_status == 'good':
            recommendations.extend([
                "Continue monitoring and maintenance",
                "Address remaining low-priority items",
                "Plan for continuous improvement"
            ])
        else:  # excellent
            recommendations.extend([
                "Maintain current high standards",
                "Focus on proactive improvements",
                "Share best practices across organization"
            ])

        return recommendations

    def check_compliance_monitoring_health(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check compliance monitoring system health"""
        metrics_count = len([m for m in self.compliance_metrics.values() if m.is_active])
        rules_count = len([r for r in self.monitoring_rules.values() if r.is_active])
        alerts_count = len(self.active_alerts)
        dashboards_count = len([d for d in self.compliance_dashboards.values() if d.is_active])

        health_score = 100

        # Check for adequate monitoring coverage
        if metrics_count < 20:  # Arbitrary minimum
            health_score -= 20

        if rules_count < 10:
            health_score -= 15

        if dashboards_count < 3:
            health_score -= 10

        # Check for alert backlog
        critical_alerts = len([a for a in self.active_alerts.values()
                             if a.severity == AlertSeverity.CRITICAL and a.status == AlertStatus.ACTIVE])
        if critical_alerts > 0:
            health_score -= critical_alerts * 5

        health_status = 'GOOD' if health_score >= 80 else 'FAIR' if health_score >= 60 else 'POOR'

        return {
            'tenant_id': tenant_id,
            'health_score': max(health_score, 0),
            'health_status': health_status,
            'metrics_count': metrics_count,
            'rules_count': rules_count,
            'alerts_count': alerts_count,
            'dashboards_count': dashboards_count,
            'critical_alerts': critical_alerts,
            'last_check': datetime.utcnow().isoformat()
        }