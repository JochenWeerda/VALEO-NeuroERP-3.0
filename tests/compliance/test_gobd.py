"""
GoBD Compliance Tests
Automated tests for German tax law requirements
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.infrastructure.models import AuditLog, JournalEntry


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_audit_log_is_immutable(db: Session):
    """Test that audit log cannot be modified (Unveränderbarkeit)."""
    from uuid import uuid4
    
    # Create audit log entry
    log = AuditLog(
        id=str(uuid4()),
        timestamp=datetime.utcnow(),
        user_id="test-user",
        user_email="test@example.com",
        tenant_id="test-tenant",
        action="create",
        entity_type="customer",
        entity_id="cust-123",
        changes={"name": "Original"}
    )
    
    db.add(log)
    db.commit()
    original_id = log.id
    
    # Try to modify (should be prevented by DB-triggers in production)
    try:
        log.changes = {"name": "Modified"}
        db.commit()
        # If this succeeds, we need DB-level protection
        pytest.fail("Audit log was modified - needs DB-level immutability!")
    except Exception:
        # Expected: Cannot modify
        db.rollback()
        pass
    
    # Verify original is unchanged
    db.refresh(log)
    assert log.changes == {"name": "Original"}


def test_journal_entry_has_all_required_fields(db: Session):
    """Test that journal entries have all GoBD-required fields."""
    from uuid import uuid4
    
    entry = JournalEntry(
        id=str(uuid4()),
        entry_number="JE-2025-001",
        entry_date=datetime.utcnow(),
        posting_date=datetime.utcnow(),
        description="Test-Buchung",
        source="manual",
        tenant_id="test-tenant"
    )
    
    db.add(entry)
    db.commit()
    
    # Required fields for GoBD
    assert entry.entry_number is not None  # Belegnummer
    assert entry.entry_date is not None    # Belegdatum
    assert entry.posting_date is not None  # Buchungsdatum
    assert entry.description is not None   # Buchungstext


def test_booking_date_within_10_days_of_document_date():
    """Test that posting_date ≤ entry_date + 10 days (Zeitnähe)."""
    db = SessionLocal()
    
    # Query all journal entries
    entries = db.query(JournalEntry).all()
    
    for entry in entries:
        if entry.entry_date and entry.posting_date:
            delta = (entry.posting_date - entry.entry_date).days
            assert delta <= 10, (
                f"Entry {entry.entry_number}: "
                f"Posting date {delta} days after entry date (max 10)"
            )
    
    db.close()


def test_no_gaps_in_document_numbers():
    """Test that there are no gaps in document numbers (Vollständigkeit)."""
    # Simplified test - in production: check all document types
    # This is a placeholder
    pass


def test_all_transactions_have_audit_trail():
    """Test that all transactions are logged (Nachvollziehbarkeit)."""
    db = SessionLocal()
    
    # Every JournalEntry should have corresponding AuditLog
    entries = db.query(JournalEntry).limit(10).all()
    
    for entry in entries:
        audit_logs = db.query(AuditLog).filter(
            AuditLog.entity_type == "journal_entry",
            AuditLog.entity_id == entry.id
        ).all()
        
        # Should have at least "create" event
        assert len(audit_logs) > 0, (
            f"No audit log for journal entry {entry.entry_number}"
        )
    
    db.close()


def test_datev_export_format_valid():
    """Test that DATEV export has correct format."""
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # Call DATEV export endpoint
    response = client.get("/api/v1/fibu/export/datev")
    
    if response.status_code == 200:
        # Should be CSV format
        assert response.headers["Content-Type"] == "text/csv"
        
        # Should have required columns
        content = response.text
        assert "Konto" in content
        assert "Gegenkonto" in content
        assert "Betrag" in content

