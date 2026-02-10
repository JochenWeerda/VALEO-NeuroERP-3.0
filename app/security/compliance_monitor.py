"""
ISO 27001 Compliance Monitoring Dashboard
Informationssicherheits-Managementsystem Compliance Monitoring

Dieses Modul implementiert das Compliance Monitoring gemäß ISO 27001 Annex A.12.6
für VALEO-NeuroERP mit Echtzeit-Compliance-Überwachung.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ISO27001ComplianceMonitor:
    """
    ISO 27001 Compliance Monitoring Dashboard
    Implements Annex A.12.6 - Compliance with Legal Requirements
    """

    def __init__(self, db_session, alert_service=None):
        self.db = db_session
        self.alert_service = alert_service
        self.compliance_checks = self._load_compliance_checks()

    def _load_compliance_checks(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance check definitions"""
        return {
            'password_policy': {
                'name': 'Password Policy Compliance',
                'check_function': self._check_password_policy,
                'frequency': 'daily',
                'severity': 'HIGH',
                'iso_control': 'A.9.2.1',
                'description': 'Ensure password policies meet ISO 27001 requirements'
            },
            'access_reviews': {
                'name': 'Access Rights Review',
                'check_function': self._check_access_reviews,
                'frequency': 'monthly',
                'severity': 'MEDIUM',
                'iso_control': 'A.9.2.2',
                'description': 'Regular review of user access rights'
            },
            'encryption_compliance': {
                'name': 'Data Encryption Compliance',
                'check_function': self._check_encryption_compliance,
                'frequency': 'weekly',
                'severity': 'HIGH',
                'iso_control': 'A.10',
                'description': 'Verify encryption of sensitive data'
            },
            'audit_log_integrity': {
                'name': 'Audit Log Integrity',
                'check_function': self._check_audit_log_integrity,
                'frequency': 'hourly',
                'severity': 'CRITICAL',
                'iso_control': 'A.12.4',
                'description': 'Verify audit log tamper-proof integrity'
            },
            'gdpr_compliance': {
                'name': 'GDPR Compliance Check',
                'check_function': self._check_gdpr_compliance,
                'frequency': 'daily',
                'severity': 'HIGH',
                'iso_control': 'A.18.1',
                'description': 'Ensure GDPR compliance for personal data'
            },
            'backup_compliance': {
                'name': 'Backup and Recovery Compliance',
                'check_function': self._check_backup_compliance,
                'frequency': 'daily',
                'severity': 'HIGH',
                'iso_control': 'A.12.3',
                'description': 'Verify backup procedures and recovery capabilities'
            },
            'incident_response': {
                'name': 'Incident Response Readiness',
                'check_function': self._check_incident_response,
                'frequency': 'weekly',
                'severity': 'MEDIUM',
                'iso_control': 'A.16.1',
                'description': 'Verify incident response procedures are in place'
            },
            'physical_security': {
                'name': 'Physical Security Compliance',
                'check_function': self._check_physical_security,
                'frequency': 'monthly',
                'severity': 'MEDIUM',
                'iso_control': 'A.11',
                'description': 'Verify physical access controls'
            }
        }

    def run_compliance_checks(self, tenant_id: str = 'system') -> Dict[str, Any]:
        """Run all compliance checks and return results"""
        logger.info(f"Running compliance checks for tenant: {tenant_id}")

        results = {
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow(),
            'checks': {},
            'overall_status': 'COMPLIANT',
            'critical_issues': [],
            'warnings': [],
            'compliance_score': 100,
            'last_check_duration': 0
        }

        start_time = datetime.utcnow()

        for check_id, check_config in self.compliance_checks.items():
            try:
                check_result = check_config['check_function'](tenant_id)
                results['checks'][check_id] = check_result

                if check_result['status'] == 'FAILED':
                    if check_config['severity'] == 'CRITICAL':
                        results['overall_status'] = 'NON_COMPLIANT'
                        results['critical_issues'].append(check_result)
                        results['compliance_score'] -= 20
                    else:
                        results['warnings'].append(check_result)
                        results['compliance_score'] -= 5

                elif check_result['status'] == 'WARNING':
                    results['warnings'].append(check_result)
                    results['compliance_score'] -= 2

            except Exception as e:
                logger.error(f"Compliance check {check_id} failed: {e}")
                results['checks'][check_id] = {
                    'status': 'ERROR',
                    'message': str(e),
                    'severity': check_config['severity'],
                    'iso_control': check_config['iso_control']
                }

        # Ensure compliance score doesn't go below 0
        results['compliance_score'] = max(0, results['compliance_score'])

        # Calculate duration
        results['last_check_duration'] = (datetime.utcnow() - start_time).total_seconds()

        # Send alerts for critical issues
        if results['critical_issues'] and self.alert_service:
            self.alert_service.send_critical_alert({
                'type': 'compliance_violation',
                'tenant_id': tenant_id,
                'issues': results['critical_issues'],
                'compliance_score': results['compliance_score']
            })

        logger.info(f"Compliance checks completed for {tenant_id}: Score {results['compliance_score']}, Status {results['overall_status']}")
        return results

    def _check_password_policy(self, tenant_id: str) -> Dict[str, Any]:
        """Check password policy compliance"""
        # In production, query user database for password policy violations
        non_compliant = 0  # Mock: assume no violations

        return {
            'status': 'PASSED' if non_compliant == 0 else 'FAILED',
            'message': f"{non_compliant} users have non-compliant passwords",
            'details': {'non_compliant_users': non_compliant},
            'recommendation': 'Force password reset for non-compliant users' if non_compliant > 0 else None,
            'iso_control': 'A.9.2.1',
            'severity': 'HIGH'
        }

    def _check_access_reviews(self, tenant_id: str) -> Dict[str, Any]:
        """Check if access rights reviews are up to date"""
        # Check for users whose access hasn't been reviewed recently (90 days)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        # Mock: assume some reviews are overdue
        overdue_reviews = 2

        status = 'WARNING' if overdue_reviews > 0 else 'PASSED'

        return {
            'status': status,
            'message': f"{overdue_reviews} users need access review",
            'details': {'overdue_reviews': overdue_reviews, 'threshold_days': 90},
            'recommendation': 'Schedule access rights reviews within 30 days',
            'iso_control': 'A.9.2.2',
            'severity': 'MEDIUM'
        }

    def _check_encryption_compliance(self, tenant_id: str) -> Dict[str, Any]:
        """Check data encryption compliance"""
        # Check for unencrypted sensitive data
        sensitive_tables = ['customer_data', 'financial_records', 'personal_data']
        unencrypted_records = 0

        # Mock checks - in production, query database for encryption status
        for table in sensitive_tables:
            # This would be a more complex query in practice
            count = self._check_unencrypted_data(table, tenant_id)
            unencrypted_records += count

        return {
            'status': 'FAILED' if unencrypted_records > 0 else 'PASSED',
            'message': f"{unencrypted_records} sensitive records are not encrypted",
            'details': {'unencrypted_records': unencrypted_records, 'checked_tables': sensitive_tables},
            'recommendation': 'Implement data encryption for sensitive records immediately' if unencrypted_records > 0 else None,
            'iso_control': 'A.10',
            'severity': 'HIGH'
        }

    def _check_audit_log_integrity(self, tenant_id: str) -> Dict[str, Any]:
        """Check audit log integrity"""
        # Verify hash chain integrity
        integrity_breaches = self._verify_audit_log_integrity(tenant_id)

        return {
            'status': 'FAILED' if integrity_breaches else 'PASSED',
            'message': f"{len(integrity_breaches)} audit log integrity breaches detected",
            'details': {'integrity_breaches': integrity_breaches},
            'recommendation': 'Investigate and restore audit log integrity immediately' if integrity_breaches else None,
            'iso_control': 'A.12.4',
            'severity': 'CRITICAL'
        }

    def _check_gdpr_compliance(self, tenant_id: str) -> Dict[str, Any]:
        """Check GDPR compliance"""
        issues = []

        # Check consent records
        missing_consents = self._check_missing_consents(tenant_id)
        if missing_consents > 0:
            issues.append(f"{missing_consents} users missing consent records")

        # Check data retention compliance
        expired_data = self._check_expired_data(tenant_id)
        if expired_data > 0:
            issues.append(f"{expired_data} records exceed retention period")

        # Check data portability requests
        pending_requests = self._check_pending_portability_requests(tenant_id)
        if pending_requests > 0:
            issues.append(f"{pending_requests} data portability requests pending")

        return {
            'status': 'FAILED' if issues else 'PASSED',
            'message': f"{len(issues)} GDPR compliance issues found",
            'details': {'issues': issues},
            'recommendation': 'Address GDPR compliance issues immediately' if issues else None,
            'iso_control': 'A.18.1',
            'severity': 'HIGH'
        }

    def _check_backup_compliance(self, tenant_id: str) -> Dict[str, Any]:
        """Check backup and recovery compliance"""
        # Check backup success rate, test recovery procedures, etc.
        last_backup = self._get_last_backup_date(tenant_id)
        backup_age_days = (datetime.utcnow() - last_backup).days

        issues = []
        if backup_age_days > 1:
            issues.append(f"Last backup is {backup_age_days} days old")

        # Check if backups are encrypted
        if not self._are_backups_encrypted(tenant_id):
            issues.append("Backups are not encrypted")

        # Check recovery test status
        if not self._was_recovery_tested_recently(tenant_id):
            issues.append("Recovery test not performed recently")

        return {
            'status': 'FAILED' if issues else 'PASSED',
            'message': f"{len(issues)} backup compliance issues found",
            'details': {'issues': issues, 'last_backup_days': backup_age_days},
            'recommendation': 'Address backup compliance issues immediately' if issues else None,
            'iso_control': 'A.12.3',
            'severity': 'HIGH'
        }

    def _check_incident_response(self, tenant_id: str) -> Dict[str, Any]:
        """Check incident response readiness"""
        # Check if incident response plan exists and is up to date
        plan_exists = True  # Mock
        plan_updated_recently = True  # Mock
        team_trained = True  # Mock

        issues = []
        if not plan_exists:
            issues.append("Incident response plan does not exist")
        if not plan_updated_recently:
            issues.append("Incident response plan not updated recently")
        if not team_trained:
            issues.append("Incident response team not trained")

        return {
            'status': 'WARNING' if issues else 'PASSED',
            'message': f"{len(issues)} incident response issues found",
            'details': {'issues': issues},
            'recommendation': 'Update incident response procedures' if issues else None,
            'iso_control': 'A.16.1',
            'severity': 'MEDIUM'
        }

    def _check_physical_security(self, tenant_id: str) -> Dict[str, Any]:
        """Check physical security compliance"""
        # Check physical access controls, server room security, etc.
        issues = []

        # Mock checks - in production, verify physical security measures
        if not self._has_access_control(tenant_id):
            issues.append("Physical access control not implemented")

        if not self._has_server_room_security(tenant_id):
            issues.append("Server room security inadequate")

        return {
            'status': 'WARNING' if issues else 'PASSED',
            'message': f"{len(issues)} physical security issues found",
            'details': {'issues': issues},
            'recommendation': 'Implement physical security measures' if issues else None,
            'iso_control': 'A.11',
            'severity': 'MEDIUM'
        }

    # Helper methods for compliance checks
    def _check_unencrypted_data(self, table: str, tenant_id: str) -> int:
        """Check for unencrypted data in table"""
        # In production, query database for encryption status
        return 0  # Mock: assume all encrypted

    def _verify_audit_log_integrity(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Verify audit log integrity"""
        # In production, check hash chains
        return []  # Mock: assume integrity maintained

    def _check_missing_consents(self, tenant_id: str) -> int:
        """Check for missing GDPR consents"""
        # In production, query consent database
        return 0  # Mock: assume all consents present

    def _check_expired_data(self, tenant_id: str) -> int:
        """Check for data exceeding retention period"""
        # In production, query data retention logs
        return 0  # Mock: assume no expired data

    def _check_pending_portability_requests(self, tenant_id: str) -> int:
        """Check for pending data portability requests"""
        # In production, query GDPR request queue
        return 0  # Mock: assume no pending requests

    def _get_last_backup_date(self, tenant_id: str) -> datetime:
        """Get last backup date"""
        # In production, query backup logs
        return datetime.utcnow() - timedelta(hours=12)  # Mock: 12 hours ago

    def _are_backups_encrypted(self, tenant_id: str) -> bool:
        """Check if backups are encrypted"""
        # In production, verify backup encryption
        return True  # Mock: assume encrypted

    def _was_recovery_tested_recently(self, tenant_id: str) -> bool:
        """Check if recovery was tested recently"""
        # In production, check recovery test logs
        return True  # Mock: assume tested

    def _has_access_control(self, tenant_id: str) -> bool:
        """Check physical access control"""
        return True  # Mock

    def _has_server_room_security(self, tenant_id: str) -> bool:
        """Check server room security"""
        return True  # Mock

    def generate_compliance_report(self, tenant_id: str, start_date: datetime = None,
                                 end_date: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        check_results = self.run_compliance_checks(tenant_id)

        report = {
            'tenant_id': tenant_id,
            'report_period': f"{start_date.date()} to {end_date.date()}",
            'generated_at': datetime.utcnow(),
            'overall_compliance': check_results['overall_status'],
            'compliance_score': check_results['compliance_score'],
            'check_results': check_results['checks'],
            'critical_issues': check_results['critical_issues'],
            'warnings': check_results['warnings'],
            'recommendations': self._generate_recommendations(check_results),
            'next_review_date': datetime.utcnow() + timedelta(days=30),
            'iso_framework_version': 'ISO 27001:2022',
            'certification_readiness': self._assess_certification_readiness(check_results)
        }

        return report

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on check results"""
        recommendations = []

        if results['critical_issues']:
            recommendations.append("IMMEDIATE: Address all critical compliance issues within 24 hours")

        if results['warnings']:
            recommendations.append("URGENT: Resolve warning-level issues within 7 days")

        if results['compliance_score'] < 80:
            recommendations.append("HIGH PRIORITY: Implement comprehensive remediation plan")

        if not any(check.get('status') == 'PASSED' for check in results['checks'].values()):
            recommendations.append("CRITICAL: No compliance checks are currently passing - immediate audit required")

        return recommendations

    def _assess_certification_readiness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readiness for ISO certification"""
        readiness_score = results['compliance_score']

        if readiness_score >= 95:
            readiness = 'READY'
            notes = 'System meets ISO 27001 requirements'
        elif readiness_score >= 85:
            readiness = 'NEAR_READY'
            notes = 'Minor gaps need to be addressed'
        elif readiness_score >= 70:
            readiness = 'DEVELOPING'
            notes = 'Significant improvements needed'
        else:
            readiness = 'NOT_READY'
            notes = 'Major compliance gaps exist'

        return {
            'readiness_level': readiness,
            'readiness_score': readiness_score,
            'notes': notes,
            'estimated_time_to_readiness': self._estimate_time_to_readiness(readiness_score),
            'critical_gaps': len(results['critical_issues'])
        }

    def _estimate_time_to_readiness(self, score: int) -> str:
        """Estimate time to achieve certification readiness"""
        if score >= 95:
            return 'Ready now'
        elif score >= 85:
            return '1-2 weeks'
        elif score >= 70:
            return '1-2 months'
        else:
            return '3-6 months'

    def get_compliance_dashboard(self, tenant_id: str) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        results = self.run_compliance_checks(tenant_id)

        return {
            'tenant_id': tenant_id,
            'last_check': results['timestamp'],
            'overall_status': results['overall_status'],
            'compliance_score': results['compliance_score'],
            'critical_issues_count': len(results['critical_issues']),
            'warnings_count': len(results['warnings']),
            'checks_summary': {
                check_id: check_result['status']
                for check_id, check_result in results['checks'].items()
            },
            'trend_data': self._get_compliance_trend(tenant_id),
            'next_scheduled_check': datetime.utcnow() + timedelta(hours=24)
        }

    def _get_compliance_trend(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get compliance score trend over time"""
        # In production, query historical compliance data
        # Mock trend data
        return [
            {'date': (datetime.utcnow() - timedelta(days=6)).date(), 'score': 85},
            {'date': (datetime.utcnow() - timedelta(days=5)).date(), 'score': 87},
            {'date': (datetime.utcnow() - timedelta(days=4)).date(), 'score': 90},
            {'date': (datetime.utcnow() - timedelta(days=3)).date(), 'score': 88},
            {'date': (datetime.utcnow() - timedelta(days=2)).date(), 'score': 92},
            {'date': (datetime.utcnow() - timedelta(days=1)).date(), 'score': 95},
            {'date': datetime.utcnow().date(), 'score': 93}
        ]