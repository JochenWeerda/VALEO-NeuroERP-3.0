"""Service layer for finance journal entry and posting operations."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import JournalEntry
from app.infrastructure.models.journal import JournalEntryLine
from app.core import finance_periods

logger = logging.getLogger(__name__)

VALID_STATUSES = {"draft", "posted", "cancelled", "reversed"}
MONEY_MAX = Decimal("9999999999999.99")
MONEY_CENT = Decimal("0.01")


class FinanceTransactionService:
    """Encapsulates journal entry creation, validation, posting, and GoBD compliance."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── validation ────────────────────────────────────────────────────────────

    @staticmethod
    def _money(value: Any) -> Decimal:
        """The stored NUMERIC(15,2) contract: exact finite currency cents."""
        try:
            amount = Decimal(str(value))
            if (not amount.is_finite() or amount < 0
                    or amount > MONEY_MAX
                    or amount != amount.quantize(MONEY_CENT)):
                raise ValidationFailedError("Journal amounts require finite nonnegative exact cents within NUMERIC(15,2)")
            return Decimal("0.00") if amount == 0 else amount.quantize(MONEY_CENT)
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationFailedError("Journal amount is not a valid exact decimal") from exc

    def validate_balanced(self, lines: List[Dict[str, Any]]) -> Decimal:
        if not isinstance(lines, list) or len(lines) < 2:
            raise ValidationFailedError("A journal requires at least two nonzero lines")
        total_debit = total_credit = Decimal("0.00")
        for line in lines:
            if not isinstance(line, dict):
                raise ValidationFailedError("Journal lines require typed amount fields")
            if {"debit", "credit", "debitAmount", "creditAmount"}.intersection(line):
                raise ValidationFailedError("Journal lines require canonical debit_amount and credit_amount")
            if "debit_amount" not in line or "credit_amount" not in line:
                raise ValidationFailedError("Both canonical journal amount fields are required")
            debit = self._money(line["debit_amount"])
            credit = self._money(line["credit_amount"])
            if (debit > 0) == (credit > 0):
                raise ValidationFailedError("Each journal line requires exactly one positive side")
            total_debit += debit
            total_credit += credit
            if total_debit > MONEY_MAX or total_credit > MONEY_MAX:
                raise ValidationFailedError("Journal totals exceed NUMERIC(15,2)")
        if total_debit != total_credit:
            raise ValidationFailedError("Journal entry is not balanced")
        return total_debit

    def _validated_existing_lines(self, obj: JournalEntry) -> List[JournalEntryLine]:
        lines = self.db.query(JournalEntryLine).filter(
            JournalEntryLine.journal_entry_id == obj.id
        ).all()
        payload = []
        for line in lines:
            if line.tenant_id != self.tenant_id:
                raise ValidationFailedError("Journal line belongs to another tenant")
            debit = self._money(line.debit_amount)
            credit = self._money(line.credit_amount)
            if debit != self._money(line.debit) or credit != self._money(line.credit):
                raise ValidationFailedError("Conflicting stored journal amounts")
            payload.append({"account_id": line.account_id, "debit_amount": debit, "credit_amount": credit})
        total = self.validate_balanced(payload)
        if self._money(obj.total_debit) != total or self._money(obj.total_credit) != total:
            raise ValidationFailedError("Journal header amounts contradict its lines")
        self._validate_line_accounts(payload)
        return lines

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
        """Weist eine Buchung in eine gesperrte Periode ab.

        Vorher endete diese Pruefung mit ``except Exception: pass  # allow
        through``: War die Periodentabelle nicht lesbar, **entfiel die Sperre
        ganz** — stillschweigend. Das ist die Unveraenderbarkeit nach GoBD
        (Rz. 107 ff.) genau verkehrt herum: Wer nicht feststellen kann, ob eine
        Periode offen ist, darf nicht buchen lassen.
        """
        if not period:
            return
        try:
            gesperrt = finance_periods.gesperrter_zustand(self.db, self.tenant_id, period)
        except Exception as fehler:  # noqa: BLE001
            raise ValidationFailedError(
                f"Zustand der Periode {period} ist nicht feststellbar "
                f"({type(fehler).__name__}). Buchung abgewiesen."
            ) from fehler
        if gesperrt:
            raise ValidationFailedError(
                f"Periode {period} ist {gesperrt}. "
                "Buchungen in geschlossenen Perioden sind gesperrt."
            )

    # ── GoBD helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(entry: JournalEntry, prev_hash: Optional[str], sequence_number: Optional[int] = None) -> str:
        payload = (
            f"{entry.tenant_id}|{entry.sequence_number if sequence_number is None else sequence_number}|{entry.entry_number}|"
            f"{entry.entry_date}|{entry.total_debit}|{prev_hash or ''}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def _stamp_gobd(self, obj: JournalEntry) -> None:
        """Serialize chain allocation and refuse writes without valid evidence.

        The transaction owns the tenant lock until commit/rollback. Existing
        incomplete chains are rejected, never repaired by guessing a predecessor.
        This validates chain metadata; the historical hash payload still needs
        a separate canonical contract covering all journal attributes and lines.
        """
        if not self.tenant_id or obj.tenant_id != self.tenant_id:
            raise ValidationFailedError("Journal stamp requires the owning tenant")
        if obj.sequence_number is not None or obj.hash_current is not None or obj.hash_prev is not None:
            raise ValidationFailedError("Existing journal stamp cannot be replaced")
        try:
            isolation = self.db.execute(
                text("SELECT current_setting('transaction_isolation'), pg_advisory_xact_lock(hashtextextended(:chain_key, 0))"),
                {"chain_key": f"journal-chain:{self.tenant_id}"},
            ).fetchone()
            if isolation is None or isolation[0] != "read committed":
                raise ValidationFailedError("Journal allocation requires READ COMMITTED isolation")
            row = self.db.execute(text("""
                WITH chain AS (
                    SELECT sequence_number, hash_current, hash_prev,
                           LAG(hash_current) OVER (ORDER BY sequence_number) AS predecessor
                    FROM domain_erp.journal_entries WHERE tenant_id = :tenant_id
                )
                SELECT COUNT(*), MAX(sequence_number), COUNT(DISTINCT sequence_number),
                       COUNT(*) FILTER (WHERE sequence_number IS NULL OR sequence_number <= 0
                         OR hash_current IS NULL OR hash_current !~ '^[0-9a-f]{64}$'
                         OR hash_prev IS DISTINCT FROM predecessor),
                       (SELECT hash_current FROM chain
                        ORDER BY sequence_number DESC NULLS LAST LIMIT 1)
                FROM chain
            """), {"tenant_id": self.tenant_id}).fetchone()
            if row is None:
                raise ValidationFailedError("Journal chain evidence unavailable")
            count, maximum, distinct, invalid, previous = row
            if invalid or distinct != count or (maximum or 0) != count:
                raise ValidationFailedError("Journal chain metadata is inconsistent")
            # Assign only once every read and check succeeded; no partial stamp.
            sequence = count + 1
            current = self._compute_hash(obj, previous, sequence)
            obj.sequence_number = sequence
            obj.hash_prev = previous
            obj.hash_current = current
        except ValidationFailedError:
            raise
        except Exception as exc:
            raise ValidationFailedError(
                "Journal chain evidence unavailable; write rejected"
            ) from exc

    def _resolve_account_id(self, account_id: str) -> str:
        """Validate the canonical ID; account numbers are never aliases."""
        return self._bookable_account("id", account_id)

    def account_id_for_number(self, account_number: str) -> str:
        """Explicit tenant-owned number lookup before constructing journal lines."""
        return self._bookable_account("account_number", account_number)

    def _bookable_account(self, field: str, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationFailedError("A nonempty account reference is required")
        # field is selected exclusively by the two fixed methods above.
        if field not in {"id", "account_number"}:
            raise ValidationFailedError("Unsupported account reference")
        row = self.db.execute(text(f"""
            SELECT id FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tenant_id AND {field} = :value
              AND is_active = TRUE AND deleted_at IS NULL
              AND COALESCE(is_summary, FALSE) = FALSE
        """), {"tenant_id": self.tenant_id, "value": value}).first()
        if row is None:
            raise ValidationFailedError("Own active bookable account not found")
        return str(row[0])

    def _validate_line_accounts(self, lines: List[Dict[str, Any]]) -> List[str]:
        ids = []
        for line in lines:
            if "accountId" in line or "account_number" in line:
                raise ValidationFailedError("Journal lines require canonical account_id")
            value = line.get("account_id")
            if not isinstance(value, str) or not value.strip():
                raise ValidationFailedError("A nonempty account reference is required")
            ids.append(value)
        if not ids:
            return ids
        requested = set(ids)
        statement = text("""
            SELECT id FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tenant_id AND id IN :account_ids
              AND is_active = TRUE AND deleted_at IS NULL
              AND COALESCE(is_summary, FALSE) = FALSE
            FOR SHARE
        """).bindparams(bindparam("account_ids", expanding=True))
        found = {str(row[0]) for row in self.db.execute(statement,
            {"tenant_id": self.tenant_id, "account_ids": sorted(requested)}).all()}
        if found != requested:
            raise ValidationFailedError("Own active bookable account not found")
        return ids

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
        total_debit = self.validate_balanced(lines)
        self.check_period_open(period)
        account_ids = self._validate_line_accounts(lines)

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
            debit = self._money(ln["debit_amount"])
            credit = self._money(ln["credit_amount"])
            line = JournalEntryLine(
                id=uuid7(),
                journal_entry_id=obj.id,
                tenant_id=self.tenant_id,
                account_id=account_ids[line_number - 1],
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
        self._validated_existing_lines(obj)
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

        orig_lines = self._validated_existing_lines(original)

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
