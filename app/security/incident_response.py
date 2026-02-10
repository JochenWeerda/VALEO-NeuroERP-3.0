"""
ISO 27001 Incident Response Framework
Informationssicherheits-Managementsystem Incident Management

Dieses Modul implementiert das Incident Response System gemäß ISO 27001 Annex A.16.1
für VALEO-NeuroERP mit automatischer Detektion, Klassifizierung und Response.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels according to ISO 27001"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(Enum):
    """Incident status lifecycle"""
    DETECTED = "DETECTED"
    CLASSIFIED = "CLASSIFIED"
    CONTAINED = "CONTAINED"
    ERADICATED = "ERADICATED"
    RECOVERED = "RECOVERED"
    LESSONS_LEARNED = "LESSONS_LEARNED"
    CLOSED = "CLOSED"


class IncidentCategory(Enum):
    """Incident categories for classification"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALWARE_INFECTION = "malware_infection"
    DENIAL_OF_SERVICE = "denial_of_service"
    SYSTEM_COMPROMISE = "system_compromise"
    INSIDER_THREAT = "insider_threat"
    PHYSICAL_SECURITY = "physical_security"
    THIRD_PARTY_COMPROMISE = "third_party_compromise"
    CONFIGURATION_ERROR = "configuration_error"
    AVAILABILITY_INCIDENT = "availability_incident"


@dataclass
class Incident:
    """Security incident representation"""
    id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime
    reported_by: str
    assigned_to: Optional[str] = None
    tenant_id: str = "system"

    # Impact assessment
    affected_assets: List[str] = field(default_factory=list)
    affected_users: int = 0
    data_compromised: bool = False
    data_classification: str = "internal"

    # Response tracking
    containment_actions: List[Dict[str, Any]] = field(default_factory=list)
    eradication_actions: List[Dict[str, Any]] = field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Timeline
    contained_at: Optional[datetime] = None
    eradicated_at: Optional[datetime] = None
    recovered_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    # Communication
    stakeholders_notified: List[str] = field(default_factory=list)
    external_notifications: List[Dict[str, Any]] = field(default_factory=list)

    # Evidence and analysis
    evidence_collected: List[Dict[str, Any]] = field(default_factory=list)
    forensic_analysis: Dict[str, Any] = field(default_factory=dict)
    root_cause_analysis: str = ""

    # Lessons learned
    lessons_learned: List[str] = field(default_factory=list)
    preventive_actions: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IncidentResponsePlan:
    """Incident response plan for different incident types"""
    incident_type: IncidentCategory
    detection_methods: List[str]
    immediate_actions: List[str]
    escalation_criteria: Dict[str, Any]
    communication_plan: Dict[str, Any]
    recovery_procedures: List[str]
    preventive_measures: List[str]


class ISO27001IncidentResponse:
    """
    ISO 27001 Incident Response Framework
    Implements Annex A.16.1 - Information Security Incident Management
    """

    def __init__(self, audit_service=None, alert_service=None, notification_service=None):
        self.audit_service = audit_service
        self.alert_service = alert_service
        self.notification_service = notification_service

        # Incident tracking
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: List[Incident] = []

        # Response plans
        self.response_plans = self._initialize_response_plans()

        # Escalation matrix
        self.escalation_matrix = self._initialize_escalation_matrix()

        # SLA definitions
        self.sla_targets = {
            IncidentSeverity.LOW: timedelta(hours=4),
            IncidentSeverity.MEDIUM: timedelta(hours=2),
            IncidentSeverity.HIGH: timedelta(hours=1),
            IncidentSeverity.CRITICAL: timedelta(minutes=30)
        }

    def _initialize_response_plans(self) -> Dict[IncidentCategory, IncidentResponsePlan]:
        """Initialize response plans for different incident types"""
        return {
            IncidentCategory.UNAUTHORIZED_ACCESS: IncidentResponsePlan(
                incident_type=IncidentCategory.UNAUTHORIZED_ACCESS,
                detection_methods=["SIEM alerts", "Failed login monitoring", "Anomaly detection"],
                immediate_actions=[
                    "Block suspicious IP addresses",
                    "Force password reset for affected accounts",
                    "Enable enhanced monitoring"
                ],
                escalation_criteria={
                    "severity": "HIGH",
                    "conditions": ["Privileged account access", "Data exfiltration detected"]
                },
                communication_plan={
                    "immediate": ["Security Team"],
                    "1_hour": ["IT Management", "Legal"],
                    "4_hours": ["Executive Team"] if "privileged" in "conditions" else []
                },
                recovery_procedures=[
                    "Verify account access patterns",
                    "Review recent activities",
                    "Implement additional authentication controls"
                ],
                preventive_measures=[
                    "Implement multi-factor authentication",
                    "Regular access reviews",
                    "Enhanced logging and monitoring"
                ]
            ),

            IncidentCategory.DATA_BREACH: IncidentResponsePlan(
                incident_type=IncidentCategory.DATA_BREACH,
                detection_methods=["DLP alerts", "Anomaly detection", "User reports"],
                immediate_actions=[
                    "Isolate affected systems",
                    "Stop data exfiltration",
                    "Preserve evidence"
                ],
                escalation_criteria={
                    "severity": "CRITICAL",
                    "conditions": ["Personal data involved", "Large data volume", "External breach"]
                },
                communication_plan={
                    "immediate": ["Security Team", "Legal"],
                    "1_hour": ["Data Protection Officer", "Executive Team"],
                    "4_hours": ["Regulatory Authorities", "Affected Customers"]
                },
                recovery_procedures=[
                    "Assess data exposure scope",
                    "Notify affected parties per GDPR",
                    "Implement additional security controls"
                ],
                preventive_measures=[
                    "Enhanced data encryption",
                    "Data Loss Prevention (DLP) systems",
                    "Regular security awareness training"
                ]
            ),

            IncidentCategory.MALWARE_INFECTION: IncidentResponsePlan(
                incident_type=IncidentCategory.MALWARE_INFECTION,
                detection_methods=["Antivirus alerts", "EDR alerts", "Network monitoring"],
                immediate_actions=[
                    "Isolate infected systems",
                    "Block malicious network traffic",
                    "Initiate malware analysis"
                ],
                escalation_criteria={
                    "severity": "HIGH",
                    "conditions": ["Ransomware detected", "Data encryption occurred", "Lateral movement"]
                },
                communication_plan={
                    "immediate": ["Security Team"],
                    "1_hour": ["IT Operations", "Management"],
                    "4_hours": ["External Cybersecurity Experts"] if "ransomware" in "conditions" else []
                },
                recovery_procedures=[
                    "Clean infected systems",
                    "Restore from clean backups",
                    "Update security signatures"
                ],
                preventive_measures=[
                    "Regular security updates",
                    "Advanced endpoint protection",
                    "Network segmentation"
                ]
            )
        }

    def _initialize_escalation_matrix(self) -> Dict[IncidentSeverity, Dict[str, Any]]:
        """Initialize escalation matrix for different severity levels"""
        return {
            IncidentSeverity.LOW: {
                "response_team": ["Security Analyst"],
                "notification_delay": timedelta(hours=4),
                "management_notification": False,
                "external_notification": False
            },
            IncidentSeverity.MEDIUM: {
                "response_team": ["Security Analyst", "IT Operations"],
                "notification_delay": timedelta(hours=2),
                "management_notification": True,
                "external_notification": False
            },
            IncidentSeverity.HIGH: {
                "response_team": ["Security Team", "IT Management"],
                "notification_delay": timedelta(hours=1),
                "management_notification": True,
                "external_notification": False
            },
            IncidentSeverity.CRITICAL: {
                "response_team": ["Crisis Response Team", "Executive Management"],
                "notification_delay": timedelta(minutes=30),
                "management_notification": True,
                "external_notification": True
            }
        }

    def detect_incident(self, detection_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect and create incident from monitoring alerts
        Returns incident ID if created
        """
        # Analyze detection data
        incident_category = self._classify_detection(detection_data)
        if not incident_category:
            return None

        severity = self._assess_severity(detection_data, incident_category)

        # Create incident
        incident = Incident(
            id=str(uuid.uuid4()),
            title=detection_data.get('title', f'{incident_category.value.title()} Incident'),
            description=detection_data.get('description', 'Automatically detected security incident'),
            category=incident_category,
            severity=severity,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            reported_by='automated_detection',
            tenant_id=detection_data.get('tenant_id', 'system'),
            affected_assets=detection_data.get('affected_assets', []),
            evidence_collected=[{
                'type': 'detection_alert',
                'data': detection_data,
                'collected_at': datetime.utcnow().isoformat()
            }]
        )

        # Store incident
        self.active_incidents[incident.id] = incident

        # Log to audit
        if self.audit_service:
            self.audit_service.log_security_event({
                'event_type': 'incident_detected',
                'incident_id': incident.id,
                'category': incident.category.value,
                'severity': incident.severity.value,
                'details': detection_data
            })

        # Trigger immediate response
        self._trigger_immediate_response(incident)

        logger.warning(f"Security incident detected: {incident.id} - {incident.title}")
        return incident.id

    def _classify_detection(self, detection_data: Dict[str, Any]) -> Optional[IncidentCategory]:
        """Classify detection data into incident category"""
        detection_type = detection_data.get('type', '')

        # Classification logic based on detection type
        classification_map = {
            'failed_login': IncidentCategory.UNAUTHORIZED_ACCESS,
            'suspicious_traffic': IncidentCategory.UNAUTHORIZED_ACCESS,
            'data_exfiltration': IncidentCategory.DATA_BREACH,
            'malware_detected': IncidentCategory.MALWARE_INFECTION,
            'dos_attack': IncidentCategory.DENIAL_OF_SERVICE,
            'privilege_escalation': IncidentCategory.SYSTEM_COMPROMISE,
            'insider_activity': IncidentCategory.INSIDER_THREAT,
            'physical_breach': IncidentCategory.PHYSICAL_SECURITY,
            'third_party_compromise': IncidentCategory.THIRD_PARTY_COMPROMISE,
            'config_error': IncidentCategory.CONFIGURATION_ERROR,
            'system_down': IncidentCategory.AVAILABILITY_INCIDENT
        }

        return classification_map.get(detection_type)

    def _assess_severity(self, detection_data: Dict[str, Any], category: IncidentCategory) -> IncidentSeverity:
        """Assess incident severity based on detection data"""
        severity_score = 0

        # Base severity by category
        base_severity = {
            IncidentCategory.UNAUTHORIZED_ACCESS: 3,
            IncidentCategory.DATA_BREACH: 8,
            IncidentCategory.MALWARE_INFECTION: 6,
            IncidentCategory.DENIAL_OF_SERVICE: 5,
            IncidentCategory.SYSTEM_COMPROMISE: 9,
            IncidentCategory.INSIDER_THREAT: 7,
            IncidentCategory.PHYSICAL_SECURITY: 4,
            IncidentCategory.THIRD_PARTY_COMPROMISE: 7,
            IncidentCategory.CONFIGURATION_ERROR: 2,
            IncidentCategory.AVAILABILITY_INCIDENT: 6
        }

        severity_score = base_severity.get(category, 3)

        # Adjust based on impact indicators
        if detection_data.get('privileged_access', False):
            severity_score += 2
        if detection_data.get('data_exfiltration', False):
            severity_score += 3
        if detection_data.get('customer_impact', False):
            severity_score += 2
        if detection_data.get('financial_impact', False):
            severity_score += 2

        # Classify final severity
        if severity_score >= 10:
            return IncidentSeverity.CRITICAL
        elif severity_score >= 7:
            return IncidentSeverity.HIGH
        elif severity_score >= 4:
            return IncidentSeverity.MEDIUM
        else:
            return IncidentSeverity.LOW

    def _trigger_immediate_response(self, incident: Incident):
        """Trigger immediate response actions"""
        response_plan = self.response_plans.get(incident.category)
        if not response_plan:
            logger.error(f"No response plan for incident category: {incident.category}")
            return

        # Execute immediate actions
        for action in response_plan.immediate_actions:
            self._execute_response_action(incident, action, "immediate")

        # Assign to response team
        escalation_info = self.escalation_matrix[incident.severity]
        incident.assigned_to = escalation_info['response_team'][0]

        # Send alerts
        self._send_incident_alerts(incident, escalation_info)

    def _execute_response_action(self, incident: Incident, action: str, phase: str):
        """Execute a specific response action"""
        # Log action execution
        action_record = {
            'action': action,
            'phase': phase,
            'executed_at': datetime.utcnow().isoformat(),
            'executed_by': 'automated_system',
            'status': 'completed'  # In production, this would be actual execution result
        }

        # Add to appropriate action list
        if phase == 'immediate':
            incident.containment_actions.append(action_record)
        elif phase == 'containment':
            incident.containment_actions.append(action_record)
        elif phase == 'eradication':
            incident.eradication_actions.append(action_record)
        elif phase == 'recovery':
            incident.recovery_actions.append(action_record)

        logger.info(f"Executed response action for incident {incident.id}: {action}")

    def _send_incident_alerts(self, incident: Incident, escalation_info: Dict[str, Any]):
        """Send incident alerts to appropriate teams"""
        alert_data = {
            'incident_id': incident.id,
            'title': incident.title,
            'severity': incident.severity.value,
            'category': incident.category.value,
            'detected_at': incident.detected_at.isoformat(),
            'assigned_to': incident.assigned_to,
            'immediate_actions_taken': len(incident.containment_actions),
            'escalation_required': escalation_info['management_notification']
        }

        if self.alert_service:
            self.alert_service.send_incident_alert(alert_data)

        logger.warning(f"Incident alerts sent for {incident.id}")

    def update_incident_status(self, incident_id: str, new_status: IncidentStatus,
                             update_data: Dict[str, Any] = None) -> bool:
        """
        Update incident status and execute appropriate actions
        """
        if incident_id not in self.active_incidents:
            return False

        incident = self.active_incidents[incident_id]
        old_status = incident.status
        incident.status = new_status
        incident.updated_at = datetime.utcnow()

        # Execute status-specific actions
        if new_status == IncidentStatus.CONTAINED:
            incident.contained_at = datetime.utcnow()
            self._execute_containment_actions(incident)
        elif new_status == IncidentStatus.ERADICATED:
            incident.eradicated_at = datetime.utcnow()
            self._execute_eradication_actions(incident)
        elif new_status == IncidentStatus.RECOVERED:
            incident.recovered_at = datetime.utcnow()
            self._execute_recovery_actions(incident)
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.utcnow()
            self._close_incident(incident)

        # Update additional data
        if update_data:
            for key, value in update_data.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)

        # Log status change
        if self.audit_service:
            self.audit_service.log_security_event({
                'event_type': 'incident_status_changed',
                'incident_id': incident_id,
                'old_status': old_status.value,
                'new_status': new_status.value,
                'updated_by': update_data.get('updated_by', 'system') if update_data else 'system'
            })

        logger.info(f"Incident {incident_id} status updated: {old_status.value} -> {new_status.value}")
        return True

    def _execute_containment_actions(self, incident: Incident):
        """Execute containment actions"""
        response_plan = self.response_plans.get(incident.category)
        if response_plan:
            # Additional containment actions beyond immediate
            for action in response_plan.recovery_procedures[:2]:  # First 2 as containment
                self._execute_response_action(incident, action, "containment")

    def _execute_eradication_actions(self, incident: Incident):
        """Execute eradication actions"""
        response_plan = self.response_plans.get(incident.category)
        if response_plan:
            for action in response_plan.preventive_measures[:2]:  # First 2 as eradication
                self._execute_response_action(incident, action, "eradication")

    def _execute_recovery_actions(self, incident: Incident):
        """Execute recovery actions"""
        response_plan = self.response_plans.get(incident.category)
        if response_plan:
            for action in response_plan.recovery_procedures:
                self._execute_response_action(incident, action, "recovery")

    def _close_incident(self, incident: Incident):
        """Close incident and move to history"""
        # Move to history
        self.incident_history.append(incident)
        del self.active_incidents[incident.id]

        # Generate lessons learned report
        self._generate_lessons_learned(incident)

        logger.info(f"Incident {incident.id} closed and moved to history")

    def _generate_lessons_learned(self, incident: Incident):
        """Generate lessons learned from incident"""
        lessons = [
            f"Improve detection for {incident.category.value} incidents",
            "Review response procedures effectiveness",
            "Update preventive measures based on root cause"
        ]

        incident.lessons_learned = lessons

        # In production, this would trigger a formal lessons learned meeting
        logger.info(f"Lessons learned generated for incident {incident.id}")

    def get_incident_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed incident report"""
        incident = self.active_incidents.get(incident_id)
        if not incident:
            # Check history
            for hist_incident in self.incident_history:
                if hist_incident.id == incident_id:
                    incident = hist_incident
                    break

        if not incident:
            return None

        return {
            'id': incident.id,
            'title': incident.title,
            'description': incident.description,
            'category': incident.category.value,
            'severity': incident.severity.value,
            'status': incident.status.value,
            'timeline': {
                'detected': incident.detected_at.isoformat(),
                'contained': incident.contained_at.isoformat() if incident.contained_at else None,
                'eradicated': incident.eradicated_at.isoformat() if incident.eradicated_at else None,
                'recovered': incident.recovered_at.isoformat() if incident.recovered_at else None,
                'closed': incident.closed_at.isoformat() if incident.closed_at else None
            },
            'impact': {
                'affected_assets': incident.affected_assets,
                'affected_users': incident.affected_users,
                'data_compromised': incident.data_compromised
            },
            'response_actions': {
                'containment': incident.containment_actions,
                'eradication': incident.eradication_actions,
                'recovery': incident.recovery_actions
            },
            'analysis': {
                'root_cause': incident.root_cause_analysis,
                'forensic_findings': incident.forensic_analysis,
                'lessons_learned': incident.lessons_learned
            }
        }

    def get_incident_dashboard(self, tenant_id: str = 'system') -> Dict[str, Any]:
        """Get incident dashboard data"""
        # Filter incidents by tenant
        tenant_incidents = [
            incident for incident in self.active_incidents.values()
            if incident.tenant_id == tenant_id
        ]

        recent_incidents = [
            incident for incident in self.incident_history[-10:]  # Last 10 closed incidents
            if incident.tenant_id == tenant_id
        ]

        # Calculate metrics
        severity_counts = {}
        for incident in tenant_incidents + recent_incidents:
            severity_counts[incident.severity.value] = severity_counts.get(incident.severity.value, 0) + 1

        status_counts = {}
        for incident in tenant_incidents:
            status_counts[incident.status.value] = status_counts.get(incident.status.value, 0) + 1

        # Calculate MTTR (Mean Time To Resolution)
        resolved_incidents = [i for i in recent_incidents if i.closed_at and i.detected_at]
        if resolved_incidents:
            total_resolution_time = sum(
                (i.closed_at - i.detected_at).total_seconds()
                for i in resolved_incidents
            )
            mttr_seconds = total_resolution_time / len(resolved_incidents)
            mttr_hours = mttr_seconds / 3600
        else:
            mttr_hours = 0

        return {
            'active_incidents': len(tenant_incidents),
            'severity_breakdown': severity_counts,
            'status_breakdown': status_counts,
            'mttr_hours': round(mttr_hours, 2),
            'recent_incidents': [
                {
                    'id': i.id,
                    'title': i.title,
                    'severity': i.severity.value,
                    'status': i.status.value,
                    'detected_at': i.detected_at.isoformat()
                } for i in recent_incidents[-5:]  # Last 5
            ],
            'generated_at': datetime.utcnow().isoformat()
        }

    def simulate_incident_drill(self, incident_type: IncidentCategory) -> Dict[str, Any]:
        """
        Simulate incident response drill for training purposes
        """
        # Create mock incident
        mock_incident = Incident(
            id=f"drill-{uuid.uuid4()}",
            title=f"Simulated {incident_type.value.title()} Incident",
            description="This is a simulated incident for training purposes",
            category=incident_type,
            severity=IncidentSeverity.MEDIUM,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            reported_by='training_system',
            tenant_id='training'
        )

        # Execute response plan (without actual actions)
        response_plan = self.response_plans.get(incident_type)
        simulation_results = {
            'incident_id': mock_incident.id,
            'incident_type': incident_type.value,
            'response_plan': {
                'detection_methods': response_plan.detection_methods if response_plan else [],
                'immediate_actions': response_plan.immediate_actions if response_plan else [],
                'escalation_criteria': response_plan.escalation_criteria if response_plan else {},
                'communication_plan': response_plan.communication_plan if response_plan else {}
            },
            'simulation_timestamp': datetime.utcnow().isoformat(),
            'training_purpose': True
        }

        logger.info(f"Incident response drill simulated for {incident_type.value}")
        return simulation_results