"""
ISO 27001 Physical and Environmental Security Management
Physical and Environmental Security Framework

Dieses Modul implementiert das Physical and Environmental Security Management Framework
gemäß ISO 27001 Annex A.11 für VALEO-NeuroERP mit Secure Areas, Equipment Security und Environmental Controls.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Physical access levels"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    SECURE = "secure"
    HIGHLY_SECURE = "highly_secure"
    MAXIMUM_SECURITY = "maximum_security"


class SecurityZone(Enum):
    """Security zone classifications"""
    PUBLIC = "public"
    PERIMETER = "perimeter"
    BUILDING = "building"
    OFFICE = "office"
    SERVER_ROOM = "server_room"
    DATA_CENTER = "data_center"
    SECURE_LAB = "secure_lab"


class AccessMethod(Enum):
    """Physical access methods"""
    KEY = "key"
    CARD = "card"
    BIOMETRIC = "biometric"
    PIN = "pin"
    KEY_CARD = "key_card"
    MOBILE_APP = "mobile_app"
    REMOTE_ACCESS = "remote_access"


class EquipmentType(Enum):
    """Equipment classifications"""
    SERVER = "server"
    NETWORK_EQUIPMENT = "network_equipment"
    STORAGE_SYSTEM = "storage_system"
    WORKSTATION = "workstation"
    MOBILE_DEVICE = "mobile_device"
    PERIPHERAL = "peripheral"
    MONITOR = "monitor"
    PRINTER = "printer"


class EnvironmentalControl(Enum):
    """Environmental control types"""
    HVAC = "hvac"
    FIRE_SUPPRESSION = "fire_suppression"
    POWER_BACKUP = "power_backup"
    TEMPERATURE_MONITORING = "temperature_monitoring"
    HUMIDITY_CONTROL = "humidity_control"
    AIR_QUALITY = "air_quality"
    WATER_DETECTION = "water_detection"
    SMOKE_DETECTION = "smoke_detection"


class AlarmType(Enum):
    """Security alarm types"""
    INTRUSION = "intrusion"
    FIRE = "fire"
    ENVIRONMENTAL = "environmental"
    EQUIPMENT_FAILURE = "equipment_failure"
    ACCESS_VIOLATION = "access_violation"
    EMERGENCY = "emergency"


class AlarmSeverity(Enum):
    """Alarm severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityZone:
    """Security zone definition"""
    id: str
    name: str
    zone_type: SecurityZone
    access_level: AccessLevel
    location: str
    perimeter_description: str
    authorized_personnel: List[str] = field(default_factory=list)
    access_methods: List[AccessMethod] = field(default_factory=list)
    surveillance_cameras: List[str] = field(default_factory=list)
    alarm_systems: List[str] = field(default_factory=list)
    environmental_controls: List[EnvironmentalControl] = field(default_factory=list)
    emergency_procedures: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessLog:
    """Physical access log entry"""
    id: str
    zone_id: str
    person_id: str
    person_name: str
    access_method: AccessMethod
    access_time: datetime
    access_result: str  # granted, denied, forced
    denial_reason: str = ""
    location_details: str = ""
    authorized_by: Optional[str] = None
    additional_notes: str = ""


@dataclass
class EquipmentInventory:
    """Equipment inventory record"""
    id: str
    asset_tag: str
    equipment_type: EquipmentType
    manufacturer: str
    model: str
    serial_number: str
    location: str
    zone_id: str
    assigned_to: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    security_classification: str = "internal"
    encryption_enabled: bool = False
    remote_wipe_capable: bool = False
    last_inventory_check: Optional[datetime] = None
    maintenance_schedule: str = ""
    disposal_date: Optional[datetime] = None
    disposal_method: str = ""
    is_active: bool = True


@dataclass
class EnvironmentalMonitoring:
    """Environmental monitoring record"""
    id: str
    zone_id: str
    control_type: EnvironmentalControl
    sensor_id: str
    measurement_time: datetime
    temperature_celsius: Optional[float] = None
    humidity_percent: Optional[float] = None
    air_quality_index: Optional[int] = None
    power_status: Optional[str] = None
    smoke_detected: bool = False
    water_detected: bool = False
    alarm_triggered: bool = False
    alarm_type: Optional[AlarmType] = None
    alarm_severity: Optional[AlarmSeverity] = None
    response_actions: List[str] = field(default_factory=list)


@dataclass
class SecurityAlarm:
    """Security alarm record"""
    id: str
    zone_id: str
    alarm_type: AlarmType
    severity: AlarmSeverity
    triggered_at: datetime
    sensor_location: str
    description: str
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: str = ""
    false_alarm: bool = False
    escalation_level: int = 1
    notified_parties: List[str] = field(default_factory=list)


@dataclass
class VisitorAccess:
    """Visitor access record"""
    id: str
    visitor_name: str
    visitor_company: str
    host_employee: str
    purpose: str
    access_zones: List[str] = field(default_factory=list)
    access_start: datetime
    access_end: datetime
    access_methods: List[AccessMethod] = field(default_factory=list)
    escort_required: bool = True
    escort_name: Optional[str] = None
    special_instructions: str = ""
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    assets_provided: List[str] = field(default_factory=list)
    security_briefing_completed: bool = False


@dataclass
class MaintenanceAccess:
    """Maintenance access record"""
    id: str
    contractor_name: str
    contractor_company: str
    contact_person: str
    work_description: str
    access_zones: List[str] = field(default_factory=list)
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    authorized_by: str
    supervisor_present: bool = True
    supervisor_name: Optional[str] = None
    security_clearance_verified: bool = False
    equipment_used: List[str] = field(default_factory=list)
    work_completed: bool = False
    post_work_verification: str = ""


@dataclass
class SecurityIncident:
    """Physical security incident"""
    id: str
    zone_id: str
    incident_type: str
    severity: str
    reported_at: datetime
    reported_by: str
    description: str
    location_details: str
    persons_involved: List[str] = field(default_factory=list)
    witnesses: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    investigation_findings: str = ""
    corrective_actions: List[str] = field(default_factory=list)
    preventive_measures: List[str] = field(default_factory=list)
    resolved_at: Optional[datetime] = None
    resolution_status: str = "open"


@dataclass
class PhysicalSecurityDashboard:
    """Physical security dashboard data"""
    id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    zone_status: Dict[str, Any] = field(default_factory=dict)
    access_statistics: Dict[str, Any] = field(default_factory=dict)
    alarm_summary: Dict[str, Any] = field(default_factory=dict)
    environmental_status: Dict[str, Any] = field(default_factory=dict)
    equipment_inventory: Dict[str, Any] = field(default_factory=dict)
    visitor_activity: Dict[str, Any] = field(default_factory=dict)
    maintenance_activity: Dict[str, Any] = field(default_factory=dict)
    security_incidents: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class ISO27001PhysicalSecurity:
    """
    ISO 27001 Physical and Environmental Security Management
    Implements Annex A.11 - Physical and Environmental Security
    """

    def __init__(self, db_session, access_control_service=None, monitoring_service=None):
        self.db = db_session
        self.access_control = access_control_service
        self.monitoring = monitoring_service

        # Physical security components
        self.security_zones: Dict[str, SecurityZone] = {}
        self.access_logs: List[AccessLog] = {}
        self.equipment_inventory: Dict[str, EquipmentInventory] = {}
        self.environmental_monitoring: List[EnvironmentalMonitoring] = {}
        self.security_alarms: List[SecurityAlarm] = {}
        self.visitor_access: List[VisitorAccess] = {}
        self.maintenance_access: List[MaintenanceAccess] = {}
        self.security_incidents: List[SecurityIncident] = {}

        # Security configuration
        self.security_config = self._initialize_security_config()

        # Default security zones
        self._initialize_default_zones()

    def _initialize_security_config(self) -> Dict[str, Any]:
        """Initialize physical security configuration"""
        return {
            'access_control': {
                'max_visitor_duration_hours': 8,
                'escort_required_zones': ['server_room', 'data_center', 'secure_lab'],
                'access_log_retention_days': 365,
                'failed_access_lockout_minutes': 15
            },
            'environmental_monitoring': {
                'temperature_range_celsius': {'min': 18, 'max': 27},
                'humidity_range_percent': {'min': 30, 'max': 60},
                'monitoring_interval_seconds': 300,
                'alarm_escalation_minutes': [5, 15, 60]
            },
            'equipment_security': {
                'inventory_check_frequency_days': 90,
                'warranty_monitoring_days': 30,
                'disposal_verification_required': True,
                'encryption_required_types': ['server', 'storage_system', 'mobile_device']
            },
            'alarm_management': {
                'auto_acknowledgement_minutes': 5,
                'escalation_levels': 3,
                'emergency_response_minutes': 10,
                'notification_channels': ['email', 'sms', 'alarm_system']
            },
            'maintenance_security': {
                'background_check_required': True,
                'supervisor_presence_required': True,
                'post_work_verification_required': True,
                'access_log_review_required': True
            }
        }

    def _initialize_default_zones(self):
        """Initialize default security zones"""
        default_zones = [
            {
                'id': 'perimeter',
                'name': 'Building Perimeter',
                'zone_type': SecurityZone.PERIMETER,
                'access_level': AccessLevel.PUBLIC,
                'location': 'Exterior building boundary',
                'perimeter_description': 'Fenced perimeter with controlled entry points',
                'access_methods': [AccessMethod.CARD, AccessMethod.BIOMETRIC],
                'surveillance_cameras': ['perimeter_cam_01', 'perimeter_cam_02'],
                'alarm_systems': ['perimeter_alarm_01'],
                'emergency_procedures': {
                    'intrusion': 'Activate alarm system and notify security',
                    'fire': 'Evacuate building and call fire department'
                }
            },
            {
                'id': 'server_room',
                'name': 'Server Room',
                'zone_type': SecurityZone.SERVER_ROOM,
                'access_level': AccessLevel.MAXIMUM_SECURITY,
                'location': 'Basement Level, Room B-12',
                'perimeter_description': 'Mantrap entry with biometric access control',
                'authorized_personnel': ['system_administrators', 'it_security_team'],
                'access_methods': [AccessMethod.BIOMETRIC, AccessMethod.KEY_CARD],
                'surveillance_cameras': ['server_room_cam_01', 'server_room_cam_02'],
                'alarm_systems': ['server_room_alarm_01'],
                'environmental_controls': [
                    EnvironmentalControl.HVAC,
                    EnvironmentalControl.TEMPERATURE_MONITORING,
                    EnvironmentalControl.HUMIDITY_CONTROL,
                    EnvironmentalControl.FIRE_SUPPRESSION,
                    EnvironmentalControl.POWER_BACKUP
                ],
                'emergency_procedures': {
                    'fire': 'Activate fire suppression and evacuate',
                    'power_failure': 'Switch to backup power systems',
                    'environmental_alarm': 'Check environmental controls and alert maintenance'
                }
            },
            {
                'id': 'office_area',
                'name': 'Office Area',
                'zone_type': SecurityZone.OFFICE,
                'access_level': AccessLevel.RESTRICTED,
                'location': 'Floors 1-3, General office spaces',
                'perimeter_description': 'Card access entry points with time-based restrictions',
                'access_methods': [AccessMethod.CARD, AccessMethod.PIN],
                'surveillance_cameras': ['office_cam_01', 'office_cam_02', 'office_cam_03'],
                'emergency_procedures': {
                    'intrusion': 'Secure area and notify security',
                    'medical_emergency': 'Call emergency services and provide first aid'
                }
            }
        ]

        for zone_data in default_zones:
            zone = SecurityZone(**zone_data)
            self.security_zones[zone.id] = zone

    def create_security_zone(self, zone_data: Dict[str, Any]) -> str:
        """
        Create a new security zone
        Returns zone ID
        """
        zone_id = str(uuid.uuid4())

        zone = SecurityZone(
            id=zone_id,
            name=zone_data['name'],
            zone_type=SecurityZone[zone_data['zone_type'].upper()],
            access_level=AccessLevel[zone_data['access_level'].upper()],
            location=zone_data['location'],
            perimeter_description=zone_data['perimeter_description'],
            authorized_personnel=zone_data.get('authorized_personnel', []),
            access_methods=[AccessMethod[method.upper()] for method in zone_data.get('access_methods', [])],
            surveillance_cameras=zone_data.get('surveillance_cameras', []),
            alarm_systems=zone_data.get('alarm_systems', []),
            environmental_controls=[EnvironmentalControl[control.upper()] for control in zone_data.get('environmental_controls', [])],
            emergency_procedures=zone_data.get('emergency_procedures', {})
        )

        self.security_zones[zone_id] = zone

        logger.info(f"Security zone created: {zone.name} ({zone.zone_type.value})")
        return zone_id

    def log_physical_access(self, access_data: Dict[str, Any]) -> str:
        """
        Log physical access attempt
        Returns access log ID
        """
        log_id = str(uuid.uuid4())

        access_log = AccessLog(
            id=log_id,
            zone_id=access_data['zone_id'],
            person_id=access_data['person_id'],
            person_name=access_data['person_name'],
            access_method=AccessMethod[access_data['access_method'].upper()],
            access_time=datetime.utcnow(),
            access_result=access_data['access_result'],
            denial_reason=access_data.get('denial_reason', ''),
            location_details=access_data.get('location_details', ''),
            authorized_by=access_data.get('authorized_by'),
            additional_notes=access_data.get('additional_notes', '')
        )

        if access_data['zone_id'] not in self.access_logs:
            self.access_logs[access_data['zone_id']] = []

        self.access_logs[access_data['zone_id']].append(access_log)

        # Check for security violations
        if access_log.access_result == 'denied':
            self._handle_access_denial(access_log)

        logger.info(f"Physical access logged: {access_log.person_name} → {access_log.zone_id} ({access_log.access_result})")
        return log_id

    def _handle_access_denial(self, access_log: AccessLog):
        """Handle access denial security event"""
        # Create security incident for repeated access denials
        denial_count = len([log for log in self.access_logs[access_log.zone_id][-10:]
                           if log.person_id == access_log.person_id and log.access_result == 'denied'])

        if denial_count >= 3:
            incident_data = {
                'zone_id': access_log.zone_id,
                'incident_type': 'repeated_access_denial',
                'severity': 'medium',
                'reported_by': 'access_control_system',
                'description': f'Repeated access denial for {access_log.person_name} in zone {access_log.zone_id}',
                'location_details': access_log.location_details,
                'persons_involved': [access_log.person_id],
                'immediate_actions': ['Review access permissions', 'Notify security team']
            }
            self.report_security_incident(incident_data)

    def register_equipment(self, equipment_data: Dict[str, Any]) -> str:
        """
        Register equipment in inventory
        Returns equipment ID
        """
        equipment_id = str(uuid.uuid4())

        equipment = EquipmentInventory(
            id=equipment_id,
            asset_tag=equipment_data['asset_tag'],
            equipment_type=EquipmentType[equipment_data['equipment_type'].upper()],
            manufacturer=equipment_data['manufacturer'],
            model=equipment_data['model'],
            serial_number=equipment_data['serial_number'],
            location=equipment_data['location'],
            zone_id=equipment_data['zone_id'],
            assigned_to=equipment_data.get('assigned_to'),
            purchase_date=equipment_data.get('purchase_date'),
            warranty_expiry=equipment_data.get('warranty_expiry'),
            security_classification=equipment_data.get('security_classification', 'internal'),
            encryption_enabled=equipment_data.get('encryption_enabled', False),
            remote_wipe_capable=equipment_data.get('remote_wipe_capable', False),
            maintenance_schedule=equipment_data.get('maintenance_schedule', '')
        )

        self.equipment_inventory[equipment_id] = equipment

        # Check security requirements
        self._validate_equipment_security(equipment)

        logger.info(f"Equipment registered: {equipment.asset_tag} ({equipment.equipment_type.value})")
        return equipment_id

    def _validate_equipment_security(self, equipment: EquipmentInventory):
        """Validate equipment meets security requirements"""
        issues = []

        # Check encryption requirements
        if equipment.equipment_type in [EquipmentType.SERVER, EquipmentType.STORAGE_SYSTEM, EquipmentType.MOBILE_DEVICE]:
            if not equipment.encryption_enabled:
                issues.append("Encryption required but not enabled")

        # Check remote wipe capability for mobile devices
        if equipment.equipment_type == EquipmentType.MOBILE_DEVICE:
            if not equipment.remote_wipe_capable:
                issues.append("Remote wipe capability required for mobile devices")

        if issues:
            logger.warning(f"Equipment security validation failed for {equipment.asset_tag}: {issues}")

    def monitor_environmental_conditions(self, monitoring_data: Dict[str, Any]) -> str:
        """
        Record environmental monitoring data
        Returns monitoring record ID
        """
        record_id = str(uuid.uuid4())

        monitoring = EnvironmentalMonitoring(
            id=record_id,
            zone_id=monitoring_data['zone_id'],
            control_type=EnvironmentalControl[monitoring_data['control_type'].upper()],
            sensor_id=monitoring_data['sensor_id'],
            measurement_time=datetime.utcnow(),
            temperature_celsius=monitoring_data.get('temperature_celsius'),
            humidity_percent=monitoring_data.get('humidity_percent'),
            air_quality_index=monitoring_data.get('air_quality_index'),
            power_status=monitoring_data.get('power_status'),
            smoke_detected=monitoring_data.get('smoke_detected', False),
            water_detected=monitoring_data.get('water_detected', False)
        )

        # Check for alarm conditions
        alarm_triggered, alarm_type, severity = self._check_environmental_alarms(monitoring)

        if alarm_triggered:
            monitoring.alarm_triggered = True
            monitoring.alarm_type = alarm_type
            monitoring.alarm_severity = severity
            monitoring.response_actions = self._get_alarm_response_actions(alarm_type, severity)

            # Create security alarm
            self._create_environmental_alarm(monitoring)

        self.environmental_monitoring.append(monitoring)

        return record_id

    def _check_environmental_alarms(self, monitoring: EnvironmentalMonitoring) -> Tuple[bool, Optional[AlarmType], Optional[AlarmSeverity]]:
        """Check if environmental conditions trigger alarms"""
        config = self.security_config['environmental_monitoring']

        # Temperature check
        if monitoring.temperature_celsius is not None:
            temp_range = config['temperature_range_celsius']
            if monitoring.temperature_celsius < temp_range['min'] or monitoring.temperature_celsius > temp_range['max']:
                severity = AlarmSeverity.HIGH if abs(monitoring.temperature_celsius - 22.5) > 10 else AlarmSeverity.MEDIUM
                return True, AlarmType.ENVIRONMENTAL, severity

        # Humidity check
        if monitoring.humidity_percent is not None:
            humidity_range = config['humidity_range_percent']
            if monitoring.humidity_percent < humidity_range['min'] or monitoring.humidity_percent > humidity_range['max']:
                return True, AlarmType.ENVIRONMENTAL, AlarmSeverity.MEDIUM

        # Smoke detection
        if monitoring.smoke_detected:
            return True, AlarmType.FIRE, AlarmSeverity.CRITICAL

        # Water detection
        if monitoring.water_detected:
            return True, AlarmType.ENVIRONMENTAL, AlarmSeverity.HIGH

        return False, None, None

    def _get_alarm_response_actions(self, alarm_type: AlarmType, severity: AlarmSeverity) -> List[str]:
        """Get appropriate response actions for alarm"""
        actions = []

        if alarm_type == AlarmType.FIRE:
            actions.extend([
                "Activate fire suppression systems",
                "Evacuate affected zones",
                "Notify fire department",
                "Shutdown non-essential systems"
            ])
        elif alarm_type == AlarmType.ENVIRONMENTAL:
            if severity == AlarmSeverity.CRITICAL:
                actions.extend([
                    "Immediate evacuation of affected areas",
                    "Notify emergency response team",
                    "Shutdown critical systems if necessary"
                ])
            else:
                actions.extend([
                    "Check environmental control systems",
                    "Notify maintenance team",
                    "Monitor conditions closely"
                ])

        return actions

    def _create_environmental_alarm(self, monitoring: EnvironmentalMonitoring):
        """Create environmental alarm"""
        alarm = SecurityAlarm(
            id=str(uuid.uuid4()),
            zone_id=monitoring.zone_id,
            alarm_type=monitoring.alarm_type,
            severity=monitoring.alarm_severity,
            triggered_at=monitoring.measurement_time,
            sensor_location=f"Zone {monitoring.zone_id}, Sensor {monitoring.sensor_id}",
            description=f"Environmental alarm: {monitoring.alarm_type.value}",
            escalation_level=2 if monitoring.alarm_severity == AlarmSeverity.CRITICAL else 1
        )

        self.security_alarms.append(alarm)

        logger.warning(f"Environmental alarm triggered: {alarm.description} in zone {alarm.zone_id}")

    def register_visitor_access(self, visitor_data: Dict[str, Any]) -> str:
        """
        Register visitor access
        Returns visitor access ID
        """
        access_id = str(uuid.uuid4())

        visitor = VisitorAccess(
            id=access_id,
            visitor_name=visitor_data['visitor_name'],
            visitor_company=visitor_data['visitor_company'],
            host_employee=visitor_data['host_employee'],
            purpose=visitor_data['purpose'],
            access_zones=visitor_data['access_zones'],
            access_start=visitor_data['access_start'],
            access_end=visitor_data['access_end'],
            access_methods=[AccessMethod[method.upper()] for method in visitor_data.get('access_methods', [])],
            escort_required=visitor_data.get('escort_required', True),
            escort_name=visitor_data.get('escort_name'),
            special_instructions=visitor_data.get('special_instructions', ''),
            security_briefing_completed=visitor_data.get('security_briefing_completed', False)
        )

        self.visitor_access.append(visitor)

        # Log visitor check-in
        self._log_visitor_check_in(visitor)

        logger.info(f"Visitor access registered: {visitor.visitor_name} from {visitor.visitor_company}")
        return access_id

    def _log_visitor_check_in(self, visitor: VisitorAccess):
        """Log visitor check-in event"""
        for zone_id in visitor.access_zones:
            access_data = {
                'zone_id': zone_id,
                'person_id': f"visitor_{visitor.id}",
                'person_name': visitor.visitor_name,
                'access_method': visitor.access_methods[0].value if visitor.access_methods else 'escort',
                'access_result': 'granted',
                'authorized_by': visitor.host_employee,
                'additional_notes': f"Visitor access - escorted by {visitor.escort_name}" if visitor.escort_required else "Visitor access - unescorted"
            }
            self.log_physical_access(access_data)

    def register_maintenance_access(self, maintenance_data: Dict[str, Any]) -> str:
        """
        Register maintenance access
        Returns maintenance access ID
        """
        access_id = str(uuid.uuid4())

        maintenance = MaintenanceAccess(
            id=access_id,
            contractor_name=maintenance_data['contractor_name'],
            contractor_company=maintenance_data['contractor_company'],
            contact_person=maintenance_data['contact_person'],
            work_description=maintenance_data['work_description'],
            access_zones=maintenance_data['access_zones'],
            scheduled_start=maintenance_data['scheduled_start'],
            scheduled_end=maintenance_data['scheduled_end'],
            authorized_by=maintenance_data['authorized_by'],
            supervisor_present=maintenance_data.get('supervisor_present', True),
            supervisor_name=maintenance_data.get('supervisor_name'),
            security_clearance_verified=maintenance_data.get('security_clearance_verified', False)
        )

        self.maintenance_access.append(maintenance)

        logger.info(f"Maintenance access registered: {maintenance.contractor_company} - {maintenance.work_description}")
        return access_id

    def report_security_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Report a physical security incident
        Returns incident ID
        """
        incident_id = str(uuid.uuid4())

        incident = SecurityIncident(
            id=incident_id,
            zone_id=incident_data['zone_id'],
            incident_type=incident_data['incident_type'],
            severity=incident_data['severity'],
            reported_at=datetime.utcnow(),
            reported_by=incident_data['reported_by'],
            description=incident_data['description'],
            location_details=incident_data.get('location_details', ''),
            persons_involved=incident_data.get('persons_involved', []),
            witnesses=incident_data.get('witnesses', []),
            immediate_actions=incident_data.get('immediate_actions', [])
        )

        self.security_incidents.append(incident)

        # Create corresponding alarm if not already created
        if incident.severity in ['high', 'critical']:
            alarm = SecurityAlarm(
                id=str(uuid.uuid4()),
                zone_id=incident.zone_id,
                alarm_type=AlarmType.INTRUSION if 'intrusion' in incident.incident_type.lower() else AlarmType.EMERGENCY,
                severity=AlarmSeverity.CRITICAL if incident.severity == 'critical' else AlarmSeverity.HIGH,
                triggered_at=incident.reported_at,
                sensor_location=incident.location_details,
                description=f"Security incident: {incident.description}",
                escalation_level=3
            )
            self.security_alarms.append(alarm)

        logger.warning(f"Security incident reported: {incident.incident_type} in zone {incident.zone_id}")
        return incident_id

    def acknowledge_alarm(self, alarm_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge a security alarm
        """
        for alarm in self.security_alarms:
            if alarm.id == alarm_id:
                alarm.acknowledged_at = datetime.utcnow()
                alarm.acknowledged_by = acknowledged_by
                logger.info(f"Alarm acknowledged: {alarm_id} by {acknowledged_by}")
                return True
        return False

    def resolve_alarm(self, alarm_id: str, resolution_data: Dict[str, Any]) -> bool:
        """
        Resolve a security alarm
        """
        for alarm in self.security_alarms:
            if alarm.id == alarm_id:
                alarm.resolved_at = datetime.utcnow()
                alarm.resolved_by = resolution_data.get('resolved_by')
                alarm.resolution_notes = resolution_data.get('resolution_notes', '')
                alarm.false_alarm = resolution_data.get('false_alarm', False)
                logger.info(f"Alarm resolved: {alarm_id}")
                return True
        return False

    def get_physical_security_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive physical security dashboard"""
        # Get zone status
        zone_status = {}
        for zone_id, zone in self.security_zones.items():
            recent_access = len([log for logs in self.access_logs.values() for log in logs
                               if log.zone_id == zone_id and (datetime.utcnow() - log.access_time).days <= 1])
            active_alarms = len([alarm for alarm in self.security_alarms
                               if alarm.zone_id == zone_id and not alarm.resolved_at])

            zone_status[zone_id] = {
                'name': zone.name,
                'type': zone.zone_type.value,
                'access_level': zone.access_level.value,
                'recent_access_count': recent_access,
                'active_alarms': active_alarms,
                'status': 'ALERT' if active_alarms > 0 else 'SECURE'
            }

        # Get access statistics
        total_access_attempts = sum(len(logs) for logs in self.access_logs.values())
        granted_access = sum(len([log for log in logs if log.access_result == 'granted'])
                           for logs in self.access_logs.values())
        denied_access = total_access_attempts - granted_access

        access_statistics = {
            'total_attempts': total_access_attempts,
            'granted': granted_access,
            'denied': denied_access,
            'success_rate': (granted_access / total_access_attempts * 100) if total_access_attempts > 0 else 100,
            'recent_denials': len([log for logs in self.access_logs.values() for log in logs
                                 if log.access_result == 'denied' and (datetime.utcnow() - log.access_time).hours <= 24])
        }

        # Get alarm summary
        alarm_summary = {
            'total_alarms': len(self.security_alarms),
            'active_alarms': len([a for a in self.security_alarms if not a.resolved_at]),
            'resolved_today': len([a for a in self.security_alarms
                                 if a.resolved_at and (datetime.utcnow() - a.resolved_at).days < 1]),
            'false_alarms': len([a for a in self.security_alarms if a.false_alarm]),
            'by_severity': {
                'critical': len([a for a in self.security_alarms if a.severity == AlarmSeverity.CRITICAL]),
                'high': len([a for a in self.security_alarms if a.severity == AlarmSeverity.HIGH]),
                'medium': len([a for a in self.security_alarms if a.severity == AlarmSeverity.MEDIUM]),
                'low': len([a for a in self.security_alarms if a.severity == AlarmSeverity.LOW])
            }
        }

        # Get environmental status
        environmental_status = self._get_environmental_status()

        # Get equipment inventory summary
        equipment_inventory = {
            'total_equipment': len(self.equipment_inventory),
            'by_type': {},
            'security_compliant': 0,
            'warranty_expiring': 0,
            'needs_maintenance': 0
        }

        for equipment in self.equipment_inventory.values():
            eq_type = equipment.equipment_type.value
            equipment_inventory['by_type'][eq_type] = equipment_inventory['by_type'].get(eq_type, 0) + 1

            # Check security compliance
            if self._is_equipment_security_compliant(equipment):
                equipment_inventory['security_compliant'] += 1

            # Check warranty
            if equipment.warranty_expiry and (equipment.warranty_expiry - datetime.utcnow()).days <= 30:
                equipment_inventory['warranty_expiring'] += 1

        # Get visitor and maintenance activity
        visitor_activity = {
            'active_visitors': len([v for v in self.visitor_access if not v.checked_out_at]),
            'total_today': len([v for v in self.visitor_access if (datetime.utcnow() - v.access_start).days < 1]),
            'escorted_visits': len([v for v in self.visitor_access if v.escort_required])
        }

        maintenance_activity = {
            'active_maintenance': len([m for m in self.maintenance_access if not m.actual_end]),
            'completed_today': len([m for m in self.maintenance_access
                                  if m.actual_end and (datetime.utcnow() - m.actual_end).days < 1]),
            'scheduled_this_week': len([m for m in self.maintenance_access
                                      if (m.scheduled_start - datetime.utcnow()).days <= 7])
        }

        # Get security incidents
        security_incidents = {
            'total_incidents': len(self.security_incidents),
            'open_incidents': len([i for i in self.security_incidents if i.resolution_status == 'open']),
            'resolved_today': len([i for i in self.security_incidents
                                 if i.resolved_at and (datetime.utcnow() - i.resolved_at).days < 1]),
            'by_severity': {
                'critical': len([i for i in self.security_incidents if i.severity == 'critical']),
                'high': len([i for i in self.security_incidents if i.severity == 'high']),
                'medium': len([i for i in self.security_incidents if i.severity == 'medium']),
                'low': len([i for i in self.security_incidents if i.severity == 'low'])
            }
        }

        # Generate recommendations
        recommendations = self._generate_security_recommendations(
            zone_status, access_statistics, alarm_summary, equipment_inventory
        )

        dashboard = PhysicalSecurityDashboard(
            id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            zone_status=zone_status,
            access_statistics=access_statistics,
            alarm_summary=alarm_summary,
            environmental_status=environmental_status,
            equipment_inventory=equipment_inventory,
            visitor_activity=visitor_activity,
            maintenance_activity=maintenance_activity,
            security_incidents=security_incidents,
            recommendations=recommendations
        )

        return {
            'dashboard_id': dashboard.id,
            'generated_at': dashboard.generated_at.isoformat(),
            'period': f"{dashboard.period_start.date()} to {dashboard.period_end.date()}",
            'zone_status': dashboard.zone_status,
            'access_statistics': dashboard.access_statistics,
            'alarm_summary': dashboard.alarm_summary,
            'environmental_status': dashboard.environmental_status,
            'equipment_inventory': dashboard.equipment_inventory,
            'visitor_activity': dashboard.visitor_activity,
            'maintenance_activity': dashboard.maintenance_activity,
            'security_incidents': dashboard.security_incidents,
            'recommendations': dashboard.recommendations
        }

    def _get_environmental_status(self) -> Dict[str, Any]:
        """Get environmental monitoring status"""
        recent_monitoring = [m for m in self.environmental_monitoring
                           if (datetime.utcnow() - m.measurement_time).hours <= 24]

        return {
            'total_readings': len(recent_monitoring),
            'alarms_triggered': len([m for m in recent_monitoring if m.alarm_triggered]),
            'temperature_avg': self._calculate_average_temperature(recent_monitoring),
            'humidity_avg': self._calculate_average_humidity(recent_monitoring),
            'zones_monitored': len(set(m.zone_id for m in recent_monitoring))
        }

    def _calculate_average_temperature(self, monitoring: List[EnvironmentalMonitoring]) -> Optional[float]:
        """Calculate average temperature"""
        temperatures = [m.temperature_celsius for m in monitoring if m.temperature_celsius is not None]
        return round(sum(temperatures) / len(temperatures), 1) if temperatures else None

    def _calculate_average_humidity(self, monitoring: List[EnvironmentalMonitoring]) -> Optional[float]:
        """Calculate average humidity"""
        humidities = [m.humidity_percent for m in monitoring if m.humidity_percent is not None]
        return round(sum(humidities) / len(humidities), 1) if humidities else None

    def _is_equipment_security_compliant(self, equipment: EquipmentInventory) -> bool:
        """Check if equipment meets security requirements"""
        # Check encryption requirements
        if equipment.equipment_type in [EquipmentType.SERVER, EquipmentType.STORAGE_SYSTEM, EquipmentType.MOBILE_DEVICE]:
            if not equipment.encryption_enabled:
                return False

        # Check remote wipe for mobile devices
        if equipment.equipment_type == EquipmentType.MOBILE_DEVICE:
            if not equipment.remote_wipe_capable:
                return False

        return True

    def _generate_security_recommendations(self, zones: Dict, access: Dict,
                                         alarms: Dict, equipment: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        # Zone security recommendations
        alert_zones = [zone_id for zone_id, status in zones.items() if status['status'] == 'ALERT']
        if alert_zones:
            recommendations.append(f"Address active alarms in zones: {', '.join(alert_zones)}")

        # Access control recommendations
        if access['success_rate'] < 95:
            recommendations.append("Review access control policies to reduce denial rates")

        if access['recent_denials'] > 10:
            recommendations.append("Investigate recent access denial patterns")

        # Alarm management recommendations
        if alarms['active_alarms'] > 5:
            recommendations.append("Reduce active alarm count through better maintenance")

        # Equipment security recommendations
        if equipment['security_compliant'] / equipment['total_equipment'] < 0.9:
            recommendations.append("Improve equipment security compliance")

        if equipment['warranty_expiring'] > 0:
            recommendations.append(f"Renew warranties for {equipment['warranty_expiring']} expiring equipment items")

        recommendations.append("Conduct regular physical security assessments and drills")

        return recommendations

    def check_physical_security_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 physical security compliance"""
        compliance_checks = {
            'secure_areas': self._check_secure_areas_compliance(),
            'equipment_security': self._check_equipment_security_compliance(),
            'environmental_security': self._check_environmental_security_compliance(),
            'access_control': self._check_physical_access_control_compliance(),
            'maintenance_security': self._check_maintenance_security_compliance()
        }

        overall_score = sum(compliance_checks.values()) / len(compliance_checks)

        issues = []
        if compliance_checks['secure_areas'] < 80:
            issues.append("Secure areas require improved protection measures")
        if compliance_checks['equipment_security'] < 85:
            issues.append("Equipment security controls need enhancement")
        if compliance_checks['access_control'] < 90:
            issues.append("Physical access controls require strengthening")

        return {
            'tenant_id': tenant_id,
            'compliance_score': round(overall_score, 1),
            'total_issues': len(issues),
            'issues': issues,
            'recommendations': self._generate_physical_security_recommendations(issues),
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.11 Physical and Environmental Security',
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_secure_areas_compliance(self) -> float:
        """Check secure areas compliance"""
        zones = list(self.security_zones.values())

        if not zones:
            return 0.0

        compliant_zones = 0
        for zone in zones:
            score = 100

            # Check surveillance
            if not zone.surveillance_cameras:
                score -= 20

            # Check alarm systems
            if not zone.alarm_systems:
                score -= 15

            # Check access controls
            if not zone.access_methods:
                score -= 25

            # Check environmental controls for critical zones
            if zone.zone_type in [SecurityZone.SERVER_ROOM, SecurityZone.DATA_CENTER]:
                if not zone.environmental_controls:
                    score -= 20

            compliant_zones += max(score, 0)

        return compliant_zones / len(zones)

    def _check_equipment_security_compliance(self) -> float:
        """Check equipment security compliance"""
        equipment = list(self.equipment_inventory.values())

        if not equipment:
            return 100.0

        compliant_equipment = 0
        for item in equipment:
            if self._is_equipment_security_compliant(item):
                compliant_equipment += 1

        return (compliant_equipment / len(equipment)) * 100

    def _check_environmental_security_compliance(self) -> float:
        """Check environmental security compliance"""
        # Check if critical zones have environmental monitoring
        critical_zones = [z for z in self.security_zones.values()
                         if z.zone_type in [SecurityZone.SERVER_ROOM, SecurityZone.DATA_CENTER]]

        if not critical_zones:
            return 100.0

        monitored_zones = 0
        for zone in critical_zones:
            # Check if zone has recent environmental monitoring
            recent_monitoring = len([m for m in self.environmental_monitoring
                                   if m.zone_id == zone.id and (datetime.utcnow() - m.measurement_time).hours <= 24])
            if recent_monitoring >= 12:  # At least every 2 hours
                monitored_zones += 1

        return (monitored_zones / len(critical_zones)) * 100

    def _check_physical_access_control_compliance(self) -> float:
        """Check physical access control compliance"""
        # Check access log completeness
        total_zones = len(self.security_zones)
        logged_zones = len([z for z in self.security_zones.keys() if z in self.access_logs])

        if total_zones == 0:
            return 100.0

        log_completeness = (logged_zones / total_zones) * 100

        # Check access denial rates
        total_access = sum(len(logs) for logs in self.access_logs.values())
        denied_access = sum(len([log for log in logs if log.access_result == 'denied'])
                          for logs in self.access_logs.values())

        denial_rate = (denied_access / total_access * 100) if total_access > 0 else 0

        # Lower score if denial rate is too high
        access_score = max(0, 100 - denial_rate)

        return (log_completeness + access_score) / 2

    def _check_maintenance_security_compliance(self) -> float:
        """Check maintenance security compliance"""
        maintenance = self.maintenance_access[-20:]  # Last 20 maintenance activities

        if not maintenance:
            return 100.0

        compliant_maintenance = 0
        for activity in maintenance:
            score = 100

            if not activity.supervisor_present:
                score -= 30

            if not activity.security_clearance_verified:
                score -= 20

            if not activity.post_work_verification:
                score -= 25

            compliant_maintenance += max(score, 0)

        return compliant_maintenance / len(maintenance)

    def _generate_physical_security_recommendations(self, issues: List[str]) -> List[str]:
        """Generate physical security compliance recommendations"""
        recommendations = []

        if any('secure areas' in issue.lower() for issue in issues):
            recommendations.append("Enhance secure area protections with surveillance, alarms, and access controls")

        if any('equipment security' in issue.lower() for issue in issues):
            recommendations.append("Implement comprehensive equipment security including encryption and tracking")

        if any('environmental security' in issue.lower() for issue in issues):
            recommendations.append("Deploy environmental monitoring and control systems for critical areas")

        if any('access control' in issue.lower() for issue in issues):
            recommendations.append("Strengthen physical access controls with multi-factor authentication and logging")

        if any('maintenance security' in issue.lower() for issue in issues):
            recommendations.append("Improve maintenance security procedures with supervision and verification")

        recommendations.append("Conduct regular physical security assessments and penetration testing")

        return recommendations