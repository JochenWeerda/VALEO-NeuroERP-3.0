"""
Repository for persistent channel process threads.
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.channel_process_actions import (
    ChannelProcessThread,
    ChannelProcessThreadStore,
    ChannelThreadAuditItem,
    get_channel_process_thread_store,
)
from app.models.channel_threads import (
    ChannelProcessThreadRecord,
    ChannelThreadAuditItemRecord,
)


class PersistentChannelProcessThreadStore(ChannelProcessThreadStore):
    def __init__(self, db: Session):
        self.db = db

    def save(self, thread: ChannelProcessThread) -> ChannelProcessThread:
        record = self.db.get(ChannelProcessThreadRecord, thread.thread_id)
        if record is None:
            record = ChannelProcessThreadRecord(thread_id=thread.thread_id)
            self.db.add(record)

        record.kanal = thread.kanal
        record.tenant_id = thread.tenant_id
        record.process_definition_key = thread.process_definition_key
        record.command_name = thread.command_name
        record.aggregate_type = thread.aggregate_type
        record.aggregate_id = thread.aggregate_id
        record.rolle = thread.rolle
        record.issuer_type = thread.issuer_type
        record.employee_ref = thread.employee_ref
        record.channel_user_id = thread.channel_user_id
        record.request_payload = dict(thread.request_payload)
        record.status = thread.status
        record.execution = dict(thread.execution)
        record.approval_requirement = (
            dict(thread.approval_requirement) if thread.approval_requirement is not None else None
        )
        record.approval_record = dict(thread.approval_record) if thread.approval_record is not None else None
        record.message = thread.message
        record.is_active = thread.status == "pending_approval"

        record.audit_items.clear()
        for position, item in enumerate(thread.audit_trail):
            record.audit_items.append(
                ChannelThreadAuditItemRecord(
                    position=position,
                    audit_type=item.audit_type,
                    payload=dict(item.payload),
                    recorded_at=item.recorded_at,
                )
            )

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return get_channel_process_thread_store().save(thread)
        self.db.refresh(record)
        return self._to_domain(record)

    def get(self, thread_id: str) -> ChannelProcessThread | None:
        stmt = (
            select(ChannelProcessThreadRecord)
            .where(ChannelProcessThreadRecord.thread_id == thread_id)
        )
        record = self.db.execute(stmt).unique().scalar_one_or_none()
        if record is None:
            return get_channel_process_thread_store().get(thread_id)
        return self._to_domain(record)

    def clear(self) -> None:
        self.db.query(ChannelThreadAuditItemRecord).delete()
        self.db.query(ChannelProcessThreadRecord).delete()
        self.db.commit()
        get_channel_process_thread_store().clear()

    @staticmethod
    def _to_domain(record: ChannelProcessThreadRecord) -> ChannelProcessThread:
        return ChannelProcessThread(
            thread_id=record.thread_id,
            kanal=record.kanal,
            tenant_id=record.tenant_id,
            process_definition_key=record.process_definition_key,
            command_name=record.command_name,
            aggregate_type=record.aggregate_type,
            aggregate_id=record.aggregate_id,
            rolle=record.rolle,
            issuer_type=record.issuer_type,
            employee_ref=record.employee_ref,
            channel_user_id=record.channel_user_id,
            request_payload=dict(record.request_payload or {}),
            status=record.status,
            execution=dict(record.execution or {}),
            approval_requirement=dict(record.approval_requirement or {}) if record.approval_requirement else None,
            approval_record=dict(record.approval_record or {}) if record.approval_record else None,
            audit_trail=[
                ChannelThreadAuditItem(
                    audit_type=item.audit_type,
                    payload=dict(item.payload or {}),
                    recorded_at=item.recorded_at,
                )
                for item in sorted(record.audit_items, key=lambda entry: entry.position)
            ],
            message=record.message or "",
        )
