"""
ISO 9001 Process Documentation System
Qualitätsmanagementsystem Process Documentation

Dieses Modul implementiert das Process Documentation System gemäß ISO 9001
für VALEO-NeuroERP mit dokumentierten Prozessen, Workflows und Qualitätsaufzeichnungen.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
import json

logger = logging.getLogger(__name__)


class ProcessType(Enum):
    """Types of business processes"""
    CORE_PROCESS = "core_process"
    SUPPORTING_PROCESS = "supporting_process"
    MANAGEMENT_PROCESS = "management_process"


class ProcessStatus(Enum):
    """Process documentation status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class DocumentType(Enum):
    """Types of process documents"""
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    POLICY = "policy"
    FORM = "form"
    TEMPLATE = "template"
    RECORD = "record"


@dataclass
class ProcessDocument:
    """Process document representation"""
    id: str
    title: str
    document_type: DocumentType
    process_type: ProcessType
    version: str
    status: ProcessStatus
    content: Dict[str, Any]
    created_by: str
    approved_by: Optional[str] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    related_processes: List[str] = field(default_factory=list)
    responsible_roles: List[str] = field(default_factory=list)
    required_training: List[str] = field(default_factory=list)

    # Version control
    previous_version: Optional[str] = None
    change_reason: str = ""
    approval_history: List[Dict[str, Any]] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessExecution:
    """Process execution record"""
    id: str
    process_id: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    executed_by: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    quality_checks: List[Dict[str, Any]] = field(default_factory=list)
    deviations: List[str] = field(default_factory=list)
    duration: Optional[int] = None  # seconds


@dataclass
class QualityRecord:
    """Quality record for process compliance"""
    id: str
    record_type: str
    process_id: str
    execution_id: Optional[str]
    recorded_by: str
    recorded_at: datetime
    data: Dict[str, Any]
    compliance_status: str = "compliant"  # compliant, non_compliant, not_applicable
    notes: str = ""
    attachments: List[str] = field(default_factory=list)


@dataclass
class ProcessMetric:
    """Process performance metric"""
    id: str
    process_id: str
    metric_name: str
    metric_type: str  # count, percentage, duration, cost
    value: float
    target_value: Optional[float]
    recorded_at: datetime
    recorded_by: str
    period: str = "daily"  # daily, weekly, monthly


class ISO9001ProcessDocumentation:
    """
    ISO 9001 Process Documentation System
    Implements quality management principles for documented processes
    """

    def __init__(self, db_session, workflow_service=None, audit_service=None):
        self.db = db_session
        self.workflow = workflow_service
        self.audit = audit_service

        # Process documentation
        self.process_documents: Dict[str, ProcessDocument] = {}

        # Process executions
        self.process_executions: List[ProcessExecution] = []

        # Quality records
        self.quality_records: List[QualityRecord] = []

        # Process metrics
        self.process_metrics: List[ProcessMetric] = []

        # Document templates
        self.document_templates = self._initialize_document_templates()

        # Review cycles
        self.review_cycles = {
            DocumentType.POLICY: timedelta(days=365),  # Annual
            DocumentType.PROCEDURE: timedelta(days=180),  # Semi-annual
            DocumentType.WORK_INSTRUCTION: timedelta(days=90),  # Quarterly
            DocumentType.FORM: timedelta(days=180),
            DocumentType.TEMPLATE: timedelta(days=180),
            DocumentType.RECORD: None  # Records don't have review cycles
        }

    def _initialize_document_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize document templates for different types"""
        return {
            'procedure_template': {
                'sections': [
                    'Purpose', 'Scope', 'Responsibilities', 'Procedure',
                    'Records', 'References', 'Revision History'
                ],
                'required_fields': ['purpose', 'scope', 'responsibilities', 'steps']
            },
            'work_instruction_template': {
                'sections': [
                    'Purpose', 'Scope', 'Safety Considerations', 'Equipment Needed',
                    'Step-by-Step Instructions', 'Quality Checks', 'Troubleshooting'
                ],
                'required_fields': ['purpose', 'steps', 'quality_checks']
            },
            'policy_template': {
                'sections': [
                    'Purpose', 'Scope', 'Policy Statement', 'Responsibilities',
                    'Compliance', 'Consequences', 'Review Process'
                ],
                'required_fields': ['purpose', 'policy_statement', 'responsibilities']
            }
        }

    def create_process_document(self, document_data: Dict[str, Any]) -> str:
        """
        Create a new process document
        Returns document ID
        """
        document_id = str(uuid.uuid4())

        # Validate required fields
        self._validate_document_data(document_data)

        # Generate version number
        version = self._generate_version_number(document_data)

        document = ProcessDocument(
            id=document_id,
            title=document_data['title'],
            document_type=DocumentType[document_data['document_type'].upper()],
            process_type=ProcessType[document_data['process_type'].upper()],
            version=version,
            status=ProcessStatus.DRAFT,
            content=document_data['content'],
            created_by=document_data['created_by'],
            tags=document_data.get('tags', []),
            related_processes=document_data.get('related_processes', []),
            responsible_roles=document_data.get('responsible_roles', []),
            required_training=document_data.get('required_training', [])
        )

        # Set review date based on document type
        if self.review_cycles[document.document_type]:
            document.next_review_date = datetime.utcnow() + self.review_cycles[document.document_type]

        self.process_documents[document_id] = document

        # Log document creation
        if self.audit:
            self.audit.log_quality_event({
                'event_type': 'document_created',
                'document_id': document_id,
                'document_type': document.document_type.value,
                'created_by': document.created_by
            })

        logger.info(f"Process document created: {document.title} (v{document.version})")
        return document_id

    def _validate_document_data(self, data: Dict[str, Any]):
        """Validate document creation data"""
        required_fields = ['title', 'document_type', 'process_type', 'content', 'created_by']

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field missing: {field}")

        # Validate document type
        try:
            DocumentType[data['document_type'].upper()]
        except KeyError:
            raise ValueError(f"Invalid document type: {data['document_type']}")

        # Validate process type
        try:
            ProcessType[data['process_type'].upper()]
        except KeyError:
            raise ValueError(f"Invalid process type: {data['process_type']}")

    def _generate_version_number(self, data: Dict[str, Any]) -> str:
        """Generate version number for document"""
        # Find existing documents with same title
        existing_versions = [
            doc.version for doc in self.process_documents.values()
            if doc.title == data['title']
        ]

        if not existing_versions:
            return "1.0"

        # Parse existing versions and increment
        version_numbers = []
        for v in existing_versions:
            try:
                major, minor = map(int, v.split('.'))
                version_numbers.append((major, minor))
            except ValueError:
                continue

        if version_numbers:
            max_major, max_minor = max(version_numbers)
            return f"{max_major}.{max_minor + 1}"

        return "1.0"

    def update_process_document(self, document_id: str, update_data: Dict[str, Any],
                              updated_by: str) -> bool:
        """
        Update process document
        """
        if document_id not in self.process_documents:
            return False

        document = self.process_documents[document_id]

        # Create new version for significant changes
        if 'content' in update_data or 'major_change' in update_data:
            new_document_id = self._create_new_version(document, update_data, updated_by)
            return new_document_id is not None

        # Minor updates to existing document
        for key, value in update_data.items():
            if hasattr(document, key):
                setattr(document, key, value)

        document.updated_at = datetime.utcnow()

        # Log update
        if self.audit:
            self.audit.log_quality_event({
                'event_type': 'document_updated',
                'document_id': document_id,
                'updated_by': updated_by
            })

        logger.info(f"Process document updated: {document.title}")
        return True

    def _create_new_version(self, document: ProcessDocument, update_data: Dict[str, Any],
                          updated_by: str) -> Optional[str]:
        """Create new version of document"""
        # Increment version
        major, minor = map(int, document.version.split('.'))
        new_version = f"{major}.{minor + 1}"

        # Create new document
        new_document_data = {
            'title': document.title,
            'document_type': document.document_type.value,
            'process_type': document.process_type.value,
            'content': update_data.get('content', document.content),
            'created_by': updated_by,
            'tags': document.tags,
            'related_processes': document.related_processes,
            'responsible_roles': document.responsible_roles,
            'required_training': document.required_training
        }

        new_document_id = self.create_process_document(new_document_data)

        if new_document_id:
            new_doc = self.process_documents[new_document_id]
            new_doc.previous_version = document.version
            new_doc.change_reason = update_data.get('change_reason', 'Content update')

            # Update old document status
            document.status = ProcessStatus.DEPRECATED

        return new_document_id

    def approve_process_document(self, document_id: str, approved_by: str,
                               approval_notes: str = "") -> bool:
        """
        Approve process document
        """
        if document_id not in self.process_documents:
            return False

        document = self.process_documents[document_id]

        if document.status != ProcessStatus.REVIEW:
            raise ValueError("Document must be in REVIEW status to be approved")

        document.status = ProcessStatus.APPROVED
        document.approved_by = approved_by
        document.effective_date = datetime.utcnow()

        # Add approval to history
        approval_record = {
            'approved_by': approved_by,
            'approved_at': datetime.utcnow().isoformat(),
            'notes': approval_notes,
            'version': document.version
        }
        document.approval_history.append(approval_record)

        # Set next review date
        if self.review_cycles[document.document_type]:
            document.next_review_date = datetime.utcnow() + self.review_cycles[document.document_type]

        # Log approval
        if self.audit:
            self.audit.log_quality_event({
                'event_type': 'document_approved',
                'document_id': document_id,
                'approved_by': approved_by,
                'version': document.version
            })

        logger.info(f"Process document approved: {document.title} v{document.version}")
        return True

    def submit_for_review(self, document_id: str, submitted_by: str) -> bool:
        """
        Submit document for review
        """
        if document_id not in self.process_documents:
            return False

        document = self.process_documents[document_id]

        if document.status != ProcessStatus.DRAFT:
            raise ValueError("Only DRAFT documents can be submitted for review")

        document.status = ProcessStatus.REVIEW
        document.review_date = datetime.utcnow()

        # Log submission
        if self.audit:
            self.audit.log_quality_event({
                'event_type': 'document_submitted_review',
                'document_id': document_id,
                'submitted_by': submitted_by
            })

        logger.info(f"Process document submitted for review: {document.title}")
        return True

    def record_process_execution(self, execution_data: Dict[str, Any]) -> str:
        """
        Record process execution
        Returns execution ID
        """
        execution_id = str(uuid.uuid4())

        execution = ProcessExecution(
            id=execution_id,
            process_id=execution_data['process_id'],
            execution_id=execution_data.get('execution_id', execution_id),
            started_at=datetime.utcnow(),
            executed_by=execution_data['executed_by'],
            inputs=execution_data.get('inputs', {}),
            quality_checks=execution_data.get('quality_checks', [])
        )

        self.process_executions.append(execution)

        logger.debug(f"Process execution started: {execution.process_id}")
        return execution_id

    def complete_process_execution(self, execution_id: str, results: Dict[str, Any]) -> bool:
        """
        Complete process execution
        """
        execution = self._find_execution_by_id(execution_id)
        if not execution:
            return False

        execution.completed_at = datetime.utcnow()
        execution.status = results.get('status', 'completed')
        execution.outputs = results.get('outputs', {})
        execution.deviations = results.get('deviations', [])

        # Calculate duration
        if execution.completed_at and execution.started_at:
            execution.duration = int((execution.completed_at - execution.started_at).total_seconds())

        # Record quality checks
        quality_checks = results.get('quality_checks', [])
        for check in quality_checks:
            self.record_quality_check(execution.process_id, execution_id, check, execution.executed_by)

        # Log completion
        if self.audit:
            self.audit.log_quality_event({
                'event_type': 'process_execution_completed',
                'execution_id': execution_id,
                'process_id': execution.process_id,
                'status': execution.status,
                'duration': execution.duration
            })

        logger.info(f"Process execution completed: {execution.process_id} ({execution.status})")
        return True

    def _find_execution_by_id(self, execution_id: str) -> Optional[ProcessExecution]:
        """Find execution by ID"""
        for execution in self.process_executions:
            if execution.id == execution_id:
                return execution
        return None

    def record_quality_check(self, process_id: str, execution_id: str,
                           check_data: Dict[str, Any], recorded_by: str) -> str:
        """
        Record quality check result
        Returns record ID
        """
        record_id = str(uuid.uuid4())

        record = QualityRecord(
            id=record_id,
            record_type=check_data.get('check_type', 'process_check'),
            process_id=process_id,
            execution_id=execution_id,
            recorded_by=recorded_by,
            recorded_at=datetime.utcnow(),
            data=check_data.get('data', {}),
            compliance_status=check_data.get('compliance_status', 'compliant'),
            notes=check_data.get('notes', '')
        )

        self.quality_records.append(record)

        # Log non-compliant checks
        if record.compliance_status == 'non_compliant':
            logger.warning(f"Quality check failed: {process_id} - {check_data.get('check_name', 'Unknown')}")

        return record_id

    def record_process_metric(self, metric_data: Dict[str, Any]) -> str:
        """
        Record process performance metric
        Returns metric ID
        """
        metric_id = str(uuid.uuid4())

        metric = ProcessMetric(
            id=metric_id,
            process_id=metric_data['process_id'],
            metric_name=metric_data['metric_name'],
            metric_type=metric_data['metric_type'],
            value=metric_data['value'],
            target_value=metric_data.get('target_value'),
            recorded_at=datetime.utcnow(),
            recorded_by=metric_data['recorded_by'],
            period=metric_data.get('period', 'daily')
        )

        self.process_metrics.append(metric)

        # Check against targets and alert if necessary
        if metric.target_value and not self._is_metric_within_target(metric):
            self._alert_metric_deviation(metric)

        logger.debug(f"Process metric recorded: {metric.process_id} - {metric.metric_name} = {metric.value}")
        return metric_id

    def _is_metric_within_target(self, metric: ProcessMetric) -> bool:
        """Check if metric is within acceptable range of target"""
        if not metric.target_value:
            return True

        tolerance = 0.1  # 10% tolerance
        min_acceptable = metric.target_value * (1 - tolerance)
        max_acceptable = metric.target_value * (1 + tolerance)

        return min_acceptable <= metric.value <= max_acceptable

    def _alert_metric_deviation(self, metric: ProcessMetric):
        """Alert on metric deviation from target"""
        deviation = abs(metric.value - metric.target_value) / metric.target_value * 100

        logger.warning(f"Process metric deviation: {metric.metric_name} = {metric.value} "
                      f"(target: {metric.target_value}, deviation: {deviation:.1f}%)")

    def get_process_documentation_status(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive process documentation status"""
        # Filter documents by tenant
        tenant_documents = [d for d in self.process_documents.values() if d.created_by == tenant_id]

        # Calculate documentation metrics
        documentation_stats = self._calculate_documentation_stats(tenant_documents)
        process_coverage = self._assess_process_coverage(tenant_documents)
        compliance_status = self._check_documentation_compliance(tenant_documents)
        review_status = self._check_review_status(tenant_documents)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'documentation_stats': documentation_stats,
            'process_coverage': process_coverage,
            'compliance_status': compliance_status,
            'review_status': review_status,
            'overall_maturity_score': self._calculate_maturity_score(documentation_stats, process_coverage, compliance_status)
        }

    def _calculate_documentation_stats(self, documents: List[ProcessDocument]) -> Dict[str, Any]:
        """Calculate documentation statistics"""
        if not documents:
            return {'total_documents': 0, 'by_type': {}, 'by_status': {}}

        by_type = {}
        by_status = {}

        for doc in documents:
            # Count by type
            type_key = doc.document_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by status
            status_key = doc.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

        return {
            'total_documents': len(documents),
            'by_type': by_type,
            'by_status': by_status,
            'active_documents': by_status.get('active', 0) + by_status.get('approved', 0)
        }

    def _assess_process_coverage(self, documents: List[ProcessDocument]) -> Dict[str, Any]:
        """Assess process coverage across different areas"""
        # Define expected process areas
        expected_processes = {
            'core': ['software_development', 'testing', 'deployment', 'maintenance'],
            'supporting': ['documentation', 'training', 'audit', 'compliance'],
            'management': ['quality_management', 'risk_management', 'change_management']
        }

        covered_processes = set()
        for doc in documents:
            if doc.status in [ProcessStatus.APPROVED, ProcessStatus.ACTIVE]:
                covered_processes.update(doc.related_processes)

        coverage_by_type = {}
        for process_type, processes in expected_processes.items():
            covered = len([p for p in processes if p in covered_processes])
            total = len(processes)
            coverage_rate = (covered / total * 100) if total > 0 else 0

            coverage_by_type[process_type] = {
                'covered': covered,
                'total': total,
                'coverage_rate': round(coverage_rate, 1)
            }

        overall_coverage = sum(c['coverage_rate'] for c in coverage_by_type.values()) / len(coverage_by_type)

        return {
            'overall_coverage': round(overall_coverage, 1),
            'by_process_type': coverage_by_type
        }

    def _check_documentation_compliance(self, documents: List[ProcessDocument]) -> Dict[str, Any]:
        """Check documentation compliance with ISO 9001 requirements"""
        issues = []

        # Check for required document types
        required_types = [DocumentType.POLICY, DocumentType.PROCEDURE, DocumentType.WORK_INSTRUCTION]
        for req_type in required_types:
            type_docs = [d for d in documents if d.document_type == req_type and d.status in [ProcessStatus.APPROVED, ProcessStatus.ACTIVE]]
            if not type_docs:
                issues.append(f"Missing {req_type.value} documents")

        # Check for approved documents
        draft_docs = [d for d in documents if d.status == ProcessStatus.DRAFT]
        if len(draft_docs) > len(documents) * 0.2:  # More than 20% draft
            issues.append("Too many documents in draft status")

        compliance_score = max(0, 100 - (len(issues) * 10))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'required_types_present': len(required_types) - len([i for i in issues if 'Missing' in i])
        }

    def _check_review_status(self, documents: List[ProcessDocument]) -> Dict[str, Any]:
        """Check document review status"""
        now = datetime.utcnow()
        overdue_reviews = 0
        upcoming_reviews = 0

        for doc in documents:
            if doc.next_review_date:
                if doc.next_review_date < now:
                    overdue_reviews += 1
                elif doc.next_review_date < now + timedelta(days=30):
                    upcoming_reviews += 1

        return {
            'overdue_reviews': overdue_reviews,
            'upcoming_reviews': upcoming_reviews,
            'total_reviewable': len([d for d in documents if d.next_review_date])
        }

    def _calculate_maturity_score(self, doc_stats: Dict, process_coverage: Dict,
                                compliance: Dict) -> float:
        """Calculate overall process documentation maturity score"""
        score = 0

        # Documentation completeness (40%)
        total_docs = doc_stats.get('total_documents', 0)
        active_docs = doc_stats.get('active_documents', 0)
        if total_docs > 0:
            score += (active_docs / total_docs) * 40

        # Process coverage (30%)
        score += process_coverage.get('overall_coverage', 0) * 0.3

        # Compliance (30%)
        score += compliance.get('compliance_score', 0) * 0.3

        return round(score, 1)

    def get_process_performance_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get process performance dashboard"""
        # Filter data by tenant
        tenant_executions = [e for e in self.process_executions if e.executed_by == tenant_id]
        tenant_metrics = [m for m in self.process_metrics if m.recorded_by == tenant_id]
        tenant_records = [r for r in self.quality_records if r.recorded_by == tenant_id]

        # Calculate performance metrics
        execution_stats = self._calculate_execution_stats(tenant_executions)
        quality_stats = self._calculate_quality_stats(tenant_records)
        metric_trends = self._calculate_metric_trends(tenant_metrics)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'execution_stats': execution_stats,
            'quality_stats': quality_stats,
            'metric_trends': metric_trends,
            'performance_score': self._calculate_performance_score(execution_stats, quality_stats, metric_trends)
        }

    def _calculate_execution_stats(self, executions: List[ProcessExecution]) -> Dict[str, Any]:
        """Calculate process execution statistics"""
        if not executions:
            return {'total_executions': 0, 'success_rate': 0, 'avg_duration': 0}

        total = len(executions)
        successful = len([e for e in executions if e.status == 'completed'])
        success_rate = (successful / total * 100) if total > 0 else 0

        completed_executions = [e for e in executions if e.completed_at and e.duration]
        avg_duration = sum(e.duration for e in completed_executions) / len(completed_executions) if completed_executions else 0

        return {
            'total_executions': total,
            'successful_executions': successful,
            'success_rate': round(success_rate, 1),
            'avg_duration_seconds': round(avg_duration, 1)
        }

    def _calculate_quality_stats(self, records: List[QualityRecord]) -> Dict[str, Any]:
        """Calculate quality statistics"""
        if not records:
            return {'total_records': 0, 'compliance_rate': 0, 'by_type': {}}

        total = len(records)
        compliant = len([r for r in records if r.compliance_status == 'compliant'])
        compliance_rate = (compliant / total * 100) if total > 0 else 0

        by_type = {}
        for record in records:
            type_key = record.record_type
            by_type[type_key] = by_type.get(type_key, {'total': 0, 'compliant': 0})
            by_type[type_key]['total'] += 1
            if record.compliance_status == 'compliant':
                by_type[type_key]['compliant'] += 1

        return {
            'total_records': total,
            'compliant_records': compliant,
            'compliance_rate': round(compliance_rate, 1),
            'by_type': by_type
        }

    def _calculate_metric_trends(self, metrics: List[ProcessMetric]) -> Dict[str, Any]:
        """Calculate metric trends"""
        trends = {}

        # Group by metric name
        metric_groups = {}
        for metric in metrics[-100:]:  # Last 100 metrics
            name = metric.metric_name
            if name not in metric_groups:
                metric_groups[name] = []
            metric_groups[name].append(metric)

        for name, metric_list in metric_groups.items():
            if len(metric_list) >= 2:
                # Sort by date
                sorted_metrics = sorted(metric_list, key=lambda x: x.recorded_at)

                # Calculate trend (simple linear trend)
                values = [m.value for m in sorted_metrics]
                if len(values) >= 2:
                    trend = (values[-1] - values[0]) / len(values)
                else:
                    trend = 0

                latest = sorted_metrics[-1]
                target = latest.target_value

                status = 'ON_TRACK'
                if target:
                    deviation = abs(latest.value - target) / target
                    if deviation > 0.1:  # 10% deviation
                        status = 'OFF_TRACK'

                trends[name] = {
                    'current_value': round(latest.value, 2),
                    'target_value': target,
                    'trend': round(trend, 3),
                    'status': status,
                    'data_points': len(sorted_metrics)
                }

        return trends

    def _calculate_performance_score(self, execution_stats: Dict, quality_stats: Dict,
                                   metric_trends: Dict) -> float:
        """Calculate overall process performance score"""
        score = 0

        # Execution success (40%)
        success_rate = execution_stats.get('success_rate', 0)
        score += success_rate * 0.4

        # Quality compliance (40%)
        compliance_rate = quality_stats.get('compliance_rate', 0)
        score += compliance_rate * 0.4

        # Metric performance (20%)
        on_track_metrics = sum(1 for t in metric_trends.values() if t['status'] == 'ON_TRACK')
        total_metrics = len(metric_trends)
        if total_metrics > 0:
            metric_score = (on_track_metrics / total_metrics) * 100
            score += metric_score * 0.2

        return round(score, 1)

    def generate_process_documentation_report(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive process documentation report"""
        documentation_status = self.get_process_documentation_status(tenant_id)
        performance_dashboard = self.get_process_performance_dashboard(tenant_id)

        report = {
            'tenant_id': tenant_id,
            'report_period': 'Current',
            'generated_at': datetime.utcnow().isoformat(),
            'documentation_status': documentation_status,
            'performance_dashboard': performance_dashboard,
            'iso9001_compliance': self._assess_iso9001_compliance(documentation_status, performance_dashboard),
            'recommendations': self._generate_documentation_recommendations(documentation_status, performance_dashboard),
            'action_items': self._identify_action_items(documentation_status, performance_dashboard)
        }

        return report

    def _assess_iso9001_compliance(self, doc_status: Dict, perf_status: Dict) -> Dict[str, Any]:
        """Assess ISO 9001 compliance for process documentation"""
        compliance_score = 0
        requirements = []

        # Documentation requirements (ISO 9001 clause 7.5)
        doc_compliance = doc_status.get('compliance_status', {})
        if doc_compliance.get('compliance_score', 0) >= 80:
            compliance_score += 30
            requirements.append("Documented processes (7.5) - COMPLIANT")
        else:
            requirements.append("Documented processes (7.5) - NON_COMPLIANT")

        # Process performance (ISO 9001 clause 8.1)
        perf_score = perf_status.get('performance_score', 0)
        if perf_score >= 80:
            compliance_score += 25
            requirements.append("Process monitoring (8.1) - COMPLIANT")
        else:
            requirements.append("Process monitoring (8.1) - PARTIALLY_COMPLIANT")

        # Quality records (ISO 9001 clause 8.3)
        quality_compliance = perf_status.get('quality_stats', {}).get('compliance_rate', 0)
        if quality_compliance >= 90:
            compliance_score += 25
            requirements.append("Quality records (8.3) - COMPLIANT")
        else:
            requirements.append("Quality records (8.3) - PARTIALLY_COMPLIANT")

        # Continual improvement (ISO 9001 clause 10.3)
        maturity_score = doc_status.get('overall_maturity_score', 0)
        if maturity_score >= 75:
            compliance_score += 20
            requirements.append("Continual improvement (10.3) - COMPLIANT")
        else:
            requirements.append("Continual improvement (10.3) - DEVELOPING")

        overall_status = 'COMPLIANT' if compliance_score >= 80 else 'PARTIALLY_COMPLIANT' if compliance_score >= 60 else 'NON_COMPLIANT'

        return {
            'overall_status': overall_status,
            'compliance_score': compliance_score,
            'requirements_assessment': requirements,
            'iso_standard': 'ISO 9001:2015'
        }

    def _generate_documentation_recommendations(self, doc_status: Dict, perf_status: Dict) -> List[str]:
        """Generate recommendations for process documentation improvement"""
        recommendations = []

        # Documentation coverage
        coverage = doc_status.get('process_coverage', {}).get('overall_coverage', 0)
        if coverage < 80:
            recommendations.append("Increase process documentation coverage to at least 80%")

        # Document approval status
        doc_stats = doc_status.get('documentation_stats', {})
        draft_count = doc_stats.get('by_status', {}).get('draft', 0)
        total_docs = doc_stats.get('total_documents', 0)
        if total_docs > 0 and (draft_count / total_docs) > 0.2:
            recommendations.append("Reduce draft documents by approving and implementing documented processes")

        # Review compliance
        review_status = doc_status.get('review_status', {})
        if review_status.get('overdue_reviews', 0) > 0:
            recommendations.append("Conduct overdue document reviews within the next 30 days")

        # Performance issues
        perf_score = perf_status.get('performance_score', 0)
        if perf_score < 75:
            recommendations.append("Implement process performance monitoring and improvement measures")

        if not recommendations:
            recommendations.append("Maintain current process documentation standards and continue monitoring")

        return recommendations

    def _identify_action_items(self, doc_status: Dict, perf_status: Dict) -> List[Dict[str, Any]]:
        """Identify specific action items for improvement"""
        action_items = []

        # Missing document types
        compliance = doc_status.get('compliance_status', {})
        issues = compliance.get('issues', [])
        for issue in issues:
            if 'Missing' in issue:
                action_items.append({
                    'priority': 'HIGH',
                    'action': f"Create {issue.lower()}",
                    'owner': 'Quality Manager',
                    'due_date': (datetime.utcnow() + timedelta(days=30)).isoformat()
                })

        # Overdue reviews
        review_status = doc_status.get('review_status', {})
        if review_status.get('overdue_reviews', 0) > 0:
            action_items.append({
                'priority': 'MEDIUM',
                'action': f"Review {review_status['overdue_reviews']} overdue documents",
                'owner': 'Document Owners',
                'due_date': (datetime.utcnow() + timedelta(days=14)).isoformat()
            })

        # Performance improvements
        execution_stats = perf_status.get('execution_stats', {})
        success_rate = execution_stats.get('success_rate', 100)
        if success_rate < 95:
            action_items.append({
                'priority': 'MEDIUM',
                'action': "Improve process execution success rate above 95%",
                'owner': 'Process Owners',
                'due_date': (datetime.utcnow() + timedelta(days=60)).isoformat()
            })

        return action_items