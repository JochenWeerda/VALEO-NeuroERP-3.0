"""
Business Command Layer — Wave 5 Paket A.

Formale Business-Commands mit Preconditions, Rollenfilter und CommandResult.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Any
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CommandStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING_APPROVAL = "pending_approval"
    EXECUTED = "executed"
    FAILED = "failed"


class CommandError(BaseModel):
    code: str           # z.B. "PRECONDITION_FAILED", "POLICY_BLOCKED", "NOT_FOUND"
    message: str
    detail: Optional[str] = None
    schema_version: int = 1


class CommandResult(BaseModel):
    command_id: str
    status: CommandStatus
    aggregate_type: str
    aggregate_id: str
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    explainability: Optional[dict] = None   # serialisierter ExplainabilityView
    error: Optional[CommandError] = None
    schema_version: int = 1


class BusinessCommand(BaseModel):
    """Basisklasse fuer alle ausfuehrbaren Business-Commands."""
    command_id: str                         # UUID, vom Aufrufer gesetzt
    tenant_id: str
    aggregate_type: str                     # z.B. "ap_invoice"
    aggregate_id: str
    command_name: str                       # z.B. "ApproveAPInvoice"
    process_definition_key: Optional[str] = None
    workflow_key: Optional[str] = None
    workflow_version_number: Optional[int] = None
    issued_by: str                          # User-ID oder Agent-ID
    idempotency_key: str                    # fuer sichere Wiederholung
    payload: dict[str, Any] = Field(default_factory=dict)
    requires_human_confirmation: bool = False
    schema_version: int = 1


class CommandPrecondition(BaseModel):
    """Vorbedingung, die vor einem Command erfuellt sein muss."""
    field: str
    operator: str           # "eq", "in", "not_in", "gt", "gte"
    expected: Any
    error_code: str = "PRECONDITION_FAILED"
    schema_version: int = 1

    def evaluate(self, actual_value: Any) -> bool:
        if self.operator == "eq":
            return actual_value == self.expected
        if self.operator == "in":
            return actual_value in self.expected
        if self.operator == "not_in":
            return actual_value not in self.expected
        if self.operator == "gt":
            return actual_value > self.expected
        if self.operator == "gte":
            return actual_value >= self.expected
        return False


class CommandDefinition(BaseModel):
    """Formale Definition eines Commands (erweiterter ProcessCommandDefinition)."""
    command_name: str                       # z.B. "ApproveAPInvoice"
    aggregate_type: str
    preconditions: list[CommandPrecondition] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=list)
    allowed_agent_types: list[str] = Field(default_factory=list)
    requires_human_confirmation: bool = False
    idempotent: bool = False
    post_event: Optional[str] = None        # z.B. "APInvoiceApproved"
    schema_version: int = 1


def build_core_command_catalog() -> list[CommandDefinition]:
    """Vollstaendiger Kern-Command-Katalog fuer alle Kernprozessschritte."""
    return [
        CommandDefinition(
            command_name="ApproveAPInvoice",
            aggregate_type="ap_invoice",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="in",
                    expected=["ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN"],
                    error_code="WRONG_STATUS",
                ),
            ],
            allowed_roles=["finance_manager", "ap_approver"],
            allowed_agent_types=["audit_agent"],
            requires_human_confirmation=False,
            idempotent=False,
            post_event="APInvoiceApproved",
        ),
        CommandDefinition(
            command_name="RejectAPInvoice",
            aggregate_type="ap_invoice",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="in",
                    expected=["ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN"],
                    error_code="WRONG_STATUS",
                ),
            ],
            allowed_roles=["finance_manager", "ap_approver"],
            allowed_agent_types=[],
            requires_human_confirmation=False,
            post_event="APInvoiceRejected",
        ),
        CommandDefinition(
            command_name="PostAPInvoice",
            aggregate_type="ap_invoice",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="eq",
                    expected="FREIGEGEBEN",
                    error_code="NOT_APPROVED",
                ),
            ],
            allowed_roles=["finance_manager", "accountant"],
            allowed_agent_types=[],
            requires_human_confirmation=True,
            idempotent=True,
            post_event="APInvoicePosted",
        ),
        CommandDefinition(
            command_name="FinalizeHarvestAcceptance",
            aggregate_type="harvest_acceptance",
            preconditions=[
                CommandPrecondition(
                    field="release_status",
                    operator="eq",
                    expected="final",
                    error_code="NOT_FINAL",
                ),
            ],
            allowed_roles=["acceptance_manager", "warehouse_manager"],
            allowed_agent_types=["acceptance_agent"],
            post_event="HarvestAcceptanceCompleted",
        ),
        CommandDefinition(
            command_name="ReleaseQualityProtocol",
            aggregate_type="quality_protocol",
            preconditions=[
                CommandPrecondition(
                    field="approved_by",
                    operator="not_in",
                    expected=["", None],
                    error_code="NO_APPROVER",
                ),
            ],
            allowed_roles=["quality_manager", "lab_manager"],
            allowed_agent_types=["quality_agent"],
            post_event="QualityProtocolCompleted",
        ),
        CommandDefinition(
            command_name="CreateAgrarSettlement",
            aggregate_type="agrar_settlement",
            preconditions=[],
            allowed_roles=["settlement_manager", "agrar_manager"],
            allowed_agent_types=["settlement_agent"],
            post_event="AgrarSettlementCreated",
        ),
        CommandDefinition(
            command_name="FinalizeAgrarSettlement",
            aggregate_type="agrar_settlement",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="eq",
                    expected="DRAFT",
                    error_code="WRONG_STATUS",
                ),
            ],
            allowed_roles=["settlement_manager"],
            allowed_agent_types=[],
            requires_human_confirmation=True,
            post_event="AgrarSettlementFinalized",
        ),
        CommandDefinition(
            command_name="ExecutePaymentRun",
            aggregate_type="payment_run",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="eq",
                    expected="FREIGEGEBEN",
                    error_code="NOT_APPROVED",
                ),
            ],
            allowed_roles=["treasury_manager"],
            allowed_agent_types=[],
            requires_human_confirmation=True,
            idempotent=True,
            post_event="PaymentRunExecuted",
        ),
        CommandDefinition(
            command_name="ExecuteDirectDebit",
            aggregate_type="direct_debit_run",
            preconditions=[
                CommandPrecondition(
                    field="status",
                    operator="eq",
                    expected="FREIGEGEBEN",
                    error_code="NOT_APPROVED",
                ),
            ],
            allowed_roles=["treasury_manager"],
            allowed_agent_types=[],
            requires_human_confirmation=True,
            post_event="DirectDebitExecuted",
        ),
        CommandDefinition(
            command_name="CreatePurchaseOrder",
            aggregate_type="purchase_order",
            preconditions=[
                CommandPrecondition(
                    field="approval_status",
                    operator="eq",
                    expected="approved",
                    error_code="NOT_APPROVED",
                ),
            ],
            allowed_roles=["buyer", "einkauf_manager"],
            allowed_agent_types=["procurement_agent"],
            post_event="PurchaseOrderCreated",
        ),
    ]
