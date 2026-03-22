"""
Settlement completion contracts for Gap 004.

This module defines a single acceptance contract for the fachliche
end-to-end closure of a settlement lifecycle across approval, financial
document generation, correction flow and posting evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SettlementCompletionVariant(str, Enum):
    GUTSCHRIFT = "GUTSCHRIFT"
    BELASTUNG = "BELASTUNG"
    KORREKTUR = "KORREKTUR"


class SettlementFinancialDocumentKind(str, Enum):
    GUTSCHRIFT = "GUTSCHRIFT"
    BELASTUNG = "BELASTUNG"
    STORNO = "STORNO"
    KORREKTUR_NEU = "KORREKTUR_NEU"


@dataclass(frozen=True)
class SettlementCompletionEvidence:
    settlement_id: str
    variant: SettlementCompletionVariant
    approval_status: str
    has_approval_history: bool
    has_audit_chain: bool
    has_gobd_check: bool
    has_journal_entry: bool
    has_blockchain_anchor: bool = False
    financial_document_kind: SettlementFinancialDocumentKind | None = None
    financial_document_status: str | None = None
    correction_mode: str | None = None
    correction_links_complete: bool = False


@dataclass(frozen=True)
class SettlementCompletionResult:
    settlement_id: str
    variant: SettlementCompletionVariant
    completed: bool
    completion_pct: int
    missing_controls: list[str] = field(default_factory=list)
    next_step: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "settlement_id": self.settlement_id,
            "variant": self.variant.value,
            "completed": self.completed,
            "completion_pct": self.completion_pct,
            "missing_controls": list(self.missing_controls),
            "next_step": self.next_step,
        }


def evaluate_settlement_completion(
    evidence: SettlementCompletionEvidence,
) -> SettlementCompletionResult:
    missing: list[str] = []

    if evidence.approval_status not in {"FREIGEGEBEN", "VERBUCHT"}:
        missing.append("approval_status")
    if not evidence.has_approval_history:
        missing.append("approval_history")
    if not evidence.has_audit_chain:
        missing.append("audit_chain")
    if not evidence.has_gobd_check:
        missing.append("gobd_check")
    if not evidence.has_journal_entry:
        missing.append("journal_entry")

    if evidence.variant == SettlementCompletionVariant.GUTSCHRIFT:
        if evidence.financial_document_kind != SettlementFinancialDocumentKind.GUTSCHRIFT:
            missing.append("credit_note_document")
        if evidence.financial_document_status not in {"ISSUED", "BOOKED", "SETTLED", "PAID"}:
            missing.append("credit_note_status")
    elif evidence.variant == SettlementCompletionVariant.BELASTUNG:
        if evidence.financial_document_kind != SettlementFinancialDocumentKind.BELASTUNG:
            missing.append("debit_memo_document")
        if evidence.financial_document_status not in {"OPEN", "BOOKED", "SETTLED"}:
            missing.append("debit_memo_status")
    elif evidence.variant == SettlementCompletionVariant.KORREKTUR:
        if evidence.correction_mode != "STORNO_UND_NEU":
            missing.append("correction_mode")
        if not evidence.correction_links_complete:
            missing.append("correction_links")
        if evidence.financial_document_kind not in {
            SettlementFinancialDocumentKind.STORNO,
            SettlementFinancialDocumentKind.KORREKTUR_NEU,
        }:
            missing.append("correction_documents")
        if evidence.financial_document_status not in {"BOOKED", "SETTLED", "ISSUED"}:
            missing.append("correction_status")

    total_controls = 8 if evidence.variant != SettlementCompletionVariant.KORREKTUR else 10
    completion_pct = max(0, round(((total_controls - len(missing)) / total_controls) * 100))
    completed = len(missing) == 0

    next_step = None if completed else f"Fehlende Nachweise nachziehen: {', '.join(missing)}"
    return SettlementCompletionResult(
        settlement_id=evidence.settlement_id,
        variant=evidence.variant,
        completed=completed,
        completion_pct=completion_pct,
        missing_controls=missing,
        next_step=next_step,
    )
