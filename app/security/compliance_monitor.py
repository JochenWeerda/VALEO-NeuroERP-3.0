"""
ISO 27001 Compliance Monitoring Dashboard
Informationssicherheits-Managementsystem Compliance Monitoring

Dieses Modul implementiert das Compliance Monitoring gemäß ISO 27001 Annex A.12.6
für VALEO-NeuroERP mit Echtzeit-Compliance-Überwachung.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
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

    def run_compliance_checks(self, tenant_id: str = '00000000-0000-0000-0000-000000000001') -> Dict[str, Any]:
        """Run all compliance checks and return results"""
        logger.info(f"Running compliance checks for tenant: {tenant_id}")

        results = {
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow(),
            'checks': {},
            'overall_status': 'COMPLIANT',
            'critical_issues': [],
            'warnings': [],
            'unverified_checks': [],
            'compliance_score': 100,
            'last_check_duration': 0
        }

        start_time = datetime.utcnow()

        for check_id, check_config in self.compliance_checks.items():
            try:
                check_result = check_config['check_function'](tenant_id)
                if not isinstance(check_result, dict) or check_result.get('status') not in {
                    'PASSED', 'FAILED', 'WARNING', 'UNKNOWN', 'ERROR'
                }:
                    raise ValueError("Invalid compliance check result")
                results['checks'][check_id] = check_result

                if check_result['status'] in {'UNKNOWN', 'ERROR'}:
                    results['unverified_checks'].append(check_id)
                elif check_result['status'] == 'FAILED':
                    results['overall_status'] = 'NON_COMPLIANT'
                    if check_config['severity'] == 'CRITICAL':
                        results['critical_issues'].append(check_result)
                        results['compliance_score'] -= 20
                    else:
                        results['warnings'].append(check_result)
                        results['compliance_score'] -= 5

                elif check_result['status'] == 'WARNING':
                    results['warnings'].append(check_result)
                    results['compliance_score'] -= 2

            except Exception as e:
                logger.error("Compliance check %s failed (%s)", check_id, type(e).__name__)
                results["unverified_checks"].append(check_id)
                results['checks'][check_id] = {
                    'status': 'ERROR',
                    'message': 'Compliance check failed; evidence is unavailable.',
                    'severity': check_config['severity'],
                    'iso_control': check_config['iso_control']
                }

        # Ensure compliance score doesn't go below 0
        if not results['checks'] or results['unverified_checks']:
            results['compliance_score'] = None
            if results['overall_status'] != 'NON_COMPLIANT':
                results['overall_status'] = 'UNKNOWN'
        else:
            results['compliance_score'] = max(0, results['compliance_score'])
            if results['warnings'] and results['overall_status'] == 'COMPLIANT':
                results['overall_status'] = 'WARNING'

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

    def _unverified_check(self, check_id: str) -> Dict[str, Any]:
        """No positive assertion without a verified, tenant-bound evidence source."""
        config = self.compliance_checks[check_id]
        return {
            "status": "UNKNOWN",
            "message": "Verified evidence source is not configured.",
            "details": {"evidence_available": False},
            "recommendation": "Connect and verify the tenant-bound evidence source.",
            "iso_control": config["iso_control"],
            "severity": config["severity"],
        }

    def _check_password_policy(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("password_policy")

    def _check_access_reviews(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("access_reviews")

    def _check_encryption_compliance(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("encryption_compliance")

    def _check_audit_log_integrity(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("audit_log_integrity")

    def _check_gdpr_compliance(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("gdpr_compliance")

    def _check_backup_compliance(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("backup_compliance")

    def _check_incident_response(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("incident_response")

    def _check_physical_security(self, tenant_id: str) -> Dict[str, Any]:
        return self._unverified_check("physical_security")

    # Helper methods for compliance checks


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

        if results['compliance_score'] is None:
            recommendations.append('REQUIRED: Establish verified evidence for all checks')
        elif results['compliance_score'] < 80:
            recommendations.append("HIGH PRIORITY: Implement comprehensive remediation plan")

        if not any(check.get('status') == 'PASSED' for check in results['checks'].values()):
            recommendations.append("CRITICAL: No compliance checks are currently passing - immediate audit required")

        return recommendations

    def _assess_certification_readiness(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readiness for ISO certification"""
        readiness_score = results['compliance_score']
        if readiness_score is None:
            return {
                'readiness_level': 'UNKNOWN', 'readiness_score': None,
                'notes': 'Insufficient verified evidence; no certification assessment is possible.',
                'estimated_time_to_readiness': None,
                'critical_gaps': len(results['critical_issues']),
            }

        if readiness_score >= 95:
            readiness = 'READY'
            notes = 'Automated checks passed; certification requires an independent audit.'
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

    def _estimate_time_to_readiness(self, score: int) -> None:
        """Certification dates require an independently assessed remediation plan."""
        return None

    def get_compliance_dashboard(self, tenant_id: str) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        results = self.run_compliance_checks(tenant_id)

        return {
            'tenant_id': tenant_id,
            'last_check': results['timestamp'],
            'overall_status': results['overall_status'],
            'compliance_score': results['compliance_score'],
            'unverified_checks': results['unverified_checks'],
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
        """No historical evidence is persisted by this monitor."""
        return []
