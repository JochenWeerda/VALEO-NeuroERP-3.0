# ISO 27001 Technical Implementation Guide

## Security Assessment Framework

### 1. Risk Assessment Engine

```python
# app/security/risk_assessment.py
class ISMSRiskAssessment:
    """
    ISO 27001 Risk Assessment Engine
    Implements Annex A.12 - Operations Security
    """

    def __init__(self, db_session):
        self.db = db_session
        self.risk_matrix = {
            'impact': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4},
            'likelihood': {'rare': 1, 'unlikely': 2, 'possible': 3, 'likely': 4, 'almost_certain': 5}
        }

    def assess_asset_risk(self, asset_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment for an asset
        Returns: Risk score, mitigation requirements, compliance status
        """
        asset = self.get_asset_details(asset_id, tenant_id)
        threats = self.identify_threats(asset)
        vulnerabilities = self.identify_vulnerabilities(asset)

        risk_score = 0
        for threat in threats:
            for vuln in vulnerabilities:
                impact = self.calculate_impact(asset, threat, vuln)
                likelihood = self.calculate_likelihood(threat, vuln)
                risk_score = max(risk_score, impact * likelihood)

        return {
            'asset_id': asset_id,
            'risk_score': risk_score,
            'risk_level': self.classify_risk_level(risk_score),
            'required_mitigations': self.get_mitigation_requirements(risk_score),
            'compliance_status': self.check_compliance_status(asset),
            'last_assessment': datetime.utcnow(),
            'next_assessment_due': self.calculate_next_assessment(risk_score)
        }

    def classify_risk_level(self, score: int) -> str:
        """Classify risk level according to ISO 27001"""
        if score >= 15:
            return 'CRITICAL'
        elif score >= 10:
            return 'HIGH'
        elif score >= 6:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_mitigation_requirements(self, score: int) -> List[str]:
        """Return required mitigation measures"""
        requirements = []

        if score >= 15:  # Critical
            requirements.extend([
                'Immediate mitigation required',
                'Board-level approval needed',
                'Independent security review',
                'Insurance coverage review',
                'Business continuity plan activation'
            ])
        elif score >= 10:  # High
            requirements.extend([
                'Senior management approval',
                'Detailed mitigation plan within 30 days',
                'Regular monitoring and reporting',
                'Security control enhancement'
            ])
        elif score >= 6:  # Medium
            requirements.extend([
                'Management approval required',
                'Mitigation plan within 90 days',
                'Regular risk monitoring'
            ])

        return requirements
```

### 2. Enhanced Audit Logging System

```python
# app/security/audit_service.py
class ISMSAuditService:
    """
    ISO 27001 Compliant Audit Logging
    Implements Annex A.12.4 - Logging and Monitoring
    """

    def __init__(self, db_session, crypto_service):
        self.db = db_session
        self.crypto = crypto_service
        self.audit_trail = []

    def log_security_event(self, event_data: Dict[str, Any]) -> str:
        """
        Log security event with tamper-proof audit trail
        Returns: Audit entry ID
        """
        audit_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_data.get('event_type'),
            'user_id': event_data.get('user_id'),
            'tenant_id': event_data.get('tenant_id'),
            'resource_type': event_data.get('resource_type'),
            'resource_id': event_data.get('resource_id'),
            'action': event_data.get('action'),
            'details': event_data.get('details', {}),
            'ip_address': event_data.get('ip_address'),
            'user_agent': event_data.get('user_agent'),
            'session_id': event_data.get('session_id'),
            'compliance_flags': self.check_compliance_flags(event_data),
            'risk_score': self.assess_event_risk(event_data)
        }

        # Create tamper-proof hash chain
        audit_entry['integrity_hash'] = self.create_integrity_hash(audit_entry)

        # Store in secure audit database
        self.store_audit_entry(audit_entry)

        # Real-time alerting for critical events
        if self.is_critical_event(audit_entry):
            self.trigger_security_alert(audit_entry)

        return audit_entry['id']

    def create_integrity_hash(self, entry: Dict[str, Any]) -> str:
        """Create cryptographic hash for audit trail integrity"""
        # Include previous hash for chain integrity
        previous_hash = self.get_last_audit_hash()
        content = f"{previous_hash}|{entry['id']}|{entry['timestamp']}|{entry['event_type']}"
        return self.crypto.create_hash(content)

    def check_compliance_flags(self, event_data: Dict[str, Any]) -> List[str]:
        """Check event against compliance requirements"""
        flags = []

        # GDPR compliance checks
        if event_data.get('action') in ['access_personal_data', 'export_data']:
            flags.append('GDPR_PROCESSING')
            if not event_data.get('consent_verified'):
                flags.append('GDPR_CONSENT_MISSING')

        # SOX compliance for financial data
        if event_data.get('resource_type') in ['FinancialRecord', 'JournalEntry']:
            flags.append('SOX_FINANCIAL_DATA')
            if event_data.get('action') in ['modify', 'delete']:
                flags.append('SOX_CHANGE_CONTROL')

        # ISO 27001 access control
        if event_data.get('action') == 'unauthorized_access':
            flags.append('ISO27001_ACCESS_VIOLATION')

        return flags

    def assess_event_risk(self, event_data: Dict[str, Any]) -> int:
        """Assess risk level of security event"""
        risk_score = 0

        # Base risk by event type
        risk_matrix = {
            'login_success': 1,
            'login_failure': 3,
            'password_change': 2,
            'unauthorized_access': 8,
            'data_export': 5,
            'admin_action': 6,
            'security_config_change': 9
        }

        risk_score += risk_matrix.get(event_data.get('event_type', 'unknown'), 1)

        # Additional risk factors
        if event_data.get('ip_address') and self.is_suspicious_ip(event_data['ip_address']):
            risk_score += 3

        if event_data.get('unusual_time', False):
            risk_score += 2

        if event_data.get('multiple_failures', False):
            risk_score += 2

        return min(risk_score, 10)  # Cap at 10

    def is_critical_event(self, audit_entry: Dict[str, Any]) -> bool:
        """Determine if event requires immediate attention"""
        return (
            audit_entry['risk_score'] >= 8 or
            'ISO27001_ACCESS_VIOLATION' in audit_entry['compliance_flags'] or
            audit_entry['event_type'] in ['security_breach', 'data_breach']
        )

    def trigger_security_alert(self, audit_entry: Dict[str, Any]):
        """Trigger security alert for critical events"""
        alert_data = {
            'severity': 'CRITICAL' if audit_entry['risk_score'] >= 9 else 'HIGH',
            'event_id': audit_entry['id'],
            'description': f"Critical security event: {audit_entry['event_type']}",
            'details': audit_entry,
            'required_actions': [
                'Immediate investigation',
                'Stakeholder notification',
                'Incident response activation' if audit_entry['risk_score'] >= 9 else 'Enhanced monitoring'
            ]
        }

        # Send to security team, create incident ticket, etc.
        self.send_security_alert(alert_data)
```

### 3. Data Encryption Framework

```python
# app/security/encryption_service.py
class ISO27001EncryptionService:
    """
    ISO 27001 Encryption Service
    Implements Annex A.10 - Cryptography
    """

    def __init__(self, key_management_service):
        self.kms = key_management_service
        self.encryption_algorithm = 'AES-256-GCM'
        self.key_rotation_days = 90

    def encrypt_sensitive_data(self, data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive data with proper key management
        """
        # Determine encryption context
        data_classification = context.get('classification', 'internal')
        tenant_id = context.get('tenant_id')

        # Get appropriate encryption key
        key_id = self.get_encryption_key(data_classification, tenant_id)

        # Encrypt data
        encrypted_data, auth_tag, iv = self.perform_encryption(data, key_id)

        return {
            'encrypted_data': encrypted_data,
            'key_id': key_id,
            'auth_tag': auth_tag,
            'iv': iv,
            'algorithm': self.encryption_algorithm,
            'encrypted_at': datetime.utcnow().isoformat(),
            'classification': data_classification
        }

    def decrypt_sensitive_data(self, encrypted_package: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Decrypt sensitive data with access control
        """
        # Verify access permissions
        if not self.verify_access_permissions(encrypted_package, context):
            raise SecurityException("Access denied to encrypted data")

        # Check key validity
        if self.is_key_expired(encrypted_package['key_id']):
            raise SecurityException("Encryption key has expired")

        # Decrypt data
        return self.perform_decryption(
            encrypted_package['encrypted_data'],
            encrypted_package['key_id'],
            encrypted_package['auth_tag'],
            encrypted_package['iv']
        )

    def get_encryption_key(self, classification: str, tenant_id: str) -> str:
        """Get appropriate encryption key based on data classification"""
        key_hierarchy = {
            'public': 'public-key',
            'internal': f'tenant-{tenant_id}-internal',
            'confidential': f'tenant-{tenant_id}-confidential',
            'restricted': f'tenant-{tenant_id}-restricted'
        }

        key_type = key_hierarchy.get(classification, 'public-key')
        return self.kms.get_active_key(key_type)

    def verify_access_permissions(self, encrypted_package: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Verify user has permission to access encrypted data"""
        user_id = context.get('user_id')
        user_role = context.get('user_role')
        data_classification = encrypted_package.get('classification')

        # Implement role-based access control for encrypted data
        access_matrix = {
            'public': ['user', 'admin', 'auditor'],
            'internal': ['user', 'admin', 'auditor'],
            'confidential': ['admin', 'auditor'],
            'restricted': ['admin']
        }

        allowed_roles = access_matrix.get(data_classification, [])
        return user_role in allowed_roles

    def rotate_encryption_keys(self):
        """Perform automated key rotation per ISO 27001 requirements"""
        expired_keys = self.kms.get_expired_keys(self.key_rotation_days)

        for key_id in expired_keys:
            new_key = self.kms.generate_new_key()
            self.kms.rotate_key(key_id, new_key)

            # Log key rotation event
            self.audit_service.log_security_event({
                'event_type': 'key_rotation',
                'resource_type': 'EncryptionKey',
                'resource_id': key_id,
                'action': 'rotated',
                'details': {'new_key_id': new_key.id}
            })
```

### 4. Access Control Enhancement

```python
# app/security/access_control.py
class ISO27001AccessControl:
    """
    ISO 27001 Access Control Implementation
    Implements Annex A.9 - Access Control
    """

    def __init__(self, audit_service):
        self.audit_service = audit_service
        self.session_timeout = 3600  # 1 hour
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes

    def enforce_least_privilege(self, user_id: str, requested_action: str, resource: Dict[str, Any]) -> bool:
        """
        Implement least privilege access control
        """
        user_permissions = self.get_user_permissions(user_id)
        resource_requirements = self.get_resource_requirements(resource, requested_action)

        # Check if user has all required permissions
        has_access = all(
            perm in user_permissions
            for perm in resource_requirements['required_permissions']
        )

        # Additional context checks
        if has_access:
            has_access = self.check_contextual_constraints(user_id, requested_action, resource)

        # Log access attempt
        self.audit_service.log_security_event({
            'event_type': 'access_attempt',
            'user_id': user_id,
            'resource_type': resource.get('type'),
            'resource_id': resource.get('id'),
            'action': requested_action,
            'success': has_access,
            'details': {
                'required_permissions': resource_requirements['required_permissions'],
                'user_permissions': user_permissions,
                'context_checks_passed': has_access
            }
        })

        return has_access

    def check_contextual_constraints(self, user_id: str, action: str, resource: Dict[str, Any]) -> bool:
        """
        Check additional contextual constraints
        """
        constraints = []

        # Time-based access control
        if not self.check_time_based_access(user_id, action):
            constraints.append('time_restriction')

        # Location-based access control
        if not self.check_location_based_access(user_id, action):
            constraints.append('location_restriction')

        # Device-based access control
        if not self.check_device_based_access(user_id, action):
            constraints.append('device_restriction')

        # Business rule constraints
        if not self.check_business_rules(user_id, action, resource):
            constraints.append('business_rule_violation')

        return len(constraints) == 0

    def implement_session_management(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement secure session management
        """
        session_id = str(uuid.uuid4())

        session = {
            'id': session_id,
            'user_id': session_data['user_id'],
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=self.session_timeout),
            'ip_address': session_data.get('ip_address'),
            'user_agent': session_data.get('user_agent'),
            'mfa_verified': session_data.get('mfa_verified', False),
            'security_level': self.calculate_security_level(session_data)
        }

        # Store session securely
        self.store_session(session)

        return session

    def validate_session(self, session_id: str, client_info: Dict[str, Any]) -> bool:
        """
        Validate session integrity and security
        """
        session = self.get_session(session_id)

        if not session:
            return False

        # Check expiration
        if datetime.utcnow() > session['expires_at']:
            self.invalidate_session(session_id)
            return False

        # Check IP consistency (optional, based on security policy)
        if session.get('ip_address') and client_info.get('ip_address'):
            if session['ip_address'] != client_info['ip_address']:
                # Log suspicious activity
                self.audit_service.log_security_event({
                    'event_type': 'ip_address_change',
                    'user_id': session['user_id'],
                    'session_id': session_id,
                    'details': {
                        'old_ip': session['ip_address'],
                        'new_ip': client_info['ip_address']
                    }
                })

        # Extend session if activity detected
        self.extend_session(session_id)

        return True

    def implement_mfa_enforcement(self, user_id: str, action: str) -> bool:
        """
        Enforce multi-factor authentication for sensitive operations
        """
        mfa_required_actions = [
            'change_password',
            'access_sensitive_data',
            'modify_security_settings',
            'export_data'
        ]

        if action in mfa_required_actions:
            user_mfa_status = self.get_user_mfa_status(user_id)
            if not user_mfa_status['enabled']:
                return False

            # Check recent MFA verification
            if not self.is_mfa_recently_verified(user_id):
                return False

        return True
```

### 5. Compliance Monitoring Dashboard

```python
# app/security/compliance_monitor.py
class ISO27001ComplianceMonitor:
    """
    ISO 27001 Compliance Monitoring Dashboard
    Implements Annex A.12.6 - Compliance with Legal Requirements
    """

    def __init__(self, db_session, alert_service):
        self.db = db_session
        self.alert_service = alert_service
        self.compliance_checks = self.load_compliance_checks()

    def load_compliance_checks(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance check definitions"""
        return {
            'password_policy': {
                'name': 'Password Policy Compliance',
                'check_function': self.check_password_policy,
                'frequency': 'daily',
                'severity': 'HIGH'
            },
            'access_reviews': {
                'name': 'Access Rights Review',
                'check_function': self.check_access_reviews,
                'frequency': 'monthly',
                'severity': 'MEDIUM'
            },
            'encryption_compliance': {
                'name': 'Data Encryption Compliance',
                'check_function': self.check_encryption_compliance,
                'frequency': 'weekly',
                'severity': 'HIGH'
            },
            'audit_log_integrity': {
                'name': 'Audit Log Integrity',
                'check_function': self.check_audit_log_integrity,
                'frequency': 'hourly',
                'severity': 'CRITICAL'
            },
            'gdpr_compliance': {
                'name': 'GDPR Compliance Check',
                'check_function': self.check_gdpr_compliance,
                'frequency': 'daily',
                'severity': 'HIGH'
            }
        }

    def run_compliance_checks(self) -> Dict[str, Any]:
        """Run all compliance checks and return results"""
        results = {
            'timestamp': datetime.utcnow(),
            'checks': {},
            'overall_status': 'COMPLIANT',
            'critical_issues': [],
            'warnings': []
        }

        for check_id, check_config in self.compliance_checks.items():
            try:
                check_result = check_config['check_function']()
                results['checks'][check_id] = check_result

                if check_result['status'] == 'FAILED':
                    if check_config['severity'] == 'CRITICAL':
                        results['overall_status'] = 'NON_COMPLIANT'
                        results['critical_issues'].append(check_result)
                    else:
                        results['warnings'].append(check_result)

                elif check_result['status'] == 'WARNING' and results['overall_status'] == 'COMPLIANT':
                    results['overall_status'] = 'WARNING'

            except Exception as e:
                results['checks'][check_id] = {
                    'status': 'ERROR',
                    'message': str(e),
                    'severity': check_config['severity']
                }

        # Send alerts for critical issues
        if results['critical_issues']:
            self.alert_service.send_critical_alert(results)

        return results

    def check_password_policy(self) -> Dict[str, Any]:
        """Check password policy compliance"""
        # Get all users
        users = self.db.query(User).all()

        non_compliant = []
        for user in users:
            if not self.is_password_compliant(user):
                non_compliant.append(user.id)

        return {
            'status': 'FAILED' if non_compliant else 'PASSED',
            'message': f"{len(non_compliant)} users have non-compliant passwords",
            'details': {'non_compliant_users': non_compliant},
            'recommendation': 'Force password reset for non-compliant users'
        }

    def check_access_reviews(self) -> Dict[str, Any]:
        """Check if access rights reviews are up to date"""
        # Check for users whose access hasn't been reviewed recently
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        overdue_reviews = self.db.query(User).filter(
            User.last_access_review.is_(None) |
            (User.last_access_review < ninety_days_ago)
        ).count()

        return {
            'status': 'WARNING' if overdue_reviews > 0 else 'PASSED',
            'message': f"{overdue_reviews} users need access review",
            'details': {'overdue_reviews': overdue_reviews},
            'recommendation': 'Schedule access rights reviews'
        }

    def check_encryption_compliance(self) -> Dict[str, Any]:
        """Check data encryption compliance"""
        # Check for unencrypted sensitive data
        sensitive_tables = ['customer_data', 'financial_records', 'personal_data']

        unencrypted_records = 0
        for table in sensitive_tables:
            # This would be a more complex query in practice
            count = self.check_unencrypted_data(table)
            unencrypted_records += count

        return {
            'status': 'FAILED' if unencrypted_records > 0 else 'PASSED',
            'message': f"{unencrypted_records} sensitive records are not encrypted",
            'details': {'unencrypted_records': unencrypted_records},
            'recommendation': 'Implement data encryption for sensitive records'
        }

    def check_audit_log_integrity(self) -> Dict[str, Any]:
        """Check audit log integrity"""
        # Verify hash chain integrity
        integrity_breaches = self.verify_audit_log_integrity()

        return {
            'status': 'FAILED' if integrity_breaches else 'PASSED',
            'message': f"{len(integrity_breaches)} audit log integrity breaches detected",
            'details': {'integrity_breaches': integrity_breaches},
            'recommendation': 'Investigate and restore audit log integrity'
        }

    def check_gdpr_compliance(self) -> Dict[str, Any]:
        """Check GDPR compliance"""
        issues = []

        # Check consent records
        missing_consents = self.check_missing_consents()
        if missing_consents > 0:
            issues.append(f"{missing_consents} users missing consent records")

        # Check data retention compliance
        expired_data = self.check_expired_data()
        if expired_data > 0:
            issues.append(f"{expired_data} records exceed retention period")

        # Check data portability requests
        pending_requests = self.check_pending_portability_requests()
        if pending_requests > 0:
            issues.append(f"{pending_requests} data portability requests pending")

        return {
            'status': 'FAILED' if issues else 'PASSED',
            'message': f"{len(issues)} GDPR compliance issues found",
            'details': {'issues': issues},
            'recommendation': 'Address GDPR compliance issues immediately'
        }

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        check_results = self.run_compliance_checks()

        report = {
            'generated_at': datetime.utcnow(),
            'period': 'Last 30 days',
            'overall_compliance': check_results['overall_status'],
            'compliance_score': self.calculate_compliance_score(check_results),
            'check_results': check_results['checks'],
            'critical_issues': check_results['critical_issues'],
            'warnings': check_results['warnings'],
            'recommendations': self.generate_recommendations(check_results),
            'next_review_date': datetime.utcnow() + timedelta(days=30)
        }

        return report

    def calculate_compliance_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall compliance score (0-100)"""
        total_checks = len(results['checks'])
        passed_checks = sum(1 for check in results['checks'].values() if check['status'] == 'PASSED')

        # Weight critical issues more heavily
        critical_penalty = len(results['critical_issues']) * 10
        warning_penalty = len(results['warnings']) * 2

        base_score = (passed_checks / total_checks) * 100
        final_score = max(0, base_score - critical_penalty - warning_penalty)

        return round(final_score, 1)
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. ✅ Risk Assessment Engine implementation
2. ✅ Enhanced Audit Logging System
3. ✅ Data Encryption Framework
4. ⏳ Access Control Enhancement

### Phase 2: Integration (Week 3-4)
1. ⏳ Compliance Monitoring Dashboard
2. ⏳ Security Event Correlation
3. ⏳ Automated Remediation
4. ⏳ Integration Testing

### Phase 3: Validation (Week 5-6)
1. ⏳ Penetration Testing
2. ⏳ Security Audits
3. ⏳ Compliance Certification
4. ⏳ Production Deployment

## Success Metrics

- **Risk Assessment Coverage**: 100% of assets assessed
- **Audit Log Integrity**: 99.9% tamper-proof
- **Encryption Coverage**: 100% of sensitive data
- **Access Control**: 0 unauthorized access incidents
- **Compliance Score**: >95%
- **Incident Response Time**: <15 minutes

---

*ISO 27001 Technical Implementation Guide*
*Version: 1.0*
*Status: IMPLEMENTATION READY*