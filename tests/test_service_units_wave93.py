"""Wave 93 — Unit-Tests fuer personal_service, nats_event_handlers (pure domain functions)."""

from __future__ import annotations

import pytest
import asyncio
from datetime import date


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# personal_service — pure string/date utility functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_to_iso_returns_date_string() -> None:
    from app.services.personal_service import to_iso
    result = to_iso(date(2024, 1, 15))
    assert result == "2024-01-15"


@pytest.mark.unit
def test_to_iso_none_returns_empty_string() -> None:
    from app.services.personal_service import to_iso
    result = to_iso(None)
    assert result == ""


@pytest.mark.unit
def test_split_name_two_parts() -> None:
    from app.services.personal_service import split_name
    first, last = split_name("Max Mustermann")
    assert first == "Max"
    assert last == "Mustermann"


@pytest.mark.unit
def test_split_name_single_word() -> None:
    from app.services.personal_service import split_name
    first, last = split_name("Max")
    assert first == "Max"
    assert last == ""


@pytest.mark.unit
def test_normalize_status_known_value_preserved() -> None:
    from app.services.personal_service import normalize_status
    result = normalize_status("aktiv", "unknown")
    assert result == "aktiv"


@pytest.mark.unit
def test_normalize_status_none_returns_fallback() -> None:
    from app.services.personal_service import normalize_status
    result = normalize_status(None, "unbekannt")
    assert result == "unbekannt"


@pytest.mark.unit
def test_parse_json_list_valid_json() -> None:
    from app.services.personal_service import parse_json_list
    result = parse_json_list('["a", "b", "c"]')
    assert result == ["a", "b", "c"]


@pytest.mark.unit
def test_parse_json_list_invalid_returns_empty() -> None:
    from app.services.personal_service import parse_json_list
    result = parse_json_list("not json")
    assert result == []


@pytest.mark.unit
def test_parse_json_list_none_returns_empty() -> None:
    from app.services.personal_service import parse_json_list
    result = parse_json_list(None)
    assert result == []


@pytest.mark.unit
def test_parse_preferences_valid_json() -> None:
    from app.services.personal_service import parse_preferences
    result = parse_preferences('{"lang": "de", "theme": "dark"}')
    assert result == {"lang": "de", "theme": "dark"}


@pytest.mark.unit
def test_parse_preferences_none_returns_empty_dict() -> None:
    from app.services.personal_service import parse_preferences
    result = parse_preferences(None)
    assert result == {}


@pytest.mark.unit
def test_display_name_from_row_first_last() -> None:
    from app.services.personal_service import display_name_from_row
    row = {"first_name": "Max", "last_name": "Mustermann"}
    result = display_name_from_row(row)
    assert "Max" in result
    assert "Mustermann" in result


@pytest.mark.unit
def test_display_name_from_row_fallback_to_email() -> None:
    from app.services.personal_service import display_name_from_row
    row = {"email": "max@example.com"}
    result = display_name_from_row(row)
    assert result == "max@example.com"


@pytest.mark.unit
def test_role_label_from_row_with_roles() -> None:
    from app.services.personal_service import role_label_from_row
    row = {"roles": ["admin", "manager"]}
    result = role_label_from_row(row)
    assert result == "admin"


@pytest.mark.unit
def test_role_label_from_row_empty_roles_returns_mitarbeiter() -> None:
    from app.services.personal_service import role_label_from_row
    row = {"roles": []}
    result = role_label_from_row(row)
    assert result == "Mitarbeiter"


# ---------------------------------------------------------------------------
# nats_event_handlers — async event processors  (in-memory, no NATS connection)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_handle_audit_event_returns_without_crash() -> None:
    from app.services.nats_event_handlers import handle_audit_event
    payload = {
        "tenant_id": "T001", "entry_id": "E-001", "actor": "admin",
        "action": "create", "resource_type": "invoice", "resource_id": "INV-001",
    }
    result = _run(handle_audit_event(payload))
    # Should return without raising — None is acceptable
    assert result is None or isinstance(result, dict)


@pytest.mark.unit
def test_handle_inventory_movement_event_returns_without_crash() -> None:
    from app.services.nats_event_handlers import handle_inventory_movement_event
    payload = {
        "tenant_id": "T001", "movement_id": "MV-001",
        "article_id": "ART-001", "quantity": 100, "direction": "in",
    }
    result = _run(handle_inventory_movement_event(payload))
    assert result is None or isinstance(result, dict)


@pytest.mark.unit
def test_handle_settlement_created_event_returns_without_crash() -> None:
    from app.services.nats_event_handlers import handle_settlement_created_event
    payload = {
        "tenant_id": "T001", "settlement_id": "SET-001",
        "lieferant_id": "L-001", "betrag": 1500.0,
    }
    result = _run(handle_settlement_created_event(payload))
    assert result is None or isinstance(result, dict)
