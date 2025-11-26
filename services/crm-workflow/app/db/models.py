"""SQLAlchemy models for CRM Workflow Service."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class TriggerType(str, Enum):
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class ActionType(str, Enum):
    NOTIFICATION = "notification"
    UPDATE_RECORD = "update_record"
    CREATE_TASK = "create_task"
    ESCALATE = "escalate"
    WEBHOOK = "webhook"


class NotificationType(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    WEBHOOK = "webhook"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


enum_values = lambda enum_cls: [member.value for member in enum_cls]  # noqa: E731


class Workflow(Base):
    __tablename__ = "crm_workflow_workflows"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(
            WorkflowStatus,
            name="crm_workflow_status",
            values_callable=enum_values,
        ),
        default=WorkflowStatus.DRAFT,
        nullable=False,
    )

    trigger_conditions: Mapped[dict] = mapped_column(JSON, nullable=False)  # Conditions that trigger the workflow
    actions: Mapped[list[dict]] = mapped_column(JSON, nullable=False)  # List of actions to execute

    is_active: Mapped[bool] = mapped_column(default=True)
    created_by: Mapped[str | None] = mapped_column(String(64))
    updated_by: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions: Mapped[list["WorkflowExecution"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class Trigger(Base):
    __tablename__ = "crm_workflow_triggers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    trigger_type: Mapped[TriggerType] = mapped_column(
        SQLEnum(
            TriggerType,
            name="crm_workflow_trigger_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    event_type: Mapped[str | None] = mapped_column(String(128))  # For event triggers
    schedule_cron: Mapped[str | None] = mapped_column(String(128))  # For scheduled triggers
    conditions: Mapped[dict] = mapped_column(JSON, nullable=False)  # Filter conditions

    workflow_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_workflow_workflows.id"))
    is_active: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workflow: Mapped[Workflow] = relationship("Workflow")


class WorkflowExecution(Base):
    __tablename__ = "crm_workflow_executions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_workflow_workflows.id"), nullable=False)

    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(
            ExecutionStatus,
            name="crm_workflow_execution_status",
            values_callable=enum_values,
        ),
        default=ExecutionStatus.PENDING,
        nullable=False,
    )

    trigger_event: Mapped[dict] = mapped_column(JSON, nullable=False)  # The event that triggered execution
    execution_context: Mapped[dict] = mapped_column(JSON, nullable=False)  # Variables and context

    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workflow: Mapped[Workflow] = relationship(back_populates="executions")


class Notification(Base):
    __tablename__ = "crm_workflow_notifications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)

    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(
            NotificationType,
            name="crm_workflow_notification_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    recipient: Mapped[str] = mapped_column(String(255), nullable=False)  # Email, user ID, webhook URL
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")  # pending, sent, failed
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)

    workflow_execution_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("crm_workflow_executions.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workflow_execution: Mapped[WorkflowExecution | None] = relationship("WorkflowExecution")