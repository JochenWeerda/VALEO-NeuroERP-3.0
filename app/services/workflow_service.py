"""
Workflow Service
State-Machine für mehrstufige Beleg-Workflows mit Guards und Transitions
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
import time

from .workflow_guards import guard_total_positive, guard_price_not_below_cost, guard_has_approval_role, guard_has_submit_role


TransitionGuard = Callable[[dict], tuple[bool, str]]


@dataclass
class Transition:
    name: str           # e.g. "submit", "approve", "reject", "post"
    src: str
    dst: str
    guard: Optional[TransitionGuard] = None


@dataclass
class Workflow:
    type: str
    states: List[str]
    transitions: List[Transition]


class WorkflowService:
    """Workflow-Service für State-Management"""

    def __init__(self):
        self.flows: Dict[str, Workflow] = {
            "sales": Workflow(
                type="sales",
                states=["draft", "pending", "approved", "posted", "rejected"],
                transitions=[
                    Transition("submit", "draft", "pending", guard_has_submit_role),
                    Transition("approve", "pending", "approved", guard_price_not_below_cost),
                    Transition("reject", "pending", "rejected", guard_has_approval_role),
                    Transition("post", "approved", "posted", guard_total_positive),
                ],
            ),
            "purchase": Workflow(
                type="purchase",
                states=["draft", "pending", "approved", "posted", "rejected"],
                transitions=[
                    Transition("submit", "draft", "pending", guard_has_submit_role),
                    Transition("approve", "pending", "approved", guard_has_approval_role),
                    Transition("reject", "pending", "rejected", guard_has_approval_role),
                    Transition("post", "approved", "posted", guard_total_positive),
                ],
            ),
        }

    def allowed(self, domain: str, state: str) -> List[Transition]:
        """
        Holt erlaubte Transitions für einen State

        Args:
            domain: Belegtyp (sales/purchase)
            state: Aktueller State

        Returns:
            Liste erlaubter Transitions
        """
        wf = self.flows[domain]
        return [t for t in wf.transitions if t.src == state]

    def next(self, domain: str, state: str, action: str, payload: dict) -> tuple[bool, str, str]:
        """
        Führt Transition aus

        Args:
            domain: Belegtyp
            state: Aktueller State
            action: Aktion (submit/approve/reject/post)
            payload: Beleg-Daten für Guards

        Returns:
            (success, new_state, message)
        """
        wf = self.flows[domain]
        cand = next((t for t in wf.transitions if t.src == state and t.name == action), None)
        if not cand:
            return False, state, "transition not allowed"
        if cand.guard:
            ok, reason = cand.guard(payload)
            if not ok:
                return False, state, reason
        return True, cand.dst, "ok"


# Global Workflow Instance
workflow = WorkflowService()