from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agrar_settlements, credit_debit_memos, process_kernel_api
from app.core.database import get_db


def _build_repo():
    return {
        "partner": {
            "SUP-1": {"id": "SUP-1", "name": "Agrar Nord"},
        },
        "ap_invoice": {
            "INV-1": {
                "id": "INV-1",
                "number": "RE-1",
                "supplierId": "SUP-1",
                "openAmount": 1000.0,
                "totalGross": 1000.0,
            }
        },
        "credit_memo": {},
        "debit_memo": {},
        "ap_memo_booking": {},
        "journal_entry": {},
    }


def _repo_get(entity_type: str, entity_id: str, repo: dict):
    return repo.get(entity_type, {}).get(entity_id)


def _repo_save(entity_type: str, entity_id: str, payload: dict, repo: dict):
    repo.setdefault(entity_type, {})[entity_id] = payload


def _repo_list(
    doc_type: str,
    skip: int = 0,
    limit: int = 100,
    filters: dict | None = None,
    repo: dict | None = None,
):
    """Spiegelt router_helpers.list_from_store: dict mit data/total/skip/limit."""
    items = list((repo or {}).get(doc_type, {}).values())
    if filters:
        if "tenantId" in filters:
            tid = filters["tenantId"]
            items = [m for m in items if m.get("tenantId") in (tid, None, "")]
        if "status" in filters:
            items = [m for m in items if m.get("status") == filters["status"]]
        if "customerId" in filters:
            items = [m for m in items if m.get("customerId") == filters["customerId"]]
        if "supplierId" in filters:
            items = [m for m in items if m.get("supplierId") == filters["supplierId"]]
    total = len(items)
    page = items[skip : skip + limit]
    return {"ok": True, "data": page, "total": total, "skip": skip, "limit": limit}


@dataclass
class _FakeSettlement:
    id: str = "SET-1"
    tenant_id: str = "tenant-1"
    settlement_number: str = "SET-2026-0001"
    contract_id: str | None = None
    ticket_id: str | None = None
    supplier_id: str = "SUP-1"
    article_id: str | None = "WEIZEN"
    gross_quantity_kg: float = 10000.0
    billing_quantity_kg: float = 9800.0
    unit_price_eur_per_ton: float = 220.0
    gross_amount_eur: float = 2200.0
    total_deductions_eur: float = 100.0
    net_amount_eur: float = 2100.0
    currency: str = "EUR"
    status: str = "draft"
    posted_journal_ref: str | None = None
    posted_at: str | None = None
    note: str | None = None
    drying_result: dict | None = None
    created_at: str = "2026-03-22T10:00:00Z"


class _FakeQuery:
    def __init__(self, db: "_FakeDb", model):
        self.db = db
        self.model = model

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        if self.model is agrar_settlements.AgrarSettlement:
            return self.db.settlement
        return None

    def all(self):
        if self.model is agrar_settlements.AgrarSettlementDeduction:
            return []
        if self.model is agrar_settlements.AgrarSettlement:
            return [self.db.settlement]
        return []

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self


class _FakeDb:
    def __init__(self, settlement: _FakeSettlement):
        self.settlement = settlement
        self.commits = 0

    def query(self, model):
        return _FakeQuery(self, model)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        return obj


def _app_with_repo_and_settlement(monkeypatch, settlement: _FakeSettlement):
    repo = _build_repo()
    fake_db = _FakeDb(settlement)

    monkeypatch.setattr(credit_debit_memos, "get_repository", lambda db: repo)
    monkeypatch.setattr(credit_debit_memos, "get_from_store", _repo_get)
    monkeypatch.setattr(credit_debit_memos, "save_to_store", _repo_save)
    monkeypatch.setattr(credit_debit_memos, "list_from_store", _repo_list)

    monkeypatch.setattr(agrar_settlements, "get_repository", lambda db: repo)
    monkeypatch.setattr(agrar_settlements, "get_from_store", _repo_get)
    monkeypatch.setattr(agrar_settlements, "save_to_store", _repo_save)
    monkeypatch.setattr(agrar_settlements, "list_from_store", _repo_list)

    app = FastAPI()
    app.include_router(credit_debit_memos.router)
    app.include_router(agrar_settlements.router)
    app.include_router(process_kernel_api.router)
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[agrar_settlements.get_tenant_id] = lambda: "tenant-1"
    return app, repo, fake_db


def test_posting_requires_freigabe_before_fibu(monkeypatch):
    app, repo, fake_db = _app_with_repo_and_settlement(monkeypatch, _FakeSettlement())
    client = TestClient(app)

    blocked = client.post(
        "/SET-1/post-fibu",
        json={
            "debit_account": "5000",
            "credit_account_supplier": "3300",
            "credit_account_deductions": "5490",
        },
    )
    assert blocked.status_code == 409
    assert "approval_status=ENTWURF" in blocked.json()["detail"]

    submit_resp = client.post(
        "/SET-1/freigabe",
        json={
            "actor_id": "sb-1",
            "actor_type": "SACHBEARBEITER",
            "target_status": "ZUR_FREIGABE",
        },
    )
    assert submit_resp.status_code == 200
    assert submit_resp.json()["allowed"] is True

    approve_resp = client.post(
        "/SET-1/freigabe",
        json={
            "actor_id": "lead-1",
            "actor_type": "ABTEILUNGSLEITER",
            "target_status": "FREIGEGEBEN",
        },
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["allowed"] is True

    post_resp = client.post(
        "/SET-1/post-fibu",
        json={
            "debit_account": "5000",
            "credit_account_supplier": "3300",
            "credit_account_deductions": "5490",
        },
    )
    assert post_resp.status_code == 200
    assert post_resp.json()["journal_ref"].startswith("JE-SET-")
    assert fake_db.settlement.status == "posted"
    assert fake_db.settlement.posted_journal_ref == post_resp.json()["journal_ref"]
    assert fake_db.settlement.drying_result["approval_status"] == "VERBUCHT"
    assert fake_db.settlement.drying_result["approval_history"][-1]["new_status"] == "VERBUCHT"
    assert repo["journal_entry"][post_resp.json()["journal_ref"]]["source_id"] == "SET-1"


def test_correction_draft_prefills_credit_and_debit_flow(monkeypatch):
    settlement = _FakeSettlement(status="posted", posted_journal_ref="JE-SET-0001", drying_result={"approval_status": "VERBUCHT"})
    app, _repo, _fake_db = _app_with_repo_and_settlement(monkeypatch, settlement)
    client = TestClient(app)

    credit_resp = client.get("/SET-1/correction-draft", params={"memo_type": "credit"})
    assert credit_resp.status_code == 200
    credit_body = credit_resp.json()
    assert credit_body["memo_type"] == "credit"
    assert credit_body["supplier_id"] == "SUP-1"
    assert credit_body["suggested_route"].endswith("/einkauf/gutschriften-belastungen/credit?settlementId=SET-1")
    assert credit_body["items"][0]["grossAmount"] == 2100.0

    debit_resp = client.get("/SET-1/correction-draft", params={"memo_type": "debit"})
    assert debit_resp.status_code == 200
    debit_body = debit_resp.json()
    assert debit_body["memo_type"] == "debit"
    assert debit_body["suggested_route"].endswith("/einkauf/gutschriften-belastungen/debit?settlementId=SET-1")


def test_completion_status_tracks_credit_debit_and_korrektur_variants(monkeypatch):
    settlement = _FakeSettlement(
        status="posted",
        posted_journal_ref="JE-SET-0001",
        drying_result={
            "approval_status": "VERBUCHT",
            "approval_history": [
                {"new_status": "ZUR_FREIGABE"},
                {"new_status": "FREIGEGEBEN"},
                {"new_status": "VERBUCHT"},
            ],
        },
    )
    app, repo, _fake_db = _app_with_repo_and_settlement(monkeypatch, settlement)
    client = TestClient(app)

    credit_create = client.post(
        "/einkauf/credit-memos",
        json={
            "supplierId": "SUP-1",
            "settlementId": "SET-1",
            "correctionMode": "CREDIT_NOTE",
            "memoDate": "2026-03-22",
            "reason": "Preisabweichung aus Settlement-Korrektur",
            "items": [
                {
                    "productName": "Weizen",
                    "quantity": 1,
                    "unitPrice": 100,
                    "netAmount": 100,
                    "taxAmount": 19,
                    "grossAmount": 119,
                }
            ],
        },
    )
    assert credit_create.status_code == 200
    credit_id = credit_create.json()["id"]
    client.post(f"/einkauf/credit-memos/{credit_id}/buchung")

    debit_create = client.post(
        "/einkauf/debit-memos",
        json={
            "supplierId": "SUP-1",
            "settlementId": "SET-1",
            "correctionMode": "DEBIT_MEMO",
            "memoDate": "2026-03-22",
            "reason": "Nachbelastung fuer Settlement-Korrektur",
            "items": [
                {
                    "productName": "Weizen",
                    "quantity": 1,
                    "unitPrice": 80,
                    "netAmount": 80,
                    "taxAmount": 15.2,
                    "grossAmount": 95.2,
                }
            ],
        },
    )
    assert debit_create.status_code == 200
    debit_id = debit_create.json()["id"]
    client.post(f"/einkauf/debit-memos/{debit_id}/buchung")

    credit_completion = client.get("/SET-1/completion-status", params={"variant": "GUTSCHRIFT"})
    assert credit_completion.status_code == 200
    assert credit_completion.json()["completed"] is True
    assert credit_completion.json()["variant"] == "GUTSCHRIFT"

    debit_completion = client.get("/SET-1/completion-status", params={"variant": "BELASTUNG"})
    assert debit_completion.status_code == 200
    assert debit_completion.json()["completed"] is True
    assert debit_completion.json()["variant"] == "BELASTUNG"

    correction_completion = client.get("/SET-1/completion-status", params={"variant": "KORREKTUR"})
    assert correction_completion.status_code == 200
    correction_body = correction_completion.json()
    assert correction_body["completed"] is True
    assert correction_body["variant"] == "KORREKTUR"
    assert len(correction_body["linked_documents"]) == 2
    assert {doc["memo_type"] for doc in correction_body["linked_documents"]} == {"credit", "debit"}
    assert repo["credit_memo"][credit_id]["settlementId"] == "SET-1"
    assert repo["debit_memo"][debit_id]["settlementId"] == "SET-1"
