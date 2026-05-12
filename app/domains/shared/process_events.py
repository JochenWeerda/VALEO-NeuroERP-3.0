"""
Process Kernel Events — Wave 2
Versionierte Kernprozess-Events fuer AP-Freigabe, Annahme, Qualitaet und Settlement.

Event-Namenskonvention (NATS-Subject):
  {tenant_id}.{domain}.{aggregate}.{verb}

  Beispiele:
    tenant1.finance.ap_invoice.approval_requested
    tenant1.finance.ap_invoice.approved
    tenant1.finance.ap_invoice.rejected
    tenant1.finance.ap_invoice.posted
    tenant1.agrar.harvest_acceptance.completed
    tenant1.agrar.quality_protocol.completed
    tenant1.agrar.settlement.posted

Wildcards fuer Consumer:
  *.finance.>          alle Finance-Events aller Tenants
  tenant1.>            alle Events von tenant1
  *.*.ap_invoice.*     alle AP-Invoice-Events aller Tenants und Domains
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domains.shared.events import DomainEvent


# ---------------------------------------------------------------------------
# Hilfsfunktion: NATS-Subject aus Event ableiten
# ---------------------------------------------------------------------------

def build_event_subject(event: "ProcessKernelEvent") -> str:
    """Gibt den NATS-Subject-String fuer ein Kernprozess-Event zurueck.

    Format: {tenant_id}.{domain}.{aggregate}.{verb}
    """
    return f"{event.tenant_id}.{event.domain}.{event.aggregate}.{event.verb}"


# ---------------------------------------------------------------------------
# Basis fuer alle Kernprozess-Events
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class ProcessKernelEvent(DomainEvent):
    """Basis fuer alle versionierten Kernprozess-Events."""

    tenant_id: str
    domain: str          # finance | agrar | lager | ...
    aggregate: str       # ap_invoice | harvest_acceptance | quality_protocol | ...
    verb: str            # approval_requested | approved | rejected | posted | completed | ...
    schema_version: int = 1
    workflow_instance_id: str | None = None


# ---------------------------------------------------------------------------
# Finance / AP-Invoice Events
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class APInvoiceApprovalRequested(ProcessKernelEvent):
    """Freigabeanforderung fuer eine Eingangsrechnung."""

    invoice_id: str
    requested_by: str
    required_approvals: int
    rule_id: str

    domain: str = field(default="finance", init=False)
    aggregate: str = field(default="ap_invoice", init=False)
    verb: str = field(default="approval_requested", init=False)


@dataclass(kw_only=True)
class APInvoiceApprovalGranted(ProcessKernelEvent):
    """Ein Freigabeschritt fuer eine Eingangsrechnung wurde erteilt."""

    invoice_id: str
    approved_by: str
    current_approvals: int
    required_approvals: int
    rule_id: str

    domain: str = field(default="finance", init=False)
    aggregate: str = field(default="ap_invoice", init=False)
    verb: str = field(default="approval_granted", init=False)


@dataclass(kw_only=True)
class APInvoiceApproved(ProcessKernelEvent):
    """Eingangsrechnung ist vollstaendig freigegeben."""

    invoice_id: str
    approved_by: str
    rule_id: str

    domain: str = field(default="finance", init=False)
    aggregate: str = field(default="ap_invoice", init=False)
    verb: str = field(default="approved", init=False)


@dataclass(kw_only=True)
class APInvoiceRejected(ProcessKernelEvent):
    """Eingangsrechnung wurde im Freigabeworkflow abgelehnt."""

    invoice_id: str
    rejected_by: str
    rule_id: str

    domain: str = field(default="finance", init=False)
    aggregate: str = field(default="ap_invoice", init=False)
    verb: str = field(default="rejected", init=False)


@dataclass(kw_only=True)
class APInvoicePosted(ProcessKernelEvent):
    """Eingangsrechnung wurde verbucht (GL-Buchung erzeugt)."""

    invoice_id: str
    posted_by: str
    journal_entry_id: str | None

    domain: str = field(default="finance", init=False)
    aggregate: str = field(default="ap_invoice", init=False)
    verb: str = field(default="posted", init=False)


# ---------------------------------------------------------------------------
# Agrar / Harvest Acceptance Events
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class HarvestAcceptanceCompleted(ProcessKernelEvent):
    """Annahmevorgang abgeschlossen und freigegeben."""

    acceptance_id: str
    contract_id: str | None
    supplier_id: str | None
    article_id: str | None
    net_weight: float | None

    domain: str = field(default="agrar", init=False)
    aggregate: str = field(default="harvest_acceptance", init=False)
    verb: str = field(default="completed", init=False)


# ---------------------------------------------------------------------------
# Agrar / Quality Protocol Events
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class QualityProtocolCompleted(ProcessKernelEvent):
    """Qualitaetsprotokoll abgeschlossen."""

    protocol_id: str
    acceptance_id: str | None
    contract_id: str | None

    domain: str = field(default="agrar", init=False)
    aggregate: str = field(default="quality_protocol", init=False)
    verb: str = field(default="completed", init=False)


# ---------------------------------------------------------------------------
# Flow Spine Events (Wave 104 — GAP-104-G)
# ---------------------------------------------------------------------------

@dataclass(kw_only=True)
class FlowSpineInstanceCreated(ProcessKernelEvent):
    """Flow-Spine-Prozessinstanz wurde angelegt."""

    instance_id: str
    process_key: str
    case_number: str
    label: str
    entry_mode: str | None = None
    linked_document_type: str | None = None

    domain: str = field(default="operations", init=False)
    aggregate: str = field(default="flow_spine", init=False)
    verb: str = field(default="instance_created", init=False)


@dataclass(kw_only=True)
class FlowSpineTransitionOccurred(ProcessKernelEvent):
    """Flow-Spine-Knoten wechselte den Status."""

    instance_id: str
    process_key: str
    node_id: str
    new_status: str   # ok | active | pending | warning | error
    action_label: str
    actor_id: str | None = None

    domain: str = field(default="operations", init=False)
    aggregate: str = field(default="flow_spine", init=False)
    verb: str = field(default="transition_occurred", init=False)
