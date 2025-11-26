"""
Settings for CRM Security & Compliance Service.
"""

import os
from typing import List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://valeo_dev:valeo_dev_2024!@postgres:5432/valeo_neuro_erp"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/11"

    # Elasticsearch for audit logs
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "crm_security"

    # Service
    SERVICE_NAME: str = "crm-security"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encryption
    ENCRYPTION_KEY: str = "dev-encryption-key-32-chars-long"
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"

    # SSL/TLS
    SSL_CERT_FILE: Optional[str] = None
    SSL_KEY_FILE: Optional[str] = None
    ENABLE_HTTPS: bool = False

    # Trusted hosts
    ALLOWED_HOSTS: List[str] = ["*"]

    # Tenant
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"

    # Audit logging
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    AUDIT_LOG_COMPRESSION: bool = True
    AUDIT_LOG_ENCRYPTION: bool = True

    # GDPR compliance
    GDPR_DATA_RETENTION_YEARS: int = 7
    GDPR_AUTO_DELETE: bool = True
    GDPR_CONSENT_REQUIRED: bool = True

    # Security monitoring
    SECURITY_ALERT_EMAILS: List[str] = ["security@company.com"]
    SECURITY_MAX_LOGIN_ATTEMPTS: int = 5
    SECURITY_LOCKOUT_DURATION_MINUTES: int = 30
    SECURITY_PASSWORD_MIN_LENGTH: int = 12
    SECURITY_PASSWORD_REQUIRE_UPPERCASE: bool = True
    SECURITY_PASSWORD_REQUIRE_LOWERCASE: bool = True
    SECURITY_PASSWORD_REQUIRE_NUMBERS: bool = True
    SECURITY_PASSWORD_REQUIRE_SYMBOLS: bool = True

    # Threat detection
    THREAT_DETECTION_ENABLED: bool = True
    THREAT_DETECTION_ANOMALY_THRESHOLD: float = 0.95
    THREAT_DETECTION_IP_BLACKLIST: List[str] = []
    THREAT_DETECTION_RATE_LIMIT_REQUESTS: int = 1000
    THREAT_DETECTION_RATE_LIMIT_WINDOW: int = 60  # seconds

    # Data masking
    DATA_MASKING_ENABLED: bool = True
    DATA_MASKING_PATTERNS: dict = {
        "email": "***@***.***",
        "phone": "***-***-****",
        "ssn": "***-**-****",
        "credit_card": "****-****-****-****"
    }

    # Compliance
    COMPLIANCE_AUTO_REPORTING: bool = True
    COMPLIANCE_REPORT_FREQUENCY: str = "monthly"  # daily, weekly, monthly
    COMPLIANCE_REPORT_RECIPIENTS: List[str] = ["compliance@company.com"]

    # Incident response
    INCIDENT_RESPONSE_AUTO_TRIGGER: bool = True
    INCIDENT_RESPONSE_ESCALATION_TIME_MINUTES: int = 15
    INCIDENT_RESPONSE_SEVERITY_LEVELS: dict = {
        "low": ["log", "notify"],
        "medium": ["log", "notify", "alert"],
        "high": ["log", "notify", "alert", "block"],
        "critical": ["log", "notify", "alert", "block", "escalate"]
    }

    # Key management
    KEY_ROTATION_ENABLED: bool = True
    KEY_ROTATION_INTERVAL_DAYS: int = 90
    KEY_BACKUP_ENABLED: bool = True

    # Monitoring
    MONITORING_ENABLED: bool = True
    MONITORING_METRICS_PORT: int = 9090
    MONITORING_HEALTH_CHECK_INTERVAL: int = 30

    # External integrations
    SIEM_ENABLED: bool = False
    SIEM_ENDPOINT: Optional[str] = None
    SIEM_API_KEY: Optional[str] = None

    VAULT_ENABLED: bool = False
    VAULT_URL: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator('ENCRYPTION_KEY')
    def validate_encryption_key(cls, v):
        if len(v) != 32:
            raise ValueError('Encryption key must be exactly 32 characters long')
        return v


settings = Settings()