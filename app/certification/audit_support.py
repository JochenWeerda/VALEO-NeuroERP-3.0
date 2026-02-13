"""
ISO Certification Preparation and Audit Support
Comprehensive Audit Support Framework for ISO 27001, ISO 9001, and ISO 22301

Dieses Modul implementiert das Certification Preparation and Audit Support Framework
für VALEO-NeuroERP mit Audit Evidence Management, Certification Application Support,
Audit Readiness Assessment und Compliance Documentation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class CertificationStandard(Enum):
    """Supported certification standards"""
    ISO_27001 = "ISO 27001:2022"
    ISO_9001 = "ISO 9001:2015"
    ISO_22301 = "ISO 22301:2019"
    ISO_14001 = "ISO 14001:2015"
    ISO_45001 = "ISO 45001:2018"


class AuditType(Enum):
    """Types of audits"""
    INTERNAL_AUDIT = "internal_audit"
    EXTERNAL_AUDIT = "external_audit"
    CERTIFICATION_AUDIT = "certification_audit"
    SURVEILLANCE_AUDIT = "surveillance_audit"
    RECERTIFICATION_AUDIT = "recertification_audit"


class AuditPhase(Enum):
    """Audit phases"""
    PLANNING = "planning"
    FIELDWORK = "fieldwork"
    REPORTING = "reporting"
    CORRECTIVE_ACTIONS = "corrective_actions"
    CLOSURE = "closure"


class EvidenceType(Enum):
    """Types of audit evidence"""
    DOCUMENTARY = "documentary"
    INTERVIEW = "interview"
    OBSERVATION = "observation"
    PHYSICAL = "physical"
    DIGITAL = "digital"
    TEST_RESULTS = "test_results"


class ComplianceStatus(Enum):
    """Compliance assessment status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    NOT_ASSESSED = "not_assessed"


@dataclass
class AuditEvidence:
    """Audit evidence record"""
    id: str
    audit_id: str
    control_id: str
    evidence_type: EvidenceType
    description: str
    location: str
    collected_by: str
    collected_at: datetime
    validity_period: Optional[timedelta] = None
    digital_signature: Optional[str] = None
    blockchain_hash: Optional[str] = None
    is_valid: bool = True
    validation_notes: str = ""


@dataclass
class AuditFinding:
    """Audit finding record"""
    id: str
    audit_id: str
    control_id: str
    finding_type: str  # major, minor, observation
    severity: str
    description: str
    root_cause: str
    impact_assessment: str
    corrective_action_required: bool
    preventive_action_required: bool
    deadline: datetime
    assigned_to: str
    status: str = "open"
    evidence_ids: List[str] = field(default_factory=list)


@dataclass
class AuditPlan:
    """Audit plan and schedule"""
    id: str
    audit_type: AuditType
    certification_standard: CertificationStandard
    scope: str
    objectives: List[str]
    planned_start_date: datetime
    planned_end_date: datetime
    lead_auditor: str
    audit_team: List[str]
    audit_criteria: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    status: str = "planned"


@dataclass
class AuditExecution:
    """Audit execution record"""
    id: str
    audit_plan_id: str
    current_phase: AuditPhase
    started_at: datetime
    completed_at: Optional[datetime] = None
    findings: List[AuditFinding] = field(default_factory=list)
    evidence_collected: List[AuditEvidence] = field(default_factory=list)
    compliance_assessment: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    status: str = "in_progress"


@dataclass
class CertificationApplication:
    """Certification application record"""
    id: str
    certification_standard: CertificationStandard
    certification_body: str
    application_date: datetime
    scope_statement: str
    management_system_description: str
    quality_policy: str
    quality_objectives: List[str]
    internal_audit_results: Dict[str, Any]
    management_review_results: Dict[str, Any]
    required_documents: List[str]
    application_fee: float
    status: str = "draft"
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None


@dataclass
class ComplianceAssessment:
    """Compliance assessment for certification"""
    id: str
    certification_standard: CertificationStandard
    assessment_date: datetime
    assessed_by: str
    scope: str
    overall_compliance_score: float
    control_assessments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    gaps_identified: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    readiness_level: str = "not_assessed"
    estimated_certification_date: Optional[datetime] = None


@dataclass
class AuditReadinessChecklist:
    """Audit readiness checklist"""
    id: str
    certification_standard: CertificationStandard
    checklist_items: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completion_percentage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    responsible_party: str = ""


class ISOCertificationAuditSupport:
    """
    ISO Certification Preparation and Audit Support
    Comprehensive framework for ISO certification audits
    """

    def __init__(self, db_session, evidence_service=None, compliance_service=None):
        self.db = db_session
        self.evidence = evidence_service
        self.compliance = compliance_service

        # Audit management
        self.audit_plans: Dict[str, AuditPlan] = {}
        self.audit_executions: Dict[str, AuditExecution] = {}
        self.audit_evidence: List[AuditEvidence] = {}
        self.audit_findings: List[AuditFinding] = {}

        # Certification management
        self.certification_applications: Dict[str, CertificationApplication] = {}
        self.compliance_assessments: List[ComplianceAssessment] = {}
        self.readiness_checklists: Dict[str, AuditReadinessChecklist] = {}

        # Certification standards configuration
        self.certification_standards = self._initialize_certification_standards()

        # Audit checklists
        self.audit_checklists = self._initialize_audit_checklists()

    def _initialize_certification_standards(self) -> Dict[CertificationStandard, Dict[str, Any]]:
        """Initialize certification standards configuration"""
        return {
            CertificationStandard.ISO_27001: {
                'name': 'Information Security Management Systems',
                'version': '2022',
                'controls': 93,
                'annexes': ['A.5-A.18'],
                'certification_bodies': ['BSI', 'TÜV', 'DNV', 'Lloyd\'s Register'],
                'validity_period': 3,  # years
                'surveillance_frequency': 12,  # months
                'transition_period': 36  # months from 2013 version
            },
            CertificationStandard.ISO_9001: {
                'name': 'Quality Management Systems',
                'version': '2015',
                'controls': 10,
                'annexes': ['A.4-A.10'],
                'certification_bodies': ['TÜV', 'DNV', 'SGS', 'Bureau Veritas'],
                'validity_period': 3,
                'surveillance_frequency': 12,
                'transition_period': 36
            },
            CertificationStandard.ISO_22301: {
                'name': 'Business Continuity Management Systems',
                'version': '2019',
                'controls': 10,
                'annexes': ['A.4-A.10'],
                'certification_bodies': ['BSI', 'TÜV', 'DNV'],
                'validity_period': 3,
                'surveillance_frequency': 12,
                'transition_period': 36
            }
        }

    def _initialize_audit_checklists(self) -> Dict[CertificationStandard, Dict[str, Any]]:
        """Initialize audit checklists for each standard"""
        return {
            CertificationStandard.ISO_27001: {
                'context_of_organization': ['A.4', 'A.5', 'A.6'],
                'leadership': ['A.7', 'A.8', 'A.9'],
                'planning': ['A.10', 'A.11', 'A.12'],
                'support': ['A.13', 'A.14', 'A.15'],
                'operation': ['A.16', 'A.17', 'A.18'],
                'performance_evaluation': ['A.19'],
                'improvement': ['A.20']
            },
            CertificationStandard.ISO_9001: {
                'context_of_organization': ['4.1', '4.2', '4.3'],
                'leadership': ['5.1', '5.2'],
                'planning': ['6.1', '6.2', '6.3'],
                'support': ['7.1', '7.2', '7.3', '7.4', '7.5'],
                'operation': ['8.1', '8.2', '8.3'],
                'performance_evaluation': ['9.1', '9.2', '9.3'],
                'improvement': ['10.1', '10.2', '10.3']
            },
            CertificationStandard.ISO_22301: {
                'context_of_organization': ['4.1', '4.2', '4.3'],
                'leadership': ['5.1', '5.2'],
                'planning': ['6.1', '6.2', '6.3'],
                'support': ['7.1', '7.2', '7.3', '7.4'],
                'operation': ['8.1', '8.2', '8.3'],
                'performance_evaluation': ['9.1', '9.2', '9.3'],
                'improvement': ['10.1', '10.2', '10.3']
            }
        }

    def create_audit_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Create an audit plan
        Returns plan ID
        """
        plan_id = str(uuid.uuid4())

        plan = AuditPlan(
            id=plan_id,
            audit_type=AuditType[plan_data['audit_type'].upper()],
            certification_standard=CertificationStandard[plan_data['certification_standard'].upper()],
            scope=plan_data['scope'],
            objectives=plan_data.get('objectives', []),
            planned_start_date=plan_data['planned_start_date'],
            planned_end_date=plan_data['planned_end_date'],
            lead_auditor=plan_data['lead_auditor'],
            audit_team=plan_data.get('audit_team', []),
            audit_criteria=plan_data.get('audit_criteria', {}),
            risk_assessment=plan_data.get('risk_assessment', {}),
            resource_requirements=plan_data.get('resource_requirements', {})
        )

        self.audit_plans[plan_id] = plan

        logger.info(f"Audit plan created: {plan.audit_type.value} for {plan.certification_standard.value}")
        return plan_id

    def start_audit_execution(self, plan_id: str) -> str:
        """
        Start audit execution
        Returns execution ID
        """
        if plan_id not in self.audit_plans:
            raise ValueError(f"Audit plan not found: {plan_id}")

        execution_id = str(uuid.uuid4())

        execution = AuditExecution(
            id=execution_id,
            audit_plan_id=plan_id,
            current_phase=AuditPhase.PLANNING,
            started_at=datetime.utcnow()
        )

        self.audit_executions[execution_id] = execution

        # Update plan status
        self.audit_plans[plan_id].status = "in_progress"

        logger.info(f"Audit execution started for plan: {plan_id}")
        return execution_id

    def collect_audit_evidence(self, execution_id: str, evidence_data: Dict[str, Any]) -> str:
        """
        Collect audit evidence
        Returns evidence ID
        """
        if execution_id not in self.audit_executions:
            raise ValueError(f"Audit execution not found: {execution_id}")

        evidence_id = str(uuid.uuid4())

        evidence = AuditEvidence(
            id=evidence_id,
            audit_id=execution_id,
            control_id=evidence_data['control_id'],
            evidence_type=EvidenceType[evidence_data['evidence_type'].upper()],
            description=evidence_data['description'],
            location=evidence_data['location'],
            collected_by=evidence_data['collected_by'],
            collected_at=datetime.utcnow(),
            validity_period=evidence_data.get('validity_period'),
            digital_signature=evidence_data.get('digital_signature'),
            blockchain_hash=evidence_data.get('blockchain_hash')
        )

        if evidence_id not in self.audit_evidence:
            self.audit_evidence[evidence_id] = []

        self.audit_evidence[evidence_id].append(evidence)

        # Add to execution
        execution = self.audit_executions[execution_id]
        execution.evidence_collected.append(evidence)

        logger.info(f"Audit evidence collected: {evidence.evidence_type.value} for control {evidence.control_id}")
        return evidence_id

    def record_audit_finding(self, execution_id: str, finding_data: Dict[str, Any]) -> str:
        """
        Record an audit finding
        Returns finding ID
        """
        if execution_id not in self.audit_executions:
            raise ValueError(f"Audit execution not found: {execution_id}")

        finding_id = str(uuid.uuid4())

        finding = AuditFinding(
            id=finding_id,
            audit_id=execution_id,
            control_id=finding_data['control_id'],
            finding_type=finding_data['finding_type'],
            severity=finding_data['severity'],
            description=finding_data['description'],
            root_cause=finding_data.get('root_cause', ''),
            impact_assessment=finding_data.get('impact_assessment', ''),
            corrective_action_required=finding_data.get('corrective_action_required', True),
            preventive_action_required=finding_data.get('preventive_action_required', False),
            deadline=finding_data['deadline'],
            assigned_to=finding_data['assigned_to'],
            evidence_ids=finding_data.get('evidence_ids', [])
        )

        self.audit_findings.append(finding)

        # Add to execution
        execution = self.audit_executions[execution_id]
        execution.findings.append(finding)

        logger.warning(f"Audit finding recorded: {finding.finding_type} severity for control {finding.control_id}")
        return finding_id

    def assess_control_compliance(self, execution_id: str, control_id: str,
                                assessment_data: Dict[str, Any]) -> bool:
        """
        Assess compliance of a specific control
        """
        if execution_id not in self.audit_executions:
            raise ValueError(f"Audit execution not found: {execution_id}")

        execution = self.audit_executions[execution_id]

        assessment = {
            'control_id': control_id,
            'compliance_status': assessment_data['compliance_status'],
            'evidence_reviewed': assessment_data.get('evidence_reviewed', []),
            'compliance_score': assessment_data.get('compliance_score', 0),
            'notes': assessment_data.get('notes', ''),
            'assessed_at': datetime.utcnow().isoformat(),
            'assessed_by': assessment_data.get('assessed_by', 'system')
        }

        if 'control_assessments' not in execution.compliance_assessment:
            execution.compliance_assessment['control_assessments'] = {}

        execution.compliance_assessment['control_assessments'][control_id] = assessment

        logger.info(f"Control compliance assessed: {control_id} - {assessment['compliance_status']}")
        return True

    def complete_audit_execution(self, execution_id: str, completion_data: Dict[str, Any]) -> bool:
        """
        Complete audit execution
        """
        if execution_id not in self.audit_executions:
            return False

        execution = self.audit_executions[execution_id]
        execution.completed_at = datetime.utcnow()
        execution.status = "completed"
        execution.recommendations = completion_data.get('recommendations', [])

        # Calculate overall compliance
        execution.compliance_assessment['overall_compliance'] = self._calculate_overall_compliance(execution)
        execution.compliance_assessment['completion_summary'] = completion_data.get('completion_summary', '')

        # Update plan status
        plan = self.audit_plans[execution.audit_plan_id]
        plan.status = "completed"

        logger.info(f"Audit execution completed: {execution_id}")
        return True

    def _calculate_overall_compliance(self, execution: AuditExecution) -> Dict[str, Any]:
        """Calculate overall compliance score"""
        assessments = execution.compliance_assessment.get('control_assessments', {})

        if not assessments:
            return {'score': 0, 'level': 'not_assessed', 'summary': 'No assessments completed'}

        total_score = 0
        compliant_count = 0
        major_findings = 0
        minor_findings = 0

        for assessment in assessments.values():
            score = assessment.get('compliance_score', 0)
            total_score += score

            if assessment.get('compliance_status') == 'compliant':
                compliant_count += 1

        # Count findings
        for finding in execution.findings:
            if finding.finding_type == 'major':
                major_findings += 1
            elif finding.finding_type == 'minor':
                minor_findings += 1

        avg_score = total_score / len(assessments)

        # Determine compliance level
        if avg_score >= 95 and major_findings == 0:
            level = 'excellent'
        elif avg_score >= 85 and major_findings <= 2:
            level = 'good'
        elif avg_score >= 75:
            level = 'satisfactory'
        else:
            level = 'needs_improvement'

        return {
            'score': round(avg_score, 1),
            'level': level,
            'compliant_controls': compliant_count,
            'total_controls': len(assessments),
            'major_findings': major_findings,
            'minor_findings': minor_findings,
            'summary': f"{compliant_count}/{len(assessments)} controls compliant, {major_findings} major findings"
        }

    def create_certification_application(self, application_data: Dict[str, Any]) -> str:
        """
        Create a certification application
        Returns application ID
        """
        application_id = str(uuid.uuid4())

        application = CertificationApplication(
            id=application_id,
            certification_standard=CertificationStandard[application_data['certification_standard'].upper()],
            certification_body=application_data['certification_body'],
            application_date=datetime.utcnow(),
            scope_statement=application_data['scope_statement'],
            management_system_description=application_data.get('management_system_description', ''),
            quality_policy=application_data.get('quality_policy', ''),
            quality_objectives=application_data.get('quality_objectives', []),
            internal_audit_results=application_data.get('internal_audit_results', {}),
            management_review_results=application_data.get('management_review_results', {}),
            required_documents=application_data.get('required_documents', []),
            application_fee=application_data.get('application_fee', 0.0)
        )

        self.certification_applications[application_id] = application

        logger.info(f"Certification application created for: {application.certification_standard.value}")
        return application_id

    def perform_compliance_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """
        Perform comprehensive compliance assessment
        Returns assessment ID
        """
        assessment_id = str(uuid.uuid4())

        assessment = ComplianceAssessment(
            id=assessment_id,
            certification_standard=CertificationStandard[assessment_data['certification_standard'].upper()],
            assessment_date=datetime.utcnow(),
            assessed_by=assessment_data['assessed_by'],
            scope=assessment_data['scope']
        )

        # Perform automated assessment
        assessment.control_assessments = self._perform_automated_control_assessment(assessment.certification_standard)
        assessment.gaps_identified = self._identify_compliance_gaps(assessment.control_assessments)
        assessment.recommendations = self._generate_assessment_recommendations(assessment.gaps_identified)

        # Calculate overall score
        assessment.overall_compliance_score = self._calculate_compliance_score(assessment.control_assessments)
        assessment.readiness_level = self._determine_readiness_level(assessment.overall_compliance_score)
        assessment.estimated_certification_date = self._estimate_certification_date(assessment)

        self.compliance_assessments.append(assessment)

        logger.info(f"Compliance assessment completed: {assessment.certification_standard.value} - {assessment.overall_compliance_score}%")
        return assessment_id

    def _perform_automated_control_assessment(self, standard: CertificationStandard) -> Dict[str, Dict[str, Any]]:
        """Perform automated control assessment"""
        assessments = {}

        # Get checklist for standard
        checklist = self.audit_checklists.get(standard, {})

        for section, controls in checklist.items():
            for control in controls:
                # Simulate assessment (in production, this would check actual implementation)
                compliance_status = ComplianceStatus.COMPLIANT  # Assume compliant for demo
                evidence_count = 5  # Mock evidence count
                last_assessed = datetime.utcnow() - timedelta(days=30)

                assessments[control] = {
                    'compliance_status': compliance_status.value,
                    'evidence_count': evidence_count,
                    'last_assessed': last_assessed.isoformat(),
                    'notes': f'Control {control} assessed as {compliance_status.value}',
                    'score': 95 if compliance_status == ComplianceStatus.COMPLIANT else 0
                }

        return assessments

    def _identify_compliance_gaps(self, assessments: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify compliance gaps"""
        gaps = []

        for control_id, assessment in assessments.items():
            if assessment['compliance_status'] != 'compliant':
                gaps.append({
                    'control_id': control_id,
                    'gap_type': assessment['compliance_status'],
                    'severity': 'high' if assessment['score'] < 50 else 'medium',
                    'description': f'Control {control_id} is {assessment["compliance_status"]}',
                    'recommended_actions': [f'Implement control {control_id} requirements']
                })

        return gaps

    def _generate_assessment_recommendations(self, gaps: List[Dict[str, Any]]) -> List[str]:
        """Generate assessment recommendations"""
        recommendations = []

        high_priority_gaps = [g for g in gaps if g['severity'] == 'high']
        if high_priority_gaps:
            recommendations.append(f"Address {len(high_priority_gaps)} high-priority compliance gaps immediately")

        if gaps:
            recommendations.append("Develop corrective action plan for identified gaps")
            recommendations.append("Schedule follow-up assessment after gap remediation")

        recommendations.append("Maintain regular compliance monitoring and assessments")

        return recommendations

    def _calculate_compliance_score(self, assessments: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall compliance score"""
        if not assessments:
            return 0.0

        total_score = sum(assessment['score'] for assessment in assessments.values())
        return round(total_score / len(assessments), 1)

    def _determine_readiness_level(self, score: float) -> str:
        """Determine certification readiness level"""
        if score >= 95:
            return 'certification_ready'
        elif score >= 85:
            return 'conditionally_ready'
        elif score >= 75:
            return 'needs_minor_improvements'
        elif score >= 60:
            return 'needs_major_improvements'
        else:
            return 'not_ready'

    def _estimate_certification_date(self, assessment: ComplianceAssessment) -> Optional[datetime]:
        """Estimate certification date based on assessment"""
        if assessment.readiness_level == 'certification_ready':
            return datetime.utcnow() + timedelta(days=90)  # 3 months for audit process
        elif assessment.readiness_level == 'conditionally_ready':
            return datetime.utcnow() + timedelta(days=180)  # 6 months with remediation
        else:
            return None  # Cannot estimate

    def generate_audit_readiness_checklist(self, standard: CertificationStandard) -> str:
        """
        Generate audit readiness checklist
        Returns checklist ID
        """
        checklist_id = str(uuid.uuid4())

        checklist = AuditReadinessChecklist(
            id=checklist_id,
            certification_standard=standard
        )

        # Generate checklist items based on standard
        checklist_items = {}

        if standard == CertificationStandard.ISO_27001:
            checklist_items = self._generate_iso27001_checklist()
        elif standard == CertificationStandard.ISO_9001:
            checklist_items = self._generate_iso9001_checklist()
        elif standard == CertificationStandard.ISO_22301:
            checklist_items = self._generate_iso22301_checklist()

        checklist.checklist_items = checklist_items
        checklist.completion_percentage = self._calculate_checklist_completion(checklist_items)

        self.readiness_checklists[checklist_id] = checklist

        logger.info(f"Audit readiness checklist generated for: {standard.value}")
        return checklist_id

    def _generate_iso27001_checklist(self) -> Dict[str, Dict[str, Any]]:
        """Generate ISO 27001 readiness checklist"""
        return {
            'scope_and_context': {
                'description': 'Define ISMS scope and context',
                'completed': True,
                'evidence_required': ['scope_statement', 'context_analysis'],
                'responsible': 'ISMS Manager'
            },
            'leadership_and_commitment': {
                'description': 'Demonstrate management commitment',
                'completed': True,
                'evidence_required': ['policy_statement', 'management_review_minutes'],
                'responsible': 'Executive Management'
            },
            'risk_management': {
                'description': 'Implement risk management framework',
                'completed': True,
                'evidence_required': ['risk_register', 'risk_treatment_plan'],
                'responsible': 'Risk Manager'
            },
            'security_controls': {
                'description': 'Implement required security controls',
                'completed': True,
                'evidence_required': ['control_implementations', 'control_effectiveness'],
                'responsible': 'Security Team'
            },
            'internal_audits': {
                'description': 'Conduct internal audits',
                'completed': True,
                'evidence_required': ['audit_reports', 'audit_findings'],
                'responsible': 'Internal Audit Team'
            }
        }

    def _generate_iso9001_checklist(self) -> Dict[str, Dict[str, Any]]:
        """Generate ISO 9001 readiness checklist"""
        return {
            'quality_management_system': {
                'description': 'Establish QMS documentation',
                'completed': True,
                'evidence_required': ['quality_manual', 'procedures'],
                'responsible': 'Quality Manager'
            },
            'management_responsibility': {
                'description': 'Define management responsibilities',
                'completed': True,
                'evidence_required': ['organizational_chart', 'responsibility_matrix'],
                'responsible': 'Executive Management'
            },
            'resource_management': {
                'description': 'Ensure adequate resources',
                'completed': True,
                'evidence_required': ['resource_plan', 'competence_records'],
                'responsible': 'HR Manager'
            },
            'product_realization': {
                'description': 'Implement product realization processes',
                'completed': True,
                'evidence_required': ['process_maps', 'work_instructions'],
                'responsible': 'Operations Manager'
            },
            'measurement_and_monitoring': {
                'description': 'Establish measurement processes',
                'completed': True,
                'evidence_required': ['quality_metrics', 'monitoring_reports'],
                'responsible': 'Quality Manager'
            }
        }

    def _generate_iso22301_checklist(self) -> Dict[str, Dict[str, Any]]:
        """Generate ISO 22301 readiness checklist"""
        return {
            'business_impact_analysis': {
                'description': 'Complete business impact analysis',
                'completed': True,
                'evidence_required': ['bia_report', 'critical_process_identification'],
                'responsible': 'Continuity Manager'
            },
            'continuity_strategy': {
                'description': 'Develop continuity strategies',
                'completed': True,
                'evidence_required': ['strategy_documents', 'recovery_plans'],
                'responsible': 'Continuity Manager'
            },
            'incident_response': {
                'description': 'Establish incident response procedures',
                'completed': True,
                'evidence_required': ['incident_plans', 'response_procedures'],
                'responsible': 'Security Team'
            },
            'testing_and_exercises': {
                'description': 'Conduct testing and exercises',
                'completed': True,
                'evidence_required': ['test_reports', 'exercise_results'],
                'responsible': 'Continuity Manager'
            },
            'continuity_planning': {
                'description': 'Develop business continuity plans',
                'completed': True,
                'evidence_required': ['continuity_plans', 'recovery_procedures'],
                'responsible': 'Continuity Manager'
            }
        }

    def _calculate_checklist_completion(self, checklist_items: Dict[str, Dict[str, Any]]) -> float:
        """Calculate checklist completion percentage"""
        if not checklist_items:
            return 0.0

        completed_items = sum(1 for item in checklist_items.values() if item.get('completed', False))
        return round((completed_items / len(checklist_items)) * 100, 1)

    def get_certification_readiness_report(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive certification readiness report"""
        # Get latest assessments
        assessments = [a for a in self.compliance_assessments[-10:]]  # Last 10 assessments

        # Get active applications
        active_applications = [a for a in self.certification_applications.values()
                             if a.status in ['draft', 'submitted']]

        # Get readiness checklists
        checklists = list(self.readiness_checklists.values())

        # Calculate overall readiness
        overall_readiness = self._calculate_overall_readiness(assessments, checklists)

        # Generate recommendations
        recommendations = self._generate_readiness_recommendations(overall_readiness, assessments)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'overall_readiness': overall_readiness,
            'latest_assessments': [
                {
                    'standard': a.certification_standard.value,
                    'score': a.overall_compliance_score,
                    'readiness_level': a.readiness_level,
                    'date': a.assessment_date.isoformat()
                } for a in assessments[-3:]  # Last 3 assessments
            ],
            'active_applications': [
                {
                    'standard': a.certification_standard.value,
                    'body': a.certification_body,
                    'status': a.status,
                    'submitted': a.submitted_at.isoformat() if a.submitted_at else None
                } for a in active_applications
            ],
            'checklist_completion': [
                {
                    'standard': c.certification_standard.value,
                    'completion': c.completion_percentage,
                    'last_updated': c.last_updated.isoformat()
                } for c in checklists
            ],
            'recommendations': recommendations,
            'next_steps': self._generate_next_steps(overall_readiness)
        }

    def _calculate_overall_readiness(self, assessments: List[ComplianceAssessment],
                                   checklists: List[AuditReadinessChecklist]) -> Dict[str, Any]:
        """Calculate overall certification readiness"""
        if not assessments:
            return {
                'readiness_score': 0,
                'readiness_level': 'not_assessed',
                'standards_assessed': 0,
                'avg_compliance_score': 0
            }

        # Calculate average scores
        total_score = sum(a.overall_compliance_score for a in assessments)
        avg_score = total_score / len(assessments)

        # Determine overall readiness level
        if avg_score >= 95:
            readiness_level = 'certification_ready'
        elif avg_score >= 85:
            readiness_level = 'conditionally_ready'
        elif avg_score >= 75:
            readiness_level = 'minor_gaps'
        elif avg_score >= 60:
            readiness_level = 'major_gaps'
        else:
            readiness_level = 'significant_gaps'

        # Checklist completion
        checklist_completion = sum(c.completion_percentage for c in checklists) / len(checklists) if checklists else 0

        return {
            'readiness_score': round(avg_score, 1),
            'readiness_level': readiness_level,
            'standards_assessed': len(set(a.certification_standard for a in assessments)),
            'avg_compliance_score': round(avg_score, 1),
            'checklist_completion': round(checklist_completion, 1),
            'assessment_count': len(assessments),
            'checklist_count': len(checklists)
        }

    def _generate_readiness_recommendations(self, readiness: Dict[str, Any],
                                          assessments: List[ComplianceAssessment]) -> List[str]:
        """Generate readiness recommendations"""
        recommendations = []

        score = readiness['readiness_score']

        if score < 75:
            recommendations.append("Conduct comprehensive gap analysis and develop remediation plan")
            recommendations.append("Schedule additional internal audits to identify improvement areas")

        if score >= 75 and score < 85:
            recommendations.append("Address identified gaps with corrective actions")
            recommendations.append("Conduct management review of assessment findings")

        if score >= 85 and score < 95:
            recommendations.append("Prepare detailed evidence documentation for certification audit")
            recommendations.append("Conduct pre-audit assessment with certification body")

        if score >= 95:
            recommendations.append("Submit formal certification application")
            recommendations.append("Prepare audit team and logistics")

        # Standard recommendations
        recommendations.extend([
            "Maintain regular compliance monitoring",
            "Keep documentation current and accessible",
            "Train staff on certification requirements"
        ])

        return recommendations

    def _generate_next_steps(self, readiness: Dict[str, Any]) -> List[str]:
        """Generate next steps based on readiness"""
        next_steps = []

        level = readiness['readiness_level']

        if level == 'certification_ready':
            next_steps.extend([
                "Submit certification application to chosen certification body",
                "Schedule Stage 1 audit (documentation review)",
                "Prepare audit team and evidence documentation"
            ])
        elif level == 'conditionally_ready':
            next_steps.extend([
                "Complete outstanding corrective actions",
                "Conduct final internal audit",
                "Schedule certification audit"
            ])
        elif level in ['minor_gaps', 'major_gaps']:
            next_steps.extend([
                "Develop detailed remediation plan",
                "Implement corrective actions for identified gaps",
                "Schedule follow-up assessment"
            ])
        else:
            next_steps.extend([
                "Conduct comprehensive readiness assessment",
                "Develop implementation roadmap",
                "Begin systematic gap remediation"
            ])

        return next_steps

    def check_audit_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check overall audit and certification compliance"""
        assessments = [a for a in self.compliance_assessments[-5:]]  # Last 5 assessments
        applications = list(self.certification_applications.values())
        plans = list(self.audit_plans.values())

        compliance_status = self._assess_audit_compliance(assessments, applications, plans)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'standards': ['ISO 27001:2022', 'ISO 9001:2015', 'ISO 22301:2019'],
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_audit_compliance(self, assessments: List[ComplianceAssessment],
                               applications: List[CertificationApplication],
                               plans: List[AuditPlan]) -> Dict[str, Any]:
        """Assess overall audit compliance"""
        issues = []

        # Check assessment frequency
        recent_assessments = len([a for a in assessments if (datetime.utcnow() - a.assessment_date).days <= 180])
        if recent_assessments < 3:
            issues.append("Insufficient recent compliance assessments")

        # Check application status
        active_applications = len([a for a in applications if a.status in ['draft', 'submitted']])
        if active_applications == 0:
            issues.append("No active certification applications")

        # Check audit planning
        planned_audits = len([p for p in plans if p.status == 'planned'])
        if planned_audits == 0:
            issues.append("No planned audits for upcoming period")

        compliance_score = max(0, 100 - (len(issues) * 12))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_audit_compliance_recommendations(issues)
        }

    def _generate_audit_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate audit compliance recommendations"""
        recommendations = []

        if any('assessment' in issue.lower() for issue in issues):
            recommendations.append("Establish regular compliance assessment schedule")

        if any('application' in issue.lower() for issue in issues):
            recommendations.append("Prepare and submit certification applications")

        if any('audit' in issue.lower() for issue in issues):
            recommendations.append("Develop comprehensive audit planning and scheduling")

        recommendations.append("Maintain continuous audit readiness and compliance monitoring")

        return recommendations