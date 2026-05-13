"""Service layer for finance journal entry and posting operations."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import JournalEntry

logger = logging.getLogger(__name__)

VALID_STATUSES = {"draft", "posted", "cancelled", "reversed"}


class FinanceTransactionService:
    """Encapsulates journal entry creation, validation, and posting."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── validation ────────────────────────────────────────────────────────────

    def validate_balanced(self, lines: List[Dict[str, Any]]) -> None:
        """Raise ValidationFailedError when debit ≠ credit."""
        total_debit = sum(Decimal(str(ln.get("debit_amount", 0))) for ln in lines)
        total_credit = sum(Decimal(str(ln.get("credit_amount", 0))) for ln in lines)
        if total_debit != total_credit:
            raise ValidationFailedError(
                f"Journal entry is not balanced: debit={total_debit}, credit={total_credit}"
            )

    def validate_status_transition(self, current: str, target: str) -> None:
        allowed: Dict[str, set] = {
            "draft": {"posted", "cancelled"},
            "posted": {"reversed"},
            "cancelled": set(),
            "reversed": set(),
        }
        if target not in allowed.get(current, set()):
            raise ValidationFailedError(
                f"Status transition '{current}' → '{target}' is not allowed"
            )

    # ── queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, entry_id: str) -> JournalEntry:
        obj = (
            self.db.query(JournalEntry)
            .filter(
                JournalEntry.id == entry_id,
                JournalEntry.tenant_id == self.tenant_id,
            )
            .first()
        )
        if obj is None:
            raise EntityNotFoundError("JournalEntry", entry_id)
        return obj

    def list_paginated(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[List[JournalEntry], int]:
        q = self.db.query(JournalEntry).filter(
            JournalEntry.tenant_id == self.tenant_id
        )
        if status:
            q = q.filter(JournalEntry.status == status)
        if date_from:
            q = q.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            q = q.filter(JournalEntry.entry_date <= date_to)
        total = q.count()
        items = q.order_by(JournalEntry.entry_date.desc()).offset(skip).limit(limit).all()
        return items, total

    # ── mutations ─────────────────────────────────────────────────────────────

    def create(
        self,
        entry_number: str,
        description: str,
        entry_date: datetime,
        lines: List[Dict[str, Any]],
        reference: Optional[str] = None,
        source: Optional[str] = None,
    ) -> JournalEntry:
        self.validate_balanced(lines)
        total_debit = sum(Decimal(str(ln.get("debit_amount", 0))) for ln in lines)
        obj = JournalEntry(
            id=uuid7(),
            tenant_id=self.tenant_id,
            entry_number=entry_number,
            description=description,
            entry_date=entry_date,
            posting_date=entry_date,
            reference=reference,
            source=source or "manual",
            status="draft",
            total_debit=total_debit,
            total_credit=total_debit,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        logger.info("Created JournalEntry %s (%s)", obj.id, entry_number)
        return obj

    def post(self, entry_id: str) -> JournalEntry:
        obj = self.get_by_id(entry_id)
        self.validate_status_transition(obj.status, "posted")
        obj.status = "posted"
        obj.posted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def cancel(self, entry_id: str, reason: str) -> JournalEntry:
        obj = self.get_by_id(entry_id)
        self.validate_status_transition(obj.status, "cancelled")
        obj.status = "cancelled"
        if hasattr(obj, "cancel_reason"):
            obj.cancel_reason = reason
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def reverse(self, entry_id: str) -> JournalEntry:
        obj = self.get_by_id(entry_id)
        self.validate_status_transition(obj.status, "reversed")
        obj.status = "reversed"
        self.db.commit()
        self.db.refresh(obj)
        return obj
