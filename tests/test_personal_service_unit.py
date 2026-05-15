"""Unit tests for PersonalService (no DB required)."""
from datetime import date
from unittest.mock import MagicMock, call

import pytest

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.personal_service import (
    PersonalService,
    _parse_date,
    _parse_event_dt,
    normalize_status,
    split_name,
    to_iso,
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_normalize_status_maps_inaktiv():
    assert normalize_status("inaktiv") == "inaktiv"


def test_normalize_status_passes_through_known():
    assert normalize_status("aktiv") == "aktiv"
    assert normalize_status("urlaub") == "urlaub"


def test_normalize_status_fallback():
    assert normalize_status(None) == "aktiv"
    assert normalize_status("xyz") == "aktiv"


def test_split_name_two_parts():
    assert split_name("Max Mustermann") == ("Max", "Mustermann")


def test_split_name_single():
    assert split_name("Madonna") == ("Madonna", "")


def test_split_name_three_parts():
    first, last = split_name("Johann Sebastian Bach")
    assert first == "Johann"
    assert "Bach" in last


def test_to_iso_date():
    assert to_iso(date(2024, 3, 15)) == "2024-03-15"


def test_to_iso_none():
    assert to_iso(None) == ""


def test_parse_date_valid():
    d = _parse_date("2025-06-01")
    assert d == date(2025, 6, 1)


def test_parse_date_invalid():
    with pytest.raises(ValidationFailedError):
        _parse_date("not-a-date")


def test_parse_event_dt_valid():
    dt = _parse_event_dt("2025-06-01T10:00:00")
    assert dt.year == 2025


def test_parse_event_dt_z_suffix():
    dt = _parse_event_dt("2025-06-01T10:00:00Z")
    assert dt.year == 2025


def test_parse_event_dt_invalid():
    with pytest.raises(ValidationFailedError):
        _parse_event_dt("not-a-datetime")


# ---------------------------------------------------------------------------
# PersonalService — mitarbeiter mutations (mocked DB)
# ---------------------------------------------------------------------------

def _make_svc(tenant_id="t1"):
    db = MagicMock()
    svc = PersonalService(db, tenant_id)
    return svc, db


class FakeMitarbeiterPayload:
    name = "Max Mustermann"
    email = "max@test.de"
    abteilung = "IT"
    position = "Entwickler"
    status = "aktiv"


def test_create_mitarbeiter_conflict():
    svc, db = _make_svc()
    db.execute.return_value.first.return_value = MagicMock()  # existing record
    with pytest.raises(ConflictError):
        svc.create_mitarbeiter(FakeMitarbeiterPayload())


def test_create_mitarbeiter_inserts():
    svc, db = _make_svc()
    # first execute = check existing (returns None), second = INSERT
    db.execute.return_value.first.return_value = None
    user_id = svc.create_mitarbeiter(FakeMitarbeiterPayload())
    assert isinstance(user_id, str) and len(user_id) > 0
    db.commit.assert_called_once()


def test_update_mitarbeiter_not_found():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 0
    with pytest.raises(EntityNotFoundError):
        svc.update_mitarbeiter("uid-1", FakeMitarbeiterPayload())


def test_update_mitarbeiter_success():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 1
    svc.update_mitarbeiter("uid-1", FakeMitarbeiterPayload())
    db.commit.assert_called_once()


def test_delete_mitarbeiter_not_found():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 0
    with pytest.raises(EntityNotFoundError):
        svc.delete_mitarbeiter("uid-1")


def test_delete_mitarbeiter_success():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 1
    svc.delete_mitarbeiter("uid-1")
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# PersonalService — shifts
# ---------------------------------------------------------------------------

def test_list_shifts_returns_dicts():
    svc, db = _make_svc()
    mock_row = {"id": "s1", "shift_date": date(2025, 5, 1),
                "name": "Frühschicht", "location_code": "main",
                "required_role": "worker", "required_qualifications": "[]",
                "required_headcount": 2, "starts_at": "06:00", "ends_at": "14:00",
                "assigned_employee_refs": "[]", "status": "planned", "conflicts": "[]", "notes": None}
    db.execute.return_value.mappings.return_value.all.return_value = [mock_row]
    rows = svc.list_shifts()
    assert rows[0]["id"] == "s1"


def test_delete_shift_not_found():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 0
    with pytest.raises(EntityNotFoundError):
        svc.delete_shift("shift-99")


def test_delete_shift_success():
    svc, db = _make_svc()
    db.execute.return_value.rowcount = 1
    svc.delete_shift("shift-1")
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# PersonalService — list_calendar_events
# ---------------------------------------------------------------------------

def test_list_calendar_events_calls_db():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = []
    result = svc.list_calendar_events()
    assert result == []
    db.execute.assert_called_once()


def test_list_calendar_events_with_filters():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = []
    svc.list_calendar_events(
        start="2025-05-01T00:00:00",
        end="2025-05-31T23:59:59",
        employee_ref="emp-1",
        event_type="training",
    )
    # Just ensure it runs without error and the execute was called
    db.execute.assert_called_once()


# ---------------------------------------------------------------------------
# PersonalService — list_payroll_exports
# ---------------------------------------------------------------------------

def test_list_payroll_exports_returns_list():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = []
    result = svc.list_payroll_exports()
    assert result == []


# ---------------------------------------------------------------------------
# PersonalService — field service plans
# ---------------------------------------------------------------------------

def test_list_field_service_plans_no_filter():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = []
    result = svc.list_field_service_plans()
    assert result == []


def test_list_field_service_plans_with_employee_ref():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = []
    svc.list_field_service_plans(employee_ref="emp-42")
    db.execute.assert_called_once()
