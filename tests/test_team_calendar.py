from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.services.calendar_projection_service import CalendarProjectionService

pytestmark = pytest.mark.unit
NOW = datetime(2026, 8, 21, 8, tzinfo=UTC)


def _result(rows):  # noqa: ANN001, ANN202
    result = MagicMock()
    result.mappings.return_value.all.return_value = rows
    return result


def test_rejects_unapproved_team_scope() -> None:
    db = MagicMock()
    db.execute.return_value = _result([{"team_id": "team-a"}])
    with pytest.raises(PermissionError, match="verweigert"):
        CalendarProjectionService(db).list_team_items(
            "tenant-1",
            NOW,
            NOW + timedelta(days=7),
            user_ref="user-1",
            team_ids=["team-b"],
        )


def test_private_foreign_event_is_free_busy_redacted() -> None:
    db = MagicMock()
    memberships = _result([{"team_id": "team-a"}])
    items = _result(
        [
            {
                "id": "event-1",
                "tenant_id": "tenant-1",
                "owner_id": "user-2",
                "team_id": "team-a",
                "visibility": "private",
                "response_status": "accepted",
                "title": "Personalgespraech",
                "object_type": "crm_activity",
                "object_id": "secret",
                "object_route": "/secret",
                "object_screen_id": "crm/customer-360",
                "payload": {"note": "secret"},
            }
        ]
    )
    db.execute.side_effect = [memberships, items]
    result = CalendarProjectionService(db).list_team_items(
        "tenant-1",
        NOW,
        NOW + timedelta(days=7),
        user_ref="user-1",
        team_ids=["team-a"],
        can_view_details=True,
    )
    assert result[0]["title"] == "Belegt"
    assert result[0]["object_route"] is None
    assert result[0]["payload"] == {"availability": "busy", "redacted": True}


def test_team_detail_requires_permission_and_declined_filter_is_bound() -> None:
    db = MagicMock()
    db.execute.side_effect = [_result([{"team_id": "team-a"}]), _result([])]
    CalendarProjectionService(db).list_team_items(
        "tenant-1",
        NOW,
        NOW + timedelta(days=7),
        user_ref="user-1",
        team_ids=["team-a"],
        include_declined=True,
        can_view_details=False,
    )
    params = db.execute.call_args_list[1].args[1]
    assert params["include_declined"] is True
    assert params["team_ids"] == ["team-a"]


def test_screen_declares_team_privacy_contract() -> None:
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("planung/kalender")
    assert definition and definition["calendar"]["teamView"] is True
    assert definition["calendar"]["privacy"]["redactObjectLinks"] is True
