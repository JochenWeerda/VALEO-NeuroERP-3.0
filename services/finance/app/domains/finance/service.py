"""Finance domain service layer."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable

from sqlalchemy.orm import Session
from structlog import get_logger

from finance_shared.gobd.audit_trail import GoBDAuditTrail

from .repository import AccountRepository, JournalEntryRepository, OpenItemRepository
from .schemas import JournalEntryCreate

logger = get_logger(__name__)
_audit_registry: dict[str, GoBDAuditTrail] = {}


def _demo_open_items() -> Iterable[dict]:
    base_due = date.today() + timedelta(days=14)
    return (
        {
            "document_number": "AR-2025-001",
            "customer_id": "CUST-1000",
            "customer_name": "Acme GmbH",
            "amount": Decimal("1230.55"),
            "currency": "EUR",
            "due_date": base_due,
            "status": "open",
        },
        {
            "document_number": "AR-2025-002",
            "customer_id": "CUST-1001",
            "customer_name": "Rhein Consulting",
            "amount": Decimal("890.00"),
            "currency": "EUR",
            "due_date": base_due + timedelta(days=7),
            "status": "open",
        },
    )


def _get_audit_trail(tenant_id: str) -> GoBDAuditTrail:
    if tenant_id not in _audit_registry:
        _audit_registry[tenant_id] = GoBDAuditTrail(tenant_id=tenant_id)
    return _audit_registry[tenant_id]


class FinanceService:
    """Coordinates repositories & compliance hooks."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.accounts = AccountRepository(db)
        self.journal_entries = JournalEntryRepository(db)
        self.open_items = OpenItemRepository(db)

    def list_accounts(self):
        self.accounts.ensure_seed_data(self.tenant_id)
        return self.accounts.list_active(self.tenant_id)

    def list_journal_entries(self):
        return self.journal_entries.list_entries(self.tenant_id)

    def list_open_items(self):
        self.open_items.seed_demo_items(tenant_id=self.tenant_id, items=_demo_open_items())
        return self.open_items.list_items(self.tenant_id)

    def create_journal_entry(self, payload: JournalEntryCreate):
        entry = self.journal_entries.create_entry(
            tenant_id=self.tenant_id,
            account_id=payload.account_id,
            description=payload.description,
            amount=payload.amount,
            currency=payload.currency,
            period=payload.period,
            document_id=payload.document_id,
            user_id=payload.user_id,
        )

        audit_trail = _get_audit_trail(self.tenant_id)
        audit_entry = audit_trail.create_entry(
            entity_type="journal_entry",
            entity_id=entry.id,
            action="create",
            payload={
                "account_id": entry.account_id,
                "amount": str(entry.amount),
                "currency": entry.currency,
                "period": entry.period,
            },
            user_id=payload.user_id,
        )
        audit_trail.append_entry(audit_entry)
        logger.info(
            "journal_entry_created",
            tenant_id=self.tenant_id,
            entry_id=entry.id,
            audit_hash=audit_entry.hash,
        )
        return entry, audit_entry.hash

