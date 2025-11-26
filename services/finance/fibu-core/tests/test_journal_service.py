from uuid import uuid4

from finance_shared.gobd import GoBDAuditTrail

from app.services.journal_service import JournalService


def test_journal_service_creates_audit_and_event():
    trail = GoBDAuditTrail(tenant_id="tenant-1")
    service = JournalService(trail)
    booking_id = str(uuid4())
    payload = {
        "id": booking_id,
        "account_id": "8400",
        "amount": "99.90",
        "currency": "EUR",
        "period": "2025-11",
    }

    result = service.create_entry(payload, user_id="user-1")

    assert result["event"]["payload"]["account_id"] == "8400"
    assert len(trail.entries()) == 1
    assert result["audit_entry"]["entity_id"] == booking_id


