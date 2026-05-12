"""
Workflow Service (Gap 011: versionierte Definitionen).
State-Machine für mehrstufige Beleg-Workflows mit Guards und Transitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from app.core.workflow_definitions import WorkflowDef, get_workflow_def

TransitionGuard = Callable[[dict], tuple[bool, str]]


@dataclass
class Transition:
    name: str
    src: str
    dst: str
    guard: Optional[TransitionGuard] = None


@dataclass
class Workflow:
    type: str
    states: List[str]
    transitions: List[Transition]


def _def_to_workflow(defn: WorkflowDef) -> Workflow:
    """Konvertiert WorkflowDef in internes Workflow-Format."""
    transitions = [
        Transition(t.name, t.src, t.dst, t.guard)
        for t in defn.transitions
    ]
    return Workflow(type=defn.domain, states=defn.states, transitions=transitions)


class WorkflowService:
    """Workflow-Service (Gap 011: versionierte Definitionen)."""

    @property
    def flows(self) -> Dict[str, Workflow]:
        """Alle registrierten Workflows als {domain: Workflow}-Dict."""
        from app.core.workflow_definitions import _bootstrap, _REGISTRY
        _bootstrap()
        return {domain: _def_to_workflow(defn) for (domain, _ver), defn in _REGISTRY.items()}

    def _get_flow(self, domain: str, version: str = "1") -> Workflow:
        defn = get_workflow_def(domain, version)
        if not defn:
            raise ValueError(f"Unknown workflow {domain} v{version}")
        return _def_to_workflow(defn)

    def allowed(self, domain: str, state: str, version: str = "1") -> List[Transition]:
        """
        Holt erlaubte Transitions für einen State.
        """
        wf = self._get_flow(domain, version)
        return [t for t in wf.transitions if t.src == state]

    def next(
        self,
        domain: str,
        state: str,
        action: str,
        payload: dict,
        version: str = "1",
    ) -> tuple[bool, str, str]:
        """
        Führt Transition aus.
        """
        wf = self._get_flow(domain, version)
        cand = next((t for t in wf.transitions if t.src == state and t.name == action), None)
        if not cand:
            return False, state, "transition not allowed"
        if cand.guard:
            ok, reason = cand.guard(payload)
            if not ok:
                return False, state, reason
        return True, cand.dst, "ok"


workflow = WorkflowService()
