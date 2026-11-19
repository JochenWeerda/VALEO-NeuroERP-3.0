"""Vertraege fuer Idempotenz und serverseitige Identitaet delegierter Aktionen."""
import asyncio
import json

import pytest

from app.services import mask_action_runtime_service as runtime


class Result:
    def __init__(self, row=None):
        self.row = row

    def mappings(self):
        return self

    def first(self):
        return self.row


class FakeSession:
    def __init__(self, previous=None, fingerprint=None):
        self.previous = previous
        self.fingerprint = fingerprint
        self.calls = []
        self.commits = 0

    def execute(self, statement, params):
        sql = str(statement)
        self.calls.append((sql, params))
        if "SELECT id, entity_id" in sql:
            return Result(self.previous)
        if "SELECT payload::jsonb->>'request_fingerprint'" in sql:
            return Result(None if self.fingerprint is None else {"request_fingerprint": self.fingerprint})
        return Result()

    def rollback(self):
        pass

    def commit(self):
        self.commits += 1


def run(db, *, fingerprint="fp", entity="customer-1", check=None, actor="verified-user"):
    mutations = []

    def delegate(*args):
        mutations.append(True)
        return "ok"

    result = asyncio.run(runtime.run_delegated_mask_action(
        db, action_key="edit", entity_type="customer", entity_id=entity,
        tenant_id="tenant-1", body={"_idempotencyKey": "key", "performed_by": "spoofed"},
        check_fn=check or (lambda *args: []), delegate_fn=delegate,
        outbox_event_type="customer.changed", performed_by=actor,
        request_fingerprint=fingerprint,
    ))
    return result, mutations


@pytest.mark.parametrize("stored,entity,success", [
    ("fp", "customer-1", True),
    ("different", "customer-1", False),
    (None, "customer-1", False),
    ("fp", "customer-2", False),
])
def test_replay_validates_fingerprint_and_entity(stored, entity, success):
    db = FakeSession({"id": "audit-1", "entity_id": "customer-1"}, stored)
    result, mutations = run(db, entity=entity)
    assert result.success is success
    assert not mutations
    assert db.commits == 0
    query = next(params for sql, params in db.calls if "SELECT payload::jsonb->>'request_fingerprint'" in sql)
    assert query == {"t": "tenant-1", "e": "customer-1", "a": "audit-1"}
    if not success:
        assert result.validationErrors[0]["severity"] == "blocking"


def test_second_check_rejects_key_used_during_validation():
    db = FakeSession()

    def check(*args):
        db.previous = {"id": "audit-1", "entity_id": "customer-1"}
        db.fingerprint = "different"
        return []

    result, mutations = run(db, check=check)
    assert not result.success
    assert not mutations
    assert db.commits == 0


def test_actor_and_fingerprint_are_server_metadata():
    db = FakeSession()
    result, mutations = run(db)
    assert result.success and mutations == [True]
    audit = next(params for sql, params in db.calls if "INSERT INTO domain_crm.crm_action_audit_log" in sql)
    assert audit["durch"] == "verified-user"
    assert "spoofed" not in audit.values()
    outbox = next(params for sql, params in db.calls if "INSERT INTO outbox_events" in sql)
    payload = json.loads(outbox["payload"])
    assert payload["performed_by"] == "verified-user"
    assert payload["request_fingerprint"] == "fp"


def test_legacy_call_avoids_fingerprint_lookup_and_actor_column():
    db = FakeSession()
    result, _ = run(db, fingerprint=None, actor=None)
    assert result.success
    assert not any("SELECT payload::jsonb->>'request_fingerprint'" in sql for sql, _ in db.calls)
    audit = next(params for sql, params in db.calls if "INSERT INTO domain_crm.crm_action_audit_log" in sql)
    assert "durch" not in audit
    outbox = next(params for sql, params in db.calls if "INSERT INTO outbox_events" in sql)
    payload = json.loads(outbox["payload"])
    assert "performed_by" not in payload and "request_fingerprint" not in payload
