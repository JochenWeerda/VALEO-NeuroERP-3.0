"""
ISO 27001 Network Security System
Informationssicherheits-Managementsystem Network Security

Dieses Modul implementiert die Network Security gemäß ISO 27001 Annex A.13
für VALEO-NeuroERP mit Network Segmentation, Secure Communications und Monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import ipaddress
import re

logger = logging.getLogger(__name__)


class NetworkZone(Enum):
    """Network security zones"""
    INTERNET = "internet"
    DMZ = "dmz"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    MANAGEMENT = "management"


class TrafficDirection(Enum):
    """Network traffic directions"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    LATERAL = "lateral"


class SecurityProtocol(Enum):
    """Supported security protocols"""
    TLS_1_3 = "TLS_1.3"
    IPSEC = "IPSEC"
    SSH = "SSH"
    HTTPS = "HTTPS"
    SFTP = "SFTP"


@dataclass
class NetworkAsset:
    """Network asset representation"""
    id: str
    hostname: str
    ip_address: str
    mac_address: Optional[str]
    network_zone: NetworkZone
    asset_type: str  # server, workstation, network_device, etc.
    criticality: str  # low, medium, high, critical
    services: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    compliance_status: str = "unknown"


@dataclass
class FirewallRule:
    """Firewall rule representation"""
    id: str
    name: str
    source_zone: NetworkZone
    destination_zone: NetworkZone
    source_ip: str
    destination_ip: str
    protocol: str
    port: Optional[int]
    action: str  # allow, deny, log
    direction: TrafficDirection
    enabled: bool = True
    priority: int = 100
    description: str = ""


@dataclass
class NetworkEvent:
    """Network security event"""
    id: str
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: str
    destination_ip: str
    source_port: Optional[int]
    destination_port: Optional[int]
    protocol: str
    action_taken: str
    details: Dict[str, Any]
    tenant_id: str = "system"


@dataclass
class VPNConnection:
    """VPN connection details"""
    id: str
    user_id: str
    client_ip: str
    assigned_ip: str
    protocol: SecurityProtocol
    connected_at: datetime
    last_activity: datetime
    bytes_sent: int = 0
    bytes_received: int = 0
    status: str = "active"


class ISO27001NetworkSecurity:
    """
    ISO 27001 Network Security Implementation
    Implements Annex A.13 - Communications Security
    """

    def __init__(self, db_session, firewall_service=None, ids_service=None, vpn_service=None):
        self.db = db_session
        self.firewall = firewall_service
        self.ids = ids_service
        self.vpn = vpn_service

        # Network asset tracking
        self.network_assets: Dict[str, NetworkAsset] = {}

        # Security policies
        self.firewall_rules: Dict[str, FirewallRule] = {}
        self.network_policies = self._initialize_network_policies()

        # Monitoring
        self.network_events: List[NetworkEvent] = []
        self.vpn_connections: Dict[str, VPNConnection] = {}

        # Compliance thresholds
        self.compliance_thresholds = {
            'max_open_ports': 10,
            'max_unencrypted_connections': 0,
            'min_encryption_strength': 'TLS_1.2',
            'max_zones_without_segmentation': 0
        }

    def _initialize_network_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize network security policies"""
        return {
            'zone_segmentation': {
                'enabled': True,
                'internet_to_internal': 'deny_all',
                'internal_to_sensitive': 'allow_business_only',
                'dmz_to_internal': 'allow_specific_ports',
                'management_access': 'restricted_ip_only'
            },
            'encryption_policy': {
                'minimum_tls_version': 'TLS_1.3',
                'require_encryption': ['web_traffic', 'api_calls', 'database_connections'],
                'forbid_protocols': ['SSLv3', 'TLS_1.0', 'TLS_1.1']
            },
            'access_control': {
                'default_deny': True,
                'least_privilege': True,
                'time_based_access': True,
                'geographic_restrictions': True
            },
            'monitoring_policy': {
                'log_all_traffic': False,
                'alert_on_suspicious': True,
                'intrusion_detection': True,
                'traffic_analysis': True
            }
        }

    def register_network_asset(self, asset_data: Dict[str, Any]) -> str:
        """
        Register a network asset for security monitoring
        Returns asset ID
        """
        asset_id = asset_data.get('id') or str(uuid.uuid4())

        asset = NetworkAsset(
            id=asset_id,
            hostname=asset_data['hostname'],
            ip_address=asset_data['ip_address'],
            mac_address=asset_data.get('mac_address'),
            network_zone=NetworkZone[asset_data['network_zone'].upper()],
            asset_type=asset_data['asset_type'],
            criticality=asset_data.get('criticality', 'medium'),
            services=asset_data.get('services', []),
            open_ports=asset_data.get('open_ports', [])
        )

        self.network_assets[asset_id] = asset

        # Perform initial security assessment
        self._assess_asset_security(asset)

        logger.info(f"Network asset registered: {asset.hostname} ({asset.ip_address}) in {asset.network_zone.value}")
        return asset_id

    def _assess_asset_security(self, asset: NetworkAsset):
        """Perform security assessment of network asset"""
        issues = []

        # Check for excessive open ports
        if len(asset.open_ports) > self.compliance_thresholds['max_open_ports']:
            issues.append(f"Too many open ports: {len(asset.open_ports)}")

        # Check for sensitive services on wrong zones
        sensitive_services = ['database', 'domain_controller', 'file_server']
        if asset.network_zone == NetworkZone.DMZ and any(s in asset.services for s in sensitive_services):
            issues.append("Sensitive services exposed in DMZ")

        # Check for unencrypted services
        unencrypted_ports = [80, 21, 23, 25, 110, 143]  # HTTP, FTP, Telnet, SMTP, POP3, IMAP
        if any(port in unencrypted_ports for port in asset.open_ports):
            issues.append("Unencrypted services detected")

        # Update compliance status
        asset.compliance_status = "compliant" if not issues else "non_compliant"

        if issues:
            logger.warning(f"Security issues found for asset {asset.hostname}: {', '.join(issues)}")

    def create_firewall_rule(self, rule_data: Dict[str, Any]) -> str:
        """
        Create a firewall rule
        Returns rule ID
        """
        rule_id = str(uuid.uuid4())

        rule = FirewallRule(
            id=rule_id,
            name=rule_data['name'],
            source_zone=NetworkZone[rule_data['source_zone'].upper()],
            destination_zone=NetworkZone[rule_data['destination_zone'].upper()],
            source_ip=rule_data['source_ip'],
            destination_ip=rule_data['destination_ip'],
            protocol=rule_data['protocol'],
            port=rule_data.get('port'),
            action=rule_data.get('action', 'allow'),
            direction=TrafficDirection[rule_data.get('direction', 'inbound').upper()],
            priority=rule_data.get('priority', 100),
            description=rule_data.get('description', '')
        )

        # Validate rule against security policies
        if not self._validate_firewall_rule(rule):
            raise ValueError("Firewall rule violates security policy")

        self.firewall_rules[rule_id] = rule

        # Apply rule if firewall service available
        if self.firewall:
            self.firewall.apply_rule(rule)

        logger.info(f"Firewall rule created: {rule.name} ({rule.action} {rule.protocol})")
        return rule_id

    def _validate_firewall_rule(self, rule: FirewallRule) -> bool:
        """Validate firewall rule against security policies"""
        policies = self.network_policies['zone_segmentation']

        # Check zone segmentation rules
        if rule.source_zone == NetworkZone.INTERNET and rule.destination_zone == NetworkZone.INTERNAL:
            if policies['internet_to_internal'] == 'deny_all':
                return rule.action == 'deny'

        if rule.source_zone == NetworkZone.INTERNAL and rule.destination_zone == NetworkZone.SENSITIVE:
            if policies['internal_to_sensitive'] == 'allow_business_only':
                # Additional business logic validation would go here
                return True

        # Check for dangerous rules
        if rule.action == 'allow' and rule.protocol in ['all', '*']:
            logger.warning(f"Potentially dangerous allow-all rule: {rule.name}")
            return False

        return True

    def monitor_network_traffic(self, traffic_data: Dict[str, Any]) -> Optional[str]:
        """
        Monitor network traffic for security events
        Returns event ID if security event detected
        """
        # Analyze traffic patterns
        anomalies = self._detect_traffic_anomalies(traffic_data)

        if anomalies:
            event_id = self._create_security_event(traffic_data, anomalies)
            self._respond_to_security_event(event_id, anomalies)
            return event_id

        return None

    def _detect_traffic_anomalies(self, traffic_data: Dict[str, Any]) -> List[str]:
        """Detect anomalies in network traffic"""
        anomalies = []

        source_ip = traffic_data.get('source_ip')
        destination_ip = traffic_data.get('destination_ip')
        protocol = traffic_data.get('protocol')
        port = traffic_data.get('destination_port')

        # Check for suspicious source IPs
        if self._is_suspicious_ip(source_ip):
            anomalies.append(f"suspicious_source_ip: {source_ip}")

        # Check for port scanning
        if self._detects_port_scan(traffic_data):
            anomalies.append("port_scan_detected")

        # Check for unusual protocols
        forbidden_protocols = self.network_policies['encryption_policy']['forbid_protocols']
        if protocol in forbidden_protocols:
            anomalies.append(f"forbidden_protocol: {protocol}")

        # Check for traffic to sensitive ports from wrong zones
        if port in [3389, 5900] and not self._is_management_traffic_allowed(source_ip):  # RDP, VNC
            anomalies.append(f"unauthorized_remote_access: port {port}")

        # Check for data exfiltration patterns
        if self._detects_data_exfiltration(traffic_data):
            anomalies.append("potential_data_exfiltration")

        return anomalies

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            ip = ipaddress.ip_address(ip_address)

            # Check for private IPs in public context
            if ip.is_private and not self._is_trusted_private_ip(ip_address):
                return True

            # Check for known malicious ranges (simplified)
            suspicious_ranges = [
                ipaddress.ip_network('10.0.0.0/8'),  # RFC 1918 but often malicious
            ]

            for net in suspicious_ranges:
                if ip in net:
                    return True

        except ValueError:
            return True  # Invalid IP format

        return False

    def _is_trusted_private_ip(self, ip_address: str) -> bool:
        """Check if private IP is trusted"""
        # In production, this would check against known trusted IP ranges
        return True  # Simplified

    def _detects_port_scan(self, traffic_data: Dict[str, Any]) -> bool:
        """Detect port scanning activity"""
        # Simplified port scan detection
        # In production, this would analyze traffic patterns over time
        ports = traffic_data.get('ports_scanned', [])
        return len(ports) > 10

    def _is_management_traffic_allowed(self, source_ip: str) -> bool:
        """Check if management traffic is allowed from source IP"""
        # Check against management access policy
        management_policy = self.network_policies['zone_segmentation']['management_access']
        if management_policy == 'restricted_ip_only':
            # In production, check against allowed management IPs
            return False  # Simplified - deny by default

        return True

    def _detects_data_exfiltration(self, traffic_data: Dict[str, Any]) -> bool:
        """Detect potential data exfiltration"""
        bytes_sent = traffic_data.get('bytes_sent', 0)
        unusual_time = traffic_data.get('unusual_time', False)
        large_transfer = bytes_sent > 100 * 1024 * 1024  # 100MB

        return large_transfer and unusual_time

    def _create_security_event(self, traffic_data: Dict[str, Any], anomalies: List[str]) -> str:
        """Create a security event"""
        event_id = str(uuid.uuid4())

        # Determine severity based on anomalies
        severity = 'LOW'
        if any('data_exfiltration' in a or 'unauthorized' in a for a in anomalies):
            severity = 'HIGH'
        elif len(anomalies) > 2:
            severity = 'MEDIUM'

        event = NetworkEvent(
            id=event_id,
            timestamp=datetime.utcnow(),
            event_type='network_anomaly',
            severity=severity,
            source_ip=traffic_data.get('source_ip', 'unknown'),
            destination_ip=traffic_data.get('destination_ip', 'unknown'),
            source_port=traffic_data.get('source_port'),
            destination_port=traffic_data.get('destination_port'),
            protocol=traffic_data.get('protocol', 'unknown'),
            action_taken='logged',
            details={
                'anomalies': anomalies,
                'traffic_data': traffic_data,
                'detection_time': datetime.utcnow().isoformat()
            }
        )

        self.network_events.append(event)

        logger.warning(f"Network security event created: {event_id} - {', '.join(anomalies)}")
        return event_id

    def _respond_to_security_event(self, event_id: str, anomalies: List[str]):
        """Respond to detected security events"""
        # Implement automated responses based on anomaly type
        responses = []

        for anomaly in anomalies:
            if 'suspicious_source_ip' in anomaly:
                responses.append("Block suspicious IP temporarily")
            elif 'port_scan' in anomaly:
                responses.append("Implement rate limiting")
            elif 'data_exfiltration' in anomaly:
                responses.append("Alert security team and isolate affected systems")
            elif 'unauthorized' in anomaly:
                responses.append("Block unauthorized access and investigate")

        if responses and self.firewall:
            for response in responses:
                logger.info(f"Automated response: {response}")

    def establish_vpn_connection(self, connection_data: Dict[str, Any]) -> str:
        """
        Establish a secure VPN connection
        Returns connection ID
        """
        connection_id = str(uuid.uuid4())

        connection = VPNConnection(
            id=connection_id,
            user_id=connection_data['user_id'],
            client_ip=connection_data['client_ip'],
            assigned_ip=connection_data['assigned_ip'],
            protocol=SecurityProtocol[connection_data.get('protocol', 'IPSEC')],
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )

        self.vpn_connections[connection_id] = connection

        # Validate connection security
        if not self._validate_vpn_security(connection):
            logger.warning(f"VPN connection security validation failed: {connection_id}")
            # In production, this might terminate the connection

        logger.info(f"VPN connection established: {connection.user_id} from {connection.client_ip}")
        return connection_id

    def _validate_vpn_security(self, connection: VPNConnection) -> bool:
        """Validate VPN connection security"""
        # Check protocol strength
        if connection.protocol not in [SecurityProtocol.IPSEC, SecurityProtocol.TLS_1_3]:
            return False

        # Check client IP (should be from trusted ranges)
        if self._is_suspicious_ip(connection.client_ip):
            return False

        return True

    def monitor_vpn_connection(self, connection_id: str, activity_data: Dict[str, Any]):
        """Monitor VPN connection activity"""
        if connection_id not in self.vpn_connections:
            return

        connection = self.vpn_connections[connection_id]
        connection.last_activity = datetime.utcnow()
        connection.bytes_sent += activity_data.get('bytes_sent', 0)
        connection.bytes_received += activity_data.get('bytes_received', 0)

        # Check for suspicious activity
        if self._detects_vpn_anomaly(connection, activity_data):
            self._handle_vpn_anomaly(connection, activity_data)

    def _detects_vpn_anomaly(self, connection: VPNConnection, activity_data: Dict[str, Any]) -> bool:
        """Detect anomalies in VPN connection"""
        # Check for unusual data transfer patterns
        bytes_per_minute = activity_data.get('bytes_per_minute', 0)
        if bytes_per_minute > 50 * 1024 * 1024:  # 50MB/min
            return True

        # Check for connection from unusual location
        if activity_data.get('unusual_location', False):
            return True

        # Check for multiple failed authentications
        failed_attempts = activity_data.get('failed_attempts', 0)
        if failed_attempts > 3:
            return True

        return False

    def _handle_vpn_anomaly(self, connection: VPNConnection, activity_data: Dict[str, Any]):
        """Handle detected VPN anomalies"""
        logger.warning(f"VPN anomaly detected for connection {connection.id}: {activity_data}")

        # Implement graduated response
        anomaly_type = activity_data.get('anomaly_type', 'unknown')

        if anomaly_type == 'high_bandwidth':
            # Temporary throttling
            pass
        elif anomaly_type == 'unusual_location':
            # Require additional authentication
            pass
        elif anomaly_type == 'failed_attempts':
            # Temporary connection block
            connection.status = 'blocked'

    def get_network_security_status(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive network security status"""
        # Filter assets by tenant
        tenant_assets = [a for a in self.network_assets.values() if a.tenant_id == tenant_id]

        # Calculate compliance metrics
        compliant_assets = sum(1 for a in tenant_assets if a.compliance_status == 'compliant')
        total_assets = len(tenant_assets)
        compliance_rate = (compliant_assets / total_assets * 100) if total_assets > 0 else 0

        # Recent security events
        recent_events = [e for e in self.network_events[-50:] if e.tenant_id == tenant_id]
        critical_events = [e for e in recent_events if e.severity == 'HIGH']

        # Active VPN connections
        active_vpn = [c for c in self.vpn_connections.values()
                     if c.status == 'active' and c.tenant_id == tenant_id]

        return {
            'tenant_id': tenant_id,
            'asset_compliance': {
                'total_assets': total_assets,
                'compliant_assets': compliant_assets,
                'compliance_rate': round(compliance_rate, 1)
            },
            'security_events': {
                'total_recent': len(recent_events),
                'critical_events': len(critical_events),
                'last_event': recent_events[-1].timestamp.isoformat() if recent_events else None
            },
            'vpn_status': {
                'active_connections': len(active_vpn),
                'total_bandwidth': sum(c.bytes_sent + c.bytes_received for c in active_vpn)
            },
            'firewall_status': {
                'total_rules': len(self.firewall_rules),
                'enabled_rules': sum(1 for r in self.firewall_rules.values() if r.enabled)
            },
            'overall_risk_score': self._calculate_network_risk_score(tenant_assets, recent_events),
            'generated_at': datetime.utcnow().isoformat()
        }

    def _calculate_network_risk_score(self, assets: List[NetworkAsset], events: List[NetworkEvent]) -> int:
        """Calculate overall network risk score (0-100)"""
        risk_score = 0

        # Asset compliance factor
        non_compliant = sum(1 for a in assets if a.compliance_status != 'compliant')
        risk_score += min(non_compliant * 5, 30)

        # Security events factor
        critical_events = sum(1 for e in events if e.severity == 'HIGH')
        risk_score += min(critical_events * 10, 40)

        # Firewall coverage factor
        enabled_rules = sum(1 for r in self.firewall_rules.values() if r.enabled)
        if enabled_rules < 10:  # Arbitrary minimum
            risk_score += 20

        # VPN security factor
        active_vpn = sum(1 for c in self.vpn_connections.values() if c.status == 'active')
        if active_vpn > 0:
            risk_score -= 10  # VPN reduces risk

        return max(0, min(risk_score, 100))

    def check_network_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 network security compliance"""
        issues = []

        # Check zone segmentation
        segmentation_issues = self._check_zone_segmentation()
        issues.extend(segmentation_issues)

        # Check encryption compliance
        encryption_issues = self._check_encryption_compliance()
        issues.extend(encryption_issues)

        # Check monitoring coverage
        monitoring_issues = self._check_monitoring_coverage()
        issues.extend(monitoring_issues)

        # Check firewall configuration
        firewall_issues = self._check_firewall_configuration()
        issues.extend(firewall_issues)

        compliance_score = max(0, 100 - (len(issues) * 5))

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_score,
            'total_issues': len(issues),
            'issues': issues,
            'iso_control': 'A.13',
            'recommendations': self._generate_network_recommendations(issues),
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_zone_segmentation(self) -> List[str]:
        """Check network zone segmentation compliance"""
        issues = []

        # Check for assets in wrong zones
        for asset in self.network_assets.values():
            if asset.network_zone == NetworkZone.INTERNET:
                if asset.asset_type in ['database', 'application_server']:
                    issues.append(f"Critical asset {asset.hostname} exposed in internet zone")

        # Check firewall rules for proper segmentation
        internet_to_internal = [
            r for r in self.firewall_rules.values()
            if r.source_zone == NetworkZone.INTERNET and r.destination_zone == NetworkZone.INTERNAL
        ]

        if len(internet_to_internal) > 5:  # Too many exceptions
            issues.append("Too many internet-to-internal firewall exceptions")

        return issues

    def _check_encryption_compliance(self) -> List[str]:
        """Check encryption compliance"""
        issues = []

        # Check for unencrypted services
        for asset in self.network_assets.values():
            unencrypted_ports = [80, 21, 23, 25, 110, 143]  # HTTP, FTP, Telnet, SMTP, POP3, IMAP
            exposed_unencrypted = [p for p in asset.open_ports if p in unencrypted_ports]

            if exposed_unencrypted:
                issues.append(f"Asset {asset.hostname} has unencrypted services on ports {exposed_unencrypted}")

        # Check VPN encryption strength
        weak_vpn = [
            c for c in self.vpn_connections.values()
            if c.protocol not in [SecurityProtocol.IPSEC, SecurityProtocol.TLS_1_3]
        ]

        if weak_vpn:
            issues.append(f"{len(weak_vpn)} VPN connections use weak encryption")

        return issues

    def _check_monitoring_coverage(self) -> List[str]:
        """Check monitoring coverage"""
        issues = []

        # Check for unmonitored assets
        monitored_zones = set()
        for event in self.network_events[-100:]:  # Last 100 events
            # This is simplified - in production, check actual monitoring coverage
            pass

        # Check IDS coverage
        if not self.ids:
            issues.append("Intrusion Detection System not configured")

        return issues

    def _check_firewall_configuration(self) -> List[str]:
        """Check firewall configuration compliance"""
        issues = []

        # Check for default allow rules
        allow_all_rules = [
            r for r in self.firewall_rules.values()
            if r.action == 'allow' and r.protocol in ['all', '*']
        ]

        if allow_all_rules:
            issues.append(f"{len(allow_all_rules)} dangerous allow-all firewall rules found")

        # Check for disabled critical rules
        disabled_rules = [r for r in self.firewall_rules.values() if not r.enabled]
        if len(disabled_rules) > len(self.firewall_rules) * 0.1:  # More than 10% disabled
            issues.append("Too many firewall rules disabled")

        return issues

    def _generate_network_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        if any('segmentation' in issue.lower() for issue in issues):
            recommendations.append("Implement stricter network zone segmentation")

        if any('encryption' in issue.lower() for issue in issues):
            recommendations.append("Upgrade all services to use TLS 1.3 encryption")

        if any('monitoring' in issue.lower() for issue in issues):
            recommendations.append("Deploy comprehensive network monitoring and IDS")

        if any('firewall' in issue.lower() for issue in issues):
            recommendations.append("Review and harden firewall rule configuration")

        if not recommendations:
            recommendations.append("Maintain current strong network security posture")

        return recommendations