"""A blocked cash close cannot double-book an unrelated daily journal."""

from unittest.mock import MagicMock
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import finance_actions
from app.core.database import get_db
from app.core.tenant import get_tenant_id
import test_journal_amount_integrity as amount_contracts

case = amount_contracts.case
store = amount_contracts.store


def client(db, tenant, prefix="/finance"):
    app = FastAPI()
    app.include_router(finance_actions.router, prefix=prefix)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: tenant
    return TestClient(app)


def test_cash_close_never_accesses_database_or_reports_success():
    db = MagicMock()
    with client(db, "tenant") as api:
        for body in ({}, {"id": "cash-proof", "betrag": "100.00"}, {"id": "cash-proof"}):
            response = api.post("/finance/cash/close-day", json=body)
            assert response.status_code == 409
            assert "Gegenkontierung" in response.json()["detail"]
            assert "success" not in response.json()
    db.execute.assert_not_called()
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_existing_journals_and_lines_remain_identical_after_repeated_closing(case):
    db, tenant, _, _ = case
    sql = (
        "SELECT row_to_json(j) FROM domain_erp.journal_entries j WHERE tenant_id=:t ORDER BY id",
        "SELECT row_to_json(l) FROM domain_erp.journal_entry_lines l WHERE tenant_id=:t ORDER BY id",
    )
    before = [db.execute(text(q), {"t": tenant}).scalars().all() for q in sql]
    assert len(before[0]) == 1 and len(before[1]) == 2
    with client(db, tenant) as api:
        for _ in range(3):
            response = api.post("/finance/cash/close-day", json={"id": "persisted-form"})
            assert response.status_code == 409
    assert [db.execute(text(q), {"t": tenant}).scalars().all() for q in sql] == before


def test_openapi_advertises_conflict_without_success_response():
    with client(MagicMock(), "tenant") as api:
        operation = api.get("/openapi.json").json()["paths"]["/finance/cash/close-day"]["post"]
    assert "409" in operation["responses"]
    assert "200" not in operation["responses"]
    assert "keine Journalbuchung" in operation["responses"]["409"]["description"]


def test_scoped_openapi_matches_actual_route_contract():
    snapshot = json.loads((Path(__file__).resolve().parents[1] /
        "docs/schnittstellen/contracts/cash-close-retirement-20261005.openapi.json").read_text(encoding="utf-8"))
    with client(MagicMock(), "tenant", prefix="/api/v1/finance") as api:
        current = api.get("/openapi.json").json()
    assert snapshot["paths"]["/api/v1/finance/cash/close-day"] == current["paths"]["/api/v1/finance/cash/close-day"]
