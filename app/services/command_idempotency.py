"""Transaction-bound replay helpers for versioned domain commands.

The caller must authorize the verified principal before invoking these helpers.
The advisory lock, business mutation, audit, outbox and replay record belong to
one caller-owned transaction. No helper commits or rolls back that transaction.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session


_HASH = re.compile(r"^[0-9a-f]{64}$")


def _validate(tenant: str, command: str, key: str, actor: str, fingerprint: str) -> None:
    for value, limit in ((tenant, 100), (command, 200), (key, 200), (actor, 1000)):
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise HTTPException(422, "Ungueltiger Wiederholungsvertrag")
    if not isinstance(fingerprint, str) or not _HASH.fullmatch(fingerprint):
        raise HTTPException(422, "Ungueltiger Auftragsfingerabdruck")


def lock_and_replay(db: Session, *, tenant: str, command: str, key: str, actor: str,
                    fingerprint: str) -> dict[str, Any] | None:
    """Lock one tenant/command/key and read its actor- and payload-bound result.

    Caller authorization must already have succeeded, including on replays.
    Returned data does not imply any commit; the caller owns transaction scope.
    """
    _validate(tenant, command, key, actor, fingerprint)
    material = json.dumps([tenant, command, key]).encode("utf-8")
    lock = int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=True)
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock})
    row = db.execute(text("""
        SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
        WHERE tenant_id=:tenant AND tool_name=:command AND idempotency_key=:key
    """), {"tenant": tenant, "command": command, "key": key}).mappings().first()
    if row is None:
        return None
    stored_hash = row.get("payload_hash")
    if (row.get("actor_id") != actor or not isinstance(stored_hash, str) or not _HASH.fullmatch(stored_hash)
            or not hmac.compare_digest(stored_hash, fingerprint)):
        raise HTTPException(409, "Wiederholungsschluessel gehoert zu einem anderen Auftrag")
    result = row.get("result")
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except ValueError as exc:
            raise HTTPException(503, "Gespeichertes Auftragsergebnis ist ungueltig") from exc
    if not isinstance(result, dict):
        raise HTTPException(503, "Gespeichertes Auftragsergebnis ist ungueltig")
    return {**result, "replayed": True}


def store_execution(db: Session, *, tenant: str, command: str, key: str, actor: str,
                    fingerprint: str, result: dict[str, Any]) -> None:
    """Store a result in the same transaction as its mutation and audit."""
    _validate(tenant, command, key, actor, fingerprint)
    if not isinstance(result, dict):
        raise HTTPException(422, "Ungueltiges Auftragsergebnis")
    db.execute(text("""
        INSERT INTO public.mcp_tool_executions
            (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
        VALUES (:tenant, :command, :key, :actor, :fingerprint, CAST(:result AS jsonb))
    """), {"tenant": tenant, "command": command, "key": key, "actor": actor,
           "fingerprint": fingerprint, "result": json.dumps(result, ensure_ascii=False)})
