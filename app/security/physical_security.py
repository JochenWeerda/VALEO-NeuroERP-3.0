"""
ISO 27001 Physical Security System
Informationssicherheits-Managementsystem Physical Security

Dieses Modul implementiert die Physical Security gemäß ISO 27001 Annex A.11
für VALEO-NeuroERP mit Facility Access Control, Asset Protection und Environmental Security.
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
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highly_confidential"


class FacilityZone(Enum):
    """Facility security zones"""
    EXTERNAL = "external"
    PERIMETER = "perimeter"
    BUILDING_ENTRANCE = "building_entrance"
    OFFICE_AREAS = "office_areas"
    SERVER_ROOM = "server_room"
    DATA_CENTER = "data_center"
    SECURE_STORAGE = "secure_storage"


class AccessMethod(Enum):
    """Physical access methods"""
    KEYCARD = "keycard"
    BIOMETRIC = "biometric"
    PIN_CODE = "pin_code"
    KEY = "key"
    MOBILE_APP = "mobile_app"


@dataclass
class PhysicalAsset:
    """Physical asset representation"""
    id: str
    name: str
    asset_type: str  # server, workstation, storage_device, etc.
    location: str
    facility_zone: FacilityZone
    access_level: AccessLevel
    criticality: str  # low, medium, high, critical
    value: float  # monetary value
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    last_inventory_check: Optional[datetime] = None
    security_features: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None


@dataclass
class AccessEvent:
    """Physical access event"""
    id: str
    timestamp: datetime
    person_id: str
    asset_id: Optional[str]
    facility_zone: FacilityZone
    access_method: AccessMethod
    access_granted: bool
    reason: str
    location_details: Dict[str, Any]
    tenant_id: str = "system"


@dataclass
class SecurityIncident:
    """Physical security incident"""
    id: str
    timestamp: datetime
    incident_type: str
    severity: str
    location: str
    facility_zone: FacilityZone
    description: str
    reported_by: str
    affected_assets: List[str]
    response_actions: List[str]
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class EnvironmentalReading:
    """Environmental monitoring reading"""
    id: str
    timestamp: datetime
    location: str
    sensor_type: str  # temperature, humidity, smoke, water, etc.
    value: float
    unit: str
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    alert_triggered: bool = False


class ISO27001PhysicalSecurity:
    """
    ISO 27001 Physical Security Implementation
    Implements Annex A.11 - Physical and Environmental Security
    """

    def __init__(self, db_session, access_control_service=None, monitoring_service=None):
        self.db = db_session
        self.access_control = access_control_service
        self.monitoring = monitoring_service

        # Asset tracking
        self.physical_assets: Dict[str, PhysicalAsset] = {}

        # Access control
        self.access_permissions: Dict[str, Dict[str, Any]] = {}
        self.access_events: List[AccessEvent] = []

        # Security incidents
        self.security_incidents: List[SecurityIncident] = []

        # Environmental monitoring
        self.environmental_readings: List[EnvironmentalReading] = []

        # Security policies
        self.security_policies = self._initialize_security_policies()

        # Access levels and requirements
        self.access_requirements = self._initialize_access_requirements()

    def _initialize_security_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize physical security policies"""
        return {
            'access_control': {
                'least_privilege': True,
                'dual_authorization': True,  # for critical areas
                'time_based_access': True,
                'visitor_management': True,
                'access_logging': True
            },
            'asset_protection': {
                'asset_inventory': True,
                'asset_tagging': True,
                'secure_storage': True,
                'asset_movement_logging': True,
                'regular_inventory_checks': True
            },
            'environmental_security': {
                'temperature_monitoring': True,
                'humidity_control': True,
                'fire_suppression': True,
                'flood_protection': True,
                'power_backup': True
            },
            'physical_barriers': {
                'perimeter_fencing': True,
                'building_locks': True,
                'server_room_restrictions': True,
                'secure_cabling': True,
                'window_security': True
            }
        }

    def _initialize_access_requirements(self) -> Dict[FacilityZone, Dict[str, Any]]:
        """Initialize access requirements for different zones"""
        return {
            FacilityZone.EXTERNAL: {
                'access_level': AccessLevel.PUBLIC,
                'authentication_required': False,
                'logging_required': False,
                'supervision_required': False
            },
            FacilityZone.PERIMETER: {
                'access_level': AccessLevel.RESTRICTED,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': False
            },
            FacilityZone.BUILDING_ENTRANCE: {
                'access_level': AccessLevel.RESTRICTED,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': False
            },
            FacilityZone.OFFICE_AREAS: {
                'access_level': AccessLevel.CONFIDENTIAL,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': False
            },
            FacilityZone.SERVER_ROOM: {
                'access_level': AccessLevel.HIGHLY_CONFIDENTIAL,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': False,
                'dual_authorization': True,
                'time_restricted': True
            },
            FacilityZone.DATA_CENTER: {
                'access_level': AccessLevel.HIGHLY_CONFIDENTIAL,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': True,
                'dual_authorization': True,
                'time_restricted': True,
                'background_checks': True
            },
            FacilityZone.SECURE_STORAGE: {
                'access_level': AccessLevel.HIGHLY_CONFIDENTIAL,
                'authentication_required': True,
                'logging_required': True,
                'supervision_required': True,
                'dual_authorization': True,
                'time_restricted': True
            }
        }

    def register_physical_asset(self, asset_data: Dict[str, Any]) -> str:
        """
        Register a physical asset for security tracking
        Returns asset ID
        """
        asset_id = asset_data.get('id') or str(uuid.uuid4())

        asset = PhysicalAsset(
            id=asset_id,
            name=asset_data['name'],
            asset_type=asset_data['asset_type'],
            location=asset_data['location'],
            facility_zone=FacilityZone[asset_data['facility_zone'].upper()],
            access_level=AccessLevel[asset_data['access_level'].upper()],
            criticality=asset_data.get('criticality', 'medium'),
            value=asset_data.get('value', 0.0),
            serial_number=asset_data.get('serial_number'),
            purchase_date=asset_data.get('purchase_date'),
            security_features=asset_data.get('security_features', []),
            assigned_to=asset_data.get('assigned_to')
        )

        self.physical_assets[asset_id] = asset

        # Perform initial security assessment
        self._assess_asset_security(asset)

        logger.info(f"Physical asset registered: {asset.name} in {asset.facility_zone.value}")
        return asset_id

    def _assess_asset_security(self, asset: PhysicalAsset):
        """Assess security requirements for physical asset"""
        # Check if asset is in appropriate zone for its access level
        zone_requirements = self.access_requirements[asset.facility_zone]

        if asset.access_level.value > zone_requirements['access_level'].value:
            logger.warning(f"Asset {asset.name} has higher access level than zone {asset.facility_zone.value}")

        # Check security features
        required_features = []
        if asset.criticality in ['high', 'critical']:
            required_features.extend(['tamper_evident', 'secure_mounting'])

        if asset.value > 50000:  # High-value assets
            required_features.extend(['insurance_tracked', 'theft_protection'])

        missing_features = [f for f in required_features if f not in asset.security_features]
        if missing_features:
            logger.warning(f"Asset {asset.name} missing security features: {missing_features}")

    def grant_access_permission(self, person_id: str, zone: FacilityZone,
                              access_method: AccessMethod, validity_period: timedelta = None) -> str:
        """
        Grant physical access permission
        Returns permission ID
        """
        permission_id = str(uuid.uuid4())

        zone_requirements = self.access_requirements[zone]

        permission = {
            'id': permission_id,
            'person_id': person_id,
            'facility_zone': zone,
            'access_method': access_method,
            'granted_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + (validity_period or timedelta(days=365)),
            'is_active': True,
            'access_level': zone_requirements['access_level'],
            'restrictions': {
                'time_based': zone_requirements.get('time_restricted', False),
                'dual_auth_required': zone_requirements.get('dual_authorization', False),
                'supervision_required': zone_requirements.get('supervision_required', False)
            },
            'background_check_required': zone_requirements.get('background_checks', False)
        }

        self.access_permissions[permission_id] = permission

        logger.info(f"Access permission granted to {person_id} for {zone.value}")
        return permission_id

    def validate_physical_access(self, person_id: str, zone: FacilityZone,
                               access_method: AccessMethod, location_details: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Validate physical access attempt
        Returns: (access_granted, reason)
        """
        location_details = location_details or {}

        # Find active permissions for this person and zone
        active_permissions = [
            p for p in self.access_permissions.values()
            if p['person_id'] == person_id and
            p['facility_zone'] == zone and
            p['is_active'] and
            p['expires_at'] > datetime.utcnow()
        ]

        if not active_permissions:
            self._log_access_attempt(person_id, zone, access_method, False, "No active permission", location_details)
            return False, "Access denied: No active permission for this zone"

        permission = active_permissions[0]  # Use first valid permission

        # Check time-based restrictions
        if permission['restrictions']['time_based']:
            if not self._check_time_restrictions(person_id, zone):
                self._log_access_attempt(person_id, zone, access_method, False, "Time restriction violation", location_details)
                return False, "Access denied: Outside allowed hours"

        # Check dual authorization for critical areas
        if permission['restrictions']['dual_auth_required']:
            if not self._check_dual_authorization(person_id, zone, location_details):
                self._log_access_attempt(person_id, zone, access_method, False, "Dual authorization required", location_details)
                return False, "Access denied: Dual authorization required"

        # Check supervision requirements
        if permission['restrictions']['supervision_required']:
            if not self._check_supervision(person_id, zone, location_details):
                self._log_access_attempt(person_id, zone, access_method, False, "Supervision required", location_details)
                return False, "Access denied: Supervision required"

        # Check access method compatibility
        if not self._validate_access_method(access_method, permission):
            self._log_access_attempt(person_id, zone, access_method, False, "Invalid access method", location_details)
            return False, "Access denied: Invalid access method for this permission"

        # All checks passed
        self._log_access_attempt(person_id, zone, access_method, True, "Access granted", location_details)
        return True, "Access granted"

    def _check_time_restrictions(self, person_id: str, zone: FacilityZone) -> bool:
        """Check if access is within allowed time windows"""
        now = datetime.utcnow()
        current_hour = now.hour
        current_day = now.weekday()  # 0=Monday, 6=Sunday

        # Define time restrictions based on zone
        time_restrictions = {
            FacilityZone.SERVER_ROOM: {
                'allowed_hours': range(8, 18),  # Business hours
                'allowed_days': range(0, 5)  # Monday-Friday
            },
            FacilityZone.DATA_CENTER: {
                'allowed_hours': range(8, 18),
                'allowed_days': range(0, 5),
                'maintenance_window': True  # Allow maintenance access
            },
            FacilityZone.SECURE_STORAGE: {
                'allowed_hours': range(8, 18),
                'allowed_days': range(0, 5)
            }
        }

        restrictions = time_restrictions.get(zone)
        if not restrictions:
            return True  # No restrictions for this zone

        if current_hour not in restrictions['allowed_hours']:
            return False

        if current_day not in restrictions['allowed_days']:
            return False

        return True

    def _check_dual_authorization(self, person_id: str, zone: FacilityZone, location_details: Dict[str, Any]) -> bool:
        """Check dual authorization requirements"""
        # In production, this would check for secondary authorization
        # For now, simulate based on context
        secondary_auth = location_details.get('secondary_authorization', False)
        return secondary_auth

    def _check_supervision(self, person_id: str, zone: FacilityZone, location_details: Dict[str, Any]) -> bool:
        """Check supervision requirements"""
        supervisor_present = location_details.get('supervisor_present', False)
        return supervisor_present

    def _validate_access_method(self, access_method: AccessMethod, permission: Dict[str, Any]) -> bool:
        """Validate access method compatibility"""
        # Check if the access method is allowed for this permission
        allowed_methods = [AccessMethod.KEYCARD, AccessMethod.BIOMETRIC, AccessMethod.PIN_CODE]

        if permission['facility_zone'] in [FacilityZone.DATA_CENTER, FacilityZone.SECURE_STORAGE]:
            allowed_methods.append(AccessMethod.KEY)  # Physical keys allowed for critical areas

        return access_method in allowed_methods

    def _log_access_attempt(self, person_id: str, zone: FacilityZone, access_method: AccessMethod,
                          access_granted: bool, reason: str, location_details: Dict[str, Any]):
        """Log physical access attempt"""
        event = AccessEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            person_id=person_id,
            facility_zone=zone,
            access_method=access_method,
            access_granted=access_granted,
            reason=reason,
            location_details=location_details
        )

        self.access_events.append(event)

        if not access_granted:
            logger.warning(f"Access denied: {person_id} to {zone.value} - {reason}")
        else:
            logger.info(f"Access granted: {person_id} to {zone.value}")

    def report_security_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Report a physical security incident
        Returns incident ID
        """
        incident_id = str(uuid.uuid4())

        incident = SecurityIncident(
            id=incident_id,
            timestamp=datetime.utcnow(),
            incident_type=incident_data['incident_type'],
            severity=incident_data.get('severity', 'MEDIUM'),
            location=incident_data['location'],
            facility_zone=FacilityZone[incident_data['facility_zone'].upper()],
            description=incident_data['description'],
            reported_by=incident_data['reported_by'],
            affected_assets=incident_data.get('affected_assets', [])
        )

        self.security_incidents.append(incident)

        # Trigger immediate response
        self._trigger_incident_response(incident)

        logger.warning(f"Physical security incident reported: {incident.incident_type} at {incident.location}")
        return incident_id

    def _trigger_incident_response(self, incident: SecurityIncident):
        """Trigger response to security incident"""
        response_actions = []

        if incident.incident_type == 'unauthorized_access':
            response_actions.extend([
                "Secure the affected area",
                "Review access logs",
                "Update access permissions if necessary"
            ])
        elif incident.incident_type == 'theft':
            response_actions.extend([
                "Notify law enforcement",
                "Conduct inventory check",
                "Review security camera footage"
            ])
        elif incident.incident_type == 'environmental_hazard':
            response_actions.extend([
                "Evacuate affected area if necessary",
                "Contact emergency services",
                "Activate backup systems"
            ])

        incident.response_actions = response_actions

        # In production, this would trigger alerts and notifications
        logger.critical(f"Incident response triggered for {incident.incident_type}")

    def record_environmental_reading(self, sensor_data: Dict[str, Any]) -> str:
        """
        Record environmental monitoring reading
        Returns reading ID
        """
        reading_id = str(uuid.uuid4())

        reading = EnvironmentalReading(
            id=reading_id,
            timestamp=datetime.utcnow(),
            location=sensor_data['location'],
            sensor_type=sensor_data['sensor_type'],
            value=sensor_data['value'],
            unit=sensor_data['unit'],
            threshold_min=sensor_data.get('threshold_min'),
            threshold_max=sensor_data.get('threshold_max')
        )

        # Check thresholds and trigger alerts
        if reading.threshold_min and reading.value < reading.threshold_min:
            reading.alert_triggered = True
            self._trigger_environmental_alert(reading, "below_minimum")
        elif reading.threshold_max and reading.value > reading.threshold_max:
            reading.alert_triggered = True
            self._trigger_environmental_alert(reading, "above_maximum")

        self.environmental_readings.append(reading)

        if reading.alert_triggered:
            logger.warning(f"Environmental alert: {reading.sensor_type} at {reading.location} = {reading.value} {reading.unit}")

        return reading_id

    def _trigger_environmental_alert(self, reading: EnvironmentalReading, alert_type: str):
        """Trigger environmental monitoring alert"""
        alert_message = f"Environmental threshold violation: {reading.sensor_type} {alert_type} at {reading.location}"

        # In production, this would trigger notifications and automated responses
        logger.warning(alert_message)

    def perform_inventory_check(self, asset_id: str, checked_by: str, location_verified: bool = True) -> bool:
        """
        Perform physical inventory check
        Returns success status
        """
        if asset_id not in self.physical_assets:
            return False

        asset = self.physical_assets[asset_id]
        asset.last_inventory_check = datetime.utcnow()

        # In production, this would update inventory status and check for discrepancies
        logger.info(f"Inventory check performed for asset {asset.name} by {checked_by}")

        return True

    def get_physical_security_status(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive physical security status"""
        # Filter data by tenant
        tenant_assets = [a for a in self.physical_assets.values() if a.tenant_id == tenant_id]
        tenant_events = [e for e in self.access_events if e.tenant_id == tenant_id]
        tenant_incidents = [i for i in self.security_incidents if i.tenant_id == tenant_id]

        # Calculate metrics
        asset_compliance = self._calculate_asset_compliance(tenant_assets)
        access_patterns = self._analyze_access_patterns(tenant_events)
        incident_summary = self._summarize_security_incidents(tenant_incidents)
        environmental_status = self._check_environmental_status()

        # Calculate overall risk score
        risk_score = self._calculate_physical_risk_score(tenant_assets, tenant_events, tenant_incidents)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'asset_compliance': asset_compliance,
            'access_patterns': access_patterns,
            'incident_summary': incident_summary,
            'environmental_status': environmental_status,
            'risk_score': risk_score,
            'active_alerts': self._get_active_security_alerts(tenant_id)
        }

    def _calculate_asset_compliance(self, assets: List[PhysicalAsset]) -> Dict[str, Any]:
        """Calculate asset compliance metrics"""
        if not assets:
            return {'total_assets': 0, 'compliant_assets': 0, 'compliance_rate': 0}

        compliant = 0
        overdue_inventory = 0

        for asset in assets:
            # Check inventory compliance (quarterly checks)
            if asset.last_inventory_check:
                days_since_check = (datetime.utcnow() - asset.last_inventory_check).days
                if days_since_check > 90:  # 90 days = quarterly
                    overdue_inventory += 1
                else:
                    compliant += 1
            else:
                overdue_inventory += 1

        compliance_rate = (compliant / len(assets)) * 100 if assets else 0

        return {
            'total_assets': len(assets),
            'compliant_assets': compliant,
            'overdue_inventory': overdue_inventory,
            'compliance_rate': round(compliance_rate, 1)
        }

    def _analyze_access_patterns(self, events: List[AccessEvent]) -> Dict[str, Any]:
        """Analyze physical access patterns"""
        if not events:
            return {'total_events': 0, 'access_denied_rate': 0, 'peak_hours': []}

        total_events = len(events)
        denied_events = sum(1 for e in events if not e.access_granted)
        denied_rate = (denied_events / total_events) * 100 if total_events > 0 else 0

        # Analyze peak access hours
        hour_counts = {}
        for event in events:
            hour = event.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [hour for hour, count in peak_hours]

        return {
            'total_events': total_events,
            'access_denied_rate': round(denied_rate, 1),
            'peak_hours': peak_hours
        }

    def _summarize_security_incidents(self, incidents: List[SecurityIncident]) -> Dict[str, Any]:
        """Summarize security incidents"""
        if not incidents:
            return {'total_incidents': 0, 'unresolved_incidents': 0, 'avg_resolution_time': 0}

        total_incidents = len(incidents)
        unresolved = sum(1 for i in incidents if not i.resolved_at)

        # Calculate average resolution time
        resolved_incidents = [i for i in incidents if i.resolved_at]
        if resolved_incidents:
            resolution_times = [
                (i.resolved_at - i.timestamp).total_seconds() / 3600  # hours
                for i in resolved_incidents
            ]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        else:
            avg_resolution_time = 0

        return {
            'total_incidents': total_incidents,
            'unresolved_incidents': unresolved,
            'avg_resolution_time': round(avg_resolution_time, 1)
        }

    def _check_environmental_status(self) -> Dict[str, Any]:
        """Check environmental monitoring status"""
        recent_readings = [r for r in self.environmental_readings[-100:]]  # Last 100 readings

        if not recent_readings:
            return {'status': 'NO_DATA', 'alerts': 0, 'sensors_active': 0}

        alerts = sum(1 for r in recent_readings if r.alert_triggered)
        sensors_active = len(set(r.location + r.sensor_type for r in recent_readings))

        status = 'NORMAL'
        if alerts > 0:
            status = 'WARNING' if alerts < 5 else 'CRITICAL'

        return {
            'status': status,
            'alerts': alerts,
            'sensors_active': sensors_active,
            'last_reading': recent_readings[-1].timestamp.isoformat() if recent_readings else None
        }

    def _calculate_physical_risk_score(self, assets: List[PhysicalAsset],
                                     events: List[AccessEvent], incidents: List[SecurityIncident]) -> int:
        """Calculate overall physical security risk score (0-100)"""
        risk_score = 0

        # Asset protection factor
        unprotected_high_value = sum(1 for a in assets if a.criticality in ['high', 'critical'] and len(a.security_features) < 2)
        risk_score += min(unprotected_high_value * 10, 30)

        # Access control factor
        denied_rate = sum(1 for e in events if not e.access_granted) / len(events) if events else 0
        if denied_rate > 0.1:  # More than 10% denied
            risk_score += 10

        # Incident factor
        unresolved_incidents = sum(1 for i in incidents if not i.resolved_at)
        risk_score += min(unresolved_incidents * 5, 20)

        # Environmental factor
        recent_alerts = sum(1 for r in self.environmental_readings[-50:] if r.alert_triggered)
        risk_score += min(recent_alerts * 2, 20)

        return max(0, min(risk_score, 100))

    def _get_active_security_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active physical security alerts"""
        alerts = []

        # Check for overdue inventory
        overdue_assets = [
            a for a in self.physical_assets.values()
            if a.tenant_id == tenant_id and a.last_inventory_check and
            (datetime.utcnow() - a.last_inventory_check).days > 90
        ]

        for asset in overdue_assets:
            alerts.append({
                'type': 'overdue_inventory',
                'severity': 'MEDIUM',
                'message': f"Inventory check overdue for {asset.name}",
                'asset_id': asset.id,
                'days_overdue': (datetime.utcnow() - asset.last_inventory_check).days
            })

        # Check for unresolved incidents
        unresolved_incidents = [
            i for i in self.security_incidents
            if i.tenant_id == tenant_id and not i.resolved_at
        ]

        for incident in unresolved_incidents:
            alerts.append({
                'type': 'unresolved_incident',
                'severity': 'HIGH',
                'message': f"Unresolved security incident: {incident.incident_type}",
                'incident_id': incident.id,
                'days_open': (datetime.utcnow() - incident.timestamp).days
            })

        return alerts

    def check_physical_security_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 physical security compliance"""
        issues = []

        # Check access control compliance
        access_issues = self._check_access_control_compliance()
        issues.extend(access_issues)

        # Check asset protection compliance
        asset_issues = self._check_asset_protection_compliance()
        issues.extend(asset_issues)

        # Check environmental security compliance
        environmental_issues = self._check_environmental_security_compliance()
        issues.extend(environmental_issues)

        # Check physical barriers compliance
        barrier_issues = self._check_physical_barriers_compliance()
        issues.extend(barrier_issues)

        compliance_score = max(0, 100 - (len(issues) * 3))  # 3 points per issue

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_score,
            'total_issues': len(issues),
            'issues': issues,
            'iso_control': 'A.11',
            'recommendations': self._generate_physical_security_recommendations(issues),
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_access_control_compliance(self) -> List[str]:
        """Check access control compliance"""
        issues = []

        # Check for zones without proper access control
        for zone in FacilityZone:
            if zone == FacilityZone.EXTERNAL:
                continue  # External areas don't need access control

            zone_permissions = [p for p in self.access_permissions.values() if p['facility_zone'] == zone]
            if not zone_permissions:
                issues.append(f"No access permissions defined for {zone.value}")

        # Check for expired permissions
        expired_permissions = [
            p for p in self.access_permissions.values()
            if p['is_active'] and p['expires_at'] < datetime.utcnow()
        ]

        if expired_permissions:
            issues.append(f"{len(expired_permissions)} access permissions have expired")

        return issues

    def _check_asset_protection_compliance(self) -> List[str]:
        """Check asset protection compliance"""
        issues = []

        # Check for untagged assets
        untagged_assets = [a for a in self.physical_assets.values() if not a.serial_number]
        if untagged_assets:
            issues.append(f"{len(untagged_assets)} assets are not properly tagged")

        # Check for overdue inventory
        overdue_inventory = [
            a for a in self.physical_assets.values()
            if not a.last_inventory_check or (datetime.utcnow() - a.last_inventory_check).days > 90
        ]

        if overdue_inventory:
            issues.append(f"{len(overdue_inventory)} assets have overdue inventory checks")

        return issues

    def _check_environmental_security_compliance(self) -> List[str]:
        """Check environmental security compliance"""
        issues = []

        # Check for missing environmental monitoring
        monitored_locations = set(r.location for r in self.environmental_readings)
        asset_locations = set(a.location for a in self.physical_assets.values())

        unmonitored_locations = asset_locations - monitored_locations
        if unmonitored_locations:
            issues.append(f"{len(unmonitored_locations)} locations lack environmental monitoring")

        # Check for recent alerts
        recent_alerts = [r for r in self.environmental_readings[-24:] if r.alert_triggered]  # Last 24 hours
        if recent_alerts:
            issues.append(f"{len(recent_alerts)} environmental alerts in the last 24 hours")

        return issues

    def _check_physical_barriers_compliance(self) -> List[str]:
        """Check physical barriers compliance"""
        issues = []

        # This would check for physical security measures in production
        # For now, return placeholder checks
        issues.append("Physical barrier assessment requires on-site inspection")

        return issues

    def _generate_physical_security_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        if any('access' in issue.lower() for issue in issues):
            recommendations.append("Implement comprehensive access control system with proper permissions")

        if any('inventory' in issue.lower() or 'tag' in issue.lower() for issue in issues):
            recommendations.append("Establish regular asset inventory procedures and proper asset tagging")

        if any('environmental' in issue.lower() for issue in issues):
            recommendations.append("Deploy environmental monitoring systems for all critical areas")

        if any('barrier' in issue.lower() for issue in issues):
            recommendations.append("Conduct physical security assessment and implement necessary barriers")

        if not recommendations:
            recommendations.append("Maintain current physical security measures and conduct regular reviews")

        return recommendations