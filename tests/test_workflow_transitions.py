"""
Unit tests for workflow transitions.
"""

from app.services.workflow_service import workflow


class TestWorkflowTransitions:
    def test_sales_workflow_states(self):
        wf = workflow.flows["sales"]
        assert wf.type == "sales"
        assert {"draft", "pending", "approved", "posted", "rejected"}.issubset(set(wf.states))

    def test_purchase_workflow_states(self):
        wf = workflow.flows["purchase"]
        assert wf.type == "purchase"
        assert {"draft", "pending", "approved", "posted", "rejected"}.issubset(set(wf.states))

    def test_allowed_transitions_draft(self):
        allowed = workflow.allowed("sales", "draft")
        assert len(allowed) == 1
        assert allowed[0].name == "submit"

    def test_allowed_transitions_pending(self):
        names = [t.name for t in workflow.allowed("sales", "pending")]
        assert "approve" in names
        assert "reject" in names

    def test_allowed_transitions_approved(self):
        allowed = workflow.allowed("sales", "approved")
        assert len(allowed) == 1
        assert allowed[0].name == "post"

    def test_transition_draft_to_pending(self):
        payload = {"lines": [{"qty": 10, "price": 50}], "user_info": {"roles": ["sales"]}}
        ok, new_state, msg = workflow.next("sales", "draft", "submit", payload)
        assert ok is True
        assert new_state == "pending"
        assert msg == "ok"

    def test_transition_pending_to_approved(self):
        payload = {"lines": [{"qty": 10, "price": 50, "cost": 30}], "total": 500}
        ok, new_state, _ = workflow.next("sales", "pending", "approve", payload)
        assert ok is True
        assert new_state == "approved"

    def test_transition_pending_to_rejected(self):
        payload = {"reason": "Price too low", "user_info": {"roles": ["admin"]}}
        ok, new_state, _ = workflow.next("sales", "pending", "reject", payload)
        assert ok is True
        assert new_state == "rejected"

    def test_transition_approved_to_posted(self):
        payload = {"total": 500, "lines": []}
        ok, new_state, _ = workflow.next("sales", "approved", "post", payload)
        assert ok is True
        assert new_state == "posted"

    def test_invalid_transition_draft_to_approved(self):
        ok, new_state, msg = workflow.next("sales", "draft", "approve", {})
        assert ok is False
        assert new_state == "draft"
        assert "not allowed" in msg

    def test_invalid_transition_posted_to_draft(self):
        ok, new_state, _ = workflow.next("sales", "posted", "submit", {})
        assert ok is False
        assert new_state == "posted"

    def test_guard_total_positive_fails(self):
        ok, new_state, msg = workflow.next("sales", "approved", "post", {"total": 0, "lines": []})
        assert ok is False
        assert new_state == "approved"
        assert "Total must be > 0" in msg

    def test_guard_price_below_cost_fails(self):
        payload = {"lines": [{"article": "SKU-001", "qty": 10, "price": 40, "cost": 50}]}
        ok, new_state, msg = workflow.next("sales", "pending", "approve", payload)
        assert ok is False
        assert new_state == "pending"
        assert "Price below cost" in msg

    def test_guard_price_below_cost_passes(self):
        payload = {"lines": [{"article": "SKU-001", "qty": 10, "price": 60, "cost": 50}], "total": 600}
        ok, new_state, _ = workflow.next("sales", "pending", "approve", payload)
        assert ok is True
        assert new_state == "approved"

    def test_complete_workflow_happy_path(self):
        payload = {
            "lines": [{"article": "SKU-001", "qty": 10, "price": 60, "cost": 50}],
            "total": 600,
            "user_info": {"roles": ["admin"]},
        }
        ok, state, _ = workflow.next("sales", "draft", "submit", payload)
        assert ok and state == "pending"
        ok, state, _ = workflow.next("sales", state, "approve", payload)
        assert ok and state == "approved"
        ok, state, _ = workflow.next("sales", state, "post", payload)
        assert ok and state == "posted"

    def test_complete_workflow_rejection_path(self):
        payload = {"lines": [{"qty": 10, "price": 50}], "user_info": {"roles": ["sales"]}}
        ok, state, _ = workflow.next("sales", "draft", "submit", payload)
        assert ok and state == "pending"
        ok, state, _ = workflow.next("sales", state, "reject", {"reason": "Test", "user_info": {"roles": ["admin"]}})
        assert ok and state == "rejected"

    def test_purchase_workflow_similar_to_sales(self):
        submit_payload = {"total": 500, "lines": [{"qty": 10, "price": 50, "cost": 30}], "user_info": {"roles": ["purchase"]}}
        ok, state, _ = workflow.next("purchase", "draft", "submit", submit_payload)
        assert ok and state == "pending"
        ok, state, _ = workflow.next("purchase", state, "approve", {"user_info": {"roles": ["admin"]}, "lines": [], "total": 500})
        assert ok and state == "approved"
        ok, state, _ = workflow.next("purchase", state, "post", {"total": 500, "lines": []})
        assert ok and state == "posted"


class TestWorkflowGuards:
    def test_guard_total_positive_with_zero(self):
        from app.services.workflow_guards import guard_total_positive

        ok, reason = guard_total_positive({"total": 0})
        assert ok is False
        assert "must be > 0" in reason.lower()

    def test_guard_total_positive_with_positive(self):
        from app.services.workflow_guards import guard_total_positive

        ok, _ = guard_total_positive({"total": 100})
        assert ok is True

    def test_guard_price_not_below_cost_blocks(self):
        from app.services.workflow_guards import guard_price_not_below_cost

        ok, reason = guard_price_not_below_cost({"lines": [{"article": "TEST", "price": 40, "cost": 50}]})
        assert ok is False
        assert "below cost" in reason.lower()

    def test_guard_price_not_below_cost_allows(self):
        from app.services.workflow_guards import guard_price_not_below_cost

        ok, _ = guard_price_not_below_cost({"lines": [{"article": "TEST", "price": 60, "cost": 50}]})
        assert ok is True

    def test_guard_handles_missing_cost(self):
        from app.services.workflow_guards import guard_price_not_below_cost

        ok, _ = guard_price_not_below_cost({"lines": [{"article": "TEST", "price": 60}]})
        assert ok is True

    def test_guard_handles_empty_lines(self):
        from app.services.workflow_guards import guard_price_not_below_cost

        ok, _ = guard_price_not_below_cost({"lines": []})
        assert ok is True
