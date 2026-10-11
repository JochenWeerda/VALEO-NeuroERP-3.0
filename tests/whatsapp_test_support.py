"""Explicit storage boundary double for DB-free template and HTTP-guard tests.

Real SQL, transactions, replay and restart are tested in test_whatsapp_persistence.
"""
import uuid
from functools import partial


class NoDatabaseSession:
    def commit(self):
        pass


def attach_unit_store(monkeypatch, service):
    messages = {}
    monkeypatch.setattr(service, "_OUTBOX", messages, raising=False)
    db = NoDatabaseSession()

    def persist(msg, db, actor, key):
        messages.setdefault(msg.tenant_id, []).append(service._message_payload(msg))
        return msg

    def read(tenant, db, limit):
        return list(reversed(messages.get(tenant, [])))[:limit]

    monkeypatch.setattr(service, "_persist_message", persist)
    monkeypatch.setattr(service, "_read_outbox", read)
    for name in ("send_dokument_ready", "send_lieferankuendigung"):
        original = getattr(service, name)

        def call(*args, _original=original, **kwargs):
            kwargs.setdefault("db", db)
            kwargs.setdefault("actor", "unit-actor")
            kwargs.setdefault("idempotency_key", uuid.uuid4().hex)
            return _original(*args, **kwargs)

        monkeypatch.setattr(service, name, call)
    monkeypatch.setattr(service, "get_outbox", partial(service.get_outbox, db=db))
    return db
