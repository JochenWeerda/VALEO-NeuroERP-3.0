from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.recent_documents_service import (
    RecentDocumentError,
    RecentDocumentsService,
)

pytestmark = pytest.mark.unit


def payload(**overrides):  # noqa: ANN003, ANN201
    base = {
        "screen_id": "finance/ap-invoice",
        "document_id": "invoice-1",
        "document_type": "Eingangsrechnung",
        "document_number": "ER-1001",
        "partner_id": "supplier-1",
        "partner_name": "Muster GmbH",
        "title": "Eingangsrechnung ER-1001",
        "route": "/finance/ap-invoice/invoice-1",
    }
    return {**base, **overrides}


def test_touch_requires_matching_document_role() -> None:
    with pytest.raises(RecentDocumentError, match="berechtigt"):
        RecentDocumentsService(MagicMock(), "tenant-1", "user-1", ["CRM_LESEN"]).touch(
            payload()
        )


def test_touch_rejects_external_route() -> None:
    with pytest.raises(RecentDocumentError, match="intern"):
        RecentDocumentsService(
            MagicMock(), "tenant-1", "user-1", ["FINANCE_LESEN"]
        ).touch(payload(route="https://evil.invalid/invoice-1"))


def test_touch_is_personal_deduplicated_and_bounded() -> None:
    db = MagicMock()
    inserted = MagicMock()
    inserted.mappings.return_value.one.return_value = {
        "id": "recent-1",
        "document_id": "invoice-1",
    }
    db.execute.side_effect = [inserted, MagicMock()]
    result = RecentDocumentsService(db, "tenant-1", "user-1", ["FINANCE_LESEN"]).touch(
        payload()
    )
    assert result["id"] == "recent-1"
    insert_sql = str(db.execute.call_args_list[0].args[0])
    cleanup_sql = str(db.execute.call_args_list[1].args[0])
    assert "ON CONFLICT (tenant_id,user_id,screen_id,document_id)" in insert_sql
    assert "LIMIT 200" in cleanup_sql and "expires_at" in cleanup_sql


def test_list_is_tenant_user_and_current_role_scoped() -> None:
    db = MagicMock()
    count = MagicMock()
    count.scalar_one.return_value = 1
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [
        {"id": "recent-1", "route": "/finance/a"}
    ]
    db.execute.side_effect = [count, rows]
    result = RecentDocumentsService(db, "tenant-1", "user-1", ["FINANCE_LESEN"]).list()
    assert result["total"] == 1
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"
        assert call.args[1]["uid"] == "user-1"
        assert call.args[1]["roles"] == ["FINANCE_LESEN"]


def test_remove_cannot_delete_another_users_history() -> None:
    db = MagicMock()
    db.execute.return_value.rowcount = 1
    deleted = RecentDocumentsService(db, "tenant-1", "user-1", ["user"]).remove(
        "recent-1"
    )
    assert deleted == 1
    assert "tenant_id=:tid AND user_id=:uid" in str(db.execute.call_args.args[0])


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("workspace/letzte-dokumente")
    assert definition and definition["tables"][0]["serverPagination"] is True
    assert _check_readiness(definition)["generatorReady"] is True
