"""Unit tests for HarvestAcceptanceService."""
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError


def _make_svc(tenant_id="t1"):
    db = MagicMock()
    from app.services.harvest_acceptance_service import HarvestAcceptanceService
    return HarvestAcceptanceService(db, tenant_id), db


def _mock_obj(**kwargs):
    obj = MagicMock()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# _get_or_raise
# ---------------------------------------------------------------------------

def _stub_get(db, return_val):
    """Configure db mock to return return_val from any .query().filter...first() chain."""
    # Use a flexible mock that returns the same thing for any filter chain
    q = MagicMock()
    q.filter.return_value = q
    q.first.return_value = return_val
    q.order_by.return_value = q
    q.limit.return_value = q
    q.all.return_value = [] if return_val is None else [return_val]
    db.query.return_value = q
    return q


def test_get_or_raise_not_found():
    svc, db = _make_svc()
    _stub_get(db, None)
    with pytest.raises(EntityNotFoundError):
        svc._get_or_raise("id-99")


def test_get_or_raise_found():
    svc, db = _make_svc()
    obj = _mock_obj(id="id-1")
    _stub_get(db, obj)
    result = svc._get_or_raise("id-1")
    assert result is obj


# ---------------------------------------------------------------------------
# delete_acceptance
# ---------------------------------------------------------------------------

def test_delete_acceptance_draft_succeeds():
    svc, db = _make_svc()
    obj = _mock_obj(release_status="draft")
    _stub_get(db, obj)
    svc.delete_acceptance("id-1")
    db.delete.assert_called_once_with(obj)
    db.commit.assert_called_once()


def test_delete_acceptance_non_draft_raises():
    svc, db = _make_svc()
    obj = _mock_obj(release_status="released")
    _stub_get(db, obj)
    with pytest.raises(ValidationFailedError):
        svc.delete_acceptance("id-1")


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------

def test_cancel_final_raises():
    svc, db = _make_svc()
    obj = _mock_obj(release_status="final")
    _stub_get(db, obj)
    with pytest.raises(ValidationFailedError):
        svc.cancel("id-1", "mistake")


def test_cancel_already_cancelled_raises():
    svc, db = _make_svc()
    obj = _mock_obj(release_status="cancelled")
    _stub_get(db, obj)
    with pytest.raises(ConflictError):
        svc.cancel("id-1", "mistake")


def test_cancel_success():
    svc, db = _make_svc()
    obj = _mock_obj(release_status="draft", notes="")
    _stub_get(db, obj)
    with patch("app.services.harvest_acceptance_service._to_dict_with_positions", return_value={"id": "id-1"}):
        result = svc.cancel("id-1", "test reason")
    assert obj.release_status == "cancelled"
    assert "STORNIERT" in obj.notes
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# derive_nuts2
# ---------------------------------------------------------------------------

def test_derive_nuts2_no_postal_code():
    svc, db = _make_svc()
    obj = _mock_obj(origin_postal_code=None)
    _stub_get(db, obj)
    with pytest.raises(ValidationFailedError):
        svc.derive_nuts2("id-1")


def test_derive_nuts2_success():
    svc, db = _make_svc()
    obj = _mock_obj(origin_postal_code="80333", origin_country_code="DE",
                    nuts_version="NUTS 2024")
    _stub_get(db, obj)
    result = svc.derive_nuts2("id-1")
    # Munich -> DE21 Oberbayern
    assert result["origin_nuts2_code"] == "DE21"
    assert obj.origin_nuts2_code == "DE21"
    db.commit.assert_called_once()


def test_derive_nuts2_unknown_postal():
    svc, db = _make_svc()
    obj = _mock_obj(origin_postal_code="00001", origin_country_code="DE",
                    nuts_version=None)
    _stub_get(db, obj)
    result = svc.derive_nuts2("id-1")
    assert result["origin_nuts2_code"] is None


# ---------------------------------------------------------------------------
# calculate_frachtkosten
# ---------------------------------------------------------------------------

def test_calculate_frachtkosten_missing_data():
    svc, db = _make_svc()
    # No gewicht_kg in data, no weighing ticket, no positions
    obj = _mock_obj(weighing_ticket_id=None)
    q = _stub_get(db, obj)
    q.all.return_value = []  # no positions
    data = {}  # no gewicht_kg
    with pytest.raises(ValidationFailedError):
        svc.calculate_frachtkosten("id-1", data)


def test_calculate_frachtkosten_basic():
    svc, db = _make_svc()
    obj = _mock_obj(id="id-1", weighing_ticket_id=None)
    _stub_get(db, obj)
    data = {"gewicht_kg": 20000, "entfernung_km": 100}
    result = svc.calculate_frachtkosten("id-1", data)
    assert "frachtkosten_eur" in result
    assert result["gewicht_kg"] == 20000
