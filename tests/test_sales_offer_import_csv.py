import pytest
from fastapi import HTTPException
from app.services.sales_offer_import import parse_offer_csv

HEADER = "offer_number;subject;customer_id;total_amount;currency;valid_until\n"

def test_quoted_semicolon_bom_and_optional_date():
    rows = parse_offer_csv("\ufeff" + HEADER + 'A-1;"Saat;gut";c1;12.50;EUR;\n')
    assert rows[0]["subject"] == "Saat;gut"
    assert rows[0]["total_amount"] == 12.5
    assert rows[0]["valid_until"] is None

@pytest.mark.parametrize("content", [
    HEADER + "A;;c1;1;EUR;\n",
    HEADER + "A;Test;c1;NaN;EUR;\n",
    HEADER + "A;Test;c1;1;EUR;\nA;Test;c1;2;EUR;\n",
    HEADER + 'A;"unterminated;c1;1;EUR;\n',
    "offer_number;subject\nA;Test\n",
    HEADER + "A;Test;;1;EUR;\n",
])
def test_invalid_rows_fail_before_writes(content):
    with pytest.raises(HTTPException):
        parse_offer_csv(content)


def test_import_replay_and_conflict_are_actor_and_payload_bound(monkeypatch):
    from types import SimpleNamespace
    import json
    from app.services import sales_offer_import as service

    class Result:
        def __init__(self, row=None): self.row = row
        def mappings(self): return self
        def first(self): return self.row

    class DB:
        def __init__(self): self.record = None; self.commits = 0; self.rollbacks = 0; self.events = []
        def execute(self, statement, params):
            sql = str(statement)
            if sql.startswith("SELECT actor_id"): return Result(self.record)
            if sql.startswith("INSERT INTO public.mcp_tool_executions"):
                self.record = {"actor_id": params["actor"], "payload_hash": params["hash"], "result": json.loads(params["result"])}
            return Result()
        def add(self, event): self.events.append(event)
        def commit(self): self.commits += 1
        def rollback(self): self.rollbacks += 1

    actor = SimpleNamespace(tenant_id="t1", subject="person", claims={"identity_type": "human"})
    monkeypatch.setattr(service, "current_identity", lambda: actor)
    monkeypatch.setattr(service, "_write_audit", lambda *a, **kw: "audit")
    calls = []
    monkeypatch.setattr(service, "persist_offer", lambda db, tenant, row, actor: (calls.append(row["offer_number"]) or "one"))
    db = DB()
    content = HEADER + "A;Test;c1;1;EUR;\n"
    assert service.import_offers(db, "t1", content, "key", None)["count"] == 1
    assert service.import_offers(db, "t1", content, "key", None)["replayed"] is True
    assert calls == ["A"] and len(db.events) == 1
    with pytest.raises(HTTPException) as error:
        service.import_offers(db, "t1", content.replace("Test", "Other"), "key", None)
    assert error.value.status_code == 409 and db.rollbacks == 1


def test_import_rolls_back_on_second_offer_failure(monkeypatch):
    from types import SimpleNamespace
    from app.services import sales_offer_import as service
    class DB:
        rolled_back = False
        def execute(self, *args): return self
        def mappings(self): return self
        def first(self): return None
        def rollback(self): self.rolled_back = True
    db = DB()
    monkeypatch.setattr(service, "current_identity", lambda: SimpleNamespace(tenant_id="t1", subject="person", claims={"identity_type": "human"}))
    def persist(db, tenant, row, actor):
        if row["offer_number"] == "B": raise HTTPException(409, "duplicate")
        return "one"
    monkeypatch.setattr(service, "persist_offer", persist)
    with pytest.raises(HTTPException):
        service.import_offers(db, "t1", HEADER + "A;First;c1;1;EUR;\nB;Second;c1;2;EUR;\n", "key", None)
    assert db.rolled_back
