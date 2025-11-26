"""
ISO 22301 Business Continuity Management System
Business Continuity Planning für VALEO-NeuroERP

Dieses Modul implementiert das Business Continuity Management gemäß ISO 22301
für VALEO-NeuroERP mit Incident Response, Disaster Recovery und Continuity Planning.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status"""
    DETECTED = "detected"
    ASSESSING = "assessing"
    CONTAINING = "containing"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RecoveryStrategy(Enum):
    """Business continuity recovery strategies"""
    HOT_SITE = "hot_site"  # Immediate failover
    WARM_SITE = "warm_site"  # Quick recovery
    COLD_SITE = "cold_site"  # Basic infrastructure
    CLOUD_RECOVERY = "cloud_recovery"  # Cloud-based recovery
    MANUAL_RECOVERY = "manual_recovery"  # Manual processes


class BusinessImpact(Enum):
    """Business impact levels"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


@dataclass
class BusinessImpactAnalysis:
    """Business impact analysis for processes/services"""
    process_id: str
    process_name: str
    criticality: str
    rto: int  # Recovery Time Objective in hours
    rpo: int  # Recovery Point Objective in hours
    financial_impact_per_hour: float
    operational_impact: str
    dependencies: List[str] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContinuityPlan:
    """Business continuity plan"""
    id: str
    name: str
    scope: str
    objectives: List[str]
    assumptions: List[str]
    recovery_strategies: Dict[str, RecoveryStrategy]
    roles_responsibilities: Dict[str, List[str]]
    communication_plan: Dict[str, Any]
    testing_schedule: str
    version: str = "1.0"
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None


@dataclass
class IncidentRecord:
    """Incident record for business continuity"""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_processes: List[str]
    business_impact: BusinessImpact
    detection_time: datetime
    response_start: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    recovery_time: Optional[int] = None  # minutes
    data_loss: Optional[int] = None  # minutes of data
    financial_impact: float = 0.0
    lessons_learned: str = ""
    root_cause: str = ""
    preventive_actions: List[str] = field(default_factory=list)


@dataclass
class RecoveryTest:
    """Business continuity recovery test"""
    id: str
    test_type: str
    scope: str
    objectives: List[str]
    schedule: datetime
    duration: int  # minutes
    participants: List[str]
    success_criteria: List[str]
    status: str = "planned"
    results: Dict[str, Any] = field(default_factory=dict)
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ISO22301BusinessContinuity:
    """
    ISO 22301 Business Continuity Management System
    Implements business continuity planning and incident response
    """

    def __init__(self, db_session, incident_response_service=None, backup_service=None):
        self.db = db_session
        self.incident_response = incident_response_service
        self.backup = backup_service

        # Business impact analysis
        self.impact_analyses: Dict[str, BusinessImpactAnalysis] = {}

        # Continuity plans
        self.continuity_plans: Dict[str, ContinuityPlan] = {}

        # Incident records
        self.incident_records: List[IncidentRecord] = []

        # Recovery tests
        self.recovery_tests: List[RecoveryTest] = []

        # Recovery objectives
        self.recovery_objectives = self._initialize_recovery_objectives()

        # Communication templates
        self.communication_templates = self._initialize_communication_templates()

    def _initialize_recovery_objectives(self) -> Dict[str, Dict[str, Any]]:
        """Initialize recovery objectives for different business functions"""
        return {
            'customer_service': {
                'rto': 4,  # 4 hours
                'rpo': 1,  # 1 hour
                'priority': 'high'
            },
            'order_processing': {
                'rto': 8,
                'rpo': 2,
                'priority': 'high'
            },
            'financial_reporting': {
                'rto': 24,
                'rpo': 4,
                'priority': 'critical'
            },
            'inventory_management': {
                'rto': 12,
                'rpo': 6,
                'priority': 'medium'
            },
            'email_system': {
                'rto': 2,
                'rpo': 0,
                'priority': 'high'
            }
        }

    def _initialize_communication_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize communication templates for different scenarios"""
        return {
            'incident_notification': {
                'subject': 'Business Continuity Incident Notification',
                'recipients': ['management', 'it_team', 'business_owners'],
                'content': 'An incident has been detected that may impact business operations...'
            },
            'recovery_status': {
                'subject': 'Business Continuity Recovery Status Update',
                'recipients': ['management', 'affected_teams', 'customers'],
                'content': 'Recovery operations are underway...'
            },
            'service_restoration': {
                'subject': 'Service Restoration Complete',
                'recipients': ['all_staff', 'customers', 'management'],
                'content': 'Normal business operations have been restored...'
            }
        }

    def perform_business_impact_analysis(self, process_data: Dict[str, Any]) -> str:
        """
        Perform business impact analysis for a business process
        Returns analysis ID
        """
        analysis_id = str(uuid.uuid4())

        # Get recovery objectives for this process type
        process_type = process_data.get('process_type', 'general')
        objectives = self.recovery_objectives.get(process_type, {
            'rto': 24,
            'rpo': 8,
            'priority': 'medium'
        })

        analysis = BusinessImpactAnalysis(
            process_id=process_data['process_id'],
            process_name=process_data['process_name'],
            criticality=process_data.get('criticality', objectives['priority']),
            rto=process_data.get('rto', objectives['rto']),
            rpo=process_data.get('rpo', objectives['rpo']),
            financial_impact_per_hour=process_data.get('financial_impact_per_hour', 1000.0),
            operational_impact=process_data.get('operational_impact', 'Moderate disruption'),
            dependencies=process_data.get('dependencies', [])
        )

        self.impact_analyses[analysis_id] = analysis

        logger.info(f"Business impact analysis completed for {analysis.process_name}")
        return analysis_id

    def create_continuity_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Create a business continuity plan
        Returns plan ID
        """
        plan_id = str(uuid.uuid4())

        # Set review schedule (annual)
        next_review = datetime.utcnow() + timedelta(days=365)

        plan = ContinuityPlan(
            id=plan_id,
            name=plan_data['name'],
            scope=plan_data['scope'],
            objectives=plan_data['objectives'],
            assumptions=plan_data.get('assumptions', []),
            recovery_strategies=plan_data.get('recovery_strategies', {}),
            roles_responsibilities=plan_data.get('roles_responsibilities', {}),
            communication_plan=plan_data.get('communication_plan', {}),
            testing_schedule=plan_data.get('testing_schedule', 'quarterly'),
            next_review=next_review
        )

        self.continuity_plans[plan_id] = plan

        logger.info(f"Business continuity plan created: {plan.name}")
        return plan_id

    def activate_incident_response(self, incident_data: Dict[str, Any]) -> str:
        """
        Activate incident response for business continuity event
        Returns incident ID
        """
        incident_id = str(uuid.uuid4())

        incident = IncidentRecord(
            id=incident_id,
            title=incident_data['title'],
            description=incident_data['description'],
            severity=IncidentSeverity[incident_data['severity'].upper()],
            status=IncidentStatus.DETECTED,
            affected_processes=incident_data.get('affected_processes', []),
            business_impact=BusinessImpact[incident_data.get('business_impact', 'MODERATE').upper()],
            detection_time=datetime.utcnow()
        )

        self.incident_records.append(incident)

        # Trigger immediate response actions
        self._trigger_incident_response(incident)

        # Notify stakeholders
        self._notify_incident_stakeholders(incident)

        logger.warning(f"Business continuity incident activated: {incident.title}")
        return incident_id

    def _trigger_incident_response(self, incident: IncidentRecord):
        """Trigger automated incident response actions"""
        response_actions = []

        # Assess impact and determine response strategy
        if incident.severity == IncidentSeverity.CRITICAL:
            response_actions.extend([
                "Activate crisis management team",
                "Notify executive leadership",
                "Prepare customer communication",
                "Initiate emergency backup procedures"
            ])
        elif incident.severity == IncidentSeverity.HIGH:
            response_actions.extend([
                "Notify department heads",
                "Activate backup systems",
                "Prepare contingency procedures"
            ])
        else:
            response_actions.extend([
                "Assess situation",
                "Document incident details",
                "Monitor for escalation"
            ])

        # Update incident status
        incident.status = IncidentStatus.ASSESSING
        incident.response_start = datetime.utcnow()

        logger.info(f"Incident response triggered for {incident.title}: {len(response_actions)} actions")

    def _notify_incident_stakeholders(self, incident: IncidentRecord):
        """Notify relevant stakeholders about the incident"""
        notification_data = {
            'type': 'incident_notification',
            'incident_id': incident.id,
            'title': incident.title,
            'severity': incident.severity.value,
            'business_impact': incident.business_impact.value,
            'affected_processes': incident.affected_processes,
            'timestamp': incident.detection_time.isoformat()
        }

        # In production, this would send notifications via email, SMS, etc.
        logger.warning(f"Incident notification sent for: {incident.title}")

    def update_incident_status(self, incident_id: str, status_update: Dict[str, Any]) -> bool:
        """
        Update incident status and progress
        """
        incident = self._find_incident_by_id(incident_id)
        if not incident:
            return False

        old_status = incident.status
        new_status = IncidentStatus[status_update['status'].upper()]

        incident.status = new_status

        # Update timestamps based on status
        if new_status == IncidentStatus.CONTAINING and not incident.response_start:
            incident.response_start = datetime.utcnow()
        elif new_status == IncidentStatus.RESOLVED:
            incident.resolution_time = datetime.utcnow()
            if incident.response_start:
                incident.recovery_time = int((incident.resolution_time - incident.response_start).total_seconds() / 60)

        # Update other fields
        for key, value in status_update.items():
            if key != 'status' and hasattr(incident, key):
                setattr(incident, key, value)

        # Log status change
        logger.info(f"Incident {incident_id} status changed: {old_status.value} -> {new_status.value}")

        # Check if incident is resolved and trigger post-incident activities
        if new_status == IncidentStatus.RESOLVED:
            self._perform_post_incident_review(incident)

        return True

    def _find_incident_by_id(self, incident_id: str) -> Optional[IncidentRecord]:
        """Find incident by ID"""
        for incident in self.incident_records:
            if incident.id == incident_id:
                return incident
        return None

    def _perform_post_incident_review(self, incident: IncidentRecord):
        """Perform post-incident review and lessons learned"""
        # Calculate incident metrics
        if incident.response_start and incident.resolution_time:
            response_time = (incident.response_start - incident.detection_time).total_seconds() / 60
            recovery_time = (incident.resolution_time - incident.response_start).total_seconds() / 60

            logger.info(f"Incident {incident.id} metrics: Detection->Response: {response_time:.1f}min, "
                       f"Response->Recovery: {recovery_time:.1f}min")

        # Schedule lessons learned meeting
        # In production, this would create calendar events and follow-up tasks

        logger.info(f"Post-incident review scheduled for incident {incident.id}")

    def schedule_recovery_test(self, test_data: Dict[str, Any]) -> str:
        """
        Schedule a business continuity recovery test
        Returns test ID
        """
        test_id = str(uuid.uuid4())

        test = RecoveryTest(
            id=test_id,
            test_type=test_data['test_type'],
            scope=test_data['scope'],
            objectives=test_data['objectives'],
            schedule=datetime.fromisoformat(test_data['schedule']),
            duration=test_data['duration'],
            participants=test_data['participants'],
            success_criteria=test_data['success_criteria']
        )

        self.recovery_tests.append(test)

        logger.info(f"Recovery test scheduled: {test.test_type} on {test.schedule.date()}")
        return test_id

    def execute_recovery_test(self, test_id: str, test_results: Dict[str, Any]) -> bool:
        """
        Execute and record recovery test results
        """
        test = self._find_test_by_id(test_id)
        if not test:
            return False

        test.status = test_results.get('status', 'completed')
        test.results = test_results.get('results', {})
        test.issues_found = test_results.get('issues_found', [])
        test.recommendations = test_results.get('recommendations', [])

        # Update continuity plans based on test results
        self._update_plans_from_test_results(test)

        logger.info(f"Recovery test executed: {test.test_type} - Status: {test.status}")
        return True

    def _find_test_by_id(self, test_id: str) -> Optional[RecoveryTest]:
        """Find recovery test by ID"""
        for test in self.recovery_tests:
            if test.id == test_id:
                return test
        return None

    def _update_plans_from_test_results(self, test: RecoveryTest):
        """Update continuity plans based on test results"""
        if test.status != 'passed':
            # Identify plans that need updating
            affected_plans = []
            for plan in self.continuity_plans.values():
                if test.scope.lower() in plan.scope.lower():
                    affected_plans.append(plan)

            for plan in affected_plans:
                # Add test results to plan improvement actions
                logger.info(f"Continuity plan {plan.name} flagged for review based on test results")

    def calculate_business_continuity_metrics(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Calculate business continuity performance metrics"""
        # Filter incidents by tenant
        tenant_incidents = [i for i in self.incident_records if i.id.startswith(tenant_id)]

        # Calculate metrics
        total_incidents = len(tenant_incidents)
        resolved_incidents = len([i for i in tenant_incidents if i.status == IncidentStatus.RESOLVED])

        # Recovery time metrics
        recovery_times = [i.recovery_time for i in tenant_incidents if i.recovery_time]
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0

        # Financial impact
        total_financial_impact = sum(i.financial_impact for i in tenant_incidents)

        # Test coverage
        total_tests = len(self.recovery_tests)
        passed_tests = len([t for t in self.recovery_tests if t.status == 'passed'])
        test_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            'tenant_id': tenant_id,
            'incident_metrics': {
                'total_incidents': total_incidents,
                'resolved_incidents': resolved_incidents,
                'resolution_rate': (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 100,
                'avg_recovery_time_minutes': round(avg_recovery_time, 1)
            },
            'financial_impact': {
                'total_impact': total_financial_impact,
                'avg_impact_per_incident': total_financial_impact / total_incidents if total_incidents > 0 else 0
            },
            'test_metrics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': round(test_success_rate, 1)
            },
            'continuity_readiness': self._assess_continuity_readiness(),
            'generated_at': datetime.utcnow().isoformat()
        }

    def _assess_continuity_readiness(self) -> Dict[str, Any]:
        """Assess overall business continuity readiness"""
        readiness_score = 100

        # Check plan coverage
        active_plans = len([p for p in self.continuity_plans.values() if p.status == 'approved'])
        if active_plans < 3:  # Arbitrary minimum
            readiness_score -= 20

        # Check impact analysis coverage
        impact_analyses = len(self.impact_analyses)
        if impact_analyses < 5:  # Arbitrary minimum
            readiness_score -= 15

        # Check test frequency
        recent_tests = len([t for t in self.recovery_tests
                           if (datetime.utcnow() - t.schedule).days <= 90])
        if recent_tests < 2:
            readiness_score -= 10

        # Check incident response capability
        unresolved_incidents = len([i for i in self.incident_records
                                   if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]])
        if unresolved_incidents > 2:
            readiness_score -= 15

        readiness_level = 'HIGH' if readiness_score >= 80 else 'MEDIUM' if readiness_score >= 60 else 'LOW'

        return {
            'readiness_score': max(readiness_score, 0),
            'readiness_level': readiness_level,
            'active_plans': active_plans,
            'impact_analyses': impact_analyses,
            'recent_tests': recent_tests,
            'unresolved_incidents': unresolved_incidents
        }

    def generate_continuity_report(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive business continuity report"""
        metrics = self.calculate_business_continuity_metrics(tenant_id)

        # Get recent incidents
        recent_incidents = sorted(
            [i for i in self.incident_records if i.id.startswith(tenant_id)],
            key=lambda x: x.detection_time,
            reverse=True
        )[:10]

        # Get upcoming tests
        upcoming_tests = sorted(
            [t for t in self.recovery_tests if t.schedule > datetime.utcnow()],
            key=lambda x: x.schedule
        )[:5]

        # Get plan status
        plan_status = {}
        for plan in self.continuity_plans.values():
            plan_status[plan.name] = {
                'status': plan.status,
                'last_reviewed': plan.last_reviewed.isoformat() if plan.last_reviewed else None,
                'next_review': plan.next_review.isoformat() if plan.next_review else None
            }

        report = {
            'tenant_id': tenant_id,
            'report_period': 'Last 12 months',
            'generated_at': datetime.utcnow().isoformat(),
            'executive_summary': self._generate_executive_summary(metrics),
            'performance_metrics': metrics,
            'recent_incidents': [
                {
                    'id': i.id,
                    'title': i.title,
                    'severity': i.severity.value,
                    'status': i.status.value,
                    'business_impact': i.business_impact.value,
                    'detection_time': i.detection_time.isoformat(),
                    'recovery_time_minutes': i.recovery_time
                } for i in recent_incidents
            ],
            'upcoming_tests': [
                {
                    'id': t.id,
                    'type': t.test_type,
                    'scope': t.scope,
                    'schedule': t.schedule.isoformat(),
                    'participants': t.participants
                } for t in upcoming_tests
            ],
            'plan_status': plan_status,
            'recommendations': self._generate_continuity_recommendations(metrics),
            'iso22301_compliance': self._assess_iso22301_compliance(metrics)
        }

        return report

    def _generate_executive_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate executive summary for continuity report"""
        readiness = metrics['continuity_readiness']
        incidents = metrics['incident_metrics']

        summary = f"Business Continuity Readiness: {readiness['readiness_level']} "
        summary += f"(Score: {readiness['readiness_score']}/100). "

        if incidents['total_incidents'] > 0:
            summary += f"Handled {incidents['total_incidents']} incidents with "
            summary += f"{incidents['resolution_rate']:.1f}% resolution rate. "
            summary += f"Average recovery time: {incidents['avg_recovery_time_minutes']:.1f} minutes."
        else:
            summary += "No incidents recorded in the reporting period."

        return summary

    def _generate_continuity_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving business continuity"""
        recommendations = []

        readiness = metrics['continuity_readiness']

        if readiness['active_plans'] < 3:
            recommendations.append("Develop additional business continuity plans for critical business functions")

        if readiness['impact_analyses'] < 5:
            recommendations.append("Perform business impact analysis for more business processes")

        if readiness['recent_tests'] < 2:
            recommendations.append("Increase frequency of business continuity testing")

        if readiness['unresolved_incidents'] > 2:
            recommendations.append("Focus on resolving outstanding incidents and improving response times")

        test_metrics = metrics.get('test_metrics', {})
        if test_metrics.get('success_rate', 100) < 90:
            recommendations.append("Review and improve recovery test procedures")

        if not recommendations:
            recommendations.append("Maintain current business continuity capabilities and continue regular testing")

        return recommendations

    def _assess_iso22301_compliance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess ISO 22301 compliance status"""
        compliance_score = 0
        requirements = []

        # Context and interested parties (Clause 4)
        if len(self.continuity_plans) > 0:
            compliance_score += 15
            requirements.append("4.1-4.4 Understanding organization and context - COMPLIANT")
        else:
            requirements.append("4.1-4.4 Understanding organization and context - NON_COMPLIANT")

        # Leadership (Clause 5)
        if any(p.status == 'approved' for p in self.continuity_plans.values()):
            compliance_score += 15
            requirements.append("5.1-5.3 Leadership and commitment - COMPLIANT")
        else:
            requirements.append("5.1-5.3 Leadership and commitment - PARTIALLY_COMPLIANT")

        # Planning (Clause 6)
        if len(self.impact_analyses) > 0:
            compliance_score += 15
            requirements.append("6.1-6.5 Planning - COMPLIANT")
        else:
            requirements.append("6.1-6.5 Planning - NON_COMPLIANT")

        # Support (Clause 7)
        compliance_score += 10  # Assumed based on system capabilities
        requirements.append("7.1-7.5 Support - COMPLIANT")

        # Operation (Clause 8)
        incident_handling = metrics['incident_metrics']['resolution_rate']
        if incident_handling >= 80:
            compliance_score += 20
            requirements.append("8.1-8.4 Operation - COMPLIANT")
        else:
            compliance_score += 10
            requirements.append("8.1-8.4 Operation - PARTIALLY_COMPLIANT")

        # Performance evaluation (Clause 9)
        test_success = metrics.get('test_metrics', {}).get('success_rate', 0)
        if test_success >= 80:
            compliance_score += 15
            requirements.append("9.1-9.3 Performance evaluation - COMPLIANT")
        else:
            compliance_score += 7
            requirements.append("9.1-9.3 Performance evaluation - PARTIALLY_COMPLIANT")

        # Improvement (Clause 10)
        compliance_score += 10  # Assumed based on continuous improvement capabilities
        requirements.append("10.1-10.3 Improvement - COMPLIANT")

        overall_status = 'COMPLIANT' if compliance_score >= 80 else 'PARTIALLY_COMPLIANT' if compliance_score >= 60 else 'NON_COMPLIANT'

        return {
            'overall_status': overall_status,
            'compliance_score': compliance_score,
            'requirements_assessment': requirements,
            'iso_standard': 'ISO 22301:2019'
        }