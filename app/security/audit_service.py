"""
ISO 27001 Enhanced Audit Logging System
Informationssicherheits-Managementsystem Audit Service

Dieses Modul implementiert das Audit Logging System gemäß ISO 27001 Annex A.12.4
für VALEO-NeuroERP mit tamper-proof Hash-Chains.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import hashlib
import json
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Audit log entry with tamper-proof integrity"""
    id: str
    timestamp: str
    event_type: str
    user_id: str
    tenant_id: str
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    compliance_flags: List[str]
    risk_score: int
    integrity_hash: str
    previous_hash: str


class ISMSAuditService:
    """
    ISO 27001 Compliant Audit Logging
    Implements Annex A.12.4 - Logging and Monitoring
    """

    def __init__(self, db_session, crypto_service=None):
        self.db = db_session
        self.crypto = crypto_service
        self.audit_trail = []
        self.last_hash = self._get_last_audit_hash()

    def log_security_event(self, event_data: Dict[str, Any]) -> str:
        """
        Log security event with tamper-proof audit trail
        Returns: Audit entry ID
        """
        audit_entry = self._create_audit_entry(event_data)
        audit_entry.integrity_hash = self._create_integrity_hash(audit_entry)

        # Store in secure audit database
        self._store_audit_entry(audit_entry)

        # Real-time alerting for critical events
        if self._is_critical_event(audit_entry):
            self._trigger_security_alert(audit_entry)

        logger.info(f"Audit entry created: {audit_entry.id} - {audit_entry.event_type}")
        return audit_entry.id

    def _create_audit_entry(self, event_data: Dict[str, Any]) -> AuditEntry:
        """Create audit entry from event data"""
        entry_id = str(uuid.uuid4())

        return AuditEntry(
            id=entry_id,
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_data.get('event_type', 'unknown'),
            user_id=event_data.get('user_id', 'system'),
            tenant_id=event_data.get('tenant_id', 'system'),
            resource_type=event_data.get('resource_type', 'unknown'),
            resource_id=event_data.get('resource_id', 'unknown'),
            action=event_data.get('action', 'unknown'),
            details=event_data.get('details', {}),
            ip_address=event_data.get('ip_address'),
            user_agent=event_data.get('user_agent'),
            session_id=event_data.get('session_id'),
            compliance_flags=self._check_compliance_flags(event_data),
            risk_score=self._assess_event_risk(event_data),
            integrity_hash="",  # Will be set later
            previous_hash=self.last_hash
        )

    def _create_integrity_hash(self, entry: AuditEntry) -> str:
        """Create cryptographic hash for audit trail integrity"""
        # Create content string for hashing
        content_parts = [
            entry.previous_hash,
            entry.id,
            entry.timestamp,
            entry.event_type,
            entry.user_id,
            entry.tenant_id,
            entry.resource_type,
            entry.resource_id,
            entry.action,
            json.dumps(entry.details, sort_keys=True),
            str(entry.risk_score)
        ]

        content = "|".join(content_parts)

        # Use SHA-256 for integrity
        if self.crypto and hasattr(self.crypto, 'create_hash'):
            return self.crypto.create_hash(content)
        else:
            # Fallback to hashlib
            return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _check_compliance_flags(self, event_data: Dict[str, Any]) -> List[str]:
        """Check event against compliance requirements"""
        flags = []

        action = event_data.get('action', '')
        resource_type = event_data.get('resource_type', '')

        # GDPR compliance checks
        if action in ['access_personal_data', 'export_data', 'modify_user_data']:
            flags.append('GDPR_PROCESSING')
            if not event_data.get('consent_verified', False):
                flags.append('GDPR_CONSENT_MISSING')

        if resource_type in ['User', 'Customer', 'PersonalData']:
            flags.append('GDPR_PERSONAL_DATA')

        # SOX compliance for financial data
        if resource_type in ['FinancialRecord', 'JournalEntry', 'Account']:
            flags.append('SOX_FINANCIAL_DATA')
            if action in ['modify', 'delete', 'create']:
                flags.append('SOX_CHANGE_CONTROL')

        # ISO 27001 access control
        if action == 'unauthorized_access':
            flags.append('ISO27001_ACCESS_VIOLATION')

        if event_data.get('unusual_time', False):
            flags.append('ISO27001_UNUSUAL_TIME')

        if event_data.get('unusual_location', False):
            flags.append('ISO27001_UNUSUAL_LOCATION')

        # PCI DSS for payment data
        if resource_type in ['Payment', 'CreditCard', 'BankAccount']:
            flags.append('PCI_DSS_PAYMENT_DATA')

        return flags

    def _assess_event_risk(self, event_data: Dict[str, Any]) -> int:
        """Assess risk level of security event (0-10 scale)"""
        risk_score = 0

        # Base risk by event type
        risk_matrix = {
            'login_success': 1,
            'login_failure': 3,
            'logout': 1,
            'password_change': 2,
            'password_reset': 3,
            'profile_update': 1,
            'data_access': 2,
            'data_export': 5,
            'data_modify': 4,
            'data_delete': 7,
            'admin_action': 6,
            'security_config_change': 9,
            'unauthorized_access': 8,
            'suspicious_activity': 7,
            'security_breach': 10,
            'data_breach': 10
        }

        event_type = event_data.get('event_type', 'unknown')
        risk_score += risk_matrix.get(event_type, 2)

        # Additional risk factors
        if event_data.get('ip_address') and self._is_suspicious_ip(event_data['ip_address']):
            risk_score += 3

        if event_data.get('unusual_time', False):
            risk_score += 2

        if event_data.get('unusual_location', False):
            risk_score += 2

        if event_data.get('multiple_failures', False):
            risk_score += 2

        if event_data.get('admin_privileges', False):
            risk_score += 1

        # Cap at 10
        return min(risk_score, 10)

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        # This would check against known malicious IP lists
        # For now, return False (not suspicious)
        return False

    def _is_critical_event(self, audit_entry: AuditEntry) -> bool:
        """Determine if event requires immediate attention"""
        return (
            audit_entry.risk_score >= 8 or
            'ISO27001_ACCESS_VIOLATION' in audit_entry.compliance_flags or
            audit_entry.event_type in ['security_breach', 'data_breach', 'unauthorized_access']
        )

    def _trigger_security_alert(self, audit_entry: AuditEntry):
        """Trigger security alert for critical events"""
        alert_data = {
            'severity': 'CRITICAL' if audit_entry.risk_score >= 9 else 'HIGH',
            'event_id': audit_entry.id,
            'description': f"Critical security event: {audit_entry.event_type}",
            'details': {
                'user_id': audit_entry.user_id,
                'resource': f"{audit_entry.resource_type}:{audit_entry.resource_id}",
                'action': audit_entry.action,
                'ip_address': audit_entry.ip_address,
                'compliance_flags': audit_entry.compliance_flags
            },
            'required_actions': [
                'Immediate investigation required',
                'Stakeholder notification within 1 hour',
                'Incident response team activation' if audit_entry.risk_score >= 9 else 'Enhanced monitoring initiated'
            ],
            'escalation_matrix': {
                'immediate': ['Security Team Lead', 'CISO'],
                '1_hour': ['Management', 'Legal'],
                '4_hours': ['Board Members'] if audit_entry.risk_score >= 10 else []
            }
        }

        # Send to security team, create incident ticket, etc.
        self._send_security_alert(alert_data)
        logger.warning(f"Security alert triggered for event {audit_entry.id}")

    def _store_audit_entry(self, entry: AuditEntry):
        """Store audit entry in tamper-proof database"""
        # In production, this would use a secure, tamper-proof database
        # For now, store in memory and log
        self.audit_trail.append(entry)
        self.last_hash = entry.integrity_hash

        # Log to file for persistence
        logger.info(f"AUDIT: {entry.id}|{entry.timestamp}|{entry.event_type}|{entry.user_id}|{entry.action}")

    def _get_last_audit_hash(self) -> str:
        """Get the last audit hash for chain integrity"""
        # In production, this would query the database
        return "genesis" if not self.audit_trail else self.audit_trail[-1].integrity_hash

    def _send_security_alert(self, alert_data: Dict[str, Any]):
        """Send security alert to appropriate channels"""
        # This would integrate with alerting systems (email, SMS, Slack, etc.)
        logger.critical(f"SECURITY ALERT: {alert_data['description']}")

    def verify_audit_integrity(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Verify audit trail integrity"""
        entries = self._get_audit_entries_in_range(start_date, end_date)

        integrity_breaches = []
        expected_hash = self._get_hash_at_date(start_date) if start_date else "genesis"

        for entry in entries:
            calculated_hash = self._create_integrity_hash(entry)
            if calculated_hash != entry.integrity_hash:
                integrity_breaches.append({
                    'entry_id': entry.id,
                    'expected_hash': calculated_hash,
                    'stored_hash': entry.integrity_hash,
                    'timestamp': entry.timestamp
                })
            expected_hash = entry.integrity_hash

        return {
            'entries_checked': len(entries),
            'integrity_breaches': len(integrity_breaches),
            'breach_details': integrity_breaches,
            'integrity_maintained': len(integrity_breaches) == 0
        }

    def _get_audit_entries_in_range(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[AuditEntry]:
        """Get audit entries in date range"""
        # In production, this would query the database
        return self.audit_trail

    def _get_hash_at_date(self, date: datetime) -> str:
        """Get audit hash at specific date"""
        # This would find the last hash before the given date
        return "genesis"

    def get_audit_report(self, tenant_id: str, start_date: datetime, end_date: datetime,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate audit report for compliance"""
        entries = self._get_filtered_audit_entries(tenant_id, start_date, end_date, filters)

        report = {
            'tenant_id': tenant_id,
            'period': f"{start_date.date()} to {end_date.date()}",
            'total_events': len(entries),
            'event_summary': self._summarize_events(entries),
            'compliance_flags': self._summarize_compliance_flags(entries),
            'risk_distribution': self._summarize_risk_levels(entries),
            'integrity_status': self.verify_audit_integrity(start_date, end_date),
            'generated_at': datetime.utcnow()
        }

        return report

    def _get_filtered_audit_entries(self, tenant_id: str, start_date: datetime,
                                   end_date: datetime, filters: Optional[Dict[str, Any]]) -> List[AuditEntry]:
        """Get filtered audit entries"""
        # Apply filters and return matching entries
        filtered_entries = [
            entry for entry in self.audit_trail
            if entry.tenant_id == tenant_id and
               start_date <= datetime.fromisoformat(entry.timestamp) <= end_date
        ]

        if filters:
            if 'event_type' in filters:
                filtered_entries = [e for e in filtered_entries if e.event_type == filters['event_type']]
            if 'user_id' in filters:
                filtered_entries = [e for e in filtered_entries if e.user_id == filters['user_id']]
            if 'resource_type' in filters:
                filtered_entries = [e for e in filtered_entries if e.resource_type == filters['resource_type']]

        return filtered_entries

    def _summarize_events(self, entries: List[AuditEntry]) -> Dict[str, int]:
        """Summarize events by type"""
        summary = {}
        for entry in entries:
            summary[entry.event_type] = summary.get(entry.event_type, 0) + 1
        return summary

    def _summarize_compliance_flags(self, entries: List[AuditEntry]) -> Dict[str, int]:
        """Summarize compliance flags"""
        summary = {}
        for entry in entries:
            for flag in entry.compliance_flags:
                summary[flag] = summary.get(flag, 0) + 1
        return summary

    def _summarize_risk_levels(self, entries: List[AuditEntry]) -> Dict[str, int]:
        """Summarize risk levels"""
        summary = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        for entry in entries:
            if entry.risk_score >= 8:
                summary['CRITICAL'] += 1
            elif entry.risk_score >= 6:
                summary['HIGH'] += 1
            elif entry.risk_score >= 4:
                summary['MEDIUM'] += 1
            else:
                summary['LOW'] += 1
        return summary

    def get_security_dashboard(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get security dashboard data"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        entries = self._get_filtered_audit_entries(tenant_id, start_date, end_date)

        return {
            'period_days': days,
            'total_events': len(entries),
            'critical_events': len([e for e in entries if e.risk_score >= 8]),
            'compliance_violations': len([e for e in entries if e.compliance_flags]),
            'top_event_types': self._summarize_events(entries),
            'risk_trend': self._calculate_risk_trend(entries, days),
            'integrity_status': 'VERIFIED' if self.verify_audit_integrity(start_date, end_date)['integrity_maintained'] else 'BREACHED'
        }

    def _calculate_risk_trend(self, entries: List[AuditEntry], days: int) -> List[Dict[str, Any]]:
        """Calculate risk trend over time"""
        # Group by day and calculate average risk score
        daily_risks = {}
        for entry in entries:
            day = datetime.fromisoformat(entry.timestamp).date()
            if day not in daily_risks:
                daily_risks[day] = []
            daily_risks[day].append(entry.risk_score)

        trend = []
        for day in sorted(daily_risks.keys()):
            avg_risk = sum(daily_risks[day]) / len(daily_risks[day])
            trend.append({
                'date': day.isoformat(),
                'average_risk': round(avg_risk, 2),
                'event_count': len(daily_risks[day])
            })

        return trend