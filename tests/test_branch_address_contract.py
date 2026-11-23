"""Keep branch addresses valid JSON and bound to the SQL statement."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints.branches import BranchCreate, BranchUpdate, create_branch, update_branch


@pytest.mark.asyncio
@pytest.mark.parametrize("create", [True, False])
async def test_branch_address_is_bound_as_json(create):
    db = MagicMock()
    address = {"street": "O'Brien", "primary": True, "extra": None}
    now = datetime.now(timezone.utc)
    db.execute.return_value.first.return_value = None
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "branch", "tenant_id": "tenant", "branch_number": 1,
        "name": "Nord", "address": address, "created_at": now, "updated_at": now,
    }
    if create:
        await create_branch(BranchCreate(branch_number=1, name="Nord", address=address), tenant_id="tenant", db=db)
    else:
        await update_branch("branch", BranchUpdate(address=address), tenant_id="tenant", db=db)
    statement, bindings = db.execute.call_args_list[int(create)].args
    assert "CAST(:address AS jsonb)" in statement.text
    if not create:
        assert "RETURNING *" in statement.text
        db.execute.assert_called_once()
    assert statement.compile().params["address"] is None
    assert json.loads(bindings["address"]) == address
    assert bindings["tenant_id"] == "tenant"
    db.commit.assert_called_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_branch_addresses_roundtrip_in_postgresql(require_db):
    from uuid import uuid4

    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.api.v1.endpoints.branches import get_branch
    from app.core.database import engine

    tenant = str(uuid4())
    original = {"street": "O'Brien", "primary": True, "extra": None}
    revised = {"street": 'Markt "Nord"', "primary": False, "extra": {"number": 7}}
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:id, :name, :domain, TRUE)"),
                {"id": tenant, "name": "Synthetic branch address test", "domain": f"{tenant}.test.local"},
            )
            with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
                branch = await create_branch(
                    BranchCreate(branch_number=1, name="Nord", address=original), tenant_id=tenant, db=db,
                )
                assert branch.address == original
                updated = await update_branch(branch.id, BranchUpdate(address=revised), tenant_id=tenant, db=db)
                assert updated.address == revised
                assert (await get_branch(branch.id, tenant_id=tenant, db=db)).address == revised
        finally:
            transaction.rollback()
