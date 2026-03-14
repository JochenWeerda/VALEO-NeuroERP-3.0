"""
Settlement-Command-Contracts — Wave 12 AP3/AP4

Typisierte Command-Payloads und Dispatch-Ergebnisse fuer den Settlement-Kernprozess.
Verbindet den Command-Katalog (Wave 11) mit der Prozessreferenzkette (Wave 11).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.core.process_references import ProcessReferenceContext
from app.core.settlement_compatibility import (
    CANONICAL_SETTLEMENT_AGGREGATE,
    CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
)


CommandStatus = Literal["accepted", "rejected", "pending_approval", "executed"]


class SettlementCommandPayload(BaseModel):
    """Eingehende Nutzlast fuer einen Settlement-Command."""

    command_id: str = Field(min_length=1)          # z.B. "settlement.create"
    tenant_id: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    process_ref: ProcessReferenceContext | None = None
    canonical_aggregate_type: str = CANONICAL_SETTLEMENT_AGGREGATE
    canonical_process_definition_key: str = CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY
    params: dict = Field(default_factory=dict)
    idempotency_key: str | None = None
    schema_version: int = 1


class SettlementCommandDispatchResult(BaseModel):
    """Ergebnis der synchronen Command-Validierung und -Weiterleitung."""

    command_id: str
    dispatch_id: str
    tenant_id: str
    status: CommandStatus
    result_ref: str | None = None        # z.B. Settlement-ID nach Anlage
    error_code: str | None = None
    error_detail: str | None = None
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class CommandDispatchLog(BaseModel):
    """Audit-Eintrag fuer einen abgesandten Command."""

    dispatch_id: str
    command_id: str
    tenant_id: str
    actor: str
    status: CommandStatus
    process_ref_chain: dict | None = None      # Serialisierte ProcessReferenceContext.chain
    canonical_aggregate_type: str = CANONICAL_SETTLEMENT_AGGREGATE
    canonical_process_definition_key: str = CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY
    outbox_event_id: str | None = None
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


def build_settlement_dispatch_result(
    payload: SettlementCommandPayload,
    *,
    dispatch_id: str,
    status: CommandStatus = "accepted",
    result_ref: str | None = None,
    error_code: str | None = None,
    error_detail: str | None = None,
) -> SettlementCommandDispatchResult:
    return SettlementCommandDispatchResult(
        command_id=payload.command_id,
        dispatch_id=dispatch_id,
        tenant_id=payload.tenant_id,
        status=status,
        result_ref=result_ref,
        error_code=error_code,
        error_detail=error_detail,
    )


def build_command_dispatch_log(
    result: SettlementCommandDispatchResult,
    *,
    actor: str,
    process_ref: ProcessReferenceContext | None = None,
    outbox_event_id: str | None = None,
) -> CommandDispatchLog:
    return CommandDispatchLog(
        dispatch_id=result.dispatch_id,
        command_id=result.command_id,
        tenant_id=result.tenant_id,
        actor=actor,
        status=result.status,
        process_ref_chain=(
            process_ref.chain.model_dump(mode="json") if process_ref else None
        ),
        canonical_aggregate_type=CANONICAL_SETTLEMENT_AGGREGATE,
        canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
        outbox_event_id=outbox_event_id,
    )
