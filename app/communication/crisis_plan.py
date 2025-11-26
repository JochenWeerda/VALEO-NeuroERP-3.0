"""
ISO 22301 Crisis Communication Plan
Business Continuity Management System Crisis Communication

Dieses Modul implementiert den Crisis Communication Plan gemäß ISO 22301
für VALEO-NeuroERP mit Stakeholder Communication, Media Relations und Regulatory Reporting.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class CommunicationType(Enum):
    """Types of crisis communications"""
    INTERNAL_STAFF = "internal_staff"
    EXTERNAL_STAKEHOLDERS = "external_stakeholders"
    CUSTOMERS = "customers"
    REGULATORS = "regulators"
    MEDIA = "media"
    SUPPLIERS = "suppliers"
    LAW_ENFORCEMENT = "law_enforcement"
    INSURANCE = "insurance"


class CommunicationChannel(Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    PRESS_RELEASE = "press_release"
    SOCIAL_MEDIA = "social_media"
    WEBSITE = "website"
    NEWS_CONFERENCE = "news_conference"
    REGULATORY_FILING = "regulatory_filing"


class CommunicationPriority(Enum):
    """Communication priority levels"""
    CRITICAL = "critical"  # Immediate, < 15 minutes
    HIGH = "high"         # Urgent, < 1 hour
    MEDIUM = "medium"     # Important, < 4 hours
    LOW = "low"          # Routine, < 24 hours


class StakeholderGroup(Enum):
    """Stakeholder groups for communication"""
    EMPLOYEES = "employees"
    CUSTOMERS = "customers"
    SUPPLIERS = "suppliers"
    INVESTORS = "investors"
    REGULATORS = "regulators"
    MEDIA = "media"
    LAW_ENFORCEMENT = "law_enforcement"
    INSURANCE = "insurance"
    EXECUTIVES = "executives"
    BOARD_MEMBERS = "board_members"


@dataclass
class CommunicationTemplate:
    """Communication template for different scenarios"""
    id: str
    name: str
    communication_type: CommunicationType
    crisis_type: str
    priority: CommunicationPriority
    subject_template: str
    body_template: str
    required_fields: List[str]
    approval_required: bool = True
    legal_review_required: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None


@dataclass
class StakeholderContact:
    """Stakeholder contact information"""
    id: str
    stakeholder_group: StakeholderGroup
    name: str
    contact_info: Dict[str, Any]  # email, phone, address, etc.
    priority_level: CommunicationPriority
    language_preference: str = "de"
    special_instructions: str = ""
    is_active: bool = True
    last_contacted: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CommunicationLog:
    """Log of crisis communications"""
    id: str
    incident_id: str
    communication_type: CommunicationType
    stakeholder_group: StakeholderGroup
    channel: CommunicationChannel
    priority: CommunicationPriority
    subject: str
    content: str
    sent_by: str
    sent_at: datetime
    recipient_count: int
    delivery_status: str = "sent"
    response_count: int = 0
    feedback_received: str = ""
    approval_obtained: bool = False
    legal_review_completed: bool = False


@dataclass
class MediaResponse:
    """Media inquiry response tracking"""
    id: str
    incident_id: str
    inquiry_received: datetime
    media_outlet: str
    journalist_name: str
    inquiry_topic: str
    response_sent: Optional[datetime] = None
    response_content: str = ""
    spokesperson: str = ""
    follow_up_required: bool = False
    status: str = "pending"


@dataclass
class RegulatoryReporting:
    """Regulatory incident reporting"""
    id: str
    incident_id: str
    regulatory_body: str
    report_type: str
    reporting_deadline: datetime
    report_submitted: Optional[datetime] = None
    report_content: str = ""
    reference_number: str = ""
    status: str = "pending"
    follow_up_actions: List[str] = field(default_factory=list)


class ISO22301CrisisCommunicationPlan:
    """
    ISO 22301 Crisis Communication Plan
    Implements crisis communication and stakeholder management
    """

    def __init__(self, db_session, notification_service=None, template_engine=None):
        self.db = db_session
        self.notifications = notification_service
        self.templates = template_engine

        # Communication management
        self.communication_templates: Dict[str, CommunicationTemplate] = {}
        self.stakeholder_contacts: Dict[str, StakeholderContact] = {}
        self.communication_logs: List[CommunicationLog] = {}
        self.media_responses: List[MediaResponse] = {}
        self.regulatory_reports: List[RegulatoryReporting] = {}

        # Communication configuration
        self.communication_config = self._initialize_communication_config()

        # Stakeholder database
        self.stakeholder_db = self._initialize_stakeholder_database()

        # Regulatory requirements
        self.regulatory_requirements = self._initialize_regulatory_requirements()

    def _initialize_communication_config(self) -> Dict[str, Any]:
        """Initialize communication configuration"""
        return {
            'response_time_sla': {
                'critical': timedelta(minutes=15),
                'high': timedelta(hours=1),
                'medium': timedelta(hours=4),
                'low': timedelta(hours=24)
            },
            'approval_matrix': {
                'internal_staff': ['communication_lead'],
                'customers': ['communication_lead', 'executive'],
                'regulators': ['legal_counsel', 'executive'],
                'media': ['communication_lead', 'legal_counsel']
            },
            'communication_channels': {
                'primary': ['email', 'phone'],
                'secondary': ['sms', 'website'],
                'emergency': ['news_conference', 'social_media']
            },
            'languages_supported': ['de', 'en', 'fr'],
            'timezone_considerations': True
        }

    def _initialize_stakeholder_database(self) -> Dict[StakeholderGroup, List[Dict[str, Any]]]:
        """Initialize stakeholder contact database"""
        return {
            StakeholderGroup.EMPLOYEES: [
                {
                    'name': 'All Employees',
                    'contact_method': 'company_email',
                    'priority': CommunicationPriority.HIGH,
                    'estimated_count': 500
                }
            ],
            StakeholderGroup.CUSTOMERS: [
                {
                    'name': 'Key Account Customers',
                    'contact_method': 'direct_email',
                    'priority': CommunicationPriority.CRITICAL,
                    'estimated_count': 50
                },
                {
                    'name': 'General Customers',
                    'contact_method': 'website_notification',
                    'priority': CommunicationPriority.HIGH,
                    'estimated_count': 5000
                }
            ],
            StakeholderGroup.REGULATORS: [
                {
                    'name': 'Bundesamt für Sicherheit in der Informationstechnik (BSI)',
                    'contact_method': 'secure_email',
                    'priority': CommunicationPriority.CRITICAL,
                    'reporting_deadline': timedelta(hours=24)
                },
                {
                    'name': 'Datenschutzbehörde',
                    'contact_method': 'secure_email',
                    'priority': CommunicationPriority.CRITICAL,
                    'reporting_deadline': timedelta(hours=72)
                }
            ],
            StakeholderGroup.MEDIA: [
                {
                    'name': 'Financial Press',
                    'contact_method': 'press_release',
                    'priority': CommunicationPriority.HIGH,
                    'estimated_count': 20
                },
                {
                    'name': 'Technology Media',
                    'contact_method': 'press_release',
                    'priority': CommunicationPriority.MEDIUM,
                    'estimated_count': 15
                }
            ]
        }

    def _initialize_regulatory_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize regulatory reporting requirements"""
        return {
            'germany': {
                'bsi': {
                    'incident_reporting': timedelta(hours=24),
                    'data_breach_notification': timedelta(hours=72),
                    'contact': 'incident@bsi.bund.de'
                },
                'datenschutz': {
                    'data_breach_notification': timedelta(hours=72),
                    'contact': 'incident@datenschutz.de'
                }
            },
            'eu': {
                'gdpr': {
                    'data_breach_notification': timedelta(hours=72),
                    'supervisory_authority': True
                }
            },
            'financial': {
                'baffin': {
                    'incident_reporting': timedelta(hours=24),
                    'contact': 'incident@baffin.de'
                }
            }
        }

    def create_communication_template(self, template_data: Dict[str, Any]) -> str:
        """
        Create a communication template
        Returns template ID
        """
        template_id = str(uuid.uuid4())

        template = CommunicationTemplate(
            id=template_id,
            name=template_data['name'],
            communication_type=CommunicationType[template_data['communication_type'].upper()],
            crisis_type=template_data['crisis_type'],
            priority=CommunicationPriority[template_data['priority'].upper()],
            subject_template=template_data['subject_template'],
            body_template=template_data['body_template'],
            required_fields=template_data.get('required_fields', []),
            approval_required=template_data.get('approval_required', True),
            legal_review_required=template_data.get('legal_review_required', False)
        )

        self.communication_templates[template_id] = template

        logger.info(f"Communication template created: {template.name} for {template.crisis_type}")
        return template_id

    def register_stakeholder_contact(self, contact_data: Dict[str, Any]) -> str:
        """
        Register a stakeholder contact
        Returns contact ID
        """
        contact_id = str(uuid.uuid4())

        contact = StakeholderContact(
            id=contact_id,
            stakeholder_group=StakeholderGroup[contact_data['stakeholder_group'].upper()],
            name=contact_data['name'],
            contact_info=contact_data['contact_info'],
            priority_level=CommunicationPriority[contact_data.get('priority_level', 'MEDIUM').upper()],
            language_preference=contact_data.get('language_preference', 'de'),
            special_instructions=contact_data.get('special_instructions', '')
        )

        self.stakeholder_contacts[contact_id] = contact

        logger.info(f"Stakeholder contact registered: {contact.name} ({contact.stakeholder_group.value})")
        return contact_id

    def initiate_crisis_communication(self, incident_id: str, crisis_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate crisis communication for an incident
        Returns communication plan summary
        """
        crisis_type = crisis_details.get('crisis_type', 'general')
        severity = crisis_details.get('severity', 'medium')

        # Determine communication strategy
        communication_strategy = self._determine_communication_strategy(crisis_type, severity)

        # Generate communication plan
        communication_plan = self._generate_communication_plan(incident_id, crisis_details, communication_strategy)

        # Execute immediate communications
        immediate_communications = self._execute_immediate_communications(incident_id, communication_plan)

        # Schedule follow-up communications
        scheduled_communications = self._schedule_follow_up_communications(incident_id, communication_plan)

        logger.critical(f"Crisis communication initiated for incident {incident_id}: {len(immediate_communications)} immediate, {len(scheduled_communications)} scheduled")

        return {
            'incident_id': incident_id,
            'communication_strategy': communication_strategy,
            'immediate_communications': immediate_communications,
            'scheduled_communications': scheduled_communications,
            'regulatory_requirements': self._identify_regulatory_requirements(crisis_details),
            'status': 'communication_initiated'
        }

    def _determine_communication_strategy(self, crisis_type: str, severity: str) -> Dict[str, Any]:
        """Determine communication strategy based on crisis type and severity"""
        strategy = {
            'crisis_type': crisis_type,
            'severity': severity,
            'communication_priority': CommunicationPriority.HIGH,
            'channels': ['email', 'phone'],
            'timeline': {
                'immediate': timedelta(minutes=15),
                'follow_up': timedelta(hours=2),
                'detailed_update': timedelta(hours=24)
            }
        }

        # Adjust strategy based on crisis type
        if crisis_type == 'data_breach':
            strategy.update({
                'communication_priority': CommunicationPriority.CRITICAL,
                'channels': ['email', 'phone', 'website'],
                'legal_review_required': True,
                'regulatory_reporting_required': True
            })
        elif crisis_type == 'cyber_attack':
            strategy.update({
                'communication_priority': CommunicationPriority.CRITICAL,
                'channels': ['email', 'phone', 'press_release'],
                'technical_details_minimal': True
            })
        elif crisis_type == 'financial_impact':
            strategy.update({
                'communication_priority': CommunicationPriority.HIGH,
                'channels': ['email', 'phone', 'investor_call'],
                'financial_disclosure_required': True
            })

        return strategy

    def _generate_communication_plan(self, incident_id: str, crisis_details: Dict[str, Any],
                                   strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed communication plan"""
        plan = {
            'incident_id': incident_id,
            'crisis_type': crisis_details.get('crisis_type'),
            'severity': crisis_details.get('severity'),
            'communication_objectives': [
                'Inform affected stakeholders',
                'Maintain trust and confidence',
                'Provide accurate information',
                'Comply with regulatory requirements'
            ],
            'key_messages': self._generate_key_messages(crisis_details),
            'communication_sequence': [],
            'stakeholder_segments': [],
            'contingency_plans': []
        }

        # Define communication sequence
        plan['communication_sequence'] = [
            {
                'phase': 'immediate',
                'timeline': 'within 15 minutes',
                'audience': ['internal_team', 'executives'],
                'content': 'Initial notification and assessment'
            },
            {
                'phase': 'early',
                'timeline': 'within 1 hour',
                'audience': ['key_stakeholders', 'regulators'],
                'content': 'Detailed impact assessment and initial response'
            },
            {
                'phase': 'ongoing',
                'timeline': 'every 4-6 hours',
                'audience': ['all_stakeholders'],
                'content': 'Progress updates and recovery status'
            },
            {
                'phase': 'resolution',
                'timeline': 'upon resolution',
                'audience': ['all_stakeholders'],
                'content': 'Final resolution and lessons learned'
            }
        ]

        # Define stakeholder segments
        plan['stakeholder_segments'] = [
            {
                'group': 'internal',
                'priority': 'critical',
                'communication_method': 'immediate_notification',
                'frequency': 'continuous'
            },
            {
                'group': 'customers',
                'priority': 'high',
                'communication_method': 'personalized_notification',
                'frequency': 'regular_updates'
            },
            {
                'group': 'regulators',
                'priority': 'critical',
                'communication_method': 'formal_reporting',
                'frequency': 'as_required'
            },
            {
                'group': 'media',
                'priority': 'medium',
                'communication_method': 'press_release',
                'frequency': 'as_needed'
            }
        ]

        return plan

    def _generate_key_messages(self, crisis_details: Dict[str, Any]) -> List[str]:
        """Generate key messages for the crisis"""
        crisis_type = crisis_details.get('crisis_type', 'general')

        base_messages = [
            "We are experiencing an incident and are actively working to resolve it",
            "Customer data and operations are our top priority",
            "We are following established incident response procedures",
            "We will provide regular updates as the situation develops"
        ]

        if crisis_type == 'data_breach':
            base_messages.extend([
                "We have identified a potential security incident",
                "We are working with authorities to investigate",
                "Affected customers will be notified individually",
                "We recommend monitoring accounts for suspicious activity"
            ])
        elif crisis_type == 'cyber_attack':
            base_messages.extend([
                "We have detected unauthorized access attempts",
                "Our security team is actively responding",
                "Business operations continue with enhanced security measures",
                "We are coordinating with law enforcement"
            ])

        return base_messages

    def _execute_immediate_communications(self, incident_id: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute immediate crisis communications"""
        immediate_comms = []

        # Internal team notification
        internal_comm = self._send_communication(
            incident_id=incident_id,
            communication_type=CommunicationType.INTERNAL_STAFF,
            stakeholder_group=StakeholderGroup.EMPLOYEES,
            channel=CommunicationChannel.EMAIL,
            priority=CommunicationPriority.CRITICAL,
            subject="URGENT: Security Incident Notification",
            content=self._generate_internal_notification(plan),
            sent_by="crisis_communication_system"
        )
        immediate_comms.append(internal_comm)

        # Executive notification
        executive_comm = self._send_communication(
            incident_id=incident_id,
            communication_type=CommunicationType.INTERNAL_STAFF,
            stakeholder_group=StakeholderGroup.EXECUTIVES,
            channel=CommunicationChannel.PHONE,
            priority=CommunicationPriority.CRITICAL,
            subject="Executive Crisis Notification",
            content=self._generate_executive_notification(plan),
            sent_by="crisis_communication_system"
        )
        immediate_comms.append(executive_comm)

        return immediate_comms

    def _schedule_follow_up_communications(self, incident_id: str, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Schedule follow-up communications"""
        scheduled_comms = []

        # Schedule regulatory reporting
        regulatory_deadlines = self._identify_regulatory_requirements(plan)
        for requirement in regulatory_deadlines:
            scheduled_comm = {
                'incident_id': incident_id,
                'type': 'regulatory_reporting',
                'deadline': requirement['deadline'],
                'recipient': requirement['authority'],
                'status': 'scheduled'
            }
            scheduled_comms.append(scheduled_comm)

        # Schedule customer communication
        customer_comm = {
            'incident_id': incident_id,
            'type': 'customer_notification',
            'scheduled_time': datetime.utcnow() + timedelta(hours=4),
            'audience': 'affected_customers',
            'status': 'scheduled'
        }
        scheduled_comms.append(customer_comm)

        return scheduled_comms

    def _send_communication(self, incident_id: str, communication_type: CommunicationType,
                          stakeholder_group: StakeholderGroup, channel: CommunicationChannel,
                          priority: CommunicationPriority, subject: str, content: str,
                          sent_by: str) -> Dict[str, Any]:
        """Send a communication and log it"""
        comm_id = str(uuid.uuid4())

        # In production, this would actually send the communication
        # For now, simulate sending

        communication = CommunicationLog(
            id=comm_id,
            incident_id=incident_id,
            communication_type=communication_type,
            stakeholder_group=stakeholder_group,
            channel=channel,
            priority=priority,
            subject=subject,
            content=content,
            sent_by=sent_by,
            sent_at=datetime.utcnow(),
            recipient_count=self._estimate_recipient_count(stakeholder_group),
            delivery_status="sent"
        )

        self.communication_logs[comm_id] = communication

        logger.info(f"Communication sent: {communication_type.value} to {stakeholder_group.value} via {channel.value}")

        return {
            'communication_id': comm_id,
            'type': communication_type.value,
            'stakeholder_group': stakeholder_group.value,
            'channel': channel.value,
            'priority': priority.value,
            'sent_at': communication.sent_at.isoformat(),
            'recipient_count': communication.recipient_count
        }

    def _estimate_recipient_count(self, stakeholder_group: StakeholderGroup) -> int:
        """Estimate number of recipients for a stakeholder group"""
        estimates = {
            StakeholderGroup.EMPLOYEES: 500,
            StakeholderGroup.CUSTOMERS: 1000,
            StakeholderGroup.EXECUTIVES: 10,
            StakeholderGroup.REGULATORS: 5,
            StakeholderGroup.MEDIA: 25
        }
        return estimates.get(stakeholder_group, 0)

    def _generate_internal_notification(self, plan: Dict[str, Any]) -> str:
        """Generate internal staff notification"""
        return f"""
        URGENT SECURITY INCIDENT NOTIFICATION

        Incident Type: {plan.get('crisis_type', 'Unknown')}
        Severity: {plan.get('severity', 'Unknown')}

        Our organization is experiencing a security incident. All teams should:

        1. Remain calm and follow normal procedures unless directed otherwise
        2. Do not discuss the incident with external parties
        3. Await further instructions from the Crisis Communication Team
        4. Report any suspicious activity immediately

        Updates will be provided as the situation develops.

        Crisis Communication Team
        """

    def _generate_executive_notification(self, plan: Dict[str, Any]) -> str:
        """Generate executive notification"""
        return f"""
        EXECUTIVE CRISIS BRIEFING

        Incident Summary:
        - Type: {plan.get('crisis_type', 'Unknown')}
        - Severity: {plan.get('severity', 'Unknown')}
        - Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

        Immediate Actions Required:
        1. Crisis Management Team activation
        2. Stakeholder communication approval
        3. Regulatory notification preparation

        Please standby for detailed briefing call.

        Crisis Management Coordinator
        """

    def _identify_regulatory_requirements(self, crisis_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify regulatory reporting requirements"""
        requirements = []

        crisis_type = crisis_details.get('crisis_type', '')

        if 'data_breach' in crisis_type or 'cyber' in crisis_type:
            # GDPR requirements
            requirements.append({
                'authority': 'Data Protection Authority',
                'requirement': 'Data Breach Notification',
                'deadline': datetime.utcnow() + timedelta(hours=72),
                'jurisdiction': 'EU/Germany'
            })

            # BSI requirements
            requirements.append({
                'authority': 'BSI (Federal Office for Information Security)',
                'requirement': 'Cyber Incident Reporting',
                'deadline': datetime.utcnow() + timedelta(hours=24),
                'jurisdiction': 'Germany'
            })

        if 'financial' in crisis_type:
            requirements.append({
                'authority': 'BaFin (Federal Financial Supervisory Authority)',
                'requirement': 'Financial Incident Reporting',
                'deadline': datetime.utcnow() + timedelta(hours=24),
                'jurisdiction': 'Germany'
            })

        return requirements

    def handle_media_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """
        Handle media inquiry during crisis
        Returns response ID
        """
        response_id = str(uuid.uuid4())

        inquiry = MediaResponse(
            id=response_id,
            incident_id=inquiry_data['incident_id'],
            inquiry_received=datetime.utcnow(),
            media_outlet=inquiry_data['media_outlet'],
            journalist_name=inquiry_data.get('journalist_name', ''),
            inquiry_topic=inquiry_data['inquiry_topic']
        )

        self.media_responses.append(inquiry)

        # Generate and send response
        response_content = self._generate_media_response(inquiry)
        inquiry.response_content = response_content
        inquiry.response_sent = datetime.utcnow()
        inquiry.spokesperson = inquiry_data.get('spokesperson', 'Communication Team')

        logger.info(f"Media inquiry handled: {inquiry.media_outlet} - {inquiry.inquiry_topic}")

        return response_id

    def _generate_media_response(self, inquiry: MediaResponse) -> str:
        """Generate media response based on inquiry"""
        base_response = f"""
        Official Statement from VALEO-NeuroERP

        Regarding your inquiry about recent events:

        VALEO-NeuroERP takes information security very seriously. We are currently
        managing a security incident and are working diligently to resolve it.

        Key Points:
        - We detected the incident promptly and activated our response procedures
        - Our teams are working around the clock to contain and resolve the situation
        - Customer data protection remains our highest priority
        - We are cooperating fully with relevant authorities

        We will provide additional updates as appropriate. For privacy and security
        reasons, we cannot comment on specific technical details at this time.

        For further information, please contact our Communications Team.

        VALEO-NeuroERP Communications
        {datetime.utcnow().strftime('%Y-%m-%d')}
        """

        return base_response

    def submit_regulatory_report(self, report_data: Dict[str, Any]) -> str:
        """
        Submit regulatory incident report
        Returns report ID
        """
        report_id = str(uuid.uuid4())

        report = RegulatoryReporting(
            id=report_id,
            incident_id=report_data['incident_id'],
            regulatory_body=report_data['regulatory_body'],
            report_type=report_data['report_type'],
            reporting_deadline=report_data.get('reporting_deadline', datetime.utcnow() + timedelta(hours=72)),
            report_content=report_data.get('report_content', ''),
            status='submitted',
            report_submitted=datetime.utcnow()
        )

        self.regulatory_reports.append(report)

        logger.info(f"Regulatory report submitted to {report.regulatory_body}: {report.report_type}")

        return report_id

    def get_communication_status(self, incident_id: str = None, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive communication status"""
        # Filter data by incident or tenant
        if incident_id:
            relevant_logs = [log for log in self.communication_logs.values() if log.incident_id == incident_id]
            relevant_media = [resp for resp in self.media_responses if resp.incident_id == incident_id]
            relevant_reports = [rep for rep in self.regulatory_reports if rep.incident_id == incident_id]
        else:
            relevant_logs = list(self.communication_logs.values())
            relevant_media = self.media_responses
            relevant_reports = self.regulatory_reports

        # Calculate metrics
        communication_stats = self._calculate_communication_statistics(relevant_logs)
        media_stats = self._calculate_media_statistics(relevant_media)
        regulatory_stats = self._calculate_regulatory_statistics(relevant_reports)
        effectiveness_metrics = self._assess_communication_effectiveness(relevant_logs)

        return {
            'incident_id': incident_id,
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'communication_statistics': communication_stats,
            'media_statistics': media_stats,
            'regulatory_statistics': regulatory_stats,
            'effectiveness_metrics': effectiveness_metrics,
            'active_communications': len([log for log in relevant_logs if log.delivery_status == 'sent'])
        }

    def _calculate_communication_statistics(self, logs: List[CommunicationLog]) -> Dict[str, Any]:
        """Calculate communication statistics"""
        if not logs:
            return {'total_communications': 0, 'success_rate': 0}

        total = len(logs)
        successful = len([log for log in logs if log.delivery_status == 'sent'])

        # Breakdown by type and stakeholder
        by_type = {}
        by_stakeholder = {}

        for log in logs:
            type_key = log.communication_type.value
            stakeholder_key = log.stakeholder_group.value

            by_type[type_key] = by_type.get(type_key, 0) + 1
            by_stakeholder[stakeholder_key] = by_stakeholder.get(stakeholder_key, 0) + 1

        return {
            'total_communications': total,
            'successful_deliveries': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'by_communication_type': by_type,
            'by_stakeholder_group': by_stakeholder,
            'average_response_time': self._calculate_average_response_time(logs)
        }

    def _calculate_average_response_time(self, logs: List[CommunicationLog]) -> float:
        """Calculate average response time for communications"""
        response_times = []
        for log in logs:
            if hasattr(log, 'response_received') and log.response_received:
                response_time = (log.response_received - log.sent_at).total_seconds() / 3600  # hours
                response_times.append(response_time)

        return sum(response_times) / len(response_times) if response_times else 0

    def _calculate_media_statistics(self, responses: List[MediaResponse]) -> Dict[str, Any]:
        """Calculate media response statistics"""
        if not responses:
            return {'total_inquiries': 0, 'response_rate': 0}

        total = len(responses)
        responded = len([resp for resp in responses if resp.response_sent])

        # Breakdown by media outlet
        by_outlet = {}
        for resp in responses:
            outlet = resp.media_outlet
            by_outlet[outlet] = by_outlet.get(outlet, {'total': 0, 'responded': 0})
            by_outlet[outlet]['total'] += 1
            if resp.response_sent:
                by_outlet[outlet]['responded'] += 1

        return {
            'total_inquiries': total,
            'responded_inquiries': responded,
            'response_rate': (responded / total * 100) if total > 0 else 0,
            'by_media_outlet': by_outlet,
            'average_response_time': self._calculate_media_response_time(responses)
        }

    def _calculate_media_response_time(self, responses: List[MediaResponse]) -> float:
        """Calculate average media response time"""
        response_times = []
        for resp in responses:
            if resp.response_sent:
                response_time = (resp.response_sent - resp.inquiry_received).total_seconds() / 3600  # hours
                response_times.append(response_time)

        return sum(response_times) / len(response_times) if response_times else 0

    def _calculate_regulatory_statistics(self, reports: List[RegulatoryReporting]) -> Dict[str, Any]:
        """Calculate regulatory reporting statistics"""
        if not reports:
            return {'total_reports': 0, 'compliance_rate': 0}

        total = len(reports)
        submitted = len([rep for rep in reports if rep.status == 'submitted'])
        on_time = len([rep for rep in reports if rep.report_submitted and
                      rep.report_submitted <= rep.reporting_deadline])

        return {
            'total_reports': total,
            'submitted_reports': submitted,
            'on_time_submissions': on_time,
            'compliance_rate': (on_time / total * 100) if total > 0 else 0,
            'by_regulatory_body': self._group_reports_by_body(reports)
        }

    def _group_reports_by_body(self, reports: List[RegulatoryReporting]) -> Dict[str, int]:
        """Group reports by regulatory body"""
        by_body = {}
        for rep in reports:
            body = rep.regulatory_body
            by_body[body] = by_body.get(body, 0) + 1
        return by_body

    def _assess_communication_effectiveness(self, logs: List[CommunicationLog]) -> Dict[str, Any]:
        """Assess communication effectiveness"""
        effectiveness_score = 100

        if not logs:
            return {'effectiveness_score': 0, 'issues': ['No communication data available']}

        # Check response rates
        response_rate = len([log for log in logs if log.response_count > 0]) / len(logs)
        if response_rate < 0.3:  # Less than 30% response rate
            effectiveness_score -= 20

        # Check delivery success
        delivery_rate = len([log for log in logs if log.delivery_status == 'sent']) / len(logs)
        if delivery_rate < 0.95:  # Less than 95% delivery success
            effectiveness_score -= 15

        # Check timeliness (simplified)
        timely_communications = len([log for log in logs if self._check_timeliness(log)])
        timeliness_rate = timely_communications / len(logs)
        if timeliness_rate < 0.8:
            effectiveness_score -= 10

        issues = []
        if response_rate < 0.3:
            issues.append("Low stakeholder response rate")
        if delivery_rate < 0.95:
            issues.append("Communication delivery failures")
        if timeliness_rate < 0.8:
            issues.append("Delayed communications")

        return {
            'effectiveness_score': max(effectiveness_score, 0),
            'response_rate': response_rate * 100,
            'delivery_rate': delivery_rate * 100,
            'timeliness_rate': timeliness_rate * 100,
            'issues': issues,
            'recommendations': self._generate_communication_recommendations(issues)
        }

    def _check_timeliness(self, log: CommunicationLog) -> bool:
        """Check if communication was sent in timely manner"""
        # Simplified timeliness check based on priority
        sla = self.communication_config['response_time_sla'].get(log.priority.value, timedelta(hours=24))
        time_taken = datetime.utcnow() - log.sent_at

        return time_taken <= sla

    def _generate_communication_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on communication issues"""
        recommendations = []

        if any('response' in issue.lower() for issue in issues):
            recommendations.append("Improve stakeholder engagement and follow-up procedures")

        if any('delivery' in issue.lower() for issue in issues):
            recommendations.append("Review and optimize communication channels and delivery methods")

        if any('delayed' in issue.lower() for issue in issues):
            recommendations.append("Streamline communication approval and distribution processes")

        if not recommendations:
            recommendations.append("Maintain current communication standards and continue monitoring effectiveness")

        return recommendations

    def check_crisis_communication_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 22301 crisis communication compliance"""
        templates = [t for t in self.communication_templates.values() if t.id.startswith(tenant_id)]
        contacts = [c for c in self.stakeholder_contacts.values() if c.id.startswith(tenant_id)]
        logs = [log for log in self.communication_logs.values() if log.id.startswith(tenant_id)]

        compliance_status = self._assess_communication_compliance(templates, contacts, logs)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_standard': 'ISO 22301',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_communication_compliance(self, templates: List[CommunicationTemplate],
                                       contacts: List[StakeholderContact],
                                       logs: List[CommunicationLog]) -> Dict[str, Any]:
        """Assess ISO 22301 communication compliance"""
        issues = []

        # Check template coverage
        if len(templates) < 5:
            issues.append("Insufficient communication templates for different crisis types")

        # Check stakeholder contact completeness
        required_groups = set(StakeholderGroup)
        available_groups = set(c.stakeholder_group for c in contacts)
        missing_groups = required_groups - available_groups
        if missing_groups:
            issues.append(f"Missing stakeholder contacts for: {', '.join(g.value for g in missing_groups)}")

        # Check communication logs for completeness
        if logs:
            approval_rate = len([log for log in logs if log.approval_obtained]) / len(logs)
            if approval_rate < 0.9:  # Less than 90% approval rate
                issues.append("Inadequate communication approval processes")

        compliance_score = max(0, 100 - (len(issues) * 10))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_compliance_recommendations(issues)
        }

    def _generate_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if any('template' in issue.lower() for issue in issues):
            recommendations.append("Develop comprehensive communication templates for all crisis scenarios")

        if any('stakeholder' in issue.lower() for issue in issues):
            recommendations.append("Complete stakeholder contact database with all required groups")

        if any('approval' in issue.lower() for issue in issues):
            recommendations.append("Strengthen communication approval and review processes")

        if not recommendations:
            recommendations.append("Maintain current compliance standards and conduct regular audits")

        return recommendations