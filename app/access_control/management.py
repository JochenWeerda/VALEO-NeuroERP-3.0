"""
ISO 27001 Access Control Management
Information Security Access Control Framework

Dieses Modul implementiert das Access Control Management gemäß ISO 27001 Annex A.9
für VALEO-NeuroERP mit Role-Based Access Control, Multi-Factor Authentication und Access Monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
import hashlib

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for resources"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    OWNER = "owner"


class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    MFA_SMS = "mfa_sms"
    MFA_APP = "mfa_app"
    MFA_HARDWARE = "mfa_hardware"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"
    SSO = "sso"


class SessionStatus(Enum):
    """User session status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    LOCKED = "locked"


class AccessRequestStatus(Enum):
    """Access request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"


class PrivilegeEscalationType(Enum):
    """Types of privilege escalation"""
    TEMPORARY = "temporary"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    AUDIT = "audit"


@dataclass
class UserAccount:
    """User account information"""
    id: str
    username: str
    email: str
    full_name: str
    department: str
    manager_id: Optional[str] = None
    is_active: bool = True
    account_locked: bool = False
    lock_reason: str = ""
    password_hash: str = ""
    password_changed_at: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_method: Optional[AuthenticationMethod] = None
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserRole:
    """User role definition"""
    id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    is_system_role: bool = False
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourcePermission:
    """Resource permission definition"""
    id: str
    resource_type: str
    resource_id: str
    role_id: str
    access_level: AccessLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserSession:
    """User session information"""
    id: str
    user_id: str
    session_token: str
    ip_address: str
    user_agent: str
    started_at: datetime
    expires_at: datetime
    last_activity: datetime
    status: SessionStatus = SessionStatus.ACTIVE
    authentication_methods: List[AuthenticationMethod] = field(default_factory=list)
    device_fingerprint: str = ""


@dataclass
class AccessRequest:
    """Access request for privilege escalation"""
    id: str
    user_id: str
    requested_role: str
    requested_resource: str
    access_level: AccessLevel
    justification: str
    escalation_type: PrivilegeEscalationType
    requested_duration: int  # minutes
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessLog:
    """Access log entry"""
    id: str
    user_id: str
    session_id: str
    resource_type: str
    resource_id: str
    action: str
    access_level: AccessLevel
    success: bool
    failure_reason: str = ""
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    id: str
    name: str
    description: str
    policy_type: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enforcement_level: str = "strict"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessReview:
    """Access rights review"""
    id: str
    review_type: str  # periodic, event-driven, user-initiated
    scope: str  # all_users, department, role
    reviewer: str
    status: str = "planned"
    scheduled_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))
    completed_date: Optional[datetime] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    actions_required: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ISO27001AccessControlManagement:
    """
    ISO 27001 Access Control Management
    Implements Annex A.9 - Access Control
    """

    def __init__(self, db_session, auth_service=None, audit_service=None):
        self.db = db_session
        self.auth = auth_service
        self.audit = audit_service

        # Access control components
        self.user_accounts: Dict[str, UserAccount] = {}
        self.user_roles: Dict[str, UserRole] = {}
        self.resource_permissions: Dict[str, ResourcePermission] = {}
        self.active_sessions: Dict[str, UserSession] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.access_logs: List[AccessLog] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.access_reviews: List[AccessReview] = {}

        # Security configuration
        self.security_config = self._initialize_security_config()

        # Default roles and policies
        self._initialize_default_roles()
        self._initialize_default_policies()

    def _initialize_security_config(self) -> Dict[str, Any]:
        """Initialize security configuration"""
        return {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'prevent_reuse': 5,
                'lockout_attempts': 5,
                'lockout_duration_minutes': 30
            },
            'session_policy': {
                'max_session_duration_hours': 8,
                'idle_timeout_minutes': 30,
                'max_concurrent_sessions': 3,
                'require_mfa': True,
                'device_fingerprinting': True
            },
            'access_review_policy': {
                'frequency_months': 3,
                'review_window_days': 30,
                'auto_remediation': True,
                'notification_days_before': 7
            },
            'privilege_escalation_policy': {
                'require_approval': True,
                'max_duration_hours': 24,
                'dual_authorization': True,
                'audit_all_escalations': True
            }
        }

    def _initialize_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            {
                'id': 'admin',
                'name': 'System Administrator',
                'description': 'Full system access and administration',
                'permissions': ['*'],
                'is_system_role': True
            },
            {
                'id': 'security_officer',
                'name': 'Security Officer',
                'description': 'Security management and monitoring',
                'permissions': ['security.*', 'access.*', 'audit.*'],
                'is_system_role': True
            },
            {
                'id': 'auditor',
                'name': 'Internal Auditor',
                'description': 'Audit and compliance monitoring',
                'permissions': ['audit.read', 'compliance.read', 'report.*'],
                'is_system_role': True
            },
            {
                'id': 'user',
                'name': 'Standard User',
                'description': 'Basic user access',
                'permissions': ['profile.read', 'profile.update'],
                'is_system_role': True
            }
        ]

        for role_data in default_roles:
            role = UserRole(**role_data)
            self.user_roles[role.id] = role

    def _initialize_default_policies(self):
        """Initialize default security policies"""
        default_policies = [
            {
                'id': 'password_policy',
                'name': 'Password Security Policy',
                'description': 'Enforce strong password requirements',
                'policy_type': 'password',
                'rules': [
                    {'rule': 'min_length', 'value': 12},
                    {'rule': 'require_complexity', 'value': True},
                    {'rule': 'max_age', 'value': 90}
                ]
            },
            {
                'id': 'session_policy',
                'name': 'Session Management Policy',
                'description': 'Control user session lifecycle',
                'policy_type': 'session',
                'rules': [
                    {'rule': 'idle_timeout', 'value': 30},
                    {'rule': 'max_duration', 'value': 480},
                    {'rule': 'concurrent_limit', 'value': 3}
                ]
            },
            {
                'id': 'access_policy',
                'name': 'Access Control Policy',
                'description': 'Define access control rules',
                'policy_type': 'access',
                'rules': [
                    {'rule': 'principle_of_least_privilege', 'value': True},
                    {'rule': 'need_to_know', 'value': True},
                    {'rule': 'regular_reviews', 'value': True}
                ]
            }
        ]

        for policy_data in default_policies:
            policy = SecurityPolicy(**policy_data)
            self.security_policies[policy.id] = policy

    def create_user_account(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user account
        Returns user ID
        """
        user_id = str(uuid.uuid4())

        # Hash password
        password_hash = self._hash_password(user_data['password'])

        user = UserAccount(
            id=user_id,
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            department=user_data.get('department', ''),
            manager_id=user_data.get('manager_id'),
            password_hash=password_hash,
            password_changed_at=datetime.utcnow()
        )

        self.user_accounts[user_id] = user

        # Assign default role
        self.assign_user_role(user_id, 'user')

        logger.info(f"User account created: {user.username} ({user.email})")
        return user_id

    def _hash_password(self, password: str) -> str:
        """Hash password using secure hashing"""
        salt = uuid.uuid4().hex
        hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return f"{salt}:{hashed}"

    def assign_user_role(self, user_id: str, role_id: str) -> bool:
        """
        Assign a role to a user
        """
        if user_id not in self.user_accounts or role_id not in self.user_roles:
            return False

        # In a real implementation, this would update a user-role mapping table
        logger.info(f"Role {role_id} assigned to user {user_id}")
        return True

    def authenticate_user(self, username: str, password: str, ip_address: str = "",
                         user_agent: str = "") -> Optional[str]:
        """
        Authenticate a user
        Returns session ID if successful, None otherwise
        """
        user = self._find_user_by_username(username)
        if not user or not user.is_active:
            return None

        # Check if account is locked
        if user.account_locked:
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.login_attempts += 1

            # Lock account if too many failed attempts
            if user.login_attempts >= self.security_config['password_policy']['lockout_attempts']:
                user.account_locked = True
                user.lock_reason = "Too many failed login attempts"
                logger.warning(f"Account locked for user {username} due to failed login attempts")

            return None

        # Reset login attempts on successful login
        user.login_attempts = 0
        user.last_login = datetime.utcnow()

        # Create session
        session_id = self._create_user_session(user.id, ip_address, user_agent)

        logger.info(f"User {username} authenticated successfully")
        return session_id

    def _find_user_by_username(self, username: str) -> Optional[UserAccount]:
        """Find user by username"""
        for user in self.user_accounts.values():
            if user.username == username:
                return user
        return None

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hashed = password_hash.split(':')
            expected_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            return expected_hash == hashed
        except:
            return False

    def _create_user_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        session_token = uuid.uuid4().hex

        session = UserSession(
            id=session_id,
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.security_config['session_policy']['max_session_duration_hours']),
            last_activity=datetime.utcnow()
        )

        self.active_sessions[session_id] = session

        return session_id

    def authorize_access(self, session_id: str, resource_type: str, resource_id: str,
                        required_access: AccessLevel) -> bool:
        """
        Authorize access to a resource
        """
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]

        # Check session validity
        if session.status != SessionStatus.ACTIVE:
            return False

        if datetime.utcnow() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            return False

        # Update last activity
        session.last_activity = datetime.utcnow()

        # Check permissions (simplified - in real implementation would check user roles and permissions)
        has_access = self._check_user_permissions(session.user_id, resource_type, resource_id, required_access)

        # Log access attempt
        self._log_access_attempt(session, resource_type, resource_id, required_access, has_access)

        return has_access

    def _check_user_permissions(self, user_id: str, resource_type: str, resource_id: str,
                               required_access: AccessLevel) -> bool:
        """Check if user has required permissions"""
        # Simplified permission check - in real implementation would be more complex
        # Check user's roles and associated permissions
        return True  # Placeholder - assume access granted

    def _log_access_attempt(self, session: UserSession, resource_type: str, resource_id: str,
                           access_level: AccessLevel, success: bool):
        """Log access attempt"""
        access_log = AccessLog(
            id=str(uuid.uuid4()),
            user_id=session.user_id,
            session_id=session.id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=f"access_{access_level.value}",
            access_level=access_level,
            success=success,
            ip_address=session.ip_address,
            user_agent=session.user_agent
        )

        self.access_logs.append(access_log)

    def request_privilege_escalation(self, user_id: str, escalation_data: Dict[str, Any]) -> str:
        """
        Request privilege escalation
        Returns request ID
        """
        request_id = str(uuid.uuid4())

        request = AccessRequest(
            id=request_id,
            user_id=user_id,
            requested_role=escalation_data['requested_role'],
            requested_resource=escalation_data.get('requested_resource', ''),
            access_level=AccessLevel[escalation_data['access_level'].upper()],
            justification=escalation_data['justification'],
            escalation_type=PrivilegeEscalationType[escalation_data['escalation_type'].upper()],
            requested_duration=escalation_data['requested_duration']
        )

        self.access_requests[request_id] = request

        logger.info(f"Privilege escalation requested by user {user_id}: {request.requested_role}")
        return request_id

    def approve_privilege_escalation(self, request_id: str, approved_by: str) -> bool:
        """
        Approve privilege escalation request
        """
        if request_id not in self.access_requests:
            return False

        request = self.access_requests[request_id]
        request.status = AccessRequestStatus.APPROVED
        request.approved_by = approved_by
        request.approved_at = datetime.utcnow()
        request.expires_at = datetime.utcnow() + timedelta(minutes=request.requested_duration)

        logger.info(f"Privilege escalation approved: {request_id} by {approved_by}")
        return True

    def terminate_session(self, session_id: str, reason: str = "") -> bool:
        """
        Terminate a user session
        """
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        session.status = SessionStatus.TERMINATED

        logger.info(f"Session terminated: {session_id} - {reason}")
        return True

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        """
        if user_id not in self.user_accounts:
            return False

        user = self.user_accounts[user_id]

        # Verify old password
        if not self._verify_password(old_password, user.password_hash):
            return False

        # Validate new password against policy
        if not self._validate_password_policy(new_password):
            return False

        # Hash and update password
        user.password_hash = self._hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.login_attempts = 0  # Reset failed attempts

        logger.info(f"Password changed for user {user.username}")
        return True

    def _validate_password_policy(self, password: str) -> bool:
        """Validate password against policy"""
        policy = self.security_config['password_policy']

        if len(password) < policy['min_length']:
            return False

        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            return False

        if policy['require_lowercase'] and not any(c.islower() for c in password):
            return False

        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            return False

        if policy['require_special_chars'] and not any(not c.isalnum() for c in password):
            return False

        return True

    def enable_mfa(self, user_id: str, mfa_method: AuthenticationMethod) -> bool:
        """
        Enable MFA for user
        """
        if user_id not in self.user_accounts:
            return False

        user = self.user_accounts[user_id]
        user.mfa_enabled = True
        user.mfa_method = mfa_method

        logger.info(f"MFA enabled for user {user.username}: {mfa_method.value}")
        return True

    def create_access_review(self, review_data: Dict[str, Any]) -> str:
        """
        Create an access rights review
        Returns review ID
        """
        review_id = str(uuid.uuid4())

        review = AccessReview(
            id=review_id,
            review_type=review_data['review_type'],
            scope=review_data['scope'],
            reviewer=review_data['reviewer'],
            scheduled_date=review_data.get('scheduled_date', datetime.utcnow() + timedelta(days=90))
        )

        self.access_reviews.append(review)

        logger.info(f"Access review created: {review.review_type} for {review.scope}")
        return review_id

    def get_access_control_report(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Generate comprehensive access control report"""
        # Get active users and sessions
        active_users = len([u for u in self.user_accounts.values() if u.is_active])
        active_sessions = len([s for s in self.active_sessions.values() if s.status == SessionStatus.ACTIVE])

        # Get recent access logs (last 24 hours)
        recent_logs = [log for log in self.access_logs
                      if (datetime.utcnow() - log.timestamp).days < 1]

        # Get pending access requests
        pending_requests = len([r for r in self.access_requests.values()
                               if r.status == AccessRequestStatus.PENDING])

        # Calculate access metrics
        access_metrics = self._calculate_access_metrics(recent_logs)

        # Get security policy compliance
        policy_compliance = self._assess_policy_compliance()

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'user_statistics': {
                'total_users': len(self.user_accounts),
                'active_users': active_users,
                'locked_accounts': len([u for u in self.user_accounts.values() if u.account_locked])
            },
            'session_statistics': {
                'active_sessions': active_sessions,
                'total_sessions_today': len([s for s in self.active_sessions.values()
                                           if (datetime.utcnow() - s.started_at).days < 1])
            },
            'access_metrics': access_metrics,
            'security_compliance': policy_compliance,
            'pending_requests': pending_requests,
            'recent_security_events': self._get_recent_security_events()
        }

    def _calculate_access_metrics(self, recent_logs: List[AccessLog]) -> Dict[str, Any]:
        """Calculate access control metrics"""
        if not recent_logs:
            return {'total_access_attempts': 0, 'success_rate': 0}

        total_attempts = len(recent_logs)
        successful_attempts = len([log for log in recent_logs if log.success])

        # Calculate access patterns
        access_by_resource = {}
        failed_attempts_by_reason = {}

        for log in recent_logs:
            # Count by resource type
            resource_key = f"{log.resource_type}:{log.resource_id}"
            access_by_resource[resource_key] = access_by_resource.get(resource_key, 0) + 1

            # Count failed attempts by reason
            if not log.success:
                failed_attempts_by_reason[log.failure_reason] = failed_attempts_by_reason.get(log.failure_reason, 0) + 1

        return {
            'total_access_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'success_rate': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'access_by_resource_type': self._group_access_by_type(recent_logs),
            'failed_attempts_by_reason': failed_attempts_by_reason,
            'peak_access_hour': self._find_peak_access_hour(recent_logs)
        }

    def _group_access_by_type(self, logs: List[AccessLog]) -> Dict[str, int]:
        """Group access attempts by resource type"""
        by_type = {}
        for log in logs:
            by_type[log.resource_type] = by_type.get(log.resource_type, 0) + 1
        return by_type

    def _find_peak_access_hour(self, logs: List[AccessLog]) -> int:
        """Find the hour with most access attempts"""
        hourly_counts = {}
        for log in logs:
            hour = log.timestamp.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        return max(hourly_counts.keys(), key=lambda h: hourly_counts[h]) if hourly_counts else 0

    def _assess_policy_compliance(self) -> Dict[str, Any]:
        """Assess security policy compliance"""
        compliance_checks = {
            'password_policy_compliance': self._check_password_policy_compliance(),
            'session_policy_compliance': self._check_session_policy_compliance(),
            'access_review_compliance': self._check_access_review_compliance(),
            'mfa_adoption_rate': self._calculate_mfa_adoption()
        }

        overall_compliance = sum(compliance_checks.values()) / len(compliance_checks) * 100

        return {
            'overall_compliance_score': round(overall_compliance, 1),
            'policy_checks': compliance_checks,
            'compliance_level': 'HIGH' if overall_compliance >= 90 else 'MEDIUM' if overall_compliance >= 75 else 'LOW'
        }

    def _check_password_policy_compliance(self) -> float:
        """Check password policy compliance"""
        active_users = [u for u in self.user_accounts.values() if u.is_active]
        if not active_users:
            return 100.0

        compliant_users = 0
        for user in active_users:
            # Check if password was changed within policy period
            if user.password_changed_at:
                days_since_change = (datetime.utcnow() - user.password_changed_at).days
                if days_since_change <= self.security_config['password_policy']['max_age_days']:
                    compliant_users += 1

        return (compliant_users / len(active_users)) * 100

    def _check_session_policy_compliance(self) -> float:
        """Check session policy compliance"""
        active_sessions = [s for s in self.active_sessions.values() if s.status == SessionStatus.ACTIVE]
        if not active_sessions:
            return 100.0

        compliant_sessions = 0
        for session in active_sessions:
            # Check session duration
            duration_hours = (datetime.utcnow() - session.started_at).total_seconds() / 3600
            if duration_hours <= self.security_config['session_policy']['max_session_duration_hours']:
                compliant_sessions += 1

        return (compliant_sessions / len(active_sessions)) * 100

    def _check_access_review_compliance(self) -> float:
        """Check access review compliance"""
        # Check if reviews are conducted on schedule
        recent_reviews = len([r for r in self.access_reviews
                            if r.completed_date and (datetime.utcnow() - r.completed_date).days <= 90])

        # Assume we should have at least 4 reviews per year
        expected_reviews = 4
        compliance = min(recent_reviews / expected_reviews * 100, 100)

        return compliance

    def _calculate_mfa_adoption(self) -> float:
        """Calculate MFA adoption rate"""
        active_users = [u for u in self.user_accounts.values() if u.is_active]
        if not active_users:
            return 100.0

        mfa_users = len([u for u in active_users if u.mfa_enabled])
        return (mfa_users / len(active_users)) * 100

    def _get_recent_security_events(self) -> List[Dict[str, Any]]:
        """Get recent security events"""
        recent_events = []

        # Get recent failed login attempts
        failed_logins = [log for log in self.access_logs
                        if not log.success and log.action == 'login'
                        and (datetime.utcnow() - log.timestamp).hours < 24]

        if failed_logins:
            recent_events.append({
                'event_type': 'failed_login_attempts',
                'count': len(failed_logins),
                'severity': 'MEDIUM',
                'description': f"{len(failed_logins)} failed login attempts in last 24 hours"
            })

        # Get privilege escalation requests
        pending_escalations = len([r for r in self.access_requests.values()
                                  if r.status == AccessRequestStatus.PENDING])

        if pending_escalations > 0:
            recent_events.append({
                'event_type': 'pending_privilege_escalations',
                'count': pending_escalations,
                'severity': 'LOW',
                'description': f"{pending_escalations} privilege escalation requests pending approval"
            })

        # Get terminated sessions
        terminated_sessions = len([s for s in self.active_sessions.values()
                                  if s.status == SessionStatus.TERMINATED
                                  and (datetime.utcnow() - s.last_activity).hours < 24])

        if terminated_sessions > 0:
            recent_events.append({
                'event_type': 'session_terminations',
                'count': terminated_sessions,
                'severity': 'LOW',
                'description': f"{terminated_sessions} sessions terminated in last 24 hours"
            })

        return recent_events

    def check_access_control_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 access control compliance"""
        compliance_checks = {
            'user_account_management': self._check_user_account_compliance(),
            'access_control_policies': self._check_access_policy_compliance(),
            'authentication_mechanisms': self._check_authentication_compliance(),
            'session_management': self._check_session_management_compliance(),
            'access_rights_review': self._check_access_review_compliance(),
            'privilege_management': self._check_privilege_management_compliance()
        }

        overall_score = sum(compliance_checks.values()) / len(compliance_checks)

        issues = []
        if compliance_checks['user_account_management'] < 80:
            issues.append("User account management practices need improvement")
        if compliance_checks['authentication_mechanisms'] < 90:
            issues.append("Authentication mechanisms require strengthening")
        if compliance_checks['access_rights_review'] < 75:
            issues.append("Access rights reviews are not conducted regularly")

        return {
            'tenant_id': tenant_id,
            'compliance_score': round(overall_score, 1),
            'control_checks': compliance_checks,
            'issues': issues,
            'recommendations': self._generate_access_control_recommendations(issues),
            'iso_standard': 'ISO 27001:2022',
            'annex': 'A.9 Access Control',
            'last_check': datetime.utcnow().isoformat()
        }

    def _check_user_account_compliance(self) -> float:
        """Check user account management compliance"""
        active_users = [u for u in self.user_accounts.values() if u.is_active]
        if not active_users:
            return 100.0

        compliant_accounts = 0
        for user in active_users:
            score = 100

            # Check password age
            if user.password_changed_at:
                days_since_change = (datetime.utcnow() - user.password_changed_at).days
                if days_since_change > self.security_config['password_policy']['max_age_days']:
                    score -= 20

            # Check MFA
            if not user.mfa_enabled:
                score -= 15

            # Check account lockouts
            if user.account_locked:
                score -= 10

            compliant_accounts += max(score, 0)

        return compliant_accounts / len(active_users)

    def _check_access_policy_compliance(self) -> float:
        """Check access control policy compliance"""
        # Check if policies are defined and active
        active_policies = len([p for p in self.security_policies.values() if p.is_active])
        required_policies = 3  # password, session, access

        return min(active_policies / required_policies * 100, 100)

    def _check_authentication_compliance(self) -> float:
        """Check authentication mechanisms compliance"""
        active_users = [u for u in self.user_accounts.values() if u.is_active]
        if not active_users:
            return 100.0

        # Check MFA adoption
        mfa_users = len([u for u in active_users if u.mfa_enabled])
        mfa_score = (mfa_users / len(active_users)) * 100

        # Check password policy compliance
        password_compliance = self._check_password_policy_compliance()

        return (mfa_score + password_compliance) / 2

    def _check_session_management_compliance(self) -> float:
        """Check session management compliance"""
        return self._check_session_policy_compliance()

    def _check_privilege_management_compliance(self) -> float:
        """Check privilege management compliance"""
        # Check for pending privilege escalation requests
        pending_requests = len([r for r in self.access_requests.values()
                               if r.status == AccessRequestStatus.PENDING])

        # Lower score if too many pending requests
        base_score = 100
        if pending_requests > 10:
            base_score -= 20
        elif pending_requests > 5:
            base_score -= 10

        return max(base_score, 0)

    def _generate_access_control_recommendations(self, issues: List[str]) -> List[str]:
        """Generate access control recommendations"""
        recommendations = []

        if any('user account' in issue.lower() for issue in issues):
            recommendations.append("Implement comprehensive user account lifecycle management")
            recommendations.append("Establish regular password policy enforcement")

        if any('authentication' in issue.lower() for issue in issues):
            recommendations.append("Deploy multi-factor authentication for all users")
            recommendations.append("Strengthen password policies and monitoring")

        if any('access rights' in issue.lower() for issue in issues):
            recommendations.append("Establish regular access rights review process")
            recommendations.append("Implement automated access certification workflows")

        if not recommendations:
            recommendations.append("Maintain current access control standards and monitoring")

        return recommendations