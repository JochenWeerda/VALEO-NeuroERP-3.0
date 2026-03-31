"""
Confidence & Risk Ledger -- Lane B, Slice 2

Append-only, hash-chained ledger that records every confidence/risk decision
made by the Neuro-Core AI Agent Orchestrator.

Design principles:
  - Every entry is immutable once written (no UPDATE, no DELETE).
  - Each entry carries a SHA-256 hash of (previous_hash + payload), forming a
    tamper-evident chain similar to a blockchain anchor.
  - Model version + input_hash enable reproducibility: re-running the same
    model on the same input must produce the same confidence_score.

Integration points:
  - ApprovalRisikostufe (human_approval_gate) feeds risk_level into entries.
  - CaseRun (neuroassist_contracts) links via case_run_id.
  - StateTransition (neuro_state_graph) can reference ledger entries as evidence.
  - AuditRecord (neuroassist_audit) embeds ledger_entry_id in evidence_refs.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ConfidenceSource(str, Enum):
    """What produced the confidence score."""
    INTENT_ENGINE = "intent_engine"
    PLANNER = "planner"
    POLICY_GATE = "policy_gate"
    APPROVAL_GATE = "approval_gate"
    DQ_GATE = "dq_gate"
    RISK_ASSESSMENT = "risk_assessment"
    MODEL_INFERENCE = "model_inference"
    HUMAN_OVERRIDE = "human_override"


class RiskLevel(str, Enum):
    """Mirrors ApprovalRisikostufe for ledger self-containment."""
    NIEDRIG = "NIEDRIG"
    MITTEL = "MITTEL"
    HOCH = "HOCH"
    KRITISCH = "KRITISCH"


# ---------------------------------------------------------------------------
# Ledger Entry
# ---------------------------------------------------------------------------

LEDGER_SCHEMA_VERSION = 1
GENESIS_HASH = "0" * 64  # SHA-256 zero-hash for the first entry in a chain


class ConfidenceLedgerEntry(BaseModel):
    """
    Single immutable entry in the Confidence Ledger.

    The chain_hash links each entry to its predecessor, making the ledger
    tamper-evident. Verifiers can walk the chain and recompute hashes.
    """

    entry_id: str = Field(min_length=3, description="UUID of this ledger entry")
    tenant_id: str = Field(min_length=1)
    case_run_id: str | None = Field(default=None, description="NeuroASSIST CaseRun reference")
    state_node_id: str | None = Field(default=None, description="State Graph node reference")

    # Score
    confidence_score: float = Field(ge=0.0, le=1.0, description="0.0 = no confidence, 1.0 = full confidence")
    risk_level: RiskLevel
    source: ConfidenceSource

    # Reproducibility
    model_id: str = Field(default="", description="ID/version of the model that produced this score")
    model_version: str = Field(default="", description="Semantic version of the scoring model")
    input_hash: str = Field(default="", description="SHA-256 of the input payload for reproducibility")

    # Evidence
    reason: str = Field(min_length=1, description="Human-readable explanation")
    evidence_refs: list[str] = Field(default_factory=list)
    context_data: dict[str, Any] = Field(default_factory=dict, description="Structured context snapshot")

    # Chain integrity
    previous_hash: str = Field(default=GENESIS_HASH, description="SHA-256 of previous entry in chain")
    chain_hash: str = Field(default="", description="SHA-256(previous_hash + canonical(payload))")

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = LEDGER_SCHEMA_VERSION


class LedgerChainBroken(Exception):
    """Raised when the hash chain cannot be verified."""


class LedgerImmutabilityViolation(Exception):
    """Raised on an attempt to modify or delete a ledger entry."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ConfidenceLedgerService:
    """
    Pure-logic service for the Confidence Ledger.

    Stateless -- all persistence goes through the repository/ORM layer.
    """

    @staticmethod
    def _canonical_payload(entry: ConfidenceLedgerEntry) -> str:
        """Deterministic JSON representation of the entry (excluding chain fields)."""
        payload = {
            "entry_id": entry.entry_id,
            "tenant_id": entry.tenant_id,
            "case_run_id": entry.case_run_id or "",
            "state_node_id": entry.state_node_id or "",
            "confidence_score": entry.confidence_score,
            "risk_level": entry.risk_level.value,
            "source": entry.source.value,
            "model_id": entry.model_id,
            "model_version": entry.model_version,
            "input_hash": entry.input_hash,
            "reason": entry.reason,
            "evidence_refs": entry.evidence_refs,
            "recorded_at": entry.recorded_at.isoformat(),
        }
        return json.dumps(payload, sort_keys=True, default=str)

    @staticmethod
    def compute_chain_hash(previous_hash: str, entry: ConfidenceLedgerEntry) -> str:
        """SHA-256(previous_hash + canonical(payload))."""
        canonical = ConfidenceLedgerService._canonical_payload(entry)
        raw = f"{previous_hash}:{canonical}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def compute_input_hash(input_data: dict[str, Any]) -> str:
        """SHA-256 of the model input for reproducibility tracking."""
        canonical = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    @staticmethod
    def build_entry(
        *,
        entry_id: str,
        tenant_id: str,
        confidence_score: float,
        risk_level: RiskLevel,
        source: ConfidenceSource,
        reason: str,
        previous_hash: str = GENESIS_HASH,
        case_run_id: str | None = None,
        state_node_id: str | None = None,
        model_id: str = "",
        model_version: str = "",
        input_data: dict[str, Any] | None = None,
        evidence_refs: list[str] | None = None,
        context_data: dict[str, Any] | None = None,
    ) -> ConfidenceLedgerEntry:
        """Build a new ledger entry with computed hashes."""
        input_hash = ""
        if input_data:
            input_hash = ConfidenceLedgerService.compute_input_hash(input_data)

        entry = ConfidenceLedgerEntry(
            entry_id=entry_id,
            tenant_id=tenant_id,
            case_run_id=case_run_id,
            state_node_id=state_node_id,
            confidence_score=confidence_score,
            risk_level=risk_level,
            source=source,
            model_id=model_id,
            model_version=model_version,
            input_hash=input_hash,
            reason=reason,
            evidence_refs=evidence_refs or [],
            context_data=context_data or {},
            previous_hash=previous_hash,
            chain_hash="",  # computed below
        )

        entry.chain_hash = ConfidenceLedgerService.compute_chain_hash(
            previous_hash, entry
        )
        return entry

    @staticmethod
    def verify_chain(entries: list[ConfidenceLedgerEntry]) -> bool:
        """
        Verify integrity of a sequence of ledger entries.

        Returns True if the chain is intact. Raises LedgerChainBroken on the
        first entry whose chain_hash does not match the recomputed value.
        """
        expected_prev = GENESIS_HASH

        for entry in entries:
            if entry.previous_hash != expected_prev:
                raise LedgerChainBroken(
                    f"Entry {entry.entry_id}: previous_hash mismatch. "
                    f"Expected {expected_prev}, got {entry.previous_hash}"
                )

            recomputed = ConfidenceLedgerService.compute_chain_hash(
                entry.previous_hash, entry
            )
            if entry.chain_hash != recomputed:
                raise LedgerChainBroken(
                    f"Entry {entry.entry_id}: chain_hash mismatch. "
                    f"Expected {recomputed}, got {entry.chain_hash}"
                )

            expected_prev = entry.chain_hash

        return True

    @staticmethod
    def latest_confidence(
        entries: list[ConfidenceLedgerEntry],
        source: ConfidenceSource | None = None,
    ) -> ConfidenceLedgerEntry | None:
        """Return the most recent entry, optionally filtered by source."""
        filtered = entries
        if source:
            filtered = [e for e in entries if e.source == source]
        if not filtered:
            return None
        # Ledger entries are append-only and callers hand them in chronological order.
        # Using the last entry avoids unstable ties when recorded_at timestamps are equal.
        return filtered[-1]

    @staticmethod
    def risk_score(entries: list[ConfidenceLedgerEntry]) -> float:
        """
        Derive a composite 0-100 risk score from confidence and discrete risk levels.

        The score intentionally leans conservative:
          - lower confidence raises risk
          - later / more severe entries dominate earlier low-risk ones
          - repeated high-risk entries nudge the aggregate further upward
        """
        if not entries:
            return 0.0

        risk_weight = {
            RiskLevel.NIEDRIG: 0.2,
            RiskLevel.MITTEL: 0.45,
            RiskLevel.HOCH: 0.75,
            RiskLevel.KRITISCH: 1.0,
        }

        weighted = []
        for index, entry in enumerate(entries, start=1):
            confidence_component = 1.0 - entry.confidence_score
            severity_component = risk_weight[entry.risk_level]
            recency_factor = 0.85 + (0.15 * index / len(entries))
            weighted.append(((confidence_component * 0.55) + (severity_component * 0.45)) * recency_factor)

        aggregate = sum(weighted) / len(weighted)
        return round(min(max(aggregate * 100, 0.0), 100.0), 2)

    @staticmethod
    def risk_summary(entries: list[ConfidenceLedgerEntry]) -> dict[str, Any]:
        """Aggregate risk statistics for a case/node."""
        if not entries:
            return {
                "count": 0,
                "avg_confidence": 0.0,
                "min_confidence": 0.0,
                "max_confidence": 0.0,
                "max_risk": None,
                "risk_score": 0.0,
                "latest_confidence": None,
                "latest_risk": None,
                "sources": [],
                "risk_distribution": {risk.value: 0 for risk in RiskLevel},
            }

        scores = [e.confidence_score for e in entries]
        risk_order = [RiskLevel.NIEDRIG, RiskLevel.MITTEL, RiskLevel.HOCH, RiskLevel.KRITISCH]
        max_risk = max(entries, key=lambda e: risk_order.index(e.risk_level)).risk_level
        latest = ConfidenceLedgerService.latest_confidence(entries)
        risk_distribution = {
            risk.value: sum(1 for entry in entries if entry.risk_level == risk)
            for risk in RiskLevel
        }

        return {
            "count": len(entries),
            "avg_confidence": round(sum(scores) / len(scores), 4),
            "min_confidence": min(scores),
            "max_confidence": max(scores),
            "max_risk": max_risk.value,
            "risk_score": ConfidenceLedgerService.risk_score(entries),
            "latest_confidence": latest.confidence_score if latest else None,
            "latest_risk": latest.risk_level.value if latest else None,
            "sources": list({e.source.value for e in entries}),
            "risk_distribution": risk_distribution,
        }
