"""HTTP route registration and transaction wrapper for HR deletion commands."""
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import training
from app.services import hr_row_delete_commands


@pytest.mark.parametrize("path,kind,legacy", [
    ("/training/onboarding/runs/{item_id}/actions/loeschen", "onboarding", training.legacy_delete_onboarding),
    ("/training/qualifications/{item_id}/actions/loeschen", "qualification", training.legacy_delete_qualification),
    ("/training/assignments/{item_id}/actions/loeschen", "assignment", training.legacy_delete_assignment),
])
def test_versioned_command_registered_and_legacy_delete_guard(monkeypatch, path, kind, legacy):
    route = next(r for r in training.router.routes if r.path == path and "POST" in r.methods)
    assert route.dependencies
    with pytest.raises(HTTPException) as error:
        legacy("row-1").send(None)
    assert error.value.status_code == 409
    db = MagicMock()
    calls = []
    monkeypatch.setattr(hr_row_delete_commands, "delete_hr_row", lambda db, cmd, *, tenant: calls.append((cmd, tenant)) or {"success": True})
    body = training.HrDeleteBody.model_validate({"expected_revision": "a" * 64, "_idempotencyKey": "key"})
    assert training._execute_hr_delete(db, "tenant-a", kind, "row-1", body)["success"]
    assert calls[0][0].kind == kind and calls[0][0].entity_id == "row-1" and calls[0][1] == "tenant-a"
    db.commit.assert_called_once()


def test_command_rolls_back_when_delegate_fails(monkeypatch):
    db = MagicMock()
    def fail(*args, **kwargs):
        raise RuntimeError("synthetic")
    monkeypatch.setattr(hr_row_delete_commands, "delete_hr_row", fail)
    body = training.HrDeleteBody.model_validate({"expected_revision": "a" * 64, "_idempotencyKey": "key"})
    with pytest.raises(HTTPException) as error:
        training._execute_hr_delete(db, "tenant-a", "qualification", "row-1", body)
    assert error.value.status_code == 503
    db.rollback.assert_called_once()
    db.commit.assert_not_called()
