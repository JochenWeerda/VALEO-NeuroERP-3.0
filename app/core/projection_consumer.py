"""
Asynchrone Projektionen und Consumer — Wave 4 AP2

Beschreibt Read-Model-Consumer, die auf NATS-Events hoeren,
und steuert Rebuild-Prozesse fuer Projektionen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProjectionStatus(str, Enum):
    CURRENT = "current"       # up-to-date
    STALE = "stale"           # hinter Event-Stream zurueck
    REBUILDING = "rebuilding"
    ERROR = "error"


class ProjectionConsumer(BaseModel):
    """Beschreibt einen Read-Model-Consumer, der auf Events hoert."""

    consumer_id: str
    projection_name: str        # z.B. "ap_invoice_cockpit"
    event_subjects: list[str]   # NATS-Subjects, z.B. ["*.finance.ap_invoice.*"]
    last_event_id: Optional[str] = None
    last_updated: Optional[datetime] = None
    status: ProjectionStatus = ProjectionStatus.STALE
    lag_count: int = 0          # Events hinter aktuellem Stand
    schema_version: int = 1

    def mark_current(self, event_id: str) -> None:
        """Markiert den Consumer als aktuell und setzt den letzten Event."""
        self.last_event_id = event_id
        self.last_updated = datetime.now(timezone.utc)
        self.status = ProjectionStatus.CURRENT
        self.lag_count = 0

    def mark_stale(self, lag: int) -> None:
        """Markiert den Consumer als veraltet mit der angegebenen Rueckstandszahl."""
        self.status = ProjectionStatus.STALE
        self.lag_count = lag


class RebuildPolicy(BaseModel):
    """Regeln fuer Projektion-Rebuild (Backfill)."""

    projection_name: str
    rebuild_from: str          # "beginning" | ISO-datetime
    batch_size: int = 100
    require_approval: bool = False  # fuer produktive Projections
    schema_version: int = 1


class RebuildRequest(BaseModel):
    """Anforderung fuer den Rebuild einer Projektion."""

    projection_name: str
    requested_by: str
    tenant_id: str
    rebuild_from: str = "beginning"
    reason: str
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "accepted"
    schema_version: int = 1


class ProjectionRegistry(BaseModel):
    """Registry aller bekannten Projektion-Consumer."""

    consumers: list[ProjectionConsumer] = Field(default_factory=list)
    schema_version: int = 1

    def get(self, projection_name: str) -> Optional[ProjectionConsumer]:
        """Gibt den Consumer fuer eine bestimmte Projektion zurueck."""
        return next(
            (c for c in self.consumers if c.projection_name == projection_name), None
        )

    def get_stale(self) -> list[ProjectionConsumer]:
        """Gibt alle Consumer zurueck, die veraltet sind."""
        return [c for c in self.consumers if c.status == ProjectionStatus.STALE]


def build_default_projection_registry() -> ProjectionRegistry:
    """Erstellt die Standard-Projektion-Registry mit den Cockpit-Consumers."""
    consumers = [
        ProjectionConsumer(
            consumer_id="consumer-ap-invoice-cockpit",
            projection_name="ap_invoice_cockpit",
            event_subjects=[
                "*.finance.ap_invoice.created",
                "*.finance.ap_invoice.approved",
                "*.finance.ap_invoice.rejected",
                "*.finance.ap_invoice.posted",
            ],
        ),
        ProjectionConsumer(
            consumer_id="consumer-payment-run-cockpit",
            projection_name="payment_run_cockpit",
            event_subjects=[
                "*.finance.payment_run.created",
                "*.finance.payment_run.approved",
                "*.finance.payment_run.executed",
                "*.finance.payment_run.failed",
            ],
        ),
        ProjectionConsumer(
            consumer_id="consumer-process-observation",
            projection_name="process_observation",
            event_subjects=[
                "*.workflow.instance.started",
                "*.workflow.instance.completed",
                "*.workflow.instance.failed",
                "*.workflow.instance.cancelled",
                "*.workflow.checkpoint.recorded",
            ],
        ),
    ]
    return ProjectionRegistry(consumers=consumers)
