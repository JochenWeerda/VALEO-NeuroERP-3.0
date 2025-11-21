"""
Schemas für Workflow-Definitionen, Instanzen und Ereignisse.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field, constr


HookType = constr(pattern=r"^(before_transition|after_transition|policy|action)$")


class HookConfig(BaseModel):
    """Deklarative Definition für Hook-Punkte."""

    type: HookType
    name: str
    configuration: Dict[str, Any] = Field(default_factory=dict)


class Transition(BaseModel):
    """Übergang in einer Workflow-Zustandsmaschine."""

    name: str
    source: str
    target: str
    description: Optional[str] = None
    event_type: Optional[str] = Field(
        default=None,
        description="Domain-Event, das den Übergang auslösen darf (z. B. order.shipped)",
    )
    conditions: List[HookConfig] = Field(default_factory=list)
    actions: List[HookConfig] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    """Deklaration einer Workflow-Definition."""

    name: str
    version: str = "1.0.0"
    tenant: str = "default"
    description: Optional[str] = None
    states: List[str]
    initial_state: str
    transitions: List[Transition]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def transition_lookup(self) -> Dict[str, Transition]:
        return {transition.name: transition for transition in self.transitions}


class WorkflowInstance(BaseModel):
    """Laufzeitdaten eines Workflows."""

    id: UUID = Field(default_factory=uuid4)
    workflow_name: str
    workflow_version: str
    tenant: str
    state: str
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateInstanceRequest(BaseModel):
    """Request zum Start eines Workflows."""

    workflow_name: str
    workflow_version: Optional[str] = None
    tenant: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class TransitionRequest(BaseModel):
    """Request zum Auslösen eines Übergangs."""

    transition_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventPayload(BaseModel):
    """Domain-Event, das Workflows triggern kann."""

    event_type: str
    tenant: str = "default"
    data: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None


class SimulationRequest(BaseModel):
    """Simulation eines Workflows mit synthetischem Kontext."""

    workflow_name: str
    workflow_version: Optional[str] = None
    tenant: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    transitions: List[str]


class SimulationResult(BaseModel):
    """Ergebnis einer Workflow-Simulation."""

    succeeded: bool
    final_state: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


