"""
Neuro State Graph -- Lane B, Slice 1

Unified business-object state tracking for the Neuro-Core AI Agent Orchestrator.
Tracks state nodes (Bestellung, Rechnung, Lagerbestand, Kunde, Freigabestatus)
and directed edges (transitions) between them.

Each transition is append-only: nodes gain new states, old states are never deleted.

Integration points:
  - CaseRun (neuroassist_contracts) references a state_graph_id
  - NeuroAssistAuditRecord can include state_graph_snapshot as evidence
  - Action & Policy Layer queries current node states before command dispatch
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StateNodeType(str, Enum):
    """Business-object types tracked by the Neuro State Graph."""
    BESTELLUNG = "bestellung"
    RECHNUNG = "rechnung"
    LAGERBESTAND = "lagerbestand"
    KUNDE = "kunde"
    FREIGABE = "freigabe"
    LIEFERSCHEIN = "lieferschein"
    KONTRAKT = "kontrakt"
    GUTSCHRIFT = "gutschrift"


class StatePhase(str, Enum):
    """Canonical lifecycle phases shared across all node types."""
    ENTWURF = "entwurf"
    OFFEN = "offen"
    IN_BEARBEITUNG = "in_bearbeitung"
    FREIGEGEBEN = "freigegeben"
    ABGESCHLOSSEN = "abgeschlossen"
    STORNIERT = "storniert"
    ARCHIVIERT = "archiviert"


class EdgeRelation(str, Enum):
    """Semantic relationship between two state nodes."""
    ERZEUGT = "erzeugt"           # Bestellung -> Lieferschein
    REFERENZIERT = "referenziert"  # Rechnung -> Bestellung
    BLOCKIERT = "blockiert"        # Freigabe -> Rechnung
    FOLGT_AUF = "folgt_auf"       # Gutschrift -> Rechnung
    ENTHAELT = "enthaelt"         # Kontrakt -> Bestellung


# ---------------------------------------------------------------------------
# State Graph Models (Pydantic -- runtime)
# ---------------------------------------------------------------------------

class StateNode(BaseModel):
    """One business-object node in the state graph."""

    node_id: str = Field(min_length=3, description="UUID or domain-key of this node")
    node_type: StateNodeType
    phase: StatePhase
    tenant_id: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1, description="Domain aggregate ID (e.g. order number)")
    aggregate_type: str = Field(min_length=1, description="e.g. SalesOrder, PurchaseOrder")
    label: str = Field(min_length=1, description="Human-readable label for UI")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class StateEdge(BaseModel):
    """Directed edge between two state nodes."""

    edge_id: str = Field(min_length=3)
    source_node_id: str = Field(min_length=3)
    target_node_id: str = Field(min_length=3)
    relation: EdgeRelation
    tenant_id: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class StateTransition(BaseModel):
    """Immutable record of a node's phase change. Append-only."""

    transition_id: str = Field(min_length=3)
    node_id: str = Field(min_length=3)
    from_phase: StatePhase
    to_phase: StatePhase
    tenant_id: str = Field(min_length=1)
    triggered_by: str = Field(min_length=1, description="actor/system that caused the transition")
    reason: str = Field(default="", description="Human-readable reason")
    case_run_id: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    context_hash: str = Field(default="", description="SHA-256 of transition context for integrity")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class StateGraphSnapshot(BaseModel):
    """Point-in-time projection of a subgraph for audit/explainability."""

    snapshot_id: str = Field(min_length=3)
    tenant_id: str = Field(min_length=1)
    root_node_id: str = Field(min_length=3)
    nodes: list[StateNode] = Field(default_factory=list)
    edges: list[StateEdge] = Field(default_factory=list)
    transitions: list[StateTransition] = Field(default_factory=list)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Allowed transitions per node type
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: dict[StateNodeType, list[tuple[StatePhase, StatePhase]]] = {
    StateNodeType.BESTELLUNG: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.IN_BEARBEITUNG),
        (StatePhase.OFFEN, StatePhase.STORNIERT),
        (StatePhase.IN_BEARBEITUNG, StatePhase.FREIGEGEBEN),
        (StatePhase.IN_BEARBEITUNG, StatePhase.STORNIERT),
        (StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
    StateNodeType.RECHNUNG: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.FREIGEGEBEN),
        (StatePhase.OFFEN, StatePhase.STORNIERT),
        (StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
    StateNodeType.LAGERBESTAND: [
        (StatePhase.OFFEN, StatePhase.IN_BEARBEITUNG),
        (StatePhase.IN_BEARBEITUNG, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
    StateNodeType.KUNDE: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
    StateNodeType.FREIGABE: [
        (StatePhase.OFFEN, StatePhase.FREIGEGEBEN),
        (StatePhase.OFFEN, StatePhase.STORNIERT),
        (StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN),
    ],
    StateNodeType.LIEFERSCHEIN: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.IN_BEARBEITUNG),
        (StatePhase.IN_BEARBEITUNG, StatePhase.FREIGEGEBEN),
        (StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
    StateNodeType.KONTRAKT: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.IN_BEARBEITUNG),
        (StatePhase.IN_BEARBEITUNG, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
        (StatePhase.OFFEN, StatePhase.STORNIERT),
    ],
    StateNodeType.GUTSCHRIFT: [
        (StatePhase.ENTWURF, StatePhase.OFFEN),
        (StatePhase.OFFEN, StatePhase.FREIGEGEBEN),
        (StatePhase.FREIGEGEBEN, StatePhase.ABGESCHLOSSEN),
        (StatePhase.ABGESCHLOSSEN, StatePhase.ARCHIVIERT),
    ],
}


def _compute_context_hash(data: dict[str, Any]) -> str:
    """SHA-256 hash of a JSON-serialised context dict."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class StateGraphValidationError(Exception):
    """Raised when a state transition violates the allowed-transitions matrix."""


class StateGraphService:
    """
    Pure-logic service for the Neuro State Graph.

    Stateless -- all persistence goes through the repository/ORM layer.
    """

    @staticmethod
    def validate_transition(
        node_type: StateNodeType,
        from_phase: StatePhase,
        to_phase: StatePhase,
    ) -> None:
        """Raise if the transition is not in the allowed matrix."""
        allowed = _ALLOWED_TRANSITIONS.get(node_type, [])
        if (from_phase, to_phase) not in allowed:
            raise StateGraphValidationError(
                f"Transition {from_phase.value} -> {to_phase.value} "
                f"not allowed for {node_type.value}. "
                f"Allowed: {[(a.value, b.value) for a, b in allowed]}"
            )

    @staticmethod
    def build_transition(
        *,
        transition_id: str,
        node: StateNode,
        to_phase: StatePhase,
        triggered_by: str,
        reason: str = "",
        case_run_id: str | None = None,
        evidence_refs: list[str] | None = None,
    ) -> StateTransition:
        """Build and validate a new transition record."""
        StateGraphService.validate_transition(node.node_type, node.phase, to_phase)

        context = {
            "node_id": node.node_id,
            "node_type": node.node_type.value,
            "from_phase": node.phase.value,
            "to_phase": to_phase.value,
            "triggered_by": triggered_by,
            "case_run_id": case_run_id or "",
        }

        return StateTransition(
            transition_id=transition_id,
            node_id=node.node_id,
            from_phase=node.phase,
            to_phase=to_phase,
            tenant_id=node.tenant_id,
            triggered_by=triggered_by,
            reason=reason,
            case_run_id=case_run_id,
            evidence_refs=evidence_refs or [],
            context_hash=_compute_context_hash(context),
        )

    @staticmethod
    def build_snapshot(
        *,
        snapshot_id: str,
        tenant_id: str,
        root_node: StateNode,
        related_nodes: list[StateNode],
        edges: list[StateEdge],
        transitions: list[StateTransition],
    ) -> StateGraphSnapshot:
        """Build a point-in-time snapshot for audit evidence."""
        all_nodes = [root_node, *related_nodes]
        return StateGraphSnapshot(
            snapshot_id=snapshot_id,
            tenant_id=tenant_id,
            root_node_id=root_node.node_id,
            nodes=all_nodes,
            edges=edges,
            transitions=transitions,
        )

    @staticmethod
    def allowed_transitions(node_type: StateNodeType) -> list[tuple[str, str]]:
        """Return the allowed-transition pairs for a node type (for UI/API)."""
        return [
            (a.value, b.value)
            for a, b in _ALLOWED_TRANSITIONS.get(node_type, [])
        ]

    @staticmethod
    def reachable_phases(node_type: StateNodeType, current_phase: StatePhase) -> list[str]:
        """Return phases reachable from the current phase."""
        allowed = _ALLOWED_TRANSITIONS.get(node_type, [])
        return [b.value for a, b in allowed if a == current_phase]
