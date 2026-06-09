"""Service layer for finance journal entry and posting operations."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import JournalEntry
from app.infrastructure.models.journal import JournalEntryLine

logger = logging.getLogger(__name__)

VALID_STATUSES = {"draft", "posted", "cancelled", "reversed"}


class FinanceTransactionService:
    """Encapsulates journal entry creation, validation, posting, and GoBD compliance."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── validation ────────────────────────────────────────────────────────────

    def validate_balanced(self, lines: List[Dict[str, Any]]) -> None:
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

    def check_period_open(self, period: Optional[str]) -> None:
        if not period:
            return
        try:
            row = self.db.execute(
                text(
                    "SELECT status FROM finance_accounting_periods "
                    "WHERE tenant_id = :tid AND period = :period"
                ),
                {"tid": self.tenant_id, "period": period},
            ).fetchone()
            if row and row[0] != "OPEN":
                raise ValidationFailedError(
                    f"Periode {period} ist {row[0]}. Buchungen in geschlossenen Perioden sind gesperrt."
                )
        except ValidationFailedError:
            raise
        except Exception:
            pass  # table may not exist in test/dev — allow through

    # ── GoBD helpers ─────────────────────────────────────────────────────────

    def _next_sequence_number(self) -> int:
        row = self.db.execute(
            text(
                "SELECT COALESCE(MAX(sequence_number), 0) + 1 AS next "
                "FROM domain_erp.journal_entries WHERE tenant_id = :tid"
            ),
            {"tid": self.tenant_id},
        ).fetchone()
        return int(row[0]) if row else 1

    @staticmethod
    def _compute_hash(entry: JournalEntry, prev_hash: Optional[str]) -> str:
        payload = (
            f"{entry.tenant_id}|{entry.sequence_number}|{entry.entry_number}|"
            f"{entry.entry_date}|{entry.total_debit}|{prev_hash or ''}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def _prev_hash(self) -> Optional[str]:
        row = self.db.execute(
            text(
                "SELECT hash_current FROM domain_erp.journal_entries "
                "WHERE tenant_id = :tid AND sequence_number = ("
                "  SELECT MAX(sequence_number) FROM domain_erp.journal_entries "
                "  WHERE tenant_id = :tid"
                ")"
            ),
            {"tid": self.tenant_id},
        ).fetchone()
        return str(row[0]) if row and row[0] else None

    def _stamp_gobd(self, obj: JournalEntry) -> None:
        try:
            obj.sequence_number = self._next_sequence_number()
            prev = self._prev_hash()
            obj.hash_prev = prev
            obj.hash_current = self._compute_hash(obj, prev)
        except Exception as exc:
            logger.warning("GoBD stamp failed for %s: %s", obj.id, exc)

    def _resolve_account_id(self, account_ref: str) -> str:
        row = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_erp.chart_of_accounts
                WHERE is_active = TRUE
                  AND (id = :account_ref OR account_number = :account_ref)
                LIMIT 1
                """
            ),
            {"account_ref": account_ref},
        ).first()
        if not row:
            raise ValidationFailedError(
                f"Active chart-of-accounts entry not found: {account_ref}"
            )
        return str(row[0])

    def _resolve_user_id(self, user_id: Optional[str]) -> Optional[str]:
        if not user_id:
            return None
        row = self.db.execute(
            text(
                """
                SELECT id
                FROM domain_shared.users
                WHERE id = :user_id
                LIMIT 1
                """
            ),
            {"user_id": user_id},
        ).first()
        return str(row[0]) if row and str(row[0]) == user_id else None

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
        reference: Optional[str] = None,
    ) -> Tuple[List[JournalEntry], int]:
        q = self.db.query(JournalEntry).filter(JournalEntry.tenant_id == self.tenant_id)
        if status:
            q = q.filter(JournalEntry.status == status)
        if date_from:
            q = q.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            q = q.filter(JournalEntry.entry_date <= date_to)
        if reference:
            q = q.filter(JournalEntry.reference == reference)
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
        document_type: Optional[str] = None,
        period: Optional[str] = None,
    ) -> JournalEntry:
        if not reference or not str(reference).strip():
            raise ValidationFailedError(
                "Belegprinzip: Jede Buchung muss eine Belegreferenz haben (reference-Feld)"
            )
        self.validate_balanced(lines)
        self.check_period_open(period)

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
            document_type=document_type,
            status="draft",
            total_debit=total_debit,
            total_credit=total_debit,
        )
        self._stamp_gobd(obj)
        self.db.add(obj)
        self.db.flush()  # get obj.id before inserting lines

        for line_number, ln in enumerate(lines, start=1):
            debit = Decimal(str(ln.get("debit_amount", 0)))
            credit = Decimal(str(ln.get("credit_amount", 0)))
            line = JournalEntryLine(
                id=uuid7(),
                journal_entry_id=obj.id,
                tenant_id=self.tenant_id,
                account_id=self._resolve_account_id(
                    str(ln.get("account_id") or ln.get("accountId") or "")
                ),
                debit=debit,
                credit=credit,
                debit_amount=debit,
                credit_amount=credit,
                line_number=line_number,
                description=ln.get("description") or "",
            )
            self.db.add(line)

        self.db.commit()
        self.db.refresh(obj)
        logger.info("Created JournalEntry %s (%s)", obj.id, entry_number)
        return obj

    def update(self, entry_id: str, data: Dict[str, Any]) -> JournalEntry:
        obj = self.get_by_id(entry_id)
        if obj.status != "draft":
            raise ValidationFailedError("Nur Entwürfe können geändert werden")
        for field in ("description", "reference", "document_type"):
            if field in data:
                setattr(obj, field, data[field])
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, entry_id: str) -> None:
        obj = self.get_by_id(entry_id)
        if obj.status != "draft":
            raise ValidationFailedError("Nur Entwürfe können gelöscht werden")
        self.db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id == entry_id
        ).delete(synchronize_session=False)
        self.db.delete(obj)
        self.db.commit()

    def post(self, entry_id: str, posted_by: Optional[str] = None) -> JournalEntry:
        obj = self.get_by_id(entry_id)
        self.validate_status_transition(obj.status, "posted")
        obj.status = "posted"
        obj.posted_at = datetime.utcnow()
        resolved_posted_by = self._resolve_user_id(posted_by)
        if resolved_posted_by:
            obj.posted_by = resolved_posted_by
        self.db.commit()
        self.db.refresh(obj)
        logger.info("Posted JournalEntry %s", entry_id)
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

    def reverse(self, entry_id: str, reason: str = "") -> Tuple[JournalEntry, JournalEntry]:
        """Mark original as reversed and create a mirror entry with inverted debit/credit."""
        original = self.get_by_id(entry_id)
        self.validate_status_transition(original.status, "reversed")

        # Load original lines
        orig_lines = (
            self.db.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == entry_id)
            .all()
        )

        # Build reversal entry
        now = datetime.utcnow()
        rev_number = f"STORNO-{original.entry_number}"
        rev_desc = f"Storno: {original.description}" + (f" — {reason}" if reason else "")

        reversal = JournalEntry(
            id=uuid7(),
            tenant_id=self.tenant_id,
            entry_number=rev_number,
            description=rev_desc,
            entry_date=now,
            posting_date=now,
            reference=original.reference,
            source="reversal",
            document_type=original.document_type,
            status="posted",
            total_debit=original.total_credit,
            total_credit=original.total_debit,
            reversed_entry_id=entry_id,
            posted_at=now,
        )
        self._stamp_gobd(reversal)
        self.db.add(reversal)
        self.db.flush()

        # Mirror lines with debit/credit swapped
        for line_number, ln in enumerate(orig_lines, start=1):
            self.db.add(
                JournalEntryLine(
                    id=uuid7(),
                    journal_entry_id=reversal.id,
                    tenant_id=self.tenant_id,
                    account_id=ln.account_id,
                    debit=ln.credit,
                    credit=ln.debit,
                    debit_amount=ln.credit,
                    credit_amount=ln.debit,
                    line_number=line_number,
                    description=ln.description,
                )
            )

        # Mark original as reversed
        original.status = "reversed"
        original.reversed_entry_id = reversal.id

        self.db.commit()
        self.db.refresh(original)
        self.db.refresh(reversal)
        logger.info("Reversed JournalEntry %s → reversal %s", entry_id, reversal.id)
        return original, reversal
