"""Real summary handler with database-result doubles; no SQL/RLS acceptance."""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.budget_planning import budget_summary

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """No compatibility-app identity or application startup needed here."""
    yield


def database(actual):
    plan = {"id": "synthetic-budget", "plan_name": "Synthetic", "plan_year": 2026}
    db = Mock()
    db.execute.side_effect = [
        Mock(), Mock(),
        Mock(mappings=lambda: SimpleNamespace(first=lambda: plan)),
        Mock(scalar=lambda: Decimal("1000")),
        actual if isinstance(actual, Exception) else Mock(scalar=lambda: actual),
    ]
    return db


@pytest.mark.parametrize("failure", [RuntimeError("private SQL and input"), ConnectionError("private DSN")])
def test_failed_actual_read_never_becomes_a_reported_zero(failure):
    db = database(failure)
    with pytest.raises(HTTPException) as caught:
        budget_summary(tenant_id="synthetic-tenant", db=db)
    assert caught.value.status_code == 503
    assert "private" not in str(caught.value.detail)
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


@pytest.mark.parametrize("actual,expected,pct", [(Decimal("250"), 250.0, 25.0), (Decimal("0"), 0.0, 0.0), (None, 0.0, 0.0)])
def test_successful_actual_read_preserves_real_value_including_zero(actual, expected, pct):
    db = database(actual)
    result = budget_summary(tenant_id="synthetic-tenant", db=db)
    assert result["total_budget_eur"] == 1000.0
    assert result["total_actual_eur"] == expected
    assert result["pct_used"] == pct
    assert db.execute.call_args.args[1] == {"tid": "synthetic-tenant", "yr": 2026}
    db.rollback.assert_not_called()
    db.commit.assert_not_called()
