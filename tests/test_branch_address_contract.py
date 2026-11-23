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
    statement, bindings = db.execute.call_args_list[1].args
    assert "CAST(:address AS jsonb)" in statement.text
    assert statement.compile().params["address"] is None
    assert json.loads(bindings["address"]) == address
    assert bindings["tenant_id"] == "tenant"
    db.commit.assert_called_once()
