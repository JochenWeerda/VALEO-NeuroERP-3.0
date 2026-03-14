"""
Persistente Workflow-Laufzeit — Wave 4 AP1

Modelliert laufende Workflow-Instanzen mit Checkpoint/Resume/Replay-Faehigkeit.
Produktiv wird der In-Memory-Store durch eine persistente DB ersetzt.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowRuntimeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowCheckpoint(BaseModel):
    """Persistenter Zwischenstand einer Workflow-Instanz (fuer Replay/Resume)."""

    checkpoint_id: str
    step_name: str
    state_snapshot: dict[str, Any]  # serialisierter Zustand
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class WorkflowInstance(BaseModel):
    """Persistente Laufzeit-Instanz eines Workflows."""

    instance_id: str
    tenant_id: str
    process_key: str           # z.B. "ap_invoice_approval"
    definition_version: str    # verweist auf WorkflowDefinition.version
    status: WorkflowRuntimeStatus = WorkflowRuntimeStatus.PENDING
    aggregate_type: str        # z.B. "ap_invoice"
    aggregate_id: str
    current_step: Optional[str] = None
    checkpoints: list[WorkflowCheckpoint] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    schema_version: int = 1

    def add_checkpoint(self, step_name: str, state: dict[str, Any]) -> WorkflowCheckpoint:
        """Fuegt einen neuen Checkpoint hinzu und aktualisiert den aktuellen Schritt."""
        cp = WorkflowCheckpoint(
            checkpoint_id=f"cp-{len(self.checkpoints) + 1}",
            step_name=step_name,
            state_snapshot=state,
        )
        self.checkpoints.append(cp)
        self.current_step = step_name
        self.updated_at = datetime.now(timezone.utc)
        return cp

    def latest_checkpoint(self) -> Optional[WorkflowCheckpoint]:
        """Gibt den zuletzt gespeicherten Checkpoint zurueck."""
        return self.checkpoints[-1] if self.checkpoints else None

    def is_resumable(self) -> bool:
        """Prueft ob die Instanz wiederaufgenommen werden kann."""
        return self.status in (
            WorkflowRuntimeStatus.WAITING_APPROVAL,
            WorkflowRuntimeStatus.FAILED,
        )


class WorkflowRuntimeStore(BaseModel):
    """In-Memory-Store fuer Workflow-Instanzen (Produktiv: persistente DB)."""

    instances: list[WorkflowInstance] = Field(default_factory=list)
    schema_version: int = 1

    def get(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Gibt eine Instanz anhand ihrer ID zurueck."""
        return next(
            (i for i in self.instances if i.instance_id == instance_id), None
        )

    def get_by_aggregate(
        self, aggregate_type: str, aggregate_id: str
    ) -> list[WorkflowInstance]:
        """Gibt alle Instanzen fuer ein bestimmtes Aggregat zurueck."""
        return [
            i
            for i in self.instances
            if i.aggregate_type == aggregate_type and i.aggregate_id == aggregate_id
        ]

    def get_by_status(self, status: WorkflowRuntimeStatus) -> list[WorkflowInstance]:
        """Gibt alle Instanzen mit einem bestimmten Status zurueck."""
        return [i for i in self.instances if i.status == status]

    def upsert(self, instance: WorkflowInstance) -> None:
        """Fuegt eine Instanz ein oder aktualisiert sie."""
        for idx, existing in enumerate(self.instances):
            if existing.instance_id == instance.instance_id:
                self.instances[idx] = instance
                return
        self.instances.append(instance)
