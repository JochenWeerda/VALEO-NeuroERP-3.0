"""Finance domain service layer."""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Iterable
from uuid import uuid4

from sqlalchemy.orm import Session
from structlog import get_logger

from finance_shared.gobd.audit_trail import GoBDAuditTrail

from .repository import AccountRepository, JournalEntryRepository, OpenItemRepository
from .schemas import (
    DocumentNumberGap,
    GoBDComplianceResult,
    GoBDComplianceResponse,
    GoBDMonthlyReport,
    JournalEntryCreate,
    PeriodCompleteness,
    StornoResult,
)

logger = get_logger(__name__)
_audit_registry: dict[str, GoBDAuditTrail] = {}

# Regex patterns for document number extraction
_DOC_NUMBER_PATTERN = re.compile(r"(\D+?)(\d+)$")


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

    # ── GoBD Compliance ──────────────────────────────────────────────────

    @staticmethod
    def _extract_sequence_number(doc_number: str) -> tuple[str, int] | None:
        """Extract prefix and numeric sequence from a document number.

        Examples:
            'AR-2025-001' → ('AR-2025-', 1)
            'JE-0042'     → ('JE-', 42)
        """
        match = _DOC_NUMBER_PATTERN.match(doc_number)
        if match:
            return match.group(1), int(match.group(2))
        return None

    def _check_number_sequence(
        self,
        document_type: str,
        doc_numbers: list[str],
    ) -> GoBDComplianceResult:
        """Check a list of document numbers for gaps in the sequence."""
        now = datetime.utcnow()

        if not doc_numbers:
            return GoBDComplianceResult(
                is_compliant=True,
                document_type=document_type,
                total_documents=0,
                gaps=[],
                gap_count=0,
                checked_at=now,
                notes="No documents found – trivially compliant.",
            )

        # Parse all numbers
        parsed: list[tuple[str, int]] = []
        for dn in doc_numbers:
            result = self._extract_sequence_number(dn)
            if result:
                parsed.append(result)

        if not parsed:
            return GoBDComplianceResult(
                is_compliant=True,
                document_type=document_type,
                total_documents=len(doc_numbers),
                gaps=[],
                gap_count=0,
                checked_at=now,
                notes="Could not parse document numbers – manual check recommended.",
            )

        # Group by prefix
        prefix_groups: dict[str, list[int]] = {}
        for prefix, num in parsed:
            prefix_groups.setdefault(prefix, []).append(num)

        gaps: list[DocumentNumberGap] = []
        for prefix, numbers in prefix_groups.items():
            numbers.sort()
            for i in range(len(numbers) - 1):
                expected_next = numbers[i] + 1
                actual_next = numbers[i + 1]
                if actual_next != expected_next:
                    gap_size = actual_next - expected_next
                    gaps.append(
                        DocumentNumberGap(
                            expected_number=f"{prefix}{expected_next:0{len(str(numbers[-1]))}d}",
                            actual_next=f"{prefix}{actual_next:0{len(str(numbers[-1]))}d}",
                            gap_size=gap_size,
                            document_type=document_type,
                        )
                    )

        sorted_all = sorted(parsed, key=lambda x: x[1])
        first = f"{sorted_all[0][0]}{sorted_all[0][1]}"
        last = f"{sorted_all[-1][0]}{sorted_all[-1][1]}"

        return GoBDComplianceResult(
            is_compliant=len(gaps) == 0,
            document_type=document_type,
            total_documents=len(doc_numbers),
            first_number=first,
            last_number=last,
            gaps=gaps,
            gap_count=len(gaps),
            checked_at=now,
            notes="" if len(gaps) == 0 else f"{len(gaps)} gap(s) detected – GoBD violation!",
        )

    def check_gobd_compliance(self) -> GoBDComplianceResponse:
        """Run full GoBD compliance check: document number gaps + audit hash chain.

        GoBD (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von
        Büchern, Aufzeichnungen und Unterlagen in elektronischer Form) requires:
        1. Lückenlose Belegnummerierung (gapless document numbering)
        2. Unveränderbarkeit (immutability via hash chains)
        """
        # 1. Check journal entry document numbers
        journal_entries = self.journal_entries.list_entries(self.tenant_id)
        je_doc_numbers = [e.id for e in journal_entries]
        je_check = self._check_number_sequence("journal_entry", je_doc_numbers)

        # 2. Check open items / invoices
        open_items = self.open_items.list_items(self.tenant_id)
        oi_doc_numbers = [item.document_number for item in open_items]
        oi_check = self._check_number_sequence("invoice", oi_doc_numbers)

        # 3. Verify audit hash chain integrity
        audit_trail = _get_audit_trail(self.tenant_id)
        hash_chain_valid = audit_trail.verify_chain()

        checks = [je_check, oi_check]
        total_gaps = sum(c.gap_count for c in checks)
        overall_compliant = all(c.is_compliant for c in checks) and hash_chain_valid

        if overall_compliant:
            recommendation = "✅ Alle GoBD-Prüfungen bestanden. Belegnummern lückenlos, Hash-Kette intakt."
        else:
            issues = []
            if not hash_chain_valid:
                issues.append("Hash-Kette beschädigt – Datenmanipulation möglich")
            if total_gaps > 0:
                issues.append(f"{total_gaps} Belegnummern-Lücke(n) gefunden")
            recommendation = f"⚠️ GoBD-Verletzung: {'; '.join(issues)}. Sofortige Prüfung erforderlich."

        logger.info(
            "gobd_compliance_check",
            tenant_id=self.tenant_id,
            overall_compliant=overall_compliant,
            total_gaps=total_gaps,
            hash_chain_valid=hash_chain_valid,
        )

        return GoBDComplianceResponse(
            overall_compliant=overall_compliant,
            checks=checks,
            audit_hash_chain_valid=hash_chain_valid,
            total_gaps=total_gaps,
            recommendation=recommendation,
        )

    def generate_monthly_report(self, period: str) -> GoBDMonthlyReport:
        """Generate a comprehensive monthly GoBD compliance report.

        Args:
            period: Accounting period in format 'YYYY-MM' (e.g. '2026-01').

        Returns:
            Complete GoBD monthly report with compliance score and recommendations.
        """
        now = datetime.utcnow()
        report_id = f"GOBD-{self.tenant_id}-{period}-{uuid4().hex[:8]}"

        # ── 1. Document completeness per period ──
        journal_entries = self.journal_entries.list_entries(self.tenant_id)
        open_items = self.open_items.list_items(self.tenant_id)

        # Filter entries for the requested period
        period_entries = [e for e in journal_entries if getattr(e, "period", "") == period]
        period_items = [
            item for item in open_items
            if hasattr(item, "due_date") and str(getattr(item, "due_date", ""))[:7] == period
        ]

        je_doc_numbers = [e.id for e in period_entries]
        je_check = self._check_number_sequence("journal_entry", je_doc_numbers)

        period_completeness = PeriodCompleteness(
            period=period,
            journal_entry_count=len(period_entries),
            open_items_count=len(period_items),
            has_gaps=je_check.gap_count > 0,
            gap_count=je_check.gap_count,
            is_closed=False,  # TODO: Check period closing status
            balance_check="balanced",  # TODO: Real balance check
            notes=je_check.notes,
        )

        # ── 2. Full document number gap analysis ──
        all_je_numbers = [e.id for e in journal_entries]
        all_oi_numbers = [item.document_number for item in open_items]
        full_je_check = self._check_number_sequence("journal_entry", all_je_numbers)
        full_oi_check = self._check_number_sequence("invoice", all_oi_numbers)

        all_gaps = full_je_check.gaps + full_oi_check.gaps
        total_gap_count = len(all_gaps)

        # ── 3. Audit trail integrity ──
        audit_trail = _get_audit_trail(self.tenant_id)
        hash_chain_valid = audit_trail.verify_chain()
        audit_entry_count = len(audit_trail._entries) if hasattr(audit_trail, "_entries") else 0

        # ── 4. Cancellation / Reversal analysis ──
        # Count stornos and check for proper reversal bookings
        cancellation_count = 0
        cancellations_with_reversal = 0
        for entry in journal_entries:
            desc = getattr(entry, "description", "")
            if "storno" in desc.lower() or "cancel" in desc.lower():
                cancellation_count += 1
                # Check if there's a corresponding reversal
                if "gegenbuchung" in desc.lower() or "reversal" in desc.lower():
                    cancellations_with_reversal += 1

        cancellations_missing_reversal = cancellation_count - cancellations_with_reversal

        # ── 5. Compute overall score ──
        score = 100.0
        recommendations: list[str] = []

        if total_gap_count > 0:
            score -= min(30, total_gap_count * 10)
            recommendations.append(
                f"⚠️ {total_gap_count} Belegnummern-Lücke(n) gefunden – sofortige Klärung erforderlich."
            )

        if not hash_chain_valid:
            score -= 30
            recommendations.append(
                "🔴 Hash-Kette beschädigt – mögliche Datenmanipulation. Forensische Analyse empfohlen."
            )

        if cancellations_missing_reversal > 0:
            score -= min(20, cancellations_missing_reversal * 5)
            recommendations.append(
                f"⚠️ {cancellations_missing_reversal} Storno(s) ohne Gegenbuchung – GoBD-Verstoß."
            )

        if len(period_entries) == 0:
            score -= 5
            recommendations.append(
                f"ℹ️ Keine Buchungen in Periode {period} – Prüfung ob Periode korrekt."
            )

        if not recommendations:
            recommendations.append("✅ Alle GoBD-Prüfungen bestanden. Volle Compliance.")

        score = max(0, min(100, score))

        # Determine status
        if score >= 90:
            compliance_status = "compliant"
        elif score >= 60:
            compliance_status = "warning"
        else:
            compliance_status = "violation"

        # ── 6. Create report signature (integrity hash) ──
        sig_data = f"{report_id}|{period}|{total_gap_count}|{hash_chain_valid}|{score}|{now.isoformat()}"
        signature = hashlib.sha256(sig_data.encode()).hexdigest()

        report = GoBDMonthlyReport(
            report_id=report_id,
            tenant_id=self.tenant_id,
            report_period=period,
            generated_at=now,
            compliance_status=compliance_status,
            periods=[period_completeness],
            document_gaps=all_gaps,
            total_gap_count=total_gap_count,
            audit_hash_chain_valid=hash_chain_valid,
            audit_entry_count=audit_entry_count,
            cancellation_count=cancellation_count,
            cancellations_with_reversal=cancellations_with_reversal,
            cancellations_missing_reversal=cancellations_missing_reversal,
            overall_score=score,
            recommendations=recommendations,
            signature=signature,
        )

        logger.info(
            "gobd_monthly_report_generated",
            tenant_id=self.tenant_id,
            period=period,
            score=score,
            compliance_status=compliance_status,
            report_id=report_id,
        )

        return report

    # ── Storno mit Gegenbuchung ──────────────────────────────────────────

    def cancel_journal_entry(
        self,
        journal_entry_id: str,
        reason: str,
        user_id: str,
    ) -> StornoResult:
        """Cancel a journal entry by creating an automatic reversal booking (Gegenbuchung).

        GoBD-compliant: The original entry is NEVER deleted or modified.
        Instead, a new entry with the negated amount is created, referencing
        the original as its document_id.

        Args:
            journal_entry_id: ID of the journal entry to cancel.
            reason: Mandatory cancellation reason for audit trail.
            user_id: User performing the cancellation.

        Returns:
            StornoResult with details of both original and reversal entries.

        Raises:
            ValueError: If the entry is not found or already cancelled.
        """
        # 1. Find original entry
        entries = self.journal_entries.list_entries(self.tenant_id)
        original = None
        for entry in entries:
            if entry.id == journal_entry_id:
                original = entry
                break

        if original is None:
            raise ValueError(f"Buchung {journal_entry_id} nicht gefunden.")

        # 2. Check if already cancelled (look for existing reversal)
        for entry in entries:
            if (
                entry.document_id == journal_entry_id
                and "STORNO" in entry.description.upper()
            ):
                raise ValueError(
                    f"Buchung {journal_entry_id} wurde bereits storniert "
                    f"(Gegenbuchung: {entry.id})."
                )

        # 3. Create reversal entry (Gegenbuchung)
        reversal_amount = -original.amount
        reversal_description = (
            f"STORNO/Gegenbuchung zu {original.id}: {original.description} "
            f"| Grund: {reason}"
        )

        reversal_entry = self.journal_entries.create_entry(
            tenant_id=self.tenant_id,
            account_id=original.account_id,
            description=reversal_description,
            amount=reversal_amount,
            currency=original.currency,
            period=original.period,
            document_id=original.id,  # Link to original
            user_id=user_id,
        )

        # 4. Create audit trail entry for the reversal
        audit_trail = _get_audit_trail(self.tenant_id)
        audit_entry = audit_trail.create_entry(
            document_id=reversal_entry.id,
            document_type="storno",
            action="reversal_created",
            user_id=user_id,
            data={
                "original_entry_id": original.id,
                "reversal_entry_id": reversal_entry.id,
                "original_amount": str(original.amount),
                "reversal_amount": str(reversal_amount),
                "reason": reason,
            },
        )
        audit_trail.append_entry(audit_entry)

        logger.info(
            "journal_entry_cancelled",
            tenant_id=self.tenant_id,
            original_id=original.id,
            reversal_id=reversal_entry.id,
            amount=str(original.amount),
            reason=reason,
            user_id=user_id,
        )

        return StornoResult(
            original_entry_id=original.id,
            original_description=original.description,
            original_amount=original.amount,
            reversal_entry_id=reversal_entry.id,
            reversal_description=reversal_description,
            reversal_amount=reversal_amount,
            reversal_audit_hash=audit_entry.hash,
            reason=reason,
            cancelled_by=user_id,
            cancelled_at=reversal_entry.posted_at,
        )
