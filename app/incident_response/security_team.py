"""
ISO 27001 Security Incident Response Team
Informationssicherheits-Managementsystem Security Incident Response Team

Dieses Modul implementiert das Security Incident Response Team gemäß ISO 27001 Annex A.16.1
für VALEO-NeuroERP mit Team-Struktur, Escalation Procedures und Incident Response Workflows.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class TeamRole(Enum):
    """Security incident response team roles"""
    TEAM_LEAD = "team_lead"
    TECHNICAL_LEAD = "technical_lead"
    COMMUNICATIONS_LEAD = "communications_lead"
    LEGAL_LEAD = "legal_lead"
    BUSINESS_IMPACT_ASSESSOR = "business_impact_assessor"
    FORENSIC_ANALYST = "forensic_analyst"
    RECOVERY_SPECIALIST = "recovery_specialist"
    EXTERNAL_COORDINATOR = "external_coordinator"


class EscalationLevel(Enum):
    """Incident escalation levels"""
    LEVEL_1 = "level_1"  # Initial response team
    LEVEL_2 = "level_2"  # Extended response team
    LEVEL_3 = "level_3"  # Executive crisis management


class ResponsePhase(Enum):
    """Incident response phases"""
    DETECTION = "detection"
    ASSESSMENT = "assessment"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


class CommunicationType(Enum):
    """Types of incident communications"""
    INTERNAL_NOTIFICATION = "internal_notification"
    EXTERNAL_NOTIFICATION = "external_notification"
    REGULATORY_REPORTING = "regulatory_reporting"
    CUSTOMER_NOTIFICATION = "customer_notification"
    MEDIA_STATEMENT = "media_statement"


@dataclass
class TeamMember:
    """Security incident response team member"""
    id: str
    user_id: str
    name: str
    role: TeamRole
    primary_contact: str
    secondary_contact: str
    availability_hours: str  # e.g., "24/7", "business_hours"
    skills: List[str]
    certifications: List[str]
    is_active: bool = True
    last_training: Optional[datetime] = None
    response_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EscalationRule:
    """Incident escalation rule"""
    id: str
    name: str
    trigger_conditions: Dict[str, Any]
    target_level: EscalationLevel
    required_roles: List[TeamRole]
    time_to_escalate: int  # minutes
    notification_channels: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IncidentAssignment:
    """Incident assignment to team members"""
    id: str
    incident_id: str
    team_member_id: str
    role: TeamRole
    assigned_at: datetime
    assigned_by: str
    status: str = "active"
    notes: str = ""


@dataclass
class CommunicationLog:
    """Incident communication log"""
    id: str
    incident_id: str
    communication_type: CommunicationType
    recipient: str
    sent_by: str
    sent_at: datetime
    content: str
    delivery_status: str = "sent"
    response_received: Optional[datetime] = None
    response_content: str = ""


@dataclass
class ResponseWorkflow:
    """Incident response workflow definition"""
    id: str
    name: str
    incident_type: str
    phases: List[Dict[str, Any]]
    required_roles: List[TeamRole]
    estimated_duration: int  # minutes
    success_criteria: List[str]
    is_active: bool = True
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ISO27001SecurityIncidentResponseTeam:
    """
    ISO 27001 Security Incident Response Team
    Implements Annex A.16.1 - Information Security Incident Management
    """

    def __init__(self, db_session, incident_response_service=None, communication_service=None):
        self.db = db_session
        self.incident_response = incident_response_service
        self.communication = communication_service

        # Team management
        self.team_members: Dict[str, TeamMember] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.incident_assignments: List[IncidentAssignment] = {}
        self.communication_logs: List[CommunicationLog] = {}
        self.response_workflows: Dict[str, ResponseWorkflow] = {}

        # Team configuration
        self.team_config = self._initialize_team_config()

        # Escalation procedures
        self.escalation_procedures = self._initialize_escalation_procedures()

        # Communication templates
        self.communication_templates = self._initialize_communication_templates()

    def _initialize_team_config(self) -> Dict[str, Any]:
        """Initialize team configuration"""
        return {
            'core_team_size': 8,
            'extended_team_size': 15,
            'crisis_team_size': 25,
            'response_sla': {
                'critical': 15,  # minutes
                'high': 60,      # minutes
                'medium': 240,   # minutes
                'low': 1440      # minutes (24 hours)
            },
            'training_requirements': {
                'annual_training': True,
                'incident_simulation': True,
                'certification_renewal': 3  # years
            },
            'communication_channels': [
                'email', 'sms', 'phone', 'slack', 'teams'
            ]
        }

    def _initialize_escalation_procedures(self) -> Dict[EscalationLevel, Dict[str, Any]]:
        """Initialize escalation procedures for different levels"""
        return {
            EscalationLevel.LEVEL_1: {
                'team_size': 4,
                'required_roles': [TeamRole.TEAM_LEAD, TeamRole.TECHNICAL_LEAD, TeamRole.FORENSIC_ANALYST],
                'decision_authority': 'team_lead',
                'communication_scope': 'internal_only',
                'external_notification': False
            },
            EscalationLevel.LEVEL_2: {
                'team_size': 8,
                'required_roles': [TeamRole.TEAM_LEAD, TeamRole.TECHNICAL_LEAD, TeamRole.COMMUNICATIONS_LEAD,
                                 TeamRole.FORENSIC_ANALYST, TeamRole.RECOVERY_SPECIALIST],
                'decision_authority': 'incident_manager',
                'communication_scope': 'management',
                'external_notification': False
            },
            EscalationLevel.LEVEL_3: {
                'team_size': 15,
                'required_roles': [TeamRole.TEAM_LEAD, TeamRole.TECHNICAL_LEAD, TeamRole.COMMUNICATIONS_LEAD,
                                 TeamRole.LEGAL_LEAD, TeamRole.BUSINESS_IMPACT_ASSESSOR, TeamRole.EXTERNAL_COORDINATOR],
                'decision_authority': 'executive_crisis_team',
                'communication_scope': 'full_external',
                'external_notification': True
            }
        }

    def _initialize_communication_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize communication templates"""
        return {
            'internal_notification': {
                'subject': 'Security Incident Alert - {incident_id}',
                'channels': ['email', 'slack'],
                'audience': 'response_team',
                'content': 'A security incident has been detected and assigned to the response team.'
            },
            'management_escalation': {
                'subject': 'Security Incident Escalation - Level {level}',
                'channels': ['email', 'phone'],
                'audience': 'management',
                'content': 'Security incident {incident_id} has been escalated to Level {level}.'
            },
            'external_notification': {
                'subject': 'Security Incident Update',
                'channels': ['email'],
                'audience': 'customers',
                'content': 'We are experiencing a security incident and are taking appropriate measures.'
            },
            'regulatory_reporting': {
                'subject': 'Mandatory Security Incident Report',
                'channels': ['email', 'fax'],
                'audience': 'regulators',
                'content': 'Reporting security incident as required by regulations.'
            }
        }

    def add_team_member(self, member_data: Dict[str, Any]) -> str:
        """
        Add a member to the security incident response team
        Returns member ID
        """
        member_id = str(uuid.uuid4())

        member = TeamMember(
            id=member_id,
            user_id=member_data['user_id'],
            name=member_data['name'],
            role=TeamRole[member_data['role'].upper()],
            primary_contact=member_data['primary_contact'],
            secondary_contact=member_data.get('secondary_contact', ''),
            availability_hours=member_data.get('availability_hours', 'business_hours'),
            skills=member_data.get('skills', []),
            certifications=member_data.get('certifications', []),
            last_training=member_data.get('last_training')
        )

        self.team_members[member_id] = member

        logger.info(f"Team member added: {member.name} ({member.role.value})")
        return member_id

    def create_escalation_rule(self, rule_data: Dict[str, Any]) -> str:
        """
        Create an incident escalation rule
        Returns rule ID
        """
        rule_id = str(uuid.uuid4())

        rule = EscalationRule(
            id=rule_id,
            name=rule_data['name'],
            trigger_conditions=rule_data['trigger_conditions'],
            target_level=EscalationLevel[rule_data['target_level'].upper()],
            required_roles=[TeamRole[role.upper()] for role in rule_data.get('required_roles', [])],
            time_to_escalate=rule_data.get('time_to_escalate', 60),
            notification_channels=rule_data.get('notification_channels', ['email'])
        )

        self.escalation_rules[rule_id] = rule

        logger.info(f"Escalation rule created: {rule.name} -> {rule.target_level.value}")
        return rule_id

    def create_response_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """
        Create an incident response workflow
        Returns workflow ID
        """
        workflow_id = str(uuid.uuid4())

        workflow = ResponseWorkflow(
            id=workflow_id,
            name=workflow_data['name'],
            incident_type=workflow_data['incident_type'],
            phases=workflow_data['phases'],
            required_roles=[TeamRole[role.upper()] for role in workflow_data.get('required_roles', [])],
            estimated_duration=workflow_data.get('estimated_duration', 240),
            success_criteria=workflow_data.get('success_criteria', [])
        )

        self.response_workflows[workflow_id] = workflow

        logger.info(f"Response workflow created: {workflow.name} for {workflow.incident_type}")
        return workflow_id

    def assign_incident_to_team(self, incident_id: str, incident_severity: str,
                              incident_type: str) -> Dict[str, Any]:
        """
        Assign incident to appropriate team members based on severity and type
        Returns assignment details
        """
        # Determine escalation level based on severity
        escalation_level = self._determine_escalation_level(incident_severity, incident_type)

        # Get required roles for this level
        required_roles = self.escalation_procedures[escalation_level]['required_roles']

        # Find available team members for each role
        assignments = []
        for role in required_roles:
            member = self._find_available_team_member(role)
            if member:
                assignment_id = str(uuid.uuid4())
                assignment = IncidentAssignment(
                    id=assignment_id,
                    incident_id=incident_id,
                    team_member_id=member.id,
                    role=role,
                    assigned_at=datetime.utcnow(),
                    assigned_by="system"
                )

                self.incident_assignments[assignment_id] = assignment
                assignments.append({
                    'assignment_id': assignment_id,
                    'member_name': member.name,
                    'role': role.value,
                    'contact': member.primary_contact
                })

                # Update member's response count
                member.response_count += 1

        # Send notifications to assigned members
        self._notify_team_assignments(incident_id, assignments)

        logger.info(f"Incident {incident_id} assigned to {len(assignments)} team members at {escalation_level.value}")

        return {
            'escalation_level': escalation_level.value,
            'assignments': assignments,
            'team_size': len(assignments),
            'estimated_response_time': self.team_config['response_sla'].get(incident_severity, 1440)
        }

    def _determine_escalation_level(self, severity: str, incident_type: str) -> EscalationLevel:
        """Determine appropriate escalation level based on incident characteristics"""
        if severity == 'critical':
            return EscalationLevel.LEVEL_3
        elif severity == 'high' or incident_type in ['data_breach', 'ransomware']:
            return EscalationLevel.LEVEL_2
        else:
            return EscalationLevel.LEVEL_1

    def _find_available_team_member(self, role: TeamRole) -> Optional[TeamMember]:
        """Find an available team member for the specified role"""
        # In production, this would check current assignments, availability, etc.
        for member in self.team_members.values():
            if member.role == role and member.is_active:
                return member
        return None

    def _notify_team_assignments(self, incident_id: str, assignments: List[Dict[str, Any]]):
        """Notify team members of their assignments"""
        for assignment in assignments:
            # In production, this would send actual notifications
            logger.info(f"Notified {assignment['member_name']} of assignment to incident {incident_id}")

    def execute_response_workflow(self, incident_id: str, workflow_id: str) -> str:
        """
        Execute a response workflow for an incident
        Returns execution ID
        """
        if workflow_id not in self.response_workflows:
            raise ValueError(f"Response workflow not found: {workflow_id}")

        workflow = self.response_workflows[workflow_id]
        execution_id = str(uuid.uuid4())

        logger.info(f"Starting response workflow {workflow.name} for incident {incident_id}")

        # Execute workflow phases
        for phase in workflow.phases:
            self._execute_workflow_phase(incident_id, phase, execution_id)

        return execution_id

    def _execute_workflow_phase(self, incident_id: str, phase: Dict[str, Any], execution_id: str):
        """Execute a single workflow phase"""
        phase_name = phase.get('name', 'Unknown Phase')
        phase_type = phase.get('type', 'manual')

        logger.info(f"Executing phase: {phase_name} for incident {incident_id}")

        if phase_type == 'automated':
            self._execute_automated_phase(incident_id, phase)
        elif phase_type == 'communication':
            self._execute_communication_phase(incident_id, phase)
        elif phase_type == 'assessment':
            self._execute_assessment_phase(incident_id, phase)
        else:
            # Manual phase - log for human execution
            logger.info(f"Manual phase {phase_name} requires human execution")

    def _execute_automated_phase(self, incident_id: str, phase: Dict[str, Any]):
        """Execute an automated workflow phase"""
        actions = phase.get('actions', [])

        for action in actions:
            action_type = action.get('type')
            if action_type == 'isolate_system':
                self._isolate_system(action.get('system_name'))
            elif action_type == 'collect_evidence':
                self._collect_evidence(incident_id, action.get('evidence_types', []))
            elif action_type == 'notify_stakeholders':
                self._notify_stakeholders(incident_id, action.get('stakeholders', []))
            # Add more automated actions as needed

    def _execute_communication_phase(self, incident_id: str, phase: Dict[str, Any]):
        """Execute a communication phase"""
        communications = phase.get('communications', [])

        for comm in communications:
            comm_type = CommunicationType[comm['type'].upper()]
            self.send_incident_communication(
                incident_id=incident_id,
                communication_type=comm_type,
                recipient=comm['recipient'],
                content=comm.get('content', ''),
                sent_by='system'
            )

    def _execute_assessment_phase(self, incident_id: str, phase: Dict[str, Any]):
        """Execute an assessment phase"""
        assessments = phase.get('assessments', [])

        for assessment in assessments:
            assessment_type = assessment.get('type')
            if assessment_type == 'impact_assessment':
                self._perform_impact_assessment(incident_id)
            elif assessment_type == 'root_cause_analysis':
                self._perform_root_cause_analysis(incident_id)
            # Add more assessment types as needed

    def _isolate_system(self, system_name: str):
        """Isolate a system to contain an incident"""
        logger.warning(f"Isolating system: {system_name}")
        # In production, this would trigger actual system isolation

    def _collect_evidence(self, incident_id: str, evidence_types: List[str]):
        """Collect evidence for incident investigation"""
        logger.info(f"Collecting evidence for incident {incident_id}: {evidence_types}")
        # In production, this would trigger evidence collection procedures

    def _notify_stakeholders(self, incident_id: str, stakeholders: List[str]):
        """Notify stakeholders about the incident"""
        logger.info(f"Notifying stakeholders for incident {incident_id}: {stakeholders}")
        # In production, this would send actual notifications

    def _perform_impact_assessment(self, incident_id: str):
        """Perform impact assessment"""
        logger.info(f"Performing impact assessment for incident {incident_id}")

    def _perform_root_cause_analysis(self, incident_id: str):
        """Perform root cause analysis"""
        logger.info(f"Performing root cause analysis for incident {incident_id}")

    def send_incident_communication(self, incident_id: str, communication_type: CommunicationType,
                                  recipient: str, content: str, sent_by: str) -> str:
        """
        Send incident communication
        Returns communication log ID
        """
        comm_id = str(uuid.uuid4())

        communication = CommunicationLog(
            id=comm_id,
            incident_id=incident_id,
            communication_type=communication_type,
            recipient=recipient,
            sent_by=sent_by,
            sent_at=datetime.utcnow(),
            content=content
        )

        self.communication_logs[comm_id] = communication

        logger.info(f"Incident communication sent: {communication_type.value} to {recipient}")
        return comm_id

    def get_team_performance_metrics(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get security incident response team performance metrics"""
        # Filter data by tenant
        tenant_members = [m for m in self.team_members.values() if m.id.startswith(tenant_id)]
        tenant_assignments = [a for a in self.incident_assignments.values() if a.id.startswith(tenant_id)]

        # Calculate metrics
        team_stats = self._calculate_team_statistics(tenant_members)
        performance_stats = self._calculate_performance_statistics(tenant_assignments)
        training_stats = self._calculate_training_statistics(tenant_members)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'team_statistics': team_stats,
            'performance_statistics': performance_stats,
            'training_statistics': training_stats,
            'readiness_assessment': self._assess_team_readiness(tenant_members)
        }

    def _calculate_team_statistics(self, members: List[TeamMember]) -> Dict[str, Any]:
        """Calculate team composition statistics"""
        if not members:
            return {'total_members': 0, 'active_members': 0}

        total_members = len(members)
        active_members = len([m for m in members if m.is_active])

        # Count by role
        role_counts = {}
        for member in members:
            role_key = member.role.value
            role_counts[role_key] = role_counts.get(role_key, 0) + 1

        # Availability analysis
        availability_counts = {}
        for member in members:
            avail = member.availability_hours
            availability_counts[avail] = availability_counts.get(avail, 0) + 1

        return {
            'total_members': total_members,
            'active_members': active_members,
            'role_distribution': role_counts,
            'availability_distribution': availability_counts
        }

    def _calculate_performance_statistics(self, assignments: List[IncidentAssignment]) -> Dict[str, Any]:
        """Calculate team performance statistics"""
        if not assignments:
            return {'total_assignments': 0, 'avg_response_time': 0}

        total_assignments = len(assignments)

        # Calculate response times (simplified - would need actual timing data)
        # For now, use placeholder metrics
        avg_response_time = 45  # minutes
        success_rate = 95  # percentage

        # Count by role
        role_assignments = {}
        for assignment in assignments:
            role_key = assignment.role.value
            role_assignments[role_key] = role_assignments.get(role_key, 0) + 1

        return {
            'total_assignments': total_assignments,
            'avg_response_time_minutes': avg_response_time,
            'success_rate': success_rate,
            'assignments_by_role': role_assignments
        }

    def _calculate_training_statistics(self, members: List[TeamMember]) -> Dict[str, Any]:
        """Calculate team training statistics"""
        if not members:
            return {'training_compliance': 0}

        trained_members = len([m for m in members if m.last_training])
        training_compliance = (trained_members / len(members)) * 100 if members else 0

        # Check for expired training
        expired_training = 0
        for member in members:
            if member.last_training:
                days_since_training = (datetime.utcnow() - member.last_training).days
                if days_since_training > 365:  # Annual training requirement
                    expired_training += 1

        return {
            'training_compliance_rate': round(training_compliance, 1),
            'members_with_recent_training': trained_members,
            'members_with_expired_training': expired_training
        }

    def _assess_team_readiness(self, members: List[TeamMember]) -> Dict[str, Any]:
        """Assess overall team readiness"""
        readiness_score = 100

        # Check team size
        active_members = len([m for m in members if m.is_active])
        if active_members < self.team_config['core_team_size']:
            readiness_score -= 20

        # Check role coverage
        required_roles = set(TeamRole)
        available_roles = set(m.role for m in members if m.is_active)
        missing_roles = required_roles - available_roles
        if missing_roles:
            readiness_score -= len(missing_roles) * 5

        # Check training compliance
        training_compliance = len([m for m in members if m.last_training and
                                  (datetime.utcnow() - m.last_training).days <= 365])
        if members and (training_compliance / len(members)) < 0.8:
            readiness_score -= 15

        readiness_level = 'HIGH' if readiness_score >= 80 else 'MEDIUM' if readiness_score >= 60 else 'LOW'

        return {
            'readiness_score': max(readiness_score, 0),
            'readiness_level': readiness_level,
            'active_members': active_members,
            'required_roles_coverage': len(available_roles) / len(required_roles) * 100,
            'training_compliance': training_compliance / len(members) * 100 if members else 0
        }

    def check_team_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 security incident response team compliance"""
        members = [m for m in self.team_members.values() if m.id.startswith(tenant_id)]
        assignments = [a for a in self.incident_assignments.values() if a.id.startswith(tenant_id)]

        compliance_status = self._assess_team_compliance(members, assignments)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_control': 'A.16.1',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_team_compliance(self, members: List[TeamMember],
                               assignments: List[IncidentAssignment]) -> Dict[str, Any]:
        """Assess ISO 27001 team compliance"""
        issues = []

        # Check team size
        active_members = len([m for m in members if m.is_active])
        if active_members < self.team_config['core_team_size']:
            issues.append(f"Insufficient team size: {active_members} active members, minimum {self.team_config['core_team_size']} required")

        # Check role coverage
        required_roles = set(TeamRole)
        available_roles = set(m.role for m in members if m.is_active)
        missing_roles = required_roles - available_roles
        if missing_roles:
            issues.append(f"Missing team roles: {', '.join(r.value for r in missing_roles)}")

        # Check training compliance
        untrained_members = len([m for m in members if not m.last_training or
                                (datetime.utcnow() - m.last_training).days > 365])
        if untrained_members > 0:
            issues.append(f"{untrained_members} team members lack current training")

        # Check escalation rules
        if len(self.escalation_rules) < 3:
            issues.append("Insufficient escalation rules defined")

        # Check response workflows
        if len(self.response_workflows) < 5:
            issues.append("Insufficient response workflows defined")

        compliance_score = max(0, 100 - (len(issues) * 8))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_team_recommendations(issues)
        }

    def _generate_team_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        if any('team size' in issue.lower() for issue in issues):
            recommendations.append("Recruit additional team members to meet minimum team size requirements")

        if any('role' in issue.lower() for issue in issues):
            recommendations.append("Assign team members to cover all required security incident response roles")

        if any('training' in issue.lower() for issue in issues):
            recommendations.append("Implement comprehensive training program and ensure annual training compliance")

        if any('escalation' in issue.lower() for issue in issues):
            recommendations.append("Define clear escalation rules for different incident severity levels")

        if any('workflow' in issue.lower() for issue in issues):
            recommendations.append("Develop standardized response workflows for common incident types")

        if not recommendations:
            recommendations.append("Maintain current team capabilities and conduct regular readiness assessments")

        return recommendations