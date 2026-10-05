"""Business metrics must aggregate through SQLAlchemy, not Session.func."""
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.api.v1.endpoints import system_metrics


@pytest.mark.asyncio
async def test_business_metrics_uses_real_session_interface():
    db = MagicMock(spec=Session)
    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.group_by.return_value = query
    query.count.return_value = 0
    query.first.return_value = None
    query.all.return_value = []
    db.execute.return_value.scalar.return_value = 0
    system_metrics._metrics_cache.clear()
    result = await system_metrics.get_business_metrics(
        current_user={"sub": "test-user"}, tenant_id="metrics-regression", db=db,
    )
    assert "error" not in result
    assert result["event_bus"]["pending_by_type"] == {}
    assert result["event_bus"]["pending_events"] == 0
    system_metrics._metrics_cache.clear()
