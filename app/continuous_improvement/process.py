"""
ISO 9001 Continuous Improvement Process
Quality Management System Continuous Improvement

Dieses Modul implementiert den Continuous Improvement Process gemäß ISO 9001
für VALEO-NeuroERP mit Process Performance Monitoring, Quality Metrics und Management Review.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ImprovementType(Enum):
    """Types of continuous improvements"""
    CORRECTIVE_ACTION = "corrective_action"
    PREVENTIVE_ACTION = "preventive_action"
    PROCESS_OPTIMIZATION = "process_optimization"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement"
    COMPLIANCE_ENHANCEMENT = "compliance_enhancement"


class ImprovementStatus(Enum):
    """Improvement initiative status"""
    IDENTIFIED = "identified"
    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Types of quality metrics"""
    PROCESS_PERFORMANCE = "process_performance"
    QUALITY_INDICATOR = "quality_indicator"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    COMPLIANCE_METRIC = "compliance_metric"
    EFFICIENCY_METRIC = "efficiency_metric"
    RISK_METRIC = "risk_metric"


class ReviewFrequency(Enum):
    """Management review frequencies"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BIANNUAL = "biannual"
    ANNUAL = "annual"


@dataclass
class QualityMetric:
    """Quality metric definition"""
    id: str
    name: str
    description: str
    metric_type: MetricType
    target_value: float
    unit: str
    data_source: str
    collection_frequency: str
    responsible_party: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MetricMeasurement:
    """Quality metric measurement"""
    id: str
    metric_id: str
    measured_value: float
    target_value: float
    measurement_date: datetime
    notes: str = ""
    measured_by: str = ""


@dataclass
class ImprovementInitiative:
    """Continuous improvement initiative"""
    id: str
    title: str
    description: str
    improvement_type: ImprovementType
    status: ImprovementStatus
    priority: str
    root_cause: str
    proposed_solution: str
    expected_benefits: List[str]
    required_resources: List[str]
    responsible_party: str
    target_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    success_criteria: List[str]
    verification_method: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ManagementReview:
    """Management review meeting"""
    id: str
    review_period: str
    review_date: datetime
    participants: List[str]
    agenda_items: List[Dict[str, Any]]
    decisions_made: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    next_review_date: datetime
    status: str = "completed"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CorrectiveAction:
    """Corrective action record"""
    id: str
    nonconformity_id: str
    description: str
    root_cause: str
    corrective_actions: List[str]
    preventive_actions: List[str]
    responsible_party: str
    target_completion_date: datetime
    verification_date: Optional[datetime] = None
    effectiveness_check_date: Optional[datetime] = None
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessPerformance:
    """Process performance indicator"""
    id: str
    process_name: str
    performance_metric: str
    current_value: float
    target_value: float
    trend: str  # improving, stable, declining
    last_updated: datetime
    responsible_party: str
    action_required: bool = False
    action_description: str = ""


class ISO9001ContinuousImprovement:
    """
    ISO 9001 Continuous Improvement Process
    Implements quality management continuous improvement
    """

    def __init__(self, db_session, quality_service=None, audit_service=None):
        self.db = db_session
        self.quality = quality_service
        self.audit = audit_service

        # Improvement management
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.metric_measurements: List[MetricMeasurement] = {}
        self.improvement_initiatives: Dict[str, ImprovementInitiative] = {}
        self.management_reviews: List[ManagementReview] = {}
        self.corrective_actions: Dict[str, CorrectiveAction] = {}
        self.process_performance: Dict[str, ProcessPerformance] = {}

        # Improvement configuration
        self.improvement_config = self._initialize_improvement_config()

        # Quality objectives
        self.quality_objectives = self._initialize_quality_objectives()

    def _initialize_improvement_config(self) -> Dict[str, Any]:
        """Initialize continuous improvement configuration"""
        return {
            'review_frequencies': {
                'management_review': ReviewFrequency.QUARTERLY,
                'metric_collection': 'monthly',
                'improvement_tracking': 'weekly'
            },
            'improvement_priorities': {
                'critical': {'sla_days': 7, 'resources': 'unlimited'},
                'high': {'sla_days': 30, 'resources': 'dedicated'},
                'medium': {'sla_days': 90, 'resources': 'shared'},
                'low': {'sla_days': 180, 'resources': 'as_available'}
            },
            'quality_gates': {
                'metric_deviation_threshold': 0.1,  # 10% deviation triggers review
                'improvement_success_rate_target': 0.8,  # 80% success rate
                'review_completion_target': 0.95  # 95% of reviews completed on time
            },
            'stakeholder_engagement': {
                'management_involvement': True,
                'employee_participation': True,
                'customer_feedback_integration': True,
                'supplier_collaboration': False
            }
        }

    def _initialize_quality_objectives(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality objectives"""
        return {
            'customer_satisfaction': {
                'target': 95.0,
                'unit': 'percentage',
                'measurement_method': 'survey',
                'frequency': 'quarterly'
            },
            'process_efficiency': {
                'target': 90.0,
                'unit': 'percentage',
                'measurement_method': 'performance_metrics',
                'frequency': 'monthly'
            },
            'quality_incident_rate': {
                'target': 0.5,
                'unit': 'incidents_per_month',
                'measurement_method': 'incident_tracking',
                'frequency': 'monthly'
            },
            'compliance_rate': {
                'target': 98.0,
                'unit': 'percentage',
                'measurement_method': 'audit_results',
                'frequency': 'quarterly'
            },
            'improvement_completion_rate': {
                'target': 85.0,
                'unit': 'percentage',
                'measurement_method': 'initiative_tracking',
                'frequency': 'monthly'
            }
        }

    def create_quality_metric(self, metric_data: Dict[str, Any]) -> str:
        """
        Create a quality metric
        Returns metric ID
        """
        metric_id = str(uuid.uuid4())

        metric = QualityMetric(
            id=metric_id,
            name=metric_data['name'],
            description=metric_data['description'],
            metric_type=MetricType[metric_data['metric_type'].upper()],
            target_value=metric_data['target_value'],
            unit=metric_data['unit'],
            data_source=metric_data['data_source'],
            collection_frequency=metric_data['collection_frequency'],
            responsible_party=metric_data['responsible_party']
        )

        self.quality_metrics[metric_id] = metric

        logger.info(f"Quality metric created: {metric.name} ({metric.metric_type.value})")
        return metric_id

    def record_metric_measurement(self, measurement_data: Dict[str, Any]) -> str:
        """
        Record a metric measurement
        Returns measurement ID
        """
        measurement_id = str(uuid.uuid4())

        measurement = MetricMeasurement(
            id=measurement_id,
            metric_id=measurement_data['metric_id'],
            measured_value=measurement_data['measured_value'],
            target_value=measurement_data['target_value'],
            measurement_date=datetime.utcnow(),
            notes=measurement_data.get('notes', ''),
            measured_by=measurement_data.get('measured_by', 'system')
        )

        if measurement_id not in self.metric_measurements:
            self.metric_measurements[measurement_id] = []

        self.metric_measurements[measurement_id].append(measurement)

        # Check for significant deviations
        self._check_metric_deviation(measurement)

        logger.info(f"Metric measurement recorded: {measurement.measured_value} for metric {measurement.metric_id}")
        return measurement_id

    def _check_metric_deviation(self, measurement: MetricMeasurement):
        """Check for significant metric deviations"""
        deviation_threshold = self.improvement_config['quality_gates']['metric_deviation_threshold']

        if measurement.target_value > 0:
            deviation = abs(measurement.measured_value - measurement.target_value) / measurement.target_value

            if deviation > deviation_threshold:
                # Create improvement initiative for metric deviation
                initiative_data = {
                    'title': f"Metric Deviation: {measurement.metric_id}",
                    'description': f"Metric {measurement.metric_id} deviated by {deviation:.1%} from target",
                    'improvement_type': 'PROCESS_OPTIMIZATION',
                    'priority': 'high',
                    'root_cause': 'Performance deviation from target',
                    'proposed_solution': 'Investigate root cause and implement corrective actions',
                    'expected_benefits': ['Improved process performance', 'Better quality control'],
                    'required_resources': ['Process owner', 'Quality team'],
                    'responsible_party': 'Quality Manager',
                    'target_completion_date': datetime.utcnow() + timedelta(days=30),
                    'success_criteria': ['Metric returns to target range', 'Root cause identified'],
                    'verification_method': 'Metric monitoring and trend analysis'
                }

                self.create_improvement_initiative(initiative_data)

    def create_improvement_initiative(self, initiative_data: Dict[str, Any]) -> str:
        """
        Create an improvement initiative
        Returns initiative ID
        """
        initiative_id = str(uuid.uuid4())

        initiative = ImprovementInitiative(
            id=initiative_id,
            title=initiative_data['title'],
            description=initiative_data['description'],
            improvement_type=ImprovementType[initiative_data['improvement_type'].upper()],
            status=ImprovementStatus.IDENTIFIED,
            priority=initiative_data['priority'],
            root_cause=initiative_data['root_cause'],
            proposed_solution=initiative_data['proposed_solution'],
            expected_benefits=initiative_data.get('expected_benefits', []),
            required_resources=initiative_data.get('required_resources', []),
            responsible_party=initiative_data['responsible_party'],
            target_completion_date=initiative_data['target_completion_date'],
            success_criteria=initiative_data.get('success_criteria', []),
            verification_method=initiative_data.get('verification_method', 'Management review')
        )

        self.improvement_initiatives[initiative_id] = initiative

        logger.info(f"Improvement initiative created: {initiative.title} ({initiative.improvement_type.value})")
        return initiative_id

    def update_improvement_status(self, initiative_id: str, new_status: str, notes: str = "") -> bool:
        """
        Update improvement initiative status
        """
        if initiative_id not in self.improvement_initiatives:
            return False

        initiative = self.improvement_initiatives[initiative_id]
        old_status = initiative.status

        initiative.status = ImprovementStatus[new_status.upper()]
        initiative.updated_at = datetime.utcnow()

        if new_status.upper() == 'IMPLEMENTED':
            initiative.actual_completion_date = datetime.utcnow()

        logger.info(f"Improvement initiative {initiative_id} status changed: {old_status.value} -> {new_status}")
        return True

    def create_corrective_action(self, action_data: Dict[str, Any]) -> str:
        """
        Create a corrective action
        Returns action ID
        """
        action_id = str(uuid.uuid4())

        action = CorrectiveAction(
            id=action_id,
            nonconformity_id=action_data['nonconformity_id'],
            description=action_data['description'],
            root_cause=action_data['root_cause'],
            corrective_actions=action_data.get('corrective_actions', []),
            preventive_actions=action_data.get('preventive_actions', []),
            responsible_party=action_data['responsible_party'],
            target_completion_date=action_data['target_completion_date']
        )

        self.corrective_actions[action_id] = action

        logger.info(f"Corrective action created for nonconformity: {action.nonconformity_id}")
        return action_id

    def conduct_management_review(self, review_data: Dict[str, Any]) -> str:
        """
        Conduct a management review
        Returns review ID
        """
        review_id = str(uuid.uuid4())

        review = ManagementReview(
            id=review_id,
            review_period=review_data['review_period'],
            review_date=datetime.utcnow(),
            participants=review_data['participants'],
            agenda_items=review_data.get('agenda_items', []),
            decisions_made=review_data.get('decisions_made', []),
            action_items=review_data.get('action_items', []),
            next_review_date=review_data['next_review_date']
        )

        self.management_reviews.append(review)

        # Process action items from review
        for action_item in review.action_items:
            if action_item.get('type') == 'improvement_initiative':
                self.create_improvement_initiative(action_item)

        logger.info(f"Management review conducted: {review.review_period}")
        return review_id

    def update_process_performance(self, performance_data: Dict[str, Any]) -> str:
        """
        Update process performance indicator
        Returns performance ID
        """
        process_name = performance_data['process_name']
        performance_id = f"{process_name}_{datetime.utcnow().strftime('%Y%m')}"

        performance = ProcessPerformance(
            id=performance_id,
            process_name=process_name,
            performance_metric=performance_data['performance_metric'],
            current_value=performance_data['current_value'],
            target_value=performance_data['target_value'],
            trend=performance_data.get('trend', 'stable'),
            last_updated=datetime.utcnow(),
            responsible_party=performance_data['responsible_party'],
            action_required=performance_data.get('action_required', False),
            action_description=performance_data.get('action_description', '')
        )

        self.process_performance[performance_id] = performance

        # Check if action is required
        if performance.action_required:
            initiative_data = {
                'title': f"Process Performance: {process_name}",
                'description': performance.action_description,
                'improvement_type': 'PROCESS_OPTIMIZATION',
                'priority': 'medium',
                'root_cause': 'Process performance below target',
                'proposed_solution': 'Implement process improvements',
                'expected_benefits': ['Improved process efficiency', 'Better quality outcomes'],
                'required_resources': ['Process owner', 'Quality team'],
                'responsible_party': performance.responsible_party,
                'target_completion_date': datetime.utcnow() + timedelta(days=60),
                'success_criteria': ['Process performance meets target', 'Sustainable improvement'],
                'verification_method': 'Performance metric monitoring'
            }

            self.create_improvement_initiative(initiative_data)

        logger.info(f"Process performance updated: {process_name} - {performance.current_value}")
        return performance_id

    def get_improvement_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive improvement dashboard"""
        # Filter data by tenant
        tenant_metrics = [m for m in self.quality_metrics.values() if m.id.startswith(tenant_id)]
        tenant_initiatives = [i for i in self.improvement_initiatives.values() if i.id.startswith(tenant_id)]
        tenant_reviews = [r for r in self.management_reviews if r.id.startswith(tenant_id)]
        tenant_actions = [a for a in self.corrective_actions.values() if a.id.startswith(tenant_id)]

        # Calculate metrics
        metric_performance = self._calculate_metric_performance(tenant_metrics)
        initiative_progress = self._calculate_initiative_progress(tenant_initiatives)
        review_compliance = self._calculate_review_compliance(tenant_reviews)
        action_effectiveness = self._calculate_action_effectiveness(tenant_actions)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'metric_performance': metric_performance,
            'initiative_progress': initiative_progress,
            'review_compliance': review_compliance,
            'action_effectiveness': action_effectiveness,
            'quality_objectives_status': self._assess_quality_objectives(),
            'active_alerts': self._get_improvement_alerts(tenant_id)
        }

    def _calculate_metric_performance(self, metrics: List[QualityMetric]) -> Dict[str, Any]:
        """Calculate quality metric performance"""
        if not metrics:
            return {'total_metrics': 0, 'on_target': 0, 'deviation_rate': 0}

        total_metrics = len(metrics)
        on_target = 0
        total_deviation = 0

        for metric in metrics:
            # Get latest measurement
            measurements = [m for m_list in self.metric_measurements.values()
                          for m in m_list if m.metric_id == metric.id]
            if measurements:
                latest = max(measurements, key=lambda x: x.measurement_date)
                if abs(latest.measured_value - latest.target_value) / latest.target_value <= 0.1:
                    on_target += 1
                total_deviation += abs(latest.measured_value - latest.target_value) / latest.target_value

        deviation_rate = total_deviation / total_metrics if total_metrics > 0 else 0

        return {
            'total_metrics': total_metrics,
            'on_target_metrics': on_target,
            'target_achievement_rate': (on_target / total_metrics * 100) if total_metrics > 0 else 0,
            'average_deviation': deviation_rate * 100
        }

    def _calculate_initiative_progress(self, initiatives: List[ImprovementInitiative]) -> Dict[str, Any]:
        """Calculate improvement initiative progress"""
        if not initiatives:
            return {'total_initiatives': 0, 'completed': 0, 'on_track': 0}

        total = len(initiatives)
        completed = len([i for i in initiatives if i.status == ImprovementStatus.CLOSED])
        on_track = len([i for i in initiatives if i.target_completion_date and
                       i.target_completion_date > datetime.utcnow()])

        completion_rate = (completed / total * 100) if total > 0 else 0

        # Calculate by type
        by_type = {}
        for initiative in initiatives:
            type_key = initiative.improvement_type.value
            by_type[type_key] = by_type.get(type_key, {'total': 0, 'completed': 0})
            by_type[type_key]['total'] += 1
            if initiative.status == ImprovementStatus.CLOSED:
                by_type[type_key]['completed'] += 1

        return {
            'total_initiatives': total,
            'completed_initiatives': completed,
            'completion_rate': completion_rate,
            'on_track_initiatives': on_track,
            'by_improvement_type': by_type
        }

    def _calculate_review_compliance(self, reviews: List[ManagementReview]) -> Dict[str, Any]:
        """Calculate management review compliance"""
        if not reviews:
            return {'total_reviews': 0, 'on_time_completion': 0}

        total = len(reviews)
        on_time = len([r for r in reviews if r.status == 'completed'])

        compliance_rate = (on_time / total * 100) if total > 0 else 0

        return {
            'total_reviews': total,
            'completed_reviews': on_time,
            'compliance_rate': compliance_rate,
            'average_action_items': self._calculate_average_action_items(reviews)
        }

    def _calculate_average_action_items(self, reviews: List[ManagementReview]) -> float:
        """Calculate average action items per review"""
        if not reviews:
            return 0

        total_actions = sum(len(r.action_items) for r in reviews)
        return total_actions / len(reviews)

    def _calculate_action_effectiveness(self, actions: List[CorrectiveAction]) -> Dict[str, Any]:
        """Calculate corrective action effectiveness"""
        if not actions:
            return {'total_actions': 0, 'effective_actions': 0}

        total = len(actions)
        effective = len([a for a in actions if a.status == 'closed' and a.effectiveness_check_date])

        effectiveness_rate = (effective / total * 100) if total > 0 else 0

        return {
            'total_actions': total,
            'effective_actions': effective,
            'effectiveness_rate': effectiveness_rate,
            'average_resolution_days': self._calculate_average_resolution_days(actions)
        }

    def _calculate_average_resolution_days(self, actions: List[CorrectiveAction]) -> float:
        """Calculate average resolution time for actions"""
        resolved_actions = [a for a in actions if a.verification_date]
        if not resolved_actions:
            return 0

        resolution_times = [
            (a.verification_date - a.created_at).days
            for a in resolved_actions
        ]

        return sum(resolution_times) / len(resolution_times)

    def _assess_quality_objectives(self) -> Dict[str, Any]:
        """Assess quality objectives achievement"""
        objectives_status = {}

        for obj_name, objective in self.quality_objectives.items():
            # Get latest measurements for this objective
            # This is a simplified implementation
            current_value = 85.0  # Placeholder - would be calculated from actual data
            target = objective['target']

            status = 'achieved' if current_value >= target else 'not_achieved'
            gap = target - current_value

            objectives_status[obj_name] = {
                'target': target,
                'current': current_value,
                'status': status,
                'gap': gap,
                'unit': objective['unit']
            }

        overall_achievement = len([o for o in objectives_status.values() if o['status'] == 'achieved']) / len(objectives_status) * 100

        return {
            'objectives': objectives_status,
            'overall_achievement_rate': overall_achievement,
            'objectives_met': len([o for o in objectives_status.values() if o['status'] == 'achieved']),
            'total_objectives': len(objectives_status)
        }

    def _get_improvement_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active improvement alerts"""
        alerts = []

        # Check for overdue initiatives
        overdue_initiatives = [
            i for i in self.improvement_initiatives.values()
            if i.id.startswith(tenant_id) and i.status != ImprovementStatus.CLOSED and
            i.target_completion_date and i.target_completion_date < datetime.utcnow()
        ]

        if overdue_initiatives:
            alerts.append({
                'type': 'overdue_initiatives',
                'severity': 'HIGH',
                'message': f"{len(overdue_initiatives)} improvement initiatives are overdue",
                'details': {'overdue_count': len(overdue_initiatives)}
            })

        # Check for metric deviations
        deviated_metrics = []
        for metric in self.quality_metrics.values():
            if metric.id.startswith(tenant_id):
                measurements = [m for m_list in self.metric_measurements.values()
                              for m in m_list if m.metric_id == metric.id]
                if measurements:
                    latest = max(measurements, key=lambda x: x.measurement_date)
                    deviation = abs(latest.measured_value - latest.target_value) / latest.target_value
                    if deviation > 0.1:  # 10% deviation
                        deviated_metrics.append(metric.name)

        if deviated_metrics:
            alerts.append({
                'type': 'metric_deviations',
                'severity': 'MEDIUM',
                'message': f"{len(deviated_metrics)} quality metrics are outside acceptable range",
                'details': {'deviated_metrics': deviated_metrics}
            })

        # Check for upcoming reviews
        next_review = min([r.next_review_date for r in self.management_reviews
                          if r.next_review_date > datetime.utcnow()], default=None)
        if next_review and (next_review - datetime.utcnow()).days <= 7:
            alerts.append({
                'type': 'upcoming_review',
                'severity': 'LOW',
                'message': f"Management review due in {(next_review - datetime.utcnow()).days} days",
                'details': {'review_date': next_review.isoformat()}
            })

        return alerts

    def check_continuous_improvement_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 9001 continuous improvement compliance"""
        metrics = [m for m in self.quality_metrics.values() if m.id.startswith(tenant_id)]
        initiatives = [i for i in self.improvement_initiatives.values() if i.id.startswith(tenant_id)]
        reviews = [r for r in self.management_reviews if r.id.startswith(tenant_id)]
        actions = [a for a in self.corrective_actions.values() if a.id.startswith(tenant_id)]

        compliance_status = self._assess_improvement_compliance(metrics, initiatives, reviews, actions)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_standard': 'ISO 9001:2015',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_improvement_compliance(self, metrics: List[QualityMetric],
                                     initiatives: List[ImprovementInitiative],
                                     reviews: List[ManagementReview],
                                     actions: List[CorrectiveAction]) -> Dict[str, Any]:
        """Assess ISO 9001 continuous improvement compliance"""
        issues = []

        # Check quality metrics
        if len(metrics) < 5:
            issues.append("Insufficient quality metrics defined for comprehensive monitoring")

        # Check improvement initiatives
        if len(initiatives) < 3:
            issues.append("Limited improvement initiatives - continuous improvement not adequately demonstrated")

        # Check management reviews
        recent_reviews = [r for r in reviews if (datetime.utcnow() - r.review_date).days <= 180]
        if len(recent_reviews) < 2:
            issues.append("Insufficient management reviews conducted in the last 6 months")

        # Check corrective actions
        if len(actions) < 5:
            issues.append("Limited corrective action records - problem resolution process may be inadequate")

        # Check metric monitoring
        active_metrics = len([m for m in metrics if m.is_active])
        if active_metrics < len(metrics) * 0.8:
            issues.append("Many quality metrics are inactive - monitoring coverage insufficient")

        compliance_score = max(0, 100 - (len(issues) * 8))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_improvement_recommendations(issues)
        }

    def _generate_improvement_recommendations(self, issues: List[str]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if any('metrics' in issue.lower() for issue in issues):
            recommendations.append("Expand quality metrics coverage to include all critical processes and customer requirements")

        if any('initiatives' in issue.lower() for issue in issues):
            recommendations.append("Increase improvement initiative frequency and ensure systematic identification of improvement opportunities")

        if any('reviews' in issue.lower() for issue in issues):
            recommendations.append("Establish regular management review cadence and ensure comprehensive agenda coverage")

        if any('corrective' in issue.lower() for issue in issues):
            recommendations.append("Strengthen problem identification and resolution processes with systematic root cause analysis")

        if not recommendations:
            recommendations.append("Maintain current continuous improvement practices and consider expanding scope")

        return recommendations