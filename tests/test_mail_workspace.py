from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.mail_workspace_service import MailWorkspaceError, MailWorkspaceService

pytestmark = pytest.mark.unit


def _first(value):  # noqa: ANN001, ANN202
    result = MagicMock()
    result.mappings.return_value.first.return_value = value
    return result


def test_ingest_requires_message_id() -> None:
    with pytest.raises(MailWorkspaceError, match="Message-ID"):
        MailWorkspaceService(MagicMock(), "tenant-1").ingest(
            message_id="",
            role_key="crm",
            direction="incoming",
            from_address=None,
            to_addresses=[],
            subject=None,
            body_text="",
        )


def test_ingest_is_idempotent() -> None:
    db = MagicMock()
    inserted = _first(None)
    existing = MagicMock()
    existing.mappings.return_value.one.return_value = {
        "id": "mail-1",
        "status": "received",
    }
    db.execute.side_effect = [inserted, existing]
    result = MailWorkspaceService(db, "tenant-1").ingest(
        message_id="message@example",
        role_key="crm",
        direction="incoming",
        from_address="a@example.org",
        to_addresses=["erp@example.org"],
        subject="Test",
        body_text="Text",
    )
    assert result == {"id": "mail-1", "status": "received", "idempotent": True}
    db.commit.assert_not_called()


def test_list_requires_at_least_one_role() -> None:
    with pytest.raises(PermissionError, match="Rollenpostfach"):
        MailWorkspaceService(MagicMock(), "tenant-1").list_page(allowed_roles=set())


def test_list_is_tenant_and_role_scoped() -> None:
    db = MagicMock()
    count = MagicMock()
    count.scalar_one.return_value = 2
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "m1"}]
    db.execute.side_effect = [count, rows]
    result = MailWorkspaceService(db, "tenant-1").list_page(allowed_roles={"crm"})
    assert result["total"] == 2
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1" and call.args[1]["roles"] == ["crm"]


def test_queue_rejects_received_mail() -> None:
    db = MagicMock()
    db.execute.return_value = _first(
        {"id": "m1", "status": "received", "role_key": "crm"}
    )
    with pytest.raises(MailWorkspaceError, match="Entwuerfe"):
        MailWorkspaceService(db, "tenant-1").queue_send(
            "m1", allowed_roles={"crm"}, actor="user", reason="Soll versendet werden"
        )


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("crm/mail-arbeitsplatz")
    assert definition and len(definition["tables"]) == 2
    assert _check_readiness(definition)["generatorReady"] is True
