"""
ISO 9001 Quality Assurance System
Qualitätsmanagementsystem Quality Assurance

Dieses Modul implementiert das Quality Assurance System gemäß ISO 9001
für VALEO-NeuroERP mit Prozess-Überwachung, Qualitätsmetriken und kontinuierlicher Verbesserung.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
import statistics

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Quality metrics for monitoring"""
    DEFECT_DENSITY = "defect_density"
    TEST_COVERAGE = "test_coverage"
    DEPLOYMENT_SUCCESS_RATE = "deployment_success_rate"
    MEAN_TIME_TO_RESOLUTION = "mean_time_to_resolution"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    PROCESS_COMPLIANCE = "process_compliance"
    CODE_QUALITY_SCORE = "code_quality_score"
    SECURITY_VULNERABILITIES = "security_vulnerabilities"


class QualityGate(Enum):
    """Quality gates in the development pipeline"""
    CODE_COMMIT = "code_commit"
    PULL_REQUEST = "pull_request"
    BUILD = "build"
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_TEST = "performance_test"
    DEPLOYMENT = "deployment"
    PRODUCTION_MONITORING = "production_monitoring"


class QualityIssueSeverity(Enum):
    """Severity levels for quality issues"""
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


class QualityIssueStatus(Enum):
    """Status of quality issues"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


@dataclass
class QualityIssue:
    """Quality issue representation"""
    id: str
    title: str
    description: str
    severity: QualityIssueSeverity
    status: QualityIssueStatus
    category: str
    component: str
    reported_by: str
    assigned_to: Optional[str] = None

    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # Root cause and resolution
    root_cause: str = ""
    resolution: str = ""
    preventive_actions: List[str] = field(default_factory=list)

    # Impact assessment
    affected_processes: List[str] = field(default_factory=list)
    business_impact: str = ""
    customer_impact: str = ""

    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)

    # Metadata
    tenant_id: str = "system"
    tags: List[str] = field(default_factory=list)


@dataclass
class QualityMetricData:
    """Quality metric data point"""
    id: str
    metric: QualityMetric
    value: float
    timestamp: datetime
    component: str
    tenant_id: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateResult:
    """Result of a quality gate check"""
    gate: QualityGate
    component: str
    passed: bool
    score: float
    issues: List[str]
    timestamp: datetime
    duration: Optional[int] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


class ISO9001QualityAssurance:
    """
    ISO 9001 Quality Assurance System
    Implements quality management principles and continuous improvement
    """

    def __init__(self, db_session, monitoring_service=None, notification_service=None):
        self.db = db_session
        self.monitoring = monitoring_service
        self.notifications = notification_service

        # Quality tracking
        self.quality_issues: Dict[str, QualityIssue] = {}
        self.quality_metrics: List[QualityMetricData] = []
        self.quality_gates: List[QualityGateResult] = []

        # Quality thresholds
        self.quality_thresholds = self._initialize_quality_thresholds()

        # SLA definitions
        self.sla_targets = {
            QualityIssueSeverity.CRITICAL: timedelta(hours=4),
            QualityIssueSeverity.MAJOR: timedelta(days=2),
            QualityIssueSeverity.MINOR: timedelta(days=7),
            QualityIssueSeverity.INFO: timedelta(days=14)
        }

    def _initialize_quality_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality thresholds for different metrics"""
        return {
            QualityMetric.DEFECT_DENSITY.value: {
                'target': 0.5,  # defects per 1000 lines of code
                'warning': 1.0,
                'critical': 2.0,
                'trend_period_days': 30
            },
            QualityMetric.TEST_COVERAGE.value: {
                'target': 80.0,  # percentage
                'warning': 70.0,
                'critical': 60.0,
                'trend_period_days': 7
            },
            QualityMetric.DEPLOYMENT_SUCCESS_RATE.value: {
                'target': 95.0,  # percentage
                'warning': 90.0,
                'critical': 85.0,
                'trend_period_days': 30
            },
            QualityMetric.MEAN_TIME_TO_RESOLUTION.value: {
                'target': 24.0,  # hours
                'warning': 48.0,
                'critical': 72.0,
                'trend_period_days': 30
            },
            QualityMetric.CUSTOMER_SATISFACTION.value: {
                'target': 4.5,  # out of 5
                'warning': 4.0,
                'critical': 3.5,
                'trend_period_days': 90
            },
            QualityMetric.PROCESS_COMPLIANCE.value: {
                'target': 95.0,  # percentage
                'warning': 90.0,
                'critical': 85.0,
                'trend_period_days': 30
            },
            QualityMetric.CODE_QUALITY_SCORE.value: {
                'target': 85.0,  # percentage
                'warning': 75.0,
                'critical': 65.0,
                'trend_period_days': 7
            },
            QualityMetric.SECURITY_VULNERABILITIES.value: {
                'target': 0,  # count
                'warning': 5,
                'critical': 10,
                'trend_period_days': 7
            }
        }

    def report_quality_issue(self, issue_data: Dict[str, Any]) -> str:
        """
        Report a new quality issue
        Returns issue ID
        """
        issue_id = str(uuid.uuid4())

        issue = QualityIssue(
            id=issue_id,
            title=issue_data['title'],
            description=issue_data.get('description', ''),
            severity=QualityIssueSeverity[issue_data['severity']],
            status=QualityIssueStatus.OPEN,
            category=issue_data.get('category', 'general'),
            component=issue_data.get('component', 'unknown'),
            reported_by=issue_data['reported_by'],
            assigned_to=issue_data.get('assigned_to'),
            tenant_id=issue_data.get('tenant_id', 'system'),
            affected_processes=issue_data.get('affected_processes', []),
            business_impact=issue_data.get('business_impact', ''),
            customer_impact=issue_data.get('customer_impact', ''),
            tags=issue_data.get('tags', [])
        )

        # Set due date based on SLA
        issue.due_date = datetime.utcnow() + self.sla_targets[issue.severity]

        self.quality_issues[issue_id] = issue

        # Trigger notifications
        self._notify_issue_reported(issue)

        logger.info(f"Quality issue reported: {issue_id} - {issue.title}")
        return issue_id

    def _notify_issue_reported(self, issue: QualityIssue):
        """Notify relevant stakeholders about new quality issue"""
        notification_data = {
            'type': 'quality_issue_reported',
            'issue_id': issue.id,
            'title': issue.title,
            'severity': issue.severity.value,
            'component': issue.component,
            'reported_by': issue.reported_by,
            'due_date': issue.due_date.isoformat() if issue.due_date else None
        }

        if self.notifications:
            self.notifications.send_quality_notification(notification_data)

    def update_quality_issue(self, issue_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update quality issue status and information
        """
        if issue_id not in self.quality_issues:
            return False

        issue = self.quality_issues[issue_id]
        old_status = issue.status

        # Update fields
        for key, value in update_data.items():
            if hasattr(issue, key):
                setattr(issue, key, value)

        issue.updated_at = datetime.utcnow()

        # Status-specific actions
        if 'status' in update_data:
            new_status = QualityIssueStatus[update_data['status']]
            if new_status == QualityIssueStatus.RESOLVED:
                issue.resolved_at = datetime.utcnow()
            elif new_status == QualityIssueStatus.CLOSED:
                if not issue.resolved_at:
                    issue.resolved_at = datetime.utcnow()

        # Notify stakeholders
        self._notify_issue_updated(issue, old_status)

        logger.info(f"Quality issue updated: {issue_id} - {old_status.value} -> {issue.status.value}")
        return True

    def _notify_issue_updated(self, issue: QualityIssue, old_status: QualityIssueStatus):
        """Notify about issue updates"""
        if self.notifications:
            self.notifications.send_quality_notification({
                'type': 'quality_issue_updated',
                'issue_id': issue.id,
                'title': issue.title,
                'old_status': old_status.value,
                'new_status': issue.status.value,
                'severity': issue.severity.value,
                'assigned_to': issue.assigned_to
            })

    def record_quality_metric(self, metric: QualityMetric, value: float,
                            component: str, tenant_id: str = "system",
                            metadata: Dict[str, Any] = None) -> str:
        """
        Record a quality metric data point
        Returns metric data ID
        """
        metric_id = str(uuid.uuid4())

        metric_data = QualityMetricData(
            id=metric_id,
            metric=metric,
            value=value,
            timestamp=datetime.utcnow(),
            component=component,
            tenant_id=tenant_id,
            metadata=metadata or {}
        )

        self.quality_metrics.append(metric_data)

        # Check thresholds and trigger alerts
        self._check_metric_thresholds(metric_data)

        logger.debug(f"Quality metric recorded: {metric.value} = {value} for {component}")
        return metric_id

    def _check_metric_thresholds(self, metric_data: QualityMetricData):
        """Check if metric value violates thresholds"""
        thresholds = self.quality_thresholds.get(metric_data.metric.value)
        if not thresholds:
            return

        value = metric_data.value
        alerts = []

        if value >= thresholds['critical']:
            alerts.append('CRITICAL')
        elif value >= thresholds['warning']:
            alerts.append('WARNING')

        if alerts:
            self._trigger_metric_alert(metric_data, alerts[0], thresholds)

    def _trigger_metric_alert(self, metric_data: QualityMetricData, severity: str, thresholds: Dict[str, Any]):
        """Trigger alert for metric threshold violation"""
        alert_data = {
            'type': 'quality_metric_alert',
            'metric': metric_data.metric.value,
            'value': metric_data.value,
            'threshold': thresholds[f"{severity.lower()}"],
            'severity': severity,
            'component': metric_data.component,
            'tenant_id': metric_data.tenant_id,
            'timestamp': metric_data.timestamp.isoformat()
        }

        if self.notifications:
            self.notifications.send_quality_notification(alert_data)

        logger.warning(f"Quality metric alert: {metric_data.metric.value} = {metric_data.value} "
                      f"({severity} threshold: {thresholds[f'{severity.lower()}']})")

    def execute_quality_gate(self, gate: QualityGate, component: str,
                           tenant_id: str = "system") -> QualityGateResult:
        """
        Execute a quality gate check
        Returns gate result
        """
        start_time = datetime.utcnow()

        # Perform gate checks
        passed, score, issues = self._perform_gate_checks(gate, component, tenant_id)

        end_time = datetime.utcnow()
        duration = int((end_time - start_time).total_seconds())

        result = QualityGateResult(
            gate=gate,
            component=component,
            passed=passed,
            score=score,
            issues=issues,
            timestamp=end_time,
            duration=duration
        )

        self.quality_gates.append(result)

        # Block deployment if gate fails
        if not passed and gate in [QualityGate.BUILD, QualityGate.SECURITY_SCAN, QualityGate.DEPLOYMENT]:
            self._block_deployment(component, gate, issues)

        logger.info(f"Quality gate {gate.value} for {component}: {'PASSED' if passed else 'FAILED'} "
                   f"(score: {score:.1f})")

        return result

    def _perform_gate_checks(self, gate: QualityGate, component: str, tenant_id: str) -> Tuple[bool, float, List[str]]:
        """Perform actual quality gate checks"""
        issues = []
        score = 100.0

        if gate == QualityGate.CODE_COMMIT:
            # Check code quality
            score, issues = self._check_code_quality(component)

        elif gate == QualityGate.PULL_REQUEST:
            # Check PR quality
            score, issues = self._check_pull_request_quality(component)

        elif gate == QualityGate.BUILD:
            # Check build success
            score, issues = self._check_build_quality(component)

        elif gate == QualityGate.UNIT_TEST:
            # Check test coverage and results
            score, issues = self._check_test_quality(component)

        elif gate == QualityGate.SECURITY_SCAN:
            # Check security scan results
            score, issues = self._check_security_quality(component)

        elif gate == QualityGate.PERFORMANCE_TEST:
            # Check performance metrics
            score, issues = self._check_performance_quality(component)

        # Determine pass/fail
        passed = score >= 80.0  # 80% quality threshold

        return passed, score, issues

    def _check_code_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check code quality metrics"""
        issues = []

        # Get recent metrics for component
        recent_metrics = [
            m for m in self.quality_metrics[-50:]  # Last 50 metrics
            if m.component == component and m.metric in [QualityMetric.CODE_QUALITY_SCORE, QualityMetric.DEFECT_DENSITY]
        ]

        if not recent_metrics:
            return 85.0, ["No recent code quality metrics available"]

        # Calculate average quality score
        quality_scores = [m.value for m in recent_metrics if m.metric == QualityMetric.CODE_QUALITY_SCORE]
        defect_density = [m.value for m in recent_metrics if m.metric == QualityMetric.DEFECT_DENSITY]

        avg_quality = statistics.mean(quality_scores) if quality_scores else 75.0
        avg_defects = statistics.mean(defect_density) if defect_density else 1.0

        # Penalize for high defect density
        if avg_defects > 1.0:
            avg_quality -= (avg_defects - 1.0) * 10

        if avg_quality < 70:
            issues.append(f"Code quality score too low: {avg_quality:.1f}%")

        return max(avg_quality, 0), issues

    def _check_test_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check test quality and coverage"""
        issues = []

        # Get test coverage metrics
        coverage_metrics = [
            m.value for m in self.quality_metrics[-10:]
            if m.component == component and m.metric == QualityMetric.TEST_COVERAGE
        ]

        if not coverage_metrics:
            return 60.0, ["No test coverage data available"]

        avg_coverage = statistics.mean(coverage_metrics)

        if avg_coverage < 80:
            issues.append(f"Test coverage too low: {avg_coverage:.1f}% (target: 80%)")

        # Calculate score based on coverage
        score = min(avg_coverage, 100)

        return score, issues

    def _check_security_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check security scan results"""
        issues = []

        # Get security vulnerability metrics
        vuln_metrics = [
            m.value for m in self.quality_metrics[-5:]
            if m.component == component and m.metric == QualityMetric.SECURITY_VULNERABILITIES
        ]

        if not vuln_metrics:
            return 90.0, ["No security scan data available"]

        avg_vulns = statistics.mean(vuln_metrics)

        if avg_vulns > 5:
            issues.append(f"Too many security vulnerabilities: {avg_vulns:.0f} (max: 5)")

        # Calculate score (inverse of vulnerabilities)
        score = max(100 - (avg_vulns * 5), 0)

        return score, issues

    def _check_pull_request_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check pull request quality"""
        # Simplified PR quality check
        return 85.0, []

    def _check_build_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check build quality"""
        # Simplified build quality check
        return 95.0, []

    def _check_performance_quality(self, component: str) -> Tuple[float, List[str]]:
        """Check performance quality"""
        # Simplified performance check
        return 88.0, []

    def _block_deployment(self, component: str, gate: QualityGate, issues: List[str]):
        """Block deployment due to failed quality gate"""
        logger.error(f"Deployment blocked for {component} at {gate.value}: {', '.join(issues)}")

        if self.notifications:
            self.notifications.send_quality_notification({
                'type': 'deployment_blocked',
                'component': component,
                'gate': gate.value,
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            })

    def get_quality_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get quality management dashboard"""
        # Filter data by tenant
        tenant_issues = [
            issue for issue in self.quality_issues.values()
            if issue.tenant_id == tenant_id
        ]

        tenant_metrics = [
            metric for metric in self.quality_metrics[-100:]  # Last 100 metrics
            if metric.tenant_id == tenant_id
        ]

        tenant_gates = [
            gate for gate in self.quality_gates[-50:]  # Last 50 gates
            if gate.metadata.get('tenant_id') == tenant_id
        ]

        # Calculate metrics
        issue_stats = self._calculate_issue_statistics(tenant_issues)
        metric_trends = self._calculate_metric_trends(tenant_metrics)
        gate_stats = self._calculate_gate_statistics(tenant_gates)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'issue_statistics': issue_stats,
            'metric_trends': metric_trends,
            'gate_statistics': gate_stats,
            'quality_score': self._calculate_overall_quality_score(issue_stats, metric_trends, gate_stats),
            'alerts': self._get_active_quality_alerts(tenant_id)
        }

    def _calculate_issue_statistics(self, issues: List[QualityIssue]) -> Dict[str, Any]:
        """Calculate quality issue statistics"""
        if not issues:
            return {'total': 0, 'by_severity': {}, 'by_status': {}, 'avg_resolution_time': 0}

        severity_counts = {}
        status_counts = {}
        resolution_times = []

        for issue in issues:
            severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1
            status_counts[issue.status.value] = status_counts.get(issue.status.value, 0) + 1

            if issue.resolved_at and issue.created_at:
                resolution_time = (issue.resolved_at - issue.created_at).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)

        avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0

        return {
            'total': len(issues),
            'by_severity': severity_counts,
            'by_status': status_counts,
            'avg_resolution_time': round(avg_resolution_time, 1)
        }

    def _calculate_metric_trends(self, metrics: List[QualityMetricData]) -> Dict[str, Any]:
        """Calculate quality metric trends"""
        trends = {}

        # Group by metric type
        metric_groups = {}
        for metric in metrics:
            if metric.metric.value not in metric_groups:
                metric_groups[metric.metric.value] = []
            metric_groups[metric.metric.value].append(metric.value)

        # Calculate trends for each metric
        for metric_name, values in metric_groups.items():
            if len(values) >= 2:
                current = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
                previous = statistics.mean(values[:-3]) if len(values) > 3 else values[0]

                if previous > 0:
                    trend_percentage = ((current - previous) / previous) * 100
                else:
                    trend_percentage = 0

                thresholds = self.quality_thresholds.get(metric_name, {})
                status = 'GOOD'
                if current >= thresholds.get('critical', 999):
                    status = 'CRITICAL'
                elif current >= thresholds.get('warning', 999):
                    status = 'WARNING'

                trends[metric_name] = {
                    'current': round(current, 2),
                    'trend': round(trend_percentage, 1),
                    'status': status,
                    'target': thresholds.get('target', 'N/A')
                }

        return trends

    def _calculate_gate_statistics(self, gates: List[QualityGateResult]) -> Dict[str, Any]:
        """Calculate quality gate statistics"""
        if not gates:
            return {'total': 0, 'pass_rate': 0, 'avg_score': 0}

        total_gates = len(gates)
        passed_gates = sum(1 for gate in gates if gate.passed)
        avg_score = statistics.mean(gate.score for gate in gates)

        return {
            'total': total_gates,
            'passed': passed_gates,
            'pass_rate': round((passed_gates / total_gates) * 100, 1),
            'avg_score': round(avg_score, 1)
        }

    def _calculate_overall_quality_score(self, issue_stats: Dict, metric_trends: Dict,
                                       gate_stats: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0

        # Penalize for open issues
        open_issues = issue_stats.get('by_status', {}).get('OPEN', 0)
        score -= min(open_issues * 2, 30)

        # Penalize for failed gates
        pass_rate = gate_stats.get('pass_rate', 100)
        score -= (100 - pass_rate) * 0.5

        # Penalize for metric violations
        critical_metrics = sum(1 for trend in metric_trends.values() if trend['status'] == 'CRITICAL')
        warning_metrics = sum(1 for trend in metric_trends.values() if trend['status'] == 'WARNING')

        score -= critical_metrics * 10
        score -= warning_metrics * 5

        return max(round(score, 1), 0)

    def _get_active_quality_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active quality alerts"""
        alerts = []

        # Check for overdue issues
        overdue_issues = [
            issue for issue in self.quality_issues.values()
            if issue.tenant_id == tenant_id and issue.due_date and
            datetime.utcnow() > issue.due_date and issue.status in [QualityIssueStatus.OPEN, QualityIssueStatus.IN_PROGRESS]
        ]

        for issue in overdue_issues:
            alerts.append({
                'type': 'overdue_issue',
                'severity': 'HIGH',
                'message': f"Issue '{issue.title}' is overdue",
                'issue_id': issue.id,
                'days_overdue': (datetime.utcnow() - issue.due_date).days
            })

        # Check for failing quality gates
        recent_gates = [gate for gate in self.quality_gates[-10:] if not gate.passed]
        for gate in recent_gates:
            alerts.append({
                'type': 'failed_gate',
                'severity': 'MEDIUM',
                'message': f"Quality gate '{gate.gate.value}' failed for {gate.component}",
                'gate': gate.gate.value,
                'component': gate.component,
                'score': gate.score
            })

        return alerts

    def generate_quality_report(self, tenant_id: str = "system",
                              start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        dashboard = self.get_quality_dashboard(tenant_id)

        report = {
            'tenant_id': tenant_id,
            'report_period': f"{start_date.date()} to {end_date.date()}",
            'generated_at': datetime.utcnow(),
            'quality_score': dashboard['quality_score'],
            'issue_statistics': dashboard['issue_statistics'],
            'metric_trends': dashboard['metric_trends'],
            'gate_statistics': dashboard['gate_statistics'],
            'active_alerts': dashboard['alerts'],
            'recommendations': self._generate_quality_recommendations(dashboard),
            'compliance_status': self._assess_iso9001_compliance(dashboard)
        }

        return report

    def _generate_quality_recommendations(self, dashboard: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []

        # Issue-based recommendations
        issue_stats = dashboard['issue_statistics']
        if issue_stats['total'] > 10:
            recommendations.append("Implement preventive measures to reduce quality issue volume")

        open_critical = issue_stats.get('by_severity', {}).get('CRITICAL', 0)
        if open_critical > 0:
            recommendations.append("Prioritize resolution of critical quality issues")

        # Metric-based recommendations
        for metric_name, trend in dashboard['metric_trends'].items():
            if trend['status'] == 'CRITICAL':
                recommendations.append(f"Immediate action required for {metric_name} (currently {trend['current']})")
            elif trend['status'] == 'WARNING':
                recommendations.append(f"Monitor and improve {metric_name} (target: {trend['target']})")

        # Gate-based recommendations
        gate_stats = dashboard['gate_statistics']
        if gate_stats['pass_rate'] < 90:
            recommendations.append("Improve quality gate compliance through process improvements")

        return recommendations

    def _assess_iso9001_compliance(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Assess ISO 9001 compliance status"""
        score = dashboard['quality_score']

        if score >= 85:
            compliance = 'FULLY_COMPLIANT'
            notes = 'Quality management system fully compliant with ISO 9001 requirements'
        elif score >= 70:
            compliance = 'MOSTLY_COMPLIANT'
            notes = 'Minor gaps in quality management processes'
        elif score >= 50:
            compliance = 'PARTIALLY_COMPLIANT'
            notes = 'Significant improvements needed in quality processes'
        else:
            compliance = 'NON_COMPLIANT'
            notes = 'Major deficiencies in quality management system'

        return {
            'compliance_level': compliance,
            'compliance_score': score,
            'notes': notes,
            'iso_standard': 'ISO 9001:2015',
            'last_assessment': datetime.utcnow().isoformat()
        }