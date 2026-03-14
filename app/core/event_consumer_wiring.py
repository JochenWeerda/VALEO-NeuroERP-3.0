from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class WiringStatus(str, Enum):
    WIRED = "wired"
    UNWIRED = "unwired"
    DEPRECATED = "deprecated"

class NatsSubjectMapping(BaseModel):
    """Mapping eines NATS-Subjects auf einen ProjectionConsumer."""
    subject_pattern: str        # z.B. "tenant.*.ap_invoice.approved"
    consumer_id: str            # ID des ProjectionConsumer aus Wave 4
    tenant_filter: Optional[str] = None   # None = alle Tenants
    status: WiringStatus = WiringStatus.WIRED
    schema_version: int = 1

class WiringHealthReport(BaseModel):
    """Ergebnis der Verdrahtungspruefung."""
    total_subjects: int
    wired_count: int
    unwired_count: int
    deprecated_count: int
    unwired_subjects: list[str]
    health_pct: float           # wired / total * 100
    schema_version: int = 1

class ConsumerWiringRegistry(BaseModel):
    """Registry aller NATS-Subject -> ProjectionConsumer Mappings."""
    mappings: list[NatsSubjectMapping] = []
    schema_version: int = 1

    def add(self, mapping: NatsSubjectMapping) -> None:
        self.mappings.append(mapping)

    def is_wired(self, subject: str) -> bool:
        """Prueft ob ein Subject einen aktiven Consumer hat."""
        return any(
            m.subject_pattern == subject and m.status == WiringStatus.WIRED
            for m in self.mappings
        )

    def get_consumer_id(self, subject: str) -> Optional[str]:
        for m in self.mappings:
            if m.subject_pattern == subject and m.status == WiringStatus.WIRED:
                return m.consumer_id
        return None

    def health_check(self) -> WiringHealthReport:
        wired = [m for m in self.mappings if m.status == WiringStatus.WIRED]
        unwired = [m for m in self.mappings if m.status == WiringStatus.UNWIRED]
        deprecated = [m for m in self.mappings if m.status == WiringStatus.DEPRECATED]
        total = len(self.mappings)
        return WiringHealthReport(
            total_subjects=total,
            wired_count=len(wired),
            unwired_count=len(unwired),
            deprecated_count=len(deprecated),
            unwired_subjects=[m.subject_pattern for m in unwired],
            health_pct=(len(wired) / total * 100) if total > 0 else 100.0,
        )

    def all_consumer_ids(self) -> list[str]:
        return list({m.consumer_id for m in self.mappings if m.status == WiringStatus.WIRED})

def build_default_wiring() -> ConsumerWiringRegistry:
    """Vordefinierte NATS-Subject -> Consumer Mappings fuer alle Wave-1-6-Events."""
    registry = ConsumerWiringRegistry()

    # Wave 1 - AP-Invoice Events
    for verb in ("approved", "rejected", "posted"):
        registry.add(NatsSubjectMapping(
            subject_pattern=f"tenant.*.ap_invoice.{verb}",
            consumer_id="ap_invoice_cockpit_consumer",
        ))

    # Wave 2 - Finance / Payment Events
    for verb in ("initiated", "executed", "cancelled"):
        registry.add(NatsSubjectMapping(
            subject_pattern=f"tenant.*.payment_run.{verb}",
            consumer_id="payment_run_cockpit_consumer",
        ))

    # Wave 2 - Process Observation
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.process.state_changed",
        consumer_id="process_observation_consumer",
    ))

    # Wave 3 - Evidence und IoT
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.audit_evidence.created",
        consumer_id="audit_evidence_consumer",
    ))
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.iot_device.telemetry",
        consumer_id="iot_telemetry_consumer",
    ))

    # Wave 4 - Workflow und SLA
    for verb in ("started", "completed", "cancelled", "escalated"):
        registry.add(NatsSubjectMapping(
            subject_pattern=f"tenant.*.workflow.{verb}",
            consumer_id="workflow_runtime_consumer",
        ))
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.sla.violated",
        consumer_id="process_sla_consumer",
    ))

    # Wave 5 - Commands und E2E-Kette
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.command.dispatched",
        consumer_id="command_audit_consumer",
    ))
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.e2e_chain.link_completed",
        consumer_id="e2e_chain_consumer",
    ))

    # Wave 6 - Agrar, Settlement, Silo
    for verb in ("created", "finalized"):
        registry.add(NatsSubjectMapping(
            subject_pattern=f"tenant.*.agrar_settlement.{verb}",
            consumer_id="agrar_settlement_consumer",
        ))
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.silo.transfer",
        consumer_id="silo_operations_consumer",
    ))
    registry.add(NatsSubjectMapping(
        subject_pattern="tenant.*.duenge_bilanz.calculated",
        consumer_id="agrar_p0_consumer",
    ))

    return registry
