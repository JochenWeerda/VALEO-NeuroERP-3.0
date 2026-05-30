from __future__ import annotations

import json

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import admin_suite


class _Result:
    def __init__(self, row=None):
        self._row = row

    def first(self):
        return self._row


class _FakeDb:
    def __init__(self, settings=None):
        self.settings = settings or {}
        self.commits = 0

    def execute(self, statement, params=None):
        sql = str(statement)
        if sql.startswith("SELECT settings"):
            return _Result((self.settings,))
        if sql.startswith("UPDATE domain_shared.tenants"):
            self.settings = json.loads(params["settings"])
            return _Result()
        raise AssertionError(sql)

    def commit(self):
        self.commits += 1


def test_setup_session_starts_unchecked_without_implicit_completion():
    session = admin_suite._build_setup_session("tenant-a", None)

    assert session.tenant_id == "tenant-a"
    assert session.status == "unchecked"
    assert session.completed_count == 0
    assert session.total_count == len(admin_suite.SETUP_STEPS)
    assert all(step.status == "unchecked" for step in session.steps)


@pytest.mark.asyncio
async def test_setup_step_update_is_persisted_and_resumable():
    db = _FakeDb()

    updated = await admin_suite.update_setup_step(
        "company",
        admin_suite.SetupStepUpdate(status="completed", evidence="Firmenstamm geprueft", responsible="admin"),
        tenant_id="tenant-a",
        db=db,
    )
    resumed = await admin_suite.get_setup_session(tenant_id="tenant-a", db=db)

    assert db.commits == 1
    assert updated.completed_count == 1
    assert resumed.completed_count == 1
    assert resumed.steps[0].evidence == "Firmenstamm geprueft"
    assert resumed.steps[0].responsible == "admin"


@pytest.mark.asyncio
async def test_setup_step_update_rejects_unknown_steps():
    with pytest.raises(HTTPException) as error:
        await admin_suite.update_setup_step(
            "not-a-step",
            admin_suite.SetupStepUpdate(status="completed"),
            tenant_id="tenant-a",
            db=_FakeDb(),
        )

    assert error.value.status_code == 404
