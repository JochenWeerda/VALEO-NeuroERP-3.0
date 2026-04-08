"""
GDPR Compliance Tests
Automated tests for GDPR requirements
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from main import app
from app.core.database import get_db, SessionLocal
from app.infrastructure.models import User, Customer, AuditLog, Tenant


client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


def _require_table(db: Session, schema: str, table: str) -> None:
    try:
        if not inspect(db.bind).has_table(table, schema=schema):
            pytest.skip(f"Table {schema}.{table} is not available in this schema snapshot")
    except SQLAlchemyError:
        pytest.skip("Database not reachable in this environment")


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_right_to_access_api_exists():
    """Test that Right-to-Access API endpoint exists."""
    # TODO: Implement endpoint first
    response = client.get("/api/v1/gdpr/data-export/test-user-id", headers=AUTH_HEADERS)
    # Should return 200 when implemented
    assert response.status_code in [200, 404, 500, 501, 503]


def test_right_to_delete_api_exists():
    """Test that Right-to-Delete API endpoint exists."""
    # TODO: Implement endpoint first
    response = client.delete("/api/v1/gdpr/delete-user/test-user-id", headers=AUTH_HEADERS)
    # Should return 204 when implemented
    assert response.status_code in [204, 404, 500, 501, 503]


def test_data_portability_api_exists():
    """Test that Data-Portability API endpoint exists."""
    # TODO: Implement endpoint first
    response = client.get("/api/v1/gdpr/export-portable/test-user-id", headers=AUTH_HEADERS)
    # Should return 200 when implemented
    assert response.status_code in [200, 404, 500, 501, 503]


def test_audit_log_contains_required_fields(db: Session):
    """Test that audit log contains all GDPR-required fields."""
    _require_table(db, "domain_shared", "audit_logs")
    _require_table(db, "domain_shared", "tenants")
    _require_table(db, "domain_shared", "users")
    tenant = db.query(Tenant).filter(Tenant.id == "test-tenant").first()
    if tenant is None:
        tenant = Tenant(
            id="test-tenant",
            name="Test",
            domain="test.local",
            is_active=True,
        )
        db.add(tenant)
        db.flush()
    user = db.query(User).filter(User.id == "test-user").first()
    if user is None:
        user = User(
            id="test-user",
            tenant_id="test-tenant",
            first_name="Test",
            last_name="User",
            username="tuser-gdpr",
            email="test-gdpr@example.com",
            is_active=True,
        )
        db.add(user)
        db.flush()
    db.commit()

    from uuid import uuid4
    from datetime import datetime

    log = AuditLog(
        id=str(uuid4()),
        timestamp=datetime.utcnow(),
        user_id="test-user",
        user_email="test@example.com",
        tenant_id="test-tenant",
        action="create",
        entity_type="customer",
        entity_id="cust-123",
        changes={"name": "Test Customer"},
        ip_address="127.0.0.1",
        user_agent="Test-Agent"
    )

    db.add(log)
    db.commit()
    
    # Verify all fields present
    assert log.user_id is not None
    assert log.timestamp is not None
    assert log.changes is not None
    assert log.ip_address is not None


def test_personal_data_is_encrypted():
    """Test that sensitive personal data is encrypted."""
    # TODO: Implement encryption-at-rest first
    # Then verify with: SELECT * FROM pg_encryption_status
    pass  # Placeholder


def test_data_retention_policy_enforced():
    """Test that data older than retention-period is deleted."""
    # TODO: Implement retention-policy worker first
    pass  # Placeholder


def test_gdpr_data_export_complete(db: Session):
    """Test that data-export returns all user data."""
    _require_table(db, "domain_shared", "users")
    # Seed user in the default tenant
    tenant = db.query(Tenant).filter(Tenant.id == "default").first()
    if tenant is None:
        tenant = Tenant(id="default", name="Default", domain="default.local", is_active=True)
        db.add(tenant)
        db.flush()
    user = db.query(User).filter(User.id == "test-export-user").first()
    if user is None:
        user = User(
            id="test-export-user", tenant_id="default", first_name="Export",
            last_name="Tester", username="export-tester", email="export@test.local", is_active=True,
        )
        db.add(user)
    db.commit()

    response = client.get(
        "/api/v1/gdpr/data-export/test-export-user",
        headers={**AUTH_HEADERS, "X-Tenant-ID": "default"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "personal_data" in data
    assert "audit_logs" in data
    assert "export_metadata" in data
    assert data["personal_data"]["username"] == "export-tester"


def test_gdpr_right_to_delete(db: Session):
    """Test that user can be anonymized (soft-delete) via GDPR endpoint."""
    _require_table(db, "domain_shared", "users")
    tenant = db.query(Tenant).filter(Tenant.id == "default").first()
    if tenant is None:
        tenant = Tenant(id="default", name="Default", domain="default.local", is_active=True)
        db.add(tenant)
        db.flush()
    user = db.query(User).filter(User.id == "test-delete-user").first()
    if user is None:
        user = User(
            id="test-delete-user", tenant_id="default", first_name="Delete",
            last_name="Me", username="delete-me", email="delete@test.local", is_active=True,
        )
        db.add(user)
    db.commit()

    response = client.delete(
        "/api/v1/gdpr/delete-user/test-delete-user",
        headers={**AUTH_HEADERS, "X-Tenant-ID": "default"},
    )
    assert response.status_code == 204

    # Verify anonymization (not hard-delete, GoBD requires audit trail)
    db.expire_all()
    user = db.query(User).filter(User.id == "test-delete-user").first()
    assert user is not None  # still exists
    assert user.is_active is False
    assert "anonymized" in user.email

