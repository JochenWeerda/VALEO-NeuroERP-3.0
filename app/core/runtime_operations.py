"""
Runtime Operations — Wave 4 AP6

Betriebsmetriken, Rebuild und Replay für den Process Kernel.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ComponentHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class RuntimeComponent(BaseModel):
    """Betriebszustand einer Process-Kernel-Komponente."""
    component_id: str
    component_type: str     # "workflow_engine", "event_outbox", "projection_consumer", "sla_monitor"
    health: ComponentHealth = ComponentHealth.HEALTHY
    last_heartbeat: Optional[datetime] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = 1


class ReplayRequest(BaseModel):
    """Anforderung zum Replay von Events für eine Projektion oder Instanz."""
    replay_id: str
    tenant_id: str
    target_type: str        # "projection" | "workflow_instance"
    target_id: str
    from_event_id: Optional[str] = None    # None = von Anfang
    to_event_id: Optional[str] = None      # None = bis jetzt
    requested_by: str
    reason: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class RebuildRequest(BaseModel):
    """Anforderung zum vollständigen Rebuild einer Projektion."""
    rebuild_id: str
    tenant_id: str
    projection_name: str
    requested_by: str
    reason: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class RuntimeHealthReport(BaseModel):
    """Gesamtgesundheitsbericht des Process Kernels."""
    tenant_id: str
    overall_health: ComponentHealth
    components: list[RuntimeComponent]
    active_replays: int = 0
    active_rebuilds: int = 0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1

    @classmethod
    def build_default(cls, tenant_id: str) -> "RuntimeHealthReport":
        """Erstellt Standard-Health-Report mit bekannten Komponenten."""
        components = [
            RuntimeComponent(
                component_id="wf-engine-01",
                component_type="workflow_engine",
                health=ComponentHealth.HEALTHY,
                metrics={"active_instances": 0, "completed_today": 0},
            ),
            RuntimeComponent(
                component_id="outbox-01",
                component_type="event_outbox",
                health=ComponentHealth.HEALTHY,
                metrics={"pending_events": 0, "failed_events": 0},
            ),
            RuntimeComponent(
                component_id="proj-consumer-01",
                component_type="projection_consumer",
                health=ComponentHealth.HEALTHY,
                metrics={"lag_count": 0, "last_event_processed": None},
            ),
            RuntimeComponent(
                component_id="sla-monitor-01",
                component_type="sla_monitor",
                health=ComponentHealth.HEALTHY,
                metrics={"active_violations": 0, "escalations_today": 0},
            ),
        ]
        return cls(
            tenant_id=tenant_id,
            overall_health=ComponentHealth.HEALTHY,
            components=components,
        )

    def compute_overall_health(self) -> ComponentHealth:
        """Berechnet Gesamtstatus aus Komponenten-Status."""
        if any(c.health == ComponentHealth.UNHEALTHY for c in self.components):
            return ComponentHealth.UNHEALTHY
        if any(c.health == ComponentHealth.DEGRADED for c in self.components):
            return ComponentHealth.DEGRADED
        return ComponentHealth.HEALTHY
