"""
Chat-native process execution, approval handling and audit surfacing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionService,
    ActionExecutionStatus,
)
from app.core.human_approval_gate import (
    ApprovalDecision,
    ApprovalRisikostufe,
    evaluate_approval_requirement,
    get_default_approval_rules,
    record_approval_decision,
)
from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.process_audit_contracts import (
    ProcessDecisionReason,
    build_action_execution_audit_entry,
    build_process_audit_entry,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChannelThreadAuditItem:
    audit_type: str
    payload: dict[str, Any]
    recorded_at: str = field(default_factory=lambda: _utcnow().isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {
            "audit_type": self.audit_type,
            "payload": self.payload,
            "recorded_at": self.recorded_at,
        }


@dataclass
class ChannelProcessThread:
    thread_id: str
    kanal: str
    tenant_id: str
    process_definition_key: str
    command_name: str
    aggregate_type: str
    aggregate_id: str
    rolle: str
    issuer_type: str
    employee_ref: str | None
    channel_user_id: str | None
    request_payload: dict[str, Any]
    status: str
    execution: dict[str, Any]
    approval_requirement: dict[str, Any] | None = None
    approval_record: dict[str, Any] | None = None
    audit_trail: list[ChannelThreadAuditItem] = field(default_factory=list)
    message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "kanal": self.kanal,
            "tenant_id": self.tenant_id,
            "process_definition_key": self.process_definition_key,
            "command_name": self.command_name,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "rolle": self.rolle,
            "issuer_type": self.issuer_type,
            "employee_ref": self.employee_ref,
            "channel_user_id": self.channel_user_id,
            "request_payload": self.request_payload,
            "status": self.status,
            "execution": self.execution,
            "approval_requirement": self.approval_requirement,
            "approval_record": self.approval_record,
            "audit_trail": [item.as_dict() for item in self.audit_trail],
            "message": self.message,
        }


class ChannelProcessThreadStore:
    def __init__(self) -> None:
        self._threads: dict[str, ChannelProcessThread] = {}

    def save(self, thread: ChannelProcessThread) -> ChannelProcessThread:
        self._threads[thread.thread_id] = thread
        return thread

    def get(self, thread_id: str) -> ChannelProcessThread | None:
        return self._threads.get(thread_id)

    def list_threads(
        self,
        *,
        kanal: str | None = None,
        tenant_id: str | None = None,
        status: str | None = None,
        process_definition_key: str | None = None,
        limit: int = 50,
    ) -> list[ChannelProcessThread]:
        items = list(self._threads.values())
        if kanal:
            items = [item for item in items if item.kanal == kanal]
        if tenant_id:
            items = [item for item in items if item.tenant_id == tenant_id]
        if status:
            items = [item for item in items if item.status == status]
        if process_definition_key:
            items = [
                item for item in items if item.process_definition_key == process_definition_key
            ]
        return items[: max(limit, 1)]

    def get_audit_trail(self, thread_id: str) -> list[ChannelThreadAuditItem] | None:
        thread = self.get(thread_id)
        if thread is None:
            return None
        return list(thread.audit_trail)

    def clear(self) -> None:
        self._threads.clear()


_THREAD_STORE = ChannelProcessThreadStore()


def get_channel_process_thread_store(db: Any | None = None) -> ChannelProcessThreadStore:
    if db is not None:
        from app.repositories.channel_thread_repository import PersistentChannelProcessThreadStore

        return PersistentChannelProcessThreadStore(db)
    return _THREAD_STORE


def _normalize_channel(kanal: str | KnowledgeChannel) -> KnowledgeChannel:
    if isinstance(kanal, KnowledgeChannel):
        return kanal
    return KnowledgeChannel(kanal.strip().upper())


def _map_command_to_aktions_typ(command_name: str) -> str:
    mapping = {
        "FinalizeAgrarSettlement": "SETTLEMENT_VERBUCHEN",
        "CreateAgrarSettlement": "SETTLEMENT_FREIGABE",
        "ExecutePaymentRun": "ZAHLUNGSLAUF_STARTEN",
        "ExecuteDirectDebit": "ZAHLUNG_AUSLOESEN",
        "PostAPInvoice": "BUCHUNG_FREIGABE",
    }
    return mapping.get(command_name, command_name.upper())


def _build_channel_message(
    *,
    kanal: KnowledgeChannel,
    command_name: str,
    result_status: str,
    approval_requirement: dict[str, Any] | None = None,
) -> str:
    if result_status == ActionExecutionStatus.PENDING_APPROVAL.value and approval_requirement:
        role = approval_requirement.get("freigabe_rolle", "freigeber")
        return (
            f"{command_name} ist im Kanal erfasst und wartet auf Freigabe durch Rolle '{role}'."
        )
    if result_status == ActionExecutionStatus.ACCEPTED.value:
        prefix = "Slack" if kanal == KnowledgeChannel.SLACK else "Teams"
        return f"{prefix}-Aktion {command_name} wurde fachlich akzeptiert und auditiert."
    if result_status == ActionExecutionStatus.REJECTED.value:
        return f"{command_name} wurde abgewiesen. Details stehen im Audit-Trail."
    return f"{command_name} wurde mit Status '{result_status}' verarbeitet."


def _build_reference_context(
    *,
    kanal: KnowledgeChannel,
    process_definition_key: str,
    aggregate_type: str,
    aggregate_id: str,
    channel_user_id: str | None,
    employee_ref: str | None,
    extra_context: dict[str, Any] | None,
) -> dict[str, Any]:
    context = dict(extra_context or {})
    context.update(
        {
            "process_key": process_definition_key,
            "anchor_entity": aggregate_type,
            "anchor_id": aggregate_id,
            "canonical_process_definition_key": process_definition_key,
            "canonical_anchor_entity": aggregate_type,
            "chain": {},
        }
    )
    if aggregate_type == "agrar_settlement":
        context["chain"]["settlement_id"] = aggregate_id
    elif aggregate_type == "quality_protocol":
        context["chain"]["quality_protocol_id"] = aggregate_id
    elif aggregate_type == "harvest_acceptance":
        context["chain"]["harvest_acceptance_id"] = aggregate_id
    if channel_user_id:
        context["chain"]["supplier_id"] = channel_user_id
    if employee_ref:
        context["chain"]["article_id"] = employee_ref
    context["channel_metadata"] = {"channel": kanal.value}
    return context


def _build_approval_requirement_for_request(
    command_name: str,
    payload: dict[str, Any],
    extra_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(extra_context or {})
    context.update(payload)
    requirement = evaluate_approval_requirement(
        _map_command_to_aktions_typ(command_name),
        context,
        get_default_approval_rules(),
    )
    return requirement.as_dict()


def execute_channel_process_action(
    *,
    kanal: str | KnowledgeChannel,
    tenant_id: str,
    process_definition_key: str,
    command_name: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    issuer_role: str,
    issuer_type: str,
    idempotency_key: str,
    employee_ref: str | None = None,
    channel_user_id: str | None = None,
    extra_context: dict[str, Any] | None = None,
    store: ChannelProcessThreadStore | None = None,
) -> ChannelProcessThread:
    normalized_channel = _normalize_channel(kanal)
    reference_context = _build_reference_context(
        kanal=normalized_channel,
        process_definition_key=process_definition_key,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        channel_user_id=channel_user_id,
        employee_ref=employee_ref,
        extra_context=extra_context,
    )
    request = ActionExecutionRequest(
        command_name=command_name,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        tenant_id=tenant_id,
        issuer_role=issuer_role,
        issuer_type=issuer_type,
        idempotency_key=idempotency_key,
        human_confirmation=False,
        reference_context=reference_context,
        process_definition_key=process_definition_key,
    )
    result = ActionExecutionService().execute(request)
    action_audit = build_action_execution_audit_entry(request, result)
    approval_requirement = None
    if result.status == ActionExecutionStatus.PENDING_APPROVAL:
        approval_requirement = _build_approval_requirement_for_request(
            command_name,
            payload,
            extra_context=reference_context,
        )

    thread = ChannelProcessThread(
        thread_id=f"cht-{uuid4().hex[:12]}",
        kanal=normalized_channel.value,
        tenant_id=tenant_id,
        process_definition_key=process_definition_key,
        command_name=command_name,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        rolle=issuer_role,
        issuer_type=issuer_type,
        employee_ref=employee_ref,
        channel_user_id=channel_user_id,
        request_payload=request.model_dump(mode="json"),
        status=result.status.value,
        execution=result.model_dump(mode="json"),
        approval_requirement=approval_requirement,
        audit_trail=[
            ChannelThreadAuditItem(
                audit_type="action_execution",
                payload=action_audit.model_dump(mode="json"),
            )
        ],
        message=_build_channel_message(
            kanal=normalized_channel,
            command_name=command_name,
            result_status=result.status.value,
            approval_requirement=approval_requirement,
        ),
    )
    return (store or get_channel_process_thread_store()).save(thread)


def decide_channel_process_action(
    *,
    thread_id: str,
    decision: ApprovalDecision,
    entschieden_von: str,
    approver_role: str,
    begruendung: str,
    store: ChannelProcessThreadStore | None = None,
) -> ChannelProcessThread:
    resolved_store = store or get_channel_process_thread_store()
    thread = resolved_store.get(thread_id)
    if thread is None:
        raise KeyError(f"Thread {thread_id!r} nicht gefunden")
    if thread.status != ActionExecutionStatus.PENDING_APPROVAL.value:
        raise ValueError("Nur pending_approval Threads koennen entschieden werden")

    approval_requirement = thread.approval_requirement or {}
    risiko_stufe = ApprovalRisikostufe(approval_requirement.get("risiko_stufe", ApprovalRisikostufe.HOCH.value))
    approval_record = record_approval_decision(
        aktions_typ=_map_command_to_aktions_typ(thread.command_name),
        instanz_id=thread.aggregate_id,
        agent_id=thread.channel_user_id or thread.rolle,
        risiko_stufe=risiko_stufe,
        decision=decision,
        entschieden_von=entschieden_von,
        begruendung=begruendung,
        kontext=thread.request_payload,
    )
    thread.approval_record = approval_record.as_dict()
    thread.audit_trail.append(
        ChannelThreadAuditItem(
            audit_type="approval_record",
            payload=thread.approval_record,
        )
    )

    if decision == ApprovalDecision.GENEHMIGT:
        rerun_request = ActionExecutionRequest(**thread.request_payload)
        rerun_request.human_confirmation = True
        rerun_request.idempotency_key = f"{rerun_request.idempotency_key}-approved"
        result = ActionExecutionService().execute(rerun_request)
        execution_audit = build_action_execution_audit_entry(rerun_request, result)
        thread.execution = result.model_dump(mode="json")
        thread.status = result.status.value
        thread.message = (
            f"Freigabe durch '{approver_role}' erfasst. {thread.command_name} wurde erneut ausgefuehrt."
        )
        thread.audit_trail.append(
            ChannelThreadAuditItem(
                audit_type="action_execution",
                payload=execution_audit.model_dump(mode="json"),
            )
        )
        return resolved_store.save(thread)

    rejection_audit = build_process_audit_entry(
        audit_entry_id=f"reject-{thread.thread_id}",
        tenant_id=thread.tenant_id,
        process_definition_key=thread.process_definition_key,
        aggregate_type=thread.aggregate_type,
        aggregate_id=thread.aggregate_id,
        action_name="ChannelApprovalRejected",
        actor_type="human",
        actor_id=approver_role,
        decision_reason=ProcessDecisionReason(
            code="APPROVAL_REJECTED",
            summary="Chat-Kanal-Freigabe wurde abgelehnt",
            detail=begruendung,
        ),
        reference_context={
            "channel": thread.kanal,
            "thread_id": thread.thread_id,
            "approver_role": approver_role,
        },
    )
    thread.status = "rejected"
    thread.message = f"Freigabe fuer {thread.command_name} wurde im Kanal abgelehnt."
    thread.audit_trail.append(
        ChannelThreadAuditItem(
            audit_type="process_decision",
            payload=rejection_audit.model_dump(mode="json"),
        )
    )
    return resolved_store.save(thread)
