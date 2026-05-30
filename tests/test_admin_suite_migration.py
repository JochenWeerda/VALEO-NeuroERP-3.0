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
    def __init__(self):
        self.settings = {}

    def execute(self, statement, params=None):
        sql = str(statement)
        if sql.startswith("SELECT settings"):
            return _Result((self.settings,))
        if sql.startswith("UPDATE domain_shared.tenants"):
            self.settings = json.loads(params["settings"])
            return _Result()
        raise AssertionError(sql)

    def commit(self):
        return None


@pytest.mark.asyncio
async def test_migration_batch_requires_available_profile_and_starts_as_dry_run():
    db = _FakeDb()
    batch = await admin_suite.create_migration_batch(
        admin_suite.MigrationBatchCreate(
            source_profile="l3",
            source_ref="exports/l3/customers.csv",
            source_hash="12345678abcdef",
            mapping_version="l3-v1",
            dry_run=True,
        ),
        tenant_id="tenant-a",
        db=db,
    )

    assert batch.status == "dry_run"
    assert batch.dry_run is True
    assert all(value is False for value in batch.reconciliation.values())

    with pytest.raises(HTTPException) as error:
        await admin_suite.create_migration_batch(
            admin_suite.MigrationBatchCreate(
                source_profile="amic",
                source_ref="amic",
                source_hash="12345678",
                mapping_version="amic-v0",
                dry_run=True,
            ),
            tenant_id="tenant-a",
            db=db,
        )
    assert error.value.status_code == 409


@pytest.mark.asyncio
async def test_migration_batch_cannot_be_approved_before_reconciliation():
    db = _FakeDb()
    batch = await admin_suite.create_migration_batch(
        admin_suite.MigrationBatchCreate(
            source_profile="csv",
            source_ref="imports/articles.csv",
            source_hash="abcdef12345678",
            mapping_version="csv-article-v1",
            dry_run=True,
        ),
        tenant_id="tenant-a",
        db=db,
    )

    with pytest.raises(HTTPException) as error:
        await admin_suite.approve_migration_batch(batch.id, tenant_id="tenant-a", db=db)
    assert error.value.status_code == 409

    reconciled = await admin_suite.update_migration_reconciliation(
        batch.id,
        admin_suite.MigrationReconciliationUpdate(
            checks={key: True for key in admin_suite.RECONCILIATION_KEYS},
        ),
        tenant_id="tenant-a",
        db=db,
    )
    approved = await admin_suite.approve_migration_batch(batch.id, tenant_id="tenant-a", db=db)

    assert reconciled.status == "staged"
    assert approved.status == "approved"
