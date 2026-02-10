"""
ISO 27001 Communications Security Management
Information Security Communications Framework

Dieses Modul implementiert das Communications Security Management Framework
gemäß ISO 27001 Annex A.13 für VALEO-NeuroERP mit Network Security, Information Transfer und Cryptography.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class NetworkType(Enum):
    """Network classification types"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    GUEST = "guest"
    PUBLIC = "public"
    SECURE = "secure"
    CRITICAL = "critical"


class EncryptionAlgorithm(Enum):
    """Encryption algorithm types"""
    AES_256 = "aes_256"
    AES_128 = "aes_128"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"
    ECC_P384 = "ecc_p384"
    CHACHA20 = "chacha20"


class ProtocolSecurity(Enum):
    """Protocol security levels"""
    PLAIN = "plain"
    TLS_1_2 = "tls_1_2"
    TLS_1_3 = "tls_1_3"
    QUIC = "quic"
    DTLS = "dtls"


class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_RESTRICTED = "highly_restricted"


class TransferMethod(Enum):
    """Information transfer methods"""
    EMAIL = "email"
    FILE_TRANSFER = "file_transfer"
    API = "api"
    DATABASE = "database"
    PHYSICAL_MEDIA = "physical_media"
    CLOUD_STORAGE = "cloud_storage"
    REMOTE_ACCESS = "remote_access"


class SecurityControl(Enum):
    """Security controls for communications"""
    ENCRYPTION = "encryption"
    ACCESS_CONTROL = "access_control"
    INTEGRITY_CHECK = "integrity_check"
    NON_REPUDIATION = "non_repudiation"
    ANTI_MALWARE = "anti_malware"
    FIREWALL = "firewall"
    IDS_IPS = "ids_ips"
    VPN = "vpn"
    MULTI_FACTOR = "multi_factor"


@dataclass
class NetworkSegment:
    """Network segment definition"""
    id: str
    name: str
    network_type: NetworkType
    ip_range: str
    subnet_mask: str
    gateway: str
    dns_servers: List[str] = field(default_factory=list)
    security_controls: List[SecurityControl] = field(default_factory=list)
    allowed_protocols: List[str] = field(default_factory=list)
    firewall_rules: List[Dict[str, Any]] = field(default_factory=list)
    monitoring_enabled: bool = True
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EncryptionKey:
    """Encryption key management"""
    id: str
    name: str
    algorithm: EncryptionAlgorithm
    key_size: int
    purpose: str  # encryption, signing, key_exchange
    owner: str
    expiry_date: datetime
    rotation_schedule: str  # monthly, quarterly, annually
    status: str = "active"  # active, expired, revoked
    key_material: Optional[str] = None  # Not stored in production
    fingerprint: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_rotated: Optional[datetime] = None


@dataclass
class SecureChannel:
    """Secure communication channel"""
    id: str
    name: str
    source_system: str
    destination_system: str
    protocol: ProtocolSecurity
    encryption: EncryptionAlgorithm
    authentication_method: str
    data_classification: DataClassification
    transfer_method: TransferMethod
    security_controls: List[SecurityControl] = field(default_factory=list)
    bandwidth_limit: Optional[int] = None  # Mbps
    session_timeout: int = 3600  # seconds
    monitoring_enabled: bool = True
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DataTransfer:
    """Data transfer record"""
    id: str
    transfer_method: TransferMethod
    source_location: str
    destination_location: str
    data_classification: DataClassification
    data_size_bytes: int
    encryption_used: bool
    integrity_verified: bool
    transfer_start: datetime
    transfer_end: Optional[datetime] = None
    success: bool = False
    error_message: str = ""
    checksum: str = ""
    authorized_by: str = ""
    compliance_verified: bool = False


@dataclass
class NetworkTraffic:
    """Network traffic monitoring"""
    id: str
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    session_duration: int  # seconds
    application: str
    user_id: Optional[str] = None
    anomaly_detected: bool = False
    anomaly_score: float = 0.0
    blocked: bool = False
    block_reason: str = ""


@dataclass
class SecurityGateway:
    """Security gateway configuration"""
    id: str
    name: str
    gateway_type: str  # firewall, proxy, vpn, load_balancer
    ip_address: str
    ports: List[int] = field(default_factory=list)
    security_policies: List[Dict[str, Any]] = field(default_factory=list)
    encryption_policies: List[Dict[str, Any]] = field(default_factory=list)
    monitoring_rules: List[Dict[str, Any]] = field(default_factory=list)
    high_availability: bool = False
    failover_gateway: Optional[str] = None
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"


@dataclass
class CommunicationsAudit:
    """Communications security audit"""
    id: str
    audit_type: str  # network, encryption, transfer, compliance
    scope: str
    start_date: datetime
    end_date: Optional[datetime] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    auditor: str = ""
    status: str = "in_progress"  # in_progress, completed, failed


@dataclass
class CommunicationsDashboard:
    """Communications security dashboard"""
    id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    network_status: Dict[str, Any] = field(default_factory=dict)
    encryption_status: Dict[str, Any] = field(default_factory=dict)
    transfer_metrics: Dict[str, Any] = field(default_factory=dict)
    security_events: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class ISO27001CommunicationsSecurity:
    """
    ISO 27001 Communications Security Management
    Implements Annex A.13 - Communications Security
    """

    def __init__(self, db_session, network_monitor=None, encryption_service=None):
        self.db = db_session
        self.network_monitor = network_monitor
        self.encryption_svc = encryption_service

        # Communications security components
        self.network_segments: Dict[str, NetworkSegment] = {}
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.secure_channels: Dict[str, SecureChannel] = {}
        self.data_transfers: List[DataTransfer] = {}
        self.network_traffic: List[NetworkTraffic] = {}
        self.security_gateways: Dict[str, SecurityGateway] = {}
        self.communications_audits: List[CommunicationsAudit] = {}

        # Security configuration
        self.security_config = self._initialize_security_config()

        # Default network segments
        self._initialize_default_networks()

    def _initialize_security_config(self) -> Dict[str, Any]:
        """Initialize communications security configuration"""
        return {
            'network_security': {
                'segmentation_required': True,
                'zero_trust_enabled': True,
                'micro_segmentation': True,
                'traffic_encryption': 'tls_1_3',
                'monitoring_interval': 60,  # seconds
                'anomaly_detection': True
            },
            'encryption_policy': {
                'minimum_algorithm': 'aes_256',
                'key_rotation_period': 365,  # days
                'perfect_forward_secrecy': True,
                'quantum_resistant': False,  # Future requirement
                'certificate_validation': 'strict'
            },
            'data_transfer': {
                'classification_required': True,
                'encryption_mandatory': True,
                'integrity_checking': True,
                'audit_logging': True,
                'size_limits': {'confidential': 100 * 1024 * 1024, 'restricted': 10 * 1024 * 1024}  # bytes
            },
            'remote_access': {
                'vpn_required': True,
                'multi_factor_required': True,
                'session_recording': True,
                'time_restrictions': True,
                'geographic_restrictions': False
            }
        }

    def _initialize_default_networks(self):
        """Initialize default network segments"""
        default_segments = [
            {
                'id': 'corporate_lan',
                'name': 'Corporate LAN',
                'network_type': NetworkType.INTERNAL,
                'ip_range': '192.168.1.0/24',
                'subnet_mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns_servers': ['192.168.1.10', '8.8.8.8'],
                'security_controls': [
                    SecurityControl.FIREWALL,
                    SecurityControl.IDS_IPS,
                    SecurityControl.ENCRYPTION
                ],
                'allowed_protocols': ['https', 'ssh', 'rdp']
            },
            {
                'id': 'dmz',
                'name': 'DMZ Network',
                'network_type': NetworkType.EXTERNAL,
                'ip_range': '192.168.100.0/24',
                'subnet_mask': '255.255.255.0',
                'gateway': '192.168.100.1',
                'dns_servers': ['8.8.8.8', '1.1.1.1'],
                'security_controls': [
                    SecurityControl.FIREWALL,
                    SecurityControl.IDS_IPS,
                    SecurityControl.ANTI_MALWARE
                ],
                'allowed_protocols': ['https', 'smtp', 'dns']
            },
            {
                'id': 'server_network',
                'name': 'Server Network',
                'network_type': NetworkType.CRITICAL,
                'ip_range': '10.0.1.0/24',
                'subnet_mask': '255.255.255.0',
                'gateway': '10.0.1.1',
                'dns_servers': ['10.0.1.10'],
                'security_controls': [
                    SecurityControl.FIREWALL,
                    SecurityControl.IDS_IPS,
                    SecurityControl.ENCRYPTION,
                    SecurityControl.ACCESS_CONTROL
                ],
                'allowed_protocols': ['https', 'ssh', 'database']
            }
        ]

        for segment_data in default_segments:
            segment = NetworkSegment(**segment_data)
            self.network_segments[segment.id] = segment

    def create_network_segment(self, segment_data: Dict[str, Any]) -> str:
        """
        Create a new network segment
        Returns segment ID
        """
        segment_id = str(uuid.uuid4())

        segment = NetworkSegment(
            id=segment_id,
            name=segment_data['name'],
            network_type=NetworkType[segment_data['network_type'].upper()],
            ip_range=segment_data['ip_range'],
            subnet_mask=segment_data['subnet_mask'],
            gateway=segment_data['gateway'],
            dns_servers=segment_data.get('dns_servers', []),
            security_controls=[SecurityControl[control.upper()] for control in segment_data.get('security_controls', [])],
            allowed_protocols=segment_data.get('allowed_protocols', []),
            firewall_rules=segment_data.get('firewall_rules', [])
        )

        self.network_segments[segment_id] = segment

        # Validate network security
        self._validate_network_security(segment)

        logger.info(f"Network segment created: {segment.name} ({segment.network_type.value})")
        return segment_id

    def _validate_network_security(self, segment: NetworkSegment):
        """Validate network segment security configuration"""
        issues = []

        # Check security controls based on network type
        if segment.network_type in [NetworkType.CRITICAL, NetworkType.SECURE]:
            required_controls = [SecurityControl.FIREWALL, SecurityControl.ENCRYPTION, SecurityControl.ACCESS_CONTROL]
            missing_controls = [control for control in required_controls if control not in segment.security_controls]
            if missing_controls:
                issues.append(f"Missing required security controls: {missing_controls}")

        if segment.network_type == NetworkType.EXTERNAL:
            if SecurityControl.ANTI_MALWARE not in segment.security_controls:
                issues.append("External networks require anti-malware protection")

        if issues:
            logger.warning(f"Network security validation issues for {segment.name}: {issues}")

    def generate_encryption_key(self, key_data: Dict[str, Any]) -> str:
        """
        Generate a new encryption key
        Returns key ID
        """
        key_id = str(uuid.uuid4())

        # Calculate expiry based on rotation schedule
        rotation_days = {
            'monthly': 30,
            'quarterly': 90,
            'annually': 365
        }.get(key_data['rotation_schedule'], 365)

        expiry_date = datetime.utcnow() + timedelta(days=rotation_days)

        key = EncryptionKey(
            id=key_id,
            name=key_data['name'],
            algorithm=EncryptionAlgorithm[key_data['algorithm'].upper()],
            key_size=key_data['key_size'],
            purpose=key_data['purpose'],
            owner=key_data['owner'],
            expiry_date=expiry_date,
            rotation_schedule=key_data['rotation_schedule'],
            fingerprint=key_data.get('fingerprint', '')
        )

        self.encryption_keys[key_id] = key

        # Schedule key rotation
        self._schedule_key_rotation(key_id)

        logger.info(f"Encryption key generated: {key.name} ({key.algorithm.value})")
        return key_id

    def _schedule_key_rotation(self, key_id: str):
        """Schedule key rotation"""
        key = self.encryption_keys[key_id]
        rotation_days = {
            'monthly': 30,
            'quarterly': 90,
            'annually': 365
        }.get(key.rotation_schedule, 365)

        # In production, this would create a scheduled task
        logger.info(f"Key rotation scheduled for {key.name} in {rotation_days} days")

    def establish_secure_channel(self, channel_data: Dict[str, Any]) -> str:
        """
        Establish a secure communication channel
        Returns channel ID
        """
        channel_id = str(uuid.uuid4())

        channel = SecureChannel(
            id=channel_id,
            name=channel_data['name'],
            source_system=channel_data['source_system'],
            destination_system=channel_data['destination_system'],
            protocol=ProtocolSecurity[channel_data['protocol'].upper()],
            encryption=EncryptionAlgorithm[channel_data['encryption'].upper()],
            authentication_method=channel_data['authentication_method'],
            data_classification=DataClassification[channel_data['data_classification'].upper()],
            transfer_method=TransferMethod[channel_data['transfer_method'].upper()],
            security_controls=[SecurityControl[control.upper()] for control in channel_data.get('security_controls', [])],
            bandwidth_limit=channel_data.get('bandwidth_limit'),
            session_timeout=channel_data.get('session_timeout', 3600)
        )

        self.secure_channels[channel_id] = channel

        # Validate channel security
        self._validate_channel_security(channel)

        logger.info(f"Secure channel established: {channel.name} ({channel.protocol.value})")
        return channel_id

    def _validate_channel_security(self, channel: SecureChannel):
        """Validate secure channel configuration"""
        issues = []

        # Check protocol security
        if channel.protocol == ProtocolSecurity.PLAIN:
            if channel.data_classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
                issues.append("Plain protocols not allowed for sensitive data")

        # Check encryption strength
        if channel.data_classification in [DataClassification.RESTRICTED, DataClassification.HIGHLY_RESTRICTED]:
            if channel.encryption not in [EncryptionAlgorithm.AES_256, EncryptionAlgorithm.RSA_4096]:
                issues.append("Insufficient encryption for highly sensitive data")

        # Check security controls
        required_controls = [SecurityControl.ENCRYPTION, SecurityControl.INTEGRITY_CHECK]
        if channel.data_classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            required_controls.append(SecurityControl.NON_REPUDIATION)

        missing_controls = [control for control in required_controls if control not in channel.security_controls]
        if missing_controls:
            issues.append(f"Missing required security controls: {missing_controls}")

        if issues:
            logger.warning(f"Channel security validation issues for {channel.name}: {issues}")

    def initiate_data_transfer(self, transfer_data: Dict[str, Any]) -> str:
        """
        Initiate a secure data transfer
        Returns transfer ID
        """
        transfer_id = str(uuid.uuid4())

        transfer = DataTransfer(
            id=transfer_id,
            transfer_method=TransferMethod[transfer_data['transfer_method'].upper()],
            source_location=transfer_data['source_location'],
            destination_location=transfer_data['destination_location'],
            data_classification=DataClassification[transfer_data['data_classification'].upper()],
            data_size_bytes=transfer_data['data_size_bytes'],
            encryption_used=transfer_data.get('encryption_used', True),
            integrity_verified=transfer_data.get('integrity_verified', False),
            transfer_start=datetime.utcnow(),
            checksum=transfer_data.get('checksum', ''),
            authorized_by=transfer_data['authorized_by']
        )

        self.data_transfers.append(transfer)

        # Validate transfer compliance
        self._validate_transfer_compliance(transfer)

        logger.info(f"Data transfer initiated: {transfer.transfer_method.value} ({transfer.data_size_bytes} bytes)")
        return transfer_id

    def _validate_transfer_compliance(self, transfer: DataTransfer):
        """Validate data transfer compliance"""
        issues = []

        # Check size limits
        size_limits = self.security_config['data_transfer']['size_limits']
        max_size = size_limits.get(transfer.data_classification.value)
        if max_size and transfer.data_size_bytes > max_size:
            issues.append(f"Data size exceeds limit for {transfer.data_classification.value} classification")

        # Check encryption requirements
        if not transfer.encryption_used and transfer.data_classification != DataClassification.PUBLIC:
            issues.append("Encryption required for non-public data")

        # Check authorization
        if not transfer.authorized_by:
            issues.append("Transfer authorization required")

        if issues:
            logger.warning(f"Transfer compliance issues: {issues}")

    def complete_data_transfer(self, transfer_id: str, completion_data: Dict[str, Any]) -> bool:
        """
        Complete a data transfer
        """
        transfer = None
        for t in self.data_transfers:
            if t.id == transfer_id:
                transfer = t
                break

        if not transfer:
            return False

        transfer.transfer_end = datetime.utcnow()
        transfer.success = completion_data.get('success', True)
        transfer.error_message = completion_data.get('error_message', '')
        transfer.compliance_verified = completion_data.get('compliance_verified', False)

        # Calculate transfer duration
        if transfer.transfer_end and transfer.transfer_start:
            duration = transfer.transfer_end - transfer.transfer_start
            logger.info(f"Data transfer completed: {transfer_id} in {duration}")

        return True

    def monitor_network_traffic(self, traffic_data: Dict[str, Any]) -> str:
        """
        Record network traffic for monitoring
        Returns traffic record ID
        """
        traffic_id = str(uuid.uuid4())

        traffic = NetworkTraffic(
            id=traffic_id,
            timestamp=datetime.utcnow(),
            source_ip=traffic_data['source_ip'],
            destination_ip=traffic_data['destination_ip'],
            source_port=traffic_data['source_port'],
            destination_port=traffic_data['destination_port'],
            protocol=traffic_data['protocol'],
            bytes_sent=traffic_data['bytes_sent'],
            bytes_received=traffic_data['bytes_received'],
            packets_sent=traffic_data['packets_sent'],
            packets_received=traffic_data['packets_received'],
            session_duration=traffic_data['session_duration'],
            application=traffic_data['application'],
            user_id=traffic_data.get('user_id'),
            anomaly_detected=traffic_data.get('anomaly_detected', False),
            anomaly_score=traffic_data.get('anomaly_score', 0.0),
            blocked=traffic_data.get('blocked', False),
            block_reason=traffic_data.get('block_reason', '')
        )

        self.network_traffic.append(traffic)

        # Check for anomalies
        if traffic.anomaly_detected:
            self._handle_traffic_anomaly(traffic)

        return traffic_id

    def _handle_traffic_anomaly(self, traffic: NetworkTraffic):
        """Handle detected traffic anomaly"""
        logger.warning(f"Network traffic anomaly detected: {traffic.source_ip} -> {traffic.destination_ip} "
                      f"(Score: {traffic.anomaly_score})")

        # In production, this would trigger automated responses
        if traffic.anomaly_score > 0.8:
            # High anomaly - potential security incident
            logger.error(f"High anomaly score detected - potential security incident")

    def configure_security_gateway(self, gateway_data: Dict[str, Any]) -> str:
        """
        Configure a security gateway
        Returns gateway ID
        """
        gateway_id = str(uuid.uuid4())

        gateway = SecurityGateway(
            id=gateway_id,
            name=gateway_data['name'],
            gateway_type=gateway_data['gateway_type'],
            ip_address=gateway_data['ip_address'],
            ports=gateway_data.get('ports', []),
            security_policies=gateway_data.get('security_policies', []),
            encryption_policies=gateway_data.get('encryption_policies', []),
            monitoring_rules=gateway_data.get('monitoring_rules', []),
            high_availability=gateway_data.get('high_availability', False),
            failover_gateway=gateway_data.get('failover_gateway')
        )

        self.security_gateways[gateway_id] = gateway

        logger.info(f"Security gateway configured: {gateway.name} ({gateway.gateway_type})")
        return gateway_id

    def perform_communications_audit(self, audit_data: Dict[str, Any]) -> str:
        """
        Perform communications security audit
        Returns audit ID
        """
        audit_id = str(uuid.uuid4())

        audit = CommunicationsAudit(
            id=audit_id,
            audit_type=audit_data['audit_type'],
            scope=audit_data['scope'],
            start_date=datetime.utcnow(),
            auditor=audit_data['auditor']
        )

        self.communications_audits.append(audit)

        # Execute audit based on type
        if audit.audit_type == 'network':
            findings = self._audit_network_security()
        elif audit.audit_type == 'encryption':
            findings = self._audit_encryption_compliance()
        elif audit.audit_type == 'transfer':
            findings = self._audit_data_transfer_compliance()
        else:
            findings = []

        audit.findings = findings
        audit.recommendations = self._generate_audit_recommendations(findings)
        audit.compliance_score = self._calculate_audit_compliance_score(findings)
        audit.end_date = datetime.utcnow()
        audit.status = 'completed'

        logger.info(f"Communications audit completed: {audit.audit_type} (Score: {audit.compliance_score}%)")
        return audit_id

    def _audit_network_security(self) -> List[Dict[str, Any]]:
        """Audit network security configuration"""
        findings = []

        for segment in self.network_segments.values():
            # Check firewall rules
            if not segment.firewall_rules:
                findings.append({
                    'severity': 'high',
                    'category': 'network_security',
                    'finding': f'No firewall rules configured for segment {segment.name}',
                    'impact': 'Unauthorized network access possible'
                })

            # Check security controls
            if segment.network_type == NetworkType.CRITICAL:
                required_controls = [SecurityControl.FIREWALL, SecurityControl.ENCRYPTION]
                missing = [c for c in required_controls if c not in segment.security_controls]
                if missing:
                    findings.append({
                        'severity': 'critical',
                        'category': 'network_security',
                        'finding': f'Missing critical security controls in {segment.name}: {missing}',
                        'impact': 'Critical systems unprotected'
                    })

        return findings

    def _audit_encryption_compliance(self) -> List[Dict[str, Any]]:
        """Audit encryption compliance"""
        findings = []

        # Check key expiry
        expired_keys = [k for k in self.encryption_keys.values()
                       if k.expiry_date < datetime.utcnow() and k.status == 'active']
        if expired_keys:
            findings.append({
                'severity': 'high',
                'category': 'encryption',
                'finding': f'{len(expired_keys)} encryption keys have expired',
                'impact': 'Data protection compromised'
            })

        # Check algorithm strength
        weak_algorithms = [k for k in self.encryption_keys.values()
                          if k.algorithm in [EncryptionAlgorithm.AES_128, EncryptionAlgorithm.RSA_2048]]
        if weak_algorithms:
            findings.append({
                'severity': 'medium',
                'category': 'encryption',
                'finding': f'{len(weak_algorithms)} keys use weak encryption algorithms',
                'impact': 'Reduced security strength'
            })

        return findings

    def _audit_data_transfer_compliance(self) -> List[Dict[str, Any]]:
        """Audit data transfer compliance"""
        findings = []

        # Check unencrypted transfers
        unencrypted_transfers = [t for t in self.data_transfers
                               if not t.encryption_used and t.data_classification != DataClassification.PUBLIC]
        if unencrypted_transfers:
            findings.append({
                'severity': 'high',
                'category': 'data_transfer',
                'finding': f'{len(unencrypted_transfers)} sensitive data transfers were unencrypted',
                'impact': 'Data confidentiality compromised'
            })

        # Check failed transfers
        failed_transfers = [t for t in self.data_transfers if not t.success]
        if len(failed_transfers) > len(self.data_transfers) * 0.1:  # More than 10% failure rate
            findings.append({
                'severity': 'medium',
                'category': 'data_transfer',
                'finding': f'High data transfer failure rate: {len(failed_transfers)}/{len(self.data_transfers)}',
                'impact': 'Data transfer reliability issues'
            })

        return findings

    def _generate_audit_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate audit recommendations"""
        recommendations = []

        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        categories = set()

        for finding in findings:
            severity_counts[finding['severity']] += 1
            categories.add(finding['category'])

        if severity_counts['critical'] > 0:
            recommendations.append("Address all critical findings immediately to prevent security breaches")

        if 'network_security' in categories:
            recommendations.append("Strengthen network segmentation and firewall configurations")

        if 'encryption' in categories:
            recommendations.append("Update encryption policies and rotate expired keys")

        if 'data_transfer' in categories:
            recommendations.append("Implement stricter data transfer controls and monitoring")

        recommendations.append("Establish regular communications security audits and monitoring")

        return recommendations

    def _calculate_audit_compliance_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate audit compliance score"""
        if not findings:
            return 100.0

        # Weight findings by severity
        weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        total_weight = sum(weights.get(f['severity'], 1) for f in findings)
        max_possible_weight = 50  # Arbitrary maximum

        score = max(0, 100 - (total_weight / max_possible_weight * 100))
        return round(score, 1)

    def get_communications_dashboard(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive communications security dashboard"""
        # Get network status
        network_status = {}
        for segment_id, segment in self.network_segments.items():
            # Calculate segment health (simplified)
            control_count = len(segment.security_controls)
            health_score = min(100, control_count * 20)  # 20 points per control

            network_status[segment_id] = {
                'name': segment.name,
                'type': segment.network_type.value,
                'health_score': health_score,
                'active': segment.is_active,
                'security_controls': len(segment.security_controls)
            }

        # Get encryption status
        encryption_status = {
            'total_keys': len(self.encryption_keys),
            'active_keys': len([k for k in self.encryption_keys.values() if k.status == 'active']),
            'expired_keys': len([k for k in self.encryption_keys.values() if k.expiry_date < datetime.utcnow()]),
            'algorithms': {}
        }

        for key in self.encryption_keys.values():
            alg = key.algorithm.value
            encryption_status['algorithms'][alg] = encryption_status['algorithms'].get(alg, 0) + 1

        # Get transfer metrics
        recent_transfers = [t for t in self.data_transfers
                           if (datetime.utcnow() - t.transfer_start).days <= 7]

        transfer_metrics = {
            'total_transfers': len(recent_transfers),
            'successful_transfers': len([t for t in recent_transfers if t.success]),
            'encrypted_transfers': len([t for t in recent_transfers if t.encryption_used]),
            'average_size_mb': round(sum(t.data_size_bytes for t in recent_transfers) / len(recent_transfers) / (1024*1024), 1) if recent_transfers else 0
        }

        # Get security events
        recent_traffic = [t for t in self.network_traffic
                         if (datetime.utcnow() - t.timestamp).hours <= 24]

        security_events = {
            'total_traffic': len(recent_traffic),
            'anomalies_detected': len([t for t in recent_traffic if t.anomaly_detected]),
            'blocked_traffic': len([t for t in recent_traffic if t.blocked]),
            'top_applications': self._get_top_applications(recent_traffic)
        }

        # Get compliance status
        compliance_status = self._calculate_overall_compliance()

        # Generate recommendations
        recommendations = self._generate_dashboard_recommendations(
            network_status, encryption_status, security_events
        )

        dashboard = CommunicationsDashboard(
            id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            network_status=network_status,
            encryption_status=encryption_status,
            transfer_metrics=transfer_metrics,
            security_events=security_events,
            compliance_status=compliance_status,
            recommendations=recommendations
        )

        return {
            'dashboard_id': dashboard.id,
            'generated_at': dashboard.generated_at.isoformat(),
            'period': f"{dashboard.period_start.date()} to {dashboard.period_end.date()}",
            'network_status': dashboard.network_status,
            'encryption_status': dashboard.encryption_status,
            'transfer_metrics': dashboard.transfer_metrics,
            'security_events': dashboard.security_events,
            'compliance_status': dashboard.compliance_status,
            'recommendations': dashboard.recommendations
        }

    def _get_top_applications(self, traffic: List[NetworkTraffic]) -> List[Dict[str, Any]]:
        """Get top applications by traffic volume"""
        app_stats = {}
        for t in traffic:
            app = t.application
            app_stats[app] = app_stats.get(app, 0) + t.bytes_sent + t.bytes_received

        sorted_apps = sorted(app_stats.items(), key=lambda x: x[1], reverse=True)
        return [{'application': app, 'bytes': bytes_count} for app, bytes_count in sorted_apps[:5]]

    def _calculate_overall_compliance(self) -> Dict[str, Any]:
        """Calculate overall communications compliance"""
        # Simplified compliance calculation
        network_compliant = len([s for s in self.network_segments.values() if len(s.security_controls) >= 3])
        network_score = (network_compliant / len(self.network_segments)) * 100 if self.network_segments else 100

        encryption_compliant = len([k for k in self.encryption_keys.values()
                                  if k.status == 'active' and k.expiry_date > datetime.utcnow()])
        encryption_score = (encryption_compliant / len(self.encryption_keys)) * 100 if self.encryption_keys else 100

        transfer_compliant = len([t for t in self.data_transfers if t.encryption_used and t.integrity_verified])
        transfer_score = (transfer_compliant / len(self.data_transfers)) * 100 if self.data_transfers else 100

        overall_score = (network_score + encryption_score + transfer_score) / 3

        return {
            'overall_score': round(overall_score, 1),
            'network_score': round(network_score, 1),
            'encryption_score': round(encryption_score, 1),
            'transfer_score': round(transfer_score, 1),
            'status': 'COMPLIANT' if overall_score >= 85 else 'NEEDS_ATTENTION' if overall_score >= 70 else 'NON_COMPLIANT'
        }

    def _generate_dashboard_recommendations(self, network: Dict, encryption: Dict,
                                          security: Dict) -> List[str]:
        """Generate dashboard recommendations"""
        recommendations = []

        # Network recommendations
        low_health_segments = [sid for sid, status in network.items() if status['health_score'] < 60]
        if low_health_segments:
            recommendations.append(f"Improve security controls for network segments: {low_health_segments}")

        # Encryption recommendations
        if encryption['expired_keys'] > 0:
            recommendations.append(f"Rotate {encryption['expired_keys']} expired encryption keys")

        # Security recommendations
        if security['anomalies_detected'] > security['total_traffic'] * 0.05:  # More than 5%
            recommendations.append("Review anomaly detection thresholds and investigate high anomaly rate")

        if not recommendations:
            recommendations.append("Continue monitoring communications security and maintain current standards")

        return recommendations

    def check_communications_security_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 communications security compliance"""
        compliance_checks = {
            'network_security': self._check_network_security_compliance(),
            'information_transfer': self._check_information_transfer_compliance(),
            'cryptography': self._check_cryptography_compliance()
        }

        overall_score = sum(compliance_checks.values()) / len(compliance_checks)

        issues = []
        if compliance_checks['network_security'] < 80:
            issues.append("Network security controls require strengthening")
        if compliance_checks['information_transfer'] < 85:
            issues.append("Information transfer security needs improvement")
        if compliance_checks['cryptography'] < 90:
            issues.append("Cryptographic controls require enhancement")

        return {
            'tenant_id': tenant_id,
            'compliance_score': round(overall_score, 1),
            'control_checks': compliance_checks,
            'issues': issues,
            'recommendations': self._generate_communications_compliance_recommendations(issues),
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.13 Communications Security',
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_network_security_compliance(self) -> float:
        """Check network security compliance"""
        segments = list(self.network_segments.values())

        if not segments:
            return 0.0

        compliant_segments = 0
        for segment in segments:
            score = 100

            # Check security controls
            if not segment.security_controls:
                score -= 50

            # Check firewall rules
            if not segment.firewall_rules:
                score -= 20

            # Check monitoring
            if not segment.monitoring_enabled:
                score -= 10

            compliant_segments += max(score, 0)

        return compliant_segments / len(segments)

    def _check_information_transfer_compliance(self) -> float:
        """Check information transfer compliance"""
        transfers = self.data_transfers[-100:]  # Last 100 transfers

        if not transfers:
            return 100.0

        compliant_transfers = 0
        for transfer in transfers:
            score = 100

            # Check encryption
            if not transfer.encryption_used and transfer.data_classification != DataClassification.PUBLIC:
                score -= 30

            # Check integrity
            if not transfer.integrity_verified:
                score -= 20

            # Check authorization
            if not transfer.authorized_by:
                score -= 25

            compliant_transfers += max(score, 0)

        return compliant_transfers / len(transfers)

    def _check_cryptography_compliance(self) -> float:
        """Check cryptography compliance"""
        keys = list(self.encryption_keys.values())

        if not keys:
            return 50.0  # Some compliance but no keys

        compliant_keys = 0
        for key in keys:
            score = 100

            # Check expiry
            if key.expiry_date < datetime.utcnow():
                score -= 40

            # Check algorithm strength
            if key.algorithm in [EncryptionAlgorithm.AES_128, EncryptionAlgorithm.RSA_2048]:
                score -= 20

            # Check rotation
            if key.last_rotated and (datetime.utcnow() - key.last_rotated).days > 400:  # Over a year
                score -= 15

            compliant_keys += max(score, 0)

        return compliant_keys / len(keys)

    def _generate_communications_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate communications compliance recommendations"""
        recommendations = []

        if any('network security' in issue.lower() for issue in issues):
            recommendations.append("Implement comprehensive network segmentation and security controls")

        if any('information transfer' in issue.lower() for issue in issues):
            recommendations.append("Strengthen information transfer controls with encryption and integrity checking")

        if any('cryptography' in issue.lower() for issue in issues):
            recommendations.append("Update cryptographic policies and ensure regular key rotation")

        recommendations.append("Conduct regular communications security audits and vulnerability assessments")

        return recommendations