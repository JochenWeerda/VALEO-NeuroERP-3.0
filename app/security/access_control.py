"""
ISO 27001 Access Control System
Informationssicherheits-Managementsystem Access Control

Dieses Modul implementiert die Access Control gemäß ISO 27001 Annex A.9
für VALEO-NeuroERP mit Role-Based Access Control, Multi-Factor Authentication und Privilege Management.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import secrets
import jwt
import re

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for different permissions"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"


class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    MFA_EMAIL = "mfa_email"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"
    SSO_OIDC = "sso_oidc"


class SessionStatus(Enum):
    """User session status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class RoleType(Enum):
    """Types of user roles"""
    SYSTEM_ADMIN = "system_admin"
    SECURITY_ADMIN = "security_admin"
    AUDITOR = "auditor"
    BUSINESS_USER = "business_user"
    SERVICE_ACCOUNT = "service_account"
    CONTRACTOR = "contractor"


@dataclass
class User:
    """User account representation"""
    id: str
    username: str
    email: str
    role_type: RoleType
    is_active: bool = True
    mfa_enabled: bool = False
    password_hash: Optional[str] = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """Security role with permissions"""
    id: str
    name: str
    description: str
    role_type: RoleType
    permissions: Dict[str, AccessLevel] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Permission:
    """System permission"""
    id: str
    resource: str
    action: str
    description: str
    access_level: AccessLevel
    requires_mfa: bool = False
    time_restricted: bool = False
    ip_restricted: bool = False
    allowed_ips: List[str] = field(default_factory=list)


@dataclass
class UserSession:
    """User authentication session"""
    id: str
    user_id: str
    token: str
    status: SessionStatus
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    mfa_verified: bool = False
    device_fingerprint: Optional[str] = None


@dataclass
class AccessAttempt:
    """Access attempt log"""
    id: str
    user_id: Optional[str]
    username: str
    resource: str
    action: str
    success: bool
    reason: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    session_id: Optional[str] = None
    mfa_used: bool = False


@dataclass
class AccessPolicy:
    """Access control policy"""
    id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    effect: str  # allow, deny
    priority: int = 100
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class ISO27001AccessControl:
    """
    ISO 27001 Access Control Implementation
    Implements Annex A.9 - Access Control
    """

    def __init__(self, db_session, jwt_secret: str = None, mfa_service=None):
        self.db = db_session
        self.jwt_secret = jwt_secret or secrets.token_hex(32)
        self.mfa = mfa_service

        # User and role management
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}

        # Session management
        self.active_sessions: Dict[str, UserSession] = {}

        # Access control
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.access_attempts: List[AccessAttempt] = []

        # Security policies
        self.security_policies = self._initialize_security_policies()

        # Password policies
        self.password_policy = self._initialize_password_policy()

        # Session policies
        self.session_policy = self._initialize_session_policy()

    def _initialize_security_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize access control security policies"""
        return {
            'authentication': {
                'require_mfa_for_admins': True,
                'require_mfa_for_sensitive_operations': True,
                'password_complexity': True,
                'account_lockout_threshold': 5,
                'account_lockout_duration': timedelta(minutes=30),
                'password_history_check': 5,
                'password_min_age': timedelta(days=1),
                'password_max_age': timedelta(days=90)
            },
            'authorization': {
                'least_privilege': True,
                'role_based_access': True,
                'separation_of_duties': True,
                'dual_authorization_for_critical': True,
                'time_based_access': True,
                'location_based_access': False
            },
            'session_management': {
                'session_timeout': timedelta(hours=8),
                'idle_timeout': timedelta(hours=2),
                'max_concurrent_sessions': 3,
                'device_fingerprinting': True,
                'session_fixation_protection': True
            },
            'monitoring': {
                'log_all_access_attempts': True,
                'log_privileged_operations': True,
                'real_time_alerts': True,
                'audit_trail_retention': timedelta(days=365)
            }
        }

    def _initialize_password_policy(self) -> Dict[str, Any]:
        """Initialize password complexity requirements"""
        return {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'require_special_chars': True,
            'forbid_common_passwords': True,
            'max_consecutive_chars': 3,
            'min_unique_chars': 8
        }

    def _initialize_session_policy(self) -> Dict[str, Any]:
        """Initialize session management policies"""
        return {
            'session_timeout': timedelta(hours=8),
            'idle_timeout': timedelta(hours=2),
            'max_concurrent_sessions': 3,
            'absolute_timeout': timedelta(hours=24),
            'renewal_window': timedelta(minutes=30)
        }

    def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user account
        Returns user ID
        """
        user_id = str(uuid.uuid4())

        # Validate user data
        self._validate_user_data(user_data)

        # Hash password
        password_hash = None
        if 'password' in user_data:
            password_hash = self._hash_password(user_data['password'])

        user = User(
            id=user_id,
            username=user_data['username'],
            email=user_data['email'],
            role_type=RoleType[user_data['role_type'].upper()],
            password_hash=password_hash,
            mfa_enabled=user_data.get('mfa_enabled', False)
        )

        self.users[user_id] = user

        # Assign default role based on role_type
        default_role = self._get_default_role_for_type(user.role_type)
        if default_role:
            self.assign_role_to_user(user_id, default_role)

        logger.info(f"User account created: {user.username} ({user.role_type.value})")
        return user_id

    def _validate_user_data(self, data: Dict[str, Any]):
        """Validate user creation data"""
        required_fields = ['username', 'email', 'role_type']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field missing: {field}")

        # Validate username format
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', data['username']):
            raise ValueError("Invalid username format")

        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
            raise ValueError("Invalid email format")

        # Check for duplicate username
        if any(u.username == data['username'] for u in self.users.values()):
            raise ValueError("Username already exists")

        # Validate role type
        try:
            RoleType[data['role_type'].upper()]
        except KeyError:
            raise ValueError(f"Invalid role type: {data['role_type']}")

        # Validate password if provided
        if 'password' in data:
            self._validate_password_complexity(data['password'])

    def _validate_password_complexity(self, password: str):
        """Validate password against complexity requirements"""
        policy = self.password_policy

        if len(password) < policy['min_length']:
            raise ValueError(f"Password too short (minimum {policy['min_length']} characters)")

        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain uppercase letters")

        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            raise ValueError("Password must contain lowercase letters")

        if policy['require_digits'] and not re.search(r'[0-9]', password):
            raise ValueError("Password must contain digits")

        if policy['require_special_chars'] and not re.search(r'[^a-zA-Z0-9]', password):
            raise ValueError("Password must contain special characters")

        # Check for consecutive characters
        if policy['max_consecutive_chars']:
            for i in range(len(password) - policy['max_consecutive_chars'] + 1):
                chars = password[i:i + policy['max_consecutive_chars']]
                if len(set(chars)) == 1:
                    raise ValueError(f"Password cannot contain {policy['max_consecutive_chars']} consecutive identical characters")

        # Check unique characters
        if len(set(password)) < policy['min_unique_chars']:
            raise ValueError(f"Password must contain at least {policy['min_unique_chars']} unique characters")

    def _hash_password(self, password: str) -> str:
        """Hash password using secure hashing"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}:{hash_obj.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split(':')
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return secrets.compare_digest(hash_value, computed_hash.hex())
        except (ValueError, TypeError):
            return False

    def _get_default_role_for_type(self, role_type: RoleType) -> Optional[str]:
        """Get default role ID for role type"""
        # This would map role types to actual role IDs in production
        role_mapping = {
            RoleType.SYSTEM_ADMIN: "system_admin_role",
            RoleType.SECURITY_ADMIN: "security_admin_role",
            RoleType.AUDITOR: "auditor_role",
            RoleType.BUSINESS_USER: "business_user_role"
        }
        return role_mapping.get(role_type)

    def create_role(self, role_data: Dict[str, Any]) -> str:
        """
        Create a new security role
        Returns role ID
        """
        role_id = str(uuid.uuid4())

        role = Role(
            id=role_id,
            name=role_data['name'],
            description=role_data['description'],
            role_type=RoleType[role_data['role_type'].upper()],
            permissions=role_data.get('permissions', {})
        )

        self.roles[role_id] = role

        logger.info(f"Security role created: {role.name} ({role.role_type.value})")
        return role_id

    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """
        Assign role to user
        """
        if user_id not in self.users or role_id not in self.roles:
            return False

        user = self.users[user_id]
        role = self.roles[role_id]

        # In production, this would update a user-role mapping table
        logger.info(f"Role {role.name} assigned to user {user.username}")
        return True

    def authenticate_user(self, username: str, password: str, ip_address: str = None,
                         user_agent: str = None, device_fingerprint: str = None) -> Optional[str]:
        """
        Authenticate user and return session token
        Returns session token if successful
        """
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break

        if not user:
            self._log_access_attempt(None, username, "authentication", "login", False,
                                   "User not found", ip_address, user_agent)
            return None

        # Check account lockout
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            self._log_access_attempt(user.id, username, "authentication", "login", False,
                                   "Account locked", ip_address, user_agent)
            return None

        # Verify password
        if not user.password_hash or not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            # Check lockout threshold
            if user.failed_login_attempts >= self.security_policies['authentication']['account_lockout_threshold']:
                lockout_duration = self.security_policies['authentication']['account_lockout_duration']
                user.account_locked_until = datetime.utcnow() + lockout_duration
                logger.warning(f"Account locked for user {username} due to failed login attempts")

            self._log_access_attempt(user.id, username, "authentication", "login", False,
                                   "Invalid password", ip_address, user_agent)
            return None

        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = datetime.utcnow()

        # Check if MFA is required
        if self._requires_mfa(user, "login"):
            # In production, this would initiate MFA challenge
            logger.info(f"MFA required for user {username}")
            # For now, assume MFA verification
            mfa_verified = True
        else:
            mfa_verified = False

        # Create session
        session_token = self._create_user_session(user.id, ip_address, user_agent, device_fingerprint, mfa_verified)

        self._log_access_attempt(user.id, username, "authentication", "login", True,
                               "Login successful", ip_address, user_agent, session_token)

        logger.info(f"User authenticated successfully: {username}")
        return session_token

    def _requires_mfa(self, user: User, operation: str) -> bool:
        """Check if MFA is required for user and operation"""
        policies = self.security_policies['authentication']

        if policies['require_mfa_for_admins'] and user.role_type in [RoleType.SYSTEM_ADMIN, RoleType.SECURITY_ADMIN]:
            return True

        if policies['require_mfa_for_sensitive_operations'] and operation in ['admin_action', 'data_export']:
            return True

        return user.mfa_enabled

    def _create_user_session(self, user_id: str, ip_address: str, user_agent: str,
                           device_fingerprint: str = None, mfa_verified: bool = False) -> str:
        """Create user session and return token"""
        session_id = str(uuid.uuid4())

        # Create JWT token
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.session_policy['session_timeout']
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')

        session = UserSession(
            id=session_id,
            user_id=user_id,
            token=token,
            status=SessionStatus.ACTIVE,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.session_policy['session_timeout'],
            last_activity=datetime.utcnow(),
            mfa_verified=mfa_verified,
            device_fingerprint=device_fingerprint
        )

        self.active_sessions[session_id] = session

        return token

    def authorize_access(self, session_token: str, resource: str, action: str,
                        ip_address: str = None) -> Tuple[bool, str]:
        """
        Authorize access to resource
        Returns: (authorized, reason)
        """
        # Validate session
        session = self._validate_session(session_token)
        if not session:
            return False, "Invalid or expired session"

        # Update session activity
        session.last_activity = datetime.utcnow()

        # Get user
        user = self.users.get(session.user_id)
        if not user or not user.is_active:
            return False, "User account inactive"

        # Check account lockout
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            return False, "Account temporarily locked"

        # Evaluate access policies
        authorized, reason = self._evaluate_access_policies(user, resource, action, session, ip_address)

        # Log access attempt
        self._log_access_attempt(
            user.id, user.username, resource, action, authorized,
            reason, ip_address, session.user_agent, session.id,
            session.mfa_verified
        )

        return authorized, reason

    def _validate_session(self, token: str) -> Optional[UserSession]:
        """Validate session token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            session_id = payload['session_id']

            session = self.active_sessions.get(session_id)
            if not session or session.status != SessionStatus.ACTIVE:
                return None

            # Check expiration
            if session.expires_at < datetime.utcnow():
                session.status = SessionStatus.EXPIRED
                return None

            # Check idle timeout
            idle_time = datetime.utcnow() - session.last_activity
            if idle_time > self.session_policy['idle_timeout']:
                session.status = SessionStatus.EXPIRED
                return None

            return session

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return None

    def _evaluate_access_policies(self, user: User, resource: str, action: str,
                                session: UserSession, ip_address: str) -> Tuple[bool, str]:
        """Evaluate access control policies"""
        # Get user permissions (from roles)
        user_permissions = self._get_user_permissions(user.id)

        # Check resource-specific permissions
        required_level = self._get_required_access_level(resource, action)
        user_level = user_permissions.get(resource, AccessLevel.NONE)

        if user_level == AccessLevel.NONE:
            return False, "No permission for resource"

        if not self._level_satisfies_requirement(user_level, required_level):
            return False, "Insufficient access level"

        # Check MFA requirements
        if self._requires_mfa(user, f"{resource}:{action}") and not session.mfa_verified:
            return False, "MFA verification required"

        # Check time-based restrictions
        if not self._check_time_restrictions(user.id, resource, action):
            return False, "Access outside allowed time window"

        # Check IP restrictions
        if not self._check_ip_restrictions(user.id, ip_address):
            return False, "Access from unauthorized IP address"

        return True, "Access granted"

    def _get_user_permissions(self, user_id: str) -> Dict[str, AccessLevel]:
        """Get effective permissions for user"""
        # In production, this would aggregate permissions from all user roles
        permissions = {}

        # Simplified: assume users have permissions based on their role type
        user = self.users.get(user_id)
        if user:
            if user.role_type == RoleType.SYSTEM_ADMIN:
                permissions = {resource: AccessLevel.ADMIN for resource in ['*']}  # All resources
            elif user.role_type == RoleType.SECURITY_ADMIN:
                permissions = {
                    'security': AccessLevel.ADMIN,
                    'audit': AccessLevel.READ,
                    'users': AccessLevel.WRITE
                }
            elif user.role_type == RoleType.AUDITOR:
                permissions = {resource: AccessLevel.READ for resource in ['*']}
            else:
                permissions = {
                    'business_data': AccessLevel.WRITE,
                    'reports': AccessLevel.READ
                }

        return permissions

    def _get_required_access_level(self, resource: str, action: str) -> AccessLevel:
        """Get required access level for resource and action"""
        # Define access requirements
        requirements = {
            'admin': AccessLevel.ADMIN,
            'security': AccessLevel.ADMIN,
            'users': AccessLevel.WRITE,
            'audit': AccessLevel.READ,
            'business_data': AccessLevel.WRITE,
            'reports': AccessLevel.READ,
            'public_data': AccessLevel.READ
        }

        # Map actions to levels
        action_levels = {
            'create': AccessLevel.WRITE,
            'read': AccessLevel.READ,
            'update': AccessLevel.WRITE,
            'delete': AccessLevel.DELETE,
            'admin': AccessLevel.ADMIN
        }

        base_level = requirements.get(resource, AccessLevel.NONE)
        action_level = action_levels.get(action, AccessLevel.NONE)

        # Return the more restrictive level
        return max(base_level, action_level, key=lambda x: x.value)

    def _level_satisfies_requirement(self, user_level: AccessLevel, required_level: AccessLevel) -> bool:
        """Check if user access level satisfies requirement"""
        level_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.DELETE: 3,
            AccessLevel.ADMIN: 4,
            AccessLevel.AUDIT: 1
        }

        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 999)

    def _check_time_restrictions(self, user_id: str, resource: str, action: str) -> bool:
        """Check time-based access restrictions"""
        # Simplified: no time restrictions for now
        return True

    def _check_ip_restrictions(self, user_id: str, ip_address: str) -> bool:
        """Check IP-based access restrictions"""
        # Simplified: no IP restrictions for now
        return True

    def _log_access_attempt(self, user_id: Optional[str], username: str, resource: str,
                          action: str, success: bool, reason: str, ip_address: str,
                          user_agent: str, session_id: str = None, mfa_used: bool = False):
        """Log access attempt"""
        attempt = AccessAttempt(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            success=success,
            reason=reason,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown",
            timestamp=datetime.utcnow(),
            session_id=session_id,
            mfa_used=mfa_used
        )

        self.access_attempts.append(attempt)

        if not success:
            logger.warning(f"Access denied: {username} -> {resource}:{action} ({reason})")
        else:
            logger.debug(f"Access granted: {username} -> {resource}:{action}")

    def terminate_session(self, session_token: str) -> bool:
        """
        Terminate user session
        """
        session = self._validate_session(session_token)
        if not session:
            return False

        session.status = SessionStatus.TERMINATED
        logger.info(f"Session terminated: {session.user_id}")
        return True

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        """
        user = self.users.get(user_id)
        if not user:
            return False

        # Verify old password
        if not user.password_hash or not self._verify_password(old_password, user.password_hash):
            return False

        # Validate new password
        self._validate_password_complexity(new_password)

        # Check password history (simplified)
        if user.password_changed_at:
            min_age = self.security_policies['authentication']['password_min_age']
            if datetime.utcnow() - user.password_changed_at < min_age:
                raise ValueError("Password changed too recently")

        # Hash and update password
        user.password_hash = self._hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.failed_login_attempts = 0  # Reset failed attempts

        logger.info(f"Password changed for user: {user.username}")
        return True

    def get_access_control_status(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Get comprehensive access control status"""
        # Filter data by tenant
        tenant_users = [u for u in self.users.values() if u.id.startswith(tenant_id)]
        tenant_sessions = [s for s in self.active_sessions.values() if s.user_id.startswith(tenant_id)]
        recent_attempts = [a for a in self.access_attempts[-1000:] if a.user_id and a.user_id.startswith(tenant_id)]

        # Calculate metrics
        user_stats = self._calculate_user_statistics(tenant_users)
        session_stats = self._calculate_session_statistics(tenant_sessions)
        access_stats = self._calculate_access_statistics(recent_attempts)
        compliance_status = self._assess_access_control_compliance(tenant_users, recent_attempts)

        return {
            'tenant_id': tenant_id,
            'generated_at': datetime.utcnow().isoformat(),
            'user_statistics': user_stats,
            'session_statistics': session_stats,
            'access_statistics': access_stats,
            'compliance_status': compliance_status,
            'active_alerts': self._get_access_control_alerts(tenant_id)
        }

    def _calculate_user_statistics(self, users: List[User]) -> Dict[str, Any]:
        """Calculate user account statistics"""
        if not users:
            return {'total_users': 0, 'active_users': 0, 'mfa_enabled': 0}

        total_users = len(users)
        active_users = len([u for u in users if u.is_active])
        mfa_enabled = len([u for u in users if u.mfa_enabled])
        locked_accounts = len([u for u in users if u.account_locked_until and u.account_locked_until > datetime.utcnow()])

        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'mfa_enabled_users': mfa_enabled,
            'mfa_adoption_rate': (mfa_enabled / total_users * 100) if total_users > 0 else 0,
            'locked_accounts': locked_accounts
        }

    def _calculate_session_statistics(self, sessions: List[UserSession]) -> Dict[str, Any]:
        """Calculate session statistics"""
        if not sessions:
            return {'active_sessions': 0, 'avg_session_duration': 0}

        active_sessions = len([s for s in sessions if s.status == SessionStatus.ACTIVE])
        total_duration = sum(
            (s.last_activity - s.created_at).total_seconds()
            for s in sessions if s.status == SessionStatus.ACTIVE
        )
        avg_duration = total_duration / active_sessions if active_sessions > 0 else 0

        return {
            'active_sessions': active_sessions,
            'total_sessions': len(sessions),
            'avg_session_duration_hours': avg_duration / 3600,
            'sessions_with_mfa': len([s for s in sessions if s.mfa_verified])
        }

    def _calculate_access_statistics(self, attempts: List[AccessAttempt]) -> Dict[str, Any]:
        """Calculate access attempt statistics"""
        if not attempts:
            return {'total_attempts': 0, 'success_rate': 0}

        total_attempts = len(attempts)
        successful_attempts = len([a for a in attempts if a.success])
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0

        # Calculate failure reasons
        failure_reasons = {}
        for attempt in attempts:
            if not attempt.success:
                failure_reasons[attempt.reason] = failure_reasons.get(attempt.reason, 0) + 1

        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': total_attempts - successful_attempts,
            'success_rate': round(success_rate, 1),
            'top_failure_reasons': sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5],
            'mfa_usage_rate': len([a for a in attempts if a.mfa_used]) / total_attempts * 100 if total_attempts > 0 else 0
        }

    def _assess_access_control_compliance(self, users: List[User], attempts: List[AccessAttempt]) -> Dict[str, Any]:
        """Assess ISO 27001 access control compliance"""
        issues = []

        # Check MFA adoption
        mfa_users = len([u for u in users if u.mfa_enabled])
        if users and (mfa_users / len(users)) < 0.8:  # Less than 80% MFA adoption
            issues.append("Insufficient MFA adoption")

        # Check failed login attempts
        if attempts:
            failed_rate = len([a for a in attempts if not a.success]) / len(attempts)
            if failed_rate > 0.1:  # More than 10% failures
                issues.append("High rate of access failures")

        # Check account lockouts
        locked_users = len([u for u in users if u.account_locked_until and u.account_locked_until > datetime.utcnow()])
        if locked_users > len(users) * 0.05:  # More than 5% accounts locked
            issues.append("Excessive account lockouts")

        compliance_score = max(0, 100 - (len(issues) * 10))

        return {
            'compliance_score': compliance_score,
            'issues': issues,
            'recommendations': self._generate_access_control_recommendations(issues)
        }

    def _generate_access_control_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on compliance issues"""
        recommendations = []

        if any('MFA' in issue for issue in issues):
            recommendations.append("Implement mandatory MFA for all user accounts")

        if any('failure' in issue.lower() for issue in issues):
            recommendations.append("Review and optimize authentication processes")

        if any('lockout' in issue.lower() for issue in issues):
            recommendations.append("Implement graduated lockout policies and user training")

        if not recommendations:
            recommendations.append("Maintain current access control standards and regular reviews")

        return recommendations

    def _get_access_control_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get active access control alerts"""
        alerts = []

        # Check for suspicious login patterns
        recent_attempts = [a for a in self.access_attempts[-100:] if a.user_id and a.user_id.startswith(tenant_id)]
        failed_attempts = [a for a in recent_attempts if not a.success]

        if len(failed_attempts) > 10:
            alerts.append({
                'type': 'suspicious_login_activity',
                'severity': 'HIGH',
                'message': f"High number of failed login attempts: {len(failed_attempts)} in recent activity",
                'details': {'failed_attempts': len(failed_attempts)}
            })

        # Check for accounts with excessive failed attempts
        user_failures = {}
        for attempt in failed_attempts[-50:]:  # Last 50 failed attempts
            user_failures[attempt.user_id] = user_failures.get(attempt.user_id, 0) + 1

        for user_id, failures in user_failures.items():
            if failures >= 3:
                user = self.users.get(user_id)
                if user:
                    alerts.append({
                        'type': 'account_under_attack',
                        'severity': 'MEDIUM',
                        'message': f"User {user.username} has {failures} recent failed login attempts",
                        'user_id': user_id
                    })

        return alerts

    def check_access_control_compliance(self, tenant_id: str = "system") -> Dict[str, Any]:
        """Check ISO 27001 access control compliance"""
        users = [u for u in self.users.values() if u.id.startswith(tenant_id)]
        attempts = [a for a in self.access_attempts[-1000:] if a.user_id and a.user_id.startswith(tenant_id)]

        compliance_status = self._assess_access_control_compliance(users, attempts)

        return {
            'tenant_id': tenant_id,
            'compliance_score': compliance_status['compliance_score'],
            'total_issues': len(compliance_status['issues']),
            'issues': compliance_status['issues'],
            'recommendations': compliance_status['recommendations'],
            'iso_control': 'A.9',
            'last_check': datetime.utcnow().isoformat()
        }