from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints.agrar_feldbuch import get_duengemittelmengen
from app.services.inventory_compat_service import InventoryCompatService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_fertilizer_quantities_are_paged_in_database() -> None:
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.count.return_value = 501
    aggregate_query = MagicMock()
    aggregate_query.one.return_value = (1000, 120, 80, 60)
    query.with_entities.return_value = aggregate_query
    query.options.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    result = await get_duengemittelmengen(
        jahr=2026,
        customer_id=None,
        schlag_id=None,
        q=None,
        page=3,
        page_size=50,
        db=db,
        tenant_id="tenant-1",
    )

    assert result["total"] == 501 and result["menge"] == 1000.0
    query.offset.assert_called_once_with(100)
    query.limit.assert_called_once_with(50)
    query.all.assert_called_once()


def test_legacy_inventory_lot_list_is_tenant_scoped() -> None:
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = []

    assert InventoryCompatService(db, "tenant-1").list_lots() == {"items": [], "total": 0}
    assert "tenant_id" in str(query.filter.call_args.args[0])
