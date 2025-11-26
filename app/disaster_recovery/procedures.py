"""
ISO 22301 Disaster Recovery Procedures
Business Continuity Management System Disaster Recovery

Dieses Modul implementiert die Disaster Recovery Procedures gemäß ISO 22301
für VALEO-NeuroERP mit Emergency Response, Failover Procedures und Recovery Workflows.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class DisasterType(Enum):
    """Types of disasters"""
    NATURAL_DISASTER = "natural_disaster"
    CYBER_ATTACK = "cyber_attack"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    HUMAN_ERROR = "human_error"
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    REGULATORY_CHANGE = "regulatory_change"


class RecoveryPhase(Enum):
    """Disaster recovery phases"""
    DETECTION = "detection"
    ASSESSMENT = "assessment"
    CONTAINMENT = "containment"
    RECOVERY = "recovery"
    RESTORATION = "restoration"
    LESSONS_LEARNED = "lessons_learned"


class RecoveryPriority(Enum):
    """Recovery priority levels"""
    CRITICAL = "critical"  # < 4 hours
    HIGH = "high"         # < 24 hours
    MEDIUM = "medium"     # < 72 hours
    LOW = "low"          # < 1 week


class FailoverType(Enum):
    """Types of failover mechanisms"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SEMI_AUTOMATIC = "semi_automatic"


@dataclass
class DisasterDeclaration:
    """Disaster declaration record"""
    id: str
    disaster_type: DisasterType
    severity_level: str
    affected_systems: List[str]
    affected_locations: List[str]
    declared_by: str
    declared_at: datetime
    estimated_impact: Dict[str, Any]
    recovery_objectives: Dict[str, Any]
    status: str = "active"
    resolved_at: Optional[datetime] = None


@dataclass
class RecoveryProcedure:
    """Recovery procedure definition"""
    id: str
    name: str
    disaster_type: DisasterType
    recovery_phase: RecoveryPhase
    priority: RecoveryPriority
    estimated_duration: int  # minutes
    required_resources: List[str]
    responsible_roles: List[str]
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    success_criteria: List[str]
    rollback_procedures: List[str]
    is_active: bool = True
    last_tested: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecoveryExecution:
    """Recovery procedure execution record"""
    id: str
    procedure_id: str
    disaster_id: str
    started_by: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    current_step: int = 0
    executed_steps: List[Dict[str, Any]] = field(default_factory=list)
    issues_encountered: List[str] = field(default_factory=list)
    recovery_metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class FailoverConfiguration:
    """Failover configuration for systems"""
    id: str
    system_name: str
    primary_location: str
    secondary_location: str
    failover_type: FailoverType
    trigger_conditions: List[str]
    failover_procedures: List[Dict[str, Any]]
    failback_procedures: List[Dict[str, Any]]
    rto_minutes: int
    rpo_minutes: int
    last_failover_test: Optional[datetime] = None
    is_active: bool = True


@dataclass
class RecoveryResource:
    """Recovery resource allocation"""
    id: str
    resource_type: str  # personnel, equipment, software, facilities
    resource_name: str
    quantity_available: int
    quantity_allocated: int = 0
    location: str
    contact_info: Dict[str, Any]
    availability_status: str = "available"
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ISO22301DisasterRecovery:
    """
    ISO 22301 Disaster Recovery Procedures
    Implements disaster recovery planning and execution
    """

    def __init__(self, db_session, continuity_service=None, backup_service=None):
        self.db = db_session
        self.continuity = continuity_service
        self.backup = backup_service

        # Disaster recovery management
        self.disaster_declarations: Dict[str, DisasterDeclaration] = {}
        self.recovery_procedures: Dict[str, RecoveryProcedure] = {}
        self.recovery_executions: List[RecoveryExecution] = {}
        self.failover_configurations: Dict[str, FailoverConfiguration] = {}
        self.recovery_resources: Dict[str, RecoveryResource] = {}

        # Recovery workflows
        self.recovery_workflows = self._initialize_recovery_workflows()

        # Communication templates
        self.communication_templates = self._initialize_communication_templates()

    def _initialize_recovery_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Initialize recovery workflows for different disaster types"""
        return {
            'cyber_attack': {
                'phases': ['isolation', 'assessment', 'containment', 'recovery', 'monitoring'],
                'critical_systems': ['authentication', 'database', 'network'],
                'communication_priority': 'immediate'
            },
            'infrastructure_failure': {
                'phases': ['assessment', 'failover', 'recovery', 'validation'],
                'critical_systems': ['servers', 'network', 'storage'],
                'communication_priority': 'high'
            },
            'data_center_disaster': {
                'phases': ['evacuation', 'failover', 'recovery', 'relocation'],
                'critical_systems': ['all_primary_systems'],
                'communication_priority': 'critical'
            }
        }

    def _initialize_communication_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize communication templates for disaster scenarios"""
        return {
            'disaster_declaration': {
                'subject': 'DISASTER RECOVERY ACTIVATION - {disaster_type}',
                'recipients': ['executives', 'recovery_team', 'customers', 'suppliers'],
                'content': 'A {severity} level {disaster_type} has been declared. Recovery procedures are now active.'
            },
            'recovery_status': {
                'subject': 'RECOVERY STATUS UPDATE - {disaster_type}',
                'recipients': ['executives', 'recovery_team', 'affected_parties'],
                'content': 'Recovery phase: {phase}. Estimated completion: {eta}.'
            },
            'service_restoration': {
                'subject': 'SERVICE RESTORATION COMPLETE - {disaster_type}',
                'recipients': ['all_staff', 'customers', 'partners'],
                'content': 'Normal operations have been restored. Incident summary available.'
            }
        }

    def declare_disaster(self, disaster_data: Dict[str, Any]) -> str:
        """
        Declare a disaster and initiate recovery procedures
        Returns disaster ID
        """
        disaster_id = str(uuid.uuid4())

        declaration = DisasterDeclaration(
            id=disaster_id,
            disaster_type=DisasterType[disaster_data['disaster_type'].upper()],
            severity_level=disaster_data['severity_level'],
            affected_systems=disaster_data.get('affected_systems', []),
            affected_locations=disaster_data.get('affected_locations', []),
            declared_by=disaster_data['declared_by'],
            declared_at=datetime.utcnow(),
            estimated_impact=disaster_data.get('estimated_impact', {}),
            recovery_objectives=disaster_data.get('recovery_objectives', {})
        )

        self.disaster_declarations[disaster_id] = declaration

        # Trigger immediate response actions
        self._trigger_disaster_response(declaration)

        # Notify stakeholders
        self._notify_disaster_stakeholders(declaration)

        logger.critical(f"DISASTER DECLARED: {declaration.disaster_type.value} - {declaration.severity_level} severity")
        return disaster_id

    def _trigger_disaster_response(self, disaster: DisasterDeclaration):
        """Trigger automated disaster response actions"""
        response_actions = []

        # Get relevant recovery procedures
        relevant_procedures = [
            p for p in self.recovery_procedures.values()
            if p.disaster_type == disaster.disaster_type and p.is_active
        ]

        # Prioritize critical procedures
        critical_procedures = [p for p in relevant_procedures if p.priority == RecoveryPriority.CRITICAL]

        for procedure in critical_procedures:
            # Auto-execute if possible
            if self._can_auto_execute(procedure):
                execution_id = self.execute_recovery_procedure(procedure.id, disaster.id, "system")
                response_actions.append(f"Auto-executed procedure: {procedure.name} (ID: {execution_id})")
            else:
                response_actions.append(f"Manual execution required: {procedure.name}")

        # Trigger failover for affected systems
        for system in disaster.affected_systems:
            failover_config = self._find_failover_config(system)
            if failover_config and failover_config.failover_type == FailoverType.AUTOMATIC:
                self._execute_failover(failover_config)
                response_actions.append(f"Automatic failover initiated for: {system}")

        disaster.estimated_impact['response_actions'] = response_actions

        logger.critical(f"Disaster response triggered for {disaster.disaster_type.value}: {len(response_actions)} actions")

    def _can_auto_execute(self, procedure: RecoveryProcedure) -> bool:
        """Check if procedure can be auto-executed"""
        # Check if all prerequisites are met
        for prereq in procedure.prerequisites:
            if not self._check_prerequisite(prereq):
                return False

        # Check if required resources are available
        for resource in procedure.required_resources:
            if not self._check_resource_availability(resource):
                return False

        return True

    def _check_prerequisite(self, prerequisite: str) -> bool:
        """Check if a prerequisite is met"""
        # Simplified prerequisite checking
        # In production, this would check system status, dependencies, etc.
        return True

    def _check_resource_availability(self, resource: str) -> bool:
        """Check if required resource is available"""
        resource_obj = self.recovery_resources.get(resource)
        if not resource_obj:
            return False

        return resource_obj.availability_status == "available" and \
               resource_obj.quantity_available > resource_obj.quantity_allocated

    def _find_failover_config(self, system_name: str) -> Optional[FailoverConfiguration]:
        """Find failover configuration for a system"""
        for config in self.failover_configurations.values():
            if config.system_name == system_name and config.is_active:
                return config
        return None

    def _execute_failover(self, config: FailoverConfiguration):
        """Execute system failover"""
        logger.critical(f"Executing failover for {config.system_name} from {config.primary_location} to {config.secondary_location}")

        # In production, this would trigger actual failover procedures
        # For now, simulate failover execution

    def _notify_disaster_stakeholders(self, disaster: DisasterDeclaration):
        """Notify relevant stakeholders about disaster declaration"""
        notification_data = {
            'type': 'disaster_declaration',
            'disaster_id': disaster.id,
            'disaster_type': disaster.disaster_type.value,
            'severity': disaster.severity_level,
            'affected_systems': disaster.affected_systems,
            'timestamp': disaster.declared_at.isoformat()
        }

        # In production, this would send notifications via multiple channels
        logger.critical(f"Disaster notification sent for: {disaster.disaster_type.value}")

    def create_recovery_procedure(self, procedure_data: Dict[str, Any]) -> str:
        """
        Create a recovery procedure
        Returns procedure ID
        """
        procedure_id = str(uuid.uuid4())

        procedure = RecoveryProcedure(
            id=procedure_id,
            name=procedure_data['name'],
            disaster_type=DisasterType[procedure_data['disaster_type'].upper()],
            recovery_phase=RecoveryPhase[procedure_data['recovery_phase'].upper()],
            priority=RecoveryPriority[procedure_data['priority'].upper()],
            estimated_duration=procedure_data['estimated_duration'],
            required_resources=procedure_data.get('required_resources', []),
            responsible_roles=procedure_data.get('responsible_roles', []),
            prerequisites=procedure_data.get('prerequisites', []),
            steps=procedure_data.get('steps', []),
            success_criteria=procedure_data.get('success_criteria', []),
            rollback_procedures=procedure_data.get('rollback_procedures', [])
        )

        self.recovery_procedures[procedure_id] = procedure

        logger.info(f"Recovery procedure created: {procedure.name} for {procedure.disaster_type.value}")
        return procedure_id

    def execute_recovery_procedure(self, procedure_id: str, disaster_id: str, executed_by: str) -> str:
        """
        Execute a recovery procedure
        Returns execution ID
        """
        if procedure_id not in self.recovery_procedures:
            raise ValueError(f"Recovery procedure not found: {procedure_id}")

        procedure = self.recovery_procedures[procedure_id]

        execution_id = str(uuid.uuid4())

        execution = RecoveryExecution(
            id=execution_id,
            procedure_id=procedure_id,
            disaster_id=disaster_id,
            started_by=executed_by,
            started_at=datetime.utcnow()
        )

        self.recovery_executions[execution_id] = execution

        # Allocate required resources
        for resource_name in procedure.required_resources:
            self._allocate_resource(resource_name, execution_id)

        # Start execution
        self._execute_procedure_steps(procedure, execution)

        logger.info(f"Recovery procedure execution started: {procedure.name} by {executed_by}")
        return execution_id

    def _allocate_resource(self, resource_name: str, execution_id: str):
        """Allocate a resource for recovery execution"""
        resource = self.recovery_resources.get(resource_name)
        if resource and resource.quantity_available > resource.quantity_allocated:
            resource.quantity_allocated += 1
            logger.debug(f"Resource allocated: {resource_name} for execution {execution_id}")

    def _execute_procedure_steps(self, procedure: RecoveryProcedure, execution: RecoveryExecution):
        """Execute procedure steps"""
        try:
            for step_index, step in enumerate(procedure.steps):
                execution.current_step = step_index

                # Execute step
                step_result = self._execute_step(step, execution)

                # Record executed step
                executed_step = {
                    'step_number': step_index + 1,
                    'step_name': step.get('name', f'Step {step_index + 1}'),
                    'executed_at': datetime.utcnow().isoformat(),
                    'result': step_result,
                    'status': 'completed' if step_result['success'] else 'failed'
                }

                execution.executed_steps.append(executed_step)

                if not step_result['success']:
                    execution.status = 'failed'
                    execution.issues_encountered.append(step_result.get('error', 'Step execution failed'))
                    break

            if execution.status == 'running':
                execution.status = 'completed'
                execution.completed_at = datetime.utcnow()

                # Calculate metrics
                execution.recovery_metrics = self._calculate_recovery_metrics(execution)

        except Exception as e:
            execution.status = 'failed'
            execution.issues_encountered.append(str(e))

        # Release allocated resources
        procedure_obj = self.recovery_procedures[execution.procedure_id]
        for resource_name in procedure_obj.required_resources:
            self._release_resource(resource_name, execution.id)

    def _execute_step(self, step: Dict[str, Any], execution: RecoveryExecution) -> Dict[str, Any]:
        """Execute a single procedure step"""
        step_type = step.get('type', 'manual')

        if step_type == 'automated':
            return self._execute_automated_step(step, execution)
        elif step_type == 'verification':
            return self._execute_verification_step(step, execution)
        else:
            # Manual step - simulate completion
            return {'success': True, 'message': f'Manual step completed: {step.get("name", "Unknown")}'}

    def _execute_automated_step(self, step: Dict[str, Any], execution: RecoveryExecution) -> Dict[str, Any]:
        """Execute an automated procedure step"""
        action = step.get('action', '')

        try:
            if action == 'restart_service':
                # Simulate service restart
                service_name = step.get('service_name', 'unknown')
                return {'success': True, 'message': f'Service {service_name} restarted successfully'}

            elif action == 'failover_system':
                # Simulate system failover
                system_name = step.get('system_name', 'unknown')
                return {'success': True, 'message': f'System {system_name} failed over successfully'}

            elif action == 'restore_backup':
                # Simulate backup restore
                if self.backup:
                    # In production, this would call backup service
                    return {'success': True, 'message': 'Backup restored successfully'}
                else:
                    return {'success': False, 'error': 'Backup service not available'}

            else:
                return {'success': True, 'message': f'Automated action {action} completed'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_verification_step(self, step: Dict[str, Any], execution: RecoveryExecution) -> Dict[str, Any]:
        """Execute a verification step"""
        verification_type = step.get('verification_type', 'manual')

        if verification_type == 'service_check':
            service_name = step.get('service_name', 'unknown')
            # Simulate service check
            return {'success': True, 'message': f'Service {service_name} is running'}

        elif verification_type == 'connectivity_check':
            target = step.get('target', 'unknown')
            # Simulate connectivity check
            return {'success': True, 'message': f'Connectivity to {target} verified'}

        else:
            return {'success': True, 'message': f'Verification {verification_type} completed'}

    def _calculate_recovery_metrics(self, execution: RecoveryExecution) -> Dict[str, Any]:
        """Calculate recovery execution metrics"""
        if not execution.completed_at:
            return {}

        duration = (execution.completed_at - execution.started_at).total_seconds()
        success_rate = len([s for s in execution.executed_steps if s['status'] == 'completed']) / len(execution.executed_steps) * 100

        return {
            'total_duration_seconds': duration,
            'steps_completed': len([s for s in execution.executed_steps if s['status'] == 'completed']),
            'steps_failed': len([s for s in execution.executed_steps if s['status'] == 'failed']),
            'success_rate': round(success_rate, 1),
            'issues_count': len(execution.issues_encountered)
        }

    def _release_resource(self, resource_name: str, execution_id: str):
        """Release allocated resource"""
        resource = self.recovery_resources.get(resource_name)
        if resource and resource.quantity_allocated > 0:
            resource.quantity_allocated -= 1
            logger.debug(f"Resource released: {resource_name} from execution {execution_id}")

    def create_failover_configuration(self, config_data: Dict[str, Any]) -> str:
        """
        Create a failover configuration
        Returns configuration ID
        """
        config_id = str(uuid.uuid4())

        config = FailoverConfiguration(
            id=config_id,
            system_name=config_data['system_name'],
            primary_location=config_data['primary_location'],
            secondary_location=config_data['secondary_location'],
            failover_type=FailoverType[config_data['failover_type'].upper()],
            trigger_conditions=config_data.get('trigger_conditions', []),
            failover_procedures=config_data.get('failover_procedures', []),
            failback_procedures=config_data.get('failback_procedures', []),
            rto_minutes=config_data.get('rto_minutes', 240),
            rpo_minutes=config_data.get('rpo_minutes', 60)
        )

        self.failover_configurations[config_id] = config

        logger.info(f"Failover configuration created for: {config.system_name}")
        return config_id

    def register_recovery_resource(self, resource_data: Dict[str, Any]) -> str:
        """
        Register a recovery resource
        Returns resource ID
        """
        resource_id = str(uuid.uuid4())

        resource = RecoveryResource(
            id=resource_id,
            resource_type=resource_data['resource_type'],
            resource_name=resource_data['resource_name'],
            quantity_available=resource_data['quantity_available'],
            location=resource_data.get('location', 'primary'),
            contact_info=resource_data.get('contact_info', {})
        )

        self.recovery_resources[resource_id] = resource

        logger.info(f"Recovery resource registered: {resource.resource_name} ({resource.resource_type})")
        return resource_id

    def resolve_disaster(self, disaster_id: str, resolution_data: Dict[str, Any]) -> bool:
        """
        Resolve a disaster and complete recovery
        """
        if disaster_id not in self.disaster_declarations:
            return False

        disaster = self.disaster_declarations[disaster_id]

        disaster.status = 'resolved'
        disaster.resolved_at = datetime.utcnow()

        # Execute failback procedures if applicable
        for system in disaster.affected_systems:
            config = self._find_failover_config(system)
            if config and config.failover_type != FailoverType.AUTOMATIC:
                self._execute_failback(config)

        # Generate lessons learned
        lessons_learned = self._generate_lessons_learned(disaster, resolution_data)

        # Update continuity plans based on lessons learned
        if self.continuity:
            self.continuity.update_plans_from_incident(disaster, lessons_learned)

        logger.info(f"Disaster resolved: {disaster.disaster_type.value} - Duration: {(disaster.resolved_at - disaster.declared_at).total_seconds() / 3600:.1f} hours")
        return True

    def _execute_failback(self, config: FailoverConfiguration):
        """Execute failback to primary location"""
        logger.info(f"Executing failback for {config.system_name} to {config.primary_location}")

        # In production, this would execute failback procedures

    def _generate_lessons_learned(self, disaster: DisasterDeclaration, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lessons learned from disaster recovery"""
        duration = (disaster.resolved_at - disaster.declared_at).total_seconds() / 3600 if disaster.resolved_at else 0

        return {
            'disaster_type': disaster.disaster_type.value,
            'severity': disaster.severity_level,
            'duration_hours': round(duration, 1),
            'affected_systems': disaster.affected_systems,
            'success_factors': resolution_data.get('success_factors', []),
            'challenges_encountered': resolution_data.get('challenges', []),
            'improvements_needed': resolution_data.get('improvements', []),
            'preventive_measures': resolution_data.get('preventive_measures', [])
        }

    def get_disaster_recovery_status(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive disaster recovery status"""
        # Filter data by tenant
        tenant_disasters = [d for d in self.disaster_declarations.values() if d.id.startswith(tenant_id)]
        tenant_executions = [e for e in self.recovery_executions.values() if e.id.startswith(tenant_id)]
        tenant_resources = [r for r in self.recovery_resources.values() if r.id.startswith(tenant_id)]

        # Calculate metrics
        disaster_stats = self._calculate_disaster_statistics(tenant_disasters)
        recovery_stats = self._calculate_recovery_statistics(tenant_executions)
        resource_stats = self._calculate_resource_statistics(tenant_resources)
        readiness_assessment = self._assess_recovery_readiness()

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'disaster_statistics': disaster_stats,
            'recovery_statistics': recovery_stats,
            'resource_statistics': resource_stats,
            'readiness_assessment': readiness_assessment,
            'active_disasters': [d.id for d in tenant_disasters if d.status == 'active'],
            'active_recoveries': [e.id for e in tenant_executions if e.status == 'running']
        }

    def _calculate_disaster_statistics(self, disasters: List[DisasterDeclaration]) -> Dict[str, Any]:
        """Calculate disaster statistics"""
        if not disasters:
            return {'total_disasters': 0, 'active_disasters': 0, 'avg_resolution_time': 0}

        total = len(disasters)
        active = len([d for d in disasters if d.status == 'active'])
        resolved = [d for d in disasters if d.resolved_at]

        avg_resolution_time = 0
        if resolved:
            resolution_times = [
                (d.resolved_at - d.declared_at).total_seconds() / 3600
                for d in resolved
            ]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)

        # Count by type
        by_type = {}
        for disaster in disasters:
            type_key = disaster.disaster_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        return {
            'total_disasters': total,
            'active_disasters': active,
            'resolved_disasters': len(resolved),
            'avg_resolution_time_hours': round(avg_resolution_time, 1),
            'by_type': by_type
        }

    def _calculate_recovery_statistics(self, executions: List[RecoveryExecution]) -> Dict[str, Any]:
        """Calculate recovery execution statistics"""
        if not executions:
            return {'total_executions': 0, 'success_rate': 0, 'avg_duration': 0}

        total = len(executions)
        completed = len([e for e in executions if e.status == 'completed'])
        success_rate = (completed / total * 100) if total > 0 else 0

        completed_executions = [e for e in executions if e.completed_at]
        avg_duration = 0
        if completed_executions:
            durations = [(e.completed_at - e.started_at).total_seconds() / 60 for e in completed_executions]
            avg_duration = sum(durations) / len(durations)

        return {
            'total_executions': total,
            'completed_executions': completed,
            'success_rate': round(success_rate, 1),
            'avg_duration_minutes': round(avg_duration, 1)
        }

    def _calculate_resource_statistics(self, resources: List[RecoveryResource]) -> Dict[str, Any]:
        """Calculate recovery resource statistics"""
        if not resources:
            return {'total_resources': 0, 'available_resources': 0, 'utilization_rate': 0}

        total = len(resources)
        available = len([r for r in resources if r.availability_status == 'available'])
        utilization_rate = ((total - available) / total * 100) if total > 0 else 0

        # Count by type
        by_type = {}
        for resource in resources:
            type_key = resource.resource_type
            by_type[type_key] = by_type.get(type_key, {'total': 0, 'available': 0})
            by_type[type_key]['total'] += 1
            if resource.availability_status == 'available':
                by_type[type_key]['available'] += 1

        return {
            'total_resources': total,
            'available_resources': available,
            'utilization_rate': round(utilization_rate, 1),
            'by_type': by_type
        }

    def _assess_recovery_readiness(self) -> Dict[str, Any]:
        """Assess overall disaster recovery readiness"""
        readiness_score = 100

        # Check procedure coverage
        total_procedures = len(self.recovery_procedures)
        if total_procedures < 10:  # Arbitrary minimum
            readiness_score -= 20

        # Check resource availability
        resource_availability = len([r for r in self.recovery_resources.values() if r.availability_status == 'available'])
        total_resources = len(self.recovery_resources)
        if total_resources > 0 and (resource_availability / total_resources) < 0.8:
            readiness_score -= 15

        # Check failover configurations
        failover_configs = len([c for c in self.failover_configurations.values() if c.is_active])
        if failover_configs < 5:  # Arbitrary minimum
            readiness_score -= 10

        # Check recent testing
        recent_tests = len([p for p in self.recovery_procedures.values() if p.last_tested and
                           (datetime.utcnow() - p.last_tested).days <= 90])
        if recent_tests < total_procedures * 0.5:
            readiness_score -= 15

        readiness_level = 'HIGH' if readiness_score >= 80 else 'MEDIUM' if readiness_score >= 60 else 'LOW'

        return {
            'readiness_score': max(readiness_score, 0),
            'readiness_level': readiness_level,
            'procedures_count': total_procedures,
            'resources_available': resource_availability,
            'failover_configs': failover_configs,
            'recently_tested': recent_tests
        }

    def check_disaster_recovery_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 22301 disaster recovery compliance"""
        disasters = [d for d in self.disaster_declarations.values() if d.id.startswith(tenant_id)]
        procedures = [p for p in self.recovery_procedures.values() if p.id.startswith(tenant_id)]
        executions = [e for e in self.recovery_executions.values() if e.id.startswith(tenant_id)]

        compliance_status = self._assess_dr_compliance(disasters, procedures, executions)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_standard': 'ISO 22301:2019',
            'last_check': datetime.utcnow().isoformat()
        }

    def _assess_dr_compliance(self, disasters: List[DisasterDeclaration],
                            procedures: List[RecoveryProcedure],
                            executions: List[RecoveryExecution]) -> Dict[str, Any]:
        """Assess ISO 22301 disaster recovery compliance"""
        issues = []

        # Check business impact analysis
        if not disasters:
            issues.append("No disaster declarations or impact analyses found")

        # Check recovery procedures
        if len(procedures) < 5:
            issues.append("Insufficient number of recovery procedures defined")

        # Check procedure testing
        untested_procedures = [p for p in procedures if not p.last_tested or
                              (datetime.utcnow() - p.last_tested).days > 180]
        if untested_procedures:
            issues.append(f"{len(untested_procedures)} procedures not tested within 6 months")

        # Check resource allocation
        if not self.recovery_resources:
            issues.append("No recovery resources defined")

        # Check failover configurations
        if len(self.failover_configurations) < 3:
            issues.append("Insufficient failover configurations")

        compliance_score = max(0, 100 - (len(issues) * 8))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_dr_recommendations(issues)
        }

    def _generate_dr_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        if any('procedures' in issue.lower() for issue in issues):
            recommendations.append("Develop comprehensive recovery procedures for all critical business processes")

        if any('test' in issue.lower() for issue in issues):
            recommendations.append("Implement regular testing schedule for all recovery procedures")

        if any('resource' in issue.lower() for issue in issues):
            recommendations.append("Define and allocate necessary recovery resources")

        if any('failover' in issue.lower() for issue in issues):
            recommendations.append("Configure failover mechanisms for critical systems")

        if not recommendations:
            recommendations.append("Maintain current disaster recovery capabilities and conduct regular reviews")

        return recommendations