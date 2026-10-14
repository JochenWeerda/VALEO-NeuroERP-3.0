"""Release/correction invariants discovered by real Studio simulation."""
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """Pure mocked services require no compatibility-app initialization."""
    yield

from app.core.exceptions import ValidationFailedError
from app.services.harvest_acceptance_service import HarvestAcceptanceService

@pytest.mark.parametrize("status,invoice", [("final",None),("credit_note_created","invoice"),("paid","invoice"),("draft","invoice")])
def test_bound_acceptance_cannot_be_cancelled_or_released_again(status, invoice):
    db = MagicMock()
    svc = HarvestAcceptanceService(db,"own")
    obj = SimpleNamespace(release_status=status, invoice_id=invoice)
    svc._get_or_raise = lambda _: obj
    with pytest.raises(ValidationFailedError):
        svc.cancel("acceptance", "unsafe correction")
    with pytest.raises(ValidationFailedError):
        svc.release_acceptance("acceptance", "final", True, True, "actor")
    db.commit.assert_not_called()
    db.add.assert_not_called()

def test_lot_query_uses_parent_tenant_and_line_constructor_matches_model():
    from datetime import date
    from modules.agrar.services.partie_service import create_harvest_acceptance_lines
    from app.infrastructure.models import HarvestAcceptance, HarvestAcceptanceLine
    db=MagicMock()
    query=db.query.return_value
    query.filter.return_value=query
    query.join.return_value=query
    query.first.return_value=SimpleNamespace(delivery_date=date(2026,1,15))
    query.scalar.return_value=0
    lines=create_harvest_acceptance_lines(db,"acceptance","own",[{"qty_kg_allocated":10}])
    assert len(lines)==1 and isinstance(lines[0],HarvestAcceptanceLine)
    assert lines[0].lot_id=="LOT-20260115-001"
    assert query.join.call_args.args[0] is HarvestAcceptance
    clauses=[str(arg) for call in query.filter.call_args_list for arg in call.args]
    assert any("harvest_acceptances.tenant_id" in clause for clause in clauses)
