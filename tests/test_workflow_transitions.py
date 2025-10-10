"""
Unit Tests für Workflow-Transitions
Testet State-Machine, Guards und erlaubte/unerlaubte Pfade
"""

import pytest
from app.services.workflow_service import WorkflowService, workflow


class TestWorkflowTransitions:
    """Unit-Tests für Workflow-State-Machine"""

    def test_sales_workflow_states(self):
        """Test: Sales-Workflow hat alle erforderlichen States"""
        wf = workflow.flows["sales"]
        assert wf.type == "sales"
        assert "draft" in wf.states
        assert "pending" in wf.states
        assert "approved" in wf.states
        assert "posted" in wf.states
        assert "rejected" in wf.states

    def test_purchase_workflow_states(self):
        """Test: Purchase-Workflow hat alle erforderlichen States"""
        wf = workflow.flows["purchase"]
        assert wf.type == "purchase"
        assert "draft" in wf.states
        assert "pending" in wf.states
        assert "approved" in wf.states
        assert "posted" in wf.states
        assert "rejected" in wf.states

    def test_allowed_transitions_draft(self):
        """Test: Aus Draft-State ist nur Submit erlaubt"""
        allowed = workflow.allowed("sales", "draft")
        assert len(allowed) == 1
        assert allowed[0].name == "submit"
        assert allowed[0].dst == "pending"

    def test_allowed_transitions_pending(self):
        """Test: Aus Pending-State sind Approve und Reject erlaubt"""
        allowed = workflow.allowed("sales", "pending")
        assert len(allowed) == 2
        action_names = [t.name for t in allowed]
        assert "approve" in action_names
        assert "reject" in action_names

    def test_allowed_transitions_approved(self):
        """Test: Aus Approved-State ist nur Post erlaubt"""
        allowed = workflow.allowed("sales", "approved")
        assert len(allowed) == 1
        assert allowed[0].name == "post"
        assert allowed[0].dst == "posted"

    def test_transition_draft_to_pending(self):
        """Test: Draft → Pending (submit)"""
        payload = {"lines": [{"qty": 10, "price": 50}]}
        ok, new_state, msg = workflow.next("sales", "draft", "submit", payload)
        assert ok is True
        assert new_state == "pending"
        assert msg == "ok"

    def test_transition_pending_to_approved(self):
        """Test: Pending → Approved (approve)"""
        payload = {"lines": [{"qty": 10, "price": 50, "cost": 30}], "total": 500}
        ok, new_state, msg = workflow.next("sales", "pending", "approve", payload)
        assert ok is True
        assert new_state == "approved"

    def test_transition_pending_to_rejected(self):
        """Test: Pending → Rejected (reject)"""
        payload = {"reason": "Price too low"}
        ok, new_state, msg = workflow.next("sales", "pending", "reject", payload)
        assert ok is True
        assert new_state == "rejected"

    def test_transition_approved_to_posted(self):
        """Test: Approved → Posted (post)"""
        payload = {"total": 500, "lines": []}
        ok, new_state, msg = workflow.next("sales", "approved", "post", payload)
        assert ok is True
        assert new_state == "posted"

    def test_invalid_transition_draft_to_approved(self):
        """Test: Draft → Approved ist nicht erlaubt"""
        payload = {}
        ok, new_state, msg = workflow.next("sales", "draft", "approve", payload)
        assert ok is False
        assert new_state == "draft"
        assert "not allowed" in msg

    def test_invalid_transition_posted_to_draft(self):
        """Test: Posted → Draft ist nicht erlaubt (immutable)"""
        payload = {}
        ok, new_state, msg = workflow.next("sales", "posted", "submit", payload)
        assert ok is False
        assert new_state == "posted"

    def test_guard_total_positive_fails(self):
        """Test: Guard verhindert Buchung mit Total = 0"""
        payload = {"total": 0, "lines": []}
        ok, new_state, msg = workflow.next("sales", "approved", "post", payload)
        assert ok is False
        assert new_state == "approved"
        assert "Total must be > 0" in msg

    def test_guard_price_below_cost_fails(self):
        """Test: Guard verhindert Freigabe wenn Preis < Kosten"""
        payload = {
            "lines": [
                {"article": "SKU-001", "qty": 10, "price": 40, "cost": 50}
            ]
        }
        ok, new_state, msg = workflow.next("sales", "pending", "approve", payload)
        assert ok is False
        assert new_state == "pending"
        assert "Price below cost" in msg

    def test_guard_price_below_cost_passes(self):
        """Test: Guard erlaubt Freigabe wenn Preis >= Kosten"""
        payload = {
            "lines": [
                {"article": "SKU-001", "qty": 10, "price": 60, "cost": 50}
            ],
            "total": 600
        }
        ok, new_state, msg = workflow.next("sales", "pending", "approve", payload)
        assert ok is True
        assert new_state == "approved"

    def test_complete_workflow_happy_path(self):
        """Test: Kompletter Workflow-Durchlauf (Draft → Posted)"""
        payload = {
            "lines": [
                {"article": "SKU-001", "qty": 10, "price": 60, "cost": 50}
            ],
            "total": 600
        }

        # Draft → Pending
        ok, state, _ = workflow.next("sales", "draft", "submit", payload)
        assert ok and state == "pending"

        # Pending → Approved
        ok, state, _ = workflow.next("sales", state, "approve", payload)
        assert ok and state == "approved"

        # Approved → Posted
        ok, state, _ = workflow.next("sales", state, "post", payload)
        assert ok and state == "posted"

    def test_complete_workflow_rejection_path(self):
        """Test: Rejection-Workflow (Draft → Pending → Rejected)"""
        payload = {"lines": [{"qty": 10, "price": 50}]}

        # Draft → Pending
        ok, state, _ = workflow.next("sales", "draft", "submit", payload)
        assert ok and state == "pending"

        # Pending → Rejected
        ok, state, _ = workflow.next("sales", state, "reject", {"reason": "Test"})
        assert ok and state == "rejected"

    def test_purchase_workflow_similar_to_sales(self):
        """Test: Purchase-Workflow funktioniert analog zu Sales"""
        payload = {"total": 500, "lines": [{"qty": 10, "price": 50, "cost": 30}]}

        # Draft → Pending
        ok, state, _ = workflow.next("purchase", "draft", "submit", payload)
        assert ok and state == "pending"

        # Pending → Approved
        ok, state, _ = workflow.next("purchase", state, "approve", payload)
        assert ok and state == "approved"

        # Approved → Posted
        ok, state, _ = workflow.next("purchase", state, "post", payload)
        assert ok and state == "posted"


class TestWorkflowGuards:
    """Unit-Tests für Workflow-Guards"""

    def test_guard_total_positive_with_zero(self):
        """Test: guard_total_positive blockt bei Total = 0"""
        from app.services.workflow_guards import guard_total_positive
        ok, reason = guard_total_positive({"total": 0})
        assert ok is False
        assert "must be > 0" in reason.lower()

    def test_guard_total_positive_with_positive(self):
        """Test: guard_total_positive erlaubt bei Total > 0"""
        from app.services.workflow_guards import guard_total_positive
        ok, reason = guard_total_positive({"total": 100})
        assert ok is True

    def test_guard_price_not_below_cost_blocks(self):
        """Test: guard_price_not_below_cost blockt bei Preis < Kosten"""
        from app.services.workflow_guards import guard_price_not_below_cost
        payload = {"lines": [{"article": "TEST", "price": 40, "cost": 50}]}
        ok, reason = guard_price_not_below_cost(payload)
        assert ok is False
        assert "below cost" in reason.lower()

    def test_guard_price_not_below_cost_allows(self):
        """Test: guard_price_not_below_cost erlaubt bei Preis >= Kosten"""
        from app.services.workflow_guards import guard_price_not_below_cost
        payload = {"lines": [{"article": "TEST", "price": 60, "cost": 50}]}
        ok, reason = guard_price_not_below_cost(payload)
        assert ok is True

    def test_guard_handles_missing_cost(self):
        """Test: Guard funktioniert auch wenn cost fehlt"""
        from app.services.workflow_guards import guard_price_not_below_cost
        payload = {"lines": [{"article": "TEST", "price": 60}]}
        ok, reason = guard_price_not_below_cost(payload)
        assert ok is True  # Kein cost → kein Check

    def test_guard_handles_empty_lines(self):
        """Test: Guard funktioniert mit leeren lines"""
        from app.services.workflow_guards import guard_price_not_below_cost
        payload = {"lines": []}
        ok, reason = guard_price_not_below_cost(payload)
        assert ok is True

