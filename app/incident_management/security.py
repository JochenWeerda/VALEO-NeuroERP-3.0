"""
ISO 27001 Information Security Incident Management
Information Security Incident Response Framework

Dieses Modul implementiert das Information Security Incident Management Framework
gemäß ISO 27001 Annex A.16 für VALEO-NeuroERP mit Incident Detection, Response und Recovery.
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
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class IncidentCategory(Enum):
    """Incident categories based on ISO 27001"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_INFECTION = "malware_infection"
    DATA_BREACH = "data_breach"
    DENIAL_OF_SERVICE = "denial_of_service"
    PHYSICAL_SECURITY = "physical_security"
    SOCIAL_ENGINEERING = "social_engineering"
    CONFIGURATION_ERROR = "configuration_error"
    THIRD_PARTY_COMPROMISE = "third_party_compromise"
    INSIDER_THREAT = "insider_threat"
    SUPPLY_CHAIN_ATTACK = "supply_chain_attack"


class IncidentPhase(Enum):
    """Incident response phases"""
    DETECTION = "detection"
    ASSESSMENT = "assessment"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"
    CLOSURE = "closure"


class ContainmentStrategy(Enum):
    """Containment strategies"""
    ISOLATION = "isolation"
    SEGMENTATION = "segmentation"
    ACCESS_REVOCATION = "access_revocation"
    SERVICE_DISRUPTION = "service_disruption"
    EMERGENCY_PATCHING = "emergency_patching"


class RecoveryAction(Enum):
    """Recovery actions"""
    SYSTEM_RESTORE = "system_restore"
    DATA_RECOVERY = "data_recovery"
    SERVICE_RESTART = "service_restart"
    CONFIGURATION_RESET = "configuration_reset"
    CLEANUP_OPERATIONS = "cleanup_operations"


@dataclass
class SecurityIncident:
    """Security incident record"""
    id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    current_phase: IncidentPhase
    detected_at: datetime
    reported_by: str
    assigned_to: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    business_impact: str = ""
    technical_details: Dict[str, Any] = field(default_factory=dict)
    containment_actions: List[Dict[str, Any]] = field(default_factory=list)
    eradication_actions: List[Dict[str, Any]] = field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    root_cause: str = ""
    prevention_measures: List[str] = field(default_factory=list)
    estimated_impact: Dict[str, Any] = field(default_factory=dict)
    actual_impact: Dict[str, Any] = field(default_factory=dict)
    resolution_time: Optional[timedelta] = None
    closed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IncidentResponseTeam:
    """Incident response team member"""
    id: str
    user_id: str
    role: str  # lead, technical, communication, legal, executive
    skills: List[str] = field(default_factory=list)
    contact_info: Dict[str, str] = field(default_factory=dict)
    availability: str = "24/7"  # 24/7, business_hours, on_call
    is_active: bool = True
    joined_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IncidentCommunication:
    """Incident communication record"""
    id: str
    incident_id: str
    communication_type: str  # internal, external, regulatory, customer
    recipient: str
    subject: str
    content: str
    sent_at: datetime
    sent_by: str
    delivery_status: str = "sent"
    response_required: bool = False
    response_received: bool = False
    follow_up_actions: List[str] = field(default_factory=list)


@dataclass
class IncidentEvidence:
    """Incident evidence record"""
    id: str
    incident_id: str
    evidence_type: str  # log, screenshot, memory_dump, network_traffic, etc.
    description: str
    location: str
    collected_at: datetime
    collected_by: str
    integrity_hash: str = ""
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    is_preserved: bool = True


@dataclass
class IncidentTimeline:
    """Incident timeline entry"""
    id: str
    incident_id: str
    timestamp: datetime
    phase: IncidentPhase
    action: str
    performed_by: str
    details: str
    evidence_ids: List[str] = field(default_factory=list)
    automated: bool = False


@dataclass
class IncidentMetrics:
    """Incident response metrics"""
    id: str
    incident_id: str
    detection_time: Optional[timedelta] = None  # Time to detect
    response_time: Optional[timedelta] = None   # Time to respond
    containment_time: Optional[timedelta] = None  # Time to contain
    recovery_time: Optional[timedelta] = None    # Time to recover
    total_resolution_time: Optional[timedelta] = None
    false_positive_rate: float = 0.0
    escalation_count: int = 0
    stakeholder_communications: int = 0
    lessons_learned_count: int = 0
    prevention_measures_implemented: int = 0


@dataclass
class IncidentPlaybook:
    """Incident response playbook"""
    id: str
    incident_type: IncidentCategory
    severity: IncidentSeverity
    title: str
    description: str
    detection_indicators: List[str] = field(default_factory=list)
    immediate_actions: List[Dict[str, Any]] = field(default_factory=list)
    containment_strategies: List[ContainmentStrategy] = field(default_factory=list)
    communication_templates: Dict[str, str] = field(default_factory=dict)
    escalation_criteria: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    is_active: bool = True
    last_updated: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


class ISO27001IncidentManagement:
    """
    ISO 27001 Information Security Incident Management
    Implements Annex A.16 - Information Security Incident Management
    """

    def __init__(self, db_session, alert_service=None, communication_service=None):
        self.db = db_session
        self.alerts = alert_service
        self.communication = communication_service

        # Incident management components
        self.incidents: Dict[str, SecurityIncident] = {}
        self.response_team: Dict[str, IncidentResponseTeam] = {}
        self.incident_communications: List[IncidentCommunication] = {}
        self.incident_evidence: List[IncidentEvidence] = {}
        self.incident_timelines: List[IncidentTimeline] = {}
        self.incident_metrics: Dict[str, IncidentMetrics] = {}
        self.incident_playbooks: Dict[str, IncidentPlaybook] = {}

        # Incident response configuration
        self.incident_config = self._initialize_incident_config()

        # Default playbooks
        self._initialize_default_playbooks()

        # Response team setup
        self._initialize_response_team()

    def _initialize_incident_config(self) -> Dict[str, Any]:
        """Initialize incident response configuration"""
        return {
            'response_times': {
                'critical': {'detection': 300, 'response': 1800, 'containment': 3600},  # seconds
                'high': {'detection': 1800, 'response': 7200, 'containment': 14400},
                'medium': {'detection': 7200, 'response': 28800, 'containment': 86400},
                'low': {'detection': 28800, 'response': 86400, 'containment': 259200}
            },
            'escalation_thresholds': {
                'critical': {'business_impact': 'severe', 'data_compromised': True},
                'high': {'business_impact': 'significant', 'data_compromised': False},
                'medium': {'business_impact': 'moderate', 'data_compromised': False},
                'low': {'business_impact': 'minimal', 'data_compromised': False}
            },
            'communication_requirements': {
                'internal_notification': 1800,  # seconds
                'external_notification': 7200,  # seconds for breaches
                'regulatory_notification': 7200   # seconds for regulated data
            },
            'evidence_preservation': {
                'log_retention': 2555,  # days (7 years)
                'evidence_retention': 2555,
                'chain_of_custody': True,
                'cryptographic_hashing': True
            }
        }

    def _initialize_default_playbooks(self):
        """Initialize default incident response playbooks"""
        default_playbooks = [
            {
                'incident_type': IncidentCategory.UNAUTHORIZED_ACCESS,
                'severity': IncidentSeverity.HIGH,
                'title': 'Unauthorized Access Incident Response',
                'description': 'Response procedures for unauthorized system access',
                'detection_indicators': [
                    'Failed login attempts',
                    'Suspicious IP addresses',
                    'Anomalous access patterns',
                    'Privilege escalation events'
                ],
                'immediate_actions': [
                    {'action': 'Isolate affected systems', 'priority': 'critical'},
                    {'action': 'Revoke suspicious sessions', 'priority': 'high'},
                    {'action': 'Enable enhanced logging', 'priority': 'high'}
                ],
                'containment_strategies': [
                    ContainmentStrategy.ACCESS_REVOCATION,
                    ContainmentStrategy.ISOLATION
                ],
                'communication_templates': {
                    'internal': 'Unauthorized access detected on {system}. Investigation initiated.',
                    'external': 'Security monitoring detected potential unauthorized access.'
                },
                'escalation_criteria': {
                    'data_accessed': True,
                    'production_system': True,
                    'multiple_accounts': True
                },
                'success_criteria': [
                    'Unauthorized access contained',
                    'Affected accounts secured',
                    'Access logs preserved for investigation'
                ]
            },
            {
                'incident_type': IncidentCategory.MALWARE_INFECTION,
                'severity': IncidentSeverity.CRITICAL,
                'title': 'Malware Infection Response',
                'description': 'Response procedures for malware detection and eradication',
                'detection_indicators': [
                    'Antivirus alerts',
                    'Suspicious file modifications',
                    'Unusual network traffic',
                    'System performance degradation'
                ],
                'immediate_actions': [
                    {'action': 'Isolate infected systems', 'priority': 'critical'},
                    {'action': 'Disable network connectivity', 'priority': 'critical'},
                    {'action': 'Quarantine suspicious files', 'priority': 'high'}
                ],
                'containment_strategies': [
                    ContainmentStrategy.ISOLATION,
                    ContainmentStrategy.SEGMENTATION
                ],
                'communication_templates': {
                    'internal': 'Malware detected on {system}. Containment procedures initiated.',
                    'external': 'Security systems detected and contained potential malware threat.'
                },
                'escalation_criteria': {
                    'ransomware': True,
                    'data_encryption': True,
                    'multiple_systems': True
                },
                'success_criteria': [
                    'Malware contained and eradicated',
                    'Systems cleaned and verified',
                    'No data loss or compromise confirmed'
                ]
            },
            {
                'incident_type': IncidentCategory.DATA_BREACH,
                'severity': IncidentSeverity.CRITICAL,
                'title': 'Data Breach Response',
                'description': 'Response procedures for data breach incidents',
                'detection_indicators': [
                    'Unauthorized data access logs',
                    'Data exfiltration indicators',
                    'DLP alerts',
                    'Unusual data transfers'
                ],
                'immediate_actions': [
                    {'action': 'Stop data exfiltration', 'priority': 'critical'},
                    {'action': 'Assess data exposure', 'priority': 'critical'},
                    {'action': 'Notify legal team', 'priority': 'critical'}
                ],
                'containment_strategies': [
                    ContainmentStrategy.ACCESS_REVOCATION,
                    ContainmentStrategy.SERVICE_DISRUPTION
                ],
                'communication_templates': {
                    'regulatory': 'Data breach detected. Assessment and notification procedures initiated.',
                    'customer': 'Security incident detected. We are investigating and will provide updates.'
                },
                'escalation_criteria': {
                    'personal_data': True,
                    'large_scale': True,
                    'regulatory_data': True
                },
                'success_criteria': [
                    'Data breach contained',
                    'Data exposure assessed',
                    'Regulatory notifications completed',
                    'Affected parties notified'
                ]
            }
        ]

        for playbook_data in default_playbooks:
            playbook = IncidentPlaybook(**playbook_data)
            key = f"{playbook.incident_type.value}_{playbook.severity.value}"
            self.incident_playbooks[key] = playbook

    def _initialize_response_team(self):
        """Initialize incident response team structure"""
        # This would be populated with actual team members
        # For now, creating placeholder structure
        team_roles = [
            {'role': 'incident_response_lead', 'required': True},
            {'role': 'technical_analyst', 'required': True},
            {'role': 'communication_coordinator', 'required': True},
            {'role': 'legal_advisor', 'required': False},
            {'role': 'executive_sponsor', 'required': False}
        ]

        for role_info in team_roles:
            # Create placeholder team entries
            team_id = str(uuid.uuid4())
            team_member = IncidentResponseTeam(
                id=team_id,
                user_id=f"placeholder_{role_info['role']}",
                role=role_info['role'],
                skills=['incident_response'],
                availability='24/7' if role_info['required'] else 'business_hours'
            )
            self.response_team[team_id] = team_member

    def detect_incident(self, detection_data: Dict[str, Any]) -> str:
        """
        Detect and register a new security incident
        Returns incident ID
        """
        incident_id = str(uuid.uuid4())

        # Determine severity based on detection data
        severity = self._assess_incident_severity(detection_data)

        # Determine category
        category = IncidentCategory(detection_data.get('category', 'unauthorized_access'))

        incident = SecurityIncident(
            id=incident_id,
            title=detection_data['title'],
            description=detection_data['description'],
            category=category,
            severity=severity,
            status=IncidentStatus.DETECTED,
            current_phase=IncidentPhase.DETECTION,
            detected_at=datetime.utcnow(),
            reported_by=detection_data.get('reported_by', 'system'),
            affected_systems=detection_data.get('affected_systems', []),
            technical_details=detection_data.get('technical_details', {}),
            business_impact=detection_data.get('business_impact', '')
        )

        self.incidents[incident_id] = incident

        # Initialize metrics
        self._initialize_incident_metrics(incident_id)

        # Add timeline entry
        self._add_timeline_entry(incident_id, IncidentPhase.DETECTION,
                               "Incident detected and registered", "system", automated=True)

        # Trigger immediate response
        self._trigger_incident_response(incident)

        logger.warning(f"Security incident detected: {incident.title} (Severity: {incident.severity.value})")
        return incident_id

    def _assess_incident_severity(self, detection_data: Dict[str, Any]) -> IncidentSeverity:
        """Assess incident severity based on detection data"""
        # Simple severity assessment - in production would be more sophisticated
        if detection_data.get('critical_system_affected', False):
            return IncidentSeverity.CRITICAL
        elif detection_data.get('data_breach', False):
            return IncidentSeverity.CRITICAL
        elif detection_data.get('production_impact', False):
            return IncidentSeverity.HIGH
        elif detection_data.get('multiple_users_affected', False):
            return IncidentSeverity.MEDIUM
        else:
            return IncidentSeverity.LOW

    def _initialize_incident_metrics(self, incident_id: str):
        """Initialize incident response metrics"""
        metrics = IncidentMetrics(id=str(uuid.uuid4()), incident_id=incident_id)
        self.incident_metrics[incident_id] = metrics

    def _add_timeline_entry(self, incident_id: str, phase: IncidentPhase, action: str,
                          performed_by: str, details: str = "", automated: bool = False):
        """Add entry to incident timeline"""
        timeline_entry = IncidentTimeline(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            timestamp=datetime.utcnow(),
            phase=phase,
            action=action,
            performed_by=performed_by,
            details=details,
            automated=automated
        )

        if incident_id not in self.incident_timelines:
            self.incident_timelines[incident_id] = []

        self.incident_timelines[incident_id].append(timeline_entry)

    def _trigger_incident_response(self, incident: SecurityIncident):
        """Trigger automated incident response"""
        # Find applicable playbook
        playbook_key = f"{incident.category.value}_{incident.severity.value}"
        playbook = self.incident_playbooks.get(playbook_key)

        if playbook:
            # Execute immediate actions
            for action in playbook.immediate_actions:
                self._execute_immediate_action(incident.id, action)

            # Assign response team
            self._assign_response_team(incident.id, playbook)

            # Send initial notifications
            self._send_incident_notifications(incident, playbook)

        # Update incident status
        incident.status = IncidentStatus.INVESTIGATING
        incident.current_phase = IncidentPhase.ASSESSMENT

        # Start metrics tracking
        metrics = self.incident_metrics[incident.id]
        metrics.detection_time = datetime.utcnow() - incident.detected_at

    def _execute_immediate_action(self, incident_id: str, action: Dict[str, Any]):
        """Execute immediate response action"""
        # In production, this would trigger actual system actions
        action_description = f"Executed immediate action: {action['action']}"
        self._add_timeline_entry(incident_id, IncidentPhase.CONTAINMENT,
                               action['action'], "system", action_description, automated=True)

    def _assign_response_team(self, incident_id: str, playbook: IncidentPlaybook):
        """Assign incident response team"""
        incident = self.incidents[incident_id]

        # Assign incident response lead
        lead_team_member = None
        for team_member in self.response_team.values():
            if team_member.role == 'incident_response_lead' and team_member.is_active:
                lead_team_member = team_member
                break

        if lead_team_member:
            incident.assigned_to = lead_team_member.user_id

        self._add_timeline_entry(incident_id, IncidentPhase.ASSESSMENT,
                               "Incident response team assigned", "system", automated=True)

    def _send_incident_notifications(self, incident: SecurityIncident, playbook: IncidentPlaybook):
        """Send incident notifications"""
        # Internal notification
        internal_communication = IncidentCommunication(
            id=str(uuid.uuid4()),
            incident_id=incident.id,
            communication_type='internal',
            recipient='incident_response_team',
            subject=f'Incident Alert: {incident.title}',
            content=playbook.communication_templates.get('internal', f'Incident detected: {incident.description}'),
            sent_at=datetime.utcnow(),
            sent_by='system'
        )

        if incident.id not in self.incident_communications:
            self.incident_communications[incident.id] = []

        self.incident_communications[incident.id].append(internal_communication)

    def update_incident_status(self, incident_id: str, new_status: IncidentStatus,
                             new_phase: IncidentPhase, update_data: Dict[str, Any]) -> bool:
        """
        Update incident status and phase
        """
        if incident_id not in self.incidents:
            return False

        incident = self.incidents[incident_id]
        old_status = incident.status
        old_phase = incident.phase

        incident.status = new_status
        incident.current_phase = new_phase
        incident.updated_at = datetime.utcnow()

        # Update metrics
        metrics = self.incident_metrics[incident_id]
        if new_phase == IncidentPhase.CONTAINMENT and not metrics.containment_time:
            metrics.containment_time = datetime.utcnow() - incident.detected_at
        elif new_phase == IncidentPhase.RECOVERY and not metrics.recovery_time:
            metrics.recovery_time = datetime.utcnow() - incident.detected_at

        # Add timeline entry
        action = f"Status updated from {old_status.value} to {new_status.value}, Phase: {new_phase.value}"
        details = update_data.get('details', '')
        performed_by = update_data.get('performed_by', 'system')

        self._add_timeline_entry(incident_id, new_phase, action, performed_by, details)

        # Execute phase-specific actions
        if new_phase == IncidentPhase.CONTAINMENT:
            self._execute_containment_actions(incident, update_data)
        elif new_phase == IncidentPhase.ERADICATION:
            self._execute_eradication_actions(incident, update_data)
        elif new_phase == IncidentPhase.RECOVERY:
            self._execute_recovery_actions(incident, update_data)

        logger.info(f"Incident {incident_id} status updated: {old_status.value} → {new_status.value}")
        return True

    def _execute_containment_actions(self, incident: SecurityIncident, update_data: Dict[str, Any]):
        """Execute containment actions"""
        containment_actions = update_data.get('containment_actions', [])

        for action in containment_actions:
            action_record = {
                'action': action['type'],
                'description': action.get('description', ''),
                'executed_at': datetime.utcnow().isoformat(),
                'executed_by': update_data.get('performed_by', 'system'),
                'result': action.get('result', 'successful')
            }
            incident.containment_actions.append(action_record)

    def _execute_eradication_actions(self, incident: SecurityIncident, update_data: Dict[str, Any]):
        """Execute eradication actions"""
        eradication_actions = update_data.get('eradication_actions', [])

        for action in eradication_actions:
            action_record = {
                'action': action['type'],
                'description': action.get('description', ''),
                'executed_at': datetime.utcnow().isoformat(),
                'executed_by': update_data.get('performed_by', 'system'),
                'result': action.get('result', 'successful')
            }
            incident.eradication_actions.append(action_record)

    def _execute_recovery_actions(self, incident: SecurityIncident, update_data: Dict[str, Any]):
        """Execute recovery actions"""
        recovery_actions = update_data.get('recovery_actions', [])

        for action in recovery_actions:
            action_record = {
                'action': action['type'],
                'description': action.get('description', ''),
                'executed_at': datetime.utcnow().isoformat(),
                'executed_by': update_data.get('performed_by', 'system'),
                'result': action.get('result', 'successful')
            }
            incident.recovery_actions.append(action_record)

    def collect_incident_evidence(self, incident_id: str, evidence_data: Dict[str, Any]) -> str:
        """
        Collect incident evidence
        Returns evidence ID
        """
        evidence_id = str(uuid.uuid4())

        evidence = IncidentEvidence(
            id=evidence_id,
            incident_id=incident_id,
            evidence_type=evidence_data['evidence_type'],
            description=evidence_data['description'],
            location=evidence_data['location'],
            collected_at=datetime.utcnow(),
            collected_by=evidence_data['collected_by'],
            integrity_hash=evidence_data.get('integrity_hash', ''),
            chain_of_custody=[{
                'action': 'collected',
                'performed_by': evidence_data['collected_by'],
                'timestamp': datetime.utcnow().isoformat(),
                'location': evidence_data['location']
            }]
        )

        if incident_id not in self.incident_evidence:
            self.incident_evidence[incident_id] = []

        self.incident_evidence[incident_id].append(evidence)

        self._add_timeline_entry(incident_id, IncidentPhase.ASSESSMENT,
                               f"Evidence collected: {evidence.evidence_type}", evidence.collected_by)

        logger.info(f"Incident evidence collected: {evidence.evidence_type} for incident {incident_id}")
        return evidence_id

    def close_incident(self, incident_id: str, closure_data: Dict[str, Any]) -> bool:
        """
        Close incident with lessons learned
        """
        if incident_id not in self.incidents:
            return False

        incident = self.incidents[incident_id]
        incident.status = IncidentStatus.CLOSED
        incident.closed_at = datetime.utcnow()
        incident.resolution_time = incident.closed_at - incident.detected_at

        # Add closure data
        incident.root_cause = closure_data.get('root_cause', '')
        incident.lessons_learned = closure_data.get('lessons_learned', [])
        incident.prevention_measures = closure_data.get('prevention_measures', [])
        incident.actual_impact = closure_data.get('actual_impact', {})

        # Update metrics
        metrics = self.incident_metrics[incident_id]
        metrics.total_resolution_time = incident.resolution_time
        metrics.lessons_learned_count = len(incident.lessons_learned)
        metrics.prevention_measures_implemented = len(incident.prevention_measures)

        # Add final timeline entry
        self._add_timeline_entry(incident_id, IncidentPhase.CLOSURE,
                               "Incident closed with lessons learned",
                               closure_data.get('closed_by', 'system'))

        logger.info(f"Incident {incident_id} closed. Resolution time: {incident.resolution_time}")
        return True

    def get_incident_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate incident management dashboard"""
        # Current incidents by status
        status_counts = {}
        for incident in self.incidents.values():
            status = incident.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Incidents by severity
        severity_counts = {}
        for incident in self.incidents.values():
            severity = incident.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Incidents by category
        category_counts = {}
        for incident in self.incidents.values():
            category = incident.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Recent incidents (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_incidents = [
            incident for incident in self.incidents.values()
            if incident.detected_at > thirty_days_ago
        ]

        # Average resolution times
        resolution_times = [
            incident.resolution_time.total_seconds()
            for incident in self.incidents.values()
            if incident.resolution_time
        ]
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

        # Active response team
        active_team_members = len([member for member in self.response_team.values() if member.is_active])

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'incident_statistics': {
                'total_incidents': len(self.incidents),
                'active_incidents': status_counts.get('investigating', 0) + status_counts.get('contained', 0) + status_counts.get('eradicated', 0),
                'closed_incidents': status_counts.get('closed', 0),
                'false_positives': status_counts.get('false_positive', 0)
            },
            'distribution': {
                'by_status': status_counts,
                'by_severity': severity_counts,
                'by_category': category_counts
            },
            'performance_metrics': {
                'avg_resolution_time_hours': round(avg_resolution_time / 3600, 1) if avg_resolution_time else 0,
                'recent_incidents_count': len(recent_incidents),
                'active_team_members': active_team_members
            },
            'recent_incidents': [
                {
                    'id': incident.id,
                    'title': incident.title,
                    'severity': incident.severity.value,
                    'status': incident.status.value,
                    'detected_at': incident.detected_at.isoformat(),
                    'assigned_to': incident.assigned_to
                } for incident in recent_incidents[-10:]  # Last 10
            ],
            'response_team_status': self._get_response_team_status()
        }

    def _get_response_team_status(self) -> Dict[str, Any]:
        """Get incident response team status"""
        team_by_role = {}
        for member in self.response_team.values():
            if member.is_active:
                role = member.role
                team_by_role[role] = team_by_role.get(role, 0) + 1

        return {
            'total_members': len([m for m in self.response_team.values() if m.is_active]),
            'by_role': team_by_role,
            'availability': {
                '24/7': len([m for m in self.response_team.values() if m.availability == '24/7' and m.is_active]),
                'business_hours': len([m for m in self.response_team.values() if m.availability == 'business_hours' and m.is_active]),
                'on_call': len([m for m in self.response_team.values() if m.availability == 'on_call' and m.is_active])
            }
        }

    def check_incident_management_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 incident management compliance"""
        incidents = list(self.incidents.values())
        playbooks = list(self.incident_playbooks.values())
        team_members = list(self.response_team.values())

        compliance_status = self._assess_incident_management_compliance(incidents, playbooks, team_members)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.16 Information Security Incident Management',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_incident_management_compliance(self, incidents: List[SecurityIncident],
                                             playbooks: List[IncidentPlaybook],
                                             team_members: List[IncidentResponseTeam]) -> Dict[str, Any]:
        """Assess ISO 27001 incident management compliance"""
        issues = []

        # Check incident response plan
        if len(playbooks) < 5:  # Arbitrary minimum for different incident types
            issues.append("Insufficient incident response playbooks for common incident types")

        # Check response team
        active_team = len([m for m in team_members if m.is_active])
        if active_team < 3:  # Minimum team size
            issues.append("Incident response team is understaffed")

        # Check incident documentation
        documented_incidents = len([i for i in incidents if i.root_cause and i.lessons_learned])
        if len(incidents) > 0 and documented_incidents / len(incidents) < 0.8:
            issues.append("Insufficient incident documentation and lessons learned")

        # Check response times
        recent_incidents = [i for i in incidents if (datetime.utcnow() - i.detected_at).days <= 90]
        timely_responses = len([i for i in recent_incidents if i.resolution_time and i.resolution_time.days <= 7])
        if len(recent_incidents) > 0 and timely_responses / len(recent_incidents) < 0.7:
            issues.append("Incident response times exceed acceptable thresholds")

        # Check communication procedures
        incidents_with_communication = len([i for i in incidents if i.id in self.incident_communications])
        if len(incidents) > 0 and incidents_with_communication / len(incidents) < 0.9:
            issues.append("Incident communication procedures not consistently followed")

        compliance_score = max(0, 100 - (len(issues) * 10))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_incident_compliance_recommendations(issues)
        }

    def _generate_incident_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate incident management compliance recommendations"""
        recommendations = []

        if any('playbooks' in issue.lower() for issue in issues):
            recommendations.append("Develop comprehensive incident response playbooks for all identified threat scenarios")

        if any('team' in issue.lower() for issue in issues):
            recommendations.append("Expand incident response team and ensure 24/7 coverage for critical roles")

        if any('documentation' in issue.lower() for issue in issues):
            recommendations.append("Improve incident documentation processes and ensure lessons learned are captured")

        if any('response times' in issue.lower() for issue in issues):
            recommendations.append("Review and optimize incident response processes to improve response times")

        if any('communication' in issue.lower() for issue in issues):
            recommendations.append("Strengthen incident communication procedures and stakeholder notification processes")

        recommendations.append("Conduct regular incident response exercises and update procedures based on lessons learned")

        return recommendations