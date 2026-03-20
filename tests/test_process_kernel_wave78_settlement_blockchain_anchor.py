from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import process_kernel_api


class _DummyAnchor:
    def as_dict(self):
        return {
            "anchor_id": "anchor-settlement-1",
            "subject_ref": "SET-BC-1",
            "network_profile": "ORACLE_FABRIC_PERMISSIONED",
        }


def test_settlement_audit_chain_can_be_anchored(monkeypatch):
    app = FastAPI()
    app.include_router(process_kernel_api.router)
    app.dependency_overrides[process_kernel_api.get_db] = lambda: object()
    monkeypatch.setattr(
        "app.core.blockchain_anchor_runtime.anchor_settlement_audit_chain",
        lambda db, chain: _DummyAnchor(),
    )
    client = TestClient(app)

    response = client.post(
        "/process/settlement/audit-chain/SET-BC-1/anchor",
        json={"tenant_id": "t1", "gross_amount": 1234.56, "actor_id": "tester"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["settlement_audit_chain"]["settlement_id"] == "SET-BC-1"
    assert body["blockchain_anchor"]["anchor_id"] == "anchor-settlement-1"
