import json
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.services import mcp_execution_service as service
from app.services import mailkonto_service


def request(password, mode="execute"):
    return service.ToolExecutionRequest(
        tool_name="admin.postfach.speichern", mode=mode, idempotency_key="key-1",
        parameters={"kennung": "info", "absender_email": "info@example.com",
                    "passwort": password, "reason": "Einrichten"},
    )


def test_postfach_replay_binds_password_and_keeps_outputs_secret_free(monkeypatch):
    monkeypatch.setenv("VALEO_SECRET_KEY", "synthetic-key-for-tests-only-123456789")
    receipts = {}
    audit = []
    db = Mock()
    monkeypatch.setattr(service, "_advisory_lock", lambda *args: None)

    def replay(db, tenant, tool, key, actor, fingerprint):
        if not receipts:
            return None
        if receipts["fingerprint"] != fingerprint:
            raise HTTPException(409, "Idempotency key is already bound to another request")
        return {**receipts["result"], "replayed": True}

    monkeypatch.setattr(service, "_replay_or_none", replay)
    monkeypatch.setattr(service, "_store_execution", lambda db, **kw: receipts.update(kw))
    monkeypatch.setattr(service, "_write_audit", lambda db, **kw: audit.append(kw) or "audit-1")
    save = Mock(return_value={"id": "mail-1"})
    monkeypatch.setattr(mailkonto_service, "speichern", save)
    first = service._postfach_speichern(db, request("first-secret"), "actor", "tenant-a")
    again = service._postfach_speichern(db, request("first-secret"), "actor", "tenant-a")
    with pytest.raises(HTTPException) as exc:
        service._postfach_speichern(db, request("second-secret"), "actor", "tenant-a")
    assert exc.value.status_code == 409
    assert again["replayed"] is True
    assert save.call_count == 1
    preview = service._postfach_speichern(db, request("first-secret", "dryRun"), "actor", "tenant-a")
    for value in (first, again, receipts, audit, preview, exc.value.detail):
        assert "first-secret" not in json.dumps(value)
        assert "second-secret" not in json.dumps(value)
    assert preview["proposedChanges"]["hat_passwort"] is True


def test_postfach_execute_fails_closed_without_key_but_preview_works(monkeypatch):
    monkeypatch.delenv("VALEO_SECRET_KEY", raising=False)
    db = Mock()
    monkeypatch.setattr(service, "_advisory_lock", Mock())
    with pytest.raises(HTTPException) as exc:
        service._postfach_speichern(db, request("secret"), "actor", "tenant-a")
    assert exc.value.status_code == 503
    service._advisory_lock.assert_not_called()
    assert service._postfach_speichern(db, request("secret", "dryRun"), "actor", "tenant-a")["success"]
