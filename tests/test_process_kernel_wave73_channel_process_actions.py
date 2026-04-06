"""
Wave 73 - Channel-native process execution, approvals and audit.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import channel_work_surfaces
from app.core.action_idempotency import get_action_idempotency_store
from app.core.channel_process_actions import get_channel_process_thread_store


@pytest.fixture(autouse=True)
def anchor_stub(monkeypatch):
    monkeypatch.setattr(
        "app.core.blockchain_anchor_runtime.anchor_channel_process_thread",
        lambda db, thread: type(
            "Anchor",
            (),
            {
                "as_dict": lambda self: {
                    "anchor_id": "anchor-thread-1",
                    "subject_ref": thread.thread_id,
                    "network_profile": "ORACLE_FABRIC_PERMISSIONED",
                }
            },
        )(),
    )


@pytest.fixture(autouse=True)
def clear_channel_state():
    get_channel_process_thread_store().clear()
    get_action_idempotency_store().clear()
    yield
    get_channel_process_thread_store().clear()
    get_action_idempotency_store().clear()


@pytest.fixture
def client(require_db) -> TestClient:
    app = FastAPI()
    app.include_router(channel_work_surfaces.router)
    return TestClient(app)


def test_channel_process_execute_accepts_direct_approval_flow(client: TestClient):
    response = client.post(
        "/channels/teams/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "settlement_to_finance",
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-71",
            "payload": {"status": "ZUR_FREIGABE"},
            "issuer_role": "ap_approver",
            "issuer_type": "human",
            "idempotency_key": "wave73-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["kanal"] == "TEAMS"
    assert body["execution"]["command_name"] == "ApproveAPInvoice"
    assert body["audit_trail"][0]["audit_type"] == "action_execution"
    assert body["blockchain_anchor"]["subject_ref"] == body["thread_id"]


def test_channel_process_execute_surfaces_pending_approval_and_requirement(client: TestClient):
    response = client.post(
        "/channels/slack/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "quality_to_settlement",
            "command_name": "FinalizeAgrarSettlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-71",
            "payload": {"status": "DRAFT", "betrag_eur": 75000},
            "issuer_role": "settlement_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-2",
            "channel_user_id": "slack-user-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending_approval"
    assert body["approval_requirement"]["requires_human_approval"] is True
    assert body["approval_requirement"]["risiko_stufe"] == "HOCH"
    assert "wartet auf Freigabe" in body["message"]


def test_channel_process_decision_approves_and_reexecutes_pending_thread(client: TestClient):
    create = client.post(
        "/channels/slack/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "quality_to_settlement",
            "command_name": "FinalizeAgrarSettlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-72",
            "payload": {"status": "DRAFT", "betrag_eur": 75000},
            "issuer_role": "settlement_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-3",
        },
    )
    thread_id = create.json()["thread_id"]

    decision = client.post(
        f"/channels/slack/process-actions/{thread_id}/decision",
        json={
            "decision": "GENEHMIGT",
            "entschieden_von": "user-approver-1",
            "approver_role": "teamleiter",
            "begruendung": "Betrag und Unterlagen geprueft",
        },
    )
    assert decision.status_code == 200
    body = decision.json()
    assert body["status"] == "accepted"
    assert body["approval_record"]["decision"] == "GENEHMIGT"
    assert len(body["audit_trail"]) == 3
    assert body["execution"]["status"] == "accepted"
    assert body["blockchain_anchor"]["subject_ref"] == thread_id


def test_channel_process_decision_rejects_pending_thread(client: TestClient):
    create = client.post(
        "/channels/teams/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "quality_to_settlement",
            "command_name": "FinalizeAgrarSettlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-73",
            "payload": {"status": "DRAFT", "betrag_eur": 90000},
            "issuer_role": "settlement_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-4",
        },
    )
    thread_id = create.json()["thread_id"]

    decision = client.post(
        f"/channels/teams/process-actions/{thread_id}/decision",
        json={
            "decision": "ABGELEHNT",
            "entschieden_von": "user-approver-2",
            "approver_role": "teamleiter",
            "begruendung": "Unterlagen unvollstaendig",
        },
    )
    assert decision.status_code == 200
    body = decision.json()
    assert body["status"] == "rejected"
    assert body["approval_record"]["decision"] == "ABGELEHNT"
    assert body["audit_trail"][-1]["audit_type"] == "process_decision"


def test_channel_process_thread_lookup_returns_current_snapshot(client: TestClient):
    create = client.post(
        "/channels/teams/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "settlement_to_finance",
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-72",
            "payload": {"status": "ZUR_FREIGABE"},
            "issuer_role": "finance_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-5",
        },
    )
    thread_id = create.json()["thread_id"]
    fetch = client.get(f"/channels/teams/process-actions/{thread_id}")
    assert fetch.status_code == 200
    assert fetch.json()["thread_id"] == thread_id


def test_channel_process_thread_list_can_filter_pending_backlog(client: TestClient):
    client.post(
        "/channels/slack/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "quality_to_settlement",
            "command_name": "FinalizeAgrarSettlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-74",
            "payload": {"status": "DRAFT", "betrag_eur": 70000},
            "issuer_role": "settlement_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-7a",
        },
    )
    client.post(
        "/channels/slack/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "settlement_to_finance",
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-75",
            "payload": {"status": "ZUR_FREIGABE"},
            "issuer_role": "finance_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-7b",
        },
    )

    response = client.get(
        "/channels/slack/process-actions",
        params={"tenant_id": "t1", "status": "pending_approval"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "pending_approval"
    assert body["items"][0]["process_definition_key"] == "quality_to_settlement"


def test_channel_process_thread_audit_endpoint_returns_explicit_audit_feed(client: TestClient):
    create = client.post(
        "/channels/slack/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "quality_to_settlement",
            "command_name": "FinalizeAgrarSettlement",
            "aggregate_type": "agrar_settlement",
            "aggregate_id": "SET-75",
            "payload": {"status": "DRAFT", "betrag_eur": 91000},
            "issuer_role": "settlement_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-8",
        },
    )
    thread_id = create.json()["thread_id"]
    client.post(
        f"/channels/slack/process-actions/{thread_id}/decision",
        json={
            "decision": "GENEHMIGT",
            "entschieden_von": "user-approver-4",
            "approver_role": "teamleiter",
            "begruendung": "freigegeben",
        },
    )

    response = client.get(f"/channels/slack/process-actions/{thread_id}/audit")
    assert response.status_code == 200
    body = response.json()
    assert body["thread_id"] == thread_id
    assert body["count"] == 3
    assert body["audit_trail"][0]["audit_type"] == "action_execution"
    assert body["audit_trail"][1]["audit_type"] == "approval_record"


def test_channel_process_decision_requires_pending_thread(client: TestClient):
    create = client.post(
        "/channels/teams/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "settlement_to_finance",
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-73",
            "payload": {"status": "ZUR_FREIGABE"},
            "issuer_role": "finance_manager",
            "issuer_type": "human",
            "idempotency_key": "wave73-6",
        },
    )
    thread_id = create.json()["thread_id"]
    decision = client.post(
        f"/channels/teams/process-actions/{thread_id}/decision",
        json={
            "decision": "GENEHMIGT",
            "entschieden_von": "user-approver-3",
            "approver_role": "teamleiter",
            "begruendung": "irrelevant",
        },
    )
    assert decision.status_code == 400


def test_channel_process_execute_rejects_unsupported_channel(client: TestClient):
    response = client.post(
        "/channels/email/process-actions/execute",
        json={
            "tenant_id": "t1",
            "process_definition_key": "settlement_to_finance",
            "command_name": "ApproveAPInvoice",
            "aggregate_type": "ap_invoice",
            "aggregate_id": "INV-74",
            "payload": {"status": "ZUR_FREIGABE"},
            "issuer_role": "ap_approver",
            "issuer_type": "human",
            "idempotency_key": "wave73-7",
        },
    )
    assert response.status_code == 400
