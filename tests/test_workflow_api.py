"""
API Tests für Workflow-Endpoints
Testet GET/POST Endpoints, Audit-Trail, Guards via API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestWorkflowAPI:
    """API-Tests für Workflow-Endpoints"""

    def test_get_status_default_is_draft(self):
        """Test: Neuer Beleg hat Status 'draft'"""
        response = client.get("/api/workflow/sales/SO-00001")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "draft"

    def test_submit_transition(self):
        """Test: Submit-Transition (draft → pending)"""
        payload = {
            "action": "submit",
            "lines": [{"qty": 10, "price": 50}]
        }
        response = client.post("/api/workflow/sales/SO-00002/transition", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "pending"

    def test_approve_transition(self):
        """Test: Approve-Transition (pending → approved)"""
        # Setup: Erst submit
        client.post("/api/workflow/sales/SO-00003/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 60, "cost": 50}]
        })

        # Approve
        payload = {
            "action": "approve",
            "lines": [{"qty": 10, "price": 60, "cost": 50}],
            "total": 600
        }
        response = client.post("/api/workflow/sales/SO-00003/transition", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "approved"

    def test_reject_transition(self):
        """Test: Reject-Transition (pending → rejected)"""
        # Setup: Erst submit
        client.post("/api/workflow/sales/SO-00004/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 50}]
        })

        # Reject
        payload = {
            "action": "reject",
            "reason": "Price too low"
        }
        response = client.post("/api/workflow/sales/SO-00004/transition", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "rejected"

    def test_post_transition(self):
        """Test: Post-Transition (approved → posted)"""
        # Setup: Submit & Approve
        client.post("/api/workflow/sales/SO-00005/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 60, "cost": 50}]
        })
        client.post("/api/workflow/sales/SO-00005/transition", json={
            "action": "approve",
            "lines": [{"qty": 10, "price": 60, "cost": 50}],
            "total": 600
        })

        # Post
        payload = {
            "action": "post",
            "total": 600,
            "lines": []
        }
        response = client.post("/api/workflow/sales/SO-00005/transition", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["state"] == "posted"

    def test_invalid_transition_returns_400(self):
        """Test: Ungültige Transition gibt 400 zurück"""
        # Versuche approve ohne vorheriges submit
        payload = {
            "action": "approve",
            "lines": []
        }
        response = client.post("/api/workflow/sales/SO-00006/transition", json=payload)
        assert response.status_code == 400

    def test_guard_total_positive_blocks_post(self):
        """Test: Guard blockt Buchung mit Total = 0"""
        # Setup: Submit & Approve
        client.post("/api/workflow/sales/SO-00007/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 60, "cost": 50}]
        })
        client.post("/api/workflow/sales/SO-00007/transition", json={
            "action": "approve",
            "lines": [{"qty": 10, "price": 60, "cost": 50}],
            "total": 600
        })

        # Post mit Total = 0
        payload = {
            "action": "post",
            "total": 0,
            "lines": []
        }
        response = client.post("/api/workflow/sales/SO-00007/transition", json=payload)
        assert response.status_code == 400

    def test_guard_price_below_cost_blocks_approve(self):
        """Test: Guard blockt Freigabe wenn Preis < Kosten"""
        # Setup: Submit
        client.post("/api/workflow/sales/SO-00008/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 40, "cost": 50}]
        })

        # Approve mit Preis < Kosten
        payload = {
            "action": "approve",
            "lines": [{"article": "SKU-001", "qty": 10, "price": 40, "cost": 50}]
        }
        response = client.post("/api/workflow/sales/SO-00008/transition", json=payload)
        assert response.status_code == 400

    def test_audit_trail_records_transitions(self):
        """Test: Audit-Trail zeichnet alle Transitions auf"""
        doc_number = "SO-00009"

        # Perform transitions
        client.post(f"/api/workflow/sales/{doc_number}/transition", json={
            "action": "submit",
            "lines": [{"qty": 10, "price": 60, "cost": 50}]
        })
        client.post(f"/api/workflow/sales/{doc_number}/transition", json={
            "action": "approve",
            "lines": [{"qty": 10, "price": 60, "cost": 50}],
            "total": 600
        })

        # Get audit trail
        response = client.get(f"/api/workflow/sales/{doc_number}/audit")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert len(data["items"]) == 2
        
        # Verify first transition
        assert data["items"][0]["from"] == "draft"
        assert data["items"][0]["to"] == "pending"
        assert data["items"][0]["action"] == "submit"
        
        # Verify second transition
        assert data["items"][1]["from"] == "pending"
        assert data["items"][1]["to"] == "approved"
        assert data["items"][1]["action"] == "approve"

    def test_audit_trail_includes_timestamp(self):
        """Test: Audit-Einträge haben Timestamp"""
        doc_number = "SO-00010"
        
        client.post(f"/api/workflow/sales/{doc_number}/transition", json={
            "action": "submit",
            "lines": []
        })

        response = client.get(f"/api/workflow/sales/{doc_number}/audit")
        data = response.json()
        assert data["items"][0]["ts"] > 0

    def test_purchase_workflow_api(self):
        """Test: Purchase-Workflow via API"""
        doc_number = "PO-00001"

        # Draft → Pending
        response = client.post(f"/api/workflow/purchase/{doc_number}/transition", json={
            "action": "submit",
            "lines": []
        })
        assert response.status_code == 200
        assert response.json()["state"] == "pending"

        # Pending → Approved
        response = client.post(f"/api/workflow/purchase/{doc_number}/transition", json={
            "action": "approve",
            "lines": [],
            "total": 500
        })
        assert response.status_code == 200
        assert response.json()["state"] == "approved"

        # Approved → Posted
        response = client.post(f"/api/workflow/purchase/{doc_number}/transition", json={
            "action": "post",
            "total": 500,
            "lines": []
        })
        assert response.status_code == 200
        assert response.json()["state"] == "posted"


class TestWorkflowReplay:
    """Tests für Workflow-Event-Replay"""

    def test_replay_returns_events(self):
        """Test: Replay-Endpoint gibt Events zurück"""
        # Create some workflow events
        client.post("/api/workflow/sales/SO-00011/transition", json={
            "action": "submit",
            "lines": []
        })

        # Replay
        response = client.get("/api/workflow/replay/workflow?since=0")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_replay_filters_by_timestamp(self):
        """Test: Replay filtert nach Timestamp"""
        import time
        now = time.time()

        # Create event
        client.post("/api/workflow/sales/SO-00012/transition", json={
            "action": "submit",
            "lines": []
        })

        # Replay seit now (sollte Event enthalten)
        response = client.get(f"/api/workflow/replay/workflow?since={now}")
        data = response.json()
        assert len(data["events"]) > 0

        # Replay seit Zukunft (sollte leer sein)
        response = client.get(f"/api/workflow/replay/workflow?since={now + 1000}")
        data = response.json()
        assert len(data["events"]) == 0

